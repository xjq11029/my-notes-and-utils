# uniapp 渲染差异与性能优化

> 模块：12-cross-platform（uniapp 跨端开发）
> 内容：H5 vs 小程序渲染差异、跨端样式排查路径、常见渲染陷阱、首屏秒开优化、原生模块拆分策略、小程序性能优化专项
> 格式：八段式（核心概念 → 底层原理 → 实战应用 → 常见面试题 → 避坑指南 → 本章学习自检）
> 前置知识：[uniapp 跨端开发基础](./01-uniapp跨端开发基础.md)、[加载性能优化](../08-performance/01-加载性能优化.md)

---

## 一、核心概念

uniapp 的"一套代码多端运行"理念虽然极大地提高了开发效率，但各平台的渲染引擎存在本质差异。理解这些差异并进行针对性优化，是跨端开发从"能跑"到"好用"的关键跨越。

**跨端渲染差异的核心矛盾：**

```
H5 端的渲染引擎：
  浏览器内核（WebKit / Blink）→ DOM 树 + CSSOM 树 → 渲染树 → 布局 → 绘制 → 合成
  特点：完整的 CSS 支持、灵活的事件模型、无访问限制的开发体验

小程序的渲染引擎：
  双线程架构（渲染层 WebView + 逻辑层 JSCore）→ 同层渲染 → 数据驱动更新
  特点：受限的 CSS 支持、setData 数据通信、原生组件层级最高

App 端的渲染引擎：
  Weex 原生渲染引擎 / NVUE → 原生组件 → 独立渲染管线
  特点：Native 渲染性能、flexbox 布局、独立样式系统
```

**跨端渲染差异的四大核心问题：**

1. **渲染引擎差异**：H5 使用 DOM 渲染，小程序使用同层渲染，导致同一段 CSS 在不同端表现不同
2. **CSS 支持度差异**：小程序的 CSS 支持是 Web 的子集，部分 CSS 属性在小程序中不可用
3. **布局模型差异**：小程序默认 flex 布局，H5 默认 block 布局，导致布局行为差异
4. **原生组件限制**：小程序原生组件（video、map、canvas）层级最高，无法被普通元素覆盖

---

## 二、底层原理

### 2.1 H5 vs 小程序渲染差异

#### 2.1.1 渲染引擎架构对比

**H5 端渲染（浏览器内核）：**

```
H5 渲染流程：

  浏览器主线程
  ┌─────────────────────────────────────────────────────────┐
  │  HTML 解析器 → DOM 树                                    │
  │  CSS 解析器  → CSSOM 树                                 │
  │  JavaScript 引擎（V8 / JavaScriptCore）                  │
  │                       │                                  │
  │                       ▼                                  │
  │              渲染树（Render Tree）                        │
  │                       │                                  │
  │                       ▼                                  │
  │              布局（Layout）                               │
  │                       │                                  │
  │                       ▼                                  │
  │              绘制（Paint）                                │
  │                       │                                  │
  │                       ▼                                  │
  │              合成（Composite）                            │
  └─────────────────────────────────────────────────────────┘
                              │
                              ▼
                      屏幕像素输出

  特点：
  - 单线程渲染（主线程 + 合成线程）
  - 完整的 CSS 属性支持
  - 可以直接操作 DOM（document.querySelector）
  - 事件冒泡遵循 DOM 树结构
  - 支持所有 Web API（localStorage、fetch、WebSocket 等）
```

**小程序端渲染（双线程 + 同层渲染）：**

```
小程序渲染流程：

  渲染层（WebView）                    逻辑层（JSCore）
  ┌──────────────────────┐          ┌──────────────────────┐
  │                      │          │                      │
  │  WXML 模板            │          │  JavaScript 逻辑      │
  │  WXSS 样式            │          │  - 数据管理           │
  │                      │          │  - 生命周期           │
  │  渲染树构建            │          │  - API 调用           │
  │                      │          │                      │
  │  ┌────────────────┐  │          │  ┌────────────────┐  │
  │  │  原生组件层      │  │          │  │  setData()     │  │
  │  │  (video/map/   │  │          │  │  数据通信       │  │
  │  │   canvas 等)    │  │          │  │                │  │
  │  └────────────────┘  │          │  └────────────────┘  │
  │                      │          │           │           │
  └──────────────────────┘          └───────────┼───────────┘
              ▲                                  │
              │          Native 桥接层            │
              └──────────────────────────────────┘
                    setData 数据传递（序列化 + 传输）

  特点：
  - 双线程隔离：渲染层和逻辑层是独立的两个线程
  - 同层渲染：原生组件（video、map、canvas）与 WebView 组件在同一层级渲染
  - 数据驱动：逻辑层通过 setData 向渲染层传递数据，渲染层据此更新视图
  - CSS 受限：不支持部分 CSS 属性（如 position: fixed 在 scroll-view 内无效）
  - 原生组件层级最高：video、map、canvas 等原生组件无法被普通视图覆盖
```

**双线程架构的核心瓶颈 —— setData 通信：**

```
逻辑层数据变化 → setData({ key: value }) → 序列化数据 → Native 桥接层
                                                              │
                                                              ▼
                                                      渲染层 WebView
                                                      （反序列化 → 更新视图）

每次 setData 调用都会经历：
  1. 数据序列化（JSON.stringify）
  2. 跨线程通信（Native Bridge）
  3. 数据反序列化（JSON.parse）
  4. 视图层 Diff 计算
  5. 渲染更新

这导致 setData 是天然的"昂贵操作"，频繁调用会造成性能问题。
```

#### 2.1.2 Flex 布局差异

小程序和 H5 在 flex 布局上的默认行为存在差异，这是跨端开发中最常见的布局问题。

**关键差异对比：**

| 特性 | H5 端 | 小程序端 | 影响 |
|------|-------|---------|------|
| `<view>` 默认 display | `block` | `block` | 两端默认均为 block，需手动设 flex 才能启用弹性布局 |
| `flex-wrap` 默认值 | `nowrap` | `nowrap` | 相同 |
| `flex-shrink` 默认值 | `1`（允许收缩） | `0`（不允许收缩） | 小程序中 flex 子元素默认不会收缩，可能导致溢出 |
| `inline-flex` 支持 | 支持 | 不支持 | 小程序中无法使用 `display: inline-flex` |
| `gap` 属性支持 | 现代浏览器支持 | 部分小程序基础库版本不支持 | 建议使用 `margin` 替代 `gap` |

**统一跨端 flex 布局的写法：**

