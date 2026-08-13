# 03-CSS进阶与性能 导览

> 定位：五维框架浓缩提炼 03-CSS进阶与性能.md 全部内容小节，快速查阅与复习。
> 用法：每个内容小节对应一张纵向表格，需要深入理解时跳转 [原文](./03-CSS进阶与性能.md)。
> 前置知识：[CSS布局核心](./02-CSS布局核心-导览.md)

---

## 一、CSS3 新特性

### 1.1 过渡（Transition）

| 维度 | 内容 |
|------|------|
| 是什么 | CSS3 提供的属性变化平滑过渡效果，在属性值变化时自动添加过渡动画。 |
| 能做什么 | 将样式变化（如 hover 时颜色变化、尺寸变化）从瞬间突变变成平滑过渡，提升用户体验。 |
| 怎么用 | `transition: property duration timing-function delay;` 如 `transition: width 0.3s ease;` |
| 原理和工作流程 | 浏览器监测属性值变化，在两个值之间插值计算每一帧的中间值，并在指定时间内绘制。transition 不需要定义关键帧，只需要定义起点和终点，浏览器自动补间。 |
| 缺点 | 只有开始和结束两个状态，无法控制中间过程；不是所有 CSS 属性都可过渡（display 不可过渡，opacity 可）；需要浏览器支持，极旧浏览器不生效。 |

### 1.2 动画（Animation + @keyframes）

| 维度 | 内容 |
|------|------|
| 是什么 | CSS3 提供的关键帧动画方案，通过 `@keyframes` 定义多个关键帧，控制多阶段动画流程。 |
| 能做什么 | 实现复杂多阶段动画，支持循环播放、反向播放、暂停、动画结束保持状态等高级控制。 |
| 怎么用 | `@keyframes slideIn { 0% { ... } 100% { ... } }`，然后 `animation: slideIn 1s ease infinite alternate forwards;` |
| 原理和工作流程 | 定义关键帧位置（百分比）和对应样式，浏览器按时间线在关键帧之间插值计算每一帧样式。支持多种配置：`animation-iteration-count` 控制循环次数、`animation-direction` 控制播放方向、`animation-fill-mode` 控制动画结束后样式保持。 |
| 缺点 | 复杂动画性能不如 JavaScript 控制的 Canvas 或 WebGL；调试关键帧位置不如 JavaScript 灵活。 |

### 1.3 变换（Transform）

| 维度 | 内容 |
|------|------|
| 是什么 | CSS3 提供的 2D/3D 变换能力，支持平移、旋转、缩放、倾斜，不触发回流，性能优异。 |
| 能做什么 | 实现元素位移、旋转、缩放效果；配合 transition 做动画；性能优于修改 top/left/width/height，因为只触发合成阶段，不触发布局和绘制。 |
| 怎么用 | `transform: translate(100px, 50px) rotate(45deg) scale(1.5);` |
| 原理和工作流程 | transform 改变的是元素的视觉呈现，不改变布局（周围元素位置不受影响）。变换计算在 GPU 合成层进行，不需要重新布局和绘制，因此性能远好于修改 top/left 等几何属性。组合变换顺序从右往左执行。 |
| 缺点 | 变换顺序影响最终结果，需要注意顺序；旋转 180 度文字可能模糊；占用 GPU 显存，大量元素同时变换可能导致内存不足。 |

### 1.4 CSS 视觉效果

| 维度 | 内容 |
|------|------|
| 是什么 | CSS3 提供的多种视觉增强效果：阴影（box-shadow/text-shadow）、圆角（border-radius）、渐变（linear-gradient/radial-gradient/conic-gradient）。 |
| 能做什么 | box-shadow 创建元素阴影；text-shadow 创建文字阴影；border-radius 实现圆角；渐变实现平滑颜色过渡背景。 |
| 怎么用 | `box-shadow: 2px 4px 8px rgba(0, 0, 0, 0.2);`、`border-radius: 8px;`、`background: linear-gradient(to right, #667eea, #764ba2);` |
| 原理和工作流程 | 阴影由浏览器在绘制阶段根据参数计算像素值；圆角通过路径裁剪实现；渐变通过数学插值计算每个像素颜色。这些效果都是 GPU 友好的，不会触发回流。 |
| 缺点 | 大量使用 box-shadow 会增加绘制开销，动画中使用可能导致卡顿；渐变计算比纯色背景开销大。 |

