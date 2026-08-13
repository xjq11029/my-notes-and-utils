# 05-DOM操作与事件机制 导览

> 定位：五维框架浓缩提炼 05-DOM操作与事件机制.md 全部内容小节，快速查阅与复习。
> 用法：每个内容小节对应一张纵向表格，需要深入理解时跳转 [原文](./05-DOM操作与事件机制.md)。
> 前置知识：01-语法基础与执行机制

---

## 一、DOM树概念与节点类型

### 1.1 DOM树结构与节点类型

| 维度 | 内容 |
|------|------|
| 是什么 | 浏览器将 HTML 文档解析为一棵节点树（Document Object Model），每个标签、文本、注释都对应一个节点对象，提供了可编程操作页面结构的接口。 |
| 能做什么 | 通过 JavaScript 操作 DOM 节点实现动态页面：修改页面内容、添加/删除元素、改变样式、响应用户交互。DOM 是前端与页面交互的核心桥梁。 |
| 怎么用 | 四种常用节点类型：元素节点（nodeType=1）、属性节点（nodeType=2）、文本节点（nodeType=3）、注释节点（nodeType=8）。通过 `nodeType`、`nodeName`、`nodeValue` 三个属性区分节点类型。 |
| 原理和工作流程 | 浏览器按"字节流→字符流→Token→节点对象→DOM树"的流程解析 HTML。构建完成后，`document` 对象成为根节点入口。HTML 中的换行和缩进也会被解析为空白文本节点。 |
| 缺点 | 空白文本节点容易被忽略，使用 `childNodes` 遍历时需要额外过滤；DOM 操作是同步的，频繁操作会触发重排重绘，影响性能。 |

### 1.2 childNodes vs children vs NodeList vs HTMLCollection

| 维度 | 内容 |
|------|------|
| 是什么 | `childNodes` 返回所有类型子节点（NodeList），`children` 只返回元素子节点（HTMLCollection）。NodeList 和 HTMLCollection 是两种类数组集合，在动态性上存在根本差异。 |
| 能做什么 | 区分两种集合用于不同场景：需要遍历所有节点时用 `childNodes`，只需要元素节点时用 `children`；需要动态跟踪 DOM 变化时用 `getElementsBy*` 系列，需要快照时用 `querySelectorAll`。 |
| 怎么用 | `element.childNodes` 获取所有子节点；`element.children` 获取子元素；`document.getElementsByClassName('cls')` 返回动态 HTMLCollection；`document.querySelectorAll('.cls')` 返回静态 NodeList。 |
| 原理和工作流程 | HTMLCollection 始终动态关联 DOM，每次访问 `.length` 都会重新查询；`querySelectorAll` 返回的 NodeList 是创建时的快照，不随 DOM 变化更新。动态集合在循环中增删元素时会导致索引错乱。 |
| 缺点 | 动态集合在循环中操作 DOM 容易导致索引错乱和漏删；HTMLCollection 不支持 `forEach` 需要转为数组；两个概念容易混淆。 |

---

## 二、节点增删改查

### 2.1 节点操作核心 API

| 维度 | 内容 |
|------|------|
| 是什么 | DOM 节点的五大类操作：创建（createElement/createTextNode/createDocumentFragment）、插入（appendChild/insertBefore/append/prepend）、删除（removeChild/remove）、替换（replaceChild）、克隆（cloneNode）。 |
| 能做什么 | 实现动态页面的所有基础操作：动态生成列表、表格、卡片等 UI 组件；拖拽排序；无刷新添加/删除内容；模板克隆渲染。 |
| 怎么用 | 创建：`const div = document.createElement('div');`；插入：`parent.appendChild(div);`；删除：`el.remove();`；替换：`parent.replaceChild(newEl, oldEl);`；克隆：`el.cloneNode(true);`（true 深克隆，false 浅克隆）。 |
| 原理和工作流程 | `appendChild` 具有移动语义（同一节点只能存在于 DOM 树的一个位置）；`DocumentFragment` 是内存中的轻量级 Document，批量插入节点时先将节点添加到 Fragment，再一次性插入 DOM，只触发一次重排。 |
| 缺点 | 逐个 `appendChild` 触发多次重排导致性能差；`innerHTML` 有 XSS 风险且会销毁旧 DOM 和事件监听；`cloneNode` 不克隆事件监听器；忘记 `cloneNode(true)` 参数导致只克隆外层标签。 |