```vue
<template>
  <view class="flex-demo">
    <!-- 方案一：显式声明所有 flex 属性（推荐） -->
    <view class="flex-container-safe">
      <view class="flex-item">项目 1</view>
      <view class="flex-item">项目 2</view>
      <view class="flex-item">项目 3</view>
    </view>

    <!-- 方案二：使用条件编译处理差异 -->
    <view class="flex-container">
      <view class="flex-child">子元素</view>
      <view class="flex-child">子元素</view>
    </view>
  </view>
</template>

<style>
/* ========== 方案一：安全写法（推荐） ========== */
.flex-container-safe {
  display: flex;
  flex-direction: row;          /* 显式指定方向 */
  flex-wrap: wrap;              /* 显式指定换行 */
  justify-content: space-between;
  align-items: center;
}

.flex-item {
  /* 显式指定 flex 属性，避免默认值差异 */
  flex: 0 0 auto;               /* flex-grow: 0, flex-shrink: 0, flex-basis: auto */
  width: 200rpx;
  height: 100rpx;
  /* 用 margin 替代 gap */
  margin-right: 20rpx;
  margin-bottom: 20rpx;
}

.flex-item:last-child {
  margin-right: 0;
}

/* ========== 方案二：条件编译处理差异 ========== */
.flex-container {
  display: flex;

  /* #ifdef H5 */
  /* H5 端默认 block，需要显式设置 flex */
  flex-direction: row;
  /* #endif */
}

.flex-child {
  /* #ifdef MP-WEIXIN */
  /* 小程序端默认 flex-shrink: 0，需要显式允许收缩 */
  flex-shrink: 1;
  /* #endif */

  width: 200rpx;
  height: 100rpx;
  background-color: #e0e0e0;
  margin-right: 20rpx;
}
</style>
```

#### 2.1.3 CSS 支持度差异

小程序对 CSS 的支持是 Web 标准的一个子集，以下是一些常见的 CSS 兼容性问题。

**CSS 属性支持度对比：**

| CSS 属性/特性 | H5 端 | 微信小程序 | 说明 |
|--------------|-------|-----------|------|
| `position: fixed` | 完全支持 | 部分支持 | 在 scroll-view 内失效 |
| `position: sticky` | 支持 | 不支持 | 可使用 scroll-view 配合 JS 模拟 |
| `overflow: scroll` | 支持 | 不支持（使用 scroll-view 替代） | 小程序需要专门的 scroll-view 组件 |
| `z-index` | 完全支持 | 对原生组件无效 | 原生组件层级最高 |
| `background-attachment` | 支持 | 不支持 | 小程序不支持固定背景 |
| `::before` / `::after` | 完整支持 | 支持但有限制 | 不能在原生组件上使用 |
| `transform` | 完整支持 | 支持 2D transform | 3D transform 部分支持 |
| `animation` | 完整支持 | 支持但性能有限 | 复杂动画建议使用小程序 API |
| `filter` | 支持 | 不支持 | 小程序不支持滤镜效果 |
| `backdrop-filter` | 支持 | 不支持 | 毛玻璃效果在小程序中无法实现 |
| `vh` / `vw` 单位 | 支持 | 支持 | 推荐使用 rpx 替代 |
| `calc()` | 支持 | 支持 | 运算符前后必须有空格 |
| `var()` (CSS 变量) | 支持 | 部分支持 | 基础库 2.11.1+ 支持 |
| `@media` 查询 | 支持 | 不支持 | 小程序不支持媒体查询 |
| `@keyframes` | 支持 | 支持 | 性能需注意 |

**CSS 兼容性写法示例：**

```vue
<style>
/* ========== 跨端安全 CSS 写法 ========== */

/* 1. 用 rpx 替代 vh/vw，保证跨端一致性 */
.container {
  width: 750rpx;       /* 替代 100vw */
  min-height: 100vh;   /* vh 在小程序中可用，但推荐使用 JS 动态计算 */
}

/* 2. calc() 运算符前后必须有空格 */
.calc-safe {
  width: calc(100% - 40rpx);      /* 正确 */
  /* width: calc(100%-40rpx); */  /* 错误：缺少空格 */
}

/* 3. 避免使用 backdrop-filter，用半透明背景替代 */
.glass-effect {
  /* #ifdef H5 */
  backdrop-filter: blur(10px);
  /* #endif */
  /* #ifdef MP-WEIXIN */
  background-color: rgba(255, 255, 255, 0.9); /* 降级方案 */
  /* #endif */
}

/* 4. 避免 filter 属性，用 CSS 变量或图片替代 */
.image-effect {
  /* #ifdef H5 */
  filter: grayscale(100%);
  /* #endif */
  /* #ifdef MP-WEIXIN */
  opacity: 0.6; /* 降级方案 */
  /* #endif */
}

/* 5. 不支持 @media 查询，使用 JS 动态样式 */
/* 不要在小程序中使用 @media，改用 JS 获取屏幕宽度动态设置样式 */

/* 6. 渐变背景兼容写法 */
.gradient-bg {
  /* 线性渐变 */
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  /* 备注：小程序支持 linear-gradient 和 radial-gradient */
}

/* 7. 安全的内阴影写法 */
.inner-shadow {
  box-shadow: inset 0 2rpx 8rpx rgba(0, 0, 0, 0.1);
}
</style>
```

### 2.2 标准排查路径：渲染问题的系统化诊断

当跨端应用出现渲染差异时，按照以下标准的排查路径，可以快速定位问题根因。

```
标准排查路径（五步法）：

第一步：环境检查
  ├─ 确认目标平台和基础库版本
  ├─ 检查 uni-app 编译模式（Vue 2 / Vue 3）
  ├─ 确认是否开启了 nvue 模式
  └─ 检查 manifest.json 中的平台配置

第二步：条件编译排查
  ├─ 检查 template 中的条件编译块是否匹配目标平台
  ├─ 检查 script 中的平台差异逻辑是否被正确编译
  ├─ 检查 style 中的条件编译注释是否正确闭合
  └─ 注意：条件编译注释不能嵌套在 CSS 属性值内部

第三步：样式隔离
  ├─ 检查是否使用了 scoped 样式，导致样式作用域差异
  ├─ 小程序中 scoped 样式通过属性选择器实现，H5 通过 data-v-xxx 实现
  ├─ 检查全局样式和页面样式是否存在冲突
  └─ 确认 uni.scss 中的变量在不同平台的值是否一致

第四步：原生组件限制
  ├─ 确认是否在原生组件（video、map、canvas、textarea）上使用了覆盖层
  ├─ 检查 z-index 是否在原生组件上失效
  ├─ 确认 scroll-view 内的 fixed 定位是否按预期工作
  └─ 使用 cover-view / cover-image 替代普通 view 覆盖原生组件

第五步：数据绑定差异
  ├─ 检查 v-model 在小程序端的双向绑定行为
  ├─ 确认数组/对象变更的响应式是否被正确检测
  ├─ 小程序中对象新增属性需要使用 $set 或 this.$forceUpdate()
  └─ 检查 setData 传递的数据量是否过大
```

