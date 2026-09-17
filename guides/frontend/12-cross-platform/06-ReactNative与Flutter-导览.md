> 本文档为 `06-ReactNative与Flutter.md` 的导览文件，提供快速索引和全局概览。
> 前置知识：React 基础、Vue 基础、移动端渲染常识

---

# 06-ReactNative与Flutter - 导览

---

## 1.1 三条技术路线的本质区别（核心概念）

| 维度 | 内容 |
|---|---|
| 是什么 | 按"屏幕上的像素最终由谁绘制"划分三条路线：WebView 容器（uniapp 的 App 端 Vue 页面、Cordova）用系统浏览器内核绘制；原生组件映射（React Native）把组件映射为平台原生控件；自绘引擎（Flutter）用自带引擎直接绘制 |
| 能做什么 | 建立判断跨端方案上限的统一坐标系，一眼看出某个方案在一致性、性能、原生感上的先天强弱 |
| 怎么用 | 先问"谁绘制像素"，再推导三个后果：一致性（Flutter > RN > WebView 类）、性能天花板（Flutter > RN > WebView 类）、原生感（RN > Flutter > WebView 类） |
| 原理和工作流程 | WebView 类在运行时把 Web 页面装进系统 WebView，受浏览器内核版本影响；RN 通过 JS 逻辑驱动平台原生控件，外观与行为天然跟随系统；Flutter 的引擎在构建期预编译着色器，运行期把 Widget 树转为 Layer 与 Scene 后交给 GPU，完全绕过平台控件 |
| 缺点 | 三条路线的强弱是权衡而非绝对优劣：Flutter 一致性最强但包体积最大、原生感最弱；RN 原生感最强但性能受通信层制约；WebView 类成本最低但上限也最低 |

---

## 1.2 React Native 是什么（核心概念）

| 维度 | 内容 |
|---|---|
| 是什么 | Meta 开源的跨端框架，核心理念是 "Learn once, write anywhere"——用 React 的组件化思维与声明式 UI 写代码，最终渲染为平台原生控件 |
| 能做什么 | 用一套 React 代码同时开发 iOS 与 Android 应用；复用 React 生态（Hooks、Zustand、Redux、TanStack Query）；在不发版的前提下热更新 JS 业务逻辑 |
| 怎么用 | `npx @react-native-community/cli init MyApp` 创建工程；用 `View` / `Text` / `Image` 等内置组件编写 UI；用 `StyleSheet.create` 写样式；导航用 React Navigation；`npx react-native run-android` / `run-ios` 运行 |
| 原理和工作流程 | JS 线程执行 React 逻辑 → 通信层把组件树变更传给原生侧 → Shadow 线程用 Yoga 计算 Flexbox 布局 → UI 线程创建并更新原生控件；新架构下通信层由 JSI 取代 Bridge，支持同步调用且无需 JSON 序列化 |
| 缺点 | 样式是 CSS 子集，与 Web 写法差异大（默认 `flexDirection: 'column'`、无单位、无层叠）；双端原生构建链路复杂；旧架构的 Bridge 在长列表与手势动画场景存在明显瓶颈 |

---

## 1.3 Flutter 是什么（核心概念）

| 维度 | 内容 |
|---|---|
| 是什么 | Google 开源的跨端框架，使用 Dart 语言 + 自绘渲染引擎，一套代码可运行在 iOS、Android、Web、桌面（Windows/macOS/Linux）与嵌入式设备上 |
| 能做什么 | 构建各平台表现高度一致的 UI；稳定跑满 60/120fps 的复杂动画与图形；通过 Platform Channel 调用原生能力；在 Debug 模式下享受秒级热重载 |
| 怎么用 | `flutter create my_app` 创建工程；一切 UI 由 Widget 组合表达（`Column`、`Row`、`Container`、`Text`）；状态用 `setState` 或 Riverpod / Provider / Bloc 管理；`flutter run` 运行，`flutter build apk` / `build ipa` 打包 |
| 原理和工作流程 | 执行 `build()` 生成不可变的 Widget 树 → 框架比对新旧 Widget，类型与 Key 相同则复用 Element → Element 驱动 RenderObject 执行 layout 与 paint → 生成 Layer 树与 Scene → 交给 Impeller / Skia 转为 GPU 指令绘制 |
| 缺点 | 需新学 Dart，无法复用前端 npm 生态；包体积增量最大（内置渲染引擎）；Release 为 AOT 机器码导致动态化能力弱；原生观感（滚动回弹、键盘行为、无障碍语义）需要额外适配 |

