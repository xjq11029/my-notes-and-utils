# 02-CSS布局核心 导览

> 定位：五维框架浓缩提炼 02-CSS布局核心.md 全部内容小节，快速查阅与复习。
> 用法：每个内容小节对应一张纵向表格，需要深入理解时跳转 [原文](./02-CSS布局核心.md)。
> 前置知识：[HTML核心与语义化](./01-HTML核心与语义化-导览.md)

---

## 一、核心概念

### 1.1 盒模型（Box Model）

| 维度 | 内容 |
|------|------|
| 是什么 | 页面布局的基石，每个元素被视为由 margin、border、padding、content 四层组成的矩形盒子，分为标准盒模型（content-box）和替代盒模型（border-box）两种。 |
| 能做什么 | 准确计算元素实际占用宽度，避免布局溢出；通过切换 `box-sizing` 简化复杂布局的尺寸计算。 |
| 怎么用 | `box-sizing: content-box`（标准，width = 内容区）；`box-sizing: border-box`（替代，width = content + padding + border）；全局设置 `*, *::before, *::after { box-sizing: border-box; }` |
| 原理和工作流程 | 标准盒模型下元素的 `width` 仅指 content 区域，实际宽度 = `width + padding + border + margin`；替代盒模型下 `width` 包含 content + padding + border，实际宽度 = `width + margin`。浏览器根据 `box-sizing` 值在布局阶段计算每个元素的盒尺寸。 |
| 缺点 | 标准盒模型下添加 padding 和 border 会增大元素尺寸，容易撑破布局，需要额外计算；替代盒模型下 content 区域自动缩小，在某些需要精确指定 content 宽度的场景不够直观。 |

### 1.2 BFC（块级格式化上下文）

| 维度 | 内容 |
|------|------|
| 是什么 | 一个独立的渲染区域，内部元素的布局不会影响外部元素，可看作页面中的"隔离容器"。 |
| 能做什么 | 清除浮动解决父元素高度塌陷；防止外边距折叠（margin 合并）；实现非浮动元素与浮动元素的自适应两栏布局。 |
| 怎么用 | 触发方式：`overflow: hidden`、`float: left/right`、`position: absolute/fixed`、`display: flex/grid/inline-block`、`contain: layout` |
| 原理和工作流程 | BFC 内部的 Box 在垂直方向一个接一个排列；同一 BFC 内相邻 Box 的 margin 会折叠；BFC 不会与浮动元素重叠；BFC 计算高度时会包含浮动子元素。浏览器在渲染时为每个 BFC 创建独立的布局上下文，隔离布局计算。 |
| 缺点 | 不同触发方式有副作用：`overflow: hidden` 会裁剪溢出内容；`float` 会使元素脱离文档流；`position: absolute` 完全脱离文档流。需要根据场景选择合适的方式。 |

---

## 二、Flex 布局

### 2.1 容器属性（父元素）

| 维度 | 内容 |
|------|------|
| 是什么 | 设置 `display: flex` 后容器拥有的 6 个核心属性，控制子元素在主轴和交叉轴上的排列方式。 |
| 能做什么 | 控制主轴方向（`flex-direction`）、是否换行（`flex-wrap`）、主轴对齐（`justify-content`）、交叉轴对齐（`align-items`）、多行对齐（`align-content`）、项目间距（`gap`）。 |
| 怎么用 | `display: flex; flex-direction: row; justify-content: space-between; align-items: center; gap: 16px;` |
| 原理和工作流程 | 浏览器将容器内的直接子元素作为 Flex 项目，按照主轴（由 `flex-direction` 决定）和交叉轴（垂直于主轴）进行布局。`justify-content` 在主轴方向分配剩余空间；`align-items` 在交叉轴方向对齐项目；`gap` 在项目间创建固定间距。 |
| 缺点 | `gap` 在旧版浏览器中不支持 Flex 布局（仅支持 Grid），需使用 `margin` 替代方案。 |

### 2.2 项目属性（子元素）

