# uniapp 跨端开发基础

> 模块：12-cross-platform（uniapp 跨端开发）
> 内容：uniapp 架构原理、条件编译、项目结构、生命周期、组件体系、API 体系、三端差异化实战
> 格式：八段式（核心概念 → 底层原理 → 实战应用 → 常见面试题 → 避坑指南 → 本章学习自检）
> 前置知识：[Vue 3 核心语法](../05-vue/01-Vue3核心语法.md)、[JavaScript 核心](../02-javascript-core/01-语法基础与执行机制.md)

---

## 一、核心概念

uniapp 是 DCloud 推出的基于 Vue.js 的跨端开发框架，一套代码可以同时发布到 iOS、Android、Web（H5）、以及各种小程序平台（微信、支付宝、百度、字节跳动、QQ、快手、京东等）。其核心理念是"**一套代码，多端运行**"，通过编译器 + 运行时适配层的组合来屏蔽各平台的差异。

**uniapp 的核心特点：**

1. **编译时跨端**：通过条件编译（`#ifdef`/`#ifndef`）在编译阶段生成不同平台的代码，而不是运行时判断
2. **Vue 语法兼容**：完整支持 Vue 2/Vue 3 的模板语法、指令、组件化开发模式
3. **统一 API 层**：`uni.*` 系列 API 封装了各平台的原生能力，开发者无需关心底层平台差异
4. **丰富的组件生态**：内置组件（view、scroll-view、swiper 等）+ uni-ui 扩展组件库 + 插件市场
5. **小程序优先**：以微信小程序规范为基准，向上兼容 H5 和 App 端

**跨端开发的本质挑战：**

```
各平台渲染引擎差异：

   H5 端 ──── WebView（浏览器内核）── DOM + CSSOM 渲染
   小程序 ──── 双线程架构（渲染层 + 逻辑层）── 同层渲染
   App 端 ──── Weex 原生渲染引擎 / NVUE ── 原生组件渲染
```

uniapp 通过以下机制实现"一套代码多端运行"：
- **编译时转换**：将 `.vue` 文件中的标签、API 调用转换为各平台对应的代码
- **条件编译**：允许开发者在同一文件中编写平台差异化代码，编译器按平台裁剪
- **运行时适配**：在运行时动态判断平台并提供对应的 polyfill 或降级方案

---

## 二、底层原理

### 2.1 uniapp 架构原理：编译时 vs 运行时

#### 2.1.1 编译时转换机制

uniapp 在编译阶段将 `.vue` 单文件组件转换为各平台可识别的代码。核心编译流程如下：

```text
编译流程：

  源代码（.vue 文件）
       │
       ▼
  ┌─────────────────────────────────────────────┐
  │ 1. 模板编译                                   │
  │    ├─ <view>  → H5: <div>                    │
  │    │           → 小程序: <view>               │
  │    │           → App: 原生 View 组件           │
  │    ├─ <text>  → H5: <span>                   │
  │    │           → 小程序: <text>               │
  │    ├─ <image> → H5: <img>                    │
  │    │           → 小程序: <image>              │
  │    └─ 事件绑定：@click → H5: onclick          │
  │                       → 小程序: bindtap       │
  └─────────────────────────────────────────────┘
       │
       ▼
  ┌─────────────────────────────────────────────┐
  │ 2. 条件编译处理                               │
  │    ├─ 解析 #ifdef / #ifndef 指令              │
  │    ├─ 按目标平台裁剪代码块                     │
  │    └─ 移除不属于目标平台的代码                  │
  └─────────────────────────────────────────────┘
       │
       ▼
  ┌─────────────────────────────────────────────┐
  │ 3. API 转换                                  │
  │    ├─ uni.request → H5: XMLHttpRequest/fetch │
  │    │              → 小程序: wx.request        │
  │    │              → App: 原生网络请求          │
  │    └─ uni.chooseImage → 各平台原生选图 API     │
  └─────────────────────────────────────────────┘
       │
       ▼
  ┌─────────────────────────────────────────────┐
  │ 4. 样式转换                                  │
  │    ├─ rpx 单位 → 各平台适配单位               │
  │    ├─ scoped 样式 → 各平台作用域方案           │
  │    └─ CSS 兼容性处理（前缀、降级）             │
  └─────────────────────────────────────────────┘
       │
       ▼
  各平台产物：
    ├─ H5: HTML + CSS + JS（单页应用）
    ├─ 微信小程序: wxml + wxss + js + json
    ├─ App: 原生渲染资源包
    └─ 其他小程序: 对应平台的模板文件
```

**编译时的关键转换规则：**

| 源代码 | H5 产物 | 微信小程序产物 | App 产物 |
|--------|---------|---------------|----------|
| `<view>` | `<div>` | `<view>` | 原生 View |
| `<text>` | `<span>` | `<text>` | 原生 Text |
| `<image>` | `<img>` | `<image>` | 原生 Image |
| `<scroll-view>` | `<div>` + CSS overflow | `<scroll-view>` | 原生 ScrollView |
| `@click` | `onclick` | `bindtap` | 原生点击事件 |
| `v-for` | Vue 列表渲染 | `wx:for` | 原生列表 |

#### 2.1.2 条件编译：`#ifdef` / `#ifndef`

条件编译是 uniapp 实现跨端差异化最关键的技术。它允许开发者在同一个文件中为不同平台编写不同的代码，编译器在构建时根据目标平台自动裁剪。

**条件编译支持的平台标识：**

| 标识 | 平台 | 说明 |
|------|------|------|
| `H5` | H5 网页端 | 浏览器环境 |
| `MP-WEIXIN` | 微信小程序 | 微信小程序环境 |
| `MP-ALIPAY` | 支付宝小程序 | 支付宝小程序环境 |
| `MP-BAIDU` | 百度小程序 | 百度小程序环境 |
| `MP-TOUTIAO` | 字节跳动小程序 | 抖音/头条小程序 |
| `MP-QQ` | QQ 小程序 | QQ 小程序环境 |
| `MP-KUAISHOU` | 快手小程序 | 快手小程序环境 |
| `MP-JD` | 京东小程序 | 京东小程序环境 |
| `MP-LARK` | 飞书小程序 | 飞书小程序环境 |
| `MP-XHS` | 小红书小程序 | 小红书小程序环境 |
| `MP` | 所有小程序平台 | 任意小程序平台 |
| `APP-PLUS` | App 端 | 5+App 环境 |
| `APP-PLUS-NVUE` | App nvue 页面 | weex 原生渲染 |
| `APP-VUE` | App vue 页面 | App 端 Vue 页面 |
| `APP` | 所有 App 端 | App 任意模式 |
| `VUE2` | Vue 2 版本 | 使用 Vue 2 的项目 |
| `VUE3` | Vue 3 版本 | 使用 Vue 3 的项目 |

**条件编译在三种场景中的使用：**

**（1）在 template 模板中使用：**

```vue
<template>
  <view class="container">
    <!-- 通用代码：所有平台都渲染 -->
    <view class="common-header">通用头部</view>

    <!-- #ifdef H5：仅在 H5 端渲染 -->
    <view class="h5-banner">H5 专用广告横幅</view>
    <!-- #endif -->

    <!-- #ifdef MP-WEIXIN：仅在微信小程序渲染 -->
    <view class="weixin-only">
      <official-account></official-account>
    </view>
    <!-- #endif -->

    <!-- #ifndef H5：非 H5 端渲染（即小程序 + App） -->
    <view class="native-only">原生端专属功能</view>
    <!-- #endif -->

    <!-- #ifdef MP：所有小程序平台 -->
    <view class="mini-program">小程序通用组件</view>
    <!-- #endif -->
  </view>
</template>
```

