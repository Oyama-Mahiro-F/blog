const _ = require('lodash')
const { version, name } = require('../package.json')

// Inject lodash into EJS template locals (removed in hexo-renderer-ejs v2+)
hexo.extend.filter.register('after_init', () => {
  const rendererPath = require.resolve('hexo-renderer-ejs/lib/renderer')
  delete require.cache[rendererPath]
  const origRenderer = require(rendererPath)
  const ejs = require('ejs')
  const wrappedRenderer = function(data, locals) {
    locals = Object.assign({_: _}, locals || {})
    return origRenderer.call(this, data, locals)
  }
  wrappedRenderer.compile = function(data) {
    const compiled = origRenderer.compile.call(this, data)
    return function(locals) {
      locals = Object.assign({_: _}, locals || {})
      return compiled.call(this, locals)
    }
  }
  hexo.extend.renderer.register('ejs', 'html', wrappedRenderer, true)
})

hexo.extend.helper.register('theme_version', () => version)

const source = (path, cache, ext) => {
    if (cache) {
        const minFile = `${path}${ext === '.js' ? '.min' : ''}${ext}`
        return hexo.theme.config.cdn ? `//unpkg.com/${name}@latest${minFile}` : `${minFile}?v=${version}`
    } else {
        return path + ext
    }
}
hexo.extend.helper.register('theme_js', (path, cache) => source(path, cache, '.js'))
hexo.extend.helper.register('theme_css', (path, cache) => source(path, cache, '.css'))

function renderImage(src, alt = '', title = '') {
    return `<figure class="image-bubble">
                <div class="img-lightbox">
                    <div class="overlay"></div>
                    <img src="${src}" alt="${alt}" title="${title}">
                </div>
                <div class="image-caption">${title || alt}</div>
            </figure>`
}

hexo.extend.tag.register('image', ([src, alt = '', title = '']) => {
    return hexo.theme.config.lightbox ? renderImage(src, alt, title) : `<img src="${src}" alt="${alt}" title="${title}">`
})

hexo.extend.filter.register('before_post_render', data => {
    if (hexo.theme.config.lightbox) {
        // 包含图片的代码块 <escape>[\s\S]*\!\[(.*)\]\((.+)\)[\s\S]*<\/escape>
        // 行内图片 [^`]\s*\!\[(.*)\]\((.+)\)([^`]|$)
        data.content = data.content.replace(/<escape>.*\!\[(.*)\]\((.+)\).*<\/escape>|([^`]\s*|^)\!\[(.*)\]\((.+)\)([^`]|$)/gm, match => {

            // 忽略代码块中的图片
            if (/<escape>[\s\S]*<\/escape>|.?\s{3,}/.test(match)) {
                return match
            }

            return match.replace(/\!\[(.*)\]\((.+)\)/, (img, alt, src) => {
                const titleMatch = src.match(/^(.+?)\s+["'](.+?)["']$/)
                let realSrc, title
                if (titleMatch) {
                    realSrc = titleMatch[1]
                    title = titleMatch[2]
                } else {
                    realSrc = src
                    title = ''
                }
                return `{% image '${realSrc}' '${alt}' '${title}' %}`
            })
        })
    }
    return data
})
