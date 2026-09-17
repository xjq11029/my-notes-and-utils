> 模块：12-cross-platform（拓展 跨端开发）
> 难度：★★★★ 原理进阶
> 前置知识：React 基础、Vue 基础、移动端渲染常识

---

# 06-ReactNative与Flutter

---

## 一、核心概念

### 1.1 三条技术路线的本质区别

React Native、Flutter 与 uniapp 分别代表三种截然不同的跨端思路。理解它们的区别，关键要问一个问题：**屏幕上的像素最终由谁绘制？**

| 路线 | 代表 | 谁绘制像素 | 跨端一致性来源 | 原生能力获取方式 |
|---|---|---|---|---|
| **WebView 容器** | uniapp（App 端 Vue 页面）、Cordova | 系统 WebView 的浏览器内核 | 依赖浏览器内核版本，一致性一般 | 框架封装的桥接 API |
| **原生组件映射** | React Native | 平台原生控件（UIView / android.view） | 依赖各平台原生控件，一致性中等 | JS 调用原生模块（Bridge / JSI） |
| **自绘引擎** | Flutter | Flutter 自带的渲染引擎（Skia / Impeller） | 引擎自绘，一致性极高 | Platform Channel 调用原生 |

**这个区别带来的三个直接后果：**

1. **一致性**：Flutter 最强（自己画，不受平台控件影响），RN 中等（用原生控件，外观随系统变化），WebView 类最弱
2. **性能天花板**：Flutter 最高（渲染管线完全自控），RN 次之（受 JS 与原生通信开销影响），WebView 类受限于 Web 渲染性能
3. **原生感**：RN 最强（用的就是原生控件，滚动、键盘、无障碍等行为天然一致），Flutter 需自行模拟，WebView 类最弱

### 1.2 React Native 是什么

React Native（简称 RN）是 Meta 开源的跨端框架，核心理念是 **"Learn once, write anywhere"**——用 React 的组件化思维与声明式 UI 写代码，最终渲染为平台原生控件。

1. **React 语法复用**：组件、Hooks、状态管理（Redux/Zustand/Jotai）几乎可以原样复用
2. **原生控件渲染**：`<View>` 映射为 `UIView` / `android.view.View`，`<Text>` 映射为 `UILabel` / `TextView`
3. **JS 与原生双线程**：JS 线程执行 React 逻辑，UI 线程负责真实渲染，二者通过通信层交换数据
4. **样式为 CSS 子集**：使用 Flexbox 布局，但只支持部分 CSS 属性，写法与 Web 差异显著
5. **可热更新**：JS 代码以 bundle 形式下发，可在不发版的前提下更新业务逻辑

### 1.3 Flutter 是什么

Flutter 是 Google 开源的跨端框架，使用 **Dart 语言 + 自绘渲染引擎**，一套代码可运行在 iOS、Android、Web、桌面与嵌入式设备上。

1. **自带渲染引擎**：UI 由 Flutter 自己绘制，不依赖平台原生控件，各平台表现高度一致
2. **一切皆 Widget**：布局、样式、动画、手势全部由 Widget 组合表达，没有单独的样式表
3. **声明式 UI + 状态驱动**：`setState` 或状态管理库驱动 `build()` 重新执行，框架负责最小化重建
4. **AOT 编译为机器码**：Release 模式下 Dart 编译为原生机器码，无解释器与 JIT 开销
5. **热重载**：Debug 模式下修改代码可在秒级看到效果，且保留应用状态

### 1.4 与 uniapp 的定位差异

| 对比项 | uniapp | React Native | Flutter |
|---|---|---|---|
| 主战场 | 国内小程序 + App + H5 | 海外 iOS/Android 双端 App | 全平台高性能应用 |
| 语言 | Vue（JS/TS） | React（JS/TS） | Dart |
| 渲染方式 | WebView / 小程序渲染层 | 映射原生控件 | 自绘引擎 |
| 包体积增量 | 小 | 中 | 大 |
| 动态化能力 | 强（H5 与小程序本身即动态） | 强（JS bundle 可热更新） | 弱（AOT 机器码无法热更新） |
| 生态重心 | 国内小程序生态 | npm 与原生社区 | pub.dev 与官方组件库 |

### 1.5 RN vs Flutter vs uniapp 三方对比

