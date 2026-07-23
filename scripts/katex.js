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

  // Display math: $$...$$
  out = out.replace(/\$\$([\s\S]*?)\$\$/g, (_, math) => {
    try {
      return katex.renderToString(decodeMath(math.trim()), { displayMode: true, throwOnError: false });
    } catch (e) {
      return `<span class="katex-error" style="color:#cc0000">$$${math}$$</span>`;
    }
  });

  // Inline math: $...$
  out = out.replace(/\$([^\$\n]+?)\$/g, (_, math) => {
    try {
      return katex.renderToString(decodeMath(math.trim()), { displayMode: false, throwOnError: false });
    } catch (e) {
      return `<span class="katex-error" style="color:#cc0000">$${math}$</span>`;
    }
  });

  // Restore protected blocks
  return out.replace(/\x00KA_BLOCK_(\d+)\x00/g, (_, i) => blocks[parseInt(i)]);
}

hexo.extend.filter.register('after_render:html', function(str) {
  if (str.includes('$')) {
    return renderMath(str);
  }
  return str;
});
