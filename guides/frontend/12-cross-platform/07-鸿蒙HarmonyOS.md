> 模块：12-cross-platform（拓展 跨端开发）
> 难度：★★★★ 生态进阶
> 前置知识：TypeScript 基础、Vue 或 React 声明式 UI 经验

---

# 07-鸿蒙HarmonyOS

---

## 一、核心概念

### 1.1 HarmonyOS 的定位与版本演进

HarmonyOS（鸿蒙）是华为推出的分布式操作系统。理解它需要先分清两个概念：

| 概念 | 性质 | 说明 |
|---|---|---|
| **OpenHarmony** | 完全开源，由开放原子开源基金会管理 | 共享的开源底座，可按资源需求裁剪到传感器、家电、IoT 设备上 |
| **HarmonyOS** | 商业闭源，跑在华为自家设备上 | 基于 OpenHarmony，叠加 HMS、应用市场、超级终端协同等华为专有模块 |

**版本演进时间线：**

| 版本 | 时间 | 关键变化 |
|---|---|---|
| HarmonyOS 1.0 | 2019 年 8 月 | 首发于智慧屏，LiteOS + Linux 双内核，奠定分布式基础 |
| HarmonyOS 2.0 | 2021 年 6 月 | 覆盖手机、平板、手表等；混合架构，可运行 Android APK |
| HarmonyOS 3.0 / 3.1 | 2022 年 10 月 / 2023 年 5 月 | API 8 → API 9；**引入声明式 ArkUI**，推出 Stage 模型与 ArkTS |
| HarmonyOS 4.x | 2023 年 8 月 - 2024 年 9 月 | 仍兼容 Android 应用，为 NEXT 做铺垫 |
| **HarmonyOS NEXT（5.0）** | 2024 年 10 月 8 日 Beta/Release，10 月 22 日商用 | **彻底移除 AOSP，不再兼容 APK**，核心 API 12；只支持原生鸿蒙应用（HAP 包） |
| HarmonyOS 5.1 | 2025 年 6 月 11 日 | API 17；HarmonyOS PC 形态落地 |
| **HarmonyOS 6** | 2025 年 6 月 20 日 HDC 2025 发布开发者 Beta | 配套 DevEco Studio 6 与 API 20，强化 AI 能力与跨设备流转 |

**API 版本对照（开发中常用来判断能力边界）：** HarmonyOS 3.0 为 API 8，3.1/4.x 为 API 9，NEXT 5.0 为 API 12，5.0.3 为 API 15，5.0.5 为 API 17，HarmonyOS 6 为 API 20。

### 1.2 HarmonyOS NEXT：纯血鸿蒙

**HarmonyOS NEXT 的本质变化是"去 AOSP"**，这带来了三个直接影响：

1. **应用形态改变**——不再支持 Android APK，只能安装原生鸿蒙应用包（HAP，Harmony Ability Package）
2. **开发语言改变**——主力语言从 Java/Kotlin 转为 **ArkTS**，UI 从 XML/命令式转为 **ArkUI 声明式**
3. **生态必须重建**——所有三方库、SDK、原生模块都需要重新适配

**为什么前端开发者应该关注 NEXT：**

- ArkTS 基于 TypeScript 扩展，语法与 TS 高度相似，前端迁移成本远低于从 Java 迁移
- ArkUI 是声明式 UI 范式，与 Vue/React 的心智模型接近
- 鸿蒙开发不需要 Android/iOS 原生背景，前端技能可直接复用一大半

### 1.3 ArkTS 语言特性

ArkTS 是 HarmonyOS 应用开发的主力语言，官方定位是 **"TypeScript 的严格子集 + 静态类型增强"**。

| 特性 | 说明 |
|---|---|
| **基于 TypeScript** | 语法、类型系统、接口、泛型、装饰器与 TS 高度一致 |
| **强制静态类型** | 禁用 `any` 与 `unknown`，所有变量、参数、返回值都必须有明确类型 |
| **禁止结构化类型** | 不能靠"形状相同"来兼容两个类型，必须显式声明 `implements` 或继承 |
| **禁止运行时改对象布局** | 对象的属性在编译期确定，不支持运行时增删属性；类属性必须有初始值 |
| **禁用动态执行** | 不支持 `eval()`、`with`，也限制 `Object.defineProperty` 等反射能力 |
| **无独立样式表** | 样式通过链式属性调用表达（`.fontSize(20)`），而不是 CSS |
| **并发模型** | 用 `TaskPool` 与 `Worker` 替代 Web Worker，用 `@Concurrent` 标记可并发执行的函数 |

