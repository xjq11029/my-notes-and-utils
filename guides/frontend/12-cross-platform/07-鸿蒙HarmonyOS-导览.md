> 本文档为 `07-鸿蒙HarmonyOS.md` 的导览文件，提供快速索引和全局概览。
> 前置知识：TypeScript 基础、Vue 或 React 声明式 UI 经验

---

# 07-鸿蒙HarmonyOS - 导览

---

## 1.1 HarmonyOS 的定位与版本演进（核心概念）

| 维度 | 内容 |
|---|---|
| 是什么 | HarmonyOS 是华为推出的分布式操作系统。需先分清两个概念：**OpenHarmony** 是完全开源、由开放原子开源基金会管理的共享底座，可裁剪到传感器与 IoT 设备；**HarmonyOS** 是基于 OpenHarmony 的商业闭源版本，叠加 HMS、应用市场、超级终端协同等华为专有模块 |
| 能做什么 | 覆盖手机、平板、手表、智慧屏、车机、PC 等多设备形态，并提供跨设备协同能力；OpenHarmony 侧可适配从 128KB 内存的轻量设备到 128MB 以上的标准设备 |
| 怎么用 | 开发侧统一用 DevEco Studio + ArkTS + ArkUI；通过 API 版本号判断能力边界（3.0 为 API 8，3.1/4.x 为 API 9，NEXT 5.0 为 API 12，5.0.3 为 API 15，5.0.5 为 API 17，HarmonyOS 6 为 API 20） |
| 原理和工作流程 | 1.0（2019-08）首发智慧屏；2.0（2021-06）覆盖手机并兼容 APK；3.0/3.1（2022-10 / 2023-05）引入声明式 ArkUI 与 ArkTS；4.x（2023-08 起）为 NEXT 铺垫；**NEXT（5.0，2024-10-08 Beta/Release、10-22 商用）移除 AOSP，核心 API 12**；5.1（2025-06-11，API 17）落地鸿蒙 PC；HarmonyOS 6（2025-06-20 HDC 2025 发布开发者 Beta）配套 DevEco Studio 6 与 API 20 |
| 缺点 | 版本演进快、API 版本与系统版本并非一一对应，容易在能力判断上出错；HarmonyOS 与 OpenHarmony 常被混为一谈，选型与文档检索时容易走偏 |

---

## 1.2 HarmonyOS NEXT：纯血鸿蒙（核心概念）

| 维度 | 内容 |
|---|---|
| 是什么 | HarmonyOS NEXT 的本质变化是"去 AOSP"——彻底移除 Android 开源项目代码，只支持原生鸿蒙应用包（HAP，Harmony Ability Package），不再兼容 Android APK |
| 能做什么 | 提供完全自主的应用运行与分发体系；让前端开发者可以用 ArkTS + ArkUI 这一套与 TypeScript、声明式 UI 高度重叠的技术栈开发应用，无需 Android/iOS 原生背景 |
| 怎么用 | 用 DevEco Studio 创建 Stage 模型工程；用 ArkTS 编写 `.ets` 文件；通过 Hvigor 构建出 HAP 包并上架应用市场 |
| 原理和工作流程 | 应用代码经 ArkTS 编译器编译为方舟字节码 → 由方舟运行时执行 → UI 由 ArkUI 声明式框架驱动渲染 → 应用以 HAP 包形式安装，通过 Ability 生命周期被系统调度 |
| 缺点 | 生态必须重建：三方库、SDK、原生模块都需要重新适配，ohpm 上的库覆盖度仍在补齐；存量 Android 应用无法直接迁移，业务重写成本高 |

---

## 1.3 ArkTS 语言特性（核心概念）