### 1.5 CSS 变量（自定义属性）

| 维度 | 内容 |
|------|------|
| 是什么 | CSS 原生变量支持，通过 `--变量名` 定义，`var(--变量名, 回退值)` 使用，支持继承和动态修改。 |
| 能做什么 | 统一管理主题色、间距单位、圆角大小等全局样式；实现主题切换（明暗模式）；支持 JavaScript 运行时动态修改变量值。 |
| 怎么用 | `:root { --primary-color: #4A90D9; }`，`.button { background: var(--primary-color); }`，`document.documentElement.style.setProperty('--primary-color', newColor)` |
| 原理和工作流程 | CSS 变量具有继承性，子元素可以覆盖父变量值；值在计算时被替换，浏览器在样式计算阶段解析变量。可以配合 `calc()` 进行动态计算，实现灵活的尺寸计算。 |
| 缺点 | IE 浏览器完全不支持；旧版本浏览器需要降级处理；调试工具支持不如普通 CSS 属性完善。 |

---

## 二、响应式设计

### 2.1 媒体查询（@media）

| 维度 | 内容 |
|------|------|
| 是什么 | CSS3 提供的根据设备特性（屏幕宽度、分辨率、颜色模式）应用不同样式的机制。 |
| 能做什么 | 实现响应式设计：桌面、平板、移动端应用不同样式；适配系统暗色模式；适配横屏/竖屏方向。 |
| 怎么用 | `@media (max-width: 768px) { /* 移动端样式 */ }`、`@media (min-width: 768px) and (max-width: 1024px) { /* 平板 */ }` |
| 原理和工作流程 | 浏览器加载页面时根据当前设备特性匹配媒体查询条件，匹配成功则应用对应样式。支持移动优先（从小到大）和桌面优先（从大到小）两种断点策略。 |
| 缺点 | 断点设置不完整会导致某些屏幕尺寸布局错乱；需要维护多套样式，增加代码量。 |

### 2.2 相对单位

| 维度 | 内容 |
|------|------|
| 是什么 | 相对于父元素、根元素或视口的长度单位：em、rem、vh、vw、vmin、vmax。 |
| 能做什么 | 实现移动端适配，根据屏幕宽度自动缩放字体和组件尺寸；实现全屏高度（100vh）、全屏宽度（100vw）。 |
| 怎么用 | `rem` 相对于根元素 font-size；`em` 相对于父元素 font-size；`1vh` = 视口高度 1%；`1vw` = 视口宽度 1% |
| 原理和工作流程 | rem 适合全局尺寸，不会因为嵌套累积放大；em 适合组件内部相对尺寸，但嵌套会累积；vw/vh 直接和视口绑定，实现真正的全屏效果。 |
| 缺点 | em 嵌套累积容易导致字号失控；vw 在某些浏览器存在兼容性问题；rem 需要配合根字体设置，计算略复杂。 |

### 2.3 移动端适配方案对比

| 维度 | 内容 |
|------|------|
| 是什么 | 四种常见移动端适配方案的对比：rem + 动态根字体、vw 纯 CSS 方案、rem + vw 混合、媒体查询 + 弹性布局。 |
| 能做什么 | 根据项目需求选择合适的适配方案，兼顾兼容性和开发效率。 |
| 怎么用 | rem + 动态根字体需要 JavaScript 动态修改 html font-size；纯 vw 直接用 vw 做单位；rem + vw 根字体用 vw，组件用 rem。 |
| 原理和工作流程 | rem + JS：JS 根据屏幕宽度计算并设置根字体，所有尺寸用 rem 自动缩放；纯 vw：所有尺寸直接用 vw，纯 CSS 无需 JS；rem + vw：根字体用 vw 计算，组件用 rem，兼顾简洁性和灵活性。 |
| 缺点 | rem + JS 需要 JS 辅助，首屏可能闪；纯 vw 需要大量计算；媒体查询需要写多套样式，维护成本高。 |