### 2.2 DocumentFragment 性能优化

| 维度 | 内容 |
|------|------|
| 是什么 | `DocumentFragment` 是一个轻量级的 Document 对象，存在于内存中，不在 DOM 树中渲染，用于批量操作 DOM 节点时的性能优化。 |
| 能做什么 | 将多次 DOM 操作合并为一次，减少重排次数。典型场景：批量渲染 1000 条列表数据、动态生成表格行、批量插入模板内容。 |
| 怎么用 | `const frag = document.createDocumentFragment();` 创建 Fragment，将节点逐个 `appendChild` 到 Fragment 上，最后一次性 `parent.appendChild(frag);`。Fragment 本身不会被插入 DOM，只插入其子节点。 |
| 原理和工作流程 | 每次 `appendChild` 到 DOM 树中的元素都会触发浏览器重排。Fragment 在内存中操作不触发重排，最后一次性插入时只触发一次重排，将 O(n) 次重排降低为 O(1) 次。 |
| 缺点 | 不适合需要逐步渲染的动画场景（用户看不到中间状态）；Fragment 只能一次性使用，插入后变空。 |

---

## 三、DOM遍历与选择器API

### 3.1 DOM 遍历属性

| 维度 | 内容 |
|------|------|
| 是什么 | DOM 遍历属性分为三类：向上遍历（parentNode/parentElement）、向下遍历（children/childNodes/firstChild/lastChild/firstElementChild/lastElementChild）、横向遍历（nextSibling/previousSibling/nextElementSibling/previousElementSibling）。 |
| 能做什么 | 在不使用选择器的情况下，通过 DOM 树关系查找相邻节点，常用于表格行操作、树形菜单展开/折叠、相邻元素联动等场景。 |
| 怎么用 | 向上：`el.parentNode` 获取父节点；向下：`el.children` 获取所有子元素；横向：`el.nextElementSibling` 获取下一个兄弟元素。注意带 `Element` 的版本只返回元素节点，不带的版本会返回文本和注释节点。 |
| 原理和工作流程 | 遍历属性直接访问 DOM 树中的预计算引用，不经过选择器引擎，性能优于 `querySelector`。但每次访问都是实时查询，频繁访问同一属性建议缓存结果。 |
| 缺点 | 带 `Element` 和不带 `Element` 的版本容易混淆；`parentNode` 可能返回 Document 节点（非元素）；遍历属性不支持复杂选择器筛选。 |

### 3.2 选择器 API 对比

| 维度 | 内容 |
|------|------|
| 是什么 | 六种 DOM 选择器 API：`getElementById`、`getElementsByClassName`、`getElementsByTagName`、`getElementsByName`、`querySelector`、`querySelectorAll`。前四个返回动态集合，后两个返回静态集合。 |
| 能做什么 | 通过 ID、类名、标签名、name 属性或 CSS 选择器语法查找 DOM 元素。`querySelector` 系列功能最强大，支持任意 CSS 选择器组合。 |
| 怎么用 | `document.getElementById('app')` 按 ID 查找；`document.getElementsByClassName('item')` 按类名查找（动态）；`document.querySelectorAll('.container > .item.active')` 按 CSS 选择器查找（静态）；`element.querySelector(':scope > li')` 在元素范围内查找。 |
| 原理和工作流程 | `querySelectorAll` 采用从右到左的匹配策略，先匹配最右侧选择器再向上验证祖先，效率高于从左到右。`getElementsBy*` 系列直接查询内部哈希表，简单匹配性能略高。静态集合是快照，动态集合每次访问都重新查询。 |
| 缺点 | 动态集合在循环中删除元素时索引错乱；`querySelectorAll` 返回静态快照，DOM 变化后需要重新查询；`getElementById` 只能在 document 上调用。 |

---

## 四、属性操作与样式操作

### 4.1 属性操作