| 维度 | 内容 |
|---|---|
| 是什么 | ArkTS 是 HarmonyOS 应用开发的主力语言，官方定位为"TypeScript 的严格子集 + 静态类型增强"，在 TS 语法基础上增加了强制类型与性能友好约束 |
| 能做什么 | 用接近 TypeScript 的语法编写鸿蒙应用逻辑；通过静态类型让编译器在 AOT 阶段做更激进的优化；用 `TaskPool` / `Worker` 做并发，用 `@Concurrent` 标记可并发函数 |
| 怎么用 | 变量、参数、返回值全部显式标注类型；用 `interface` + `class implements` 声明类型关系；类属性必须有初始值或在构造函数中赋值；数组写 `Array<User>` 或 `string[]` |
| 原理和工作流程 | ArkTS 禁用 `any`/`unknown`，使类型信息在编译期完整可推导 → 采用名义类型而非结构化类型，让跨类型兼容必须显式声明 → 禁止运行时改变对象布局，使属性偏移量在编译期固定 → 禁用 `eval`/`with` 与大部分反射，让编译产物可预测、可优化 |
| 缺点 | 从 TS 迁移时最易踩坑的是随手写 `any` 或依赖"形状相同即可赋值"；`number` 统一为双精度浮点，没有 int/double 之分；无独立样式表，样式必须写成链式属性调用 |

---

## 1.4 ArkUI 声明式开发范式（核心概念）

| 维度 | 内容 |
|---|---|
| 是什么 | ArkUI 是鸿蒙的声明式 UI 框架：用 `@Component` 装饰 `struct`，在 `build()` 中描述 UI 结构，状态变化自动驱动视图刷新；状态由 `@State`/`@Prop`/`@Link`/`@Provide`/`@Consume`/`@Observed`/`@ObjectLink`/`@Watch`/`@StorageLink` 等装饰器管理 |
| 能做什么 | 用声明式方式构建组件与页面；实现组件内部状态、父子单向/双向同步、跨层级共享、类对象属性观察、状态变化回调、应用级全局状态等全部状态场景 |
| 怎么用 | `@Entry @Component struct Page { @State count: number = 0; build() { Column({ space: 12 }) { Text(\`计数：${this.count}\`).fontSize(20); Button('加一').onClick(() => { this.count++; }) } } }` |
| 原理和工作流程 | 状态变量被包装为可观察对象 → 框架记录哪些 UI 节点（elementId）依赖它 → 状态变化时只通知依赖它的节点 → 重新执行受影响的 build 片段 → 与旧描述做差异比对后只应用差异 |
| 缺点 | 状态粒度直接决定刷新范围，粒度太粗会导致大范围重渲染；`ForEach` 的 key 不稳定会让列表项被整体重建，是长列表卡顿的常见原因 |

---

## 1.5 元服务与原生应用（核心概念）

| 维度 | 内容 |
|---|---|
| 是什么 | 元服务（原"原子化服务"）是鸿蒙的轻量化应用形态，免安装、即用即走，入口是服务卡片、负一屏、搜索、扫码、碰一碰等；原生鸿蒙应用则是完整的 HAP 包，需下载安装 |
| 能做什么 | 元服务适合单点服务场景（查快递、看天气、扫码点单），强调"服务直达"；原生应用承载完整业务流程与全部 API 能力 |
| 怎么用 | 元服务的卡片由独立的 `EntryFormAbility` 提供数据：在 `onAddForm` 返回初始数据，在 `onUpdateForm` 中通过 `formProvider.updateForm()` 主动刷新 |
| 原理和工作流程 | 系统按卡片配置拉起 `EntryFormAbility` → `onAddForm` 返回 `formBindingData` 作为卡片渲染数据 → 定时或主动触发 `onUpdateForm` 更新卡片内容 → 用户点击卡片跳转到元服务主流程 |
| 缺点 | 包体积有严格上限，能力范围受限，复杂业务需跳转完整应用；卡片生命周期与刷新频率受系统策略约束，不能高频更新；不适合承载复杂交互流程 |

---

## 2.1 ArkTS 与 TypeScript 的异同（底层原理）