**（2）在 script 脚本中使用：**

```javascript
<script>
export default {
  data() {
    return {
      // #ifdef H5
      // H5 端使用 localStorage 存储的 token
      token: localStorage.getItem('token') || '',
      // #endif

      // #ifndef H5
      // 非 H5 端使用 uni.getStorageSync 读取
      token: uni.getStorageSync('token') || '',
      // #endif
    }
  },
  methods: {
    handleLogin() {
      // #ifdef MP-WEIXIN
      // 微信小程序使用 wx.login 获取 code
      wx.login({
        success: (res) => {
          this.getToken(res.code)
        }
      })
      // #endif

      // #ifdef H5
      // H5 端使用微信网页授权
      const redirectUri = encodeURIComponent(window.location.href)
      window.location.href = `https://open.weixin.qq.com/connect/oauth2/authorize?appid=${this.appId}&redirect_uri=${redirectUri}&response_type=code&scope=snsapi_userinfo#wechat_redirect`
      // #endif

      // #ifdef APP-PLUS
      // App 端使用 uni.login 获取第三方登录
      uni.login({
        provider: 'weixin',
        success: (res) => {
          this.getToken(res.authResult.access_token)
        }
      })
      // #endif
    },

    async getToken(code) {
      // 通用逻辑：向服务端换取 token，所有平台共享
      const res = await uni.request({
        url: '/api/login',
        method: 'POST',
        data: { code }
      })
      // #ifdef H5
      localStorage.setItem('token', res.data.token)
      // #endif
      // #ifndef H5
      uni.setStorageSync('token', res.data.token)
      // #endif
    }
  }
}
</script>
```

**（3）在 style 样式中使用：**

```vue
<style>
/* 通用样式：所有平台共享 */
.container {
  padding: 20rpx;
  background-color: #f5f5f5;
}

/* #ifdef H5 */
/* H5 端专属样式 */
.container {
  max-width: 750px;
  margin: 0 auto;
}
/* #endif */

/* #ifdef MP-WEIXIN */
/* 微信小程序专属样式 */
.container {
  /* 小程序不支持某些 CSS 属性，需要特殊处理 */
  background-color: #f0f0f0;
}
/* #endif */

/* #ifndef APP-PLUS */
/* 非 App 端样式 */
.native-only {
  display: none;
}
/* #endif */
</style>
```

**条件编译的注意事项：**

- 条件编译指令是**编译时**处理的，不会增加运行时代码体积
- 不同平台的产物中只包含对应平台的代码块
- `#ifdef` 和 `#ifndef` 必须成对出现（每个 `#ifdef` 需要对应 `#endif`）
- 条件编译可以嵌套使用，但建议不要超过 2 层嵌套
- 在 `pages.json` 和 `manifest.json` 中也可以使用条件编译

### 2.2 项目结构详解

一个标准的 uniapp 项目结构如下：

```
my-uni-app/
├── pages/                    # 页面目录
│   ├── index/
│   │   └── index.vue        # 首页
│   └── user/
│       └── user.vue         # 用户页
├── components/               # 公共组件目录
│   └── common-header/
│       └── common-header.vue
├── static/                   # 静态资源目录（不经过编译，直接复制）
│   ├── images/
│   └── fonts/
├── store/                    # Vuex/Pinia 状态管理
│   └── index.js
├── utils/                    # 工具函数
│   ├── request.js            # 网络请求封装
│   └── common.js             # 公共工具函数
├── api/                      # API 接口层
│   └── index.js
├── pages.json                # 页面路由与窗口配置（核心配置文件）
├── manifest.json             # 应用配置（App 权限、H5 路由模式等）
├── uni.scss                  # 全局样式变量（uni 内置变量 + 自定义变量）
├── App.vue                   # 应用入口组件
├── main.js                   # 应用入口 JS 文件
├── index.html                # H5 端模板文件
└── package.json
```

#### 2.2.1 pages.json —— 页面路由与窗口配置

`pages.json` 是 uniapp 最核心的配置文件，负责页面路由注册、导航栏样式、tabBar 配置、窗口表现等。

```json
{
  // pages 数组的第一项为应用入口页
  "pages": [
    {
      "path": "pages/index/index",
      "style": {
        "navigationBarTitleText": "首页",
        "navigationBarBackgroundColor": "#007AFF",
        "navigationBarTextStyle": "white",
        "enablePullDownRefresh": true
      }
    },
    {
      "path": "pages/user/user",
      "style": {
        "navigationBarTitleText": "个人中心"
      }
    }
  ],
  // 全局窗口样式
  "globalStyle": {
    "navigationBarTextStyle": "black",
    "navigationBarTitleText": "我的应用",
    "navigationBarBackgroundColor": "#F8F8F8",
    "backgroundColor": "#F8F8F8"
  },
  // 底部 TabBar 配置
  "tabBar": {
    "color": "#7A7E83",
    "selectedColor": "#007AFF",
    "borderStyle": "black",
    "backgroundColor": "#ffffff",
    "list": [
      {
        "pagePath": "pages/index/index",
        "iconPath": "static/tab/home.png",
        "selectedIconPath": "static/tab/home-active.png",
        "text": "首页"
      },
      {
        "pagePath": "pages/user/user",
        "iconPath": "static/tab/user.png",
        "selectedIconPath": "static/tab/user-active.png",
        "text": "我的"
      }
    ]
  },
  // 分包配置（用于性能优化，将非首屏页面放入分包）
  "subPackages": [
    {
      "root": "subpkg-order",
      "pages": [
        {
          "path": "order-list/order-list",
          "style": {
            "navigationBarTitleText": "订单列表"
          }
        },
        {
          "path": "order-detail/order-detail",
          "style": {
            "navigationBarTitleText": "订单详情"
          }
        }
      ]
    }
  ],
  // 预加载配置（进入某个页面时预下载其他分包）
  "preloadRule": {
    "pages/index/index": {
      "network": "all",
      "packages": ["subpkg-order"]
    }
  },
  // 条件编译：不同平台的专属配置
  "condition": {
    // #ifdef MP-WEIXIN
    "children": [
      {
        "name": "微信小程序专属页面",
        "path": "pages/weixin-only/weixin-only"
      }
    ]
    // #endif
  }
}
```

#### 2.2.2 manifest.json —— 应用配置

`manifest.json` 是应用级别的配置文件，用于配置 App 权限、H5 路由模式、小程序 appid 等。