---

## 1.4 与 uniapp 的定位差异（核心概念）

| 维度 | 内容 |
|---|---|
| 是什么 | 三者主战场不同：uniapp 主打国内小程序 + App + H5，RN 主打海外 iOS/Android 双端 App，Flutter 主打全平台高性能应用 |
| 能做什么 | 让选型先对齐"业务重心在哪"，避免用小程序优先的框架去做重度原生应用，或用 Flutter 去做以小程序为主的业务 |
| 怎么用 | 国内小程序矩阵 → uniapp；需要原生体验的海外双端 App → RN；强 UI 一致性与高性能 → Flutter |
| 原理和工作流程 | uniapp 依赖编译期转换 + 各平台渲染层适配，因此对小程序生态最友好；RN 依赖原生控件映射，因此原生观感最好；Flutter 依赖自绘引擎，因此一致性与性能最强但包体积最大 |
| 缺点 | 定位差异是趋势性判断而非硬规则，真实项目常出现混合形态（如 uniapp 应用内嵌 RN 页面、Flutter 应用内嵌 WebView），需要按模块评估而非整体二选一 |

---

## 1.5 RN vs Flutter vs uniapp 三方对比（核心概念）

| 维度 | 内容 |
|---|---|
| 是什么 | 从渲染机制、语言与生态、性能表现、包体积、动态化能力、团队适配成本、典型选型场景七个维度做三方横向对比 |
| 能做什么 | 把"选哪个框架"转化为可讨论的取舍：一致性 vs 原生感、性能 vs 包体积、动态化 vs 编译方式 |
| 怎么用 | 一致性 vs 原生感是核心矛盾（Flutter 一致但不原生、RN 原生但随系统变化）；包体积与性能正相关（性能要 Flutter 级别就得内置渲染引擎）；动态化与编译方式强相关（JIT/解释执行才能热更新，AOT 不能） |
| 原理和工作流程 | 三条差异都源于同一组根因：渲染引擎是自带的还是系统的、UI 是自绘的还是映射的、代码是解释执行还是 AOT 编译。前者决定一致性与包体积，中者决定原生感，后者决定动态化能力 |
| 缺点 | 对比结论会随版本迭代变化（RN 新架构与 Flutter Impeller 都在持续改善短板）；团队适配成本高度依赖既有技术栈，无法用统一分值衡量 |

---

## 2.1 React Native 的 Bridge 通信机制与瓶颈（底层原理）

| 维度 | 内容 |
|---|---|
| 是什么 | 旧架构下 RN 有 JS 线程、Shadow 线程、UI（Main）线程三条线程，彼此只能通过 Bridge 通信；Bridge 具备**异步、批量、序列化**三个特性 |
| 能做什么 | 让 JS 逻辑与原生渲染解耦，使开发者用 JS 就能驱动原生控件；但也正是这三个特性构成了性能瓶颈的根源 |
| 怎么用 | 开发者无需直接操作 Bridge；理解它有助于解释"为什么快速滚动列表会白屏""为什么手势动画卡顿"这类现象 |
| 原理和工作流程 | UI 线程捕获用户交互 → 序列化后异步送往 JS 线程 → JS 执行 setState 并 diff → 把更新指令序列化回传 → Shadow 线程用 Yoga 计算布局 → UI 线程更新原生控件。整个链路的每一跳都有序列化与事件循环延迟 |
| 缺点 | 异步导致无法在同一帧内完成"读取原生值 → 计算 → 更新 UI"；序列化开销随数据量线性增长；批量发送虽降低频次却增加延迟，快速滚动时通信队列积压直接表现为白屏 |