```typescript
// ArkTS 基础语法示例：类、接口、显式类型标注
// 注意：属性必须有初始值或在构造函数中赋值，且不能运行时增删
interface UserInfo {
  id: number;
  name: string;
  email?: string; // 可选属性是允许的
}

class User implements UserInfo {
  id: number;
  name: string;
  email?: string;

  constructor(id: number, name: string, email?: string) {
    this.id = id;
    this.name = name;
    this.email = email;
  }

  // 返回值类型必须显式标注
  describe(): string {
    return `${this.name}（ID: ${this.id}）`;
  }
}

// 数组与泛型：类型参数需要显式声明
const users: Array<User> = [new User(1, '张三'), new User(2, '李四')];
const names: string[] = users.map((user: User) => user.name);
console.info(`共 ${names.length} 个用户`);
```

> **易错点**：ArkTS 中 `number` 统一为双精度浮点，没有 int/double 之分；且**不允许 `any`**，从 TS 迁移时最容易踩的坑就是随手写 `any` 导致编译报错。

### 1.4 ArkUI 声明式开发范式

ArkUI 是鸿蒙的 UI 框架，采用**声明式范式**：用 `@Component` 装饰 `struct`，在 `build()` 中描述 UI 结构，状态变化自动驱动 UI 刷新。

**核心装饰器一览（状态管理 V1）：**

| 装饰器 | 作用 | 数据流向 | 典型场景 |
|---|---|---|---|
| `@State` | 组件内部状态 | 组件内双向 | 计数器、表单输入、开关状态 |
| `@Prop` | 父 → 子单向同步 | 单向（值拷贝） | 子组件只读展示父组件数据 |
| `@Link` | 父 ↔ 子双向同步 | 双向（引用） | 子组件修改父组件状态 |
| `@Provide` / `@Consume` | 跨层级双向同步 | 双向（自动匹配） | 深层组件共享状态，免去逐层传递 |
| `@Observed` / `@ObjectLink` | 观察类实例的属性变化 | 引用 | 列表项对象的属性变更 |
| `@Watch` | 监听状态变化并执行回调 | — | 状态变化后触发副作用 |
| `@StorageLink` / `@StorageProp` | 与 AppStorage 双向/单向同步 | 双向 / 单向 | 应用级全局状态 |

**ArkUI 与 Vue / React 的心智对照：**

| 概念 | ArkUI | Vue 3 | React |
|---|---|---|---|
| 组件定义 | `@Component struct` | `.vue` SFC / `defineComponent` | 函数组件 |
| 渲染入口 | `build()` 方法 | `template` / `render()` | `return JSX` |
| 局部状态 | `@State` | `ref` / `reactive` | `useState` |
| 父子传值 | `@Prop` / `@Link` | `props` / `v-model` | `props` / 回调 |
| 跨层级共享 | `@Provide` / `@Consume` | `provide` / `inject` | `Context` |
| 条件渲染 | `if / else` 语句 | `v-if` | `{cond && <X />}` |
| 列表渲染 | `ForEach` | `v-for` | `array.map()` |
| 样式 | 链式属性 `.fontSize(20)` | `<style>` / 内联 | `style` 对象 |

### 1.5 元服务与原生应用

| 对比项 | 原生鸿蒙应用 | 元服务（原"原子化服务"） |
|---|---|---|
| 形态 | 完整的应用包（HAP），需下载安装 | 轻量化服务，免安装、即用即走 |
| 入口 | 桌面图标 | 服务卡片、负一屏、搜索、扫码、碰一碰 |
| 包体积限制 | 相对宽松 | 有严格上限，需极简 |
| 能力范围 | 完整 API 能力 | 受限，复杂能力需跳转完整应用 |
| 适用场景 | 主业务 App | 单点服务（查快递、看天气、扫码点单） |

**元服务的设计约束：** 强调"服务直达"，因此卡片（Form）是第一入口，主流程必须能在 1-2 步内完成，不适合承载复杂业务流程。

---

## 二、底层原理

### 2.1 ArkTS 与 TypeScript 的异同

| 维度 | TypeScript | ArkTS |
|---|---|---|
| 类型系统 | 结构类型（structural typing） | **名义类型（nominal typing）**，必须显式 `implements` / 继承 |
| `any` / `unknown` | 允许（`any` 为逃生舱） | **禁止** |
| 类型标注 | 大量依赖类型推断，可省略 | 强制显式标注，推断能力受限 |
| 对象属性 | 可运行时增删、`Object.defineProperty` | **禁止**运行时改变对象布局 |
| 动态执行 | `eval` / `with` 可用（严格模式下 `eval` 受限） | **禁用** |
| 反射能力 | 完整（`Reflect`、`Proxy`） | 大幅限制 |
| 空安全 | `strictNullChecks` 可选 | 强制空安全 |
| 编译目标 | 输出 JS，由宿主引擎执行 | 编译为方舟字节码，由方舟运行时执行 |
| UI 框架 | 无内置 | 内置 ArkUI（声明式 + 链式样式） |
| 包管理 | npm / pnpm / yarn | ohpm（OpenHarmony Package Manager） |

**为什么 ArkTS 要做这些限制？**