| 维度 | 内容 |
|---|---|
| 是什么 | ArkTS 与 TS 共享语法、类型系统、接口、泛型与装饰器，但 ArkTS 在类型严格性、动态能力与运行环境上做了大量收紧，并内置 ArkUI 与 ohpm 包管理 |
| 能做什么 | 让前端开发者可以低成本迁移大部分 TS 知识；同时通过限制换取更可预测、更易优化的编译产物 |
| 怎么用 | 可直接复用：TS 类型语法、接口、泛型、装饰器、组件化与单向数据流的设计模式、前端工程化与性能优化思路。需重新学习：ArkTS 的类型限制、ArkUI 组件体系与链式样式、状态管理装饰器语义、DevEco Studio 与 Hvigor |
| 原理和工作流程 | 名义类型让跨类型兼容必须显式声明，编译器可安全做去虚化 → 禁用 `any` 让类型信息完整，支持更激进的内联 → 禁止运行时改对象布局让属性访问编译为直接内存偏移 → 禁用 `eval`/`with` 消除无法静态分析的路径 |
| 缺点 | 表达力弱于 TS，某些依赖动态特性的库需要改写；编译错误信息对 TS 使用者可能不够直观；生态与工具链（ohpm vs npm）完全不同，无法直接复用前端包 |

---

## 2.2 状态管理装饰器的同步机制（底层原理）

| 维度 | 内容 |
|---|---|
| 是什么 | ArkUI 状态管理的核心是"包装类 + 依赖收集"：每个被装饰变量被包装为可观察对象，框架记录依赖它的 UI 节点，变化时只刷新这些节点。基础装饰器包括 `@State`（内部状态）、`@Prop`（父→子单向）、`@Link`（父↔子双向）、`@Provide`/`@Consume`（跨层级双向）、`@Observed`/`@ObjectLink`（对象属性观察） |
| 能做什么 | 覆盖全部状态场景：组件内状态、只读传值、双向绑定、深层共享、对象属性级观察；`@Watch` 用于状态变化后执行副作用，`@StorageLink`/`@StorageProp` 用于应用级全局状态 |
| 怎么用 | `@State` 本地初始化；`@Prop` 由父组件传值（值拷贝，不可回传）；`@Link` 禁止本地初始化、由父组件用 `Child({ value: $count })` 传入（API 9 起也支持 `Child({ value: this.count })`）；`@Provide` 在祖先声明、`@Consume` 在后代按名匹配；`@ObjectLink` 接收 `@Observed` 实例 |
| 原理和工作流程 | 初始渲染时父组件的状态包装类通过构造函数传给子组件，子组件的 `@Link` 包装类把自身指针注册给父组件的 `@State` → 父组件状态变更时遍历依赖它的系统组件与状态变量 → 通知 `@Link` 更新 → 子组件依赖该变量的 UI 节点刷新；反向则由 `@Link` 调用父组件 `@State` 包装类的 set 方法同步回父级 |
| 缺点 | `@Prop` 是值拷贝，只有第一层响应式，修改深层属性不会同步；`@State` 能观察数组增删改但观察不到元素内部属性变化，必须配合 `@Observed` + `@ObjectLink`；`@Provide`/`@Consume` 的匹配是隐式的，重构时容易漏改 |

---

## 2.3 状态管理 V2（底层原理）

| 维度 | 内容 |
|---|---|
| 是什么 | API 12 起 ArkUI 提供的状态管理 V2：`@ComponentV2` 声明组件，`@Local` 表示内部状态，`@Param`/`@Once` 表示外部传入参数，`@Event` 表示回调，`@Provider`/`@Consumer` 表示跨层级共享，`@Monitor` 监听变化，`@ObservedV2`/`@Trace` 精确标记需观察的属性 |
| 能做什么 | 解决 V1 在深度观察与大型应用中的限制：`@Trace` 可精确标记属性实现深层观察；用"参数 + 回调"替代双向绑定，使数据流更明确、更易追踪 |
| 怎么用 | V2 组件中用 `@Local` 声明内部状态、`@Param` 接收外部参数、`@Event` 接收回调；跨层级用 `@Provider`/`@Consumer`；监听变化用 `@Monitor`；需要深层观察的类用 `@ObservedV2` 装饰、需要观察的属性用 `@Trace` 装饰 |
| 原理和工作流程 | `@Trace` 在属性级别建立依赖关系，属性变更时只通知依赖该属性的 UI 节点；V2 的依赖收集更细粒度，避免了 V1 中"整个对象换掉才能触发深层更新"的问题 |
| 缺点 | V1 与 V2 **不能在同一个自定义组件中混用**；V2 的 API 面更广，学习成本高于 V1；存量 V1 项目迁移需要按模块逐步进行，期间两套写法并存会增加维护成本 |