---

## 三、回流（Reflow）与重绘（Repaint）

### 3.1 概念与区别

| 维度 | 内容 |
|------|------|
| 是什么 | 浏览器渲染页面的两个不同阶段：回流重新计算几何属性（位置尺寸），重绘只重新绘制外观（颜色背景）不改变几何。 |
| 能做什么 | 理解回流和重绘的性能开销差异，指导优化策略：减少回流，尽量只重绘。 |
| 怎么用 | 回流一定触发重绘，重绘不一定触发回流；回流性能开销远大于重绘。 |
| 原理和工作流程 | 浏览器渲染流程：HTML → DOM → CSS → CSSOM → 合并为渲染树 → 回流（计算布局）→ 重绘（绘制像素）→ 合成（合成到屏幕）。回流改变元素几何位置尺寸，需要重新构建渲染树；重绘只改变外观，不需要重新计算布局。 |
| 缺点 | 概念区分需要理解浏览器渲染流程，初学者容易混淆回流和重绘的触发条件和开销差异。 |

### 3.2 触发回流的操作

| 维度 | 内容 |
|------|------|
| 是什么 | 哪些 CSS 操作和 JavaScript 操作会触发回流，帮助开发者识别高开销操作。 |
| 能做什么 | 识别高开销操作，在开发中尽量避免或减少触发次数。 |
| 怎么用 | 常见触发：修改 width/height/padding/margin/top/left；修改 display；修改 font-size；添加删除 DOM；窗口 resize；读取 offsetHeight 等布局信息。 |
| 原理和工作流程 | 任何改变元素几何属性（位置尺寸）的操作都需要重新计算布局，触发回流。读取布局信息（如 offsetHeight）可能强制浏览器提前回流（强制同步布局），因为浏览器需要确保返回最新值。 |
| 缺点 | 很多开发者不知道读取布局信息也会触发回流，导致不经意的性能问题。 |

### 3.3 减少回流与重绘的策略

| 维度 | 内容 |
|------|------|
| 是什么 | 减少浏览器回流重绘次数，提升页面渲染性能的 5 种核心策略。 |
| 能做什么 | 降低动画卡顿概率，提升页面响应速度，特别是在低配置移动设备上体验更好。 |
| 怎么用 | 使用 transform 代替 top/left 做动画；使用 will-change 提前告知浏览器；使用 contain 隔离子树；批量修改 DOM；读写分离避免强制同步布局。 |
| 原理和工作流程 | transform 只触发合成阶段，不触发回流和重绘；will-change 让浏览器提前准备好优化；contain 告诉浏览器该元素子树独立，修改它不会影响页面其他部分；批量修改 DOM 先隐藏再修改最后显示，只触发一次回流。 |
| 缺点 | will-change 使用不当会占用过多 GPU 内存；contain 对复杂布局可能有副作用；需要理解浏览器渲染流水线才能正确应用。 |

---

## 四、CSS 性能优化

### 4.1 核心优化原则

| 维度 | 内容 |
|------|------|
| 是什么 | CSS 性能优化的 8 个核心方向，从选择器、加载、渲染多个维度优化。 |
| 能做什么 | 全面指导 CSS 性能优化，减少加载时间和渲染开销。 |
| 怎么用 | 减少回流重绘；避免深层嵌套选择器；避免 @import；关键 CSS 内联；使用 will-change 和 contain；压缩 CSS 文件。 |
| 原理和工作流程 | @import 会阻塞并行下载，比 link 慢；关键 CSS 内联到 head 减少首屏阻塞；will-change 让浏览器提前优化；contain 隔离渲染范围减少回流范围。 |
| 缺点 | 过度优化会增加代码复杂度，需要权衡收益和维护成本。 |

