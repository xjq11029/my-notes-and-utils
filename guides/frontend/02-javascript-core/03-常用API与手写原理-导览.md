# 03-常用API与手写原理 导览

> 定位：五维框架浓缩提炼 03-常用API与手写原理.md 全部内容小节，快速查阅与复习。
> 用法：每个内容小节对应一张纵向表格，需要深入理解时跳转 [原文](./03-常用API与手写原理.md)。
> 前置知识：[语法基础与执行机制](./01-语法基础与执行机制-导览.md)、[异步编程与ES6+特性](./02-异步编程与ES6+特性-导览.md)

---

## 一、防抖（Debounce）与节流（Throttle）

### 1.1 防抖（Debounce）

| 维度 | 内容 |
|------|------|
| 是什么 | 高频事件优化手段：在事件触发后等待一段时间，如果期间事件再次触发则重新计时，只有最后一次触发生效。核心策略是"重置计时，以最后一次为准"。 |
| 能做什么 | 搜索框输入联想（停止输入后发送请求）；窗口 resize 结束后重新计算布局；表单验证（用户停止输入后校验）；按钮防重复点击（结合 immediate 立即执行模式）。 |
| 怎么用 | `function debounce(fn, delay = 300, immediate = false) { let timer = null; return function(...args) { const context = this; if (timer) clearTimeout(timer); if (immediate) { const callNow = !timer; timer = setTimeout(() => timer = null, delay); if (callNow) fn.apply(context, args); } else { timer = setTimeout(() => { fn.apply(context, args); timer = null; }, delay); } }; }` |
| 原理和工作流程 | 利用闭包保存定时器 ID。每次触发时清除旧定时器并设置新定时器，只有事件停止触发超过 `delay` 毫秒后才执行回调。immediate 模式下第一次触发立即执行，通过 `timer` 是否为 null 判断是否为首次触发。需注意保存 `this` 上下文并用 `apply` 传递，否则回调中 this 会丢失。 |
| 缺点 | 延迟执行模式下不能及时响应第一次触发，用户可能感知延迟；immediate 模式需要额外配置，配置不当可能导致行为不符合预期；防抖时间设置过长用户等待感明显，过短则退化为频繁触发。 |

### 1.2 节流（Throttle）

| 维度 | 内容 |
|------|------|
| 是什么 | 高频事件优化手段：在固定时间间隔内，事件只执行一次。无论触发多频繁，按固定频率执行。核心策略是"固定间隔，稀释频率"。 |
| 能做什么 | 滚动事件监听（懒加载、无限滚动）；鼠标移动事件（拖拽实时反馈）；窗口 resize 持续响应；页面滚动进度条更新。 |
| 怎么用 | 时间戳版：`function throttle(fn, interval = 300) { let lastTime = 0; return function(...args) { const now = Date.now(); if (now - lastTime >= interval) { lastTime = now; fn.apply(this, args); } }; }` 定时器版：`function throttleTimer(fn, interval = 300) { let timer = null; return function(...args) { if (!timer) { timer = setTimeout(() => { fn.apply(this, args); timer = null; }, interval); } }; }` |
| 原理和工作流程 | 时间戳版：记录上次执行时间，每次触发计算间隔，超过 `interval` 才执行并更新时间戳，优点是首次立即执行，缺点是无法保证最后一次触发被处理。定时器版：设置一个定时器，定时器到期前忽略所有触发，到期后执行并清除定时器，优点是保证最后一次触发也会执行，缺点是有延迟。两种实现可根据场景选择或组合使用。 |
| 缺点 | 时间戳版无法处理最后一次触发（用户停止操作后可能丢失最后一次更新）；定时器版首次触发有延迟；两种实现各有优劣，需要根据场景选择，组合两者的 leading/trailing 配置实现较复杂。 |

### 1.3 防抖与节流对比

