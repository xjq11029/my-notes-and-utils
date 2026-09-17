# CSS 进阶与性能

> 模块：01-html-css（第1周 HTML/CSS 基础）
> 定位：CSS3 高级特性、响应式设计、性能优化，面试高频考点

---

## 一、CSS3 新特性

### 1.1 过渡（Transition）

过渡用于在 CSS 属性值变化时添加平滑的动画效果。

```css
/* 完整写法 */
.box {
    transition-property: width, background-color;
    transition-duration: 0.3s, 0.5s;
    transition-timing-function: ease, ease-in-out;
    transition-delay: 0s, 0.1s;
}

/* 简写：属性 时长 缓动 延迟 */
.box {
    transition: width 0.3s ease, background-color 0.5s ease-in-out 0.1s;
}

/* 常用缓动函数 */
/* ease：慢→快→慢（默认） */
/* linear：匀速 */
/* ease-in：慢→快 */
/* ease-out：快→慢 */
/* ease-in-out：慢→快→慢（比 ease 更平滑） */
/* cubic-bezier(n,n,n,n)：自定义贝塞尔曲线 */
```

**适用属性**：并非所有 CSS 属性都可过渡，常见可过渡属性包括 opacity、transform、color、background-color、width、height 等。display 属性不可过渡。

### 1.2 动画（Animation + @keyframes）

动画比过渡更强大，支持多阶段控制、循环播放、反向播放等。

```css
/* 定义关键帧 */
@keyframes slideIn {
    0% {
        transform: translateX(-100%);
        opacity: 0;
    }
    50% {
        opacity: 0.5;
    }
    100% {
        transform: translateX(0);
        opacity: 1;
    }
}

/* 应用动画 */
.box {
    animation-name: slideIn;
    animation-duration: 1s;
    animation-timing-function: ease;
    animation-delay: 0s;
    animation-iteration-count: infinite; /* 无限循环 / 可填数字 */
    animation-direction: alternate;       /* 正向→反向交替 */
    animation-fill-mode: forwards;        /* 动画结束后保持最后一帧 */
    animation-play-state: running;        /* running / paused */
}

/* 简写：名称 时长 缓动 延迟 次数 方向 填充模式 播放状态 */
.box {
    animation: slideIn 1s ease 0s infinite alternate forwards running;
}
```

**animation-fill-mode 详解**：

| 值 | 说明 |
|------|------|
| `none` | 默认，动画前后不应用任何样式 |
| `forwards` | 动画结束后保持最后一帧样式 |
| `backwards` | 在延迟期间应用第一帧样式 |
| `both` | 同时应用 forwards 和 backwards |