```json
{
  "name": "我的应用",
  "appid": "__UNI__XXXXXX",
  "description": "",
  "versionName": "1.0.0",
  "versionCode": "100",

  // H5 端专属配置
  "h5": {
    "router": {
      "mode": "history",        // 路由模式：hash / history
      "base": "/h5/"
    },
    "title": "我的应用",
    "publicPath": "/h5/",
    "async": {
      "loading": "AsyncLoading", // 异步组件加载中占位组件
      "error": "AsyncError",     // 异步组件加载失败占位组件
      "delay": 200,
      "timeout": 3000
    }
  },

  // 微信小程序专属配置
  "mp-weixin": {
    "appid": "wx1234567890abcdef",
    "setting": {
      "urlCheck": false,
      "es6": true,
      "postcss": true,
      "minified": true
    },
    "usingComponents": true,
    "permission": {
      "scope.userLocation": {
        "desc": "获取您的位置信息用于展示附近商家"
      }
    }
  },

  // App 端专属配置
  "app-plus": {
    "splashscreen": {
      "alwaysShowBeforeRender": true,
      "autoclose": true,
      "waiting": true
    },
    "modules": {
      "Payment": {},
      "Maps": {},
      "OAuth": {}
    },
    "distribute": {
      "android": {
        "permissions": [
          "<uses-permission android:name=\"android.permission.ACCESS_FINE_LOCATION\"/>"
        ]
      }
    }
  }
}
```

> **H5 history 路由模式补充说明**：当使用 `history` 模式时，uniapp 内部通过 `history.pushState` / `history.replaceState` 实现页面跳转。可以监听 `popstate` 事件来处理浏览器的前进/后退操作：

```javascript
// H5 history 路由模式下的 popstate 事件监听
// 当用户点击浏览器的前进/后退按钮时触发

// 方案一：全局监听 popstate（可在 App.vue onLaunch 中注册）
window.addEventListener('popstate', (event) => {
  console.log('浏览器前进/后退触发', {
    pathname: window.location.pathname,
    search: window.location.search,
    hash: window.location.hash,
    state: event.state, // pushState 时传入的 state 对象
  });

  // 根据当前路径做对应处理
  // 例如：更新页面标题、重新加载数据等
  document.title = getPageTitle(window.location.pathname);
});

// 方案二：拦截 pushState/replaceState 以便追踪所有路由变化
// 实现对 history API 的包装，在路由变化时触发自定义事件
const originalPushState = history.pushState;
const originalReplaceState = history.replaceState;

history.pushState = function (...args) {
  const result = originalPushState.apply(this, args);
  // 触发自定义事件供页面监听
  window.dispatchEvent(new CustomEvent('routechange', {
    detail: { type: 'pushState', url: args[2] }
  }));
  return result;
};

history.replaceState = function (...args) {
  const result = originalReplaceState.apply(this, args);
  window.dispatchEvent(new CustomEvent('routechange', {
    detail: { type: 'replaceState', url: args[2] }
  }));
  return result;
};

// 使用示例
window.addEventListener('routechange', (event) => {
  const { type, url } = event.detail;
  console.log(`路由变化 [${type}]: ${url}`);
  // 根据 url 执行相应的页面切换逻辑
});

// 注意：uniapp 框架内部已封装了路由管理，上述代码主要用于理解
// H5 history 路由模式的底层原理。实际开发中可直接使用 uniapp 提供的
// uni.onPageNotFound、uni.onAppRoute 等生命周期钩子。
```

#### 2.2.3 uni.scss —— 全局样式变量

`uni.scss` 是 uniapp 内置的全局 SCSS 变量文件，定义了跨端一致的样式变量体系，无需手动引入即可在所有页面中使用。

```scss
/* uni.scss - 全局 SCSS 变量 */

/* ========== uni 内置变量（来自 uni-ui 官方组件库） ========== */

/* 主题色 */
$uni-color-primary: #007aff;
$uni-color-success: #4cd964;
$uni-color-warning: #f0ad4e;
$uni-color-error: #dd524d;

/* 文字颜色 */
$uni-text-color: #333333;           // 基本文字色
$uni-text-color-inverse: #ffffff;   // 反色文字
$uni-text-color-grey: #999999;      // 辅助灰色
$uni-text-color-placeholder: #808080;
$uni-text-color-disable: #c0c0c0;

/* 背景色 */
$uni-bg-color: #ffffff;
$uni-bg-color-grey: #f8f8f8;
$uni-bg-color-hover: #f1f1f1;       // 点击状态背景色
$uni-bg-color-mask: rgba(0, 0, 0, 0.4); // 遮罩背景

/* 边框颜色 */
$uni-border-color: #e5e5e5;

/* 尺寸变量 */
$uni-font-size-sm: 12px;
$uni-font-size-base: 14px;
$uni-font-size-lg: 16px;

$uni-spacing-sm: 5px;
$uni-spacing-base: 10px;
$uni-spacing-lg: 15px;
$uni-spacing-row-sm: 5px;
$uni-spacing-row-base: 10px;
$uni-spacing-row-lg: 15px;

$uni-img-size-sm: 20px;
$uni-img-size-base: 26px;
$uni-img-size-lg: 40px;

/* ========== 自定义全局变量 ========== */

/* 品牌色扩展 */
$app-primary: #ff6b35;
$app-primary-light: #ff8c5a;
$app-primary-dark: #e55a2b;

/* 页面安全区域（适配 iPhone 刘海屏） */
$safe-area-inset-bottom: env(safe-area-inset-bottom);

/* 通用间距 */
$page-padding: 30rpx;
$card-radius: 12rpx;
```

### 2.3 生命周期体系

uniapp 的生命周期分为三个层级：**应用生命周期**、**页面生命周期**、**组件生命周期**。理解它们的执行顺序是避免常见开发问题的关键。

#### 2.3.1 应用生命周期（App.vue）

应用生命周期是全局的，仅在 `App.vue` 中定义，整个应用只会触发一次。

```javascript
// App.vue
<script>
export default {
  onLaunch(options) {
    // 应用初始化完成时触发（全局只触发一次）
    // 场景：检查登录状态、获取系统信息、初始化全局数据
    console.log('App Launch', options)

    // 获取系统信息
    const systemInfo = uni.getSystemInfoSync()
    console.log('设备信息：', systemInfo)

    // 检查登录状态
    const token = uni.getStorageSync('token')
    if (token) {
      // 验证 token 有效性
      this.checkToken(token)
    }
  },

  onShow(options) {
    // 应用从后台进入前台时触发
    // 场景：重新获取数据、刷新 token
    console.log('App Show', options)

    // 小程序场景：从其他小程序返回时 options.referrerInfo 可获取来源信息
    // #ifdef MP-WEIXIN
    if (options.referrerInfo && options.referrerInfo.extraData) {
      console.log('来自其他小程序的额外数据：', options.referrerInfo.extraData)
    }
    // #endif
  },

  onHide() {
    // 应用从前台进入后台时触发
    // 场景：保存临时数据、暂停音视频播放
    console.log('App Hide')
  },

  onError(error) {
    // 应用发生脚本错误或 API 调用报错时触发
    // 场景：全局错误上报
    console.error('应用错误：', error)
    // 上报到错误监控平台
    uni.request({
      url: '/api/error-report',
      method: 'POST',
      data: { error: error.message, stack: error.stack }
    })
  },

  onPageNotFound(res) {
    // 应用要打开的页面不存在时触发
    // 场景：重定向到首页或 404 页面
    console.warn('页面不存在：', res.path)
    uni.redirectTo({ url: '/pages/index/index' })
  },

  methods: {
    async checkToken(token) {
      // 验证 token 逻辑
    }
  }
}
</script>
```

#### 2.3.2 页面生命周期

页面生命周期在每个页面中定义，页面切换时会触发对应的生命周期钩子。