---

## 2.2 JSI 与 Fabric：新架构的解法（底层原理）

| 维度 | 内容 |
|---|---|
| 是什么 | 新架构用 JSI（JavaScript Interface）+ TurboModules + Fabric + Codegen 替换 Bridge；**RN 0.76（2024 年 10 月）起新架构成为默认配置**，Bridgeless 模式同时默认开启 |
| 能做什么 | JSI 让 JS 直接持有 C++ 宿主对象引用并支持同步调用；TurboModules 让原生模块按需加载；Fabric 用 C++ 实现影子树并支持同步布局；Codegen 在构建期从 TS 类型生成两侧接口代码 |
| 怎么用 | 编写 TS 规范文件（`TurboModuleRegistry.getEnforcing<Spec>('模块名')`）→ Codegen 生成原生接口 → 原生侧按签名实现并注册到 PackageList → JS 侧直接同步或异步调用 |
| 原理和工作流程 | JS 调用 JSI 暴露的宿主对象 → C++ 层直接执行原生逻辑或转发到 UI 线程 → 数据以共享内存或轻量引用传递，不再强制 JSON 序列化；Fabric 的影子树同时被 JS 线程与 UI 线程访问，省掉一次跨线程拷贝 |
| 缺点 | 原生模块必须按 Codegen 生成的接口实现，迁移旧模块有一定成本；新增或修改原生代码无法热更新；新架构下部分旧第三方库尚未完全适配 |

---

## 2.3 Hermes 引擎（底层原理）

| 维度 | 内容 |
|---|---|
| 是什么 | Meta 为 RN 定制的 JavaScript 引擎，**自 RN 0.70 起成为默认引擎**；核心设计是在构建期把 JS 预编译为字节码，放弃 JIT |
| 能做什么 | 显著加快应用启动速度、降低内存占用、减小 APK 体积（字节码可裁剪，如移除未使用的 `eval` 支持） |
| 怎么用 | 新版本 RN 默认启用，无需配置；如需关闭可显式设置 `hermesEnabled=false`（不推荐） |
| 原理和工作流程 | 构建期由 Hermes 编译器把 JS 编译为 `.hbc` 字节码并打包进应用 → 运行时直接加载字节码执行，省去解析与编译阶段 → 解释器逐条执行，无 JIT 预热与优化过程 |
| 缺点 | 无 JIT 导致长时间高强度计算的性能略弱于 JSC；真正需要重计算的逻辑应下沉到原生模块或用 C++ 编写，而不是靠 JS 硬扛 |

---

## 2.4 React Native 的样式系统（底层原理）

| 维度 | 内容 |
|---|---|
| 是什么 | RN 的样式是 CSS 的一个小子集：使用 Flexbox 布局，但**默认 `flexDirection` 为 `column`**、尺寸为无单位数字（密度无关逻辑像素）、通过 `StyleSheet.create` 定义且无层叠、基本不支持属性继承、不支持任何选择器 |
| 能做什么 | 用接近 CSS 的写法完成跨端布局；通过样式数组（`[styles.a, styles.b]`）实现组合与覆盖；用平台判断（`Platform.OS`）处理 iOS 阴影与 Android elevation 这类差异 |
| 怎么用 | `const styles = StyleSheet.create({ card: { flexDirection: 'row', padding: 16, borderRadius: 8 } })` → `<View style={styles.card} />`；组合样式写 `style={[styles.card, isActive && styles.active]}` |
| 原理和工作流程 | 样式对象被序列化后传给原生侧 → 原生侧把 Flexbox 属性映射为 Yoga 布局节点 → Yoga 计算出的位置与尺寸再应用到原生控件；因为不经过 CSS 引擎，所以不支持选择器、层叠与大部分继承 |
| 缺点 | 与 Web 写法差异大，从 Web 迁移时易踩坑（忘写 `flexDirection: 'row'`、给数字加 `px` 后缀、写简写属性 `margin: '10 20'`）；`flex: 1` 的语义与 Web 略有差异；阴影、圆角、字体等存在平台差异需分别处理 |