| 维度 | 内容 |
|------|------|
| 是什么 | 防抖和节流都是优化高频事件触发性能的手段，但核心策略不同：防抖是"重新计时，最后一次生效"，节流是"固定频率，按时间间隔执行"。 |
| 能做什么 | 根据业务场景选择合适方案：需要"等待用户操作完成"（如搜索输入）用防抖；需要"持续反馈"（如滚动加载）用节流。防抖在高频触发中只执行一次，节流在高频触发中按固定间隔执行多次。 |
| 怎么用 | 防抖适用场景：搜索框输入、表单验证、窗口 resize 结束、按钮防重复点击。节流适用场景：滚动加载、鼠标拖拽、窗口 resize 持续响应、页面滚动进度条。 |
| 原理和工作流程 | 防抖使用 setTimeout 机制，每次触发清除旧定时器重新计时；节流使用时间戳或定时器机制，记录上次执行时间，固定间隔内只执行一次。两者核心区别在于：防抖关注"最后一次"，节流关注"固定频率"。 |
| 缺点 | 最常犯的错误是混淆两者使用场景——将节流用于搜索框导致每次输入都发请求，或将防抖用于滚动事件导致用户停止滚动时才有反馈。 |

---

## 二、深浅拷贝

### 2.1 浅拷贝

| 维度 | 内容 |
|------|------|
| 是什么 | 只复制对象的第一层属性，如果属性是引用类型，则复制的是引用地址，原对象和副本共享同一个引用。修改副本的嵌套引用类型属性会直接影响原对象。 |
| 能做什么 | 快速创建对象/数组的浅层副本；适用于数据结构简单、只有一层属性的场景；配合不可变数据模式中创建新对象。 |
| 怎么用 | `Object.assign({}, source)` 对象浅拷贝；`{ ...source }` 展开运算符浅拷贝；`sourceArr.slice()` 或 `sourceArr.concat()` 数组浅拷贝。注意：`const copy = { ...obj }; copy.b.c = 999;` 会同时修改原对象 `obj.b.c`。 |
| 原理和工作流程 | 创建一个新对象，遍历原对象的可枚举属性，将属性值复制到新对象。对于基本类型属性，复制的是值；对于引用类型属性，复制的是引用地址，两个对象中该属性指向同一块堆内存。Object.assign 和展开运算符都只复制一层，行为一致。 |
| 缺点 | 嵌套引用类型属性仍然是共享的，修改副本中的嵌套对象会影响原对象，容易产生"明明是副本为什么原对象也被修改了"的困惑；开发者容易误以为 `{ ...obj }` 是完全独立的副本。 |

### 2.2 深拷贝

| 维度 | 内容 |
|------|------|
| 是什么 | 递归复制对象的所有层级属性，创建完全独立的对象副本。修改副本的任何属性（包括嵌套引用类型）都不会影响原对象。 |
| 能做什么 | 获取对象的完整独立副本；状态管理中创建不可变数据快照；表单数据的备份与恢复；避免意外修改共享数据。 |
| 怎么用 | 简单方式：`JSON.parse(JSON.stringify(source))`，有局限性（无法处理函数、undefined、Symbol、Date、RegExp、Map、Set、循环引用）。手写实现：递归遍历所有属性，基本类型直接赋值，引用类型递归创建新对象/数组，用 `WeakMap` 记录已拷贝对象处理循环引用，用 `Reflect.ownKeys` 遍历包含 Symbol 键的所有属性，分别处理 Date、RegExp、Map、Set 等特殊类型。 |
| 原理和工作流程 | 递归遍历对象所有属性：遇到基本类型直接赋值；遇到引用类型判断类型后创建对应新实例（Date→new Date、RegExp→new RegExp、Map→递归拷贝键值对、Set→递归拷贝值、数组→新数组遍历、普通对象→新对象遍历）；WeakMap 以原对象为键存储已拷贝的结果，遇到循环引用时直接返回缓存值，避免无限递归。Reflect.ownKeys 确保 Symbol 属性不被遗漏。 |
| 缺点 | 递归过深可能导致栈溢出（极端深层对象）；大量对象拷贝耗时较长，性能不如 JSON 方案；JSON 方案虽简单但有 7 个局限性（函数、undefined、Symbol、Date、RegExp、Map/Set、循环引用）；手写完整深拷贝实现复杂，需要处理多种特殊类型。 |

---

## 三、数组去重

### 3.1 数组去重方案