| 对比维度 | uniapp | React Native | Flutter |
|---|---|---|---|
| **渲染机制** | App 端 WebView 渲染（或 nvue 原生渲染）；小程序端双线程 + 同层渲染 | JS 逻辑驱动，映射为平台原生控件 | 自绘引擎直接绘制，不使用平台控件 |
| **语言与生态** | Vue（JS/TS），可复用 Vue 生态与国内小程序生态 | React（JS/TS），可复用 npm 与 React 生态 | Dart，生态独立（pub.dev），无法复用前端 npm 生态 |
| **性能表现** | 中；小程序端受 setData 与双线程通信限制 | 高；旧架构受 Bridge 瓶颈，新架构显著改善 | 极高；无跨线程通信开销，高刷场景帧率最稳 |
| **包体积** | 增量最小；H5 几 MB，App 包 20MB 起 | 中；需内置 Hermes 与原生依赖 | 最大；需内置渲染引擎，Android 包增量通常 10MB+ |
| **动态化能力** | 最强；H5 与小程序天然动态，App 端也有成熟的 wgt 热更新 | 强；JS bundle 可热更新 | 弱；Release 为 AOT 机器码，无法热更新业务逻辑 |
| **团队适配成本** | 最低；会 Vue 即可上手 | 中；需理解 RN 样式差异、原生构建链路与双端调试 | 最高；需新学 Dart 与声明式 Widget 思维 |
| **典型选型场景** | 国内小程序矩阵、To C 业务、快速多端交付 | 海外双端 App、需原生观感与热更新 | 强 UI 一致性、高性能图形动画、需覆盖桌面与嵌入式 |

**三方对比的读法：** 一致性 vs 原生感是核心矛盾；包体积与性能正相关（想要 Flutter 级别的性能就得内置渲染引擎）；动态化能力与编译方式强相关（JIT/解释执行才能热更新，AOT 不能）。

---

## 二、底层原理

### 2.1 React Native 的 Bridge 通信机制与瓶颈

旧架构下 RN 有三条线程，它们之间**只能通过 Bridge 通信**：

| 线程 | 职责 |
|---|---|
| **JS 线程** | 执行 React 组件逻辑、业务代码、状态计算 |
| **Shadow 线程** | 用 Yoga 引擎计算 Flexbox 布局，生成"影子树" |
| **UI（Main）线程** | 执行原生渲染与用户交互，是唯一能操作原生控件的线程 |

**Bridge 的三个致命特性：**

1. **异步**——JS 调用原生方法时不能立即拿到返回值，只能通过回调或 Promise
2. **批量**——消息在事件循环末尾被打包成一批统一发送，降低了通信频次但也增加了延迟
3. **序列化**——跨线程传输的数据必须序列化为 JSON 字符串，大对象或频繁通信会产生显著开销

**一次点击的完整链路：** UI 线程捕获交互 → 序列化后异步送往 JS 线程 → JS 执行 `setState` 并 diff → 把更新指令序列化回传 → Shadow 线程用 Yoga 计算布局 → UI 线程更新原生控件。每一跳都有序列化与事件循环延迟。

**由此产生的典型瓶颈：** 快速滚动列表时白屏（每帧都要跨越 Bridge 传递大量数据，通信队列积压）；手势驱动的动画卡顿（动画每帧都要 JS 计算后回传，无法稳定 60fps）；大数据量 setState 抖动（序列化成本随数据量线性增长）。

### 2.2 JSI 与 Fabric：新架构的解法

新架构用 **JSI + TurboModules + Fabric + Codegen** 替换掉 Bridge。**React Native 0.76（2024 年 10 月）起，新架构成为默认配置**，Bridgeless 模式也默认开启。

| 组件 | 替代对象 | 解决的问题 |
|---|---|---|
| **JSI**（JavaScript Interface） | Bridge 本身 | 用 C++ 层让 JS 直接持有原生对象引用，支持**同步调用**，无需 JSON 序列化 |
| **TurboModules** | 旧版 NativeModules | 原生模块按需加载（而非启动时全部初始化），并通过 Codegen 生成类型安全接口 |
| **Fabric** | 旧版渲染器 | C++ 实现影子树，布局计算更高效，支持**同步布局**与并发渲染 |
| **Codegen** | 手写桥接代码 | 在构建期从 TS 类型定义生成原生接口代码，保证两侧类型一致 |

```text
新架构通信流程：

  UI 线程  ◄──── C++ 层（JSI / Fabric 影子树）────►  JS 线程
             同步调用、无 JSON 序列化、共享内存对象
```

**JSI 的核心价值：** JS 可持有一个指向 C++ 宿主对象（HostObject）的引用，像调用普通 JS 对象一样调用它；调用是**同步**的，可在同一帧内完成"读取原生值 → 计算 → 更新 UI"；数据不再强制序列化，大对象（如图片缓冲区）可直接共享内存。

**Fabric 的核心价值：** 影子树用 C++ 实现，JS 线程与 UI 线程可同时访问，省掉一次跨线程拷贝；支持同步布局，解决旧架构下"先测量再渲染"导致的跳变；为 React 18 的并发特性铺路。

### 2.3 Hermes 引擎

Hermes 是 Meta 为 RN 定制的 JavaScript 引擎，**自 RN 0.70 起成为默认引擎**。

| 对比项 | JSC（JavaScriptCore） | Hermes |
|---|---|---|
| 执行方式 | 运行时解析 + JIT | 构建时预编译为字节码 |
| 启动速度 | 较慢（需解析与编译） | 更快（直接加载字节码） |
| 内存占用 | 较高 | 明显更低 |
| APK 体积 | 较大 | 更小（字节码可裁剪） |
| 极端计算性能 | 略优（有 JIT） | 略弱（无 JIT） |