---

## 2.5 React Native 的导航与状态管理（底层原理）

| 维度 | 内容 |
|---|---|
| 是什么 | RN 不内置路由，社区标准方案是 React Navigation（`@react-navigation/native` + `@react-navigation/native-stack`）；状态管理可原样复用 React 生态方案 |
| 能做什么 | 用 `createNativeStackNavigator` 实现使用平台原生导航容器的栈式路由，转场动画与手势天然一致；用 Zustand / Jotai / Redux Toolkit / TanStack Query 管理客户端与服务端状态 |
| 怎么用 | 导航：`NavigationContainer` 包裹 `Stack.Navigator`，注册 `Stack.Screen`；状态：小规模用 `useState`/`useReducer`，中大型用 Zustand 或 Redux Toolkit，服务端状态用 TanStack Query |
| 原理和工作流程 | `native-stack` 底层使用平台原生导航容器（iOS 的 UINavigationController、Android 的 Fragment 事务），因此转场与手势不需要 JS 参与；状态管理库通过订阅粒度控制重渲染范围，避免 Context 变更导致全树重渲染 |
| 缺点 | React Navigation 依赖 `react-native-screens` 与 `react-native-safe-area-context` 等原生依赖，需要重新构建原生工程；Context 方案在高频更新场景容易引发性能问题，需改用选择器订阅 |

---

## 2.6 React Native 的热更新（底层原理）

| 维度 | 内容 |
|---|---|
| 是什么 | 在不发版的前提下仅下发 JS bundle 来更新业务逻辑，依赖"原生壳固定、JS 逻辑以 bundle 形式加载"这一运行机制 |
| 能做什么 | 快速修复线上 Bug、灰度发布新功能、绕过应用商店审核周期；**但只能更新 JS 层**，新增原生模块或修改原生配置必须发版 |
| 怎么用 | Microsoft CodePush 随 App Center 已于 2025 年 3 月 31 日退役；现行方案包括 Expo EAS Update（配合 `expo-updates`）、自建更新服务（自托管 bundle 与版本清单）、社区维护的 CodePush 分支与 `react-native-update` 等 |
| 原理和工作流程 | 应用启动时请求版本清单 → 比较当前 bundle 版本与最新版本 → 有更新则下载新 bundle 到本地 → 下次启动（或立即）加载新 bundle；服务端需维护"原生壳版本 → 兼容的 bundle 版本"映射 |
| 缺点 | iOS 对"动态下发可执行代码"有审核限制，更新内容需限定在修复 Bug 与内容更新范畴；版本兼容性管理复杂，下发不兼容的 bundle 可能导致应用崩溃；原生变更无法覆盖，仍需发版 |

---

## 2.7 Flutter 的三棵树：Widget / Element / RenderObject（底层原理）

| 维度 | 内容 |
|---|---|
| 是什么 | Flutter 渲染核心的三棵树：Widget 树是不可变的配置描述，Element 树是 Widget 的实例化节点（持有 State 与 BuildContext），RenderObject 树负责真正的布局（layout）与绘制（paint） |
| 能做什么 | 理解它是性能优化的前提：`build()` 频繁执行不是问题（Widget 只是轻量对象），真正的开销在 RenderObject 的 layout 与 paint |
| 怎么用 | 优化手段围绕"减少 RenderObject 重建与重绘"展开：给无状态组件加 `const` 构造、用 `RepaintBoundary` 隔离重绘区域、用正确的 `Key` 帮助 Element 复用、用 `AnimatedBuilder` 缩小重建范围 |
| 原理和工作流程 | `build()` 生成新 Widget 树 → 框架比对新旧 Widget，类型与 Key 相同则复用原 Element，否则重建 Element 及其 RenderObject → Element 持有 RenderObject 引用并驱动 layout → paint 生成 Layer → 合成 Scene 交给 GPU |
| 缺点 | 三棵树的概念对初学者抽象度高，容易误以为"减少 build 次数"是优化重点；`Key` 使用不当会造成状态错乱（列表重排后输入框内容串行），而 `GlobalKey` 滥用又会带来额外开销 |