**排查工具函数：**

```javascript
// utils/debug.js - 跨端调试工具

/**
 * 获取当前渲染环境的详细信息
 */
export function getRenderEnvInfo() {
  const info = {
    // 平台信息
    platform: '',
    // 基础库版本（仅小程序）
    SDKVersion: '',
    // 设备信息
    system: '',
    model: '',
    pixelRatio: 1,
    screenWidth: 0,
    screenHeight: 0,
    // uniapp 编译模式
    vueVersion: '',
    // 是否开启 nvue
    isNVue: false
  }

  try {
    const systemInfo = uni.getSystemInfoSync()
    info.platform = systemInfo.platform
    info.system = systemInfo.system
    info.model = systemInfo.model
    info.pixelRatio = systemInfo.pixelRatio
    info.screenWidth = systemInfo.screenWidth
    info.screenHeight = systemInfo.screenHeight

    // #ifdef MP-WEIXIN
    info.SDKVersion = systemInfo.SDKVersion
    // #endif

    // #ifdef VUE3
    info.vueVersion = 'Vue 3'
    // #endif
    // #ifdef VUE2
    info.vueVersion = 'Vue 2'
    // #endif

    // #ifdef APP-NVUE
    info.isNVue = true
    // #endif
  } catch (err) {
    console.error('获取环境信息失败：', err)
  }

  return info
}

/**
 * 打印当前页面的布局信息（用于调试样式问题）
 */
export function debugLayout(selector) {
  const query = uni.createSelectorQuery()
  query.select(selector).boundingClientRect()
  query.select(selector).fields({
    computedStyle: ['width', 'height', 'margin', 'padding', 'display', 'position', 'zIndex']
  })
  query.exec((res) => {
    console.log(`[布局调试] ${selector}：`, JSON.stringify(res, null, 2))
  })
}

/**
 * 检查 CSS 属性是否在当前平台支持
 */
export function checkCSSSupport(property) {
  // #ifdef H5
  return CSS.supports(property, 'initial')
  // #endif

  // #ifdef MP-WEIXIN
  // 小程序中常见的 CSS 支持情况
  const unsupportedInMP = [
    'backdrop-filter',
    'filter',
    'position: sticky',
    'background-attachment',
    '@media'
  ]
  return !unsupportedInMP.some(item =>
    property.toLowerCase().includes(item.toLowerCase())
  )
  // #endif

  // #ifdef APP-PLUS
  return true // App 端通常支持更完整的 CSS
  // #endif
}
```

### 2.3 跨端渲染差异常见陷阱

#### 2.3.1 z-index 层级问题

```
小程序层级体系（从上到下）：

  ┌─────────────────────────────────────┐
  │ 第 1 层：原生组件                    │  ← video、map、canvas、textarea、camera
  │  (层级最高，无法被普通元素覆盖)        │
  ├─────────────────────────────────────┤
  │ 第 2 层：cover-view / cover-image   │  ← 专门用于覆盖原生组件的组件
  ├─────────────────────────────────────┤
  │ 第 3 层：普通视图组件                │  ← view、text、image 等
  │  (z-index 只在这一层内部生效)         │
  ├─────────────────────────────────────┤
  │ 第 4 层：fixed 定位元素              │  ← 在 scroll-view 内可能失效
  └─────────────────────────────────────┘
```

**z-index 问题解决方案：**

```vue
<template>
  <view>
    <!-- 问题场景：弹窗被 video 组件遮挡 -->
    <video
      id="myVideo"
      src="https://example.com/video.mp4"
      :show-center-play-btn="true"
      class="video-player"
    />

    <view class="video-overlay" v-if="showOverlay">
      <!-- 错误写法：普通 view 无法覆盖 video -->
      <view class="overlay-content">这段文字会被 video 遮挡</view>

      <!-- 正确写法：使用 cover-view 覆盖原生组件 -->
      <cover-view class="cover-content">
        <cover-image src="/static/play-icon.png" class="play-icon" />
        <cover-view class="cover-text">点击播放</cover-view>
      </cover-view>
    </view>
  </view>
</template>

<script>
export default {
  data() {
    return {
      showOverlay: true
    }
  }
}
</script>

<style>
.video-player {
  width: 100%;
  height: 400rpx;
}

/* 普通 view 无法覆盖 video，此样式无效 */
.video-overlay {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 400rpx;
  z-index: 9999; /* 在小程序中无效 */
}

/* cover-view 可以覆盖原生组件 */
.cover-content {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 400rpx;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  background-color: rgba(0, 0, 0, 0.3);
}

.play-icon {
  width: 80rpx;
  height: 80rpx;
}

.cover-text {
  color: #fff;
  font-size: 28rpx;
  margin-top: 20rpx;
}
</style>
```

#### 2.3.2 fixed 定位问题

小程序中 `position: fixed` 在 `<scroll-view>` 内部会失效，因为 `<scroll-view>` 会创建新的层叠上下文。

```vue
<template>
  <view class="page">
    <!-- 错误写法：fixed 元素在 scroll-view 内部 -->
    <scroll-view scroll-y class="wrong-scroll">
      <view class="content">
        <view v-for="item in 50" :key="item" class="item">内容 {{ item }}</view>
      </view>
      <!-- 这里的 fixed 按钮在小程序中不会固定在屏幕底部 -->
      <view class="fixed-btn-wrong">提交（错误写法）</view>
    </scroll-view>

    <!-- 正确写法：fixed 元素放在 scroll-view 外部 -->
    <scroll-view scroll-y class="correct-scroll">
      <view class="content">
        <view v-for="item in 50" :key="item" class="item">内容 {{ item }}</view>
      </view>
    </scroll-view>
    <!-- 固定按钮在 scroll-view 外部，各端均可正常 fixed -->
    <view class="fixed-btn-correct">
      <button type="primary">提交（正确写法）</button>
    </view>
  </view>
</template>

<style>
.page {
  position: relative;
  height: 100vh;
}

.wrong-scroll,
.correct-scroll {
  height: 100vh;
}

.fixed-btn-wrong {
  position: fixed;
  bottom: 0;
  left: 0;
  width: 100%;
  /* 在小程序的 scroll-view 内部，fixed 失效 */
}

.fixed-btn-correct {
  position: fixed;
  bottom: 0;
  left: 0;
  width: 100%;
  padding: 20rpx;
  background-color: #fff;
  box-shadow: 0 -4rpx 12rpx rgba(0, 0, 0, 0.05);
  /* 安全区域适配 */
  padding-bottom: calc(20rpx + env(safe-area-inset-bottom));
}
</style>
```