**Hermes 的取舍：** 放弃 JIT 换取启动速度与内存占用。移动端应用的瓶颈通常在启动与内存，而非长时间的高强度计算；真正需要重计算的部分应交给原生模块或用 C++ 编写。

### 2.4 React Native 的样式系统

| 维度 | Web CSS | React Native |
|---|---|---|
| 布局模型 | 默认 `display: block`，需显式开启 Flex | **默认就是 Flex，且 `flexDirection` 默认为 `column`** |
| 单位 | `px` / `em` / `rem` / `%` | 数字（逻辑像素，密度无关），不支持 `px` 后缀 |
| 样式复用 | 类选择器 + 层叠 | `StyleSheet.create` + 数组组合，**无层叠** |
| 继承 | 大部分属性可继承 | 基本不可继承（`Text` 嵌套 `Text` 例外） |
| 选择器 | 完整支持 | 不支持任何选择器 |
| 简写 | `margin: 10px 20px` | 必须写 `marginTop`、`marginHorizontal` 等具体属性 |

```jsx
import React from 'react';
import { View, Text, StyleSheet } from 'react-native';

export default function UserCard({ name, email }) {
  return (
    <View style={styles.card}>
      <Text style={styles.name}>{name}</Text>
      <Text style={styles.email}>{email}</Text>
    </View>
  );
}

const styles = StyleSheet.create({
  card: {
    // 注意：RN 默认 flexDirection 为 'column'，与 Web 的 'row' 相反
    flexDirection: 'column',
    padding: 16,
    marginHorizontal: 12,
    borderRadius: 8,
    backgroundColor: '#ffffff',
    // 阴影是平台差异最大的样式之一：
    // iOS 用 shadowColor / shadowOffset / shadowOpacity / shadowRadius，Android 用 elevation
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 3,
  },
  name: { fontSize: 18, fontWeight: '600', color: '#333333' },
  email: { marginTop: 6, fontSize: 14, color: '#888888' },
});
```

### 2.5 React Native 的导航与状态管理

**导航**：RN 不内置路由，社区标准方案是 **React Navigation**。

```bash
pnpm add @react-navigation/native @react-navigation/native-stack
pnpm add react-native-screens react-native-safe-area-context
```

```jsx
import { NavigationContainer } from '@react-navigation/native';
import { createNativeStackNavigator } from '@react-navigation/native-stack';

const Stack = createNativeStackNavigator();

export default function App() {
  return (
    <NavigationContainer>
      {/* native-stack 使用平台原生导航容器，转场动画与手势天然一致 */}
      <Stack.Navigator initialRouteName="Home">
        <Stack.Screen name="Home" component={HomeScreen} options={{ title: '首页' }} />
        <Stack.Screen name="Detail" component={DetailScreen} options={{ title: '详情' }} />
      </Stack.Navigator>
    </NavigationContainer>
  );
}
```

**状态管理**：RN 可以**原样复用** React 生态的方案。

| 方案 | 适用规模 | 说明 |
|---|---|---|
| `useState` / `useReducer` | 组件内部 | 无需额外依赖 |
| Context + `useReducer` | 中小型、低频更新 | Context 变更会导致所有消费者重渲染 |
| Zustand / Jotai | 中大型 | 轻量、无 Provider 嵌套、选择器订阅粒度细 |
| Redux Toolkit | 大型、需要严格数据流 | 生态最成熟，样板代码已被 RTK 大幅削减 |
| TanStack Query | 服务端状态为主 | 缓存、重试、失效策略开箱即用 |

### 2.6 React Native 的热更新

热更新指**不发版、仅下发 JS bundle** 更新业务逻辑，依赖"原生壳固定、JS 逻辑以 bundle 形式加载"这一机制。

| 方案 | 状态 | 说明 |
|---|---|---|
| Microsoft CodePush | 已停止 | 随 App Center 于 2025 年 3 月 31 日退役 |
| Expo EAS Update | 可用 | Expo 生态的官方方案，与 `expo-updates` 配合 |
| 自建更新服务 | 可用 | 自行托管 bundle 与版本清单，配合 `react-native-update` 等库 |
| 社区维护的 CodePush 分支 | 可用 | 部分社区版本仍在维护，需自行评估稳定性 |

**三个技术要点：**

1. **只更新 JS 层**——原生代码（新增原生模块、修改原生配置）的变更必须发版
2. **版本兼容性**——下发的 bundle 必须与当前原生壳接口兼容，需维护"原生版本 → bundle 版本"映射
3. **合规风险**——iOS 对"动态下发可执行代码"有审核限制，更新内容需限定在修复 Bug 与内容更新范畴

### 2.7 Flutter 的三棵树：Widget / Element / RenderObject