- **静态类型 + 名义类型**让编译器可以在 AOT 阶段做更激进的内联与去虚化优化，从而提升运行性能
- **禁止运行时改对象布局**让对象的属性偏移量在编译期固定，属性访问可编译为直接内存偏移，避免哈希查找
- **禁用动态执行**意味着不存在 `eval` 这类无法静态分析的能力，让编译产物更可预测、更安全

**迁移时的知识复用点：**

| 可直接复用 | 需要重新学习 |
|---|---|
| TypeScript 的类型、接口、泛型、装饰器语法 | ArkTS 的类型限制（不能用 `any`、不能用结构化类型） |
| 声明式 UI 的思维（状态驱动视图） | ArkUI 的组件体系与链式样式写法 |
| 组件化、单向数据流、状态提升等设计模式 | 状态管理装饰器的语义与同步规则 |
| 前端工程化经验（构建、分包、性能优化思路） | DevEco Studio、Hvigor 构建、ohpm 依赖管理 |
| Web 性能优化常识（懒加载、长列表虚拟化） | 鸿蒙特有的性能分析工具与调优手段 |

### 2.2 状态管理装饰器的同步机制

ArkUI 状态管理的核心是**"包装类 + 依赖收集"**：每个被装饰的变量都会被包装成可观察对象，框架记录哪些 UI 节点依赖它，变化时只刷新依赖它的节点。

**`@State`：组件内部状态**

- 变量被包装为可观察对象，赋值时触发依赖它的 UI 节点刷新
- 观察能力：简单类型观察赋值；类对象观察属性赋值（`Object.keys` 范围内的属性）；数组观察元素增删改

**`@Prop`：父 → 子单向同步**

- 父组件传递时**做值拷贝**，子组件修改不会回传父组件
- 适合"只读展示"场景；因为拷贝，深层对象只有第一层是响应式的

**`@Link`：父 ↔ 子双向同步**

- 与父组件的 `@State` / `@Link` / `@StorageLink` 建立双向绑定，共享同一个数据源
- **禁止本地初始化**，必须由父组件传入
- 初始化语法：`Child({ value: $count })`，API 9 起也支持 `Child({ value: this.count })`

**`@Provide` / `@Consume`：跨层级双向同步**

- `@Provide` 在祖先组件声明，`@Consume` 在后代组件声明，按变量名或别名自动匹配
- 免去逐层传递 `@Prop` 的样板代码，但**依赖关系隐式**，重构时需要留意

**`@Observed` / `@ObjectLink`：观察类实例的属性变化**

- `@Observed` 装饰类，使其实例的属性变更可被观察
- `@ObjectLink` 装饰子组件中的变量以接收该实例，**不可本地初始化**
- 典型用途：列表中每个元素是类对象，修改对象属性时只刷新对应的列表项

### 2.3 状态管理 V2

从 API 12 起，ArkUI 提供了状态管理 V2，解决 V1 在深度观察与大型应用中的若干限制。

| V1 | V2 | 说明 |
|---|---|---|
| `@Component` | `@ComponentV2` | V2 组件声明 |
| `@State` | `@Local` | 组件内部状态 |
| `@Prop` | `@Param` / `@Once` | `@Param` 支持外部传入，`@Once` 表示只接收一次 |
| `@Link` | `@Param` + `@Event` | V2 用"参数 + 回调"替代双向绑定，数据流更明确 |
| `@Provide` / `@Consume` | `@Provider` / `@Consumer` | 跨层级共享 |
| `@Watch` | `@Monitor` | 状态变化监听 |
| `@Observed` / `@ObjectLink` | `@ObservedV2` / `@Trace` | `@Trace` 精确标记需要观察的属性，支持深层观察 |

> **注意**：V1 与 V2 不能混用在同一个自定义组件中。新项目建议直接使用 V2，存量项目按模块逐步迁移。面试中如果只答 V1 而不知道 V2 存在，容易被追问。

### 2.4 页面路由与 Navigation 导航

ArkUI 有两套导航方案：

| 方案 | 模块 | 状态 | 适用场景 |
|---|---|---|---|
| **router** | `@ohos.router` / `@kit.ArkUI` | API 12 起官方**不推荐**用于新项目 | 简单页面跳转、存量项目 |
| **Navigation** | 内置组件 + `NavPathStack` | 官方推荐 | 新项目、需要分栏/平板适配、复杂路由 |

```typescript
// ============ 方案一：router（存量方案，不推荐新项目使用） ============
import { router } from '@kit.ArkUI';

// 跳转并传参
router.pushUrl({ url: 'pages/DetailPage', params: { id: 1001 } });
// 目标页读取参数
const params = router.getParams() as Record<string, number>;
// 返回上一页
router.back();
```