| 维度 | 内容 |
|------|------|
| 是什么 | 前端开发中的常见需求：将数组中的重复元素移除，保留唯一值。有多种实现方案，各有优劣，选择取决于数据类型和对性能的要求。 |
| 能做什么 | 去除列表中重复数据；统计唯一值数量；构建唯一标识符集合；数据清洗与预处理。 |
| 怎么用 | Set 方案（推荐首选）：`const unique = [...new Set(arr)];`，O(n) 时间复杂度，简洁高效，NaN 可正确去重但对象按引用去重。Map 方案：`function uniqueByMap(arr) { const map = new Map(); return arr.filter(item => !map.has(item) && map.set(item, true)); }`，O(n)，能处理 NaN。filter + indexOf 方案：`arr.filter((item, index) => arr.indexOf(item) === index)`，O(n^2)，NaN 无法去重。对象数组按属性去重：`function uniqueByProperty(arr, key) { const seen = new Set(); return arr.filter(item => { const v = item[key]; if (seen.has(v)) return false; seen.add(v); return true; }); }` |
| 原理和工作流程 | Set 方案利用 Set 内部使用 SameValueZero 算法保证值唯一（NaN 等于自身），直接去重。Map 方案通过 Map 的 has 判断是否已存在（SameValueZero 比较），不存在则存入并保留。filter + indexOf 方案通过 indexOf 查找元素首次出现位置，仅保留首次出现的元素，但 indexOf 使用严格相等比较，NaN !== NaN 导致 NaN 全部被过滤。对象属性去重先将属性值加入 Set 记录已见值，后续相同的值被过滤。 |
| 缺点 | Set 方案无法按值去重对象（只比较引用）；filter + indexOf 方案 O(n^2) 性能差且 NaN 处理错误；对象属性去重依赖 JSON.stringify 时可能不可靠；没有一种方案可以完美处理所有类型（基本类型、NaN、对象）的去重。 |

---

## 四、函数柯里化（Currying）

### 4.1 函数柯里化

| 维度 | 内容 |
|------|------|
| 是什么 | 将一个接受多个参数的函数，转换成一系列每次只接受一个参数的函数的技术。核心思想是利用闭包保存已传入的参数，等参数收集完毕后执行原函数。 |
| 能做什么 | 参数复用：固定部分参数创建偏函数（如 `curry(multiply)(2)` 创建 double 函数）；延迟执行：收集参数但不立即执行，直到参数齐全；函数组合（compose/pipe）的前置辅助；提高代码灵活性和可复用性。 |
| 怎么用 | `function curry(fn) { return function curried(...args) { if (args.length >= fn.length) { return fn.apply(this, args); } return function(...nextArgs) { return curried.apply(this, [...args, ...nextArgs]); }; }; }` 使用：`const curriedAdd = curry((a, b, c) => a + b + c); curriedAdd(1)(2)(3); // 6`，也支持 `curriedAdd(1, 2)(3)` 和 `curriedAdd(1)(2, 3)`。 |
| 原理和工作流程 | 利用闭包保存已收集的参数数组。每次调用时检查已收集参数数量是否达到原函数 `fn.length`（形参个数），达到则执行原函数并返回结果，未达到则返回一个新函数继续收集参数。新函数通过 `apply` 合并之前收集的参数和新传入的参数，递归调用 curried 继续判断。所有参数收集齐全后一次性执行原函数。 |
| 缺点 | 对可变参数函数（使用 ...rest 或 arguments）支持不好，因为 `fn.length` 不包含 rest 参数；参数过长时递归调用链深，极端情况可能栈溢出；理解门槛略高，初学者容易混淆柯里化和偏函数的概念。 |

---

## 五、继承实现

### 5.1 五种继承方式

