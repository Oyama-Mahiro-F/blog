// Server-side math rendering via KaTeX
// Two-pass approach: extract math before markdown, render after HTML
const katex = require('katex');
const he = require('he'); // HTML entity decoder

function renderMath(html) {
  // Protect code blocks
  const blocks = [];
  let out = html.replace(/<pre[^>]*>[\s\S]*?<\/pre>/gi, (m) => {
    blocks.push(m);
    return `\x00KA_BLOCK_${blocks.length - 1}\x00`;
  });
  out = out.replace(/<code[^>]*>[\s\S]*?<\/code>/gi, (m) => {
    blocks.push(m);
    return `\x00KA_BLOCK_${blocks.length - 1}\x00`;
  });

  // Decode HTML entities in $...$ math before passing to KaTeX
  function decodeMath(s) {
    return he.decode(s);
  }

  // ① Extract all paired math expressions ($$...$$ and $...$) into placeholders
  const mathExprs = [];
  out = out.replace(/\$\$([\s\S]*?)\$\$/g, (_, math) => {
    mathExprs.push({ math: decodeMath(math.trim()), display: true });
    return `\x00KA_MATH_${mathExprs.length - 1}\x00`;
  });
  out = out.replace(/\$([^\$\n]+?)\$/g, (_, math) => {
    mathExprs.push({ math: decodeMath(math.trim()), display: false });
    return `\x00KA_MATH_${mathExprs.length - 1}\x00`;
  });

  // ② Escape stray dollar signs (e.g. produced by truncated excerpts) so they
  //    never end up inside math mode
  out = out.replace(/\$/g, '&#36;');

  // ③ Render each extracted math expression back into place
  for (let i = 0; i < mathExprs.length; i++) {
    const { math, display } = mathExprs[i];
    let html;
    try {
      html = katex.renderToString(math, { displayMode: display, throwOnError: false, strict: false });
      // Drop the MathML half of KaTeX output: it visibly doubles every formula
      // when katex.min.css is missing, and its text (incl. the TeX annotation)
      // leaks into strip_html() excerpts, meta description and search index.
      html = html.replace(/<span class="katex-mathml">[\s\S]*?<\/span>(?=<span class="katex-html")/, '');
    } catch (e) {
      html = `<span class="katex-error" style="color:#cc0000">$${math}$</span>`;
    }
    out = out.replace(`\x00KA_MATH_${i}\x00`, html);
  }

  // Restore protected blocks
  return out.replace(/\x00KA_BLOCK_(\d+)\x00/g, (_, i) => blocks[parseInt(i)]);
}

// Only process post/page content (never the full-page HTML), otherwise the
// regex would also rewrite $...$ inside <head> meta attributes (description,
// og:description) and break the page markup with quote-truncated attributes.
hexo.extend.filter.register('after_post_render', function(data) {
  if (data.content && data.content.includes('$')) {
    data.content = renderMath(data.content);
  }
  if (data.excerpt && data.excerpt.includes('$')) {
    data.excerpt = renderMath(data.excerpt);
  }
  return data;
});