```javascript
// pages/index/index.vue
<script>
export default {
  data() {
    return {
      list: [],
      page: 1
    }
  },

  // ========== 页面生命周期（按执行顺序排列） ==========

  onLoad(options) {
    // 页面加载时触发，只触发一次
    // 可以获取页面跳转时传递的参数
    // 场景：发起初始数据请求
    console.log('页面参数：', options)
    this.page = options.page || 1
    this.fetchData()
  },

  onShow() {
    // 页面显示 / 切入前台时触发
    // 场景：刷新数据（从其他页面返回时需要更新）
    console.log('页面显示')
    this.fetchData()
  },

  onReady() {
    // 页面初次渲染完成时触发，只触发一次
    // 场景：获取节点信息、与视图层进行交互
    // 注意：此时页面 DOM 已渲染完成，可以安全操作节点
    // #ifdef MP-WEIXIN
    const query = uni.createSelectorQuery().in(this)
    query.select('.header').boundingClientRect((data) => {
      console.log('头部高度：', data.height)
    }).exec()
    // #endif
  },

  onHide() {
    // 页面隐藏 / 切入后台时触发
    // 场景：暂停音视频、停止定时器
    console.log('页面隐藏')
  },

  onUnload() {
    // 页面卸载时触发
    // 场景：清理定时器、取消网络请求、移除事件监听
    console.log('页面卸载')
    this.clearTimer()
  },

  // ========== 页面事件处理 ==========

  onPullDownRefresh() {
    // 下拉刷新时触发
    // 场景：刷新列表数据
    this.page = 1
    this.fetchData().then(() => {
      uni.stopPullDownRefresh() // 停止下拉刷新动画
    })
  },

  onReachBottom() {
    // 页面滚动到底部时触发
    // 场景：加载更多数据（分页）
    this.page++
    this.fetchData(true) // append 模式
  },

  onShareAppMessage() {
    // 用户点击分享按钮时触发
    // 场景：自定义分享内容
    return {
      title: '分享标题',
      path: '/pages/index/index?id=123',
      imageUrl: '/static/share-image.png'
    }
  },

  // ========== 方法 ==========

  methods: {
    async fetchData(append = false) {
      const res = await uni.request({
        url: '/api/list',
        data: { page: this.page }
      })
      if (append) {
        this.list = [...this.list, ...res.data]
      } else {
        this.list = res.data
      }
    },

    clearTimer() {
      // 清理定时器
      if (this.timer) {
        clearInterval(this.timer)
        this.timer = null
      }
    }
  }
}
</script>
```

#### 2.3.3 完整生命周期执行顺序

```
应用启动流程：

  1. App.vue - onLaunch()          ← 应用初始化
  2. App.vue - onShow()            ← 应用显示
  3. 页面 - onLoad()               ← 页面加载
  4. 页面 - onShow()               ← 页面显示
  5. 页面 - onReady()              ← 页面初次渲染完成

页面切换流程（A 页面 → B 页面）：

  1. A 页面 - onHide()             ← 当前页面隐藏
  2. B 页面 - onLoad()             ← 新页面加载
  3. B 页面 - onShow()             ← 新页面显示
  4. B 页面 - onReady()            ← 新页面渲染完成
  5. A 页面 - onUnload()           ← 旧页面卸载（非 tabBar 页面）

应用进入后台：

  1. App.vue - onHide()            ← 应用隐藏
  2. 当前页面 - onHide()            ← 页面隐藏

应用回到前台：

  1. App.vue - onShow()            ← 应用显示
  2. 当前页面 - onShow()            ← 页面显示
```

### 2.4 组件体系

#### 2.4.1 内置基础组件

uniapp 提供了一套跨端兼容的内置组件，这些组件在编译时会被转换为各平台对应的原生组件。

**最常用的内置组件：**

| 组件 | 说明 | 对应 H5 标签 | 小程序对应 |
|------|------|-------------|-----------|
| `<view>` | 视图容器，类似 div | `<div>` | `<view>` |
| `<text>` | 文本组件，用于包裹文字 | `<span>` | `<text>` |
| `<image>` | 图片组件 | `<img>` | `<image>` |
| `<scroll-view>` | 可滚动视图区域 | `<div>` + overflow | `<scroll-view>` |
| `<swiper>` | 滑块视图容器（轮播图） | 自定义 div | `<swiper>` |
| `<icon>` | 图标组件 | `<i>` 或自定义 | `<icon>` |
| `<rich-text>` | 富文本组件 | `innerHTML` | `<rich-text>` |
| `<progress>` | 进度条组件 | `<progress>` | `<progress>` |

**view 组件示例：**

```vue
<template>
  <!-- view 是最基础的容器组件，类似于 HTML 的 div -->
  <view class="container">
    <!-- hover-class：按下去的样式类 -->
    <view class="card" hover-class="card-hover" hover-start-time="20" hover-stay-time="70">
      <text class="card-title">卡片标题</text>
      <text class="card-desc">卡片描述内容</text>
    </view>
  </view>
</template>

<style>
.card {
  padding: 30rpx;
  margin: 20rpx;
  background-color: #fff;
  border-radius: 12rpx;
  box-shadow: 0 2rpx 12rpx rgba(0, 0, 0, 0.08);
}
.card-hover {
  background-color: #f5f5f5;
  opacity: 0.9;
}
</style>
```

**scroll-view 组件示例：**

```vue
<template>
  <view>
    <!-- 纵向滚动 -->
    <scroll-view
      scroll-y
      class="scroll-container"
      @scrolltolower="onLoadMore"
      :lower-threshold="50"
    >
      <view v-for="item in list" :key="item.id" class="scroll-item">
        {{ item.name }}
      </view>
      <view class="loading-tip" v-if="loading">加载中...</view>
      <view class="loading-tip" v-if="noMore">没有更多了</view>
    </scroll-view>

    <!-- 横向滚动 -->
    <scroll-view scroll-x class="horizontal-scroll" enable-flex>
      <view v-for="item in tabs" :key="item.id" class="tab-item">
        {{ item.label }}
      </view>
    </scroll-view>
  </view>
</template>

<script>
export default {
  data() {
    return {
      list: [],
      tabs: [
        { id: 1, label: '推荐' },
        { id: 2, label: '热门' },
        { id: 3, label: '最新' },
        { id: 4, label: '关注' }
      ],
      loading: false,
      noMore: false,
      page: 1
    }
  },
  methods: {
    onLoadMore() {
      if (this.loading || this.noMore) return
      this.loading = true
      this.page++
      // 加载更多数据...
    }
  }
}
</script>

<style>
.scroll-container {
  height: 100vh;
}
.horizontal-scroll {
  white-space: nowrap;
  width: 100%;
}
.tab-item {
  display: inline-block;
  width: 160rpx;
  height: 80rpx;
  line-height: 80rpx;
  text-align: center;
}
</style>
```

**swiper 组件示例（轮播图）：**

```vue
<template>
  <swiper
    class="banner-swiper"
    :indicator-dots="true"
    :autoplay="true"
    :interval="3000"
    :duration="500"
    :circular="true"
    indicator-color="rgba(255,255,255,0.5)"
    indicator-active-color="#ffffff"
  >
    <swiper-item v-for="(item, index) in banners" :key="index">
      <image :src="item.image" class="banner-image" mode="aspectFill" @click="onBannerClick(item)" />
    </swiper-item>
  </swiper>
</template>

<script>
export default {
  data() {
    return {
      banners: [
        { image: '/static/banner1.jpg', link: '/pages/detail/detail?id=1' },
        { image: '/static/banner2.jpg', link: '/pages/detail/detail?id=2' },
        { image: '/static/banner3.jpg', link: '/pages/detail/detail?id=3' }
      ]
    }
  },
  methods: {
    onBannerClick(item) {
      uni.navigateTo({ url: item.link })
    }
  }
}
</script>

<style>
.banner-swiper {
  width: 100%;
  height: 300rpx;
}
.banner-image {
  width: 100%;
  height: 100%;
}
</style>
```

