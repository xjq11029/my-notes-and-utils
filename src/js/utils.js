// 常用 JS 工具示例
function debounce(fn, wait = 300) {
  let t = null;
  return function(...args) {
    clearTimeout(t);
    t = setTimeout(() => fn.apply(this, args), wait);
  };
}

function formatDate(date = new Date(), locale = 'en-US') {
  return new Date(date).toLocaleString(locale);
}

module.exports = { debounce, formatDate };