---

## 2.4 页面路由与 Navigation 导航（底层原理）

| 维度 | 内容 |
|---|---|
| 是什么 | ArkUI 提供两套导航方案：`router`（`@ohos.router` / `@kit.ArkUI`，API 12 起官方不推荐用于新项目）与 `Navigation` 组件 + `NavPathStack`（官方推荐） |
| 能做什么 | 完成页面跳转、参数传递、返回、替换、清栈等全部导航操作；`Navigation` 还支持在平板/折叠屏上自动切换左右分栏模式，适配成本低 |
| 怎么用 | router：`router.pushUrl({ url: 'pages/DetailPage', params: { id: 1001 } })`、`router.getParams()`、`router.back()`。Navigation：`@Provide('pathStack') pathStack: NavPathStack = new NavPathStack()` → `Navigation(this.pathStack) { ... }.navDestination(this.pageMap)` → 跳转用 `this.pathStack.pushPath({ name: 'detail', param: { id: 1001 } })` → 目标页用 `@Consume('pathStack')` 拿栈对象，读取参数用 `getParamByName('detail')`，返回用 `pop()` |
| 原理和工作流程 | `NavPathStack` 维护一个页面栈，`pushPath` 把 `NavPathInfo`（含 name 与 param）入栈 → 框架用 `navDestination` 指定的 `@Builder` 路由表按 name 匹配并渲染 `NavDestination` 内容 → `pop` 出栈并回到上一页 |
| 缺点 | `router` 需要单独维护页面路径配置文件，分栏适配需自行实现；`Navigation` 需要理解 `@Builder` 路由表与 `NavPathStack` 两个概念，初学门槛略高；`getParamByName` 返回的是数组，取值时需要注意类型断言 |

---

## 2.5 ArkUI 的声明式渲染机制（底层原理）

| 维度 | 内容 |
|---|---|
| 是什么 | ArkUI 的渲染流程为"状态驱动 → 差异更新 → 局部刷新"：状态变量变化后，框架通过依赖收集找到受影响的 UI 节点，只重新执行受影响的 build 片段，再与旧描述做差异比对并只应用差异 |
| 能做什么 | 保证状态粒度越细、刷新范围越小；支撑长列表、表单、动画等常见场景的性能表现 |
| 怎么用 | 优化手段围绕"缩小刷新范围"展开：状态粒度拆细、`ForEach` 提供稳定唯一的 key、动画属性用 `animateTo` 或属性动画而非状态驱动、避免在 build 中做重计算 |
| 原理和工作流程 | 状态包装类通知依赖收集器 → 找到依赖该状态的 elementId 列表 → 只重新执行受影响片段的 build → 生成新的组件树描述并与旧描述 diff → 只把差异应用到真实渲染节点，不重建整棵树 |
| 缺点 | 依赖收集是隐式的，滥用大对象状态会导致大范围重渲染；`ForEach` 的 key 不稳定会让列表项被整体重建，性能急剧下降；动画若靠状态驱动，每帧都要触发差异比对 |

---

## 2.6 ArkWeb 组件与 H5 混合开发（底层原理）