#### 2.4.2 uni-ui 扩展组件库

uni-ui 是 DCloud 官方提供的跨端组件库，基于 uni-app 内置组件封装，提供更丰富的 UI 组件。

**常用 uni-ui 组件：**

| 组件 | 用途 |
|------|------|
| `uni-nav-bar` | 自定义导航栏 |
| `uni-icons` | 图标组件 |
| `uni-list` / `uni-list-item` | 列表组件 |
| `uni-card` | 卡片组件 |
| `uni-forms` / `uni-forms-item` | 表单组件 |
| `uni-popup` | 弹出层组件 |
| `uni-load-more` | 加载更多组件 |
| `uni-segmented-control` | 分段器 |
| `uni-collapse` | 折叠面板 |
| `uni-drawer` | 抽屉 |

**uni-ui 使用示例：**

```vue
<template>
  <view>
    <!-- 导航栏 -->
    <uni-nav-bar
      title="商品列表"
      left-icon="back"
      right-text="搜索"
      @clickLeft="goBack"
      @clickRight="goSearch"
    />

    <!-- 列表项 -->
    <uni-list>
      <uni-list-item
        v-for="product in products"
        :key="product.id"
        :title="product.name"
        :note="product.desc"
        :thumb="product.thumb"
        thumb-size="lg"
        show-arrow
        @click="onProductClick(product)"
      />
    </uni-list>

    <!-- 加载更多 -->
    <uni-load-more
      :status="loadStatus"
      @clickLoadMore="loadMore"
    />
  </view>
</template>

<script>
export default {
  data() {
    return {
      products: [],
      loadStatus: 'more' // more / loading / noMore
    }
  }
}
</script>
```

### 2.5 API 体系

uniapp 提供了 `uni.*` 系列 API，封装了各平台的原生能力，开发者无需关心底层平台差异。

#### 2.5.1 网络请求：uni.request

```javascript
// 封装统一的网络请求模块（utils/request.js）

// 基础配置
const BASE_URL = 'https://api.example.com'

// 请求拦截器
const requestInterceptor = (options) => {
  // 添加 token
  const token = uni.getStorageSync('token')
  if (token) {
    options.header = {
      ...options.header,
      'Authorization': `Bearer ${token}`
    }
  }
  return options
}

// 响应拦截器
const responseInterceptor = (response) => {
  const { statusCode, data } = response

  // HTTP 状态码处理
  if (statusCode === 200) {
    // 业务状态码处理
    if (data.code === 0) {
      return data.data
    } else if (data.code === 401) {
      // token 过期，跳转登录页
      uni.removeStorageSync('token')
      uni.reLaunch({ url: '/pages/login/login' })
      return Promise.reject(new Error('登录已过期'))
    } else {
      uni.showToast({ title: data.message || '请求失败', icon: 'none' })
      return Promise.reject(new Error(data.message))
    }
  } else if (statusCode === 404) {
    uni.showToast({ title: '请求的资源不存在', icon: 'none' })
    return Promise.reject(new Error('Not Found'))
  } else {
    uni.showToast({ title: '网络异常，请稍后重试', icon: 'none' })
    return Promise.reject(new Error(`HTTP ${statusCode}`))
  }
}

// 封装后的请求方法
const request = (options) => {
  return new Promise((resolve, reject) => {
    // 请求前处理
    const config = requestInterceptor({
      url: BASE_URL + options.url,
      method: options.method || 'GET',
      data: options.data || {},
      header: {
        'Content-Type': 'application/json',
        ...options.header
      },
      timeout: options.timeout || 15000
    })

    uni.request({
      ...config,
      success: (res) => {
        try {
          const result = responseInterceptor(res)
          resolve(result)
        } catch (err) {
          reject(err)
        }
      },
      fail: (err) => {
        uni.showToast({ title: '网络连接失败', icon: 'none' })
        reject(err)
      }
    })
  })
}

// 导出便捷方法
export const get = (url, data, options = {}) => {
  return request({ ...options, url, method: 'GET', data })
}

export const post = (url, data, options = {}) => {
  return request({ ...options, url, method: 'POST', data })
}

export default { get, post }
```

#### 2.5.2 位置服务：uni.getLocation

```javascript
// 获取用户位置
export function getUserLocation() {
  return new Promise((resolve, reject) => {
    // 首先检查定位权限
    // #ifdef MP-WEIXIN
    wx.getSetting({
      success: (res) => {
        if (!res.authSetting['scope.userLocation']) {
          // 未授权，引导用户授权
          wx.authorize({
            scope: 'scope.userLocation',
            success: () => {
              doGetLocation()
            },
            fail: () => {
              // 用户拒绝授权，引导去设置页
              uni.showModal({
                title: '位置授权',
                content: '需要获取您的位置信息来展示附近商家，请在设置中开启位置权限',
                success: (modalRes) => {
                  if (modalRes.confirm) {
                    wx.openSetting()
                  }
                }
              })
              reject(new Error('用户拒绝位置授权'))
            }
          })
        } else {
          doGetLocation()
        }
      }
    })
    // #endif

    // #ifndef MP-WEIXIN
    doGetLocation()
    // #endif

    function doGetLocation() {
      uni.getLocation({
        type: 'gcj02',        // 返回国测局坐标（用于国内地图服务）
        // #ifdef APP-PLUS
        geocode: true,        // App 端支持地址解析
        // #endif
        success: (res) => {
          const location = {
            latitude: res.latitude,
            longitude: res.longitude,
            speed: res.speed,
            accuracy: res.accuracy
          }
          // 可选：逆地理编码获取地址信息
          reverseGeocode(location)
          resolve(location)
        },
        fail: (err) => {
          console.error('获取位置失败：', err)
          // 降级方案：使用 IP 定位
          getIPLocation().then(resolve).catch(reject)
        }
      })
    }
  })
}

// 逆地理编码（坐标转地址）
function reverseGeocode(location) {
  // #ifdef MP-WEIXIN
  // 微信小程序使用腾讯地图服务
  // 需要在 mp-weixin 的 setting 中配置 qqmapkey
  // #endif
  console.log('位置信息：', location)
}

// 获取附近商家（示例）
async function getNearbyShops() {
  try {
    const location = await getUserLocation()
    const shops = await get('/api/shops/nearby', {
      lat: location.latitude,
      lng: location.longitude,
      radius: 5000 // 5 公里范围
    })
    return shops
  } catch (err) {
    console.error('获取附近商家失败：', err)
    return []
  }
}
```

#### 2.5.3 图片选择与上传：uni.chooseImage