| 维度 | 内容 |
|------|------|
| 是什么 | Flex 项目拥有的 6 个属性，控制每个子元素在容器内的伸缩行为、对齐方式和排列顺序。 |
| 能做什么 | `flex-grow` 分配剩余空间；`flex-shrink` 控制收缩权重；`flex-basis` 设定初始大小；`flex` 为三合一简写；`align-self` 单独控制某个项目的交叉轴对齐；`order` 调整排列顺序。 |
| 怎么用 | `flex: 1`（等分剩余空间）、`flex: auto`（按内容比例分配）、`flex: none`（不伸缩）、`align-self: flex-end` |
| 原理和工作流程 | `flex: 1` 等价于 `flex-grow: 1; flex-shrink: 1; flex-basis: 0%`，初始大小为 0，按 grow 权重等分剩余空间。`flex: auto` 等价于 `flex-grow: 1; flex-shrink: 1; flex-basis: auto`，按内容大小占据空间后再分配剩余空间。区别在于 `flex-basis` 的不同。 |
| 缺点 | `flex: 1` 和 `flex: auto` 容易混淆，前者按比例等分，后者按内容比例分配，选错会导致布局效果与预期不符。 |

---

## 三、Grid 布局

### 3.1 容器属性

| 维度 | 内容 |
|------|------|
| 是什么 | 二维布局系统，通过 `grid-template-columns` 和 `grid-template-rows` 同时定义行和列，构建精确的网格结构。 |
| 能做什么 | 实现复杂页面整体布局（如三栏、后台管理布局）；`fr` 弹性单位等分剩余空间；`auto-fill`/`auto-fit` 配合 `minmax()` 实现响应式网格。 |
| 怎么用 | `display: grid; grid-template-columns: 200px 1fr 200px; grid-template-rows: 60px auto; gap: 16px;` |
| 原理和工作流程 | `fr` 单位将剩余空间按弹性系数等分（如 `1fr 2fr 1fr` 将空间分 4 份，三列分别占 1/4、2/4、1/4）。`auto-fill` 尽可能多创建列，即使有空列；`auto-fit` 拉伸现有项目填满整行。浏览器在布局阶段根据网格模板计算每个单元格的精确位置和尺寸。 |
| 缺点 | 学习曲线较陡，需要同时理解行列定义、网格线编号、命名区域等多种概念；旧版浏览器不支持。 |

### 3.2 项目属性

| 维度 | 内容 |
|------|------|
| 是什么 | Grid 项目的定位属性，通过网格线编号或命名区域精确控制每个项目在网格中的位置和跨度。 |
| 能做什么 | 按网格线编号定位项目（`grid-column: 1 / 3` 跨越 2 列）；使用 `grid-area` + `grid-template-areas` 以命名方式直观布局。 |
| 怎么用 | `grid-column: 1 / 3`、`grid-row: 1 / 3`、`grid-area: header` |
| 原理和工作流程 | 网格线从 1 开始编号，`grid-column: 1 / 3` 等价于 `grid-column: 1 / span 2`，表示从第 1 条线到第 3 条线跨越 2 列。`grid-template-areas` 以字符串矩阵形式定义命名区域，项目通过 `grid-area` 引用区域名，浏览器自动计算对应的网格线位置。 |
| 缺点 | 网格线编号依赖视觉理解，复杂布局时容易混淆；`grid-template-areas` 要求区域必须是矩形，不能是 L 形等不规则形状。 |

### 3.3 Flex vs Grid 选择指南

| 维度 | 内容 |
|------|------|
| 是什么 | 总结 Flex（一维）和 Grid（二维）两种布局模式的适用场景，指导实际开发中的选择。 |
| 能做什么 | 一维排列（导航栏、列表）用 Flex；二维布局（整体页面结构）用 Grid；内容驱动（元素大小不固定）用 Flex；布局驱动（网格固定）用 Grid；居中对齐 Flex 最简洁。 |
| 怎么用 | 导航栏：`display: flex;`；整体页面结构：`display: grid; grid-template-columns: ...` |
| 原理和工作流程 | Flex 是单轴布局模型，项目沿主轴（或换行后的多行）排列，适合"一排"或"一列"中的项目分布。Grid 是双轴布局模型，同时控制行和列，适合需要精确对齐的二维平面。两者不互斥，经常在 Grid 容器内部使用 Flex 排列子项。 |
| 缺点 | Flex 不擅长需要行列严格对齐的二维布局；Grid 对于简单的单行排列显得过于复杂。 |