| 维度 | 内容 |
|------|------|
| 是什么 | JavaScript 的继承本质上是原型链的扩展，ES5 和 ES6 提供了五种继承方式：原型链继承、构造函数继承、组合继承、寄生组合继承、ES6 class extends。 |
| 能做什么 | 实现代码复用，子类继承父类的属性和方法；建立对象之间的层级关系；理解 JavaScript 面向对象编程的底层机制。 |
| 怎么用 | 原型链继承：`Child.prototype = new Parent();`（所有实例共享引用类型属性，无法传参）；构造函数继承：`function Child() { Parent.call(this); }`（无法继承原型方法）；组合继承：`Parent.call(this)` + `Child.prototype = new Parent()`（父类调用两次）；寄生组合继承（最优）：`Parent.call(this)` + `Child.prototype = Object.create(Parent.prototype)` + `Child.prototype.constructor = Child`（只调用一次父类，原型链正确）；ES6 class：`class Child extends Parent { constructor() { super(); } }`（语法糖，底层仍是原型链）。 |
| 原理和工作流程 | 原型链继承让子类原型指向父类实例，子类实例通过 `__proto__` 链访问父类属性和方法，但引用类型属性被所有实例共享。构造函数继承在子类中调用父类构造函数，每个实例有独立的属性副本，但无法继承父类原型上的方法。组合继承结合两者，但父类构造函数被调用两次。寄生组合继承通过 `Object.create(Parent.prototype)` 创建原型副本，避免第二次调用父类。ES6 class 的 extends 底层设置 `Child.prototype.__proto__ = Parent.prototype`，super 调用父类构造函数。 |
| 缺点 | 原型链继承：引用类型属性共享，无法向父类传参；构造函数继承：无法继承原型方法；组合继承：父类构造函数调用两次，原型上有冗余属性；寄生组合继承：实现稍复杂，需要手动设置 constructor；ES6 class：语法糖可能让开发者忽略底层原型链机制。 |

---

## 六、JavaScript 垃圾回收

### 6.1 垃圾回收机制

| 维度 | 内容 |
|------|------|
| 是什么 | JavaScript 引擎自动管理内存的机制，开发者不需要手动分配和释放内存。主要算法有引用计数和标记清除两种，现代引擎（V8）使用标记清除算法的变体——分代回收。 |
| 能做什么 | 自动回收不再使用的内存，防止内存泄漏；理解 GC 机制有助于编写内存友好的代码；帮助排查内存泄漏问题。 |
| 怎么用 | 开发者无需手动调用 GC，但应遵循最佳实践：及时清除定时器（`clearInterval` / `clearTimeout`）；移除不再需要的事件监听（`removeEventListener`）；避免意外的全局变量（使用 `let` / `const`）；解除不再需要的 DOM 引用（设置为 null）。 |
| 原理和工作流程 | V8 将内存分为新生代（1-8MB，存储短生命周期对象）和老生代（存储长生命周期对象）。新生代使用 Scavenge 算法（Cheney 算法），将存活对象复制到另一半空间，空间快满时触发；老生代使用 Mark-Sweep（标记清除）+ Mark-Compact（标记整理），标记从根对象可达的对象，清除未标记对象，碎片化严重时整理内存。对象晋升条件：新生代中经历一次 Scavenge 仍存活的对象，或 To 空间使用率超过 25% 时，晋升到老生代。 |
| 缺点 | 引用计数算法无法处理循环引用（已被标记清除替代）；GC 触发时会导致主线程暂停（Stop-The-World），大内存场景下暂停时间较长；开发者无法精确控制 GC 时机，只能通过优化代码减少 GC 压力。 |

---

## 七、内存泄漏场景

### 7.1 内存泄漏场景与排查

| 维度 | 内容 |
|------|------|
| 是什么 | 内存泄漏指不再需要使用的内存未被垃圾回收机制释放，导致内存占用持续增长，最终可能造成页面卡顿、崩溃。JavaScript 中常见的内存泄漏场景共 7 种。 |
| 能做什么 | 识别和避免内存泄漏：全局变量不会被 GC 回收；未清理的定时器持有回调引用；闭包不当使用保留整个外部作用域；JavaScript 引用已移除的 DOM 元素；事件监听未移除；detached DOM 树（父节点移除但子节点引用仍在）；WebSocket/EventSource 等长连接未关闭。 |
| 怎么用 | 排查工具：Chrome DevTools Performance 面板录制内存曲线，观察持续上升的内存；Memory 面板的 Heap Snapshot 对比操作前后快照，查找未释放对象；Allocation instrumentation on timeline 记录内存分配时间线；Performance Monitor 实时监控 JS Heap Size 和 DOM Nodes。预防手段：使用 WeakMap/WeakSet 存储 DOM 关联数据（弱引用不阻止 GC）；SPA 组件销毁时在 useEffect/componentWillUnmount 中清理副作用；生产环境移除 console.log；避免闭包引用整个外部作用域。 |
| 原理和工作流程 | 全局变量被挂载到 window 上，始终可达，永远不会被 GC 回收。定时器内部持有回调函数引用，未清除的定时器导致回调函数及其闭包引用的变量无法释放。事件监听器通过 addEventListener 将回调函数注册到 DOM 元素上，DOM 移除后监听器可能仍持有引用。闭包保存了外部函数的整个作用域链，即使只使用其中一小部分变量，整个作用域都无法被 GC。WeakMap 的键是弱引用，不影响 GC，适合存储 DOM 关联数据。 |
| 缺点 | 内存泄漏在开发阶段不易察觉，通常需要专门工具排查；SPA 页面切换频繁，内存泄漏累积效应明显；闭包导致的内存泄漏往往难以定位，因为闭包隐式持有引用。 |