| 树 | 是什么 | 生命周期 | 是否可复用 |
|---|---|---|---|
| **Widget 树** | 不可变的配置描述（"我想要一个什么样的 UI"） | 每次 `build()` 都重新创建，极其廉价 | 否，每次都新建 |
| **Element 树** | Widget 在树中的实例化节点，持有 State 与 BuildContext | 相对稳定，仅在 Widget 类型/Key 变化时重建 | 是，框架通过它做 diff |
| **RenderObject 树** | 真正负责布局（layout）与绘制（paint）的对象 | 稳定，只有布局或绘制属性变化时才更新 | 是，最重的一层 |

```text
build() 执行
    │
    ▼
Widget 树（不可变配置，频繁重建）
    │  框架比对新旧 Widget
    ▼
Element 树（复用判断：类型与 Key 相同则复用，否则重建）
    │  Element 持有 RenderObject 的引用
    ▼
RenderObject 树（执行 layout → paint → composite，最终出像素）
```

**关键结论：** `build()` 频繁执行**不是问题**，Widget 只是轻量配置对象；真正的开销在 **RenderObject 的 layout 与 paint**，优化方向是"减少布局范围、避免重复布局"；`const` 构造函数让框架识别出"配置没变"从而跳过 Element 重建；`Key` 的作用是帮助 Element 树正确复用节点。

### 2.8 Flutter 的布局约束模型

> **Constraints go down. Sizes go up. Parent sets position.**
> （约束向下传递，尺寸向上汇报，位置由父级决定。）

1. 父 Widget 把自己的 `BoxConstraints`（最小/最大宽高）传给子 Widget
2. 子 Widget 在约束允许的范围内决定自己的尺寸，并向上汇报
3. 父 Widget 根据子 Widget 汇报的尺寸，决定把它放在哪个位置

```dart
// 布局约束示例：理解 Expanded 与 mainAxisSize
class LayoutDemo extends StatelessWidget {
  const LayoutDemo({super.key});

  @override
  Widget build(BuildContext context) {
    return Column(
      // mainAxisSize 控制 Column 在主轴方向占多少空间
      // max（默认）占满父级可用高度，min 则只包裹子级
      mainAxisSize: MainAxisSize.max,
      children: [
        // Expanded 的本质是：在主轴方向把剩余空间按 flex 比例分配
        // 它会给子 Widget 传入一个"必须占满分配空间"的紧约束
        Expanded(
          flex: 2,
          child: Container(color: Colors.blue, child: const Center(child: Text('占 2 份剩余空间'))),
        ),
        Expanded(
          flex: 1,
          child: Container(color: Colors.orange, child: const Center(child: Text('占 1 份剩余空间'))),
        ),
        // SizedBox 直接给出固定尺寸，会覆盖父级的松约束
        const SizedBox(height: 60, child: Center(child: Text('固定高度 60'))),
      ],
    );
  }
}
```

| 错误现象 | 根本原因 |
|---|---|
| `RenderFlex overflowed by xx pixels` | 子 Widget 在主轴方向超出了父级给出的最大约束 |
| `Vertical viewport was given unbounded height` | `Column` 内嵌 `ListView` 时，ListView 拿到了无界高度约束 |
| `BoxConstraints forces an infinite width` | 把无界约束（如 `double.infinity`）传给了需要有限尺寸的子级 |
| `Expanded` 用错位置 | `Expanded` 只能放在 `Row`/`Column`/`Flex` 的直接子级中 |

### 2.9 Flutter 的渲染引擎：Skia 与 Impeller

| 引擎 | 特点 | 现状 |
|---|---|---|
| **Skia** | 通用 2D 图形库，跨平台成熟稳定；运行时编译着色器，可能出现首次渲染卡顿（着色器编译抖动） | 长期作为默认引擎 |
| **Impeller** | 为 Flutter 专门设计，**构建期预编译着色器**，消除着色器编译抖动；支持 Metal / Vulkan 后端 | iOS 上自 Flutter 3.10 起默认启用，Android 端也在新版本中陆续默认启用 |

**渲染管线：** Widget 树 → Element 树 → RenderObject 树 → Layer 树 → Scene → Impeller / Skia 生成 GPU 指令 → 平台 GPU（Metal / Vulkan / OpenGL）执行绘制。

**为什么 Flutter 性能好：** 无跨线程通信开销（渲染与业务逻辑同在 Dart isolate）；自绘带来一致性，避免平台控件差异的适配成本；AOT 编译为机器码，无解释器与 JIT 开销；UI 线程与光栅线程分工明确，配合 Impeller 的预编译着色器可稳定跑满高刷。

### 2.10 Platform Channel：Flutter 与原生混合开发

| Channel 类型 | 用途 | 通信模式 |
|---|---|---|
| **MethodChannel** | 最常用，方法调用 | 请求-响应（异步） |
| **EventChannel** | 原生向 Dart 持续推送事件流 | 流式（Stream） |
| **BasicMessageChannel** | 双向消息传递，可自定义编解码 | 双向 |
| **Pigeon** | 代码生成工具，基于以上 Channel 生成类型安全接口 | 推荐用于复杂项目 |