### 4.2 CSS 选择器效率

| 维度 | 内容 |
|------|------|
| 是什么 | CSS 选择器匹配效率从快到慢排序：ID > 类 > 标签 > 相邻兄弟 > 子选择器 > 后代 > 通配符 > 属性 > 伪类/伪元素。 |
| 能做什么 | 编写更高效的 CSS 选择器，减少浏览器匹配时间。 |
| 怎么用 | 避免深层嵌套（不超过 3 层）；减少通配符；避免过于宽泛的右侧选择器；直接给目标元素加类名。 |
| 原理和工作流程 | 浏览器匹配 CSS 选择器是从右向左匹配，因此右侧选择器越具体匹配越快。避免 `.nav a`，推荐 `.nav-link` 直接加类名。深层嵌套会增加匹配次数，降低效率。现代浏览器优化很好，选择器效率差异不如以前显著，但仍需注意。 |
| 缺点 | 过度追求选择器效率会增加 HTML 类名数量，代码可读性下降，需要权衡。 |

### 4.3 渲染性能对比

| 维度 | 内容 |
|------|------|
| 是什么 | 不同 CSS 属性修改触发的渲染阶段不同，性能开销差异巨大。 |
| 能做什么 | 选择性能最优的属性做动画，避免卡顿掉帧。 |
| 怎么用 | 仅合成：transform/opacity → 最低开销；重绘：color/background-color/box-shadow → 中等开销；回流+重绘：width/height/top/left → 最高开销。 |
| 原理和工作流程 | 渲染流水线分为 Layout（回流）→ Paint（重绘）→ Composite（合成）。仅合成阶段只需要最后合并图层，不需要布局和绘制，因此性能最好。 |
| 缺点 | 大量元素使用 transform 动画会占用过多 GPU 内存，导致内存溢出。 |

---

## 五、常见面试题

### 1. transition 和 animation 的区别？

| 维度 | 内容 |
|------|------|
| 是什么 | 考查 CSS 过渡和动画的核心差异：触发方式、状态支持、能力范围。 |
| 能做什么 | 检验候选人对 CSS 动画体系的理解深度，能否区分两种方案的适用场景。 |
| 怎么用 | transition 需要事件触发（hover/click 等），只能定义开始和结束；animation 可以自动执行，支持多关键帧，适合复杂动画。 |
| 原理和工作流程 | transition 依赖状态变化触发，只能做两个状态之间的过渡；animation 通过 @keyframes 定义多阶段，支持循环、反向、暂停等高级控制，适合自动播放的复杂动画。 |
| 缺点 | 混淆"需要触发"和"自动执行"是常见错误，回答时需要明确区分。 |

### 2. 回流和重绘的区别？如何减少回流？

| 维度 | 内容 |
|------|------|
| 是什么 | 考查回流和重绘的定义区别，以及常见优化策略的掌握。 |
| 能做什么 | 检验候选人是否理解浏览器渲染流程，能否在实际开发中写出高性能 CSS。 |
| 怎么用 | 回流重新计算几何属性，重绘只重新绘制外观；回流一定触发重绘，重绘不一定触发回流。优化：transform 代替 top/left、批量修改 DOM、读写分离、DocumentFragment、will-change。 |
| 原理和工作流程 | 回流是布局阶段，重新计算每个元素的位置和尺寸；重绘是绘制阶段，只改变像素颜色等外观。减少回流就是减少需要重新计算布局的次数。 |
| 缺点 | 回答时容易漏掉"回流一定触发重绘，重绘不一定触发回流"这个关键点。 |

### 3. 为什么 transform 比 top/left 性能更好？