| 维度 | 内容 |
|---|---|
| 是什么 | ArkWeb 是 HarmonyOS 的 Web 引擎（基于 Chromium 内核），通过 `Web` 组件在原生应用中内嵌 H5 页面；核心能力包括 `runJavaScript`、`.javaScriptProxy()`、`registerJavaScriptProxy()`、`onPageEnd`/`onPageBegin` 与 `.javaScriptAccess()` |
| 能做什么 | 复用存量 H5 页面与 Web 技术栈；实现原生与 H5 的双向通信（原生调 H5 的全局函数、H5 调原生注入的对象）；对存量 Web 业务做渐进式鸿蒙化 |
| 怎么用 | 原生调 H5：`this.controller.runJavaScript('window.onNativeReady && window.onNativeReady()')`；H5 调原生：`.javaScriptProxy({ object: this.bridge, name: 'harmonyBridge', methodList: ['showToast', 'getAppVersion'], controller: this.controller })`，H5 侧写 `window.harmonyBridge.showToast('你好')`；本地资源用 `$rawfile('index.html')` 引用 |
| 原理和工作流程 | `Web` 组件创建 Web 渲染实例 → 页面加载前注入 `javaScriptProxy` 声明的对象与方法 → H5 通过 `window.name.方法()` 调用原生 → 原生通过 `runJavaScript` 在 H5 上下文执行脚本 → `onPageEnd` 回调在页面加载完成后触发 |
| 缺点 | `.javaScriptAccess()` **默认关闭**，忘记开启会导致 H5 白屏；`.javaScriptProxy()` 必须在页面加载前设置才能保证 H5 首屏可用；运行时用 `registerJavaScriptProxy()` 注册后**必须调用 `refresh()`** 才生效；混合开发的性能上限受 Web 引擎限制，核心交互仍建议用 ArkUI 原生实现 |

---

## 2.7 跨端框架对鸿蒙的支持现状（底层原理）

| 维度 | 内容 |
|---|---|
| 是什么 | 现有跨端框架对鸿蒙的支持方式：uni-app 官方支持编译到鸿蒙；Taro 4.x 支持编译到鸿蒙 ArkTS，另有 RN for Harmony 混合方案；React Native 通过 RN-OH（React Native for OpenHarmony）基于 JSI/Fabric/TurboModule 对接 ArkUI；Flutter 由 OpenHarmony 社区维护适配版本 |
| 能做什么 | 让存量 Web / 跨端工程以较低成本产出鸿蒙应用，避免整体用 ArkTS 重写；对已有 uniapp/Taro 项目尤其友好 |
| 怎么用 | uniapp / Taro 侧：在构建配置中增加鸿蒙目标，按平台做条件编译；RN 侧：接入 RN-OH 并配置 DevEco Studio 环境（部分场景需申请白名单）；Flutter 侧：使用社区适配版本，需接受跟进主版本升级的滞后 |
| 原理和工作流程 | 编译型方案（uniapp/Taro）把前端代码编译为 ArkTS/ArkUI 产物；运行型方案（RN-OH）在鸿蒙侧实现 ArkUI 渲染器与原生模块桥接，让 JS 逻辑继续驱动 ArkUI 渲染；两者都受"鸿蒙侧原生能力覆盖度"制约 |
| 缺点 | 成熟度参差：uniapp 相对成熟，Taro 与 RN-OH 仍在发展中，Flutter 适配属早期；**不能假设"编译通过 = 功能可用"**，三方库与原生模块需逐个验证鸿蒙兼容性并做真机回归；适配成本集中在语言框架层、依赖生态层（npm 需换成 ohpm 库）与工程工具链层 |

---

## 3.1 计数器组件：`@State` 与 `@Link` 父子双向同步（实战应用）