```typescript
// ============ 方案二：Navigation + NavPathStack（官方推荐） ============
@Entry
@Component
struct Index {
  // NavPathStack 管理整个页面栈，通过 @Provide 向下共享
  @Provide('pathStack') pathStack: NavPathStack = new NavPathStack();

  // @Builder 定义路由表：name 与页面内容一一对应
  @Builder
  pageMap(name: string) {
    if (name === 'detail') {
      DetailPage()
    }
  }

  build() {
    Navigation(this.pathStack) {
      Column({ space: 16 }) {
        Button('跳转到详情页')
          .onClick(() => {
            // 入栈，param 用于传递参数
            this.pathStack.pushPath({ name: 'detail', param: { id: 1001 } });
          })
      }
      .width('100%')
      .padding(20)
    }
    .title('首页')
    .navDestination(this.pageMap)
    .mode(NavigationMode.Stack)
  }
}

@Component
struct DetailPage {
  // 通过 @Consume 拿到祖先组件 @Provide 的栈对象
  @Consume('pathStack') pathStack: NavPathStack;

  build() {
    NavDestination() {
      Column({ space: 16 }) {
        Text(`收到的参数：${JSON.stringify(this.pathStack.getParamByName('detail'))}`)
          .fontSize(16)
        Button('返回')
          .onClick(() => {
            this.pathStack.pop();
          })
      }
      .width('100%')
      .padding(20)
    }
    .title('详情页')
  }
}
```

**Navigation 的优势：**

1. **组件化路由**——路由表用 `@Builder` 声明，与 UI 代码同源，无需在配置文件中维护页面路径
2. **自动分栏**——在平板/折叠屏上可自动切换为左右分栏模式，适配成本低
3. **栈操作更灵活**——`pushPath` / `pop` / `replacePath` / `clear` / `getParamByName` 等方法覆盖复杂场景

### 2.5 ArkUI 的声明式渲染机制

ArkUI 的渲染流程可以概括为 **"状态驱动 → 差异更新 → 局部刷新"**：状态变量变化 → 状态包装类通知依赖收集器 → 找到依赖该状态的 UI 节点（elementId 列表）→ 只重新执行受影响的 build 片段 → 与旧描述做差异比对 → 只把差异应用到真实渲染节点（不重建整棵树）。

**关键结论：**

- ArkUI **不重建整棵组件树**，而是精准刷新依赖该状态的节点，因此状态粒度越细，刷新范围越小
- `ForEach` 的第三个参数（key 生成函数）至关重要，key 不稳定会导致列表项被整体重建，性能急剧下降
- 频繁变化的动画属性应使用 `animateTo` 或属性动画，而不是靠状态驱动，避免每帧触发差异比对

### 2.6 ArkWeb 组件与 H5 混合开发

ArkWeb 是 HarmonyOS 的 Web 引擎（基于 Chromium 内核），通过 `Web` 组件在原生应用中内嵌 H5 页面。

| 能力 | API | 说明 |
|---|---|---|
| 加载网页 | `Web({ src, controller })` | `src` 支持在线地址与 `$rawfile()` 本地资源 |
| 执行 JS | `controller.runJavaScript(script)` | 原生调用 H5 的全局函数 |
| 注入对象 | `.javaScriptProxy({ object, name, methodList, controller })` | 在页面加载前注册，H5 侧通过 `window.name.方法()` 调用 |
| 动态注册 | `controller.registerJavaScriptProxy(...)` | 运行时注册，**必须调用 `refresh()` 才生效** |
| 页面事件 | `.onPageEnd()` / `.onPageBegin()` | 页面加载完成/开始时回调 |
| 安全配置 | `.javaScriptAccess(true)` | **默认关闭**，需显式开启 |

```typescript
// ArkWeb 混合开发完整示例：原生 ↔ H5 双向通信
import { webview } from '@kit.ArkWeb';
import { BusinessError } from '@kit.BasicServicesKit';

// 1. 定义要暴露给 H5 的对象
// 注意：方法必须是普通函数，且必须在 methodList 中显式声明，否则 H5 侧调用不到
class JsBridge {
  // H5 侧调用：window.harmonyBridge.showToast('你好')
  showToast(message: string): void {
    console.info(`来自 H5 的调用：${message}`);
  }

  // H5 侧调用：window.harmonyBridge.getAppVersion()
  getAppVersion(): string {
    return '1.0.0';
  }
}

@Entry
@Component
struct HybridPage {
  // WebviewController 用于控制 Web 组件（执行 JS、前进后退、刷新等）
  controller: webview.WebviewController = new webview.WebviewController();
  private bridge: JsBridge = new JsBridge();

  build() {
    Column() {
      Web({ src: 'https://example.com/h5', controller: this.controller })
        // 开启 JavaScript 执行能力，默认是关闭的
        .javaScriptAccess(true)
        // 通过属性注册 JSBridge：在页面加载前就生效，H5 首屏即可调用
        .javaScriptProxy({
          object: this.bridge,
          name: 'harmonyBridge',
          methodList: ['showToast', 'getAppVersion'],
          controller: this.controller,
        })
        // 页面加载完成后，原生侧主动通知 H5
        .onPageEnd(() => {
          this.controller.runJavaScript('window.onNativeReady && window.onNativeReady()')
            .catch((error: BusinessError) => {
              console.error(`调用 H5 失败：${error.message}`);
            });
        })
    }
    .width('100%')
    .height('100%')
  }
}
```