```dart
// ============ Dart 侧：定义并调用 Channel ============
import 'package:flutter/services.dart';

class BatteryService {
  // Channel 名必须与原生侧完全一致，通常用反向域名风格
  static const MethodChannel _channel = MethodChannel('com.example.app/battery');

  static Future<int> getBatteryLevel() async {
    try {
      final int? level = await _channel.invokeMethod<int>('getBatteryLevel');
      return level ?? -1;
    } on PlatformException catch (e) {
      // 原生侧通过 result.error() 返回的错误会以 PlatformException 抛出
      throw Exception('获取电量失败：${e.message}');
    } on MissingPluginException {
      // 原生侧未实现该 Channel 时抛出
      throw Exception('当前平台未实现电量获取');
    }
  }
}
```

```kotlin
// ============ Android 侧（Kotlin）：实现 Channel ============
class MainActivity : FlutterActivity() {
    private val channelName = "com.example.app/battery"

    override fun configureFlutterEngine(flutterEngine: FlutterEngine) {
        super.configureFlutterEngine(flutterEngine)
        MethodChannel(flutterEngine.dartExecutor.binaryMessenger, channelName)
            .setMethodCallHandler { call, result ->
                if (call.method == "getBatteryLevel") {
                    val level = getBatteryLevel()
                    // 成功用 result.success()，失败用 result.error()（Dart 侧抛 PlatformException）
                    if (level != -1) result.success(level)
                    else result.error("UNAVAILABLE", "电量信息不可用", null)
                } else {
                    // 未实现的方法必须返回 notImplemented，否则 Dart 侧会一直等待
                    result.notImplemented()
                }
            }
    }

    private fun getBatteryLevel(): Int {
        val manager = getSystemService(Context.BATTERY_SERVICE) as BatteryManager
        return manager.getIntProperty(BatteryManager.BATTERY_PROPERTY_CAPACITY)
    }
}
```

```swift
// ============ iOS 侧（Swift）：实现 Channel ============
@main
@objc class AppDelegate: FlutterAppDelegate {
  override func application(
    _ application: UIApplication,
    didFinishLaunchingWithOptions launchOptions: [UIApplication.LaunchOptionsKey: Any]?
  ) -> Bool {
    let controller = window?.rootViewController as! FlutterViewController
    let channel = FlutterMethodChannel(
      name: "com.example.app/battery",
      binaryMessenger: controller.binaryMessenger
    )
    channel.setMethodCallHandler { call, result in
      if call.method == "getBatteryLevel" {
        let level = self.getBatteryLevel()
        if level != -1 { result(level) }
        else { result(FlutterError(code: "UNAVAILABLE", message: "电量信息不可用", details: nil)) }
      } else {
        result(FlutterMethodNotImplemented)
      }
    }
    GeneratedPluginRegistrant.register(with: self)
    return super.application(application, didFinishLaunchingWithOptions: launchOptions)
  }
}
```

### 2.11 Flutter 的热重载

| 能力 | 触发方式 | 保留状态 | 适用场景 |
|---|---|---|---|
| **Hot Reload** | 保存文件 / 点击闪电图标 | 是 | 调整 UI、样式、业务逻辑 |
| **Hot Restart** | `R` 键 / 重启图标 | 否 | 修改 `main()`、全局变量初始化 |
| **Full Restart** | 停止后重新运行 | 否 | 修改原生代码、依赖、资源 |

**热重载的原理：** Debug 模式下 Dart VM 使用 **JIT**，支持运行时替换方法体 → 增量编译出新 kernel 文件，通过 VM Service 注入运行中的 isolate → 框架触发整棵 Widget 树的 `build()` 重新执行，**Element 树与 State 被保留**（因此 `initState` 不会重新执行）。Release 模式使用 AOT 编译为机器码，不具备运行时替换代码的能力，这也是 Flutter 动态化能力弱于 RN 的根本原因。

---

## 三、实战应用

### 3.1 React Native 列表性能优化

```jsx
import React, { useCallback, memo } from 'react';
import { FlatList, View, Text, StyleSheet } from 'react-native';

const ROW_HEIGHT = 72;

// 1. 用 memo 包裹行组件，避免父级重渲染时所有行跟着重渲染
const ItemRow = memo(function ItemRow({ item }) {
  return (
    <View style={styles.row}>
      <Text style={styles.title}>{item.title}</Text>
      <Text style={styles.subtitle}>{item.subtitle}</Text>
    </View>
  );
});

export default function MessageList({ data }) {
  // 2. keyExtractor 必须稳定且唯一，避免用数组下标
  const keyExtractor = useCallback((item) => item.id, []);
  // 3. renderItem 用 useCallback 固定引用，否则 memo 优化失效
  const renderItem = useCallback(({ item }) => <ItemRow item={item} />, []);
  // 4. getItemLayout 提供固定行高，让 FlatList 无需测量即可计算滚动位置
  //    这是长列表滚动流畅度的关键优化
  const getItemLayout = useCallback(
    (_, index) => ({ length: ROW_HEIGHT, offset: ROW_HEIGHT * index, index }),
    []
  );

  return (
    <FlatList
      data={data}
      keyExtractor={keyExtractor}
      renderItem={renderItem}
      getItemLayout={getItemLayout}
      // 首屏渲染条数：太小会白屏，太大会拖慢首屏
      initialNumToRender={10}
      // 每批渲染条数：影响滚动时的填充速度
      maxToRenderPerBatch={10}
      // 渲染窗口大小（以"屏"为单位）：越小内存越省，越大越不容易白屏
      windowSize={5}
      // 移除屏幕外的原生视图，降低内存占用（Android 上效果更明显）
      removeClippedSubviews
    />
  );
}

const styles = StyleSheet.create({
  row: { height: ROW_HEIGHT, paddingHorizontal: 16, justifyContent: 'center' },
  title: { fontSize: 16, fontWeight: '500' },
  subtitle: { fontSize: 13, color: '#888', marginTop: 4 },
});
```