#### 2.3.3 overflow 滚动问题

小程序不支持 `overflow: scroll` 和 `overflow: auto`，需要使用 `<scroll-view>` 组件替代。

```vue
<template>
  <view>
    <!-- 错误写法：使用 CSS overflow 实现滚动 -->
    <view class="overflow-container">
      <view v-for="item in 20" :key="item" class="overflow-item">
        内容 {{ item }}
      </view>
    </view>

    <!-- 正确写法：使用 scroll-view 组件 -->
    <scroll-view scroll-y class="scroll-container">
      <view v-for="item in 20" :key="item" class="scroll-item">
        内容 {{ item }}
      </view>
    </scroll-view>

    <!-- 自定义滚动条样式（仅 H5 端生效，见下方 style 块） -->
  </view>
</template>

<style>
/* 错误写法：小程序不支持 */
.overflow-container {
  height: 400rpx;
  overflow-y: scroll; /* 小程序中无效 */
}

/* 正确写法：配合 scroll-view 使用 */
.scroll-container {
  height: 400rpx;
  /* 不需要设置 overflow，scroll-view 自带滚动能力 */
}

/* 自定义滚动条样式（仅 H5 端生效） */
/* #ifdef H5 */
.scroll-container::-webkit-scrollbar {
  width: 0;
  height: 0;
}
/* #endif */
</style>
```