---

## 补充：EventEmitter 模式与函数式编程

### 补1 EventEmitter 模式（发布-订阅）

| 维度 | 内容 |
|------|------|
| 是什么 | 发布-订阅模式（Publish-Subscribe Pattern）的经典实现，事件发布者与消费者通过事件名称解耦，发布者只管触发事件，不需要知道谁在监听。Node.js 的 events 模块广泛使用此模式。 |
| 能做什么 | 组件间通信（非父子组件数据传递）；全局事件总线（跨模块通信、状态变更通知）；自定义事件系统（WebSocket 消息分发、游戏引擎事件）；Node.js 核心模块（http.Server、fs.ReadStream、process）均基于此模式。 |
| 怎么用 | 核心 API：`on(event, listener)` 注册事件监听；`emit(event, ...args)` 触发事件并传递参数；`once(event, listener)` 单次监听（执行后自动移除）；`removeListener(event, listener)` 移除指定监听；`removeAllListeners(event)` 移除全部监听。实现时内部用 `_events` 对象存储事件名到监听列表的映射，每个监听项包含 `{ fn, once }` 两个属性。 |
| 原理和工作流程 | 构造函数初始化 `_events` 为空对象。`on` 方法将监听函数推入对应事件名的数组中。`emit` 方法取出监听列表，拷贝一份后遍历执行（拷贝是因为回调中可能修改监听列表），执行时传递参数并检查 `once` 标记，一次性监听执行后自动从原始列表移除。`removeListener` 通过 `findIndex` 匹配函数引用后 splice 移除。需注意监听函数必须用同一函数引用才能正确移除。 |
| 缺点 | 与 DOM 事件不同，EventEmitter 无事件传播（捕获/冒泡）过程，不支持事件委托；监听函数移除依赖函数引用，匿名函数或箭头函数无法直接移除；事件名使用字符串，拼写错误不会报错，调试困难。 |

### 补2 函数式编程基础

| 维度 | 内容 |
|------|------|
| 是什么 | 一种编程范式，核心原则包括：纯函数（相同输入始终相同输出，无副作用）、不可变性（数据创建后不可修改）、高阶函数（接受或返回函数的函数）、函数组合（compose/pipe 将小函数组合成新函数）、声明式编程（描述"做什么"而非"怎么做"）。 |
| 能做什么 | 纯函数提高可预测性和可测试性；不可变性避免意外修改共享状态；高阶函数实现代码复用和抽象（如 withLogging、once）；compose/pipe 将多个小函数组合成复杂逻辑，职责单一、易于维护；声明式风格（map/filter/reduce 链式调用）语义清晰，可读性强。 |
| 怎么用 | 纯函数：`const add = (a, b) => a + b;`（不依赖外部状态，不修改入参）。不可变性：使用 `Object.freeze`、展开运算符 `{ ...obj }`、数组非破坏性方法（map/filter/reduce/concat）。高阶函数：`function withLogging(fn) { return function(...args) { console.log('调用:', args); const result = fn.apply(this, args); console.log('结果:', result); return result; }; }`。函数组合：`compose(f, g, h)(x)` 等价于 `f(g(h(x)))`（从右到左），`pipe(f, g, h)(x)` 等价于 `h(g(f(x)))`（从左到右）。声明式：`arr.filter(n => n % 2 === 0).map(n => n * 2)` 替代 for 循环。 |
| 原理和工作流程 | 纯函数依赖"引用透明"特性：函数调用可以被其返回值替换而不改变程序行为。不可变性通过创建新副本而非修改原数据来实现，避免副作用。高阶函数利用闭包保存外部函数引用，返回增强后的函数。compose 使用 reduceRight 从右到左执行，pipe 使用 reduce 从左到右执行，数据依次流经每个变换函数。声明式编程依赖高阶函数（map/filter/reduce）封装了迭代逻辑，开发者只需描述转换规则。 |
| 缺点 | 纯函数不能处理 I/O、DOM 操作等副作用场景，实际项目中需要与不纯的函数结合使用；不可变性导致频繁创建新对象，大数据量场景下可能有性能开销；过度使用函数组合可能导致调用链过长，调试困难；声明式编程中的链式调用在数据量大时可能产生中间数组，需要借助 lazy evaluation 优化。 |