| 维度 | 内容 |
|------|------|
| 是什么 | 考查 CSS 动画性能优化的底层原理，检验对浏览器渲染流水线的理解。 |
| 能做什么 | 理解 transform 性能优势的底层原因，不仅知其然更知其所以然。 |
| 怎么用 | transform 只触发 Composite（合成）阶段，不经过 Layout 和 Paint；top/left 会触发完整的 Layout → Paint → Composite 流程；transform 通常在 GPU 合成层执行，利用硬件加速。 |
| 原理和工作流程 | 浏览器每一次渲染都需要走完流水线：Layout（计算几何）→ Paint（绘制像素）→ Composite（合成到屏幕）。transform 不改变几何属性，不需要 Layout 和 Paint，只需要最后合成，因此性能远好于修改 top/left。 |
| 缺点 | 大量 transform 动画同时执行会占用较多 GPU 内存，需要控制数量。 |

### 4. rem 和 em 的区别？

| 维度 | 内容 |
|------|------|
| 是什么 | 考查两种相对单位的参照物差异，以及使用场景区别。 |
| 能做什么 | 检验候选人对相对单位的理解，能否在移动端适配中正确选择。 |
| 怎么用 | rem 相对于根元素（html）font-size；em 相对于父元素 font-size；rem 不会累积嵌套，适合全局；em 嵌套会累积，适合组件内部。 |
| 原理和工作流程 | em 每次嵌套都根据父元素 font-size 重新计算，多层嵌套会累积放大字体；rem 始终相对于根元素，因此无论嵌套多少层尺寸都是一致的。 |
| 缺点 | 回答时容易混淆参照物，需要明确 rem 是根，em 是父。 |

### 5. 移动端适配方案有哪些？

| 维度 | 内容 |
|------|------|
| 是什么 | 考查对主流移动端适配方案的全面了解，能否说出优缺点。 |
| 能做什么 | 检验候选人实际移动端开发经验，能否根据项目选择方案。 |
| 怎么用 | rem + 动态设置根字体（成熟方案，需要 JS）、vw 方案（纯 CSS，不需要 JS）、rem + vw 混合（推荐）、媒体查询 + 弹性布局（精确控制）。 |
| 原理和工作流程 | rem + JS：JS 根据屏幕宽度动态修改根字体，rem 自动缩放；纯 vw：所有尺寸直接用 vw，CSS 自动适配；rem + vw：根字体用 vw 计算，组件用 rem，兼顾简洁和灵活。 |
| 缺点 | 不同方案有不同 trade-off，回答时需要说明各自优缺点，不能只说一种方案。 |

---

## 六、避坑指南

| 维度 | 内容 |
|------|------|
| 是什么 | 汇总 CSS 进阶开发中 6 个高频错误及其解决方案：动画性能、em 嵌套、媒体查询断点、will-change、@import、box-shadow 动画。 |
| 能做什么 | 帮助开发者提前避坑，减少调试时间，写出更高性能的 CSS 代码。 |
| 怎么用 | 使用 transform 代替 top/left 做动画；使用 rem 代替 em 做全局尺寸；移动优先策略设置断点；动画结束后移除 will-change；使用 link 代替 @import；避免 box-shadow 动画。 |
| 原理和工作流程 | 每个错误对应一个性能陷阱：top/left 触发回流性能差；em 嵌套累积导致字号失控；断点不全导致某些尺寸布局错乱；will-change 长期保留占用 GPU 内存；@import 阻塞并行下载减慢页面加载。 |
| 缺点 | 这些解决方案需要现代浏览器支持，在需要兼容极旧浏览器时需要降级。 |

---

## CSS contain 与 content-visibility