**ArkWeb 的三个易错点：** `.javaScriptAccess()` 默认关闭，忘记开启会导致 H5 白屏；`.javaScriptProxy()` 必须在页面加载前设置才能保证 H5 首屏可用，运行时用 `registerJavaScriptProxy()` 注册后**必须调用 `refresh()`**；本地资源需用 `$rawfile('index.html')` 引用，不能直接写文件路径。

### 2.7 跨端框架对鸿蒙的支持现状

| 框架 | 支持方式 | 成熟度 | 注意事项 |
|---|---|---|---|
| **uni-app** | 官方推出鸿蒙版本，可将 Vue 项目编译为鸿蒙应用 | 较成熟 | 部分原生能力需通过条件编译处理；插件市场对鸿蒙的支持仍在补齐 |
| **Taro** | Taro 4.x 支持编译到鸿蒙 ArkTS，另有 React Native for Harmony 的混合方案 | 发展中 | 需配合 DevEco Studio，部分场景需申请白名单 |
| **React Native** | 通过 **RN-OH**（React Native for OpenHarmony）适配，基于 JSI / Fabric / TurboModule 对接 ArkUI 渲染引擎 | 发展中 | 由华为与 OpenHarmony 社区维护；三方库需逐个验证鸿蒙兼容性 |
| **Flutter** | OpenHarmony 社区维护的 Flutter 适配版本 | 早期 | 非官方支持，跟进 Flutter 主版本升级有滞后 |
| **纯 ArkTS** | 官方原生方案 | 最成熟 | 无法复用前端框架生态，需按 ArkUI 重写 UI |

**适配成本的三个来源：**

1. **语言与框架层**——ArkTS + ArkUI 是一套新体系，即使有 TS 基础也需要重新学习状态管理与组件体系
2. **依赖与生态层**——npm/pub 生态不能直接使用，需改用 ohpm 上的库；缺失的库要自研或寻找替代
3. **工程与工具链层**——DevEco Studio、Hvigor 构建、签名与上架流程都需要重新建立

**成本评估的建议框架：**

| 项目特征 | 适配优先级 | 理由 |
|---|---|---|
| 政企、金融、能源类 To B 应用 | 高 | 国产化替代是硬性要求，鸿蒙适配常被列入合规清单 |
| 面向国内 C 端的工具/服务类应用 | 中-高 | 鸿蒙设备存量增长快，缺失会直接影响用户覆盖 |
| 已有 uniapp / Taro 工程 | 中 | 编译链路已有，主要是适配与回归测试成本 |
| 重度依赖自定义原生模块的 RN/Flutter 应用 | 低-中 | 原生模块需逐个重写，投入产出比需要仔细核算 |
| 纯海外业务 | 低 | 目标市场与鸿蒙设备覆盖不重叠 |

---

## 三、实战应用

### 3.1 计数器组件：`@State` 与 `@Link` 父子双向同步

```typescript
// ============ 子组件：用 @Link 与父组件双向同步 ============
@Component
struct CounterChild {
  // @Link 禁止本地初始化，必须由父组件传入
  @Link value: number;

  build() {
    Row({ space: 12 }) {
      // 修改 @Link 会同步回父组件的 @State
      Button('减一').onClick(() => { this.value--; })

      Text(`${this.value}`)
        .fontSize(20)
        .fontWeight(FontWeight.Medium)

      Button('加一').onClick(() => { this.value++; })
    }
    .justifyContent(FlexAlign.Center)
  }
}

// ============ 父组件：用 @State 持有状态 ============
@Entry
@Component
struct CounterPage {
  @State count: number = 0;

  build() {
    Column({ space: 20 }) {
      Text(`父组件计数：${this.count}`).fontSize(18)

      // 用 $count 语法把 @State 传给子组件的 @Link
      // API 9 起也可以写成 CounterChild({ value: this.count })
      CounterChild({ value: $count })

      // 父组件修改 @State，子组件的 @Link 也会同步更新
      Button('重置').onClick(() => { this.count = 0; })
    }
    .width('100%')
    .padding(24)
  }
}
```

**要点说明：** `@State` 是数据源，`@Link` 是引用绑定，两者共享同一个值；子组件修改 `this.value` 会触发父组件 `@State` 更新，父组件修改 `this.count` 也会同步到子组件；如果需要"子组件只读展示"，应改用 `@Prop`（值拷贝，修改不回传）。

### 3.2 列表与对象观察：`@Observed` / `@ObjectLink`

