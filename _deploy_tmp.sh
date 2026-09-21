set -e
cd /d/blog2

echo "== [1/5] git add =="
git add -A

echo "== [2/5] git commit =="
if git diff --cached --quiet; then
  echo "nothing to commit"
else
  git commit -m '更新博客：修复交互演示资源被当作页面渲染（KaTeX 吞掉 ${} 模板串 / iframe 内混入主题外壳），演示 iframe 自适应高度'
fi

echo "== [3/5] git push origin master =="
git push origin master

echo "== [4/5] hexo generate =="
npx hexo generate

echo "== [5/5] hexo deploy =="
npx hexo deploy

echo "== DONE =="
git log --oneline -1