| 优化方向 | 手段 |
|---|---|
| 列表 | `FlatList` / `SectionList` 替代 `ScrollView`；超长列表用 `FlashList` |
| 图片 | `expo-image` 或 `react-native-fast-image` 替代内置 `Image`，启用缓存与占位图 |
| 动画 | `Animated` 的 `useNativeDriver: true`（仅支持 `transform` 与 `opacity`）；复杂动画用 `react-native-reanimated` 在 UI 线程执行 |
| 重渲染 | `React.memo`、`useCallback`、`useMemo`；避免在 `renderItem` 内创建新对象或匿名函数 |
| 长任务 | 用 `InteractionManager.runAfterInteractions` 把非关键任务推迟到动画结束后 |

### 3.2 React Native 原生模块（TurboModule）

新架构下推荐用 **Codegen + TurboModule 规范**编写原生模块，以获得类型安全与按需加载。

```ts
// specs/NativeDeviceInfo.ts —— TS 规范文件，Codegen 据此生成原生接口
import type { TurboModule } from 'react-native';
import { TurboModuleRegistry } from 'react-native';

export interface Spec extends TurboModule {
  getDeviceModel(): string;              // 同步方法：新架构下 JSI 支持同步调用
  getBatteryLevel(): Promise<number>;    // 异步方法：返回 Promise
}

// getEnforcing 表示模块必须存在，缺失时直接报错而非返回 null
export default TurboModuleRegistry.getEnforcing<Spec>('NativeDeviceInfo');
```

```jsx
import NativeDeviceInfo from './specs/NativeDeviceInfo';

const model = NativeDeviceInfo.getDeviceModel();         // 同步调用
const level = await NativeDeviceInfo.getBatteryLevel();  // 异步调用
```

> 原生实现（Android 的 Kotlin/Java 类、iOS 的 Objective-C++ 类）需按 Codegen 生成的接口签名实现并注册到 `PackageList`。**新增原生模块后无法热更新，必须重新发版。**

### 3.3 Flutter 状态管理（Riverpod）

以 Riverpod 2.x 为例，用 `Notifier` 管理可变的业务状态。

```dart
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

// 声明全局 Provider：状态类型为 int，由 CounterNotifier 管理
final counterProvider = NotifierProvider<CounterNotifier, int>(CounterNotifier.new);

class CounterNotifier extends Notifier<int> {
  // build() 返回初始状态，Provider 首次被读取时调用
  @override
  int build() => 0;

  void increment() => state++;
}

class CounterView extends ConsumerWidget {
  const CounterView({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    // ref.watch：订阅状态变化，状态更新时本 Widget 重建
    final count = ref.watch(counterProvider);

    return Column(
      mainAxisAlignment: MainAxisAlignment.center,
      children: [
        Text('计数：$count'),
        ElevatedButton(
          // ref.read：只读取当前值、不订阅，适合在回调中使用
          onPressed: () => ref.read(counterProvider.notifier).increment(),
          child: const Text('加一'),
        ),
      ],
    );
  }
}
```

| 方案 | 心智模型 | 学习曲线 | 适用场景 |
|---|---|---|---|
| **Provider** | 官方推荐的轻量方案，基于 `InheritedWidget` | 低 | 中小型项目、初学者 |
| **Riverpod** | Provider 的重构版，编译期安全、无 `BuildContext` 依赖 | 中 | 中大型项目、需要良好可测试性 |
| **Bloc** | 事件驱动 + 状态流，`Event → Bloc → State` | 高 | 大型项目、业务复杂、团队规范要求高 |

### 3.4 Flutter 与原生混合开发的五条实践

1. **Channel 命名规范**——使用反向域名风格（如 `com.example.app/battery`），Dart 与原生两侧保持一致
2. **错误必须显式返回**——原生侧未实现的方法要调用 `result.notImplemented()`，否则 Dart 侧会一直等待
3. **大数据传输要分片**——Platform Channel 的消息通过内存拷贝传递，大文件应改用共享文件路径而非直接传字节数组
4. **耗时操作不要阻塞主线程**——Android 侧应切到后台线程，iOS 侧注意不要阻塞主线程
5. **优先使用 Pigeon**——手写 Channel 字符串容易拼错且无类型检查，复杂项目建议用 Pigeon 生成类型安全接口