```javascript
// 选择图片并上传
export function chooseAndUploadImage(options = {}) {
  return new Promise((resolve, reject) => {
    uni.chooseImage({
      count: options.count || 1,          // 最多可选图片数量
      sizeType: options.sizeType || ['compressed'], // 压缩图 / 原图
      sourceType: options.sourceType || ['album', 'camera'], // 相册 / 相机
      success: (res) => {
        // 选择成功，开始上传
        const tempFilePaths = res.tempFilePaths
        const uploadPromises = tempFilePaths.map((filePath) => {
          return uploadFile(filePath)
        })

        Promise.all(uploadPromises)
          .then((urls) => {
            resolve(urls)
          })
          .catch((err) => {
            uni.showToast({ title: '上传失败', icon: 'none' })
            reject(err)
          })
      },
      fail: (err) => {
        console.error('选择图片失败：', err)
        reject(err)
      }
    })
  })
}

// 上传单张图片
function uploadFile(filePath) {
  return new Promise((resolve, reject) => {
    uni.uploadFile({
      url: 'https://api.example.com/upload',
      filePath: filePath,
      name: 'file',
      header: {
        'Authorization': `Bearer ${uni.getStorageSync('token')}`
      },
      success: (res) => {
        const data = JSON.parse(res.data)
        if (data.code === 0) {
          resolve(data.data.url) // 返回服务器图片地址
        } else {
          reject(new Error(data.message))
        }
      },
      fail: (err) => {
        reject(err)
      }
    })
  })
}
```

**uni 常用 API 速查表：**

| API | 用途 | 平台差异注意 |
|-----|------|------------|
| `uni.request` | 发起网络请求 | 小程序需要配置合法域名 |
| `uni.uploadFile` | 上传文件 | 小程序只支持单文件上传 |
| `uni.downloadFile` | 下载文件 | 小程序下载后需调用 `saveFile` 保存 |
| `uni.getLocation` | 获取位置 | 需要用户授权，H5 需要 HTTPS |
| `uni.chooseImage` | 选择图片 | 小程序 count 最大为 9 |
| `uni.previewImage` | 预览图片 | H5 端使用自定义实现 |
| `uni.getSystemInfo` | 获取系统信息 | 不同平台返回字段略有差异 |
| `uni.setStorageSync` | 同步存储 | 小程序单个 key 最大 1MB |
| `uni.showToast` | 显示提示框 | 图标样式因平台而异 |
| `uni.showModal` | 显示模态弹窗 | 确认/取消按钮文案可能不同 |
| `uni.navigateTo` | 页面跳转 | 小程序页面栈最多 10 层 |
| `uni.switchTab` | 跳转 tabBar 页面 | 不能带参数 |
| `uni.makePhoneCall` | 拨打电话 | H5 端仅在移动端可用 |
| `uni.scanCode` | 扫码 | H5 端不支持 |

> 📖 **参考链接**：
> - [uni-app 官方文档](https://uniapp.dcloud.net.cn/)
> - [uni-app 条件编译](https://uniapp.dcloud.net.cn/tutorial/platform.html)
> - [uni-app 跨端适配](https://uniapp.dcloud.net.cn/tutorial/platform.html)

---

## 三、实战应用

### 3.1 条件编译实战：H5 / 小程序 / App 三端差异化代码

以下是一个完整的登录模块示例，展示如何在同一个文件中处理三端的登录逻辑差异。

```vue
<template>
  <view class="login-container">
    <view class="login-form">
      <!-- #ifdef MP-WEIXIN -->
      <!-- 微信小程序：使用 button 的 open-type 获取用户信息 -->
      <button
        class="weixin-login-btn"
        open-type="getUserInfo"
        @getuserinfo="onWeixinLogin"
      >
        <image src="/static/weixin-icon.png" class="icon" />
        <text>微信一键登录</text>
      </button>
      <!-- #endif -->

      <!-- #ifdef APP-PLUS -->
      <!-- App 端：使用 uni.login 获取第三方登录 -->
      <button class="app-login-btn" @click="onAppLogin">
        <image src="/static/weixin-icon.png" class="icon" />
        <text>微信登录</text>
      </button>
      <button class="app-login-btn" @click="onAppleLogin">
        <image src="/static/apple-icon.png" class="icon" />
        <text>Apple 登录</text>
      </button>
      <!-- #endif -->

      <!-- #ifdef H5 -->
      <!-- H5 端：使用微信网页授权（OAuth2.0） -->
      <view class="h5-login-btn" @click="onH5WeixinLogin">
        <image src="/static/weixin-icon.png" class="icon" />
        <text>微信登录</text>
      </view>
      <!-- #endif -->

      <!-- 通用：手机号 + 验证码登录（所有平台相同） -->
      <view class="phone-login">
        <view class="input-group">
          <input
            v-model="phone"
            type="number"
            placeholder="请输入手机号"
            maxlength="11"
          />
        </view>
        <view class="input-group code-group">
          <input
            v-model="code"
            type="number"
            placeholder="请输入验证码"
            maxlength="6"
          />
          <button
            class="send-code-btn"
            :disabled="countdown > 0"
            @click="sendCode"
          >
            {{ countdown > 0 ? countdown + 's' : '获取验证码' }}
          </button>
        </view>
        <button class="submit-btn" @click="onPhoneLogin">登录</button>
      </view>
    </view>

    <!-- 协议勾选 -->
    <view class="agreement">
      <checkbox :checked="agreed" @click="agreed = !agreed" />
      <text>已阅读并同意</text>
      <text class="link" @click="openAgreement('user')">《用户协议》</text>
      <text>和</text>
      <text class="link" @click="openAgreement('privacy')">《隐私政策》</text>
    </view>
  </view>
</template>

<script>
export default {
  data() {
    return {
      phone: '',
      code: '',
      countdown: 0,
      agreed: false,
      // #ifdef H5
      appId: 'wx_your_h5_app_id',
      // #endif
      // #ifdef MP-WEIXIN
      appId: 'wx_your_mp_app_id',
      // #endif
      // #ifdef APP-PLUS
      appId: 'wx_your_app_id',
      // #endif
    }
  },

  methods: {
    // ========== 微信小程序登录 ==========
    // #ifdef MP-WEIXIN
    onWeixinLogin(e) {
      if (!this.agreed) {
        uni.showToast({ title: '请先同意用户协议', icon: 'none' })
        return
      }

      // 获取用户信息（头像、昵称等）
      const { encryptedData, iv, rawData, signature } = e.detail

      // 获取登录凭证 code
      wx.login({
        success: (res) => {
          if (res.code) {
            this.doLogin({
              code: res.code,
              encryptedData,
              iv,
              rawData,
              signature,
              platform: 'mp-weixin'
            })
          }
        }
      })
    },
    // #endif

    // ========== App 端第三方登录 ==========
    // #ifdef APP-PLUS
    onAppLogin() {
      if (!this.agreed) {
        uni.showToast({ title: '请先同意用户协议', icon: 'none' })
        return
      }

      uni.login({
        provider: 'weixin',
        success: (res) => {
          this.doLogin({
            authResult: res.authResult,
            platform: 'app-weixin'
          })
        },
        fail: (err) => {
          console.error('微信登录失败：', err)
          uni.showToast({ title: '微信登录失败', icon: 'none' })
        }
      })
    },

    onAppleLogin() {
      if (!this.agreed) {
        uni.showToast({ title: '请先同意用户协议', icon: 'none' })
        return
      }

      uni.login({
        provider: 'apple',
        success: (res) => {
          this.doLogin({
            authResult: res.authResult,
            platform: 'app-apple'
          })
        },
        fail: (err) => {
          console.error('Apple 登录失败：', err)
        }
      })
    },
    // #endif

    // ========== H5 端微信网页授权 ==========
    // #ifdef H5
    onH5WeixinLogin() {
      if (!this.agreed) {
        uni.showToast({ title: '请先同意用户协议', icon: 'none' })
        return
      }

      // 微信网页授权 OAuth 2.0
      const redirectUri = encodeURIComponent(window.location.origin + '/pages/auth/auth')
      const state = this.generateState() // 防止 CSRF 攻击
      uni.setStorageSync('loginState', state)

      window.location.href =
        `https://open.weixin.qq.com/connect/oauth2/authorize` +
        `?appid=${this.appId}` +
        `&redirect_uri=${redirectUri}` +
        `&response_type=code` +
        `&scope=snsapi_userinfo` +
        `&state=${state}#wechat_redirect`
    },

    generateState() {
      return Math.random().toString(36).substring(2, 15)
    },
    // #endif

    // ========== 手机号验证码登录（通用） ==========
    sendCode() {
      if (!this.phone) {
        uni.showToast({ title: '请输入手机号', icon: 'none' })
        return
      }

      if (!/^1[3-9]\d{9}$/.test(this.phone)) {
        uni.showToast({ title: '请输入正确的手机号', icon: 'none' })
        return
      }

      // 发送验证码
      uni.request({
        url: '/api/send-code',
        method: 'POST',
        data: { phone: this.phone }
      })

      // 倒计时
      this.countdown = 60
      const timer = setInterval(() => {
        this.countdown--
        if (this.countdown <= 0) {
          clearInterval(timer)
        }
      }, 1000)
    },

    onPhoneLogin() {
      if (!this.agreed) {
        uni.showToast({ title: '请先同意用户协议', icon: 'none' })
        return
      }

      if (!this.phone || !this.code) {
        uni.showToast({ title: '请填写手机号和验证码', icon: 'none' })
        return
      }

      this.doLogin({
        phone: this.phone,
        code: this.code,
        platform: 'phone'
      })
    },

    // ========== 通用登录逻辑 ==========
    async doLogin(params) {
      uni.showLoading({ title: '登录中...', mask: true })

      try {
        const res = await uni.request({
          url: '/api/login',
          method: 'POST',
          data: params
        })

        // 保存 token
        uni.setStorageSync('token', res.data.token)
        uni.setStorageSync('userInfo', res.data.userInfo)

        uni.hideLoading()

        // 跳转到首页
        uni.reLaunch({ url: '/pages/index/index' })
      } catch (err) {
        uni.hideLoading()
        uni.showToast({ title: '登录失败，请重试', icon: 'none' })
      }
    },

    openAgreement(type) {
      const url = type === 'user'
        ? '/pages/agreement/user-agreement'
        : '/pages/agreement/privacy-policy'
      uni.navigateTo({ url })
    }
  }
}
</script>