---

## 2.8 Flutter 的布局约束模型（底层原理）

| 维度 | 内容 |
|---|---|
| 是什么 | 布局铁律：**Constraints go down. Sizes go up. Parent sets position.**（约束向下传递，尺寸向上汇报，位置由父级决定。）父级把自己的 `BoxConstraints`（min/max 宽高）传给子级 |
| 能做什么 | 解释并解决绝大多数布局报错：`RenderFlex overflowed`（子级超出最大约束）、`unbounded height`（把无界约束传给需要有限尺寸的子级）、`BoxConstraints forces an infinite width` 等 |
| 怎么用 | 用 `Expanded` / `Flexible` 分配剩余空间，用 `SizedBox` 给出固定尺寸，用 `ConstrainedBox` 调整约束范围；`Expanded` 只能作为 `Row`/`Column`/`Flex` 的直接子级 |
| 原理和工作流程 | 父 Widget 在 `performLayout` 中向子 Widget 传入约束 → 子 Widget 在约束内决定自身尺寸并向上汇报 → 父 Widget 依据汇报尺寸计算子级位置 → 沿树自顶向下传递约束、自底向上汇报尺寸 |
| 缺点 | 约束是"强制"的，子级不能凭空超出父级给的边界，这与 Web 中元素可以 overflow 的行为不同；`Column` 嵌套 `ListView` 时必须显式用 `Expanded` 或 `shrinkWrap`，而 `shrinkWrap: true` 会带来额外性能开销 |

---

## 2.9 Flutter 的渲染引擎：Skia 与 Impeller（底层原理）

| 维度 | 内容 |
|---|---|
| 是什么 | Skia 是通用 2D 图形库，运行时编译着色器，可能出现首次渲染的着色器编译抖动；Impeller 是为 Flutter 专门设计的引擎，**构建期预编译着色器**，支持 Metal / Vulkan 后端 |
| 能做什么 | Impeller 消除了着色器编译抖动，让首帧与复杂动画的帧率更稳定；Skia 作为长期默认引擎在跨平台成熟度上有优势 |
| 怎么用 | 新版本 Flutter 中 iOS 默认使用 Impeller，Android 端也在新版本中陆续默认启用；无需手动配置，特殊场景可通过启动参数切换 |
| 原理和工作流程 | Widget 树 → Element 树 → RenderObject 树 → Layer 树 → Scene → Impeller / Skia 生成 GPU 指令 → 平台 GPU（Metal / Vulkan / OpenGL）执行绘制；Impeller 在构建期就把着色器编译好，运行时不再触发编译 |
| 缺点 | Impeller 在部分低端设备或特定平台后端上仍在完善；自绘引擎也意味着包体积必然增大，这是无法回避的代价 |

---

## 2.10 Platform Channel：Flutter 与原生混合开发（底层原理）