| 维度 | 内容 |
|------|------|
| 是什么 | HTML 属性与 DOM 属性之间的映射和操作体系，包括 `getAttribute`/`setAttribute`/`removeAttribute` 操作 HTML 属性，`dataset` 操作 `data-*` 自定义属性，以及 `classList` API 专门操作类名。 |
| 能做什么 | 读取和修改元素的 HTML 属性（如 src、href、disabled）；通过 `data-*` 属性在 DOM 上存储自定义数据；通过 `classList` 安全地增删改类名而不影响其他类名。 |
| 怎么用 | `el.getAttribute('href')` 读取属性；`el.setAttribute('data-id', '123')` 设置属性；`el.dataset.userId` 读写 `data-user-id` 属性（驼峰命名）；`el.classList.add('active')` / `el.classList.remove('active')` / `el.classList.toggle('dark')` 操作类名。 |
| 原理和工作流程 | 大多数 HTML 属性与 DOM 属性同名同步，但存在例外：`class`→`className`、`for`→`htmlFor`、`tabindex`→`tabIndex`。`classList` 内部维护一个 DOMTokenList，操作时不会影响其他类名，比直接操作 `className` 字符串安全。 |
| 缺点 | `className` 整体替换会覆盖已有类名；`dataset` 在 IE10 及以下不支持；部分 HTML 属性（如 `checked`）在 HTML 层面是字符串，在 DOM 层面是布尔值，行为不一致。 |

### 4.2 样式操作

| 维度 | 内容 |
|------|------|
| 是什么 | 三种样式操作方式：`element.style` 读/写内联样式，`getComputedStyle(element)` 获取最终计算样式，`classList` 通过切换类名间接控制样式。CSS 属性名使用驼峰命名（如 `backgroundColor`）。 |
| 能做什么 | `element.style` 动态设置单个样式属性；`getComputedStyle` 获取元素经过所有 CSS 规则计算后的最终样式值（包括继承、默认值、动画中间值）；`classList` 通过切换预定义 CSS 类来批量控制样式。 |
| 怎么用 | `el.style.backgroundColor = 'red';` 设置内联样式；`el.style.cssText = 'color: red; font-size: 16px;';` 批量设置；`getComputedStyle(el).width` 获取计算后的宽度（始终返回 px 值）；`el.classList.toggle('theme-dark')` 切换主题。 |
| 原理和工作流程 | `element.style` 只映射 HTML 的 `style` 属性（内联样式），无法读取外部样式表定义的样式。`getComputedStyle` 层叠所有样式来源（浏览器默认、外部/内部样式表、内联样式、继承样式），返回最终像素值。`classList` 通过添加/移除类名触发 CSS 规则重新匹配，是推荐的样式控制方式。 |
| 缺点 | `element.style` 无法读取非内联样式（返回空字符串）；`getComputedStyle` 是只读的；在 `display: none` 元素上 `getComputedStyle` 返回的尺寸为 0；频繁修改内联样式可能触发多次重排。 |

---

## 五、尺寸与位置

### 5.1 尺寸与位置属性体系

| 维度 | 内容 |
|------|------|
| 是什么 | 三组尺寸属性：offset 系列（含边框，offsetWidth/Height、offsetLeft/Top）、client 系列（不含边框，clientWidth/Height、clientTop/Left）、scroll 系列（含溢出内容，scrollWidth/Height、scrollTop/Left）。位置 API：`getBoundingClientRect()` 返回相对于视口的精确位置。 |
| 能做什么 | 获取元素的实际占用尺寸和位置；判断元素是否在可视区域内；计算滚动位置；实现拖拽定位、滚动动画、吸顶效果、碰撞检测等。 |
| 怎么用 | `el.offsetWidth` 获取含边框的宽度；`el.clientHeight` 获取可视区域高度；`el.scrollTop` 获取/设置垂直滚动距离；`el.getBoundingClientRect()` 返回 `{top, left, right, bottom, width, height, x, y}`。 |
| 原理和工作流程 | `offsetWidth` = border + padding + content；`clientWidth` = padding + content - 滚动条宽度；`scrollWidth` = padding + 实际内容宽度（含溢出）。`getBoundingClientRect()` 返回的是经过 CSS 变换（transform）后的最终位置，不受 `offsetParent` 影响。`offsetParent` 是最近的已定位祖先元素。 |
| 缺点 | 三组属性容易混淆计算范围；在 `display: none` 元素上所有尺寸属性返回 0；`offsetTop` 相对于 `offsetParent` 而非视口，需要手动累加；频繁读取布局属性会触发强制同步布局（Forced Synchronous Layout）。 |

### 5.2 位置计算与可见性判断