---

## 四、元素居中方案

### 4.1 水平居中

| 维度 | 内容 |
|------|------|
| 是什么 | 使元素在水平方向上相对于父容器居中的 5 种常用方案及其适用场景。 |
| 能做什么 | 文本/行内元素用 `text-align: center`；定宽块级元素用 `margin: 0 auto`；任意元素用 Flex（`justify-content: center`）或 Grid（`place-items: center`）。 |
| 怎么用 | 父元素 `text-align: center`；自身 `margin: 0 auto`；父元素 `display: flex; justify-content: center`；父元素 `display: grid; place-items: center`；`left: 50%; transform: translateX(-50%)` |
| 原理和工作流程 | `text-align: center` 作用于行内内容；`margin: auto` 在块级元素两侧自动分配剩余空间；Flex/Grid 的居中属性在容器层面控制对齐；`left + transform` 通过偏移 50% 再回拉自身一半宽度实现居中。 |
| 缺点 | `text-align` 仅对行内元素有效；`margin: auto` 需要元素有明确宽度；`left + transform` 需要父元素 `position: relative`。 |

### 4.2 垂直居中

| 维度 | 内容 |
|------|------|
| 是什么 | 使元素在垂直方向上相对于父容器居中的 5 种常用方案。 |
| 能做什么 | 单行文本用 `line-height` 等于容器高度；行内块/表格单元格用 `vertical-align: middle`；任意元素用 Flex（`align-items: center`）或 Grid。 |
| 怎么用 | `line-height: 容器高度`；`display: table-cell; vertical-align: middle`；`display: flex; align-items: center`；`display: grid; align-items: center`；`top: 50%; transform: translateY(-50%)` |
| 原理和工作流程 | `line-height` 使文本在行高内垂直居中；`vertical-align: middle` 在表格单元格或行内块上下文中生效；Flex/Grid 在交叉轴方向居中；`top + transform` 通过偏移 50% 再回拉自身一半高度实现居中。 |
| 缺点 | `line-height` 仅对单行文本有效；`vertical-align` 在非表格/行内块元素中不生效；`top + transform` 需要父元素 `position: relative`。 |

### 4.3 水平垂直居中（完整方案）

| 维度 | 内容 |
|------|------|
| 是什么 | 同时实现水平垂直居中的 4 种完整方案，从推荐到备用排序。 |
| 能做什么 | Flex 方案最简洁（推荐）；Grid 方案一行搞定；absolute + transform 无需知道宽高；absolute + margin:auto 需要知道宽高但兼容性最好。 |
| 怎么用 | `display: flex; justify-content: center; align-items: center;`；`display: grid; place-items: center;`；`position: absolute; top: 50%; left: 50%; transform: translate(-50%, -50%);` |
| 原理和工作流程 | Flex 和 Grid 方案在容器层面一次设置即可；`place-items: center` 是 `align-items: center` 和 `justify-items: center` 的简写；absolute + transform 通过 `translate(-50%, -50%)` 反向偏移自身宽高的一半实现居中。 |
| 缺点 | absolute + transform 方案中元素脱离文档流，可能影响周边元素布局；absolute + margin:auto 方案需要明确宽高。 |

---

## 五、定位（Position）