---

## 四、常见面试题

**Q1：React Native 的 Bridge 为什么是性能瓶颈？新架构如何解决？**

**答案要点：**

- 旧架构有三条线程（JS、Shadow、UI），只能通过 Bridge 通信，而 Bridge 具备**异步、批量、序列化**三个特性
- 异步导致无法在同一帧内完成"读取原生值 → 计算 → 更新 UI"；序列化导致大对象传输开销随数据量线性增长
- 新架构用 **JSI** 替换 Bridge：C++ 层让 JS 直接持有原生对象引用，支持同步调用且无需 JSON 序列化
- 配套改造：**TurboModules** 实现原生模块按需加载与类型安全，**Fabric** 用 C++ 实现影子树并支持同步布局，**Codegen** 在构建期生成两侧接口代码
- RN 0.76 起新架构（含 Bridgeless 模式）成为默认配置

**Q2：Hermes 引擎的取舍是什么？为什么 RN 选择放弃 JIT？**

**答案要点：**

- Hermes 在**构建期**把 JS 预编译为字节码，运行时直接加载，省去解析与编译阶段
- 收益：启动更快、内存占用更低、APK 体积更小
- 代价：没有 JIT，长时间高强度计算的性能弱于 JSC
- 取舍依据：移动端瓶颈通常在启动速度与内存占用，而非持续重计算；真正的重计算应下沉到原生模块或用 C++ 实现
- Hermes 自 RN 0.70 起成为默认引擎

**Q3：Flutter 的三棵树分别是什么？为什么 `build()` 频繁执行不是性能问题？**

**答案要点：**

- Widget 树：不可变的配置描述，每次 `build()` 都重建，但只是轻量对象，创建成本极低
- Element 树：Widget 的实例化节点，持有 State 与 BuildContext，是框架做复用判断的依据
- RenderObject 树：真正负责 layout 与 paint 的对象，是最重的一层
- 框架比对新旧 Widget，若类型与 Key 相同则复用原 Element，从而避免 RenderObject 重建
- 因此优化重点是减少 RenderObject 的布局与重绘范围，而非减少 `build()` 调用次数

**Q4：请解释 Flutter 的布局约束模型，并说明 `Expanded` 的原理。**

**答案要点：**

- 核心口诀：**约束向下传递，尺寸向上汇报，位置由父级决定**
- 父 Widget 把 `BoxConstraints`（min/max 宽高）传给子 Widget，子 Widget 在约束内决定尺寸并向上汇报
- `Expanded` 的本质是在主轴方向按 `flex` 比例分配**剩余空间**，并给子 Widget 传入"必须占满分配空间"的紧约束
- `Expanded` 只能作为 `Row`/`Column`/`Flex` 的直接子级
- 常见错误：`RenderFlex overflowed`（子级超出最大约束）、`unbounded height`（把无界约束传给需要有限尺寸的子级）

**Q5：Flutter 的性能为什么比 React Native 好？它的代价是什么？**

**答案要点：**

- 优势来源：无跨线程通信开销（渲染与业务逻辑同在 Dart isolate）、自绘引擎保证一致性、AOT 编译为机器码、Impeller 预编译着色器消除首帧抖动
- 代价一：**包体积大**——需内置渲染引擎，Android 包体积增量通常 10MB 以上
- 代价二：**动态化能力弱**——Release 是 AOT 机器码，无法像 RN 那样热更新业务逻辑
- 代价三：**需要学 Dart**——语言与生态都是新增成本，无法复用前端 npm 生态
- 代价四：**原生感需自行模拟**——滚动回弹、键盘行为、无障碍语义等需要额外适配

**Q6：RN 与 Flutter 分别适合什么样的团队和项目？**

**答案要点：**

- 团队已有 React 积累、需要复用 Web 生态、要求原生控件观感与热更新能力 → 选 RN
- 团队愿意投入学习 Dart、要求极致 UI 一致性与高性能、包体积不是硬约束 → 选 Flutter
- 项目以国内小程序为主战场 → 选 uniapp / Taro
- 项目需要覆盖桌面与嵌入式设备 → Flutter 的多端能力更成熟
- 关键判断点：**是否愿意接受一门新语言**，以及**包体积与动态化能力哪个更重要**

---

## 五、避坑指南