| 维度 | 内容 |
|------|------|
| 是什么 | 通过 `getBoundingClientRect()` 结合 `window.scrollY`/`innerHeight` 等属性，计算元素相对于文档的绝对位置或判断其在视口中的可见性。 |
| 能做什么 | 判断元素是否进入视口（用于曝光埋点）；计算元素相对于文档的绝对位置（用于定位弹窗、下拉菜单）；实现平滑滚动到指定元素；滚动到底部加载更多。 |
| 怎么用 | 绝对位置：`{ top: rect.top + window.scrollY, left: rect.left + window.scrollX }`；可视性判断：`rect.top < window.innerHeight && rect.bottom > 0`；滚动到元素：`window.scrollTo({ top: rect.top + window.scrollY - offset, behavior: 'smooth' })`；滚动到底部：`el.scrollHeight - el.scrollTop - el.clientHeight <= threshold`。 |
| 原理和工作流程 | `getBoundingClientRect()` 的坐标是相对于视口的，加上 `scrollY`/`scrollX` 即为相对于文档的坐标。浏览器在每次访问 `getBoundingClientRect()` 时都会重新计算布局，因此频繁调用会影响性能。 |
| 缺点 | 仅靠 `getBoundingClientRect()` 判断可见性不准确（无法检测被其他元素遮挡的情况）；需要手动处理滚动偏移；频繁调用触发强制同步布局。 |

---

## 六、观察者三剑客

### 6.1 MutationObserver（DOM 变化监听）

| 维度 | 内容 |
|------|------|
| 是什么 | 异步监听 DOM 树变化的 API，可配置监听子节点增删（childList）、属性变化（attributes）、文本内容变化（characterData），以及是否监听所有后代节点（subtree）。 |
| 能做什么 | 防 XSS 攻击（监听并过滤危险属性）；水印保护（监听水印 DOM 被删除或修改）；表单自动保存（监听输入变化）；第三方脚本注入检测；所见即所得编辑器内容监控。 |
| 怎么用 | `const ob = new MutationObserver(callback);` 创建观察者；`ob.observe(target, { childList: true, attributes: true, subtree: true });` 开始观察；`ob.disconnect();` 停止观察；`ob.takeRecords();` 获取未处理的变更记录。 |
| 原理和工作流程 | DOM 变化时，变化记录被推入微任务队列，在当前宏任务完成后批量处理。回调接收一个 `MutationRecord[]` 数组，每条记录包含 `type`、`target`、`addedNodes`、`removedNodes`、`attributeName`、`oldValue` 等信息。与已废弃的 `MutationEvent` 不同，MutationObserver 不会阻塞页面渲染。 |
| 缺点 | 回调中修改 DOM 可能导致死循环（修改触发新的 mutation）；需要手动管理 `disconnect()` 避免内存泄漏；无法监听 CSS 样式变化（需用 ResizeObserver）；不支持 IE10 及以下。 |

### 6.2 IntersectionObserver（可见性监听）

| 维度 | 内容 |
|------|------|
| 是什么 | 异步监听目标元素与祖先元素（或视口）交叉状态的 API，通过 `threshold` 和 `rootMargin` 精确控制触发条件。 |
| 能做什么 | 图片/iframe 懒加载；无限滚动列表；广告曝光埋点；元素进入/离开视口动画触发；根据可见性暂停/恢复视频播放；长列表虚拟滚动中的可见性判断。 |
| 怎么用 | `const ob = new IntersectionObserver(callback, { root: null, rootMargin: '200px', threshold: 0.1 });` 创建观察者，`root` 为 null 表示视口，`rootMargin` 扩大/缩小检测区域，`threshold` 设置交叉比例阈值；`ob.observe(el);` 开始观察；`ob.unobserve(el);` 停止观察单个元素。 |
| 原理和工作流程 | 浏览器在合成器线程上异步计算交叉状态，不依赖 `scroll` 事件，不会阻塞主线程。回调在浏览器空闲时批量执行，性能远优于传统的 `getBoundingClientRect()` + `scroll` 事件方案。`rootMargin` 可以提前触发（正值）或延迟触发（负值）。 |
| 缺点 | 不支持 IE（需 polyfill）；无法精确判断元素是否被其他元素遮挡（只判断与 root 的交叉）；高频率的 `threshold` 数组可能导致回调过于频繁。 |

### 6.3 ResizeObserver（尺寸变化监听）