| 维度 | 内容 |
|------|------|
| 是什么 | CSS 定位的 5 种取值：static（默认）、relative（相对自身）、absolute（相对已定位祖先）、fixed（相对视口）、sticky（相对滚动祖先），每种对应不同的参照物和文档流行为。 |
| 能做什么 | relative 用于微调位置和为 absolute 子元素建立定位上下文；absolute 用于弹窗、下拉菜单、Tooltip；fixed 用于固定导航栏、返回顶部按钮；sticky 用于吸顶导航、表格表头固定。 |
| 怎么用 | `position: sticky; top: 0;`（吸顶导航）；`position: fixed; bottom: 0;`（固定底部栏）；`position: absolute; top: 50%; left: 50%; transform: translate(-50%, -50%);`（弹窗居中） |
| 原理和工作流程 | static 遵循正常文档流；relative 在原有位置偏移但不脱离文档流（保留占位）；absolute 寻找最近已定位祖先（非 static），完全脱离文档流；fixed 相对于浏览器视口固定，脱离文档流；sticky 在达到阈值前为 relative，达到后为 fixed，不脱离文档流。 |
| 缺点 | absolute 参照物错误是常见问题（忘记在父元素上设置 `position: relative`）；sticky 在父元素设置了 `overflow: hidden` 时失效；fixed 在 iOS 中有输入框弹出时的异常表现。 |

---

## 六、浮动（Float）与清除浮动

### 6.1 浮动的特点

| 维度 | 内容 |
|------|------|
| 是什么 | 浮动使元素脱离正常文档流，向左或向右移动直到碰到父容器边界或另一个浮动元素，行内元素会环绕浮动元素。 |
| 能做什么 | 实现文字环绕图片效果；在 Flex/Grid 普及前用于多栏布局（现已不推荐）。 |
| 怎么用 | `float: left`、`float: right` |
| 原理和工作流程 | 浮动元素脱离文档流但不完全脱离（行内元素环绕），其后的块级元素会"无视"浮动元素占据位置，但行内内容会避让。父容器不会自动撑开以包含浮动子元素，导致高度塌陷。 |
| 缺点 | 高度塌陷是浮动最核心的问题，需要额外清除浮动；现代布局中 Flex 和 Grid 已基本替代浮动做布局。 |

### 6.2 清除浮动的方案

| 维度 | 内容 |
|------|------|
| 是什么 | 解决浮动元素导致父容器高度塌陷的 4 种方案，核心是 clearfix 伪元素法。 |
| 能做什么 | clearfix 伪元素法（推荐）语义清晰、不污染 DOM；触发父元素 BFC 代码简洁；空标签法和固定高度法不推荐。 |
| 怎么用 | `.clearfix::after { content: ''; display: block; clear: both; }`；`.parent-bfc { overflow: hidden; }` |
| 原理和工作流程 | clearfix 伪元素在父元素末尾插入一个不可见的块级元素，设置 `clear: both` 使其位于所有浮动元素下方，从而撑开父元素高度。触发 BFC 使父元素在计算高度时包含浮动子元素。空标签法在 HTML 中直接插入 `<div style="clear: both;">`，语义差。 |
| 缺点 | `overflow: hidden` 会裁剪溢出内容，不适合需要溢出显示的场景；clearfix 是约定俗成的命名，需要团队统一。 |

---

## 七、常见面试题

### 1. 标准盒模型和 IE 盒模型的区别？

| 维度 | 内容 |
|------|------|
| 是什么 | 考查 content-box 和 border-box 两种盒模型的核心差异：width 包含范围不同。 |
| 能做什么 | 检验候选人是否理解元素尺寸计算方式，以及在实际项目中是否会全局设置 `border-box` 简化布局。 |
| 怎么用 | `box-sizing: content-box`（标准，width = 仅 content）；`box-sizing: border-box`（IE/替代，width = content + padding + border） |
| 原理和工作流程 | 标准盒模型总宽度 = `width + padding + border + margin`；border-box 总宽度 = `width + margin`。推荐全局使用 border-box 避免添加 padding 导致元素撑破布局。 |
| 缺点 | 回答时需注意"IE 盒模型"这个名称具有误导性，实际上 `border-box` 是 CSS3 标准的替代方案，并非 IE 专属。 |

### 2. BFC 是什么？如何触发？有哪些应用场景？