---

## 补充：Proxy、迭代器与内存排查方法论

### 补1 Proxy 与 Reflect 原理

| 维度 | 内容 |
|------|------|
| 是什么 | `Proxy` 是 ES6 的元编程能力，通过 `handler` 中的陷阱（trap）拦截对目标对象的底层操作；`Reflect` 提供与 13 种 trap 一一对应的静态方法，用于在 trap 中执行默认行为。 |
| 能做什么 | 拦截属性读写、`in`、`delete`、`ownKeys`、函数调用与 `new` 等 13 类操作；实现响应式系统（Vue 3）、数据校验、访问日志、只读视图、可撤销的临时访问权限。 |
| 怎么用 | `new Proxy(target, handler)`；`Proxy.revocable(target, handler)` 返回 `{ proxy, revoke }`，`revoke()` 后任何操作抛 `TypeError`；在 trap 中用 `Reflect.get(t, key, receiver)` / `Reflect.set(t, key, value, receiver)` 转发默认行为；`set` trap 必须返回布尔值。 |
| 原理和工作流程 | 13 种 trap 分别为 `get`、`set`、`has`、`deleteProperty`、`ownKeys`、`getOwnPropertyDescriptor`、`defineProperty`、`getPrototypeOf`、`setPrototypeOf`、`isExtensible`、`preventExtensions`、`apply`、`construct`。`Reflect` 相比 `Object` 有三个优势：返回布尔值而非抛异常、参数顺序统一为 `(target, ...)`、支持 `receiver`。`receiver` 决定访问器（getter / setter）中的 `this` 指向——传 `receiver` 才能让 getter 内部的属性访问也经过代理，这正是 Vue 3 依赖收集不漏项的关键。Vue 3 改用 Proxy 的原因：可监听新增 / 删除属性与数组索引赋值（Vue 2 需 `$set` / `$delete`）、支持 `Map` / `Set`、惰性代理使初始化开销与属性数量解耦、拦截能力从 2 种扩展到 13 种。 |
| 缺点 | 无法拦截 class 私有字段 `#x` 与闭包内变量访问；无法代理原始值；trap 返回值必须满足不变式（如 target 不可扩展时 `ownKeys` 必须返回全部键），否则抛 `TypeError`；每次属性访问多一层函数调用，热路径上有明显性能开销；`proxy !== target`，作为 `Map` / `Set` 键时与 target 视为不同键；调用代理上的方法时 `this` 是代理，访问 `#private` 字段会报错；无法 polyfill，IE 完全不支持。 |

### 补2 迭代器与生成器协议