| 维度 | 内容 |
|------|------|
| 是什么 | 监听任意元素尺寸变化的 API，替代仅能监听视口变化的 `window.resize` 事件。回调提供 `contentRect`（内容尺寸）和 `borderBoxSize`（边框盒尺寸）等信息。 |
| 能做什么 | 响应式容器组件（根据容器宽度自适应布局）；ECharts/Canvas 图表自适应重绘；CSS Container Queries 的 polyfill；监听侧边栏/面板拖拽调整大小；动态调整字体大小。 |
| 怎么用 | `const ob = new ResizeObserver(callback);` 创建观察者；`ob.observe(el);` 开始观察；`callback` 接收 `ResizeObserverEntry[]`，每个 entry 包含 `contentRect.width/height` 和 `borderBoxSize`；`ob.disconnect();` 停止所有观察。 |
| 原理和工作流程 | 回调在布局阶段之后、绘制阶段之前触发，批量异步执行，避免了 `resize` 事件循环触发重排的性能问题。即使元素尺寸因 CSS 变化（非 JavaScript 操作）而改变，ResizeObserver 也能正确检测。 |
| 缺点 | 不支持 IE；观察自身回调中修改尺寸可能触发无限循环（浏览器有保护机制，但需注意）；不支持监听伪元素尺寸变化。 |

---

## 七、事件流与事件机制

### 7.1 事件流三阶段

| 维度 | 内容 |
|------|------|
| 是什么 | DOM 事件传播的三个阶段：捕获阶段（从 window 向下传播到目标元素的父元素）、目标阶段（事件到达目标元素本身）、冒泡阶段（从目标元素向上冒泡到 window）。`addEventListener` 第三个参数决定在哪个阶段触发。 |
| 能做什么 | 精确控制事件处理的时机和顺序；利用冒泡实现事件委托（减少事件绑定数量）；利用捕获在事件到达目标前拦截处理。 |
| 怎么用 | 冒泡监听（默认）：`el.addEventListener('click', handler, false);` 或省略第三个参数；捕获监听：`el.addEventListener('click', handler, true);`；选项对象：`el.addEventListener('click', handler, { capture: true, once: true, passive: true });`。`once` 自动解绑，`passive` 声明不调用 `preventDefault()` 提升滚动性能。 |
| 原理和工作流程 | 事件触发时，浏览器先确定从 window 到目标元素的路径（捕获路径），从外到内依次触发捕获监听器，到达目标元素触发所有监听器，再从内到外依次触发冒泡监听器。`event.eventPhase` 可判断当前阶段（1=捕获，2=目标，3=冒泡）。 |
| 缺点 | 捕获阶段监听器优先级高但容易误拦截后续处理；`passive` 和 `preventDefault` 互斥，设置了 `passive: true` 后调用 `preventDefault` 会被忽略；部分事件不冒泡（focus/blur/scroll/mouseenter/mouseleave）。 |

### 7.2 事件委托

| 维度 | 内容 |
|------|------|
| 是什么 | 利用事件冒泡机制，将子元素的事件处理统一绑定到父元素上，通过 `event.target` 判断实际触发元素并执行相应处理。 |
| 能做什么 | 减少事件监听器数量，节省内存；动态添加的子元素自动获得事件处理能力；集中管理事件逻辑，简化代码维护。 |
| 怎么用 | `parent.addEventListener('click', (e) => { const target = e.target.closest('.btn'); if (!target) return; /* 处理逻辑 */ });`。使用 `e.target.closest(selector)` 或 `e.target.matches(selector)` 判断目标元素是否匹配。 |
| 原理和工作流程 | 子元素的事件冒泡到父元素，父元素的监听器被触发。`event.target` 始终指向最初触发事件的元素，`event.currentTarget` 指向当前监听器绑定的元素（父元素）。通过 `event.target` 结合选择器匹配来区分不同子元素。 |
| 缺点 | 不冒泡的事件（focus/blur/scroll/mouseenter/mouseleave/load/unload）无法委托；事件委托层级过深时 `event.target` 判断可能出错；对高频事件（mousemove）委托可能影响性能。 |

---

## 八、事件控制与自定义事件

### 8.1 stopPropagation / stopImmediatePropagation / preventDefault