| 维度 | 内容 |
|------|------|
| 是什么 | 考查 BFC 的定义、至少 3 种触发方式和 3 个应用场景的完整理解。 |
| 能做什么 | 检验候选人对 CSS 渲染机制的理解深度，以及解决实际布局问题的能力。 |
| 怎么用 | 触发：`overflow: hidden`、`float`、`position: absolute/fixed`、`display: flex/grid`；场景：清除浮动、防止 margin 折叠、自适应两栏布局。 |
| 原理和工作流程 | BFC 内部元素垂直排列、margin 折叠、不与浮动元素重叠、计算高度包含浮动子元素。浏览器为每个 BFC 创建独立的渲染上下文，隔离内外布局计算。 |
| 缺点 | 回答时需注意区分 BFC 和 IFC（行内格式化上下文），以及各自的触发条件。 |

### 3. Flex: 1 代表什么？和 flex: auto 有什么区别？

| 维度 | 内容 |
|------|------|
| 是什么 | 考查 `flex: 1`（`flex: 1 1 0%`）和 `flex: auto`（`flex: 1 1 auto`）底层 `flex-basis` 差异导致的等分与按内容比例分配的区别。 |
| 能做什么 | 检验候选人是否理解 `flex` 简写属性的展开值，以及 `flex-basis` 对空间分配的影响。 |
| 怎么用 | `flex: 1` 等分空间；`flex: auto` 按内容大小比例分配。 |
| 原理和工作流程 | `flex: 1` 的 `flex-basis: 0%` 使初始大小为 0，所有项目从同一基准开始等分剩余空间；`flex: auto` 的 `flex-basis: auto` 使项目先按内容大小占用空间，剩余空间再按 grow 权重分配。 |
| 缺点 | 回答时需注意 `flex: 1` 和 `flex: 1 1 auto` 的区别，以及 `flex: initial`（`0 1 auto`）的含义。 |

### 4. Flex 和 Grid 的区别？各自适用场景？

| 维度 | 内容 |
|------|------|
| 是什么 | 考查 Flex 一维布局和 Grid 二维布局的核心差异，以及各自的最佳适用场景。 |
| 能做什么 | 检验候选人是否能在实际项目中根据需求选择合适的布局方案，而非盲目使用其中一种。 |
| 怎么用 | Flex：一维排列（导航栏、列表）；Grid：二维布局（整体页面结构）。两者不互斥，常配合使用。 |
| 原理和工作流程 | Flex 沿单轴排列项目，适合内容驱动的动态布局；Grid 同时控制行列，适合布局驱动的精确网格。Flex 弹性计算在主轴方向；Grid 弹性计算在行和列两个方向。 |
| 缺点 | 回答时避免给出"Grid 更好"的绝对判断，两种方案各有适用场景，实际项目中常混合使用。 |

---

## 八、避坑指南

| 维度 | 内容 |
|------|------|
| 是什么 | 汇总 CSS 布局中 6 个高频错误：忘记 box-sizing、浮动高度塌陷、Flex 中 align-items 不生效、absolute 参照物错误、sticky 不生效、margin 导致布局溢出。 |
| 能做什么 | 帮助开发者快速排查和修复布局异常，减少调试时间。 |
| 怎么用 | 全局设置 `box-sizing: border-box`；使用 clearfix 或 BFC 清除浮动；给 Flex 容器设置明确高度；检查 absolute 祖先链设置 `position: relative`；确保 sticky 祖先无 `overflow: hidden`；使用 gap 替代 margin 设置间距。 |
| 原理和工作流程 | 每个错误对应一个底层渲染机制的理解偏差。例如 sticky 不生效是因为祖先的 `overflow: hidden` 破坏了滚动容器；Flex 的 align-items 需要容器有明确高度才能在交叉轴方向分配空间。 |
| 缺点 | 这些排查方案需要结合浏览器 DevTools 实际验证，不同浏览器版本可能表现不一致。 |

---

## 本章学习自检

本节为辅助内容，无五维表格。

---

> [返回原文](./02-CSS布局核心.md) | [返回模块目录](../README.md) | [返回知识导览](../知识导览.md)