| 维度 | 内容 |
|---|---|
| 是什么 | Flutter 调用原生能力的通道，包含 MethodChannel（请求-响应，最常用）、EventChannel（原生向 Dart 推送事件流）、BasicMessageChannel（双向自定义编解码），以及基于它们生成类型安全接口的 Pigeon |
| 能做什么 | 调用相机、蓝牙、系统 API 等 Flutter 未内置的原生能力；把原生侧的事件（如传感器数据、下载进度）以 Stream 形式推送给 Dart |
| 怎么用 | Dart 侧：`const MethodChannel _channel = MethodChannel('com.example.app/battery')` → `await _channel.invokeMethod<int>('getBatteryLevel')`；Android 侧：`MethodChannel(flutterEngine.dartExecutor.binaryMessenger, channelName).setMethodCallHandler { call, result -> ... }`；iOS 侧：`FlutterMethodChannel(name:binaryMessenger:)` + `setMethodCallHandler` |
| 原理和工作流程 | Dart 调用 `invokeMethod` → 消息经二进制 messenger 编码后送往原生侧 → 原生侧按方法名分发并执行 → 通过 `result.success()` 返回值或 `result.error()` 返回错误 → Dart 侧 Promise 完成，错误以 `PlatformException` 抛出 |
| 缺点 | Channel 名与方法名都是字符串，手写容易拼错且无编译期检查（复杂项目建议用 Pigeon）；消息通过内存拷贝传递，传大文件应改用共享文件路径；原生侧未实现的方法若忘记返回 `notImplemented`，Dart 侧的 `await` 会永久挂起 |

---

## 2.11 Flutter 的热重载（底层原理）

| 维度 | 内容 |
|---|---|
| 是什么 | Flutter 在 Debug 模式下提供的开发能力，包含三级：Hot Reload（保留状态）、Hot Restart（不保留状态）、Full Restart（冷启动） |
| 能做什么 | 修改代码后秒级看到效果且不丢失页面状态，极大提升 UI 调试效率；但只在 Debug 模式可用 |
| 怎么用 | 保存文件或点击闪电图标触发 Hot Reload；按 `R` 或点击重启图标触发 Hot Restart；修改原生代码、依赖或资源时需 Full Restart |
| 原理和工作流程 | Debug 模式下 Dart VM 使用 JIT，支持运行时替换方法体 → 增量编译出新 kernel 文件 → 通过 VM Service 注入运行中的 isolate → 框架触发整棵 Widget 树重新 `build()`，但 **Element 树与 State 被保留**（因此 `initState` 不会重新执行） |
| 缺点 | Release 模式使用 AOT 编译为机器码，不具备运行时替换代码的能力，这也是 Flutter 动态化能力弱于 RN 的根本原因；热重载不覆盖原生代码、依赖与资源变更 |

---

## 3.1 React Native 列表性能优化（实战应用）

| 维度 | 内容 |
|---|---|
| 是什么 | 围绕 FlatList 的一组性能优化实践：`memo` 包裹行组件、`useCallback` 固定 `renderItem` 与 `keyExtractor`、`getItemLayout` 提供固定行高、调节 `initialNumToRender` / `maxToRenderPerBatch` / `windowSize` / `removeClippedSubviews` |
| 能做什么 | 把长列表从"滚动白屏、掉帧明显"优化到流畅滚动；降低内存占用；避免因 key 不稳定导致的状态错乱 |
| 怎么用 | `getItemLayout={(_, index) => ({ length: ROW_HEIGHT, offset: ROW_HEIGHT * index, index })}`；`keyExtractor` 使用业务唯一 ID；行组件用 `React.memo` 包裹；超长列表可换用 FlashList |
| 原理和工作流程 | `getItemLayout` 让 FlatList 无需测量即可直接计算滚动位置与可见区间，省掉大量布局计算 → 固定引用的 `renderItem` 让 `memo` 生效，避免所有行跟着父级重渲染 → `windowSize` 控制渲染窗口，`removeClippedSubviews` 移除屏幕外原生视图以降低内存 |
| 缺点 | 参数需要按行高与内容复杂度调优，`initialNumToRender` 太小会白屏、太大拖慢首屏；`removeClippedSubviews` 在部分 Android 机型上可能引发内容闪烁 |

---

## 3.2 React Native 原生模块（TurboModule）（实战应用）