| 维度 | 内容 |
|------|------|
| 是什么 | 三个事件控制方法：`stopPropagation()` 阻止事件继续传播（冒泡或捕获），但不阻止当前元素上其他监听器；`stopImmediatePropagation()` 阻止传播且阻止当前元素上其他监听器；`preventDefault()` 阻止浏览器的默认行为（链接跳转、表单提交、右键菜单等），但不阻止事件传播。 |
| 能做什么 | `stopPropagation`：阻止事件冒泡到父元素，用于弹窗内部点击不关闭弹窗等场景；`stopImmediatePropagation`：确保当前监听器是唯一执行的监听器，用于插件系统中独占事件处理；`preventDefault`：阻止默认行为，实现自定义表单验证、SPA 路由拦截、自定义右键菜单等。 |
| 怎么用 | `e.stopPropagation();` 阻止冒泡；`e.stopImmediatePropagation();` 阻止冒泡和同元素其他监听器；`e.preventDefault();` 阻止默认行为。三者可组合使用：先 `preventDefault` 阻止默认行为，再 `stopPropagation` 阻止冒泡。 |
| 原理和工作流程 | `stopPropagation` 设置事件对象的内部传播标志为 false，浏览器在后续阶段检查此标志决定是否继续传播。`stopImmediatePropagation` 额外设置立即停止标志，使当前元素的事件队列中后续监听器直接被跳过。`preventDefault` 设置 `defaultPrevented` 为 true，浏览器在事件处理完成后检查此标志决定是否执行默认行为。 |
| 缺点 | 滥用 `stopPropagation` 可能导致父元素无法响应事件（影响事件委托和分析埋点）；`passive: true` 的监听器中 `preventDefault` 无效且产生控制台警告；混淆 `stopPropagation` 和 `stopImmediatePropagation` 的区别。 |

### 8.2 CustomEvent 自定义事件

| 维度 | 内容 |
|------|------|
| 是什么 | 允许开发者创建和派发自定义事件的 API，通过 `detail` 属性传递任意数据，与原生事件共用同一个事件系统。 |
| 能做什么 | 实现组件间解耦通信（替代深层回调）；构建事件总线（EventBus）模式；自定义生命周期钩子（如 `form-validated`、`route-change`）；扩展现有组件的事件体系。 |
| 怎么用 | 创建：`const event = new CustomEvent('my-event', { detail: { data }, bubbles: true, cancelable: true, composed: true });`；派发：`el.dispatchEvent(event);`；监听：`el.addEventListener('my-event', (e) => { console.log(e.detail); });`。`bubbles` 控制是否冒泡，`composed` 控制是否穿透 Shadow DOM。 |
| 原理和工作流程 | `CustomEvent` 继承自 `Event`，与原生事件共用事件系统。`dispatchEvent` 是同步方法，会依次触发所有匹配的监听器（按捕获→目标→冒泡顺序），所有监听器执行完毕后 `dispatchEvent` 才返回。`detail` 在事件创建时确定，事件派发后不可修改。 |
| 缺点 | 默认 `bubbles` 和 `composed` 为 false，忘记设置会导致父元素或 Shadow DOM 外部无法监听；`dispatchEvent` 是同步的，大量监听器或复杂回调会阻塞主线程；事件名与原生事件同名可能冲突。 |

---

## 九、常见面试题

### 1. DOM 事件流三阶段

| 维度 | 内容 |
|------|------|
| 是什么 | 考查 DOM 事件传播的三个阶段（捕获→目标→冒泡）及各阶段监听器的触发顺序。 |
| 能做什么 | 检验对 `addEventListener` 第三个参数及事件传播机制的理解，是前端面试必考题。 |
| 怎么用 | 捕获阶段（从 window 到目标元素）、目标阶段（到达目标元素）、冒泡阶段（从目标元素到 window）。`addEventListener` 第三个参数为 `true` 时在捕获阶段触发，为 `false`/省略时在冒泡阶段触发。 |
| 原理和工作流程 | 点击目标元素时，浏览器从 window 开始沿 DOM 树向下查找，触发所有捕获监听器，到达目标元素后触发其所有监听器（不分捕获/冒泡），然后沿 DOM 树向上冒泡触发所有冒泡监听器。 |
| 缺点 | 回答时容易遗漏：目标阶段不区分捕获和冒泡，所有监听器按绑定顺序执行；`event.eventPhase` 可以判断当前阶段。 |

### 2. 事件委托的原理与优缺点