<style lang="scss">
.login-container {
  min-height: 100vh;
  padding: 60rpx 40rpx;
  background-color: #f5f5f5;
}

.login-form {
  background-color: #fff;
  border-radius: 16rpx;
  padding: 60rpx 40rpx;
}

/* 微信登录按钮 */
.weixin-login-btn,
.app-login-btn,
.h5-login-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 100%;
  height: 88rpx;
  background-color: #07c160;
  color: #fff;
  border-radius: 44rpx;
  font-size: 32rpx;
  margin-bottom: 30rpx;

  .icon {
    width: 40rpx;
    height: 40rpx;
    margin-right: 16rpx;
  }
}

/* Apple 登录按钮 */
.app-login-btn:nth-child(2) {
  background-color: #000;
}

/* 手机号登录 */
.phone-login {
  margin-top: 40rpx;
}

.input-group {
  margin-bottom: 24rpx;

  input {
    width: 100%;
    height: 88rpx;
    border: 2rpx solid #e5e5e5;
    border-radius: 12rpx;
    padding: 0 24rpx;
    font-size: 28rpx;
  }
}

.code-group {
  display: flex;
  align-items: center;

  input {
    flex: 1;
  }

  .send-code-btn {
    width: 180rpx;
    height: 88rpx;
    line-height: 88rpx;
    text-align: center;
    background-color: #007aff;
    color: #fff;
    border-radius: 12rpx;
    font-size: 24rpx;
    margin-left: 20rpx;
  }
}

.submit-btn {
  width: 100%;
  height: 88rpx;
  background-color: #007aff;
  color: #fff;
  border-radius: 44rpx;
  font-size: 32rpx;
  margin-top: 40rpx;
}

.agreement {
  display: flex;
  align-items: center;
  justify-content: center;
  margin-top: 40rpx;
  font-size: 24rpx;
  color: #999;

  .link {
    color: #007aff;
  }
}
</style>
```

### 3.2 跨端适配的通用工具函数

```javascript
// utils/platform.js - 跨端适配工具函数

/**
 * 获取当前平台信息
 */
export function getPlatform() {
  const systemInfo = uni.getSystemInfoSync()
  return {
    platform: systemInfo.platform,     // ios / android / devtools / windows / mac
    isH5: systemInfo.uniPlatform === 'web',
    isWeixin: systemInfo.uniPlatform === 'mp-weixin',
    isApp: systemInfo.uniPlatform === 'app',
    isIOS: systemInfo.platform === 'ios',
    isAndroid: systemInfo.platform === 'android',
    isDevtools: systemInfo.platform === 'devtools',
    model: systemInfo.model,
    system: systemInfo.system,
    screenWidth: systemInfo.screenWidth,
    screenHeight: systemInfo.screenHeight,
    windowWidth: systemInfo.windowWidth,
    windowHeight: systemInfo.windowHeight,
    statusBarHeight: systemInfo.statusBarHeight,
    safeAreaInsets: systemInfo.safeAreaInsets,
    // 导航栏高度（状态栏 + 导航栏）
    navBarHeight: systemInfo.statusBarHeight + 44,
    // 底部安全距离（iPhone X 以上机型）
    safeAreaBottom: systemInfo.safeAreaInsets
      ? systemInfo.safeAreaInsets.bottom
      : 0
  }
}

/**
 * 判断是否为移动端
 */
export function isMobile() {
  // #ifdef H5
  return /Android|iPhone|iPad|iPod/i.test(navigator.userAgent)
  // #endif
  // #ifndef H5
  return true
  // #endif
}

/**
 * 获取导航栏样式（适配不同平台）
 */
export function getNavBarStyle() {
  const { statusBarHeight } = uni.getSystemInfoSync()
  return {
    // #ifdef MP-WEIXIN
    paddingTop: statusBarHeight + 'px',
    // #endif
    // #ifdef H5
    paddingTop: '0px',
    // #endif
    // #ifdef APP-PLUS
    paddingTop: statusBarHeight + 'px',
    // #endif
  }
}

/**
 * 页面跳转（处理小程序页面栈溢出）
 */
export function safeNavigate(url, params = {}) {
  const query = Object.keys(params)
    .map(key => `${key}=${encodeURIComponent(params[key])}`)
    .join('&')

  const fullUrl = query ? `${url}?${query}` : url

  // #ifdef MP-WEIXIN
  // 小程序页面栈最多 10 层，超过时使用 redirectTo
  const pages = getCurrentPages()
  if (pages.length >= 9) {
    uni.redirectTo({ url: fullUrl })
  } else {
    uni.navigateTo({ url: fullUrl })
  }
  // #endif

  // #ifndef MP-WEIXIN
  uni.navigateTo({ url: fullUrl })
  // #endif
}