```typescript
// 1. @Observed 装饰的类，其实例的属性变化才能被观察
@Observed
class TodoItem {
  id: number;
  title: string;
  done: boolean;

  constructor(id: number, title: string, done: boolean = false) {
    this.id = id;
    this.title = title;
    this.done = done;
  }
}

// 2. 列表项组件：用 @ObjectLink 接收 @Observed 实例（不可本地初始化）
@Component
struct TodoRow {
  @ObjectLink item: TodoItem;

  build() {
    Row() {
      Text(this.item.title)
        .fontSize(16)
        // 根据 done 状态显示删除线
        .decoration({
          type: this.item.done ? TextDecorationType.LineThrough : TextDecorationType.None,
        })

      Checkbox()
        .select(this.item.done)
        .onChange((value: boolean) => {
          // 直接修改 @Observed 对象的属性，对应列表项会自动刷新
          this.item.done = value;
        })
    }
    .width('100%')
    .justifyContent(FlexAlign.SpaceBetween)
    .padding(12)
  }
}

// 3. 列表页面
@Entry
@Component
struct TodoListPage {
  @State items: TodoItem[] = [new TodoItem(1, '学习 ArkTS 类型系统'), new TodoItem(2, '理解状态管理装饰器')];

  build() {
    List({ space: 8 }) {
      // ForEach 的第三个参数是 key 生成函数，必须稳定唯一
      // key 不稳定会导致列表项被整体重建，是长列表卡顿的常见原因
      ForEach(
        this.items,
        (item: TodoItem) => {
          ListItem() {
            TodoRow({ item: item })
          }
        },
        (item: TodoItem) => item.id.toString()
      )
    }
    .width('100%')
    .padding(16)
  }
}
```

**为什么需要 `@Observed` / `@ObjectLink`？** 数组本身的变化（push / splice）能被 `@State` 观察到，但**数组元素的内部属性变化**观察不到；`@Observed` 让类实例的属性变更可被追踪，`@ObjectLink` 让子组件接收并订阅这个实例，效果是"改哪个对象就只刷新哪个列表项"。

### 3.3 元服务卡片（Form）简介

元服务的核心入口是服务卡片，卡片由独立的 `EntryFormAbility` 提供数据。

```typescript
// EntryFormAbility：卡片生命周期与数据更新
import { formBindingData, FormExtensionAbility, formProvider } from '@kit.FormKit';
import { Want } from '@kit.AbilityKit';

export default class EntryFormAbility extends FormExtensionAbility {
  // 卡片被添加到桌面时触发，返回初始数据
  onAddForm(want: Want): formBindingData.FormBindingData {
    return formBindingData.createFormBindingData({ title: '今日待办', count: '3 项' });
  }

  // 卡片定时刷新或主动刷新时触发
  onUpdateForm(formId: string): void {
    const updated: Record<string, string> = { title: '今日待办', count: '5 项' };
    formProvider.updateForm(formId, formBindingData.createFormBindingData(updated))
      .catch((error: Error) => {
        console.error(`更新卡片失败：${error.message}`);
      });
  }
}
```

---

## 四、常见面试题

**Q1：HarmonyOS NEXT 和之前的 HarmonyOS 版本有什么本质区别？**

**答案要点：**

- NEXT 之前的版本（1.0 - 4.x）采用混合架构，包含 AOSP 代码，可以运行 Android APK
- **NEXT 彻底移除了 AOSP**，只支持原生鸿蒙应用包（HAP），不再兼容 APK
- 开发语言主力从 Java/Kotlin 转为 ArkTS，UI 从 XML/命令式转为 ArkUI 声明式
- 生态必须重建：三方库、SDK、原生模块都需要重新适配
- 版本对应关系：NEXT 即 HarmonyOS 5.0，2024 年 10 月商用，核心 API 12

**Q2：ArkTS 和 TypeScript 有什么区别？为什么 ArkTS 要禁用 `any`？**

**答案要点：**

- ArkTS 是 TypeScript 的严格子集 + 静态类型增强，语法与类型系统基本一致
- 关键差异：禁止 `any`/`unknown`、采用名义类型而非结构化类型、禁止运行时改变对象布局、禁用 `eval`/`with` 与大部分反射能力
- 禁用 `any` 的目的：让编译器能在 AOT 阶段做更激进的内联与去虚化优化；`any` 会破坏类型信息，使优化无从下手
- 禁止运行时改对象布局的目的：让属性偏移量在编译期固定，属性访问可编译为直接内存偏移，避免哈希查找开销
- 迁移注意：`number` 统一为双精度浮点，没有 int/double 之分

**Q3：`@State`、`@Prop`、`@Link` 三者的区别是什么？**

**答案要点：**

- `@State`：组件内部状态，是数据的源头，可本地初始化
- `@Prop`：父 → 子**单向**同步，传递时做值拷贝，子组件修改不回传父组件，适合只读展示
- `@Link`：父 ↔ 子**双向**同步，与父组件的 `@State`/`@Link`/`@StorageLink` 共享同一数据源，**禁止本地初始化**，初始化语法为 `Child({ value: $count })`
- 选择依据：数据只在子组件内部用 → `@State`；子组件只读 → `@Prop`；子组件要改且需回传 → `@Link`
- 跨层级共享应使用 `@Provide` / `@Consume`，避免逐层透传

**Q4：ArkUI 的声明式 UI 和 Vue / React 有什么相似与不同？**

