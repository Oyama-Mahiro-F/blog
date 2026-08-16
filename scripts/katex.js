// Server-side math rendering via KaTeX
// Two-pass approach:
//   1. before_post_render: extract $...$ / $$...$$ from the RAW markdown into
//      placeholders, so the markdown renderer cannot mangle TeX syntax
//      (e.g. "\\" -> hard line break, "_" / "*" -> emphasis, "|" in tables).
//   2. after_post_render: render the stored TeX with KaTeX and substitute it
//      back into the final HTML.
const katex = require('katex');

const STORE_KEY = '_katexMathStore';
const MATH_RE = /xxKATEXMATH(\d+)xx/g;

// --- pass 1: markdown stage -------------------------------------------------
function extractMath(md) {
  const store = [];
  const pushMath = (tex, display) => {
    store.push({ tex: tex.trim(), display });
    return `xxKATEXMATH${store.length - 1}xx`;
  };

  // Protect fenced code blocks and inline code first: their content is not math.
  const codes = [];
  const pushCode = (m) => {
    codes.push(m);
    return `xxKATEXCODE${codes.length - 1}xx`;
  };
  let out = md.replace(/```[\s\S]*?```/g, pushCode);
  out = out.replace(/`[^`\n]*`/g, pushCode);

  // Extract math: display ($$...$$, may span lines) before inline ($...$).
  out = out.replace(/(?<!\\)\$\$([\s\S]+?)(?<!\\)\$\$/g, (_, tex) => pushMath(tex, true));
  out = out.replace(/(?<!\\)\$(?!\s)([^\$\n]*?\S)(?<!\\)\$/g, (_, tex) => pushMath(tex, false));

  // Restore code so it renders normally; math stays as placeholders.
  out = out.replace(/xxKATEXCODE(\d+)xx/g, (_, i) => codes[parseInt(i)]);

  return { md: out, store };
}

// --- pass 2: html stage -----------------------------------------------------
function renderOne(store, i) {
  const item = store[parseInt(i)];
  if (!item) return '';
  const { tex, display } = item;
  let html;
  try {
    html = katex.renderToString(tex, { displayMode: display, throwOnError: false, strict: false });
    // Drop the MathML half of KaTeX output: it visibly doubles every formula
    // when katex.min.css is missing, and its text (incl. the TeX annotation)
    // leaks into strip_html() excerpts, meta description and search index.
    html = html.replace(/<span class="katex-mathml">[\s\S]*?<\/span>(?=<span class="katex-html")/, '');
  } catch (e) {
    html = `<span class="katex-error" style="color:#cc0000">$${tex}$</span>`;
  }
  return html;
}

function renderInto(html, store) {
  // Unwrap the <p> around a standalone placeholder (display math blocks).
  return html
    .replace(/<p>\s*xxKATEXMATH(\d+)xx\s*<\/p>/g, (_, i) => renderOne(store, i))
    .replace(MATH_RE, (_, i) => renderOne(store, i));
}

hexo.extend.filter.register('before_post_render', function (data) {
  if (!data.content || !data.content.includes('$')) return data;
  const { md, store } = extractMath(data.content);
  data.content = md;
  data[STORE_KEY] = store;
  return data;
});

hexo.extend.filter.register('after_post_render', function (data) {
  const store = data[STORE_KEY];
  if (!store || !store.length) return data;
  if (data.content) data.content = renderInto(data.content, store);
  if (data.excerpt) data.excerpt = renderInto(data.excerpt, store);
  return data;
});