/**
 * 设置页面标题
 */
export function setPageTitle(title) {
  uni.setNavigationBarTitle({ title })
  // #ifdef H5
  document.title = title
  // #endif
}
```

---

## 四、常见面试题

### Q1：uniapp 的条件编译是如何实现的？`#ifdef` 和 `#ifndef` 的区别是什么？

**回答要点：**

- 条件编译是**编译时**机制，在打包阶段由编译器处理，不会增加运行时代码体积
- `#ifdef PLATFORM`：如果当前编译目标是 PLATFORM 平台，则保留该代码块
- `#ifndef PLATFORM`：如果当前编译目标**不是** PLATFORM 平台，则保留该代码块
- 每个 `#ifdef` / `#ifndef` 必须对应一个 `#endif` 结束标记
- 条件编译可以在 `<template>`、`<script>`、`<style>` 以及 `.json` 配置文件中使用
- 编译器会根据目标平台，在编译产物中完全移除不属于该平台的代码块

### Q2：uniapp 的页面生命周期执行顺序是怎样的？

**回答要点：**

- 应用启动：`App.onLaunch` → `App.onShow` → 页面 `onLoad` → 页面 `onShow` → 页面 `onReady`
- 页面跳转（A → B）：A 页面 `onHide` → B 页面 `onLoad` → B 页面 `onShow` → B 页面 `onReady` → A 页面 `onUnload`（非 tabBar 页面）
- 应用后台：`App.onHide` → 当前页面 `onHide`
- 应用前台：`App.onShow` → 当前页面 `onShow`
- tabBar 页面切换时不会触发 `onUnload`，只会触发 `onHide`/`onShow`

### Q3：uniapp 中 rpx 是什么？与 px 的换算关系是什么？

**回答要点：**

- rpx（responsive pixel）是 uniapp 的响应式像素单位，可以根据屏幕宽度自适应缩放
- 规定屏幕宽度为 750rpx，在 iPhone 6 上（375px 宽），1rpx = 0.5px
- 换算公式：`实际 px = 屏幕宽度(px) / 750 * rpx值`
- 设计稿通常以 750px 宽度为基准，设计师标注的 px 值直接使用 rpx 即可
- 建议使用 rpx 作为主要单位，需要固定像素时使用 px

### Q4：uni.request 和 axios 有什么区别？在 uniapp 中应该使用哪个？

**回答要点：**

- `uni.request` 是 uniapp 原生 API，支持所有平台（H5、小程序、App），是小程序端唯一可用的网络请求方式
- axios 基于 XMLHttpRequest，只能在 H5 端使用，小程序端不支持
- 在 uniapp 项目中，推荐使用 `uni.request` 或基于 `uni.request` 封装的请求库（如 luch-request）
- 如果需要在 H5 端使用 axios，可以通过条件编译在 H5 端使用 axios，其他端使用 uni.request

### Q5：uniapp 如何实现跨端的底部安全区域适配？

**回答要点：**

- 使用 CSS 环境变量 `env(safe-area-inset-bottom)` 获取底部安全区域高度
- 在 `manifest.json` 中配置 `"safearea": { "bottom": { "offset": "auto" } }`
- 在需要适配的页面样式中添加：`padding-bottom: env(safe-area-inset-bottom)` 或 `padding-bottom: constant(safe-area-inset-bottom)`（兼容旧版 iOS）
- uniapp 提供了 `uni.getSystemInfoSync().safeAreaInsets` API 获取安全区域信息

---

## 五、避坑指南

| 常见错误 | 现象 | 原因 | 解决方案 |
|---------|------|------|----------|
| 在 `<text>` 组件中嵌套 `<view>` | 小程序端渲染异常，H5 端正常 | 小程序 `<text>` 组件内只能嵌套 `<text>`，不支持嵌套 `<view>` | 将 `<text>` 内嵌套的 `<view>` 改为 `<text>` 或调整结构 |
| 使用 `v-html` 指令 | 小程序端不支持，渲染为空 | 小程序不支持 `v-html`，因为小程序使用自定义渲染引擎 | 使用 `<rich-text>` 组件替代，或使用 `mp-html` 等第三方富文本插件 |
| 直接操作 DOM（如 `document.querySelector`） | 小程序端报错 `document is not defined` | 小程序运行在 JSCore 中，没有 DOM 环境 | 使用 `uni.createSelectorQuery()` 替代，并通过条件编译隔离 H5 专属代码 |
| 在 `onLoad` 中获取节点信息 | 获取到的节点信息为 null | `onLoad` 时页面尚未渲染完成，DOM 节点不存在 | 将节点查询放到 `onReady` 生命周期中 |
| 忘记配置小程序合法域名 | 小程序端请求失败，报错"不在以下 request 合法域名列表中" | 小程序要求 `uni.request` 的域名必须在后台配置 | 在微信小程序后台"开发管理 → 开发设置"中配置 request 合法域名 |
| 使用 `position: fixed` 在 `<scroll-view>` 内 | 小程序端 fixed 定位失效 | 小程序 `<scroll-view>` 会创建新的层叠上下文，fixed 相对于 scroll-view 定位 | 将 fixed 元素移到 `<scroll-view>` 外部 |
| 在 TabBar 页面使用 `uni.navigateTo` | 页面跳转后 TabBar 消失 | TabBar 页面必须使用 `uni.switchTab` 跳转 | TabBar 页面跳转使用 `uni.switchTab`，非 TabBar 页面使用 `uni.navigateTo` |
| `z-index` 在各端表现不一致 | H5 端正常，小程序端层级混乱 | 小程序原生组件（如 video、map、canvas）层级最高，无法被普通元素覆盖 | 使用 `cover-view` / `cover-image` 覆盖原生组件，或将原生组件隐藏后再显示自定义内容 |

---

## 本章学习自检

- [ ] 我能解释 uniapp "编译时转换"的原理，理解 `.vue` 文件如何转换为各平台代码
- [ ] 我掌握条件编译 `#ifdef` / `#ifndef` 的用法，能在 template、script、style 中正确使用
- [ ] 我能说出 `pages.json`、`manifest.json`、`uni.scss` 三个核心配置文件的作用
- [ ] 我理解应用生命周期（onLaunch/onShow/onHide）和页面生命周期（onLoad/onShow/onReady/onHide/onUnload）的执行顺序
- [ ] 我能熟练使用 view、scroll-view、swiper 等内置组件，并了解它们的跨端差异
- [ ] 我了解 uni-ui 组件库的常用组件，知道如何快速搭建移动端 UI
- [ ] 我掌握 `uni.request` 的封装方法，能写出带 token 拦截和错误处理的统一请求模块
- [ ] 我理解 `uni.getLocation`、`uni.chooseImage` 等 API 的跨端使用差异和权限处理
- [ ] 我能编写 H5 / 小程序 / App 三端差异化的登录模块代码
- [ ] 我理解 rpx 单位的原理和换算规则，能正确处理跨端响应式布局

---

> **学习导航**：
> - 返回 [学习路线总览](../README.md)
> - 本模块下一个文件：[02-uniapp渲染差异与性能优化](./02-uniapp渲染差异与性能优化.md)
> - 相关模块：[Vue 3 核心语法](../05-vue/01-Vue3核心语法.md) | [加载性能优化](../08-performance/01-加载性能优化.md)