**答案要点：**

- 相似：都是"状态驱动视图"的声明式范式，组件化 + 单向数据流的心智模型一致
- 相似：条件渲染用 `if` 语句（对应 `v-if`）、列表渲染用 `ForEach`（对应 `v-for`）
- 不同：ArkUI 组件用 `@Component struct` + `build()` 定义，而 Vue 用 SFC、React 用函数组件
- 不同：ArkUI **没有独立样式表**，样式通过链式属性调用表达（`.fontSize(20).fontColor('#333')`），不是 CSS 也不是 `style` 对象
- 不同：ArkUI 的状态装饰器体系（`@State`/`@Prop`/`@Link`/`@Provide`/`@Consume`）与 Vue 的 `ref`/`props`/`provide` 语义相近但不完全等价，尤其是 `@Link` 的双向绑定语义在 React 中没有直接对应物
- 不同：ArkUI 是编译到方舟字节码并运行在方舟运行时上，不是运行在浏览器或 JS 引擎中

**Q5：ArkWeb 是什么？和普通 WebView 有什么差异？**

**答案要点：**

- ArkWeb 是 HarmonyOS 的 Web 引擎（基于 Chromium 内核），通过 `Web` 组件在原生应用中内嵌 H5
- 与 H5 的通信有两个方向：原生调 H5 用 `controller.runJavaScript()`；H5 调原生用 `.javaScriptProxy()` 注入对象
- 三个易错点：`.javaScriptAccess()` **默认关闭**，不开启会导致 H5 白屏；`.javaScriptProxy()` 需在页面加载前设置才能保证 H5 首屏可用；运行时用 `registerJavaScriptProxy()` 注册后**必须调用 `refresh()`** 才生效
- 本地资源需用 `$rawfile('index.html')` 引用，不能直接写文件路径
- 混合开发的性能上限受 Web 引擎限制，核心交互仍建议用 ArkUI 原生实现

**Q6：现有 uniapp / Taro / React Native 项目如何适配鸿蒙？成本如何评估？**

**答案要点：**

- uniapp 官方已支持编译到鸿蒙；Taro 4.x 支持编译到鸿蒙 ArkTS，另有 RN for Harmony 混合方案；RN 通过 RN-OH 适配，基于 JSI/Fabric/TurboModule 对接 ArkUI
- 适配成本来自三层：语言与框架层（ArkTS + ArkUI 是新体系）、依赖与生态层（npm 不能直接用，需改用 ohpm 库）、工程与工具链层（DevEco Studio、Hvigor、签名上架）
- 评估优先级：政企/金融等国产化合规要求高的应用优先级最高；面向国内 C 端的工具服务类次之；重度依赖自定义原生模块的项目投入产出比需谨慎核算
- 关键提醒：RN 和 Flutter 的三方库需逐个验证鸿蒙兼容性，**不能假设"编译通过 = 功能可用"**，必须做完整回归测试

**Q7：鸿蒙开发当前的前景与就业市场如何？**

**答案要点：**

- 技术侧：ArkTS + ArkUI 与前端技能高度重叠，TypeScript 与声明式 UI 经验可直接迁移，是前端开发者拓展能力面的低成本路径
- 市场侧：鸿蒙岗位随设备存量与国产化政策增长，但总量仍小于 Android/iOS；需求集中在华为生态合作伙伴、政企与外包项目
- 岗位要求：通常要求掌握 ArkTS/ArkUI、DevEco Studio、Stage 模型与 Ability 生命周期，有元服务或 ArkWeb 混合开发经验是加分项
- 风险提示：技术栈与华为生态绑定较深，技能可迁移性低于 Web 前端；是否投入应结合自身业务方向判断

---

## 五、避坑指南