| 维度 | 内容 |
|---|---|
| 是什么 | 新架构下推荐的原生模块开发方式：先写 TS 规范文件声明接口，由 Codegen 生成原生侧接口，原生实现后注册到 PackageList |
| 能做什么 | 让 JS 侧以类型安全的方式调用原生能力，并支持同步调用（JSI）；模块按需加载，避免启动时全部初始化 |
| 怎么用 | 规范文件：`export interface Spec extends TurboModule { getDeviceModel(): string; getBatteryLevel(): Promise<number> }` 并 `export default TurboModuleRegistry.getEnforcing<Spec>('NativeDeviceInfo')`；JS 侧：`NativeDeviceInfo.getDeviceModel()`（同步）/ `await NativeDeviceInfo.getBatteryLevel()`（异步） |
| 原理和工作流程 | 编写 TS 规范 → 构建时 Codegen 生成 Android 的 Java/Kotlin 抽象类与 iOS 的 Objective-C++ 协议 → 原生侧按签名实现并注册 → 运行时 JS 通过 JSI 直接调用原生对象，同步方法立即返回，异步方法返回 Promise |
| 缺点 | 原生实现必须严格匹配生成的签名，迁移旧版 NativeModules 有一定成本；新增或修改原生模块后**无法热更新**，必须重新发版 |

---

## 3.3 Flutter 状态管理（Riverpod）（实战应用）

| 维度 | 内容 |
|---|---|
| 是什么 | 以 Riverpod 2.x 为例的状态管理实践：用 `NotifierProvider` + `Notifier` 管理可变状态，用 `ConsumerWidget` 消费状态 |
| 能做什么 | 实现编译期安全、无 `BuildContext` 依赖、易于测试的状态管理；通过 `ref.watch` 订阅、`ref.read` 单次读取，精确控制重建范围 |
| 怎么用 | 定义：`final counterProvider = NotifierProvider<CounterNotifier, int>(CounterNotifier.new)`，`class CounterNotifier extends Notifier<int> { int build() => 0; void increment() => state++ }`；消费：`final count = ref.watch(counterProvider)`，触发：`ref.read(counterProvider.notifier).increment()` |
| 原理和工作流程 | Provider 首次被读取时调用 `build()` 生成初始状态 → `ref.watch` 在 Element 上注册依赖 → `state` 变化时只通知订阅该 Provider 的 Widget 重建 → 未订阅的 Widget 不受影响，避免全树重渲染 |
| 缺点 | 概念比 Provider 多（Provider / Notifier / Ref / Consumer），初学者需要适应期；API 在不同大版本间有调整，升级时需注意迁移指南；小项目使用可能显得过重 |

---

## 3.4 Flutter 与原生混合开发要点（实战应用）

| 维度 | 内容 |
|---|---|
| 是什么 | 使用 Platform Channel 与原生代码协作时的五条工程实践：Channel 命名规范、错误必须显式返回、大数据分片传输、耗时操作不阻塞主线程、优先使用 Pigeon |
| 能做什么 | 让混合开发的接口稳定可靠：避免 Dart 侧 `await` 永久挂起、避免传输大文件时内存暴涨、避免原生耗时操作导致界面卡顿 |
| 怎么用 | Channel 名用反向域名风格（`com.example.app/battery`）并在两侧完全一致；原生侧未实现的方法显式调用 `result.notImplemented()`；大文件只传路径不传字节数组；Android 侧耗时操作切到后台线程；复杂项目用 Pigeon 生成类型安全接口 |
| 原理和工作流程 | 消息经二进制 messenger 编码传输，涉及内存拷贝 → 因此大数据的传输成本高，应改为传引用（路径）→ 原生侧的耗时逻辑若跑在主线程会阻塞 UI 渲染 → 未返回 `notImplemented` 时 Dart 侧永远等不到结果 |
| 缺点 | 混合开发的调试链路跨 Dart 与原生两侧，排查问题需要同时看两端日志；原生侧代码无法热重载，每次改动都要重新编译运行 |

---

> [返回原文](./06-ReactNative与Flutter.md) | [返回模块目录](../README.md) | [返回知识导览](../知识导览.md)