> 📖 **参考链接**：
> - [uni-app 官方文档](https://uniapp.dcloud.net.cn/)
> - [uni-app 性能优化](https://uniapp.dcloud.net.cn/tutorial/performance.html)
> - [uni-app 组件文档](https://uniapp.dcloud.net.cn/component/)

---

## 三、实战应用

### 3.1 首屏秒开优化

小程序和 H5 对首屏加载速度极为敏感。以下是一套完整的首屏优化方案。

#### 3.1.1 分包加载

分包是将小程序代码拆分为多个包，首屏只加载主包，其他页面按需加载。

```json
// pages.json - 分包配置
{
  "pages": [
    // 主包页面（首屏相关）
    { "path": "pages/index/index" },
    { "path": "pages/category/category" },
    { "path": "pages/cart/cart" },
    { "path": "pages/user/user" }
  ],
  "subPackages": [
    {
      "root": "subpkg-order",
      "name": "order",
      "pages": [
        { "path": "order-list/order-list" },
        { "path": "order-detail/order-detail" },
        { "path": "order-comment/order-comment" }
      ]
    },
    {
      "root": "subpkg-activity",
      "name": "activity",
      "pages": [
        { "path": "seckill/seckill" },
        { "path": "coupon-center/coupon-center" }
      ]
    },
    {
      "root": "subpkg-member",
      "name": "member",
      "pages": [
        { "path": "vip-center/vip-center" },
        { "path": "points/points" }
      ]
    }
  ],
  // 预加载配置：进入首页时预下载分包
  "preloadRule": {
    "pages/index/index": {
      "network": "wifi",  // 仅在 WiFi 下预下载
      "packages": ["subpkg-order"]
    },
    "pages/category/category": {
      "network": "all",
      "packages": ["subpkg-activity"]
    }
  }
}
```

**分包大小限制（微信小程序）：**

| 项目 | 限制 |
|------|------|
| 整个小程序 | 不超过 20MB |
| 单个分包 | 不超过 2MB |
| 主包 | 不超过 2MB（建议控制） |
| 总包数 | 不限，但总大小不超 20MB |

#### 3.1.2 组件懒加载

```javascript
// pages/index/index.vue
<script>
// 传统方式：首屏加载所有组件
// import HeavyChart from '@/components/heavy-chart/heavy-chart.vue'
// import RichEditor from '@/components/rich-editor/rich-editor.vue'

export default {
  components: {
    // 轻量组件：直接注册（首屏必需）
    ProductCard: () => import('@/components/product-card/product-card.vue'),

    // 重量组件：异步加载（非首屏必需）
    // #ifdef VUE3
    HeavyChart: defineAsyncComponent({
      loader: () => import('@/components/heavy-chart/heavy-chart.vue'),
      delay: 300,       // 延迟 300ms 再显示 loading
      timeout: 5000     // 超时 5s
    }),
    // #endif

    // #ifdef VUE2
    // Vue 2 中异步组件写法
    HeavyChart: () => ({
      component: import('@/components/heavy-chart/heavy-chart.vue'),
      loading: LoadingComponent,
      delay: 300,
      timeout: 5000
    }),
    // #endif
  },
  data() {
    return {
      // 控制非首屏组件的渲染时机
      isChartVisible: false
    }
  },
  onReady() {
    // 首屏渲染完成后，延迟加载非核心组件
    // #ifdef MP-WEIXIN
    // 小程序中使用 nextTick 确保首屏渲染完成
    this.$nextTick(() => {
      setTimeout(() => {
        this.isChartVisible = true
      }, 500)
    })
    // #endif

    // #ifdef H5
    // H5 端使用 requestIdleCallback 在空闲时加载
    if (window.requestIdleCallback) {
      requestIdleCallback(() => {
        this.isChartVisible = true
      })
    } else {
      setTimeout(() => {
        this.isChartVisible = true
      }, 500)
    }
    // #endif
  }
}
</script>

<template>
  <view>
    <!-- 首屏组件：立即渲染 -->
    <ProductCard :product="hotProduct" />

    <!-- 非首屏组件：条件渲染 + 懒加载 -->
    <HeavyChart v-if="isChartVisible" :data="chartData" />
  </view>
</template>
```

#### 3.1.3 图片懒加载

```vue
<template>
  <view>
    <!-- 方式一：使用 loading="lazy"（仅 H5 端支持） -->
    <!-- #ifdef H5 -->
    <image
      v-for="item in imageList"
      :key="item.id"
      :src="item.url"
      loading="lazy"
      class="lazy-image"
      mode="widthFix"
    />
    <!-- #endif -->

    <!-- 方式二：使用 IntersectionObserver（跨端通用） -->
    <view v-for="item in imageList" :key="item.id" :data-id="item.id" class="image-wrapper">
      <!-- 占位图 -->
      <image
        v-if="!item.loaded"
        src="/static/placeholder.png"
        class="lazy-image"
        mode="widthFix"
      />
      <!-- 真实图片 -->
      <image
        v-if="item.loaded"
        :src="item.url"
        class="lazy-image"
        mode="widthFix"
        @load="onImageLoad(item.id)"
        @error="onImageError(item.id)"
      />
    </view>
  </view>
</template>

<script>
export default {
  data() {
    return {
      imageList: [],
      observer: null
    }
  },
  mounted() {
    // 初始化 IntersectionObserver
    this.initImageObserver()
  },
  beforeUnmount() {
    // 销毁观察器
    if (this.observer) {
      this.observer.disconnect()
    }
  },
  methods: {
    initImageObserver() {
      // #ifdef MP-WEIXIN
      // 小程序中使用 createIntersectionObserver
      this.observer = uni.createIntersectionObserver(this, {
        thresholds: [0.1]
      })

      this.observer.relativeToViewport({ bottom: 100 }).observe('.image-wrapper', (res) => {
        if (res.intersectionRatio > 0) {
          const id = res.dataset.id
          this.loadImage(id)
        }
      })
      // #endif

      // #ifdef H5
      // H5 端使用原生 IntersectionObserver
      this.observer = new IntersectionObserver((entries) => {
        entries.forEach((entry) => {
          if (entry.isIntersecting) {
            const id = entry.target.dataset.id
            this.loadImage(id)
            this.observer.unobserve(entry.target)
          }
        })
      }, {
        rootMargin: '100px 0px' // 提前 100px 开始加载
      })

      this.$nextTick(() => {
        document.querySelectorAll('.image-wrapper').forEach((el) => {
          this.observer.observe(el)
        })
      })
      // #endif
    },

    loadImage(id) {
      const item = this.imageList.find(img => img.id === id)
      if (item && !item.loaded) {
        item.loaded = true
      }
    },

    onImageLoad(id) {
      console.log('图片加载成功：', id)
    },

    onImageError(id) {
      console.error('图片加载失败：', id)
      const item = this.imageList.find(img => img.id === id)
      if (item) {
        item.url = '/static/error-image.png' // 错误占位图
        item.loaded = true
      }
    }
  }
}
</script>

<style>
.image-wrapper {
  width: 100%;
  margin-bottom: 20rpx;
}

.lazy-image {
  width: 100%;
  display: block;
}
</style>
```

### 3.2 原生模块与 AI SDK 极限依赖拆分策略

在集成 AI SDK（如语音识别、图像识别、自然语言处理等）时，这些 SDK 通常体积较大，如果直接打入主包会严重影响首屏加载速度。以下是一套极限依赖拆分策略。

```javascript
// utils/ai-sdk-loader.js - AI SDK 动态加载器

/**
 * AI SDK 加载管理器
 * 核心策略：
 * 1. 将 AI SDK 放在独立分包中
 * 2. 使用 require.async 动态加载（小程序）
 * 3. 加载完成后缓存实例，避免重复加载
 * 4. 加载失败时提供降级方案
 */

const SDK_CACHE = new Map()

class AISDKLoader {
  constructor() {
    this.loadingPromises = new Map()
  }

  /**
   * 动态加载语音识别 SDK
   */
  async loadVoiceSDK() {
    return this.loadSDK('voice', async () => {
      // #ifdef MP-WEIXIN
      // 小程序：从独立分包动态加载
      await require.async('../subpkg-ai-sdk/voice-sdk/index.js')
      return new Promise((resolve, reject) => {
        const manager = wx.getRecorderManager()
        resolve(manager)
      })
      // #endif

      // #ifdef H5
      // H5：按需动态 import
      const { default: VoiceSDK } = await import(
        /* webpackChunkName: "voice-sdk" */
        '@/sdk/voice-sdk/index.js'
      )
      return new VoiceSDK()
      // #endif
    })
  }

  /**
   * 动态加载 OCR 识别 SDK
   */
  async loadOCRSDK() {
    return this.loadSDK('ocr', async () => {
      // #ifdef MP-WEIXIN
      await require.async('../subpkg-ai-sdk/ocr-sdk/index.js')
      // 小程序 OCR 通常使用云函数或插件
      return {
        recognize: async (imagePath) => {
          return new Promise((resolve, reject) => {
            wx.cloud.callFunction({
              name: 'ocrRecognize',
              data: { imagePath }
            }).then(resolve).catch(reject)
          })
        }
      }
      // #endif

      // #ifdef H5
      const { default: OCRSDK } = await import(
        /* webpackChunkName: "ocr-sdk" */
        '@/sdk/ocr-sdk/index.js'
      )
      return new OCRSDK()
      // #endif
    })
  }

  /**
   * 动态加载 NLP 自然语言处理 SDK
   */
  async loadNLPSDK() {
    return this.loadSDK('nlp', async () => {
      // #ifdef MP-WEIXIN
      // 小程序 NLP 通常通过 API 调用，不需要本地 SDK
      return {
        analyze: async (text) => {
          const res = await uni.request({
            url: 'https://api.example.com/nlp/analyze',
            method: 'POST',
            data: { text }
          })
          return res.data
        }
      }
      // #endif

      // #ifdef H5
      const { default: NLPSDK } = await import(
        /* webpackChunkName: "nlp-sdk" */
        '@/sdk/nlp-sdk/index.js'
      )
      return new NLPSDK()
      // #endif
    })
  }

  /**
   * 通用 SDK 加载器（带缓存、去重、降级）
   */
  async loadSDK(name, loader) {
    // 1. 检查缓存
    if (SDK_CACHE.has(name)) {
      return SDK_CACHE.get(name)
    }

    // 2. 检查是否正在加载（去重）
    if (this.loadingPromises.has(name)) {
      return this.loadingPromises.get(name)
    }

    // 3. 开始加载
    const loadPromise = loader()
      .then((instance) => {
        SDK_CACHE.set(name, instance)
        this.loadingPromises.delete(name)
        return instance
      })
      .catch((err) => {
        console.error(`[AI SDK] ${name} 加载失败：`, err)
        this.loadingPromises.delete(name)

        // 降级方案：返回一个 mock 对象
        return this.getFallbackSDK(name)
      })

    this.loadingPromises.set(name, loadPromise)
    return loadPromise
  }

  /**
   * 降级方案：当 SDK 加载失败时返回基础功能
   */
  getFallbackSDK(name) {
    const fallbacks = {
      voice: {
        start: () => console.warn('语音识别 SDK 不可用'),
        stop: () => {},
        isAvailable: false
      },
      ocr: {
        recognize: async () => {
          uni.showToast({ title: 'OCR 功能暂不可用', icon: 'none' })
          return null
        },
        isAvailable: false
      },
      nlp: {
        analyze: async () => {
          uni.showToast({ title: 'NLP 功能暂不可用', icon: 'none' })
          return null
        },
        isAvailable: false
      }
    }
    return fallbacks[name] || { isAvailable: false }
  }
}

// 导出单例
export const aiSDKLoader = new AISDKLoader()

// ========== 使用示例 ==========

// 在需要语音识别功能的页面中
export default {
  data() {
    return {
      voiceSDK: null,
      isRecording: false
    }
  },
  methods: {
    async startRecording() {
      // 按需加载 SDK，不阻塞首屏
      this.voiceSDK = await aiSDKLoader.loadVoiceSDK()

      if (!this.voiceSDK.isAvailable) {
        uni.showToast({ title: '语音识别功能不可用', icon: 'none' })
        return
      }

      this.voiceSDK.start()
      this.isRecording = true
    }
  }
}
```

**分包配置（pages.json）：**

```json
{
  "subPackages": [
    {
      "root": "subpkg-ai-sdk",
      "name": "ai-sdk",
      "pages": []  // 独立分包可以不包含页面
    }
  ]
}
```

### 3.3 小程序性能优化专项

#### 3.3.1 setData 优化

setData 是小程序性能优化的核心，频繁或大数据量的 setData 是导致卡顿的首要原因。

```javascript
// mixins/setDataOptimize.js - setData 优化策略

export default {
  methods: {
    /**
     * 策略一：合并 setData 调用
     * 将多次 setData 合并为一次，减少跨线程通信次数
     */
    // 错误写法：多次调用 setData
    badSetData() {
      this.setData({ name: '张三' })
      this.setData({ age: 18 })
      this.setData({ city: '北京' })
    },

    // 正确写法：合并为一次 setData
    goodSetData() {
      this.setData({
        name: '张三',
        age: 18,
        city: '北京'
      })
    },

    /**
     * 策略二：只传递变化的数据
     * 不要将整个 data 对象传给 setData
     */
    // 错误写法：传递整个 data
    badSetData2() {
      this.setData({
        ...this.data  // 将所有数据都传给渲染层
      })
    },

    // 正确写法：只传递变化的部分
    goodSetData2() {
      this.setData({
        'list[0].name': '新名称'   // 使用数据路径，只更新具体字段
      })
    },

    /**
     * 策略三：控制 setData 频率
     * 对于高频操作，使用节流减少 setData 调用
     */
    throttledSetData(key, value) {
      if (!this._setDataTimer) {
        this._setDataPending = {}
      }

      // 收集待更新的数据
      this._setDataPending[key] = value

      // 清除之前的定时器
      if (this._setDataTimer) {
        clearTimeout(this._setDataTimer)
      }

      // 16ms 后统一更新（一帧的时间）
      this._setDataTimer = setTimeout(() => {
        this.setData(this._setDataPending)
        this._setDataPending = {}
        this._setDataTimer = null
      }, 16)
    },

    /**
     * 策略四：减少 setData 数据量
     * 不要将不参与渲染的数据放在 data 中
     */
    // 错误写法：将不需要渲染的数据放在 data 中
    badDataStructure() {
      return {
        list: [],
        // 以下数据不需要渲染，不应该放在 data 中
        rawData: null,          // 原始数据缓存
        requestId: '',          // 请求 ID
        eventHandlers: null,    // 事件处理器
        // 这些数据应该放在 this 上（非响应式）
      }
    },

    // 正确写法：将非渲染数据挂在 this 上
    goodDataStructure() {
      // 不参与渲染的数据，挂在实例上
      this.rawData = null
      this.requestId = ''
      this.eventHandlers = null

      return {
        list: []  // 只有需要渲染的数据才放在 data 中
      }
    }
  }
}
```

**setData 数据量监控：**

```javascript
// utils/performance-monitor.js - setData 性能监控

/**
 * setData 性能监控（仅开发环境使用）
 */
export function monitorSetData() {
  // #ifdef MP-WEIXIN
  const originalSetData = Page.prototype.setData

  Page.prototype.setData = function(data, callback) {
    const dataSize = JSON.stringify(data).length

    // 警告：单次 setData 数据量超过 256KB
    if (dataSize > 256 * 1024) {
      console.warn(
        `[性能警告] setData 数据量过大：${(dataSize / 1024).toFixed(2)}KB，` +
        `建议减少传递的数据量。数据 keys：${Object.keys(data).join(', ')}`
      )
    }

    // 记录调用栈
    const startTime = Date.now()
    const callStack = new Error().stack

    const wrappedCallback = function() {
      const duration = Date.now() - startTime

      // 警告：setData 耗时超过 50ms
      if (duration > 50) {
        console.warn(
          `[性能警告] setData 耗时过长：${duration}ms，` +
          `数据量：${(dataSize / 1024).toFixed(2)}KB`
        )
      }

      if (typeof callback === 'function') {
        callback.apply(this, arguments)
      }
    }

    return originalSetData.call(this, data, wrappedCallback)
  }
  // #endif
}
```

#### 3.3.2 长列表虚拟滚动

对于包含大量数据的长列表，使用虚拟滚动技术只渲染可视区域内的元素，大幅减少 DOM 节点数量。

```vue
<template>
  <view class="virtual-list">
    <!-- 滚动容器 -->
    <scroll-view
      scroll-y
      class="scroll-container"
      :style="{ height: containerHeight + 'px' }"
      @scroll="onScroll"
    >
      <!-- 占位容器（撑开滚动高度） -->
      <view class="placeholder" :style="{ height: totalHeight + 'px' }">
        <!-- 可视区域内的列表项 -->
        <view
          class="visible-area"
          :style="{ transform: `translateY(${offsetY}px)` }"
        >
          <view
            v-for="item in visibleItems"
            :key="item.id"
            class="list-item"
            :style="{ height: itemHeight + 'px' }"
          >
            <text>{{ item.name }}</text>
          </view>
        </view>
      </view>
    </scroll-view>
  </view>
</template>

<script>
export default {
  data() {
    return {
      // 所有数据
      allItems: [],
      // 可视区域数据
      visibleItems: [],
      // 列表项固定高度
      itemHeight: 80,
      // 容器高度
      containerHeight: 0,
      // 当前滚动偏移量
      offsetY: 0,
      // 可视区域上方隐藏的项数
      startIndex: 0,
      // 可视区域能显示的项数
      visibleCount: 0,
      // 缓冲区项数（上下各多渲染几项，避免快速滚动时白屏）
      bufferCount: 3
    }
  },

  computed: {
    totalHeight() {
      return this.allItems.length * this.itemHeight
    }
  },

  mounted() {
    this.initVirtualList()
  },

  methods: {
    async initVirtualList() {
      // 获取容器高度
      const systemInfo = uni.getSystemInfoSync()
      this.containerHeight = systemInfo.windowHeight

      // 计算可视区域能显示的项数
      this.visibleCount = Math.ceil(this.containerHeight / this.itemHeight) + this.bufferCount * 2

      // 模拟加载数据
      await this.loadData()

      // 初始渲染
      this.updateVisibleItems()
    },

    async loadData() {
      // 模拟 10000 条数据
      this.allItems = Array.from({ length: 10000 }, (_, i) => ({
        id: i + 1,
        name: `列表项 ${i + 1}`
      }))
    },

    onScroll(e) {
      // 计算当前滚动位置对应的起始索引
      const scrollTop = e.detail.scrollTop
      const startIndex = Math.max(0, Math.floor(scrollTop / this.itemHeight) - this.bufferCount)

      // 如果起始索引变化，更新可视区域
      if (startIndex !== this.startIndex) {
        this.startIndex = startIndex
        this.offsetY = startIndex * this.itemHeight
        this.updateVisibleItems()
      }
    },

    updateVisibleItems() {
      const start = Math.max(0, this.startIndex)
      const end = Math.min(this.allItems.length, start + this.visibleCount)
      this.visibleItems = this.allItems.slice(start, end)
    }
  }
}
</script>

<style>
.scroll-container {
  width: 100%;
}

.placeholder {
  position: relative;
  width: 100%;
}

.visible-area {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
}

.list-item {
  display: flex;
  align-items: center;
  padding: 0 30rpx;
  border-bottom: 1rpx solid #eee;
  background-color: #fff;
  font-size: 28rpx;
}
</style>
```

#### 3.3.3 内存管理

```javascript
// mixins/memoryManager.js - 小程序内存管理

export default {
  data() {
    return {
      // 标记页面是否已销毁
      _isDestroyed: false
    }
  },

  onUnload() {
    this._isDestroyed = true
    this.cleanupMemory()
  },

  onHide() {
    // 页面隐藏时，清理不必要的大对象
    this.releaseLargeObjects()
  },

  methods: {
    /**
     * 清理内存
     */
    cleanupMemory() {
      // 1. 清理定时器
      this.clearAllTimers()

      // 2. 移除事件监听
      this.removeAllListeners()

      // 3. 释放图片缓存
      this.releaseImageCache()

      // 4. 释放大对象引用
      this.releaseLargeObjects()

      // 5. 清理请求
      this.abortPendingRequests()
    },

    /**
     * 清理所有定时器
     */
    clearAllTimers() {
      if (this._timers) {
        this._timers.forEach(timer => {
          clearTimeout(timer)
          clearInterval(timer)
        })
        this._timers = []
      }
    },

    /**
     * 安全创建定时器（自动追踪）
     */
    safeSetTimeout(fn, delay) {
      if (!this._timers) this._timers = []
      const timer = setTimeout(() => {
        if (!this._isDestroyed) {
          fn()
        }
        // 自动清理
        const index = this._timers.indexOf(timer)
        if (index > -1) this._timers.splice(index, 1)
      }, delay)
      this._timers.push(timer)
      return timer
    },

    safeSetInterval(fn, interval) {
      if (!this._timers) this._timers = []
      const timer = setInterval(() => {
        if (this._isDestroyed) {
          clearInterval(timer)
          return
        }
        fn()
      }, interval)
      this._timers.push(timer)
      return timer
    },

    /**
     * 移除所有事件监听
     */
    removeAllListeners() {
      // #ifdef MP-WEIXIN
      if (this._eventListeners) {
        this._eventListeners.forEach(({ target, event, handler }) => {
          if (target && target.off) {
            target.off(event, handler)
          }
        })
        this._eventListeners = []
      }
      // #endif
    },

    /**
     * 安全添加事件监听（自动追踪）
     */
    safeAddEventListener(target, event, handler) {
      if (!this._eventListeners) this._eventListeners = []
      target.on(event, handler)
      this._eventListeners.push({ target, event, handler })
    },

    /**
     * 释放图片缓存
     */
    releaseImageCache() {
      // 清理通过 getImageInfo 获取的图片信息缓存
      if (this._imageCache) {
        this._imageCache.clear()
        this._imageCache = null
      }
    },

    /**
     * 释放大对象引用
     */
    releaseLargeObjects() {
      // 将大对象置为 null，帮助 GC 回收
      this.largeDataList = null
      this.imageList = null
      this.cachedData = null
    },

    /**
     * 中断待处理的请求
     */
    abortPendingRequests() {
      if (this._requestTasks) {
        this._requestTasks.forEach(task => {
          if (task && task.abort) {
            task.abort()
          }
        })
        this._requestTasks = []
      }
    },

    /**
     * 安全发起请求（自动追踪）
     */
    safeRequest(options) {
      if (!this._requestTasks) this._requestTasks = []
      const task = uni.request({
        ...options,
        complete: () => {
          // 请求完成后自动清理
          const index = this._requestTasks.indexOf(task)
          if (index > -1) this._requestTasks.splice(index, 1)
        }
      })
      this._requestTasks.push(task)
      return task
    }
  }
}
```

---

## 四、常见面试题

### Q1：H5 和小程序的渲染引擎有什么本质区别？

**回答要点：**

- **H5 端**：运行在浏览器内核（WebKit/Blink）中，使用标准的 DOM + CSSOM 渲染管线，支持完整的 CSS 属性和 Web API，可以直接操作 DOM
- **小程序端**：采用双线程架构（渲染层 WebView + 逻辑层 JSCore），逻辑层通过 setData 与渲染层通信，渲染层使用同层渲染技术处理原生组件
- **核心差异**：H5 是单线程 DOM 渲染，小程序是双线程数据驱动渲染；小程序的原生组件（video、map、canvas）层级最高，无法被普通元素覆盖

### Q2：小程序中 setData 为什么是性能瓶颈？如何优化？

**回答要点：**

- setData 每次调用都会经历：数据序列化 → 跨线程通信（Native Bridge）→ 数据反序列化 → 视图层 Diff → 渲染更新
- 这个过程中涉及多次跨线程通信，每次通信都有开销
- 优化策略：
  1. 合并多次 setData 为一次调用
  2. 只传递变化的数据，使用数据路径（如 `'list[0].name'`）精确更新
  3. 控制 setData 频率，使用节流/防抖
  4. 减少 setData 数据量，不将非渲染数据放在 data 中
  5. 单次 setData 数据量建议不超过 256KB

### Q3：uniapp 中如何解决小程序原生组件（video、map）层级最高的问题？

**回答要点：**

- 原生组件（video、map、canvas、textarea、camera）在小程序中层级最高，z-index 对它们无效
- 解决方案：
  1. 使用 `cover-view` 和 `cover-image` 组件覆盖原生组件
  2. 在需要显示弹窗等覆盖层时，先隐藏原生组件（使用 `v-if` 或 `hidden`）
  3. 将覆盖层放在原生组件外部，调整布局避免重叠
  4. 在 App 端可以使用 `nvue` 页面，原生组件和普通组件在同一个层级

### Q4：如何实现 uniapp 小程序的秒开优化？

**回答要点：**

- **分包加载**：将非首屏页面放入分包，减少主包大小（主包建议 < 2MB）
- **预加载配置**：在 `pages.json` 中配置 `preloadRule`，在进入首页时预下载高频分包
- **组件懒加载**：使用动态 `import()` 或 `defineAsyncComponent` 实现非首屏组件按需加载
- **图片懒加载**：使用 `IntersectionObserver` 或 `loading="lazy"` 延迟加载非首屏图片
- **setData 优化**：减少 setData 频率和数据量
- **首屏数据预取**：在 `App.onLaunch` 中提前请求首屏数据

### Q5：uniapp 中如何排查跨端渲染差异问题？

**回答要点：**

- 遵循标准排查路径：**环境检查 → 条件编译排查 → 样式隔离 → 原生组件限制 → 数据绑定差异**
- 环境检查：确认目标平台、基础库版本、编译模式（Vue 2/Vue 3）、nvue 模式
- 条件编译排查：检查 `#ifdef`/`#ifndef` 是否正确匹配目标平台
- 样式隔离：检查 scoped 样式、全局样式冲突、uni.scss 变量
- 原生组件限制：确认 video/map/canvas 是否被覆盖，z-index 是否失效
- 数据绑定：小程序中对象新增属性需要使用 `$set` 或 `$forceUpdate()`

---

## 五、避坑指南

| 常见错误 | 现象 | 原因 | 解决方案 |
|---------|------|------|----------|
| 在 scroll-view 内使用 `position: fixed` | 小程序端 fixed 定位失效，元素随滚动移动 | scroll-view 创建了新的层叠上下文，fixed 相对于 scroll-view 定位 | 将 fixed 元素移到 scroll-view 外部 |
| 使用普通 view 覆盖 video 组件 | 小程序端 view 被 video 遮挡，H5 端正常 | 小程序原生组件层级最高，z-index 无效 | 使用 `cover-view` / `cover-image` 覆盖原生组件 |
| setData 传递大量数据 | 页面卡顿、滚动不流畅、操作延迟 | 每次 setData 都涉及跨线程通信和数据序列化，数据量大时开销巨大 | 只传递变化的数据，使用数据路径精确更新，不将非渲染数据放在 data 中 |
| 多次连续调用 setData | 页面渲染抖动、性能下降 | 同一帧内多次 setData 会导致多次渲染 | 合并 setData 调用，使用节流控制频率 |
| 在 data 中存放不需要渲染的数据 | setData 数据量过大，内存占用高 | 所有 data 中的数据都会参与 setData 传输 | 将非渲染数据挂在 this 上（非响应式），只有需要渲染的数据才放在 data 中 |
| 使用 `overflow: scroll` 实现滚动 | 小程序端不滚动，H5 端正常 | 小程序不支持 CSS overflow 滚动 | 使用 `<scroll-view>` 组件替代 |
| 未处理原生组件的层级问题 | 弹窗/提示被 video 遮挡 | 原生组件层级最高 | 显示弹窗时先隐藏原生组件，或使用 cover-view |
| 长列表未使用虚拟滚动 | 列表数据多时页面卡顿、白屏 | 大量 DOM 节点同时渲染，内存和渲染开销巨大 | 使用虚拟滚动，只渲染可视区域内的元素 |

---

## 本章学习自检

- [ ] 我能清晰描述 H5 浏览器渲染和小程序双线程渲染的架构差异
- [ ] 我理解小程序中 setData 的通信机制和性能瓶颈
- [ ] 我能说出 flex 布局在 H5 和小程序端的默认行为差异（display、flex-shrink）
- [ ] 我知道哪些 CSS 属性在小程序中不支持，能为不支持的情况提供降级方案
- [ ] 我掌握跨端渲染问题的标准排查路径（环境检查 → 条件编译 → 样式隔离 → 原生组件 → 数据绑定）
- [ ] 我能解决 z-index 在小程序原生组件上失效的问题（使用 cover-view）
- [ ] 我知道 scroll-view 内 fixed 定位失效的原因和解决方案
- [ ] 我掌握分包加载、预加载配置、组件懒加载、图片懒加载等首屏优化手段
- [ ] 我理解 AI SDK 等大依赖的极限拆分策略（独立分包 + 动态加载 + 降级方案）
- [ ] 我能说出至少 5 条 setData 优化技巧，并在实际项目中应用
- [ ] 我理解虚拟滚动的原理，能实现基本的长列表虚拟滚动
- [ ] 我掌握小程序内存管理的最佳实践（定时器清理、事件监听移除、请求中断）

---

> **学习导航**：
> - 返回 [学习路线总览](../README.md)
> - 本模块上一个文件：[01-uniapp跨端开发基础](./01-uniapp跨端开发基础.md)
> - 相关模块：[加载性能优化](../08-performance/01-加载性能优化.md) | [运行时优化](../08-performance/02-运行时优化.md)