| 维度 | 内容 |
|------|------|
| 是什么 | 可迭代协议要求对象实现 `[Symbol.iterator]()` 并返回迭代器；迭代器协议要求对象有 `next()` 方法且返回 `{ value, done }`，可选实现 `return(value)` 与 `throw(error)`；`Symbol.asyncIterator` 对应异步迭代协议。 |
| 能做什么 | 让自定义数据结构支持 `for...of`、展开运算符、解构、`Array.from`；实现惰性求值与无限序列；递归遍历树结构；可中断的遍历；用生成器实现异步流程控制（redux-saga、早期 `co` 库）。 |
| 怎么用 | 手写可迭代对象：实现 `[Symbol.iterator]()` 返回带 `next()` 的对象，并补 `[Symbol.iterator]() { return this; }` 使迭代器自身也可迭代；生成器：`function* gen() { const a = yield 1; return a; }`，`next(v)` 的实参成为上一个 `yield` 表达式的值；`yield* inner()` 委托给另一个可迭代对象并接收其返回值；异步迭代：`async function* fetchPages() { yield await fetch(url) }` 配合 `for await...of`。 |
| 原理和工作流程 | `for...of` 的执行流程是：调用 `[Symbol.iterator]()` 取迭代器 → 反复 `next()` 取值 → `done` 为 true 时退出；**提前退出（`break` / `return` / 抛异常）时会调用迭代器的 `return()`** 用于资源清理。生成器函数调用时不执行函数体，而是返回同时是迭代器与可迭代对象的生成器对象；执行到 `yield` 暂停并交出值，下次 `next(v)` 从暂停处恢复且 `v` 成为上一个 `yield` 的结果；`return(v)` 在暂停处注入 `return` 并触发 `finally`，`throw(e)` 在暂停处抛出错误。内置可迭代对象包括数组、字符串、`Map`、`Set`、`TypedArray`、`arguments`、`NodeList`，**普通对象不是可迭代对象**。 |
| 缺点 | 普通对象无法直接 `for...of`，需 `Object.entries` 转换或手动实现协议；生成器对象是**一次性**的，遍历完即 `done`，重复遍历必须重新调用生成器函数；首次 `next()` 的实参会被丢弃；迭代器若未实现 `Symbol.iterator` 则无法被展开运算符消费；忘记实现 `return()` 或缺少 `try/finally` 会导致提前退出时资源泄漏。 |

### 补3 DevTools Memory 内存排查方法论

| 维度 | 内容 |
|------|------|
| 是什么 | Chrome DevTools Memory 面板提供的三种分析工具（Heap Snapshot 堆快照、Allocation instrumentation on timeline 分配时间线、Allocation sampling 分配采样），配合 Performance Monitor 形成完整的内存泄漏排查链路。 |
| 能做什么 | 精确定位泄漏对象与引用链；区分"一次性缓存"与"真正泄漏"；识别 Detached DOM tree；判断泄漏类型（DOM Nodes / Event Listeners / JS heap）并闭环修复与验证。 |
| 怎么用 | 三快照法：强制 GC 拍 Snapshot 1（基线）→ 执行一次可疑操作后强制 GC 拍 Snapshot 2 → 重复同样操作后强制 GC 拍 Snapshot 3 → 用 Comparison 视图对比 Snapshot 2 与 3，只有两次增量都持续增长才是泄漏 → 选中可疑 Constructor 展开 Retainers 链追溯到 GC 根。Detached DOM 识别：Snapshot 中搜索 `Detached`、Console 执行 `queryObjects(HTMLElement).filter(el => !document.contains(el)).length`、观察 Performance Monitor 的 DOM Nodes 计数。 |
| 原理和工作流程 | 单张快照无法区分缓存与泄漏，因此必须用"两次增量"过滤噪音——缓存只在第一次操作时增长，泄漏则每次操作都留下无法回收的对象。关键指标中 **Shallow Size** 是对象自身占用，**Retained Size** 是释放该对象后可回收的总内存（含其独占引用的对象），判断泄漏影响看 Retained Size；**Distance** 是从 GC 根到该对象的最短引用层级。Allocation Timeline 用蓝条表示新分配且仍存活的内存、灰条表示已回收，蓝条持续堆积即为泄漏，点击可查看分配时的函数调用栈（开销大，适合短时排查）；Allocation Sampling 按间隔采样，开销小，适合长时间录制与找出"分配大户"。定位流程为：观测曲线 → 按指标分类泄漏类型 → 确定最小复现操作 → 三快照法锁定对象 → Retainers 链溯源 → 修复（移除监听、清理定时器、置 `null`、改用 `WeakMap`）→ 复测验证。 |
| 缺点 | Heap Snapshot 文件较大且分析耗时，需要人工阅读 Retainers 链；Allocation Timeline 记录每次分配，开销大，只适合短时间录制；DevTools 打开时 `console.log` 会持有对象的强引用，制造"假泄漏"干扰判断；排查依赖 DevTools 保持打开，无法在生产环境直接使用；Performance Monitor 只能提示"有增长"，无法直接指出代码位置。 |

---

## 本章学习自检

本节为辅助内容，无五维表格。

---

> [返回原文](./03-常用API与手写原理.md) | [返回模块目录](../README.md) | [返回知识导览](../知识导览.md)