| 维度 | 内容 |
|---|---|
| 是什么 | 一个完整的两级组件示例：父组件用 `@State` 持有计数，子组件用 `@Link` 建立双向绑定，双方任一侧修改都能同步到另一侧 |
| 能做什么 | 演示 `@State` 与 `@Link` 的协作方式，是理解 ArkUI 状态管理的入门范例；也是面试中最高频要求手写的代码片段 |
| 怎么用 | 子组件：`@Link value: number;` 且**不写初始值**，`build()` 中 `Button('加一').onClick(() => { this.value++; })`；父组件：`@State count: number = 0;`，传值写 `CounterChild({ value: $count })`，重置写 `this.count = 0` |
| 原理和工作流程 | 初始渲染时父组件 `@State` 的包装类传给子组件，子组件 `@Link` 包装类把自身指针注册给父组件 → 子组件修改 `this.value` 时调用父组件 `@State` 包装类的 set 方法同步回父级 → 两侧各自刷新依赖该变量的 UI 节点 |
| 缺点 | `@Link` 禁止本地初始化，写错会直接编译报错；若子组件只需只读展示，应改用 `@Prop`（值拷贝、不回传），否则会造成不必要的双向耦合 |

---

## 3.2 列表与对象观察：`@Observed` / `@ObjectLink`（实战应用）

| 维度 | 内容 |
|---|---|
| 是什么 | 列表项为类对象时的标准实践：类用 `@Observed` 装饰，列表项子组件用 `@ObjectLink` 接收实例，从而观察对象属性的变化 |
| 能做什么 | 实现"改哪个对象就只刷新哪个列表项"，而不是刷新整个列表；解决 `@State` 只能观察数组增删改、观察不到元素内部属性变化的问题 |
| 怎么用 | `@Observed class TodoItem { id: number; title: string; done: boolean; constructor(...) {...} }`；子组件 `@ObjectLink item: TodoItem;`（不可本地初始化）；列表用 `ForEach(this.items, (item: TodoItem) => { ListItem() { TodoRow({ item: item }) } }, (item: TodoItem) => item.id.toString())` |
| 原理和工作流程 | `@Observed` 让类实例的属性变更可被追踪 → `@ObjectLink` 在子组件中订阅该实例 → 直接修改 `this.item.done = value` 时，框架只刷新订阅该实例的列表项 → 未受影响的列表项不重建 |
| 缺点 | `@Observed` 只对第一层属性生效，嵌套对象需要逐层装饰；`ForEach` 的 key 必须稳定唯一，用数组下标会导致列表增删后状态错乱；`@ObjectLink` 不可本地初始化，必须由父组件传入 |

---

## 3.3 元服务卡片（Form）简介（实战应用）

| 维度 | 内容 |
|---|---|
| 是什么 | 元服务的核心入口是服务卡片，卡片数据由独立的 `EntryFormAbility` 提供，生命周期方法包括 `onAddForm`（卡片被添加时返回初始数据）与 `onUpdateForm`（定时或主动刷新时更新数据） |
| 能做什么 | 让用户在桌面直接看到关键信息并一键进入服务主流程，实现"服务直达"；适合查快递、看天气、扫码点单这类单点服务 |
| 怎么用 | `export default class EntryFormAbility extends FormExtensionAbility { onAddForm(want: Want): formBindingData.FormBindingData { return formBindingData.createFormBindingData({ title: '今日待办', count: '3 项' }); } onUpdateForm(formId: string): void { formProvider.updateForm(formId, formBindingData.createFormBindingData({ title: '今日待办', count: '5 项' })).catch(...) } }` |
| 原理和工作流程 | 系统按卡片配置拉起 `EntryFormAbility` → `onAddForm` 返回 `FormBindingData` 作为卡片渲染数据 → 系统按刷新策略或业务主动调用 `onUpdateForm` → 通过 `formProvider.updateForm()` 推送新数据 → 卡片重新渲染 |
| 缺点 | 卡片刷新频率受系统策略约束，不能高频更新；包体积与能力范围受限，复杂业务必须跳转完整应用；元服务的整体形态约束决定了它不适合承载长流程交互 |

---

> [返回原文](./07-鸿蒙HarmonyOS.md) | [返回模块目录](../README.md) | [返回知识导览](../知识导览.md)