| 维度 | 内容 |
|------|------|
| 是什么 | `contain` 属性告诉浏览器元素的内部布局/样式/绘制/尺寸与外部完全隔离，浏览器可跳过不必要的计算优化渲染性能；`content-visibility: auto` 自动跳过视口外元素的渲染，实现懒渲染。 |
| 能做什么 | `contain` 的 7 个值（none/layout/style/paint/size/content/strict）分别隔离不同渲染维度；`content-visibility: auto` 可将长页面初始渲染时间减少 50%+；`content-visibility: hidden` 保留布局状态但跳过渲染，优于 `display: none`。 |
| 怎么用 | `contain: content` 用于列表项；`contain: strict` 用于固定尺寸组件；`content-visibility: auto` 配合 `contain-intrinsic-size` 用于长页面；`content-visibility: hidden` 用于虚拟滚动/Tab 切换。 |
| 原理和工作流程 | `contain` 创建隔离边界，浏览器不会让内部变化影响外部计算；`content-visibility: auto` 检测元素是否在视口内，视口外元素完全跳过渲染（Layout + Paint + Composite），`contain-intrinsic-size` 提供占位尺寸防止滚动条跳动。 |
| 缺点 | 使用 `contain: size` 时元素尺寸若未显式设置可能塌缩为 0；`contain: paint` 会创建新层叠上下文影响 z-index；`content-visibility` 旧版浏览器不支持（但作为渐进增强无副作用）。 |

---

## 七、CSS 新特性（追加章节）

| 维度 | 内容 |
|------|------|
| 是什么 | 涵盖 CSS 近年来新增的强大特性：`@supports` 特性检测、CSS 自定义属性（变量）、`scroll-snap` 原生滚动、Container Queries 容器查询、`@layer` 级联层、CSS Nesting 原生嵌套、`:has()` 父选择器。 |
| 能做什么 | `@supports` 实现渐进增强；CSS 变量实现全局主题切换（暗黑模式）；`scroll-snap` 实现原生轮播/全屏滚动；Container Queries 实现组件级响应式；`@layer` 管理样式优先级；CSS Nesting 原生嵌套替代预处理器；`:has()` 实现父选择器和表单验证联动。 |
| 怎么用 | `@supports (display: grid) { ... }` 检测特性后降级；`--primary-color: #1890ff` 声明变量，`var(--primary-color)` 使用；`scroll-snap-type: y mandatory` + `scroll-snap-align: start` 实现滚动吸附；`@container (min-width: 400px) { ... }` 容器查询；`@layer base, components, utilities` 管理层级。 |
| 原理和工作流程 | 每个特性都是 CSS 规范演进的关键里程碑：`@supports` 在 CSS 解析阶段检测支持；CSS 变量在计算值阶段参与级联；`@layer` 改变样式优先级计算顺序（后声明的低优先级层优先级高于先声明的高优先级层）；`:has()` 突破 CSS 选择器只能向下选择的限制。 |
| 缺点 | Container Queries 和 `:has()` 较新，部分旧浏览器不支持（需渐进增强）；CSS Nesting 语法与 Sass 有差异；`@layer` 改变了传统优先级认知，需要团队理解。 |

## 八、CSS 工具链（了解即可）

| 维度 | 内容 |
|------|------|
| 是什么 | CSS 预处理、后处理、原子化 CSS 等工具链生态：Sass/Less 预处理器、Tailwind CSS 原子化框架、CSS Modules 样式隔离、PostCSS 后处理器、Stylelint 样式检查。 |
| 能做什么 | Sass 提供变量/嵌套/混入/函数；Tailwind 提供 utility-first 原子化 CSS 开发体验；CSS Modules 实现组件级样式隔离；PostCSS 通过插件（Autoprefixer 等）处理 CSS 兼容性；Stylelint 检查 CSS 代码规范。 |
| 怎么用 | Sass 使用 `$变量`、`@mixin`、`@include`；Tailwind 通过类名组合快速构建 UI；CSS Modules 的 `.module.css` 文件自动生成唯一类名；PostCSS 配置 `postcss.config.js` 加载插件。 |
| 原理和工作流程 | Sass/Less 在构建时编译为 CSS；Tailwind 通过 JIT 引擎按需生成 CSS；CSS Modules 通过哈希生成唯一类名实现隔离；PostCSS 在构建流程中作为 CSS 转换管道。 |
| 缺点 | Sass 增加构建步骤和学习成本；Tailwind 可能导致 HTML 类名过长；CSS Modules 的动态样式需要 `:global()` 显式声明。 |