| 常见错误 | 现象 | 原因 | 解决方案 |
|---|---|---|---|
| 在 ArkTS 中写 `any` 或依赖结构化类型 | 编译报错，提示类型不允许 | ArkTS 禁用 `any`/`unknown`，且采用名义类型而非结构类型 | 为所有变量显式标注类型；跨类型兼容必须显式 `implements` 或继承 |
| 运行时给对象添加新属性 | 编译报错或属性访问不到 | ArkTS 禁止运行时改变对象布局，属性必须在编译期确定 | 在 `class` 或 `interface` 中预先声明所有属性，并用构造函数初始化 |
| 在类中声明属性但不给初始值 | 编译报错，提示属性未初始化 | ArkTS 要求类属性必须有初始值或在构造函数中赋值 | 声明时给默认值，或在 `constructor` 中完成赋值 |
| 用 `@Link` 时在子组件里本地初始化 | 编译报错，提示 `@Link` 不允许本地初始化 | `@Link` 必须由父组件的数据源初始化 | 删除子组件中的初始值，父组件传值写 `Child({ value: $count })` |
| 用 `@Prop` 传递对象后修改深层属性 | 子组件修改后父组件未同步，或修改不生效 | `@Prop` 是值拷贝，且只有第一层是响应式的 | 需要双向同步改用 `@Link`；需要观察对象深层属性用 `@Observed` + `@ObjectLink` |
| 修改数组元素的属性但 UI 不刷新 | 数组长度变化能刷新，但元素内部属性变化无反应 | `@State` 只能观察到数组本身的增删改，观察不到元素内部属性变化 | 把元素类型用 `@Observed` 装饰，子组件用 `@ObjectLink` 接收 |
| `ForEach` 的 key 生成函数返回数组下标 | 列表增删后出现状态错乱、滚动位置跳变 | key 不稳定导致列表项被整体重建，框架无法正确复用节点 | 使用业务上稳定唯一的 ID 作为 key，如 `item.id.toString()` |
| ArkWeb 中 H5 页面白屏、JS 不执行 | Web 组件显示了页面框架但脚本无反应 | `.javaScriptAccess()` 默认关闭，未显式开启 | 在 `Web` 组件上调用 `.javaScriptAccess(true)` |
| 用 `registerJavaScriptProxy` 注册后 H5 仍调用不到 | H5 侧 `window.xxx` 为 `undefined` | 运行时注册后未刷新页面，注入未生效 | 注册后调用 `controller.refresh()`；或改用 `.javaScriptProxy()` 属性在页面加载前注册 |
| 混合开发中本地 HTML 加载失败 | 提示找不到文件 | 直接写了文件系统路径 | 使用 `$rawfile('index.html')` 引用本地资源 |
| 新项目仍使用 `router` 做页面导航 | 代码可运行，但官方文档标记为不推荐，分栏适配需自行实现 | API 12 起官方推荐使用 `Navigation` + `NavPathStack` | 新项目直接用 `Navigation`，通过 `@Builder` 声明路由表 |
| 在 `@Component` 与 `@ComponentV2` 中混用 V1/V2 装饰器 | 编译报错 | 状态管理 V1 与 V2 不能在同一个自定义组件中混用 | 同一组件内统一使用一套：V1 用 `@State`/`@Prop`/`@Link`，V2 用 `@Local`/`@Param`/`@Event` |
| 假设"跨端框架编译通过就等于功能可用" | 部分功能在鸿蒙设备上静默失效 | 三方库与原生模块的鸿蒙兼容性参差不齐 | 建立鸿蒙真机回归测试清单，逐个验证核心链路与三方依赖 |

---

## 本章学习自检

- [ ] 我能区分 OpenHarmony 与 HarmonyOS，并说出各自的性质与适用设备
- [ ] 我能复述 HarmonyOS 的主要版本节点，特别是 NEXT（5.0）与 HarmonyOS 6 的关键变化
- [ ] 我能解释 HarmonyOS NEXT "去 AOSP" 带来的三个直接影响（应用形态、开发语言、生态重建）
- [ ] 我能列出 ArkTS 相对 TypeScript 的五条关键限制，并说明这些限制的性能动机
- [ ] 我能写出一个包含 `@Component` / `@State` / `build()` 的完整 ArkUI 组件
- [ ] 我能准确区分 `@State`、`@Prop`、`@Link`、`@Provide`/`@Consume` 的数据流向与使用场景
- [ ] 我能说明 `@Observed` + `@ObjectLink` 解决的是什么问题，以及为什么 `@State` 观察不到数组元素的属性变化
- [ ] 我知道状态管理 V2（`@ComponentV2` / `@Local` / `@Param` / `@Trace`）的存在，并理解 V1 与 V2 不能混用
- [ ] 我能说出 `router` 与 `Navigation` 的差异，并用 `NavPathStack` 写出入栈、传参、返回的完整流程
- [ ] 我能用 `Web` 组件 + `.javaScriptProxy()` 实现原生与 H5 的双向通信，并知道 `.javaScriptAccess()` 默认关闭
- [ ] 我能说出 uniapp / Taro / RN / Flutter 对鸿蒙的支持方式与成熟度差异
- [ ] 我能区分原生鸿蒙应用与元服务，并说明元服务的入口与设计约束
- [ ] 我能从语言框架层、依赖生态层、工程工具链层三个维度评估鸿蒙适配成本
- [ ] 我能把 ArkUI 的声明式 UI 与 Vue/React 做对照，说清相似点与关键差异

---

## 学习导航

- 上一章：[06-ReactNative与Flutter](./06-ReactNative与Flutter.md)
- 下一章：无（本章为 12-cross-platform 跨端开发补充章）
- 导览文件：[07-鸿蒙HarmonyOS-导览](./07-鸿蒙HarmonyOS-导览.md)
- 相关章节：[01-uniapp跨端开发基础](./01-uniapp跨端开发基础.md) | [05-跨端方案选型与桌面端](./05-跨端方案选型与桌面端.md)
- 常见错误：[常见错误汇总](./常见错误汇总.md)
- 概念对比：[概念对比速查](./概念对比速查.md)
- 综合场景：[综合场景](./综合场景.md)