| 常见错误 | 现象 | 原因 | 解决方案 |
|---|---|---|---|
| 按 Web 习惯写 RN 样式，忘记 `flexDirection` 默认值 | 横向布局写不出来，元素竖着排 | RN 的 `flexDirection` 默认是 `column`，与 Web 的 `row` 相反 | 显式声明 `flexDirection: 'row'`，或改用 row 语义的容器组件 |
| 在 RN 样式中给数值加单位 | 报错或样式失效 | RN 的尺寸是数字（逻辑像素），不支持 `px` 等单位后缀 | 直接写数字，如 `fontSize: 16`、`padding: 12` |
| 用 `ScrollView` 渲染长列表 | 列表滚动卡顿、内存占用高、首屏慢 | `ScrollView` 会一次性渲染全部子元素，无虚拟化 | 改用 `FlatList`，并配合 `getItemLayout`、`windowSize` 等参数 |
| RN 的 `renderItem` 中写匿名函数或新建对象 | 列表滚动时频繁重渲染，掉帧明显 | 每次渲染都产生新引用，导致 `memo` 优化失效 | 用 `useCallback` 固定 `renderItem`，行组件用 `React.memo` 包裹 |
| 用数组下标作为 `keyExtractor` | 列表增删后出现状态错乱（如勾选状态串行） | 下标不稳定，Element 复用到了错误的节点 | 使用业务上稳定唯一的 ID 作为 key |
| RN 动画未开启 `useNativeDriver` | 动画卡顿、掉帧 | 动画每帧都要跨 Bridge 通信，无法稳定 60fps | 对 `transform` 与 `opacity` 开启 `useNativeDriver: true`；复杂动画用 Reanimated |
| Flutter 中在 `Column` 里直接放 `ListView` | 报错 `Vertical viewport was given unbounded height` | `Column` 给子级的是无界高度约束，而 `ListView` 需要有限高度 | 用 `Expanded` 包裹 `ListView`，或给 `ListView` 设置 `shrinkWrap: true`（性能较差，慎用） |
| Flutter 列表使用下标作为 `Key` | 列表重排后组件状态错位（如输入框内容串行） | Key 无法正确标识节点，Element 复用错误 | 使用业务唯一 ID 作为 `ValueKey` |
| 在 `initState` 中调用 `setState` | 报错或状态未生效 | `initState` 执行时尚未完成首次挂载，此时应直接赋值 | 在 `initState` 中直接给字段赋值，异步数据用 `FutureBuilder` 或 `addPostFrameCallback` |
| Platform Channel 原生侧未实现方法却不返回 `notImplemented` | Dart 侧的 `await` 永久挂起 | 原生侧既没调用 `success` 也没调用 `error`，Dart 侧一直在等 | 在 `else` 分支显式调用 `result.notImplemented()` |
| 新增原生模块后指望热更新生效 | 用户端仍然报模块不存在 | 原生代码变更无法通过 JS bundle 下发 | 新增或修改原生模块必须重新发版，热更新仅覆盖 JS 层 |
| 用 Flutter 做需要频繁热更新的业务 | 无法实现不发版更新业务逻辑 | Release 模式使用 AOT 编译为机器码，不支持运行时替换 | 需要热更新能力时选 RN；Flutter 侧可用服务端配置或 WebView 承载可变部分 |

---

## 本章学习自检

- [ ] 我能按"谁绘制像素"区分 WebView 容器、原生组件映射、自绘引擎三条路线
- [ ] 我能说出 RN 旧架构的三条线程，以及 Bridge 的异步、批量、序列化三个特性
- [ ] 我能解释 JSI、TurboModules、Fabric、Codegen 各自解决了什么问题
- [ ] 我能说明 Hermes 放弃 JIT 的取舍依据，以及它自 RN 0.70 起成为默认引擎
- [ ] 我能说出 RN 样式与 Web CSS 的三个关键差异（默认 flexDirection、单位、无层叠）
- [ ] 我能列出至少 5 条 FlatList 性能优化手段，并解释 `getItemLayout` 的作用
- [ ] 我能说明 RN 热更新的边界：只能更新 JS 层，原生变更必须发版
- [ ] 我能画出 Flutter 的 Widget / Element / RenderObject 三棵树，并解释 `const` 的价值
- [ ] 我能复述 Flutter 的布局约束口诀，并说明 `Expanded` 的本质
- [ ] 我能对比 Skia 与 Impeller，说明预编译着色器解决的是什么问题
- [ ] 我能写出一个完整的 Platform Channel 示例（Dart + Android + iOS 三侧）
- [ ] 我能解释 Flutter 热重载为什么只在 Debug 模式可用，以及它对动态化能力的影响
- [ ] 我能从渲染机制、性能、包体积、动态化、团队适配成本五个维度对比 RN / Flutter / uniapp

---

## 学习导航

- 上一章：[05-跨端方案选型与桌面端](./05-跨端方案选型与桌面端.md)
- 下一章：[07-鸿蒙HarmonyOS](./07-鸿蒙HarmonyOS.md)
- 导览文件：[06-ReactNative与Flutter-导览](./06-ReactNative与Flutter-导览.md)
- 相关章节：[01-uniapp跨端开发基础](./01-uniapp跨端开发基础.md) | [02-uniapp渲染差异与性能优化](./02-uniapp渲染差异与性能优化.md)
- 常见错误：[常见错误汇总](./常见错误汇总.md)
- 概念对比：[概念对比速查](./概念对比速查.md)