## 九、CSS 组织与命名规范（了解即可）

| 维度 | 内容 |
|------|------|
| 是什么 | CSS 方法论和命名规范，用于管理大型项目中的样式组织：BEM（块元素修饰符）、OOCSS（面向对象 CSS）、SMACSS（可扩展模块化 CSS）、ITCSS（倒三角 CSS）。 |
| 能做什么 | BEM 提供清晰的命名约定（`.block__element--modifier`）；OOCSS 分离结构和皮肤、容器和内容；SMACSS 将样式分为五类（Base/Layout/Module/State/Theme）；ITCSS 通过倒三角分层管理选择器特异性。 |
| 怎么用 | BEM：`.card__title--large` 表示 card 块的 title 元素的大号修饰符；OOCSS：`.btn`（结构）+ `.btn-primary`（皮肤）；SMACSS：`l-header`（布局）、`m-card`（模块）、`is-active`（状态）；ITCSS：从 Settings 到 Trumps 的七层倒三角结构。 |
| 原理和工作流程 | 核心思想是管理 CSS 的全局性和级联性：BEM 通过命名约定隔离样式作用域；OOCSS 通过分离关注点提高复用性；SMACSS 通过分类管理降低复杂度；ITCSS 通过分层控制特异性递增。 |
| 缺点 | BEM 命名较长可能影响可读性；OOCSS 过度抽象可能导致类名爆炸；SMACSS 分类界限有时模糊；ITCSS 需要团队统一理解和维护。 |

---

## 十、CSS 现代特性补充

### 10.1 Grid 深入（subgrid / 隐式网格 / masonry）

| 维度 | 内容 |
|------|------|
| 是什么 | CSS Grid 的三个高级特性：**subgrid**（子网格继承父网格轨道定义）、**隐式网格**（grid-auto-rows/grid-auto-columns 控制溢出项目轨道大小）、**masonry**（瀑布流布局，实验性） |
| 能做什么 | subgrid 让嵌套网格的子元素与父网格轨道对齐，实现同一行卡片内容（标题、描述、按钮）自动对齐；隐式网格通过 minmax() 和多值模式灵活控制溢出项目的行高/列宽；masonry 实现原生瀑布流效果 |
| 怎么用 | `grid-template-rows: subgrid` 继承行轨道；`grid-auto-rows: minmax(100px, auto)` 定义隐式行高；`grid-template-rows: masonry` 启用瀑布流（实验性）；`grid-auto-flow: dense` 紧凑排列 |
| 原理和工作流程 | subgrid 让子网格的轨道大小与父网格同步计算（而非独立计算）；隐式轨道在显式轨道不足时自动创建，浏览器按 grid-auto-flow 方向排列溢出项目；masonry 改变了 Grid 的行列对齐逻辑，让项目按最短列填充 |
| 缺点 | subgrid 浏览器兼容性有限（Safari 16+、Firefox 71+）；masonry 仍为实验性（仅 Firefox 通过 flag 支持）；dense 排列会改变 DOM 视觉顺序，影响可访问性 |

### 10.2 CSS @property