| 维度 | 内容 |
|------|------|
| 是什么 | 考查事件委托的定义、实现原理、优缺点以及哪些事件不冒泡。 |
| 能做什么 | 检验对事件冒泡机制的深入理解和实际应用能力。 |
| 怎么用 | 将事件监听器绑定在父元素上，通过 `event.target` 判断实际触发元素。`e.target.closest('.btn')` 匹配目标元素，根据 `data-*` 属性或类名执行不同逻辑。 |
| 原理和工作流程 | 利用事件冒泡机制，子元素的事件冒泡到父元素后触发父元素的监听器。`event.target` 始终指向最初触发事件的元素，以此区分不同子元素。 |
| 缺点 | 容易遗漏不冒泡的事件列表（focus、blur、scroll、mouseenter、mouseleave 等）；`event.target` 可能指向深层嵌套的子元素，需用 `closest` 而非直接判断。 |

### 3. MutationObserver / IntersectionObserver / ResizeObserver 的区别

| 维度 | 内容 |
|------|------|
| 是什么 | 考查三个现代观察者 API 的监听目标、触发时机、配置方式和典型应用场景的区别。 |
| 能做什么 | 检验对现代浏览器 API 的掌握程度，以及能否根据场景选择合适的观察者。 |
| 怎么用 | MutationObserver：监听 DOM 树变化（节点增删、属性、文本），配置 `childList`/`attributes`/`characterData`/`subtree`；IntersectionObserver：监听元素与视口交叉状态，配置 `threshold`/`rootMargin`；ResizeObserver：监听元素尺寸变化，通过 `contentRect` 获取新尺寸。 |
| 原理和工作流程 | 三个观察者都是异步批量执行回调，不会阻塞主线程。MutationObserver 使用微任务，IntersectionObserver 和 ResizeObserver 在浏览器空闲时批量执行。都需要手动 `disconnect()` 避免内存泄漏。 |
| 缺点 | 容易混淆三个观察者的适用场景；忘记 `disconnect()` 导致内存泄漏；MutationObserver 回调中修改 DOM 可能死循环。 |

### 4. stopPropagation vs stopImmediatePropagation

| 维度 | 内容 |
|------|------|
| 是什么 | 考查两个事件停止方法的区别：`stopPropagation` 只阻止事件传播，`stopImmediatePropagation` 同时阻止传播和同元素其他监听器。 |
| 能做什么 | 检验对事件传播控制的精细理解。 |
| 怎么用 | `e.stopPropagation()` 阻止事件向父元素传播，同元素其他监听器仍执行；`e.stopImmediatePropagation()` 阻止传播且同元素后续监听器不执行。 |
| 原理和工作流程 | 浏览器的监听器列表按绑定顺序排列。`stopPropagation` 阻止后续阶段的传播，但当前阶段（如目标阶段）的监听器列表继续执行。`stopImmediatePropagation` 立即中断当前监听器列表的遍历。 |
| 缺点 | 回答时容易混淆两者的影响范围，特别是目标阶段多个监听器的行为差异。 |

---

## 十、避坑指南

| 维度 | 内容 |
|------|------|
| 是什么 | 汇总 DOM 操作与事件机制中 10 个高频错误：空白文本节点陷阱、动态集合索引错乱、innerHTML 的 XSS 风险、cloneNode 忘记参数、style 无法读取非内联样式、尺寸属性混淆、MutationObserver 回调死循环、事件委托用了不冒泡事件、passive 与 preventDefault 冲突、dispatchEvent 同步阻塞。 |
| 能做什么 | 帮助开发者提前规避 DOM 操作中的常见陷阱，写出更安全、更高效的代码。 |
| 怎么用 | 遍历子元素用 `children` 而非 `childNodes`；循环中操作 DOM 用 `Array.from` 转静态数组；用 `textContent` 或 `classList` 替代 `innerHTML`；深克隆用 `cloneNode(true)`；读取计算样式用 `getComputedStyle`；MutationObserver 回调中修改 DOM 前先 `disconnect`；事件委托注意不冒泡的事件；需要 `preventDefault` 时不设置 `passive: true`。 |
| 原理和工作流程 | 每个错误对应一个底层机制的误解：空白文本节点是 HTML 解析的副产品；动态集合每次访问都重新查询 DOM；`innerHTML` 直接解析 HTML 字符串绕过安全机制；`dispatchEvent` 是同步方法会阻塞主线程。 |
| 缺点 | 部分避坑方案需要理解底层机制才能正确应用，初学者容易机械套用。 |

---

## 本章学习自检

本节为辅助内容，无五维表格。

---

> [返回原文](./05-DOM操作与事件机制.md) | [返回模块目录](../README.md) | [返回知识导览](../知识导览.md)