> 📖 **参考链接**：
> - [MDN - CSS 动画](https://developer.mozilla.org/zh-CN/docs/Web/CSS/CSS_animations)
> - [MDN - transition](https://developer.mozilla.org/zh-CN/docs/Web/CSS/transition)

### 1.3 变换（Transform）

变换用于对元素进行旋转、缩放、平移、倾斜等操作，**不触发回流**，性能优于修改 top/left/width/height。

```css
/* 平移 */
transform: translate(100px, 50px);       /* X轴100px, Y轴50px */
transform: translateX(100px);            /* 仅X轴 */
transform: translateY(50px);             /* 仅Y轴 */

/* 旋转 */
transform: rotate(45deg);                /* 顺时针旋转45度 */
transform: rotateX(180deg);              /* 绕X轴旋转 */
transform: rotateY(180deg);              /* 绕Y轴旋转 */

/* 缩放 */
transform: scale(1.5);                   /* 整体放大1.5倍 */
transform: scale(1.5, 0.8);              /* X轴1.5倍, Y轴0.8倍 */

/* 倾斜 */
transform: skew(10deg, 5deg);            /* X轴倾斜10度, Y轴倾斜5度 */

/* 组合变换（顺序很重要！从右往左执行） */
transform: translateX(100px) rotate(45deg) scale(1.5);

/* 3D 变换 */
transform: perspective(500px) rotateY(45deg);
transform-style: preserve-3d;            /* 子元素保留3D位置 */
```

### 1.4 CSS 视觉效果

```css
/* 阴影 */
box-shadow: 2px 4px 8px rgba(0, 0, 0, 0.2);          /* 水平偏移 垂直偏移 模糊半径 颜色 */
box-shadow: 0 0 0 3px #4A90D9;                        /* 模拟边框，不占盒模型空间 */
box-shadow: inset 0 2px 4px rgba(0, 0, 0, 0.1);      /* 内阴影 */
text-shadow: 1px 1px 2px rgba(0, 0, 0, 0.3);         /* 文字阴影 */

/* 圆角 */
border-radius: 8px;                                    /* 四个角统一 */
border-radius: 8px 16px 24px 32px;                    /* 左上 右上 右下 左下 */
border-radius: 50%;                                    /* 圆形 */

/* 渐变 */
background: linear-gradient(to right, #667eea, #764ba2);           /* 线性渐变 */
background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);     /* 角度渐变 */
background: radial-gradient(circle, #667eea, #764ba2);              /* 径向渐变 */
background: conic-gradient(from 45deg, #667eea, #764ba2, #667eea); /* 锥形渐变 */
```

> **生活化类比（层叠上下文与 z-index）**：楼层概念——每个层叠上下文是一栋楼里的一层，楼层之间**整体排序**：三楼的所有内容都在二楼之上，不管二楼里的座位号多大。`z-index` 只在**同一楼层内**决定先后顺序，数字越大越靠前。你不能在一楼坐个 999 号座位就盖过三楼的 1 号座位——楼层本身决定了大顺序，座位号只在同层内有效。

> 📖 **参考链接**：
> - [MDN - 层叠上下文](https://developer.mozilla.org/zh-CN/docs/Web/CSS/CSS_positioned_layout/Stacking_context)
> - [MDN - z-index](https://developer.mozilla.org/zh-CN/docs/Web/CSS/z-index)

### 1.5 CSS 变量（自定义属性）

```css
/* 定义：通常在 :root 中定义全局变量 */
:root {
    --primary-color: #4A90D9;
    --secondary-color: #764ba2;
    --spacing-unit: 8px;
    --border-radius: 4px;
    --font-size-base: 16px;
}

/* 使用 */
.button {
    background: var(--primary-color);
    padding: calc(var(--spacing-unit) * 2) calc(var(--spacing-unit) * 3);
    border-radius: var(--border-radius, 4px); /* 第二个参数为回退值 */
    font-size: var(--font-size-base);
}

/* 主题切换 */
[data-theme="dark"] {
    --primary-color: #1a1a2e;
    --text-color: #e0e0e0;
    --bg-color: #121212;
}
```

**CSS 变量的优势**：
- 方便主题切换和全局样式管理
- 支持运行时修改（JavaScript 动态设置）
- 具有继承性，子元素可以覆盖
- 可配合 `calc()` 进行动态计算

> 📖 **参考链接**：
> - [MDN - CSS 自定义属性](https://developer.mozilla.org/zh-CN/docs/Web/CSS/--*)
> - [MDN - var()](https://developer.mozilla.org/zh-CN/docs/Web/CSS/var)

---

## 二、响应式设计

### 2.1 媒体查询（@media）

```css
/* 基础语法 */
@media (max-width: 768px) {
    /* 屏幕宽度 <= 768px 时生效 */
}

@media (min-width: 769px) and (max-width: 1024px) {
    /* 屏幕宽度在 769px ~ 1024px 之间 */
}

/* 常见断点策略 */
/* 移动优先（Mobile First）：从小到大写 */
/* 基础样式（移动端） */
.sidebar { display: none; }
/* 平板 */
@media (min-width: 768px) {
    .sidebar { display: block; width: 200px; }
}
/* 桌面 */
@media (min-width: 1024px) {
    .sidebar { width: 250px; }
}

/* 桌面优先（Desktop First）：从大到小写 */
@media (max-width: 1024px) { /* 平板 */ }
@media (max-width: 768px)  { /* 手机 */ }

/* 其他媒体特性 */
@media (prefers-color-scheme: dark) { /* 系统暗色模式 */ }
@media (prefers-reduced-motion: reduce) { /* 用户偏好减少动画 */ }
@media (orientation: landscape) { /* 横屏 */ }
@media (hover: hover) { /* 支持 hover 的设备 */ }
```

### 2.2 相对单位

| 单位 | 参照物 | 说明 |
|------|------|------|
| `em` | 父元素的 `font-size` | 适合组件内相对尺寸，但嵌套会累积 |
| `rem` | 根元素 `<html>` 的 `font-size` | 推荐用于全局尺寸，不会累积 |
| `vh` | 视口高度的 1% | `100vh` = 视口高度 |
| `vw` | 视口宽度的 1% | `100vw` = 视口宽度 |
| `vmin` | vh 和 vw 中较小的 | 保证在横竖屏切换时都不会溢出 |
| `vmax` | vh 和 vw 中较大的 | 适合覆盖整个视口 |
| `dvh` / `svh` / `lvh` | 动态视口高度的 1% | 移动端解决 100vh 地址栏导致的计算不准确问题；dvh = 动态视口高度，svh = 小视口，lvh = 大视口 |
| `%` | 父元素的对应属性 | 不同属性参照不同（width 参照父 width，height 参照父 height） |

```css
/* rem 适配方案 */
html {
    font-size: 16px; /* 基准 */
}
@media (max-width: 768px) {
    html { font-size: 14px; }
}
.title { font-size: 2rem; } /* 32px → 28px 自动缩放 */

/* vw 适配方案 */
.hero { height: 100vh; }           /* 全屏高度 */
.card { width: calc(50vw - 20px); } /* 半屏宽度减去间距 */
```

### 2.3 移动端适配方案对比

| 方案 | 原理 | 优点 | 缺点 |
|------|------|------|------|
| rem + 动态设置根字体 | 根据屏幕宽度动态修改 `<html>` 的 font-size | 兼容性好，成熟方案 | 需要 JS 辅助，计算略复杂 |
| vw 方案 | 所有尺寸使用 vw 单位 | 纯 CSS，无需 JS | 需要大量计算，可能需要 PostCSS 插件 |
| rem + vw 混合 | 根字体用 vw，组件用 rem | 计算简单，灵活 | 需要理解两者的配合逻辑 |
| 媒体查询 + 弹性布局 | 不同断点不同样式 | 精确控制，无副作用 | 需要写多套样式，维护成本高 |

---

## 三、回流（Reflow）与重绘（Repaint）

> **本主题权威章节**：[完整讲解见 04-browser/01-浏览器渲染与V8原理.md](../04-browser/01-浏览器渲染与V8原理.md)；此处从 CSS 渲染视角展开要点。

### 3.1 概念与区别

```
回流（Reflow）：重新计算元素的几何属性（位置、尺寸），重新构建渲染树
重绘（Repaint）：元素外观改变（颜色、背景等），但几何属性不变，重新绘制像素
```

**回流一定触发重绘，重绘不一定触发回流**。回流的代价远大于重绘。

### 3.2 触发回流的操作

| 操作类型 | 具体行为 |
|---------|---------|
| 修改几何属性 | 修改 width、height、padding、margin、border、top、left、right、bottom |
| 修改显示 | 修改 display（none ↔ block） |
| 修改字体 | 修改 font-size、font-family |
| 修改内容 | 修改 innerHTML、innerText |
| 读取布局信息 | 读取 offsetHeight、offsetWidth、scrollTop、clientHeight、getComputedStyle() |
| 窗口变化 | 浏览器窗口 resize |
| 添加/删除 DOM | 插入或移除 DOM 节点 |

### 3.3 减少回流与重绘的策略

```css
/* 策略1：使用 transform 代替 top/left 做动画 */
/* 差：触发回流 */
.box { transition: left 0.3s; }
.box:hover { left: 100px; }

/* 好：仅触发合成（Composite），不触发回流重绘 */
.box { transition: transform 0.3s; }
.box:hover { transform: translateX(100px); }

/* 策略2：使用 will-change 提前告知浏览器 */
.smooth-animation {
    will-change: transform, opacity;
}

/* 策略3：使用 contain 属性隔离子树 */
.widget {
    contain: layout style paint; /* 告诉浏览器该元素子树独立 */
}
```

**JS 层面的优化**：

```javascript
// 策略4：批量修改 DOM，使用 DocumentFragment 或 display: none
const el = document.getElementById('list');
el.style.display = 'none';  // 先隐藏，脱离渲染树
// 进行大量 DOM 操作...
for (let i = 0; i < 1000; i++) {
    const li = document.createElement('li');
    li.textContent = `Item ${i}`;
    el.appendChild(li);
}
el.style.display = 'block';  // 操作完成后恢复显示（仅触发一次回流）

// 策略5：避免强制同步布局（读写分离）
// 差：交替读写触发多次强制回流
elements.forEach(el => {
    const h = el.offsetHeight;  // 读
    el.style.height = h + 10 + 'px';  // 写
});
// 好：先读后写
const heights = elements.map(el => el.offsetHeight);
elements.forEach((el, i) => {
    el.style.height = heights[i] + 10 + 'px';
});
```

> 📖 **参考链接**：
> - [MDN - will-change](https://developer.mozilla.org/zh-CN/docs/Web/CSS/will-change)
> - [MDN - CSS 性能优化](https://developer.mozilla.org/zh-CN/docs/Web/Performance/CSS_JavaScript_animation_performance)

---

## 四、CSS 性能优化

### 4.1 核心优化原则

| 优化方向 | 具体措施 |
|---------|---------|
| 减少回流重绘 | 使用 transform/opacity 做动画，批量修改 DOM，避免强制同步布局 |
| CSS 选择器效率 | 避免深层嵌套（不超过 3 层），减少通配符 `*` 的使用 |
| 避免 CSS 表达式 | CSS 表达式已废弃，不要在样式中使用 JavaScript |
| 避免 @import | @import 会阻塞并行下载，使用 `<link>` 标签替代 |
| 关键 CSS 内联 | 首屏关键 CSS 内联到 `<head>` 中，减少阻塞渲染 |
| 使用 will-change | 提前告知浏览器哪些属性会变化，让浏览器优化 |
| 使用 contain | 隔离元素的渲染范围，提升页面整体性能 |
| 压缩 CSS | 构建时使用 cssnano 等工具压缩 CSS 文件 |

### 4.2 CSS 选择器效率（从快到慢）

> **注意**：现代浏览器对选择器匹配做了大量优化，实际效率差异极小。以下排序仅作为理论参考，不应以牺牲可维护性为代价过度优化选择器。

```
ID 选择器 > 类选择器 > 标签选择器 > 相邻兄弟选择器 > 子选择器 > 后代选择器 > 通配符 > 属性选择器 > 伪类/伪元素
```

**浏览器匹配 CSS 选择器传统上是从右向左的**（现代浏览器已对此进行大量优化，但深层嵌套和宽泛的右侧选择器仍会增加匹配成本），因此避免过于宽泛的右侧选择器。

```css
/* 差：浏览器先找到所有 a 标签，再过滤出 .nav 后代 */
.nav a { }

/* 好：给 a 标签直接加类名 */
.nav-link { }
```

### 4.3 渲染性能对比

| 属性类型 | 触发阶段 | 性能开销 | 示例 |
|---------|:---:|:---:|------|
| 仅合成 | Composite | 最低 | `transform`, `opacity` |
| 重绘 | Paint + Composite | 中等 | `color`, `background-color`, `box-shadow`, `border-color` |
| 回流+重绘 | Layout + Paint + Composite | 最高 | `width`, `height`, `top`, `left`, `margin`, `padding`, `display` |

---

## 五、常见面试题

### 1. ★★ transition 和 animation 的区别？

**要点**：transition 需要事件触发（hover、click 等），只能定义开始和结束两种状态，适合简单过渡；animation 可以自动执行，支持多关键帧（@keyframes），支持循环、反向、暂停等高级控制，适合复杂动画。

### 2. ★★ 回流和重绘的区别？如何减少回流？

**要点**：回流重新计算几何属性（位置、尺寸），重绘只重新绘制外观（颜色等）。回流一定触发重绘，重绘不一定触发回流。减少策略：使用 transform 代替 top/left、批量修改 DOM、避免强制同步布局、使用 DocumentFragment、使用 will-change 提示浏览器。

### 3. ★★★ 为什么 transform 比 top/left 性能更好？

**要点**：transform 只触发 Composite（合成）阶段，不经过 Layout（布局）和 Paint（绘制）阶段；而 top/left 会触发完整的 Layout → Paint → Composite 流程。此外，transform 可以在 GPU 合成层上执行，利用硬件加速。

### 4. ★★ rem 和 em 的区别？

**要点**：rem 是相对于根元素 `<html>` 的 font-size，em 是相对于父元素的 font-size。rem 不会累积嵌套，适合全局尺寸控制；em 适合组件内部相对尺寸，但嵌套会累积放大。

### 5. ★★ 移动端适配方案有哪些？

**要点**：rem + 动态设置根字体（成熟方案）、vw 方案（纯 CSS）、rem + vw 混合、媒体查询 + 弹性布局。推荐使用 vw + rem 混合方案，兼顾灵活性和易用性。

---

## 六、避坑指南

| 常见错误 | 现象 | 原因 | 解决方案 |
|---------|------|------|---------|
| 用 top/left 做动画 | 页面卡顿、掉帧 | 触发回流，性能开销大 | 使用 `transform: translate()` 替代 |
| em 嵌套导致字号失控 | 嵌套元素字号越来越大 | em 参照父元素，多层嵌套会累积 | 使用 rem 替代 em，或仅在浅层嵌套使用 em |
| 媒体查询断点遗漏 | 某些屏幕尺寸下布局错乱 | 断点设置不完整 | 使用移动优先策略，逐步增强 |
| 忘记设置 will-change 又大量移除 | 内存占用过高 | will-change 创建独立合成层，长期保留会占内存 | 动画结束后移除 `will-change` |
| 使用 @import 引入 CSS | 页面加载变慢 | @import 会阻塞并行下载 | 使用 `<link>` 标签替代 |
| 大量使用 box-shadow 做动画 | 动画卡顿 | box-shadow 触发重绘，开销大 | 使用伪元素 + opacity 模拟阴影动画 |

---

## 七、CSS 新特性（追加章节）

### 7.1 CSS @supports 特性检测

`@supports` 用于检测浏览器是否支持某个 CSS 属性或值，是实现渐进增强（Progressive Enhancement）的核心工具。

```css
/* 基础语法：检测是否支持 display: grid */
@supports (display: grid) {
    .container {
        display: grid;
        grid-template-columns: repeat(3, 1fr);
    }
}

/* 检测是否支持某个属性值 */
@supports (position: sticky) {
    .header {
        position: sticky;
        top: 0;
    }
}

/* 组合检测：and / or / not */
@supports (display: grid) and (gap: 1rem) {
    .layout { gap: 1rem; }
}

@supports not (display: grid) {
    .container {
        display: flex;
        flex-wrap: wrap;
    }
}

/* 配合 CSS 变量做回退 */
.card {
    /* 回退值 */
    background: #f5f5f5;
    /* 浏览器支持 backdrop-filter 时使用高级效果 */
}
@supports (backdrop-filter: blur(10px)) {
    .card {
        background: rgba(255, 255, 255, 0.6);
        backdrop-filter: blur(10px);
    }
}

/* JS 中检测：CSS.supports() */
// JavaScript
if (CSS.supports('display', 'grid')) {
    console.log('支持 Grid');
}
```

**@supports vs @media 对比**：

| 对比维度 | @supports | @media |
|---------|----------|--------|
| 检测目标 | 浏览器是否支持某个 CSS 属性/值 | 设备特征（屏幕宽度、分辨率、方向等） |
| 典型用途 | 渐进增强，为支持的浏览器提供高级样式 | 响应式布局，根据屏幕尺寸切换样式 |
| 检测时机 | 运行时检测 CSS 引擎能力 | 匹配设备硬件/软件环境 |
| 逻辑运算 | `and`、`or`、`not` | `and`、`not`、`only`、`,`（或） |
| 示例 | `@supports (display: grid)` | `@media (max-width: 768px)` |
| 应用场景 | 新特性回退、浏览器兼容 | 多端适配、暗色模式、打印样式 |

**渐进增强实践**：先写基础样式（保证所有浏览器可用），再用 `@supports` 包裹增强样式（现代浏览器获得更好体验）。

```css
/* 基础：所有浏览器生效 */
.gallery { display: flex; flex-wrap: wrap; }
.gallery-item { width: calc(33.33% - 10px); margin: 5px; }

/* 增强：支持 Grid 的浏览器使用更强大的布局 */
@supports (display: grid) {
    .gallery {
        display: grid;
        grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
    }
    .gallery-item { width: auto; margin: 0; }
}
```

### 7.2 CSS scroll-snap 滚动吸附

`scroll-snap` 系列属性让滚动容器在滚动时自动吸附到指定位置，无需 JavaScript 即可实现原生轮播、卡片滑动等效果。

```css
/* 父容器：定义吸附行为 */
.scroll-container {
    /* 必须设置固定高度和 overflow */
    height: 100vh;
    overflow-y: scroll;

    /* scroll-snap-type: 轴 吸附严格度 */
    /*
      轴：x（水平）、y（垂直）、block（块轴）、inline（行内轴）、both（双向）
      吸附严格度：mandatory（强制吸附，始终定位到吸附点）、proximity（接近时吸附，距吸附点足够近才吸附）
    */
    scroll-snap-type: y mandatory;
}

/* 子元素：定义吸附对齐位置 */
.scroll-item {
    height: 100vh;
    /* scroll-snap-align: start（顶部对齐）/ center（居中对齐）/ end（底部对齐） */
    scroll-snap-align: start;
}

/* 水平吸附（卡片滑动） */
.horizontal-scroll {
    display: flex;
    overflow-x: auto;
    scroll-snap-type: x mandatory;
    gap: 16px;
    padding: 0 24px;
    /* 滚动结束后平滑吸附 */
    scroll-behavior: smooth;
}

.horizontal-scroll .card {
    flex: 0 0 300px;
    scroll-snap-align: start;
    /* 避免吸附到滚动条区域 */
    scroll-snap-stop: always;
}

/* 完整示例：原生全屏轮播 */
.slideshow {
    height: 100vh;
    overflow-y: scroll;
    scroll-snap-type: y mandatory;
    scroll-behavior: smooth;
}
.slide {
    height: 100vh;
    scroll-snap-align: start;
    display: flex;
    align-items: center;
    justify-content: center;
}
.slide:nth-child(1) { background: linear-gradient(135deg, #667eea, #764ba2); }
.slide:nth-child(2) { background: linear-gradient(135deg, #f093fb, #f5576c); }
.slide:nth-child(3) { background: linear-gradient(135deg, #4facfe, #00f2fe); }
```

```html
<!-- 对应 HTML 结构 -->
<div class="slideshow">
    <section class="slide"><h1>第一屏</h1></section>
    <section class="slide"><h1>第二屏</h1></section>
    <section class="slide"><h1>第三屏</h1></section>
</div>
```

**核心属性一览**：

| 属性 | 作用 | 常用值 |
|------|------|------|
| `scroll-snap-type` | 容器吸附方向与严格度 | `x mandatory`、`y proximity`、`both mandatory` |
| `scroll-snap-align` | 子元素吸附对齐点 | `start`、`center`、`end`、`none` |
| `scroll-snap-stop` | 是否强制停在当前元素 | `normal`（默认）、`always`（一次只滑一屏） |
| `scroll-padding` | 吸附时的偏移量（避开 fixed 元素） | 如 `scroll-padding-top: 60px` |
| `scroll-margin` | 子元素在吸附时的外边距 | 如 `scroll-margin-top: 20px` |

### 7.3 Container Queries 容器查询

容器查询允许根据**父容器**的尺寸（而非视口）来调整子元素样式，是实现组件级响应式布局的关键能力。

```css
/* 第1步：定义容器类型 */
.card-wrapper {
    /*
      container-type:
        inline-size：仅根据容器宽度响应（最常用）
        size：根据容器宽度和高度响应（需要显式高度）
        normal：不作为查询容器，但可被命名
    */
    container-type: inline-size;
    /* 容器名（可选），用于区分多个容器 */
    container-name: card;
}

/* 简写：container: 名称 / 类型 */
.card-wrapper {
    container: card / inline-size;
}

/* 第2步：使用 @container 查询容器尺寸 */
@container card (min-width: 400px) {
    .card {
        display: flex;
        flex-direction: row;
    }
    .card-image {
        width: 40%;
    }
}

@container (max-width: 399px) {
    .card {
        display: flex;
        flex-direction: column;
    }
    .card-image {
        width: 100%;
    }
}

/* 实际应用：组件级响应式 */
.media-object {
    container-type: inline-size;
    container-name: media;
}

@container media (min-width: 500px) {
    .media-body {
        display: grid;
        grid-template-columns: 200px 1fr;
    }
}

@container media (max-width: 499px) {
    .media-body {
        display: flex;
        flex-direction: column;
    }
}
```

**Container Queries vs @media 对比**：

| 对比维度 | Container Queries | @media |
|---------|------------------|--------|
| 参照物 | 父容器的尺寸 | 视口（viewport）尺寸 |
| 响应粒度 | 组件级（组件自身容器大小变化） | 页面级（屏幕大小变化） |
| 复用性 | 高：组件放到任何容器中都自适应 | 低：组件样式依赖全局视口 |
| 典型场景 | 组件库、自适应卡片、侧边栏中的列表 | 整体页面布局切换、断点适配 |
| 语法 | `@container [name] (条件)` | `@media (条件)` |
| 依赖 | 需要父元素设置 `container-type` | 无需额外设置 |
| 浏览器支持 | 较新（2023年广泛支持） | 全面支持 |

**两者配合使用**：`@media` 控制页面整体布局（侧边栏、网格），`@container` 控制组件内部布局（卡片、列表项在容器变窄时如何排列）。

### 7.4 CSS Layers @layer

`@layer` 允许开发者显式控制样式优先级（层叠顺序），解决因选择器特异性或加载顺序导致的样式冲突问题。

```css
/* 第1步：声明层的顺序（越后声明，优先级越高） */
@layer reset, base, components, utilities;

/* 第2步：向各层中写入样式 */
/* reset 层：最低优先级 */
@layer reset {
    * { margin: 0; padding: 0; box-sizing: border-box; }
    a { text-decoration: none; }
}

/* base 层 */
@layer base {
    body { font-family: sans-serif; line-height: 1.6; }
    h1 { font-size: 2rem; }
}

/* components 层 */
@layer components {
    .btn {
        padding: 8px 16px;
        border-radius: 4px;
        background: #4A90D9;
        color: #fff;
    }
}

/* utilities 层：最高优先级（最后声明） */
@layer utilities {
    .hidden { display: none !important; }
    .flex-center { display: flex; align-items: center; justify-content: center; }
}

/* 也可以内联到已有层 */
@layer components {
    .card {
        border: 1px solid #e0e0e0;
        border-radius: 8px;
    }
}

/* 未声明层优先级的样式位于“隐式外层”，优先级高于所有 @layer */
.no-layer {
    color: red; /* 这比任何 @layer 中的样式优先级都高 */
}
```

**!important 在 @layer 中的行为**：

```css
@layer base, components;

@layer base {
    .title { color: blue !important; }
}

@layer components {
    .title { color: red !important; }
}

/* 规则：!important 在 @layer 中反转——低优先级层中的 !important 反而更高 */
/* 即 base 中的 !important > components 中的 !important（与常规行为相反） */
/* 结果：base 层（先声明，优先级低）中的 !important 胜出，.title 为蓝色 */
```

**@layer 优先级模型对比**：

| 优先级来源 | 不含 @layer 的传统模型 | 含 @layer 的模型 |
|-----------|----------------------|-----------------|
| 最高 | `!important` 用户样式 | `!important` 在低优先级层（反转） |
| ^ | `!important` 作者样式 | `!important` 在高优先级层（反转） |
| ^ | 内联样式 `style=""` | 内联样式 `style=""` |
| ^ | ID 选择器 `#id` | 未分层样式（隐式外层） |
| ^ | 类/属性/伪类 `.class` | 高优先级层中的样式 |
| ^ | 元素/伪元素 `div` | 低优先级层中的样式 |
| 最低 | 通配符 `*` | 最低优先级层中的样式 |

**实际应用场景**：引入第三方 UI 库时，将库样式放在低优先级层，自定义样式放在高优先级层，无需使用 `!important` 或提高选择器特异性来覆盖。

```css
/* 典型项目结构 */
@layer third-party, reset, base, layout, components, overrides;

@layer third-party {
    /* 引入第三方库样式 */
}
@layer overrides {
    /* 覆盖第三方库和组件样式，无需 !important */
    .ant-btn { border-radius: 6px; }
}
```

### 7.5 CSS Nesting 原生嵌套

CSS Nesting 允许在 CSS 中直接嵌套规则，无需依赖 Sass/Less 等预处理器。

```css
/* 基础嵌套 */
.card {
    background: #fff;
    border-radius: 8px;

    /* & 代表父选择器 .card */
    & .title {
        font-size: 1.25rem;
        font-weight: 600;
    }

    /* 伪类嵌套 */
    &:hover {
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
    }

    /* 伪元素嵌套 */
    &::before {
        content: '';
        display: block;
    }

    /* 组合选择器 */
    &.active {
        border-color: #4A90D9;
    }

    /* 媒体查询嵌套 */
    @media (max-width: 768px) {
        border-radius: 4px;
    }

    /* 属性选择器 */
    &[data-variant="outlined"] {
        background: transparent;
        border: 2px solid currentColor;
    }
}

/* 复杂嵌套示例 */
.nav {
    display: flex;

    & > li {
        position: relative;

        & > a {
            display: block;
            padding: 8px 16px;

            &:hover {
                background: #f0f0f0;
            }
        }

        & .dropdown {
            display: none;
        }

        &:hover .dropdown {
            display: block;
        }
    }
}
```

**CSS Nesting vs Sass/Less 嵌套对比**：

| 对比维度 | CSS Nesting | Sass / Less |
|---------|------------|-------------|
| 编译需要 | 无需编译，浏览器原生支持 | 需要编译为 CSS |
| `&` 符号 | 必须显式使用 `&` 开头（除 `@` 规则外） | Sass 可省略 `&`、Less 可省略 `&` |
| 类型选择器嵌套 | 必须用 `&` 或 `:is()` 包裹（如 `& li`） | 可直接写 `li` |
| 嵌套深度 | 推荐不超过 3 层 | 推荐不超过 3 层 |
| `@media` 嵌套 | 支持 | 支持 |
| 变量 | 使用 CSS 变量 `var(--x)` | 使用 Sass 变量 `$x` 或 Less 变量 `@x` |
| 混入（Mixin） | 不支持 | 支持 `@mixin` / `.mixin()` |
| 函数 | 不支持 | 支持自定义函数 |
| 浏览器支持 | 2023 年后逐步支持 | 始终可用（编译后为普通 CSS） |

**注意事项**：
- 原生嵌套中，类型选择器（如 `h1`）前必须加 `&` 或 `:is()`，否则浏览器会将其解析为无效选择器。
- 原生嵌套不能替代预处理器的所有功能（如 mixin、函数、循环），但能覆盖最常见的嵌套场景。
- 对于已有 Sass/Less 项目的现代浏览器，可以逐步迁移到原生嵌套以减少构建依赖。

### 7.6 :has() 选择器（父选择器）

`:has()` 是 CSS 的"父选择器"，允许根据子元素的状态来选中父元素，实现了 CSS 选择器历史上缺失的"向上选择"能力。

```css
/* 基础：选中包含图片的卡片 */
.card:has(> img) {
    padding: 0;
    overflow: hidden;
}

/* 选中包含特定子元素的父元素 */
article:has(> .video) {
    background: #000;
    color: #fff;
}

/* 表单验证联动：输入框无效时高亮整个表单组 */
.form-group:has(:invalid) {
    border-left: 3px solid #e74c3c;
}

.form-group:has(:valid) {
    border-left: 3px solid #2ecc71;
}

/* 表单组内有错误提示时 */
.form-group:has(.error-message) .label {
    color: #e74c3c;
}

/* 聚焦状态联动：输入框聚焦时改变父容器样式 */
.form-group:has(:focus) {
    box-shadow: 0 0 0 2px rgba(74, 144, 217, 0.3);
    border-color: #4A90D9;
}

/* 包含选中项的容器 */
.list:has(:checked) {
    background: #f0f8ff;
}

/* 相邻兄弟联动：某个元素有特定兄弟时调整 */
h2:has(+ p) {
    margin-bottom: 4px;
}

/* 灯箱效果：当弹窗出现时隐藏页面滚动 */
body:has(.modal[open]) {
    overflow: hidden;
}

/* 空状态检测：侧边栏为空时隐藏 */
.sidebar:has(:empty) {
    display: none;
}

/* 复杂组合：卡片有图片且正在被 hover */
.card:has(> img):hover {
    transform: translateY(-4px);
    box-shadow: 0 8px 24px rgba(0, 0, 0, 0.15);
}

/* 实际应用：表格行操作 */
tr:has(input:checked) {
    background: #e8f4fd;
}

/* 导航栏子菜单联动 */
.nav-item:has(.submenu:hover) {
    background: #f0f0f0;
}
```

**:has() 的典型应用场景**：

| 场景 | 代码示例 | 效果 |
|------|---------|------|
| 父元素跟随子元素状态 | `.card:has(> img)` | 包含图片的卡片调整内边距 |
| 表单验证联动 | `.form-group:has(:invalid)` | 无效输入项高亮整个表单组 |
| 聚焦联动 | `.form-group:has(:focus)` | 聚焦时父容器边框高亮 |
| 全局状态联动 | `body:has(.modal[open])` | 弹窗出现时锁定页面滚动 |
| 空状态处理 | `.sidebar:has(:empty)` | 侧边栏无内容时自动隐藏 |
| 选中态联动 | `tr:has(:checked)` | 表格行选中时高亮背景 |
| 后代影响祖先 | `section:has(.dark) { background: #000; }` | 子元素含 .dark 时切换背景 |

**面试要点**：`:has()` 打破了 CSS 选择器只能"向下选择"的限制，但它仍是**纯 CSS 选择器**，不涉及 JavaScript，且性能经过浏览器优化。`:has()` 的匹配逻辑是"样式不回溯"，即父子关系一旦确定，`:has()` 不会造成无限循环的样式计算。

---

## 八、CSS 工具链（了解即可）

> 本章节为扩展知识，了解不同工具链的定位与适用场景即可，面试中能说出核心概念和对比即为加分项。

### 8.1 Sass / Less

Sass 和 Less 是 CSS 预处理器，在 CSS 语法基础上扩展了变量、嵌套、混入、函数等能力，最终编译为浏览器可识别的标准 CSS。

**Sass 语法（SCSS 格式）**：

```scss
// 变量：使用 $ 符号
$primary-color: #4A90D9;
$spacing: 8px;
$breakpoints: (
    'sm': 576px,
    'md': 768px,
    'lg': 1024px,
);

// 嵌套：使用 & 符号引用父选择器
.nav {
    display: flex;
    background: $primary-color;

    &-item {
        padding: $spacing * 2;
        color: #fff;

        &:hover {
            background: darken($primary-color, 10%);
        }

        &.active {
            background: darken($primary-color, 20%);
        }
    }
}

// 混入（Mixin）：可复用的样式块，支持参数
@mixin flex-center($direction: row, $gap: 0) {
    display: flex;
    flex-direction: $direction;
    align-items: center;
    justify-content: center;
    gap: $gap;
}

// 使用混入
.card {
    @include flex-center(column, 16px);
    padding: 16px;
}

// 函数：进行值计算
@function rem($px) {
    @return ($px / 16) * 1rem; // 编译为 1.5rem
}

.title {
    font-size: rem(24); // 编译为 1.5rem
}

// 继承（Extend）：共享选择器规则
%btn-base {
    padding: 8px 16px;
    border-radius: 4px;
    border: none;
    cursor: pointer;
}

.btn-primary {
    @extend %btn-base;
    background: $primary-color;
    color: #fff;
}

.btn-danger {
    @extend %btn-base;
    background: #e74c3c;
    color: #fff;
}
```

**Less 语法**：

```less
// 变量：使用 @ 符号
@primary-color: #4A90D9;
@spacing: 8px;

// 嵌套：与 Sass 语法一致
.nav {
    display: flex;

    &-item {
        padding: @spacing * 2;

        &:hover {
            background: darken(@primary-color, 10%);
        }
    }
}

// 混入：通过 .mixin() 定义，直接调用
.flex-center(@direction: row, @gap: 0) {
    display: flex;
    flex-direction: @direction;
    align-items: center;
    justify-content: center;
    gap: @gap;
}

.card {
    .flex-center(column, 16px);
}
```

**Sass vs Less 对比**：

| 对比维度 | Sass（SCSS） | Less |
|---------|-------------|------|
| 变量符号 | `$var` | `@var` |
| 混入定义 | `@mixin name` + `@include name` | `.name()` 直接调用 |
| 函数 | 支持 `@function` 自定义函数 | 不支持自定义函数（仅内置函数） |
| 继承 | `@extend` + `%placeholder` | `:extend()` 伪类 |
| 条件语句 | `@if`、`@else`、`@each`、`@for`、`@while` | `when()` 守卫表达式 |
| 内置函数 | 丰富（颜色操作、数学、字符串等） | 较少 |
| 生态 | 更强大，社区活跃 | 较简洁，学习成本低 |
| 编译库 | Dart Sass（推荐）/ LibSass / node-sass | less（JavaScript） |
| 适用场景 | 大型项目、复杂主题系统 | 中小型项目、简单主题定制 |

### 8.2 Tailwind CSS

Tailwind CSS 是**原子化 CSS（Atomic CSS）**框架，核心理念是 "utility-first"（工具类优先），通过直接在 HTML 中组合大量单一职责的工具类来构建界面，而非编写自定义 CSS。

```html
<!-- 传统方式：自定义类名 + 独立 CSS -->
<div class="card">
    <h2 class="card-title">标题</h2>
</div>

<!-- Tailwind 方式：直接在 HTML 中组合工具类 -->
<div class="bg-white rounded-lg shadow-md p-6 hover:shadow-xl transition-shadow">
    <h2 class="text-xl font-bold text-gray-800 mb-2">标题</h2>
    <p class="text-gray-600 text-sm">描述文字</p>
</div>
```

**核心特性**：

```html
<!-- 响应式前缀：sm: / md: / lg: / xl: / 2xl: -->
<div class="
    w-full           <!-- 移动端：全宽 -->
    sm:w-1/2         <!-- >= 640px：半宽 -->
    md:w-1/3         <!-- >= 768px：1/3 宽 -->
    lg:w-1/4         <!-- >= 1024px：1/4 宽 -->
">
    <p class="text-base md:text-lg lg:text-xl">响应式文字</p>
</div>

<!-- 状态变体：hover: / focus: / active: / disabled: / dark: -->
<button class="
    bg-blue-500 hover:bg-blue-600 focus:ring-2 focus:ring-blue-300
    text-white font-medium py-2 px-4 rounded
    disabled:opacity-50 disabled:cursor-not-allowed
">
    提交
</button>

<!-- 暗色模式：dark: 前缀 -->
<div class="bg-white dark:bg-gray-800 text-gray-900 dark:text-gray-100">
    自动适配暗色模式
</div>
```

**自定义配置（tailwind.config.js）**：

```javascript
// tailwind.config.js
module.exports = {
    content: ['./src/**/*.{html,js,ts,jsx,tsx}'],
    theme: {
        extend: {
            colors: {
                primary: '#4A90D9',
                secondary: '#764ba2',
            },
            spacing: {
                '18': '4.5rem',
                '88': '22rem',
            },
            fontFamily: {
                sans: ['Inter', 'sans-serif'],
            },
        },
    },
    plugins: [],
};
```

**@apply 指令**：将工具类组合为可复用的组件样式（用于提取重复模式）。

```css
/* 使用 @apply 提取重复的工具类组合 */
@layer components {
    .btn-primary {
        @apply bg-blue-500 text-white font-medium py-2 px-4 rounded
               hover:bg-blue-600 focus:ring-2 focus:ring-blue-300
               disabled:opacity-50 disabled:cursor-not-allowed
               transition-colors;
    }

    .card {
        @apply bg-white rounded-lg shadow-md p-6
               dark:bg-gray-800 dark:text-gray-100;
    }
}
```

**优缺点**：

| 优点 | 缺点 |
|------|------|
| 开发速度快，无需在 CSS 和 HTML 间切换 | HTML 可能变得冗长，类名堆积 |
| 统一的约束设计系统（间距、颜色、字号） | 需要学习大量工具类命名 |
| 构建时自动 Tree-shaking，仅保留使用的类 | 缺少传统"语义化类名"的可读性 |
| 响应式设计极其方便 | 对复杂 CSS 动画支持有限 |
| 团队协作一致性好（设计令牌化） | 初始配置成本（自定义主题） |

**Tailwind CSS v4 @theme 配置方式**：

Tailwind CSS v4 引入 `@theme` 指令替代传统的 `tailwind.config.js` 文件，直接在 CSS 中声明设计令牌，配置更加简洁直观。v4 同时引入 Oxide 引擎（Rust 重写），性能提升 10 倍以上。

**v3 vs v4 核心变化**：

| 维度 | v3 | v4 |
|------|------|------|
| 引擎 | JavaScript（PostCSS 插件） | Rust 原生引擎（Oxide），速度提升 10 倍+ |
| 配置方式 | `tailwind.config.js` | CSS `@theme` 指令 |
| 框架集成 | 通过 PostCSS 插件 | 原生 Vite 插件（`@tailwindcss/vite`） |
| 暗色模式 | `darkMode: 'class'` | 原生支持 `light-dark()` 和 `color-scheme` |
| CSS 层级 | 手动管理 | 自动使用 CSS `@layer` 管理优先级 |

```css
/* Tailwind CSS v4：@theme 配置方式 */
@import "tailwindcss";

@theme {
  --color-brand: #4f46e5;
  --color-brand-light: #818cf8;
  --font-size-hero: 3rem;
  --spacing-page: 2rem;
  --breakpoint-tablet: 768px;
}
```

```javascript
// vite.config.js - Vite 中使用 Tailwind CSS v4
import { defineConfig } from 'vite'
import tailwindcss from '@tailwindcss/vite'

export default defineConfig({
  plugins: [
    tailwindcss(), // 原生 Vite 插件，无需 PostCSS 配置
  ]
})
```

**v3 -> v4 迁移要点**：
- 安装 `@tailwindcss/vite` 替代 `tailwindcss` PostCSS 插件
- 将 `tailwind.config.js` 中的配置迁移到 CSS 的 `@theme` 块
- 颜色类名语法不变（`bg-primary` 等），向后兼容
- 移除 `tailwind.config.js` 文件，所有配置集中在 CSS 中管理

### 8.3 CSS Modules

CSS Modules 是**组件级样式隔离**方案，通过构建工具（如 Webpack、Vite）将 CSS 类名自动转换为唯一的哈希类名，从根本上避免全局样式冲突。

```css
/* Button.module.css */
.button {
    padding: 8px 16px;
    border-radius: 4px;
    border: none;
    cursor: pointer;
}

.primary {
    background: #4A90D9;
    color: #fff;
}

/* composes：组合已有样式 */
.danger {
    composes: button;
    background: #e74c3c;
    color: #fff;
}

/* :global 声明全局样式（不被哈希化） */
:global(.ant-btn) {
    border-radius: 6px;
}
```

```tsx
// Button.tsx（React 中使用）
import styles from './Button.module.css';

const Button = ({ variant = 'primary', children }) => {
    return (
        <button className={`${styles.button} ${styles[variant]}`}>
            {children}
        </button>
    );
};

// 编译后的 HTML：
// <button class="Button_button_abc123 Button_primary_xyz789">点击</button>
```

**CSS Modules vs CSS-in-JS 对比**：

| 对比维度 | CSS Modules | CSS-in-JS（styled-components 等） |
|---------|------------|----------------------------------|
| 样式书写 | 独立 .module.css 文件 | 在 JS/TS 文件中书写 |
| 隔离机制 | 编译时哈希化类名 | 运行时生成唯一类名或 `<style>` 标签 |
| 动态样式 | 通过切换类名或 CSS 变量 | 直接使用 JS 变量和 props |
| 运行时开销 | 无（编译时处理） | 有（运行时注入样式） |
| 学习成本 | 低（就是写 CSS） | 中（需要学习库的 API） |
| 适用场景 | 传统 CSS 开发者、性能敏感项目 | 强动态样式需求、组件库 |
| 与标准 CSS 关系 | 完全兼容，可直接使用 CSS 生态 | 语法略有差异 |

---

## 九、CSS 组织与命名规范（了解即可）

> 本章节为扩展知识，了解各方法论核心理念即可，面试中能说出 BEM 的命名规则和主要方法论对比即为加分项。

### 9.1 BEM 命名规范

BEM 是 **Block（块）\_\_Element（元素）--Modifier（修饰符）** 的命名约定，通过严格的命名规则解决 CSS 命名冲突和样式作用域问题。

**命名规则**：

```
.block                    // 块：独立、有意义的组件
.block__element           // 元素：块内部的组成部分（双下划线 __）
.block--modifier          // 修饰符：块或元素的状态/变体（双连字符 --）
.block__element--modifier // 元素修饰符
```

**完整示例**：

```html
<!-- BEM 命名示例：搜索表单组件 -->
<div class="search-form search-form--compact">
    <div class="search-form__header">
        <h2 class="search-form__title">高级搜索</h2>
    </div>
    <div class="search-form__body">
        <input class="search-form__input search-form__input--large" type="text" placeholder="请输入关键词" />
        <button class="search-form__button search-form__button--primary">搜索</button>
        <button class="search-form__button search-form__button--disabled" disabled>重置</button>
    </div>
    <div class="search-form__footer search-form__footer--hidden">
        <span class="search-form__count">共 0 条结果</span>
    </div>
</div>
```

```css
/* BEM 对应的 CSS */
.search-form { padding: 16px; border: 1px solid #e0e0e0; }
.search-form--compact { padding: 8px; }
.search-form__header { margin-bottom: 12px; }
.search-form__title { font-size: 18px; font-weight: 600; }
.search-form__input { padding: 8px; border: 1px solid #ccc; border-radius: 4px; }
.search-form__input--large { padding: 12px; font-size: 16px; }
.search-form__button { padding: 8px 16px; border: none; border-radius: 4px; cursor: pointer; }
.search-form__button--primary { background: #4A90D9; color: #fff; }
.search-form__button--disabled { opacity: 0.5; cursor: not-allowed; }
.search-form__footer--hidden { display: none; }
```

**BEM 的优缺点**：

| 优点 | 缺点 |
|------|------|
| 命名具有语义，一看就懂结构关系 | 类名较长，HTML 略显冗长 |
| 天然避免全局命名冲突 | 嵌套层级过深时命名冗长 |
| 无需任何工具或框架支持 | 修饰符较多时组合爆炸 |
| 适合团队协作，约定清晰 | 对小型项目可能过于繁琐 |

### 9.2 OOCSS（面向对象 CSS）

OOCSS 由 Nicole Sullivan 提出，核心理念是**将 CSS 视为可复用的"对象"**，遵循两条核心原则：

**原则一：分离结构与皮肤（Separate Structure and Skin）**

```css
/* 结构（可复用） */
.card {
    padding: 16px;
    border-radius: 8px;
    border: 1px solid #e0e0e0;
}

/* 皮肤（按需组合） */
.skin-default {
    background: #fff;
    color: #333;
}
.skin-highlight {
    background: #fff3cd;
    border-color: #ffc107;
}
.skin-dark {
    background: #333;
    color: #fff;
}
```

```html
<!-- 组合使用 -->
<div class="card skin-default">默认卡片</div>
<div class="card skin-highlight">高亮卡片</div>
<div class="card skin-dark">深色卡片</div>
```

**原则二：分离容器与内容（Separate Container and Content）**

```css
/* 差：内容样式依赖容器 */
.sidebar h2 { font-size: 18px; }
.main h2 { font-size: 24px; }

/* 好：内容样式独立，不依赖容器 */
.heading-sm { font-size: 18px; }
.heading-lg { font-size: 24px; }
```

### 9.3 SMACSS（可扩展模块化 CSS 架构）

SMACSS 由 Jonathan Snook 提出，将 CSS 规则按**职责**分为五类：

| 类别 | 前缀/命名 | 说明 | 示例 |
|------|----------|------|------|
| **Base**（基础） | 无前缀，元素选择器 | 重置默认样式、设置基础排版 | `body { font-family: sans-serif; }`、`a { color: #4A90D9; }` |
| **Layout**（布局） | `l-` 或 `layout-` 前缀 | 页面级布局，如网格、侧边栏 | `.l-sidebar { width: 250px; }`、`.l-grid { display: grid; }` |
| **Module**（模块） | 模块名作为前缀 | 可复用的独立组件 | `.card { }`、`.card-title { }`、`.btn { }` |
| **State**（状态） | `is-` 或 `has-` 前缀 | 模块或布局的运行时状态 | `.is-active { }`、`.is-hidden { }`、`.has-error { }` |
| **Theme**（主题） | `theme-` 前缀 | 主题色彩、字体等全局视觉 | `.theme-dark { }`、`.theme-light { }` |

```css
/* SMACSS 示例 */
/* Base */
html, body { margin: 0; padding: 0; }

/* Layout */
.l-container { max-width: 1200px; margin: 0 auto; }
.l-header { position: sticky; top: 0; }

/* Module */
.modal { position: fixed; background: #fff; }
.modal-header { padding: 16px; border-bottom: 1px solid #e0e0e0; }
.modal-body { padding: 16px; }

/* State */
.is-open { display: block; }
.is-loading { opacity: 0.6; pointer-events: none; }
.has-dropdown { position: relative; }

/* Theme */
.theme-dark { --bg: #121212; --text: #e0e0e0; }
```

### 9.4 ITCSS（倒三角 CSS 架构）

ITCSS 由 Harry Roberts 提出，将 CSS 按**从通用到具体、从低特异性到高特异性**分为七层，形状如同倒三角形：

```
         Settings（设置层）         ← 最通用，影响范围最大
        ↙
       Tools（工具层）
      ↙
     Generic（通用层）
    ↙
   Base（基础层）
  ↙
 Objects（对象层）
↙
Components（组件层）
↙
Trumps（覆盖层）                  ← 最具体，特异性最高（通常含 !important）
```

**七层结构详解**：

| 层级 | 说明 | 典型内容 |
|------|------|---------|
| **Settings** | 全局变量和配置，不输出 CSS | Sass 变量：`$font-size-base`、`$color-primary`、断点配置 |
| **Tools** | 工具函数和混入，不输出 CSS | `@mixin`、`@function`（如 `rem()`、`media-query()`） |
| **Generic** | 重置和标准化样式 | `reset.css`、`normalize.css`、`box-sizing: border-box` |
| **Base** | 裸 HTML 元素的基础样式 | `body`、`h1`-`h6`、`a`、`p` 等无类名选择器样式 |
| **Objects** | 无装饰的布局模式（OOCSS 对象） | `.o-container`、`.o-grid`、`.o-media`（纯布局，无颜色/字体） |
| **Components** | 可识别的 UI 组件 | `.c-card`、`.c-btn`、`.c-modal`、`.c-nav`（有具体外观） |
| **Trumps** | 覆盖层，最高特异性 | `.u-hidden`、`.u-text-center`、`.u-mt-0`（通常含 `!important`） |

```css
/* ITCSS 文件名约定（按层级加载） */
/* 1-settings/_variables.scss    */  $primary: #4A90D9;
/* 2-tools/_mixins.scss          */  @mixin respond-to($bp) { ... }
/* 3-generic/_reset.scss         */  *, *::before, *::after { box-sizing: border-box; }
/* 4-base/_typography.scss       */  h1 { font-size: 2rem; }
/* 5-objects/_container.scss     */  .o-container { max-width: 1200px; margin: 0 auto; }
/* 6-components/_button.scss     */  .c-btn { padding: 8px 16px; border-radius: 4px; }
/* 7-trumps/_utilities.scss      */  .u-hidden { display: none !important; }
```

### 9.5 各方法论对比

| 方法论 | 核心理念 | 复杂度 | 适用场景 |
|-------|---------|:---:|---------|
| **BEM** | 严格的块-元素-修饰符命名约定 | 低 | 中大型项目，团队协作，需要清晰命名规范 |
| **OOCSS** | 面向对象思想，分离结构与皮肤 | 低 | 需要高度复用样式的项目，组件库 |
| **SMACSS** | 按职责分类（Base/Layout/Module/State/Theme） | 中 | 中大型项目，需要清晰的组织结构 |
| **ITCSS** | 按特异性分层，从通用到具体 | 高 | 大型项目，复杂的样式架构，多人协作 |
| **CSS Modules** | 构建时自动哈希化类名，组件级隔离 | 低 | 组件化框架（React/Vue），需要样式隔离 |
| **Tailwind** | 原子化工具类，utility-first | 中 | 快速开发，设计系统约束，团队一致性 |

### 9.6 实践意义

**大规模 CSS 可维护性的核心挑战**：

1. **命名冲突**：全局作用域下，相同类名会互相覆盖。BEM 通过命名约定缓解，CSS Modules 通过哈希化从根本解决。
2. **特异性战争**：多个选择器竞争同一元素时，不得不使用更高特异性的选择器或 `!important`。ITCSS 的层级设计天然避免了这一问题。
3. **代码复用**：相同的样式模式在不同组件中重复出现，导致 CSS 体积膨胀。OOCSS 的对象化思维和 Tailwind 的原子化工具类都致力于解决复用问题。
4. **团队协作**：多人同时编写 CSS 时，缺乏统一规范会导致样式混乱。方法论提供了统一的"语言"和"边界"。

**选择建议**：

```
小型项目 / 个人项目  → BEM 命名 + 基础变量
中型项目 / 小团队    → BEM + CSS Modules / Tailwind
大型项目 / 多人协作  → ITCSS 架构 + CSS Modules / Tailwind
组件库 / 微前端      → CSS Modules（隔离性）+ Design Tokens
```

> **核心观念**：无论选择哪种方法论，最重要的是**团队统一执行**。方法论本身不产生价值，**一致性**才产生价值。一个严格执行的 BEM 项目远比一个混乱的 ITCSS 项目更易维护。

---

## CSS 渲染性能优化：contain 与 content-visibility

### CSS `contain` 属性

`contain` 属性是 CSS 渲染性能优化的核心属性之一，它允许开发者显式地告诉浏览器：该元素的内部布局、样式、绘制、尺寸与外部完全隔离。浏览器可以据此跳过不必要的计算，大幅提升渲染性能。

**核心原理**：正常情况下，浏览器渲染一个元素时需要考虑它对外部的影响（如子元素是否溢出、外部样式是否穿透等）。`contain` 属性明确声明了隔离边界，浏览器可以放心地优化。

#### 各属性值详解

| 值 | 隔离范围 | 行为说明 |
|----|---------|---------|
| `none` | 无 | 不施加任何隔离（默认值） |
| `layout` | 布局 | 元素内部布局变化不影响外部元素；外部布局变化也不影响元素内部；元素成为一个独立的格式化上下文（类似 BFC） |
| `style` | 样式 | 计数器（`counter-increment`、`counter-reset`）和 `quotes` 属性的作用范围被限制在元素内部，不会影响外部计数 |
| `paint` | 绘制 | 元素的后代节点不会绘制在元素边界框之外（类似 `overflow: hidden` 但对滚动有不同处理）；元素成为绝对定位和固定定位后代的包含块 |
| `size` | 尺寸 | 元素尺寸的计算不依赖其后代内容；浏览器可以跳过子元素的布局计算来获取元素尺寸，直接使用当前尺寸 |
| `content` | 布局+样式+绘制 | 复合值，等同于 `contain: layout style paint`。这是最常用的实用值 |
| `strict` | 布局+样式+绘制+尺寸 | 复合值，等同于 `contain: layout style paint size`。施加所有隔离，最严格 |

#### 代码示例

```css
/* 性能优化：长列表中的每个列表项 */
.list-item {
  contain: content; /* layout + style + paint */
}

/* 严格隔离：已知尺寸的独立组件 */
.widget {
  width: 300px;
  height: 200px;
  contain: strict; /* 完全隔离，尺寸不依赖内容 */
}

/* 仅隔离布局：减少重排影响范围 */
.sidebar {
  contain: layout;
}

/* 仅隔离绘制：优化滚动性能 */
.scrollable-section {
  contain: paint;
}
```

#### 何时使用

| 场景 | 推荐值 | 原因 |
|------|--------|------|
| 列表项（已知尺寸） | `contain: content` | 列表项内容变化时不会触发整体重排 |
| 独立组件/Widget | `contain: strict` | 组件尺寸固定，内部变化不影响外部 |
| 可滚动容器 | `contain: paint` | 优化滚动绘制性能，避免滚动区域外的内容被绘制 |
| 侧边栏/导航栏 | `contain: layout` | 侧边栏内容变化不影响主内容区布局 |

#### 注意事项

- 使用 `contain: paint` 的元素将成为新的层叠上下文，可能影响 `z-index` 管理
- 使用 `contain: size` 时，元素尺寸如果未显式设置，可能塌缩为 0（因为浏览器不再根据子元素计算尺寸）
- 使用 `contain: strict` 时，必须显式设置元素的 `width` 和 `height`
- `contain` 属性在主流现代浏览器中广泛支持（Chrome 52+、Firefox 69+、Safari 15.4+）

### CSS `content-visibility` 属性

`content-visibility` 是 CSS Containment Level 2 规范中引入的更强力性能优化属性，它允许浏览器**跳过不在视口内元素的渲染工作**，包括布局、绘制和合成。这是一项自动化的懒渲染机制。

#### 属性值

| 值 | 行为 |
|----|------|
| `visible` | 正常渲染，无任何优化（默认值） |
| `auto` | 浏览器自动跳过不在视口内元素的渲染；当元素接近视口时自动渲染 |
| `hidden` | 强制跳过渲染，类似 `display: none` 但保留布局状态和滚动位置 |

#### `content-visibility: auto` 详解

这是最具实用价值的值。当元素在视口外时，浏览器完全跳过其渲染（甚至不计算布局），但保留其占位尺寸。当元素滚动接近视口时，浏览器自动渲染该元素。

```css
/* 长页面中每个独立区块 */
.section {
  content-visibility: auto;
  contain-intrinsic-size: 0 500px; /* 提供占位尺寸，防止滚动条跳动 */
}
```

**`contain-intrinsic-size`** 是与 `content-visibility: auto` 配合的关键属性，用于为未渲染的元素提供预估占位尺寸：

```css
.section {
  content-visibility: auto;
  /* 语法：contain-intrinsic-size: <width> <height> */
  contain-intrinsic-size: 1000px 600px;
  
  /* 也可以设置 auto 关键字，让浏览器记住上次渲染时的实际尺寸 */
  contain-intrinsic-size: auto 600px;
}
```

#### 性能收益

- **大幅减少初始渲染时间**：长页面（如新闻文章、博客列表）中，`content-visibility: auto` 可将初始渲染时间减少 50%-90%
- **减少内存占用**：视口外的元素不渲染，DOM 节点仍在但渲染树更小
- **改善交互响应**：主线程不会因为渲染视口外内容而阻塞

#### 适用场景

```css
/* 博客文章列表 */
.blog-post-card {
  content-visibility: auto;
  contain-intrinsic-size: 0 300px;
}

/* 图片画廊 */
.gallery-item {
  content-visibility: auto;
  contain-intrinsic-size: 0 250px;
}

/* 长页面中的独立 Section */
.page-section {
  content-visibility: auto;
  contain-intrinsic-size: auto 600px;
}
```

#### `content-visibility: hidden` 与 `display: none` 的区别

| 特性 | `content-visibility: hidden` | `display: none` |
|------|------------------------------|-----------------|
| DOM 存在 | 是 | 是 |
| 布局保持 | 是（保留占位空间） | 否（完全脱离文档流） |
| 渲染跳过 | 是 | 是 |
| 滚动位置保持 | 是 | 否 |
| 适用场景 | 虚拟滚动、Tab 切换 | 条件隐藏 |

#### 浏览器兼容性

- `content-visibility: auto`：Chrome 85+、Edge 85+、Opera 71+；Firefox 125+ 支持；Safari 18.2+ 支持
- `contain-intrinsic-size`：Chrome 95+、Edge 95+、Firefox 107+、Safari 17+

> **实践建议**：`content-visibility: auto` 是渐进增强的优化手段。不支持的浏览器会忽略该属性，元素正常渲染，不会产生功能问题。因此在长列表、长页面中放心使用，可以显著提升用户体验。

---

## 十、CSS 现代特性补充

### 10.1 Grid 深入

#### subgrid（子网格）

`subgrid` 是 CSS Grid Level 2 引入的关键特性，它允许子网格元素**继承父网格的轨道定义**，使嵌套网格的列/行与父网格对齐。在没有 `subgrid` 之前，嵌套网格的轨道是独立计算的，无法与父网格对齐。

```css
/* 父网格：定义 3 列 */
.card-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 16px;
}

/* 子网格：继承父网格的列定义 */
.card {
  display: grid;
  /* grid-template-columns: subgrid; 继承父网格的 3 列轨道 */
  grid-template-columns: subgrid;
  /* grid-template-rows: subgrid; 也可以继承行轨道 */
  grid-column: span 1; /* 每个卡片占一列 */
}

/* 卡片内部元素对齐到父网格的列线 */
.card-header {
  grid-column: 1 / -1; /* 横跨卡片所有列（即父网格的一列） */
}
```

**subgrid 的实际应用场景**：

```html
<!-- 产品卡片列表：每个卡片内部标题、描述、按钮对齐 -->
<div class="product-grid">
  <div class="product-card">
    <h2 class="product-title">短标题</h2>
    <p class="product-desc">一段较短的描述文字</p>
    <button class="product-btn">购买</button>
  </div>
  <div class="product-card">
    <h2 class="product-title">这是一个非常长的标题需要多行显示</h2>
    <p class="product-desc">一段较长的描述文字，占据更多空间，描述了产品的详细特性和功能</p>
    <button class="product-btn">购买</button>
  </div>
</div>
```

```css
.product-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 24px;
}

.product-card {
  display: grid;
  /* 关键：每行高度由同一行中最高内容决定，自动对齐 */
  grid-template-rows: subgrid;
  grid-row: span 3; /* 每张卡片占用 3 行（标题、描述、按钮） */
  gap: 8px;
  padding: 16px;
  border: 1px solid #e0e0e0;
  border-radius: 8px;
}

.product-title {
  grid-row: 1; /* 所有卡片的标题在同一行 */
}

.product-desc {
  grid-row: 2; /* 所有卡片的描述在同一行 */
}

.product-btn {
  grid-row: 3; /* 所有卡片的按钮在同一行 */
  align-self: end;
}
```

> **subgrid 的核心价值**：让同一行中不同卡片的内容（标题、描述、按钮）在垂直方向上自动对齐，无需设置固定高度或使用 JavaScript 计算。

#### 隐式网格（Implicit Grid）

当网格项目数量超过显式定义的轨道数时，浏览器会自动创建**隐式轨道**来容纳溢出的项目。`grid-auto-rows` 和 `grid-auto-columns` 用于控制隐式轨道的大小。

```css
/* 显式定义 2 行，每行 200px */
.grid-container {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  grid-template-rows: 200px 200px; /* 显式定义 2 行 */
  
  /* 隐式轨道：超过 2 行的项目自动获得的行高 */
  grid-auto-rows: 150px; /* 第 3 行开始每行 150px */
  
  /* 隐式列：当使用 grid-auto-flow: column 时控制列宽 */
  grid-auto-columns: 200px;
  
  gap: 16px;
}

/* 排列方向：默认 row（逐行填充），可改为 column（逐列填充） */
.grid-flow {
  grid-auto-flow: column; /* 项目按列方向排列，超出时创建隐式列 */
}
```

**隐式轨道的高级用法**：

```css
/* 使用 minmax() 创建灵活的最小/最大行高 */
.grid-auto {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  grid-auto-rows: minmax(100px, auto); /* 最小 100px，内容多时自动扩展 */
}

/* 使用多值模式：交替行高（如表格斑马纹效果） */
.grid-zebra {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  grid-auto-rows: 120px 80px; /* 第1行120px，第2行80px，第3行120px...交替 */
}

/* 结合 grid-auto-flow: dense 实现紧凑排列 */
.grid-dense {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  grid-auto-rows: 100px;
  grid-auto-flow: dense; /* 尽可能填充空白区域，可能改变项目顺序 */
}
```

> **注意**：`grid-auto-flow: dense` 会改变项目的视觉顺序（与 DOM 顺序不一致），可能影响可访问性（屏幕阅读器按 DOM 顺序朗读）。仅在视觉顺序不影响语义的场景使用。

#### masonry 布局（瀑布流）

CSS Grid Level 3 规范中定义了 `masonry` 布局（实验性，目前仅在 Firefox 中通过 flag 启用），它实现了类似 Pinterest 的瀑布流效果，无需 JavaScript 计算。

```css
/* 实验性 masonry 布局（当前仅 Firefox 支持） */
.masonry-container {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  grid-template-rows: masonry; /* 关键：使用 masonry 值 */
  gap: 16px;
}

/* 调整瀑布流排列方向 */
.masonry-packed {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  grid-template-rows: masonry;
  /* masonry-auto-flow: pack 会在每列中尽量紧凑排列 */
  masonry-auto-flow: pack;
}
```

**当前可用的瀑布流替代方案（CSS Columns）**：

```css
/* 使用 CSS Columns 实现瀑布流（兼容性良好） */
.masonry-fallback {
  /* 列数 - 根据容器宽度自动调整 */
  column-count: 4;
  column-gap: 16px;
}

.masonry-fallback .item {
  /* 防止元素在列之间断裂 */
  break-inside: avoid;
  margin-bottom: 16px;
}

/* 响应式列数 */
@media (max-width: 1024px) {
  .masonry-fallback { column-count: 3; }
}
@media (max-width: 768px) {
  .masonry-fallback { column-count: 2; }
}
@media (max-width: 480px) {
  .masonry-fallback { column-count: 1; }
}
```

> **注意事项**：CSS Columns 方案的瀑布流是**先从上到下排列再从左到右**（column-first），而原生 `masonry` 是**先从左到右再从上到下**（row-first）。两者视觉顺序不同，CSS Columns 更适合内容阅读顺序不敏感的场景（如图片画廊）。

### 10.2 CSS `@property`

`@property` 是 CSS Houdini 项目的一部分，允许开发者**显式定义 CSS 自定义属性的类型、初始值和继承行为**。它的核心价值在于：让浏览器知道自定义属性的类型，从而可以对自定义属性执行**类型安全的动画和过渡**。

```css
/* 语法：@property --属性名 { syntax: '<类型>'; inherits: true/false; initial-value: 值; } */

/* 示例 1：定义带类型的颜色变量 */
@property --gradient-angle {
  syntax: '<angle>';          /* 类型：角度值 */
  inherits: false;             /* 不继承 */
  initial-value: 0deg;         /* 初始值 */
}

@property --card-color {
  syntax: '<color>';
  inherits: false;
  initial-value: #4A90D9;
}

/* 示例 2：定义数值类型变量 */
@property --progress {
  syntax: '<percentage>';
  inherits: false;
  initial-value: 0%;
}
```

#### 完整代码示例：动画渐变边框

```css
/* 使用 @property 实现流畅的渐变旋转动画 */
@property --border-angle {
  syntax: '<angle>';
  inherits: false;
  initial-value: 0deg;
}

.animated-border {
  position: relative;
  padding: 2px;
  border-radius: 12px;
  background: conic-gradient(
    from var(--border-angle),
    #4A90D9,
    #764ba2,
    #4A90D9,
    #764ba2
  );
  animation: rotate-border 3s linear infinite;
}

.animated-border::before {
  content: '';
  position: absolute;
  inset: 2px;
  border-radius: 10px;
  background: #fff;
}

@keyframes rotate-border {
  to {
    --border-angle: 360deg;
  }
}

/* 如果没有 @property，浏览器不知道 --border-angle 是角度类型，
   动画会以离散方式（跳跃）执行，而不是平滑过渡。
   @property 声明了 <angle> 类型后，浏览器可以在 0deg 到 360deg 之间插值。 */
```

#### 完整代码示例：进度条动画

```css
@property --progress-value {
  syntax: '<percentage>';
  inherits: false;
  initial-value: 0%;
}

.progress-bar {
  width: 300px;
  height: 24px;
  border-radius: 12px;
  background: conic-gradient(
    #4A90D9 var(--progress-value),
    #e0e0e0 var(--progress-value)
  );
  /* 正确的写法应该使用 linear-gradient 或自定义宽度 */
  /* 这里展示 @property 使 --progress-value 支持动画 */
  transition: --progress-value 0.5s ease;
}

.progress-bar:hover {
  --progress-value: 80%;
}
```

#### 支持的类型（syntax）

| 类型 | 说明 | 示例值 |
|------|------|------|
| `<length>` | 长度值 | `10px`、`2rem`、`50%` |
| `<number>` | 数值 | `0`、`1.5`、`-3` |
| `<percentage>` | 百分比 | `0%`、`50%`、`100%` |
| `<length-percentage>` | 长度或百分比 | `10px` 或 `50%` |
| `<color>` | 颜色值 | `#4A90D9`、`rgb(74,144,217)` |
| `<angle>` | 角度值 | `0deg`、`180deg`、`1turn` |
| `<time>` | 时间值 | `0s`、`300ms` |
| `<integer>` | 整数 | `0`、`1`、`-5` |
| `<transform-function>` | 变换函数 | `rotate(45deg)`、`scale(1.5)` |
| `<custom-ident>` | 自定义标识符 | `auto`、`none` |

> **核心价值**：`@property` 解决了 CSS 自定义属性**无法动画化**的根本问题。在 `@property` 之前，`transition: --my-var 0.5s` 不会生效，因为浏览器不知道该变量是什么类型。声明类型后，浏览器可以在关键帧之间平滑插值。

> 📖 **参考链接**：
> - [MDN - CSS Houdini](https://developer.mozilla.org/zh-CN/docs/Web/API/Houdini_APIs)
> - [MDN - @property](https://developer.mozilla.org/zh-CN/docs/Web/CSS/@property)

### 10.3 View Transitions API

View Transitions API 提供了一种声明式的方式来创建**页面之间或 DOM 状态变化之间的平滑过渡动画**，无需编写复杂的 JavaScript 动画逻辑。

#### 基础用法：SPA 视图切换

```javascript
// 方式一：使用 startViewTransition 包裹 DOM 更新
function updateContent(newContent) {
  // 检查浏览器支持
  if (!document.startViewTransition) {
    // 回退：直接更新 DOM
    document.getElementById('content').innerHTML = newContent;
    return;
  }

  // startViewTransition 会：
  // 1. 截取当前页面快照
  // 2. 执行回调更新 DOM
  // 3. 截取新页面快照
  // 4. 自动执行从旧快照到新快照的过渡动画（默认 cross-fade）
  document.startViewTransition(() => {
    document.getElementById('content').innerHTML = newContent;
  });
}
```

#### 为不同元素指定不同过渡效果

```css
/* 自定义过渡动画 */
/* 旧视图的动画 */
::view-transition-old(root) {
  animation: fade-out 0.3s ease forwards;
}

/* 新视图的动画 */
::view-transition-new(root) {
  animation: fade-in 0.3s ease forwards;
}

@keyframes fade-out {
  from { opacity: 1; }
  to { opacity: 0; }
}

@keyframes fade-in {
  from { opacity: 0; }
  to { opacity: 1; }
}

/* 为特定元素指定过渡 */
/* 通过 view-transition-name 给元素命名 */
.hero-image {
  view-transition-name: hero;
}

.page-title {
  view-transition-name: title;
}

/* 单独控制命名元素的过渡 */
::view-transition-old(hero) {
  animation: slide-out 0.4s ease forwards;
}

::view-transition-new(hero) {
  animation: slide-in 0.4s ease forwards;
}

@keyframes slide-out {
  from { transform: translateX(0); opacity: 1; }
  to { transform: translateX(-30px); opacity: 0; }
}

@keyframes slide-in {
  from { transform: translateX(30px); opacity: 0; }
  to { transform: translateX(0); opacity: 1; }
}
```

#### MPA（多页面）视图过渡

```css
/* 在 CSS 中启用跨页面（MPA）视图过渡（无需 JavaScript） */
@view-transition {
  navigation: auto;
}

/* 或指定同源导航启用 */
@view-transition {
  navigation: auto;
  types: slide; /* 自定义过渡类型，可在页面中通过 ::view-transition 伪类引用 */
}
```

```html
<!-- 在 HTML 的 meta 标签中也可启用 -->
<meta name="view-transition" content="same-origin">
```

#### View Transitions 伪元素树

```
::view-transition（根伪元素，覆盖整个视口）
├── ::view-transition-group(root)（分组容器）
│   ├── ::view-transition-image-pair(root)（新旧图像对）
│   │   ├── ::view-transition-old(root)（旧视图快照）
│   │   └── ::view-transition-new(root)（新视图快照）
```

> **核心价值**：View Transitions API 将复杂的页面过渡动画简化为声明式 API。开发者只需关注"过渡前"和"过渡后"的 DOM 状态，浏览器自动处理快照、插值和动画执行。在 SPA 中配合框架（React/Vue）使用时，可以极大简化路由切换动画的实现。

### 10.4 Popover API / Anchor Positioning

#### Popover API

Popover API 提供了**原生的弹出层能力**，无需 JavaScript 库即可实现 tooltip、dropdown、modal 等弹出组件，自动处理层级管理、焦点管理、键盘导航和无障碍访问。

```html
<!-- 方式一：使用 popover 属性 -->
<button popovertarget="my-popover">打开弹出层</button>

<div id="my-popover" popover>
  <p>这是一个原生弹出层！</p>
  <button popovertarget="my-popover" popovertargetaction="hide">关闭</button>
</div>

<!-- 方式二：popover="auto"（默认）：点击外部自动关闭，多个 popover 互斥 -->
<div id="popover-auto" popover="auto">
  <p>点击外部区域或按 ESC 自动关闭</p>
</div>

<!-- 方式三：popover="manual"：手动控制，点击外部不关闭 -->
<div id="popover-manual" popover="manual">
  <p>需要通过 JavaScript 手动控制显示/隐藏</p>
</div>
```

```css
/* 自定义 popover 样式 */
#my-popover {
  padding: 16px;
  border: 1px solid #e0e0e0;
  border-radius: 8px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
  max-width: 300px;
}

/* popover 在顶层显示（top layer），无需 z-index 管理 */
#my-popover:popover-open {
  /* popover 打开时的样式 */
}

/* 使用 ::backdrop 定义遮罩 */
#my-popover::backdrop {
  background: rgba(0, 0, 0, 0.3);
  backdrop-filter: blur(2px);
}
```

```javascript
// JavaScript 控制
const popover = document.getElementById('my-popover');

// 显示
popover.showPopover();

// 隐藏
popover.hidePopover();

// 切换
popover.togglePopover();

// 事件监听
popover.addEventListener('toggle', (event) => {
  if (event.newState === 'open') {
    console.log('popover 已打开');
  } else {
    console.log('popover 已关闭');
  }
});
```

#### Anchor Positioning（锚点定位）

Anchor Positioning（CSS Anchor Positioning）允许一个元素**相对于另一个元素（锚点）进行定位**，无需 JavaScript 计算位置。这是实现 tooltip、dropdown 菜单等组件的原生方案。

```css
/* 第 1 步：定义锚点（使用 anchor-name） */
.anchor-btn {
  anchor-name: --my-button;
}

/* 第 2 步：使用 anchor() 函数定位弹出层 */
.tooltip {
  position: absolute;
  /* 定位到锚点的底部中心 */
  bottom: anchor(--my-button top);
  left: anchor(--my-button center);
  
  /* 使用 anchor-size() 设置宽度与锚点一致 */
  /* width: anchor-size(--my-button width); */
  
  /* 回退策略：当锚点不可见时 */
  /* position-fallback: --flip-vertical; */
}

/* 第 3 步：使用 anchor-center 精确对齐 */
.tooltip {
  position: absolute;
  position-anchor: --my-button;
  /* 将 tooltip 的顶部中心对齐到锚点的底部中心 */
  top: anchor(bottom);
  justify-self: anchor-center;
  
  /* 或使用 inset-area 简写 */
  /* inset-area: bottom; */
}
```

```html
<!-- 完整示例：原生 tooltip -->
<button class="anchor-btn" anchor-name="--btn-demo">
  悬停查看提示
</button>
<div class="tooltip" popover="manual">
  这是锚点定位的提示信息
</div>
```

```css
.anchor-btn {
  anchor-name: --btn-demo;
  padding: 8px 16px;
  background: #4A90D9;
  color: #fff;
  border: none;
  border-radius: 4px;
  cursor: pointer;
}

.tooltip {
  position: absolute;
  position-anchor: --btn-demo;
  top: anchor(bottom);
  justify-self: anchor-center;
  padding: 6px 12px;
  background: #333;
  color: #fff;
  border-radius: 4px;
  font-size: 14px;
  white-space: nowrap;
  margin-top: 4px;
}

/* 小三角箭头（使用 CSS 实现） */
.tooltip::before {
  content: '';
  position: absolute;
  top: -6px;
  left: 50%;
  transform: translateX(-50%);
  border-left: 6px solid transparent;
  border-right: 6px solid transparent;
  border-bottom: 6px solid #333;
}
```

**核心 `anchor()` 函数参数**：

```
anchor(<anchor-name> <position>)
  anchor-name: 锚点名称（如 --my-button）
  position: 可以是 top/bottom/left/right/center，或百分比值（如 50%）
```

**Popover API 与 Anchor Positioning 结合**：

```html
<button id="menu-btn" popovertarget="dropdown-menu">菜单</button>

<div id="dropdown-menu" popover="auto">
  <a href="#">选项 1</a>
  <a href="#">选项 2</a>
  <a href="#">选项 3</a>
</div>
```

```css
#menu-btn {
  anchor-name: --menu-anchor;
}

#dropdown-menu {
  position: absolute;
  position-anchor: --menu-anchor;
  top: anchor(bottom);
  left: anchor(left);
  /* 宽度与按钮对齐 */
  min-width: anchor-size(width);
  padding: 8px 0;
  border: 1px solid #e0e0e0;
  border-radius: 8px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
  background: #fff;
}

#dropdown-menu a {
  display: block;
  padding: 8px 16px;
  color: #333;
  text-decoration: none;
}

#dropdown-menu a:hover {
  background: #f5f5f5;
}
```

> **核心价值**：Popover API 解决了弹出层的层级管理、焦点管理和无障碍访问等痛点；Anchor Positioning 解决了浮动组件相对于目标元素的精确定位问题。两者结合使用，可以完全替代传统的第三方 tooltip/dropdown 库，实现零依赖的原生弹出组件。

### 10.5 CSS Scroll-Driven Animations（滚动驱动动画）

滚动驱动动画允许将动画进度与滚动位置绑定，无需 JavaScript 即可实现视差滚动、滚动进度条、元素进入/退出动画等效果。Chrome 115+、Safari 2025+ 已全面支持。

**两种时间线**：

| 类型 | 语法 | 说明 |
|------|------|------|
| `scroll()` | `animation-timeline: scroll()` | 基于**最近可滚动祖先**的滚动进度 |
| `view()` | `animation-timeline: view()` | 基于**元素自身进入/离开视口**的进度 |

```css
/* === scroll() 时间线：基于滚动容器的滚动进度 === */

/* 滚动进度条（随着页面滚动从 0% 到 100% 宽度） */
.progress-bar {
  position: fixed;
  top: 0;
  left: 0;
  height: 4px;
  background: #4f46e5;
  transform-origin: left;
  animation: grow-progress 1s linear;
  animation-timeline: scroll(); /* 绑定到最近的可滚动祖先 */
}

@keyframes grow-progress {
  from { transform: scaleX(0); }
  to { transform: scaleX(1); }
}

/* 指定滚动容器（root = 视口） */
.hero-image {
  animation: scale-down 1s linear;
  animation-timeline: scroll(root); /* 基于视口滚动 */
}

/* 指定滚动轴（block = 垂直，inline = 水平） */
.horizontal-gallery {
  animation: slide 1s linear;
  animation-timeline: scroll(inline); /* 基于水平滚动 */
}

@keyframes scale-down {
  from { transform: scale(1.5); opacity: 0; }
  to { transform: scale(1); opacity: 1; }
}

/* === view() 时间线：基于元素进入/离开视口 === */

/* 卡片淡入效果：从进入视口到离开视口的过程中执行动画 */
.card {
  animation: fade-in 1s linear;
  animation-timeline: view();
}

@keyframes fade-in {
  from { opacity: 0; transform: translateY(40px); }
  to { opacity: 1; transform: translateY(0); }
}

/* 控制动画区间：crossing 百分比 */
.image-reveal {
  animation: reveal 1s linear;
  animation-timeline: view();
  animation-range: entry 25% cover 50%; /* 进入 25% 到覆盖 50% 之间 */
}

@keyframes reveal {
  from { clip-path: inset(50% 0 50% 0); }
  to { clip-path: inset(0 0 0 0); }
}
```

> **核心价值**：滚动驱动动画将以前需要大量 JavaScript（IntersectionObserver + scroll 事件监听）才能实现的滚动效果简化为纯 CSS 声明，性能更好（GPU 加速），代码更简洁。

### 10.6 CSS `@starting-style`

`@starting-style`（Chrome 117+）解决了 `display: none` 到可见元素的过渡问题。当元素首次渲染或从 `display: none` 切换为可见时，浏览器需要知道元素的"初始状态"才能执行过渡动画。

```css
/* 问题场景：display: none 的元素无法过渡 */
.modal {
  display: none;
  opacity: 0;
  transition: opacity 0.3s;
}

.modal.open {
  display: block;
  opacity: 1;
}
/* ❌ 这样写过渡不会生效！因为 display 变化时浏览器跳过过渡 */

/* 解决方案：使用 @starting-style 定义初始状态 */
.modal {
  opacity: 0;
  transition: opacity 0.3s, transform 0.3s;
  transform: translateY(20px);

  @starting-style {
    /* 元素首次渲染时的初始状态 */
    opacity: 0;
    transform: translateY(20px);
  }
}

.modal.open {
  opacity: 1;
  transform: translateY(0);
}
/* ✅ 现在过渡可以正常执行 */

/* 更实用的例子：popover 打开动画 */
[popover] {
  opacity: 0;
  transform: scale(0.95);
  transition: opacity 0.2s, transform 0.2s;
  transition-behavior: allow-discrete; /* 允许 display 属性的过渡 */

  @starting-style {
    opacity: 0;
    transform: scale(0.95);
  }
}

[popover]:popover-open {
  opacity: 1;
  transform: scale(1);
}
```

> **核心价值**：`@starting-style` 与 `transition-behavior: allow-discrete` 配合，彻底解决了 CSS 中 `display: none` 元素的过渡动画问题，配合 Popover API 和 `<dialog>` 可以实现原生的弹出/关闭动画。

### 10.7 CSS `light-dark()` 函数

`light-dark()` 是 CSS Color Level 5 提出的颜色函数（2024 年浏览器全面支持），可根据当前颜色方案自动选择浅色或深色值，大幅简化暗色模式的实现。

```css
/* 基本语法：light-dark(浅色值, 深色值) */
:root {
  color-scheme: light dark; /* 必须声明支持两种模式 */
}

body {
  /* 自动根据 color-scheme 选择颜色 */
  background-color: light-dark(#ffffff, #1a1a2e);
  color: light-dark(#333333, #e0e0e0);
}

.card {
  background: light-dark(#f8f9fa, #2d2d44);
  border: 1px solid light-dark(#e0e0e0, #444466);
  box-shadow: light-dark(
    0 2px 8px rgba(0,0,0,0.1),
    0 2px 8px rgba(0,0,0,0.4)
  );
}

/* 与 CSS 变量结合使用 */
:root {
  --bg-primary: light-dark(#ffffff, #1a1a2e);
  --bg-secondary: light-dark(#f5f5f5, #2d2d44);
  --text-primary: light-dark(#1a1a1a, #f0f0f0);
  --text-secondary: light-dark(#666666, #aaaaaa);
  --border-color: light-dark(#e0e0e0, #444466);
  --accent: light-dark(#4f46e5, #818cf8);
}

/* 手动切换（用户偏好覆盖系统设置） */
[data-theme="light"] {
  color-scheme: light;
}

[data-theme="dark"] {
  color-scheme: dark;
}
```

```html
<!-- 通过 JavaScript 切换主题 -->
<button onclick="document.documentElement.dataset.theme =
  document.documentElement.dataset.theme === 'dark' ? 'light' : 'dark'">
  切换主题
</button>
```

> **核心价值**：相比传统的暗色模式实现（`prefers-color-scheme` 媒体查询 + 两套 CSS 变量），`light-dark()` 将颜色选择逻辑内联到每个属性声明中，代码量减少约 50%，可读性大幅提升。

### 10.8 CSS `@scope`

`@scope`（Chrome 118+）提供了原生 CSS 样式作用域机制，允许将样式规则限制在特定的 DOM 子树内，避免样式冲突和全局污染。

```css
/* 基本语法：@scope (选择器) { ... } */
@scope (.card) {
  /* 以下所有样式仅作用于 .card 内部 */
  h2 {
    font-size: 1.25rem;
    color: #333;
  }

  p {
    line-height: 1.6;
  }

  .button {
    padding: 8px 16px;
    border-radius: 6px;
  }
}

/* 指定作用域上限和下限 */
@scope (.article-content) to (.comment-section) {
  /* 样式作用于 .article-content 内部，但不超过 .comment-section */
  p {
    margin-bottom: 1em;
  }

  img {
    max-width: 100%;
    border-radius: 8px;
  }
}

/* 与 CSS 变量结合——实现组件级样式隔离 */
@scope (.theme-blue) {
  :scope {
    --accent: #2563eb;
    --bg: #eff6ff;
  }

  .button {
    background: var(--accent);
    color: white;
  }
}

@scope (.theme-green) {
  :scope {
    --accent: #16a34a;
    --bg: #f0fdf4;
  }

  .button {
    background: var(--accent);
    color: white;
  }
}
```

**与 CSS Modules 的对比**：

| 维度 | `@scope` | CSS Modules |
|------|----------|-------------|
| 实现方式 | 浏览器原生支持 | 构建工具编译（生成唯一类名） |
| 样式隔离 | 基于 DOM 选择器 | 基于唯一类名哈希 |
| 全局样式 | 仍可访问外部样式 | 默认隔离，需 `:global()` 显式声明 |
| 动态性 | 运行时生效 | 编译时确定 |
| 浏览器支持 | Chrome 118+（2023 年） | 所有浏览器（编译后为普通 CSS） |

> **核心价值**：`@scope` 为 CSS 带来了原生的样式作用域机制，配合 `:scope` 伪类可以精确控制组件内部样式，是 CSS 组件化的重要里程碑。与 CSS Modules 互补：`@scope` 适合小规模组件和渐进增强，CSS Modules 适合需要严格隔离的大型项目。

---

## 补充：CSS 现代布局与工程化实践

> 本节补齐 CSS 在工程实践中高频出现、但前文未覆盖的五块内容：逻辑属性（国际化）、流体排版（无媒体查询的响应式）、无障碍动效、滚动条定制、样式方案选型。

### 1. CSS 逻辑属性与 RTL 国际化

#### 1.1 核心概念

**CSS 逻辑属性**（Logical Properties）是用"**书写方向**"而非"物理方向"来描述位置的属性。传统属性用 `left` / `right` / `top` / `bottom` 描述物理方位，逻辑属性改用两条轴来描述：

- **inline 轴**：文本流的方向（水平书写模式下即水平方向，与文字行方向一致）
- **block 轴**：文本块堆叠的方向（水平书写模式下即垂直方向）

| 物理属性 | 逻辑属性 | 说明 |
|---------|---------|------|
| `margin-left` / `margin-right` | `margin-inline-start` / `margin-inline-end` | 行内轴的起止两端 |
| `margin-top` / `margin-bottom` | `margin-block-start` / `margin-block-end` | 块轴的起止两端 |
| `padding-*` | `padding-inline-*` / `padding-block-*` | 同上规则 |
| `border-left` | `border-inline-start` | 边框也可逻辑化 |
| `width` / `height` | `inline-size` / `block-size` | 尺寸的逻辑写法 |
| `top` / `left` / `right` / `bottom` | `inset-block-start` / `inset-inline-start` / `inset-inline-end` / `inset-block-end` | `inset` 是四者的物理简写，`inset-inline` / `inset-block` 是逻辑简写 |
| `text-align: left/right` | `text-align: start/end` | 文本对齐同样支持逻辑值 |
| `border-top-left-radius` | `border-start-start-radius` | 圆角也提供逻辑写法 |

#### 1.2 底层原理

逻辑属性**不是新属性**，而是**映射到物理属性**的语法糖：浏览器在样式解析阶段根据当前元素的 `writing-mode` 与 `direction`，把 `margin-inline-start` 解析成 `margin-left` 或 `margin-right`。

因此有两个关键结论：

1. **逻辑属性与对应的物理属性是同一个属性**。同一声明块里先写物理、后写逻辑（或反之），后写的会覆盖前者，**不会叠加**。
2. **方向切换是自动的**。当 `direction: rtl`（阿拉伯语、希伯来语）或 `writing-mode: vertical-rl`（竖排）时，inline / block 轴的含义随书写模式改变，布局自动镜像，无需维护两套 CSS。

```css
/* ===== 反例：物理属性写法，切换 RTL 后布局错乱 ===== */
.card {
  margin-left: 16px;          /* 阿拉伯语环境下仍在左侧，应该镜像到右侧 */
  padding-right: 12px;
  border-left: 4px solid #4f46e5;  /* 装饰性竖线跑到了错误的一侧 */
  text-align: left;
}

/* ===== 正例：逻辑属性写法，自动适配 LTR / RTL ===== */
.card {
  margin-inline-start: 16px;             /* LTR 下为左，RTL 下自动为右 */
  padding-inline-end: 12px;
  border-inline-start: 4px solid #4f46e5;
  text-align: start;                     /* 自动跟随书写方向 */
}

/* 简写：margin-inline: <start> <end> */
.list-item {
  margin-inline: 16px 24px;   /* start = 16px，end = 24px */
  padding-block: 8px;         /* block-start 与 block-end 同为 8px */
}

/* 竖排书写模式：inline / block 两轴自动互换，同一份 CSS 直接可用 */
.vertical-text {
  writing-mode: vertical-rl;
  inline-size: 200px;         /* 竖排下这是"高度"方向的尺寸 */
  block-size: 60px;
}
```

```html
<!-- 通过 dir 属性切换书写方向，逻辑属性无需任何额外 CSS 即可镜像 -->
<html dir="rtl" lang="ar">
```

> **核心价值**：逻辑属性让"一套 CSS 支持多语言书写方向"成为可能。对于出海项目，用逻辑属性写布局的成本与物理属性完全相同，却省掉了整套 RTL 覆盖样式（传统方案是引入 `rtl.css` 或使用 `[dir="rtl"] .card { margin-right: 16px; margin-left: 0 }` 全量镜像）。

**面试常见问法**：

- **逻辑属性和物理属性的关系是什么？** 逻辑属性是语法糖，运行时映射到物理属性，两者是同一个属性，因此会相互覆盖而不是叠加。
- **`margin-inline: 10px 20px` 展开后是什么？** `margin-inline-start: 10px; margin-inline-end: 20px`。
- **哪些属性无法逻辑化？** `transform: translateX()`、`background-position: left`、`float: left` 这类仍带物理方向语义的值，需要手动处理；`float` 已新增 `inline-start` / `inline-end` 逻辑值。

**易错点**：

| 常见错误 | 现象 | 原因 | 解决方案 |
|---------|------|------|---------|
| 物理属性与逻辑属性混用 | 某个方向的样式"莫名其妙"失效 | 两者映射到同一物理属性，后声明覆盖前者 | 同一组件内统一使用一套写法 |
| 用 `translateX` 做 RTL 适配 | 滑动方向在 RTL 下反向 | `translateX` 是物理方向，不随 `direction` 变化 | 改用 `translate` 或根据 `direction` 取反 |
| 以为逻辑属性能解决所有国际化问题 | 数字、图标、时间格式仍不正确 | 逻辑属性只管布局方向，不管内容本地化 | 布局用逻辑属性，内容用 `Intl` API 处理 |
| 忽略浏览器兼容基线 | 旧浏览器整块样式失效 | 逻辑属性需要 Chrome 87+ / Firefox 66+ / Safari 14.1+ | 作为渐进增强使用，或由构建工具自动降级 |

> 📖 **参考链接**：
> - [MDN - CSS 逻辑属性与值](https://developer.mozilla.org/zh-CN/docs/Web/CSS/CSS_logical_properties_and_values)
> - [MDN - writing-mode](https://developer.mozilla.org/zh-CN/docs/Web/CSS/writing-mode)

---

### 2. 流体排版：`clamp()` / `min()` / `max()`

#### 2.1 核心概念

CSS 比较函数（Comparison Functions）让尺寸可以随视口**连续变化**，从而用一条声明替代一组媒体查询：

| 函数 | 语义 | 等价表达式 |
|------|------|-----------|
| `min(a, b, ...)` | 取**最小**值 | — |
| `max(a, b, ...)` | 取**最大**值 | — |
| `clamp(MIN, VAL, MAX)` | 把 `VAL` 限制在 `[MIN, MAX]` 区间内 | `max(MIN, min(VAL, MAX))` |

#### 2.2 底层原理

`clamp()` 的规范定义就是 `max(MIN, min(VAL, MAX))`：先取 `VAL` 与 `MAX` 的较小值（封顶），再与 `MIN` 取较大值（保底）。这带来一个重要推论：**当 `MIN > MAX` 时，结果是 `MIN`**（因为 `max` 在最后一步），所以书写时务必保证 `MIN <= MAX`。

另一个常被忽略的点：**在 `min()` / `max()` / `clamp()` 内部可以直接写数学表达式，不需要再套一层 `calc()`**。

```css
/* ===== 1. 响应式字号：小屏 1rem，大屏最多 1.75rem，中间连续过渡 ===== */
.title {
  /* 推荐：rem + vw 混合，兼顾无障碍缩放与视口自适应 */
  font-size: clamp(1rem, 0.5rem + 1.5vw, 1.75rem);
}

/* 不推荐：纯 vw 字号在用户调整浏览器默认字号时不会放大，损害可访问性 */
.title-bad {
  font-size: clamp(16px, 3vw, 28px);
}

/* ===== 2. 内部可直接写表达式，无需 calc() ===== */
.container {
  /* 等价于 clamp(16px, calc(4vw + 8px), 48px) */
  padding-inline: clamp(16px, 4vw + 8px, 48px);
  /* 等价于 max(320px, min(90vw, 1200px)) */
  inline-size: min(90vw, 1200px);
}

/* ===== 3. min() / max() 的典型用法 ===== */
.sidebar {
  inline-size: min(320px, 30%);      /* 侧栏不超过 320px，也不超过父容器的 30% */
}

.hero {
  min-block-size: max(400px, 50vh);  /* 首屏至少 400px 高 */
}

/* ===== 4. 与 Grid 结合：无媒体查询的响应式栅格 ===== */
.auto-grid {
  display: grid;
  /* 列宽在 240px 到 1fr 之间自适应，自动决定每行放几列 */
  grid-template-columns: repeat(auto-fit, minmax(min(240px, 100%), 1fr));
  gap: clamp(12px, 2vw, 24px);
}
```

> **核心价值**：`clamp()` 用一行声明替代了传统的 `@media` 断点阶梯（例如 `font-size: 16px` → `@media (min-width: 768px) { font-size: 20px }` → `@media (min-width: 1200px) { font-size: 28px }`）。它不仅代码更短，而且尺寸在断点之间是**连续变化**的，不会出现"跨过断点后字号突跳"的观感问题。

**面试常见问法**：

- **`clamp()` 的三个参数分别是什么？** 最小值、首选值（preferred）、最大值；等价于 `max(MIN, min(VAL, MAX))`。
- **`clamp()` 和媒体查询怎么选？** 尺寸需要随视口连续变化时用 `clamp()`；需要在特定断点改变**布局结构**（如三栏变单栏）时仍要用媒体查询。两者互补。
- **为什么响应式字号推荐 `rem + vw` 混合？** 纯 `vw` 字号不随用户调整浏览器默认字号而变化，违反 WCAG 的可缩放要求；混入 `rem` 后，用户放大默认字号时最小值会同步放大。
- **`clamp(2rem, 1rem, 3rem)` 的结果是多少？** `2rem`。因为 `max(MIN, ...)` 在最后一步生效，`MIN > MAX` 时结果恒为 `MIN`。

**易错点**：

| 常见错误 | 现象 | 原因 | 解决方案 |
|---------|------|------|---------|
| `MIN > MAX` | 尺寸恒定不变 | `clamp()` 等价于 `max(MIN, min(VAL, MAX))`，`MIN` 最终胜出 | 检查参数顺序，保证 `MIN <= MAX` |
| 纯 `vw` 做字号 | 用户放大浏览器字号无效 | `vw` 与视口绑定，不响应默认字号变化 | 首选值用 `rem + vw` 混合表达式 |
| 在 `min()` 内又套 `calc()` | 代码冗余但能运行 | 未了解比较函数内部已支持数学表达式 | 直接写 `min(90vw, 1200px)` 或 `clamp(1rem, 4vw + 8px, 3rem)` |
| 用 `clamp()` 替代所有断点 | 移动端布局结构未变，只是元素变小 | `clamp()` 只控制尺寸，不改变布局结构 | 布局结构变化仍用媒体查询或 Container Queries |

> 📖 **参考链接**：
> - [MDN - clamp()](https://developer.mozilla.org/zh-CN/docs/Web/CSS/clamp)
> - [MDN - min()](https://developer.mozilla.org/zh-CN/docs/Web/CSS/min)

---

### 3. `prefers-reduced-motion` 无障碍动效适配

#### 3.1 核心概念

`prefers-reduced-motion` 是一个 CSS 媒体特性，用于读取用户在操作系统层面的"减弱动态效果"偏好（macOS：辅助功能 → 显示 → 减少动态效果；Windows：设置 → 辅助功能 → 视觉效果 → 动画效果；iOS / Android 同样有对应开关）。

| 取值 | 含义 |
|------|------|
| `no-preference` | 用户未表达偏好（默认值，可省略不写） |
| `reduce` | 用户希望减少非必要的动效 |

#### 3.2 底层原理与为什么需要它

大幅度的位移动画、视差滚动、缩放、旋转会刺激**前庭系统**，可能引发前庭功能障碍用户的眩晕、恶心、头痛。WCAG 2.1 的 **2.3.3 Animation from Interactions**（AAA 级）明确要求：由交互触发的动效应当可以被禁用，除非该动效对功能至关重要。

因此正确的做法不是"禁用所有动效"，而是**按风险分级削弱**：

- **高风险**（应当移除）：视差滚动、大幅位移、缩放、旋转、自动播放的循环动画
- **低风险**（可以保留）：透明度淡入淡出、颜色过渡、边框颜色变化

```css
/* ===== 方案 1：全局"削弱"兜底（安全网，放在样式表最后）===== */
@media (prefers-reduced-motion: reduce) {
  *,
  *::before,
  *::after {
    /* 保留极短时长而非 0，确保 transitionend / animationend 事件仍会触发 */
    animation-duration: 0.01ms !important;
    /* 阻止 infinite 循环动画，否则动画仍会高频重放 */
    animation-iteration-count: 1 !important;
    transition-duration: 0.01ms !important;
    /* 关闭平滑滚动，滚动跳跃对前庭敏感用户更友好 */
    scroll-behavior: auto !important;
  }
}

/* ===== 方案 2（推荐）：定向削弱，保留低风险动效 ===== */
.hero-banner {
  transition: transform 0.6s ease, opacity 0.6s ease;
  transform: translateY(0);
}

@media (prefers-reduced-motion: reduce) {
  .hero-banner {
    /* 去掉位移与缩放，只保留淡入——既照顾无障碍又保留状态反馈 */
    transform: none !important;
    transition: opacity 0.3s ease;
  }
}

/* ===== 方案 3：反向写法，仅在用户未表达偏好时才启用动效 ===== */
@media (prefers-reduced-motion: no-preference) {
  .card {
    transition: transform 0.3s ease;
  }
  .card:hover {
    transform: translateY(-4px);
  }
}
```

```javascript
// JavaScript 侧读取与监听：适用于 Canvas / WebGL / 第三方动画库
const motionQuery = window.matchMedia('(prefers-reduced-motion: reduce)');

// 1. 初始化：根据偏好决定动画参数
function setupAnimation(reduced) {
  const duration = reduced ? 0 : 600;
  const easing = reduced ? 'linear' : 'cubic-bezier(0.4, 0, 0.2, 1)';
  return { duration, easing };
}

let config = setupAnimation(motionQuery.matches);

// 2. 监听系统设置变化，用户中途切换开关时实时响应
motionQuery.addEventListener('change', (event) => {
  config = setupAnimation(event.matches);
});
```

> **核心价值**：`prefers-reduced-motion` 是"渐进增强"思路在无障碍领域的体现——默认提供完整动效体验，仅在用户明确表达偏好时降级。它与 `prefers-color-scheme`、`prefers-contrast` 同属"用户偏好媒体特性"，是国际化产品的合规基线。

**面试常见问法**：

- **`prefers-reduced-motion` 解决什么问题？** 为前庭功能障碍等对动效敏感的用户提供减弱动效的能力，对应 WCAG 2.3.3。
- **为什么用 `0.01ms` 而不是 `0`？** `transition-duration: 0s` 时浏览器可能不派发 `transitionend` 事件，设为 `0.01ms` 可保留事件语义，同时视觉上等同于瞬时完成。
- **为什么要重置 `animation-iteration-count`？** 否则 `animation: spin 1s infinite` 这类无限动画在时长被压到 `0.01ms` 后仍会以极高频率重放，反而更刺眼，同时浪费 CPU。
- **在 React 中怎么用？** 用 `window.matchMedia('(prefers-reduced-motion: reduce)')` 封装成 `useReducedMotion` Hook，第三方库 framer-motion 已内置该支持。

**易错点**：

| 常见错误 | 现象 | 原因 | 解决方案 |
|---------|------|------|---------|
| 全局把动效时长设为 0 | 依赖 `transitionend` 的逻辑失效 | `0s` 不触发过渡事件 | 使用 `0.01ms` 而非 `0s` |
| 只压时长未压循环次数 | 无限动画高频重放 | `animation-iteration-count: infinite` 未被重置 | 同时设置 `animation-iteration-count: 1` |
| 完全禁用所有动效 | 用户失去状态反馈（如加载中、成功提示） | 把"减弱"理解为"禁用" | 分级处理：移除位移/缩放/视差，保留透明度与颜色过渡 |
| 忘记 `scroll-behavior` | 锚点跳转仍是平滑滚动，长距离滚动引起不适 | 平滑滚动也属于动效 | 在 `reduce` 分支中重置为 `auto` |

> 📖 **参考链接**：
> - [MDN - prefers-reduced-motion](https://developer.mozilla.org/zh-CN/docs/Web/CSS/@media/prefers-reduced-motion)
> - [WCAG 2.3.3 Animation from Interactions](https://www.w3.org/WAI/WCAG21/Understanding/animation-from-interactions.html)

---

### 4. 滚动条定制与兼容写法

#### 4.1 两套 API 的由来

滚动条样式长期存在**两套互不兼容的 API**，这是历史遗留问题：

| 方案 | 标准属性 / 伪元素 | 支持情况 | 能力 |
|------|-----------------|---------|------|
| 标准方案 | `scrollbar-width`、`scrollbar-color`、`scrollbar-gutter` | Firefox 64+、Chrome 121+、Safari 18.2+（`scrollbar-width` / `scrollbar-color`） | 只能设置宽度档位与两个颜色，**能力有限但标准统一** |
| WebKit 方案 | `::-webkit-scrollbar` 及系列伪元素 | Chrome、Safari、Edge（Firefox 不支持） | 可精细控制圆角、悬停色、轨道、按钮，**能力强但非标准** |

```css
/* ===== 方案 1：标准属性 ===== */
.scroll-area {
  scrollbar-width: thin;              /* auto（默认） | thin | none */
  scrollbar-color: #94a3b8 #f1f5f9;   /* 滑块颜色 轨道颜色 */
  /* 始终预留滚动条槽位，避免内容出现滚动条时发生布局跳动（CLS） */
  scrollbar-gutter: stable;
}

/* ===== 方案 2：WebKit 伪元素 ===== */
.scroll-area::-webkit-scrollbar {
  width: 8px;          /* 纵向滚动条宽度 */
  height: 8px;         /* 横向滚动条高度 */
}

.scroll-area::-webkit-scrollbar-track {
  background: #f1f5f9;
  border-radius: 4px;
}

.scroll-area::-webkit-scrollbar-thumb {
  background: #94a3b8;
  border-radius: 4px;
}

.scroll-area::-webkit-scrollbar-thumb:hover {
  background: #64748b;   /* 悬停反馈：标准属性无法实现 */
}

.scroll-area::-webkit-scrollbar-corner {
  background: transparent;  /* 横向与纵向滚动条交汇的角落 */
}
```

#### 4.2 兼容写法：不要两套同时生效

**关键陷阱**：在 Chrome 中一旦声明了 `scrollbar-width` 或 `scrollbar-color`，`::-webkit-scrollbar` 系列的样式就会被忽略。因此两套写法**不能无脑堆叠**，需要显式分流：

```css
/* ===== 推荐做法：用 @supports selector() 分流 ===== */
/* Firefox 不支持 ::-webkit-scrollbar，因此该分支只在 Firefox 生效 */
@supports not selector(::-webkit-scrollbar) {
  .scroll-area {
    scrollbar-width: thin;
    scrollbar-color: #94a3b8 #f1f5f9;
  }
}

/* Chrome / Safari / Edge 走 WebKit 伪元素，获得圆角与悬停态 */
.scroll-area::-webkit-scrollbar {
  width: 8px;
  height: 8px;
}
.scroll-area::-webkit-scrollbar-thumb {
  background: #94a3b8;
  border-radius: 4px;
}
```

**无障碍提醒**：`scrollbar-width: none` 或 `::-webkit-scrollbar { display: none }` 会完全隐藏滚动条。滚动条是"内容可滚动"的重要视觉提示，隐藏后用户可能根本不知道页面还有内容，因此：

- 只在自定义滚动容器（如带箭头的横向卡片列表、代码块）上隐藏，**不要**在页面主滚动区域隐藏；
- 隐藏后应通过渐隐遮罩、箭头按钮或 `scroll-snap` 提供替代的滚动提示；
- 必须保证键盘（`Tab` 聚焦后方向键滚动）与触摸手势仍然可用。

**面试常见问法**：

- **怎么自定义滚动条？** 两套 API：标准属性 `scrollbar-width` / `scrollbar-color`（能力有限、跨浏览器），以及 WebKit 伪元素 `::-webkit-scrollbar` 系列（能力强、Firefox 不支持）。
- **为什么两套写法不能同时写？** Chrome 中标准属性一旦声明就会覆盖 WebKit 伪元素样式，需要用 `@supports selector(::-webkit-scrollbar)` 分流。
- **`scrollbar-gutter: stable` 有什么用？** 始终预留滚动条占位，避免内容从"无滚动条"变为"有滚动条"时宽度突变导致的布局跳动（CLS 指标）。
- **隐藏滚动条有什么风险？** 失去"可滚动"的视觉提示，降低可发现性；必须提供替代提示并保证键盘可操作。

**易错点**：

| 常见错误 | 现象 | 原因 | 解决方案 |
|---------|------|------|---------|
| 同时写标准属性与 WebKit 伪元素 | 精细样式（圆角、悬停色）不生效 | Chrome 中标准属性优先，WebKit 伪元素被忽略 | 用 `@supports not selector(::-webkit-scrollbar)` 分流 |
| 用 `overflow: overlay` 隐藏占位 | 样式不生效 | `overflow: overlay` 已被废弃 | 改用 `scrollbar-gutter: stable` |
| 在页面主滚动区隐藏滚动条 | 用户不知道页面可滚动 | 移除了唯一的滚动提示 | 仅在自定义滚动容器中隐藏，并提供替代提示 |
| 在 `<body>` 上设置 `::-webkit-scrollbar` | 某些场景不生效 | 滚动容器可能是 `<html>` 或外层元素 | 明确滚动容器后再设置，必要时同时作用于 `html` 与 `body` |

> 📖 **参考链接**：
> - [MDN - scrollbar-width](https://developer.mozilla.org/zh-CN/docs/Web/CSS/scrollbar-width)
> - [MDN - ::-webkit-scrollbar](https://developer.mozilla.org/en-US/docs/Web/CSS/::-webkit-scrollbar)

---

### 5. CSS 方案选型：CSS Modules / CSS-in-JS / 原子化 / 零运行时

#### 5.1 四类方案的定位

| 方案 | 代表工具 | 样式何时产生 | 运行时开销 | 动态样式能力 | 类型安全 | SSR / RSC 兼容 |
|------|---------|------------|:---:|:---:|:---:|:---:|
| CSS Modules | 构建工具内置（Vite / webpack） | 构建时生成唯一类名 | 无 | 弱（需借助 CSS 变量或 `data-*` 属性） | 一般（需额外 `.d.ts` 声明） | 天然兼容 |
| CSS-in-JS（运行时） | styled-components、emotion | 运行时序列化并注入 `<style>` | **有**（每次渲染计算样式、插入样式表） | 强（可直接读取 props 与 theme） | 强 | RSC 不兼容；SSR 需提取关键 CSS |
| 原子化（utility-first） | Tailwind CSS、UnoCSS | 构建时扫描源码按需生成 | 无 | 中（依赖条件类名拼接） | 弱（类名字符串） | 天然兼容 |
| 零运行时（编译期） | vanilla-extract、Linaria、StyleX | 构建时生成静态 `.css` 文件 | 无 | 中（构建期生成多个类名 + CSS 变量） | 强（TS 类型推导） | 天然兼容 |

#### 5.2 各类方案的核心机制

**CSS Modules**：构建工具把 `.module.css` 中的类名编译成带哈希的唯一类名（如 `.title` → `._title_1a2b3`），从而实现组件级作用域隔离；`:global()` 用于逃出作用域；`composes` 用于样式复用。

```css
/* card.module.css */
.card {
  padding: 16px;
  border-radius: 8px;
}
.title {
  composes: card;          /* 复用 .card 的样式 */
  font-weight: 600;
}
/* :global 显式声明全局样式 */
:global(.no-scroll) {
  overflow: hidden;
}
```

```jsx
import styles from './card.module.css';

// 动态样式：类名切换（推荐）或 CSS 变量（更灵活）
export function Card({ active, accent }) {
  return (
    <div
      className={`${styles.card} ${active ? styles.active : ''}`}
      style={{ '--accent': accent }}
    >
      <h3 className={styles.title}>标题</h3>
    </div>
  );
}
```

**CSS-in-JS（运行时）**：样式写在 JS 中，通过 `styled` 的标签模板语法或 `css` 函数返回组件 / 类名，运行时把样式序列化后插入 `<style>` 标签。优势是样式可以直接读取 props 与 theme；代价是每次渲染都要做样式序列化与哈希计算，并维护一张运行时样式表。

```jsx
import styled from 'styled-components';

const Button = styled.button`
  padding: ${({ size }) => (size === 'large' ? '12px 24px' : '8px 16px')};
  background: ${({ $primary }) => ($primary ? '#4f46e5' : '#e5e7eb')};
  color: ${({ $primary }) => ($primary ? '#fff' : '#111')};
  border-radius: 6px;
`;

// emotion 提供 babel 插件在编译期做静态提取，可显著降低运行时开销
```

**原子化（Tailwind）**：构建时扫描源码中的类名，只为实际用到的原子类生成 CSS，产物极小且天然去重；设计令牌通过 `tailwind.config.js` 的 `theme` 统一约束。

```jsx
// 类名即样式；动态值需要通过完整类名映射，不能拼接字符串
const sizes = {
  sm: 'px-3 py-1.5 text-sm',
  lg: 'px-6 py-3 text-base',
};

export function Button({ size = 'sm', children }) {
  return (
    <button className={`rounded-md font-medium bg-indigo-600 text-white ${sizes[size]}`}>
      {children}
    </button>
  );
}
```

**零运行时（vanilla-extract）**：用 TypeScript 写样式，构建期编译成静态 `.css` 文件，因此既保留了类型安全与组合能力，又没有运行时开销。

```ts
// button.css.ts
import { style, styleVariants } from '@vanilla-extract/css';

export const base = style({
  borderRadius: 6,
  fontWeight: 500,
});

// 变体在构建期展开为多个静态类名
export const tone = styleVariants({
  primary: [base, { background: '#4f46e5', color: '#fff' }],
  neutral: [base, { background: '#e5e7eb', color: '#111' }],
});
```

#### 5.3 选型依据

选型时按以下优先级依次判断：

1. **是否需要在运行时根据任意 props 计算样式？** 需要且逻辑复杂 → 运行时 CSS-in-JS；只需要"切换预设变体" → 零运行时方案 + CSS 变量即可，不必付出运行时代价。
2. **是否有 SSR / React Server Components？** 有 → 优先零运行时（CSS Modules / Tailwind / vanilla-extract）。运行时 CSS-in-JS 依赖 `useInsertionEffect`、Context 等客户端能力，在 RSC 中不可用。
3. **是否追求极致性能与包体积？** 追求 → 零运行时。运行时方案会把样式逻辑打进 JS 包，且每次渲染都有额外计算。
4. **是否需要强设计系统约束？** 需要 → Tailwind（`theme` 即设计令牌）或 vanilla-extract（类型安全的令牌）。
5. **团队熟悉度与迁移成本？** 老项目增量改造 → CSS Modules 或 Tailwind 都能按文件粒度渐进接入；全新项目且团队无强偏好 → Tailwind + CSS Modules 组合是当前最主流的稳妥选择。
6. **是否与既有 CSS 生态（BEM、第三方库覆盖）协作？** 需要覆盖第三方组件库样式 → 保留一层全局 CSS + `@layer` 管理层级。

> **趋势提示**：随着 React Server Components 的普及，**运行时 CSS-in-JS 正在退潮**，社区主流转向"零运行时"路线（Tailwind、CSS Modules、vanilla-extract、Linaria、StyleX）；styled-components 已宣布进入维护模式，新项目评估时建议优先考虑零运行时方案。

**面试常见问法**：

- **CSS Modules 和 CSS-in-JS 的本质区别？** 前者在构建期生成唯一类名，无运行时开销但动态能力弱；后者在运行时生成样式，动态能力强但有运行时开销且与 RSC 不兼容。
- **Tailwind 的 CSS 体积会不会很大？** 不会。它按源码扫描结果生成 CSS，未使用的类不会出现在产物中，同时因为原子类高度复用，总体积通常小于手写 CSS。
- **Tailwind 为什么不能拼接类名？** 构建时是**静态字符串扫描**，`'text-' + size` 拼出的类名无法被扫描到，因此不会生成对应 CSS。需要完整类名映射表或 `safelist`。
- **什么是零运行时 CSS？** 在构建期把样式编译成静态 CSS 文件（vanilla-extract / Linaria / StyleX），浏览器只需解析 CSS，运行时没有样式计算与注入成本。
- **你会怎么为一个新项目选样式方案？** 先看是否有 SSR / RSC 与动态样式需求，再看性能要求与团队熟悉度，最后结合设计系统约束做决定；多数场景下 Tailwind + CSS Modules 组合已足够。

**易错点**：

| 常见错误 | 现象 | 原因 | 解决方案 |
|---------|------|------|---------|
| 在 RSC 中使用运行时 CSS-in-JS | 构建报错或样式丢失 | RSC 不支持 `useInsertionEffect`、Context 等客户端能力 | 改用 CSS Modules / Tailwind / vanilla-extract |
| 在 Tailwind 中拼接类名 | 样式不生效 | 构建期静态扫描无法识别拼接结果 | 用完整类名映射表或 `safelist` 声明 |
| 运行时 CSS-in-JS 未做 SSR 提取 | 首屏闪烁（FOUC） | 样式在客户端 JS 执行后才注入 | 配置关键 CSS 提取（如 emotion 的 `extractCritical`） |
| 混用多套方案且无边界 | 样式覆盖关系混乱、体积膨胀 | 缺少统一约束 | 明确分工：原子类写布局与常规样式，CSS Modules 写复杂组件，全局 CSS 只保留重置与令牌 |

> 📖 **参考链接**：
> - [CSS Modules 官方文档](https://github.com/css-modules/css-modules)
> - [Tailwind CSS 官方文档](https://tailwindcss.com/docs/utility-first)
> - [vanilla-extract 官方文档](https://vanilla-extract.style/)

---

## 本章学习自检

完成本章学习后，应该能够：

**基础篇：**
- [ ] 手写 transition 和 animation 实现常见动画效果
- [ ] 解释 transform 相对于 top/left 的性能优势
- [ ] 使用媒体查询实现响应式布局
- [ ] 区分 rem / em / vh / vw 的参照物和使用场景
- [ ] 用自己的话解释回流和重绘的区别
- [ ] 列出至少 4 种减少回流重绘的优化策略
- [ ] 使用 CSS 变量实现暗黑模式切换
- [ ] 使用 @supports 实现渐进增强，写出浏览器兼容回退方案
- [ ] 使用 scroll-snap 实现原生轮播/全屏滚动效果
- [ ] 使用 Container Queries 实现组件级响应式布局
- [ ] 使用 @layer 管理样式优先级，覆盖第三方库样式
- [ ] 使用 CSS Nesting 原生嵌套编写组件样式
- [ ] 使用 :has() 实现父选择器和表单验证联动

**扩展篇：**
- [ ] 说出 Sass 和 Less 的核心区别（变量符号、混入语法、函数支持）
- [ ] 理解 Tailwind 的 utility-first 理念和原子化 CSS 概念
- [ ] 使用 CSS Modules 实现组件级样式隔离，区分 :local 和 :global
- [ ] 按 BEM 规范命名一个完整的组件（块、元素、修饰符）
- [ ] 说出 OOCSS 的两条核心原则
- [ ] 列举 SMACSS 的五类规则及其前缀约定
- [ ] 画图描述 ITCSS 的七层倒三角结构
- [ ] 根据项目规模选择合适的方法论组合
- [ ] 理解 `contain` 和 `content-visibility` 的性能优化原理，能说出适用场景
- [ ] 理解 subgrid 的核心价值，能说出与普通嵌套网格的区别
- [ ] 掌握 `grid-auto-rows` / `grid-auto-columns` 的使用场景
- [ ] 了解 masonry 布局的当前状态及 CSS Columns 替代方案
- [ ] 使用 `@property` 定义自定义属性类型，实现自定义属性动画
- [ ] 理解 View Transitions API 的基本用法（SPA 和 MPA）
- [ ] 了解 Popover API 和 Anchor Positioning 的基本用法和核心价值
- [ ] 使用 CSS 逻辑属性（`margin-inline` / `padding-block` / `inset`）编写可自动适配 RTL 的布局
- [ ] 用 `clamp()` 实现无需媒体查询的流体排版，并说明为什么推荐 `rem + vw` 混合
- [ ] 说出 `clamp()` 等价于 `max(MIN, min(VAL, MAX))` 带来的两个书写注意事项
- [ ] 使用 `prefers-reduced-motion` 实现无障碍动效降级，并解释为什么用 `0.01ms` 而非 `0s`
- [ ] 区分滚动条定制的标准属性与 WebKit 伪元素两套 API，并写出 `@supports` 分流写法
- [ ] 说出隐藏滚动条的可访问性风险及替代方案
- [ ] 对比 CSS Modules / CSS-in-JS / 原子化 / 零运行时四类方案，并给出选型依据
- [ ] 解释为什么运行时 CSS-in-JS 与 React Server Components 不兼容

---

> **学习导航**：
> - 返回 [学习路线总览](../README.md)
> - 本模块其他文件：[01-HTML核心与语义化](./01-HTML核心与语义化.md) | [02-CSS布局核心](./02-CSS布局核心.md) | [04-HTMLCSS笔面试题集](./04-HTMLCSS笔面试题集.md)
> - 实战应用：[企业后台管理系统](../10-project/01-企业后台管理系统实战.md)