| 维度 | 内容 |
|------|------|
| 是什么 | CSS Houdini 项目的一部分，允许开发者显式定义 CSS 自定义属性的**类型（syntax）、初始值（initial-value）和继承行为（inherits）**，使自定义属性支持类型安全的动画和过渡 |
| 能做什么 | 解决 CSS 自定义属性无法动画化的根本问题：声明 `<angle>` 类型后 `--angle` 可在 keyframes 中平滑过渡；声明 `<color>` 类型后颜色变量可以在动画中插值；实现之前无法实现的 CSS 动画效果（如渐变角度旋转） |
| 怎么用 | `@property --border-angle { syntax: '<angle>'; inherits: false; initial-value: 0deg; }` 定义属性；`@keyframes rotate { to { --border-angle: 360deg; } }` 动画中使用；`transition: --progress 0.5s` 过渡中使用 |
| 原理和工作流程 | 在 `@property` 之前，浏览器将所有自定义属性视为"任意字符串"，无法在动画关键帧之间插值（只能跳跃）。`@property` 的 `syntax` 声明告诉浏览器变量类型，浏览器据此在关键帧之间进行数学插值计算 |
| 缺点 | 需要 `@property` 规则而非在 `:root` 中声明，增加代码量；支持的语法类型有限（约 10 种）；Safari 16.4+ 才支持，旧浏览器不兼容 |

### 10.3 View Transitions API

| 维度 | 内容 |
|------|------|
| 是什么 | 声明式 API，用于创建页面之间或 DOM 状态变化之间的平滑过渡动画，浏览器自动处理旧/新视图的快照、插值和动画执行 |
| 能做什么 | SPA 视图切换：用 `document.startViewTransition(callback)` 包裹 DOM 更新实现自动 cross-fade；MPA 跨页面过渡：通过 `@view-transition { navigation: auto }` 启用；为特定元素指定不同过渡效果（`view-transition-name`） |
| 怎么用 | SPA：`document.startViewTransition(() => updateDOM())`；MPA：`<meta name="view-transition" content="same-origin">`；自定义：`::view-transition-old(root)` / `::view-transition-new(root)` 伪元素；元素命名：`view-transition-name: hero` |
| 原理和工作流程 | 浏览器在执行 `startViewTransition` 时：(1) 截取当前页面快照 → (2) 执行回调更新 DOM → (3) 截取新页面快照 → (4) 自动执行从旧快照到新快照的过渡动画。伪元素树 `::view-transition` → `::view-transition-group` → `::view-transition-image-pair` → `::view-transition-old/new` 控制动画细节 |
| 缺点 | 浏览器兼容性有限（Chrome 111+、Edge 111+）；MPA 过渡需要浏览器支持 `@view-transition` at-rule；`view-transition-name` 同一页面内必须唯一；过渡期间 DOM 处于"冻结"状态 |

### 10.4 Popover API / Anchor Positioning

| 维度 | 内容 |
|------|------|
| 是什么 | **Popover API**：原生弹出层能力，无需 JavaScript 库即可实现 tooltip/dropdown/modal；**Anchor Positioning**：CSS 原生锚点定位，让元素相对于另一个元素（锚点）进行定位 |
| 能做什么 | Popover API 自动处理层级管理（top layer）、焦点管理、键盘导航（ESC 关闭）、无障碍访问；Anchor Positioning 使用 `anchor()` 函数和 `anchor-name` 属性实现 tooltip/dropdown 相对于触发按钮的精确定位，无需 JavaScript 计算位置 |
| 怎么用 | Popover：`<div popover>` 声明弹出层 + `popovertarget` 属性绑定按钮；JS 控制：`showPopover()` / `hidePopover()` / `togglePopover()`；Anchor：`anchor-name: --my-anchor` 定义锚点，`top: anchor(bottom)` 定位 |
| 原理和工作流程 | Popover 将元素提升到"顶层"（top layer），位于所有 z-index 之上，浏览器自动处理点击外部关闭和 ESC 关闭；`popover="auto"` 时多个 popover 互斥；Anchor Positioning 通过 CSS 计算锚点元素的边界框，将目标元素定位到锚点的指定边或中心 |
| 缺点 | 浏览器兼容性有限（Popover：Chrome 114+、Edge 114+、Safari 17+；Anchor Positioning：Chrome 125+、Edge 125+）；两个 API 均为较新标准，生产环境使用需注意回退方案 |

---

## 本章学习自检

本节为辅助内容，无五维表格。

---

> [返回原文](./03-CSS进阶与性能.md) | [返回模块目录](../README.md) | [返回知识导览](../知识导览.md)