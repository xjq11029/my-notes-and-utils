# 04-React笔面试题集 导览

> 定位：五维框架浓缩提炼 04-React笔面试题集.md 全部题目所考知识点，快速查阅与复习。
> 用法：每道题目提取所考知识点生成一张纵向表格，需要查看原题解析时跳转 [原文](./04-React笔面试题集.md)。
> 前置知识：[React核心与Hooks](./01-React核心与Hooks-导览.md)、[Diff算法与性能优化](./02-Diff算法与性能优化-导览.md)、[路由与状态管理](./03-路由与状态管理-导览.md)

---

## 一、选择题（16 题，每题附解析）

| 维度 | 内容 |
|------|------|
| 是什么 | 覆盖 JSX、虚拟 DOM、Fiber 架构、Hooks、Diff 算法、状态管理、React 18/19 并发特性等核心知识点的单项选择题 |
| 能做什么 | 检验对 React 基础概念、API 特性和底层原理的掌握程度，难度从基础到拔高递进 |
| 怎么用 | 先独立作答再对照解析，理解每个选项正确与否的原因，不满足于选对答案 |
| 原理和工作流程 | 16 题按知识点分布：JSX 本质（1）、状态管理 Hook（2）、虚拟 DOM（3）、React 18 并发特性（4）、Fiber 架构（5）、Hooks 调用规则（6）、useEffect 依赖（7）、useMemo 与 useCallback（8）、React.memo（9）、setState 批处理（10）、key 作用（11）、useLayoutEffect（12）、React Router v6（13）、Redux 原则（14）、useTransition（15）、React 19 use() API（16）。难度：★基础 3 题、★★中档 10 题、★★★拔高 3 题 |
| 缺点 | 选择题只能检验知识记忆，无法考察实际编码和调试能力；选项干扰性有限，部分题目可通过排除法猜对 |

### 1. JSX 的本质是什么

| 维度 | 内容 |
|------|------|
| 是什么 | JSX 是 `React.createElement` 的语法糖，由 Babel 编译为 JavaScript 函数调用 |
| 能做什么 | 让开发者以类 HTML 的语法编写 UI 结构，编译后生成虚拟 DOM 节点，提升代码可读性 |
| 怎么用 | `<div className="box">{name}</div>` 编译为 `React.createElement('div', { className: 'box' }, name)` |
| 原理和工作流程 | Babel 在编译阶段将 JSX 转换为标准 JavaScript 函数调用。React 17+ 引入新的 JSX 转换（`react/jsx-runtime`），不再需要手动引入 React。JSX 不是模板语言，不是浏览器内置 API，也不直接操作 DOM |
| 缺点 | 混合了 HTML 和 JavaScript 语法，初学者容易混淆表达式和语句的用法；编译后代码可读性差 |

### 2. 以下哪个 Hook 用于在函数组件中管理状态

| 维度 | 内容 |
|------|------|
| 是什么 | `useState` 是 React 函数组件中管理状态的基础 Hook，返回状态值和更新函数 |
| 能做什么 | 在函数组件中声明和更新局部状态，替代类组件中的 `this.state` 和 `this.setState` |
| 怎么用 | `const [count, setCount] = useState(0)` |
| 原理和工作流程 | `useState` 返回 `[state, setState]` 数组，`setState` 可接收新值或函数式更新 `(prev) => newValue`。`useReducer` 也可管理状态但适用于复杂逻辑；`useEffect` 处理副作用；`useContext` 订阅 Context。React 内部通过链表按调用顺序存储 Hook 状态 |
| 缺点 | 复杂状态逻辑（多个关联状态）使用多个 useState 会导致多次 setState 调用，代码可读性下降 |

### 3. 关于 React 虚拟 DOM 的说法正确的是

| 维度 | 内容 |
|------|------|
| 是什么 | 虚拟 DOM 是真实 DOM 的 JavaScript 对象表示，配合 Diff 算法最小化 DOM 操作 |
| 能做什么 | 通过 Diff 算法计算最小 DOM 变更，批量更新真实 DOM，减少昂贵的浏览器重排重绘 |
| 怎么用 | React 自动管理，开发者无需手动操作虚拟 DOM |
| 原理和工作流程 | 虚拟 DOM 本身操作不比真实 DOM 快，价值在于减少真实 DOM 操作次数。状态变化时 React 生成新虚拟 DOM 树，与旧树比较找出差异，批量更新真实 DOM。虚拟 DOM 不是浏览器内置 API，最终仍需操作真实 DOM，它是一种抽象层可跨平台渲染 |
| 缺点 | Diff 计算本身有性能开销，极简单 DOM 操作可能不如直接操作真实 DOM；需额外内存存储虚拟 DOM 树 |

### 4. React 18 中新增的并发特性不包括

| 维度 | 内容 |
|------|------|
| 是什么 | React 18 的并发特性包括 useTransition、useDeferredValue、Automatic Batching、Suspense 改进，不包括 Server Components |
| 能做什么 | 在不阻塞主线程的情况下处理非紧急更新，保持 UI 交互流畅 |
| 怎么用 | `const [isPending, startTransition] = useTransition()` 或 `const deferred = useDeferredValue(input)` |
| 原理和工作流程 | **Server Components** 是 React 18 之后才正式推出的特性（React 19 中稳定），不属于 React 18 的并发特性。React 18 的并发特性包括：useTransition（标记非紧急更新）、useDeferredValue（延迟更新值）、Automatic Batching（所有场景下自动批处理）、Suspense 改进（SSR 流式渲染和选择性注水） |
| 缺点 | 并发特性增加了 React 内部调度复杂度；错误使用 useTransition 可能导致 UI 更新延迟感知 |

### 5. React Fiber 架构主要解决什么问题

| 维度 | 内容 |
|------|------|
| 是什么 | React 16 引入的协调引擎，通过时间分片和任务优先级解决长任务阻塞主线程导致的页面卡顿 |
| 能做什么 | 将渲染任务拆分为可中断的小工作单元，优先处理紧急更新，保持高帧率渲染 |
| 怎么用 | 开箱即用，React 16+ 默认使用 Fiber 架构 |
| 原理和工作流程 | React 15 的 Stack Reconciler 使用递归遍历不可中断，组件树庞大时一次 Diff 可能超过 16ms 导致掉帧。Fiber 通过链表结构（child/sibling/return）支持遍历中断和恢复，将渲染分为 render 阶段（可中断）和 commit 阶段（不可中断），基于优先级调度实现时间分片 |
| 缺点 | Fiber 架构增加了 React 内部实现复杂度；调度优先级可能导致低优先级更新被延迟过久 |

### 6. 为什么 Hooks 不能在条件语句中使用

| 维度 | 内容 |
|------|------|
| 是什么 | Hooks 依赖调用顺序在内部链表中存储状态，条件调用会破坏顺序导致状态错乱 |
| 能做什么 | 约束开发者在函数组件顶层调用 Hooks，避免在条件、循环、嵌套函数中使用 |
| 怎么用 | 始终在函数组件最顶层调用 Hooks，不在 `if`/`for`/`while` 或嵌套函数中使用 |
| 原理和工作流程 | React 内部通过链表按调用顺序存储每个 Hook 的状态。每次渲染时 React 按顺序读取链表中的状态。如果某个 Hook 在条件语句中调用，调用顺序可能变化，导致 Hook 读取到错误的状态，引发不可预测的 bug。与 TypeScript 类型推断和性能优化无关 |
| 缺点 | 限制了 Hooks 的使用位置，某些场景下代码组织不够灵活；lint 规则可辅助检测但无法覆盖所有场景 |

### 7. useEffect 的第二个参数为空数组 [] 表示什么

| 维度 | 内容 |
|------|------|
| 是什么 | `useEffect(fn, [])` 表示依赖数组为空，副作用仅在组件挂载时执行一次 |
| 能做什么 | 模拟类组件的 `componentDidMount` 生命周期，用于初始化数据请求、事件订阅等一次性操作 |
| 怎么用 | `useEffect(() => { fetchData() }, [])` |
| 原理和工作流程 | 空数组 `[]` 表示依赖项从未变化，因此副作用仅在组件首次渲染后执行一次。如果省略第二个参数，每次渲染后都执行；依赖数组中有值时，仅在依赖值变化时执行。React 使用 `Object.is` 比较每个依赖值 |
| 缺点 | 如果在空依赖数组的 effect 中引用了外部变量，lint 会提示缺失依赖但开发者可能忽略；清理函数仅在组件卸载时执行 |

### 8. useMemo 和 useCallback 的区别

| 维度 | 内容 |
|------|------|
| 是什么 | useMemo 缓存计算结果，useCallback 缓存函数引用，useCallback 是 useMemo 的语法糖 |
| 能做什么 | useMemo 避免昂贵计算在每次渲染时重复执行；useCallback 保持函数引用稳定，配合 React.memo 避免子组件不必要的重渲染 |
| 怎么用 | `const value = useMemo(() => compute(a, b), [a, b])`；`const fn = useCallback(() => doSomething(a), [a])` |
| 原理和工作流程 | `useMemo(() => value, deps)` 缓存计算结果，返回缓存的值。`useCallback(fn, deps)` 等价于 `useMemo(() => fn, deps)`，专门用于缓存函数引用。两者都依赖 deps 数组决定是否更新缓存。两者均可在函数组件和自定义 Hook 中使用 |
| 缺点 | 滥用 useMemo/useCallback 带来额外内存开销和依赖比较成本；依赖数组不完整时可能导致闭包陷阱 |

### 9. React.memo 的作用是什么

| 维度 | 内容 |
|------|------|
| 是什么 | 一个高阶组件，对函数组件的 props 进行浅比较，避免不必要的重渲染 |
| 能做什么 | 当父组件重渲染时，若子组件的 props 未变化则跳过子组件渲染，复用上一次结果 |
| 怎么用 | `const MemoComp = React.memo(MyComponent)` 或 `React.memo(MyComponent, (prev, next) => prev.id === next.id)` |
| 原理和工作流程 | `React.memo` 包裹函数组件后，渲染前对 props 进行浅比较。props 无变化则跳过渲染。可通过第二个参数自定义比较函数。只比较 props，不比较 state 或 context 的变化。它不是缓存函数计算结果，也不是记忆组件状态 |
| 缺点 | 浅比较本身有计算开销，对 props 简单且父组件很少重渲染的组件，使用 React.memo 反而可能降低性能 |

### 10. 关于 setState 的说法正确的是

| 维度 | 内容 |
|------|------|
| 是什么 | React 18 在所有场景下（事件处理、setTimeout、Promise、原生事件）自动批处理多次 setState |
| 能做什么 | 减少不必要的重渲染次数，提升应用性能，开发者无需手动优化批处理逻辑 |
| 怎么用 | 无需额外配置，React 18 默认开启自动批处理 |
| 原理和工作流程 | React 17 仅在事件处理函数中批处理，setTimeout 等异步回调中的多次 setState 会触发多次渲染。React 18 引入 Automatic Batching，在所有场景下自动合并多次 setState 为一次更新，这是 React 18 相比 React 17 的重要改进 |
| 缺点 | 自动批处理使 setState 的异步行为更隐蔽，调试时可能困惑为何状态未立即更新；极少数场景需用 `flushSync` 同步获取 DOM |

### 11. React Diff 算法中 key 的作用是什么

| 维度 | 内容 |
|------|------|
| 是什么 | key 是同一层级节点的唯一标识，帮助 Diff 算法识别哪些元素发生了变化、可复用或需要移动 |
| 能做什么 | 在列表渲染中，通过 key 让 React 精确判断节点的增删移动，避免不必要的 DOM 重建 |
| 怎么用 | `<li key={item.id}>{item.name}</li>`，key 必须在其兄弟节点中唯一 |
| 原理和工作流程 | Diff 算法的 Element Diff 策略通过 key 标识同一层级子节点。比较新旧列表的 key 来判断：key 相同则复用节点并更新内容；key 新增则插入；key 消失则删除。key 不会作为 id 属性传递给 DOM（除非手动传递），不用于 CSS 样式选择器，也不仅用于 DevTools 调试 |
| 缺点 | 使用数组索引作为 key 在列表顺序变化时会导致错误的复用和渲染问题；key 仅在兄弟节点间比较 |

### 12. useLayoutEffect 和 useEffect 的区别

| 维度 | 内容 |
|------|------|
| 是什么 | useLayoutEffect 在 DOM 变更后同步执行、阻塞渲染；useEffect 在渲染完成后异步执行 |
| 能做什么 | useLayoutEffect 用于需要同步读取 DOM 布局信息并立即修改以避免视觉闪烁的场景；useEffect 用于不阻塞渲染的副作用 |
| 怎么用 | `useLayoutEffect(() => { /* 同步读取 DOM */ }, [])`；`useEffect(() => { /* 异步操作 */ }, [])` |
| 原理和工作流程 | `useLayoutEffect` 在 DOM 变更后、浏览器绘制前同步执行，会阻塞浏览器渲染。`useEffect` 在浏览器绘制完成后异步执行，不会阻塞渲染。两者在服务端渲染时都不执行。选择 useLayoutEffect 的场景：需要读取 DOM 尺寸并在渲染前同步调整布局 |
| 缺点 | useLayoutEffect 阻塞渲染，滥用会导致页面响应变慢；大多数场景用 useEffect 即可，不应默认使用 useLayoutEffect |

### 13. React Router v6 中哪个组件用于替代 v5 的 Switch

| 维度 | 内容 |
|------|------|
| 是什么 | `<Routes>` 是 React Router v6 中替代 v5 `<Switch>` 的路由匹配容器组件 |
| 能做什么 | 提供更智能的路由匹配（默认匹配最佳路由而非第一个匹配），支持嵌套路由和相对路径 |
| 怎么用 | `<Routes><Route path="/" element={<Home />} /><Route path="/about" element={<About />} /></Routes>` |
| 原理和工作流程 | v6 使用 `<Routes>` 替代 v5 的 `<Switch>`。`<Routes>` 扫描所有子 `<Route>`，选择最佳匹配而非第一个匹配。`<Route>` 的 `element` 属性替代了 v5 的 `component`/`render`。嵌套路由通过 `<Outlet>` 渲染，路径支持相对写法 |
| 缺点 | 从 v5 迁移时所有 `<Switch>` 和 `<Route>` 配置需逐一修改；智能匹配逻辑在复杂路由场景下可能产生非预期行为 |

### 14. 关于 Redux 的说法正确的是

| 维度 | 内容 |
|------|------|
| 是什么 | Redux 遵循三大原则：单一数据源、State 只读、纯函数修改，整个应用只有一个 Store |
| 能做什么 | 保证状态变更的可预测性和可追溯性，使应用状态管理标准化 |
| 怎么用 | `const store = createStore(rootReducer)`；`store.dispatch({ type: 'INCREMENT' })`；reducer 返回新 state |
| 原理和工作流程 | 三大原则：(1) 单一数据源——整个应用只有一个 Store，不可有多个；(2) State 只读——唯一改变 state 的方式是 dispatch action，不可直接赋值修改；(3) 纯函数修改——Reducer 必须是纯函数，返回新 state 而非修改旧 state。Redux 的 state 是不可变数据结构 |
| 缺点 | 严格遵守不可变性增加了代码量；单一 Store 在超大型应用中可能变得臃肿 |

### 15. useTransition 的作用是什么

| 维度 | 内容 |
|------|------|
| 是什么 | React 18 的并发特性，将某些状态更新标记为非紧急更新，保持 UI 在耗时更新期间仍然响应 |
| 能做什么 | 在输入搜索、选项卡切换等场景中，将耗时的列表渲染标记为非紧急，优先保证输入框的响应速度 |
| 怎么用 | `const [isPending, startTransition] = useTransition()`；`startTransition(() => { setResults(data) })` |
| 原理和工作流程 | `useTransition` 返回 `[isPending, startTransition]`。`startTransition` 包裹的非紧急更新被 React 标记为低优先级，在后台处理。React 优先处理紧急更新（如输入框输入），空闲时再处理非紧急更新。`isPending` 表示非紧急更新是否仍在处理中，可用于显示 loading 状态。不是用于实现过渡动画或路由过渡 |
| 缺点 | 非紧急更新可能被延迟较长时间，在低性能设备上体验不佳；需配合 `useDeferredValue` 或 Suspense 发挥最佳效果 |

---

## 二、简答题（12 题）

| 维度 | 内容 |
|------|------|
| 是什么 | 覆盖虚拟 DOM、类组件与函数组件对比、Fiber 架构、Hooks 规则、useEffect、Diff 算法、性能优化、setState、Redux 流程、React 18 并发特性、useOptimistic 乐观更新、Server Actions 共 12 个核心知识点 |
| 能做什么 | 检验对 React 核心概念和底层原理的深入理解，要求用文字清晰表达技术原理和设计思路 |
| 怎么用 | 先口述或写出答案再对照原文，重点关注原理阐述的完整性和准确性 |
| 原理和工作流程 | 12 题按知识点分布：虚拟 DOM 原理与优势（1）、类组件与函数组件对比（2）、Fiber 架构设计目标（3）、Hooks 使用规则与原理（4）、useEffect 依赖数组与清理（5）、Diff 算法三大策略（6）、性能优化手段（7）、setState 同步异步（8）、Redux 工作流程（9）、React 18 并发特性（10）、useOptimistic 乐观更新（11）、Server Actions 用法与对比（12） |
| 缺点 | 简答题依赖文字表达能力，答案可能正确但表述不精准；部分题目答案较长，面试中需要记忆关键要点 |

### 1. React 虚拟 DOM 的原理和优势

| 维度 | 内容 |
|------|------|
| 是什么 | 虚拟 DOM 是真实 DOM 的 JavaScript 对象表示，通过 Diff 算法比较新旧树差异并批量更新真实 DOM |
| 能做什么 | 减少真实 DOM 操作次数提升性能；跨平台渲染（Web、Native、Canvas）；支持声明式编程 |
| 怎么用 | React 自动管理，开发者只需声明 UI 状态 |
| 原理和工作流程 | 状态变化时 React 生成新虚拟 DOM 树，通过 Diff 算法（Tree Diff、Component Diff、Element Diff）与旧树比较，计算最小 DOM 变更，批量更新真实 DOM。三大优势：减少 DOM 操作提升性能；虚拟 DOM 是抽象层可渲染到不同平台；声明式编程开发者只需描述 UI 状态 |
| 缺点 | Diff 计算有额外开销；对于简单静态页面，虚拟 DOM 的抽象层增加了不必要的复杂度 |

### 2. 类组件和函数组件的区别

| 维度 | 内容 |
|------|------|
| 是什么 | 类组件通过 `class extends React.Component` 定义，函数组件通过 `function(props)` 定义，两者在七个维度有显著差异 |
| 能做什么 | 函数组件配合 Hooks 可实现类组件的所有功能，且代码更简洁、逻辑复用更灵活 |
| 怎么用 | 类组件：`class Comp extends React.Component { render() { return <div>{this.state.x}</div> } }`；函数组件：`function Comp() { const [x] = useState(0); return <div>{x}</div> }` |
| 原理和工作流程 | 七个维度对比：定义方式（class vs function）、状态管理（`this.state`/`setState` vs `useState`）、生命周期（`componentDidMount` 等 vs `useEffect`）、this 绑定（需要 bind 或箭头函数 vs 无 this）、代码量（较多 vs 较少）、性能（实例化开销 vs 更轻量）、逻辑复用（HOC/Render Props vs 自定义 Hooks） |
| 缺点 | 函数组件中 useEffect 模拟生命周期不如类组件直观；部分老旧第三方库仍依赖类组件 API |

### 3. React Fiber 架构的设计目标和工作原理

| 维度 | 内容 |
|------|------|
| 是什么 | React 16 引入的协调引擎，解决 React 15 Stack Reconciler 递归不可中断导致主线程长时间阻塞的问题 |
| 能做什么 | 将渲染任务拆分为可中断的小工作单元，基于优先级调度保证高优先级更新优先处理 |
| 怎么用 | 开箱即用，React 16+ 默认启用 |
| 原理和工作流程 | 将渲染任务拆分为多个 Fiber 节点（工作单元），通过链表结构（child/sibling/return）支持遍历中断和恢复。双缓冲机制（current 树和 workInProgress 树交替）。工作循环分为 render 阶段（可中断，标记副作用）和 commit 阶段（不可中断，应用 DOM 变更）。基于优先级调度，紧急更新优先处理 |
| 缺点 | 内部实现复杂，调试困难；调度优先级在某些场景下可能导致低优先级更新被推迟过久 |

### 4. Hooks 的使用规则和原理

| 维度 | 内容 |
|------|------|
| 是什么 | Hooks 只能在函数组件顶层调用，不能在条件/循环/嵌套函数中调用，且只能在函数组件或自定义 Hook 中使用 |
| 能做什么 | 确保 Hooks 在每次渲染时以相同顺序调用，保证状态与 Hook 的正确对应 |
| 怎么用 | 始终在函数组件顶层调用 Hooks，不在 `if`/`for` 或嵌套函数中使用 |
| 原理和工作流程 | React 内部使用链表按调用顺序存储 Hooks 状态。每次渲染时按顺序读取链表中的状态。条件调用会破坏调用顺序，导致 Hook 读取到错误的状态，引发不可预测的 bug。`eslint-plugin-react-hooks` 可静态检测违规调用 |
| 缺点 | 限制了 Hooks 的使用灵活性；自定义 Hook 中嵌套调用可能产生深层依赖链，难以追踪 |

### 5. useEffect 的依赖数组和清理函数

| 维度 | 内容 |
|------|------|
| 是什么 | 依赖数组决定 effect 何时重新执行，清理函数在下一次 effect 执行前或组件卸载时调用 |
| 能做什么 | 依赖数组控制副作用的触发时机；清理函数用于取消订阅、清除定时器、取消请求等资源释放 |
| 怎么用 | `useEffect(() => { const sub = subscribe(); return () => sub.unsubscribe() }, [userId])` |
| 原理和工作流程 | React 使用 `Object.is` 比较每个依赖值，有变化则先执行上一次的清理函数，再执行新 effect。清理函数在下一次 effect 执行前或组件卸载时调用。空数组 `[]` 表示依赖从未变化，仅在挂载时执行，卸载时清理。省略依赖数组则每次渲染后都执行 |
| 缺点 | 依赖数组不完整导致闭包陷阱，引用过期变量值；清理函数执行时机可能与预期不符 |

### 6. React Diff 算法的三大策略

| 维度 | 内容 |
|------|------|
| 是什么 | React Diff 算法的三个优化策略：Tree Diff（同级比较）、Component Diff（类型判断）、Element Diff（key 标识） |
| 能做什么 | 将 Diff 复杂度从 O(n^3) 降低到 O(n)，显著提升虚拟 DOM 比较效率 |
| 怎么用 | 开发者无需手动调用，React 内部自动应用 |
| 原理和工作流程 | Tree Diff：只比较同级节点，跨层级移动视为删除+重建，复杂度 O(n)。Component Diff：同类型组件继续比较子树，不同类型直接替换整个子树。Element Diff：通过 key 标识同一层级子节点，判断节点是移动、插入还是删除。三种策略协同将复杂度降至 O(n) |
| 缺点 | 跨层级移动节点会被视为删除重建，效率较低；key 选择不当（如使用数组索引）会导致 Diff 结果错误 |

### 7. React 性能优化手段有哪些

| 维度 | 内容 |
|------|------|
| 是什么 | 一组用于减少不必要的渲染和计算、提升 React 应用性能的技术手段 |
| 能做什么 | 通过 React.memo、useMemo、useCallback、代码分割、虚拟列表等避免不必要的重渲染和计算 |
| 怎么用 | `React.memo(Comp)`、`useMemo(() => compute(), [deps])`、`React.lazy(() => import('./Comp'))` |
| 原理和工作流程 | 八种手段：React.memo 对 props 浅比较跳过无变化渲染；useMemo 缓存昂贵计算；useCallback 缓存函数引用配合 React.memo；React.lazy + Suspense 实现代码分割；虚拟列表（react-window）只渲染可视区域；避免 render 中创建新对象/函数/数组；拆分 Context 避免全局重渲染；使用生产模式构建 |
| 缺点 | 过度使用 React.memo/useMemo/useCallback 增加内存开销和代码复杂度；虚拟列表要求固定高度或额外的高度缓存 |

### 8. setState 是同步还是异步的

| 维度 | 内容 |
|------|------|
| 是什么 | React 18 中 setState 在所有场景下都是异步批处理的，多次调用合并为一次更新 |
| 能做什么 | 减少不必要的重渲染次数，提升应用性能 |
| 怎么用 | 需要同步获取最新状态时用 `flushSync(() => setState(...))` 或在 `useEffect` 中读取更新后的 state |
| 原理和工作流程 | React 18 在所有场景下（事件处理、setTimeout、Promise、原生事件）自动批处理 setState。React 将多次 setState 收集到更新队列中，在当前事件循环结束后统一处理。需要同步获取更新后状态时，使用 `flushSync` 强制同步刷新，或通过 `useEffect` 在状态更新后执行逻辑 |
| 缺点 | setState 的异步行为使调试变得困难，开发者可能困惑为何状态未立即更新；flushSync 会破坏批处理优化 |

### 9. Redux 的工作流程

| 维度 | 内容 |
|------|------|
| 是什么 | Redux 遵循单向数据流：View dispatch Action → Store 交给 Reducer → 生成新 State → View 订阅更新 |
| 能做什么 | 实现可预测的状态管理，状态变更路径清晰可追溯 |
| 怎么用 | `dispatch({ type: 'INCREMENT' })` → reducer 返回 `{ ...state, count: state.count + 1 }` → useSelector 读取新值 |
| 原理和工作流程 | View 通过 `dispatch(action)` 发送 action 对象到 Store。Store 将当前 state 和 action 交给 Reducer 纯函数。Reducer 根据 action.type 计算并返回新 state（不可变方式）。Store 更新状态后通知所有订阅者，View 通过 `useSelector` 或 `subscribe` 获取新状态并重新渲染 |
| 缺点 | 样板代码多，简单操作需要定义 action type、action creator、reducer 分支；中间件（如 redux-thunk）增加了学习曲线 |

### 10. React 18 并发特性有哪些

| 维度 | 内容 |
|------|------|
| 是什么 | React 18 引入的一组并发渲染能力：useTransition、useDeferredValue、Automatic Batching、Suspense 改进、startTransition |
| 能做什么 | 在不阻塞主线程的情况下处理非紧急更新，保持 UI 交互流畅，提升用户体验 |
| 怎么用 | `useTransition()` 标记非紧急更新；`useDeferredValue(value)` 延迟更新值；Suspense 支持 SSR 流式渲染 |
| 原理和工作流程 | useTransition 标记非紧急更新，React 后台处理，优先保证紧急更新响应。useDeferredValue 延迟更新某个值，让出主线程。Automatic Batching 所有场景下自动批处理。Suspense 改进支持 SSR 流式渲染和选择性注水。startTransition 与 useTransition 类似，可在非组件中使用 |
| 缺点 | 并发特性增加了 React 内部复杂度；非紧急更新可能延迟过久影响用户体验；需合理区分紧急和非紧急更新 |

---

## 三、编程题（3 题）

| 维度 | 内容 |
|------|------|
| 是什么 | 三道编程题覆盖自定义 Hook 实现（useDebounce）、React 内部机制模拟（useState）、综合组件开发（防抖搜索组件） |
| 能做什么 | 检验自定义 Hook 编写能力、对 React 底层原理的理解以及综合组件设计能力 |
| 怎么用 | 先独立编码实现，再对照参考答案，重点关注闭包、清理函数、依赖数组等细节 |
| 原理和工作流程 | 题1（useDebounce）：基于 useState + useEffect 实现防抖，核心是定时器管理和清理函数。题2（useState 模拟）：基于闭包和数组实现，核心是 hooks 数组按索引存储状态、闭包捕获 index、render 时重置 hookIndex。题3（防抖搜索）：组合 useDebounce、useState、useEffect、useCallback 实现完整搜索组件 |
| 缺点 | 编程题答案不唯一，参考代码可能存在优化空间；题目侧重算法实现，未覆盖测试和错误边界等工程实践 |

### 1. 实现一个自定义 Hook：useDebounce

| 维度 | 内容 |
|------|------|
| 是什么 | 一个自定义 Hook，对频繁变化的值进行防抖处理，延迟指定时间后返回最终值 |
| 能做什么 | 在搜索输入、窗口 resize 等高频场景中减少不必要的请求或计算 |
| 怎么用 | `const debouncedValue = useDebounce(inputValue, 500)` |
| 原理和工作流程 | 内部使用 `useState` 存储防抖后的值，`useEffect` 监听原始值变化。每次 value 变化时，先通过 cleanup 函数清除上一次的定时器，再设置新定时器延迟 delay 毫秒后更新 debouncedValue。清理函数在下一次 effect 执行前取消定时器，避免过期更新 |
| 缺点 | 防抖延迟期间用户无法看到中间结果；延迟设置过长会导致响应迟钝 |

### 2. 实现一个简单的 useState Hook（基于闭包）

| 维度 | 内容 |
|------|------|
| 是什么 | 基于闭包和数组模拟 React 的 useState Hook，核心是 hooks 数组按索引存储状态 |
| 能做什么 | 深入理解 useState 的底层实现原理，尤其是闭包和调用顺序的重要性 |
| 怎么用 | `const [state, setState] = myUseState(initialValue)`，setState 支持函数式更新 |
| 原理和工作流程 | 维护 `hooks` 数组和 `hookIndex` 索引。每次调用 useState 时闭包捕获当前 index。首次渲染时初始化 hooks[index] 为 initialValue。setState 更新 hooks[index] 后触发重新渲染（render 函数重置 hookIndex 为 0）。支持函数式更新：`typeof newValue === 'function' ? newValue(hooks[index]) : newValue` |
| 缺点 | 简化实现未处理批量更新、优先级调度、Fiber 架构等生产级特性；依赖全局变量而非 React 内部 Fiber 节点 |

### 3. 实现一个带防抖的搜索输入组件

| 维度 | 内容 |
|------|------|
| 是什么 | 一个带防抖、加载状态、错误处理的完整搜索输入组件 |
| 能做什么 | 用户输入关键词后 500ms 防抖自动发起搜索请求，显示加载状态和搜索结果 |
| 怎么用 | `<SearchBox />`，组件内部管理 keyword、results、loading 三个状态 |
| 原理和工作流程 | 组合 useDebounce 自定义 Hook 实现防抖。useCallback 包裹 search 函数避免不必要的重建。useEffect 监听 debouncedKeyword 变化时调用 search。空输入时清空结果。try/catch/finally 处理请求异常和 loading 状态。组件卸载时防抖定时器被清理函数取消 |
| 缺点 | 未处理竞态条件（快速切换关键词时旧请求可能覆盖新请求结果）；使用 fetch 直接请求，未使用请求取消（AbortController） |

---

## 四、场景设计题（2 题）

| 维度 | 内容 |
|------|------|
| 是什么 | 两道场景设计题覆盖全局状态管理方案（Context + useReducer）和虚拟滚动（Virtual Scroll）方案 |
| 能做什么 | 检验架构设计能力和对 React 高级模式的综合运用，评估实际项目中的方案设计水平 |
| 怎么用 | 先理解设计思路和核心原理，再动手实现完整代码，重点关注状态拆分、性能优化和边界处理 |
| 原理和工作流程 | 题1（全局状态管理）：通过 createContext + useReducer + useMemo 构建完整方案，包含 Action 类型定义、Reducer 实现、Provider 封装、自定义 Hook 和 Action Creator。题2（虚拟滚动）：基于可视区域计算，只渲染可视范围内的 DOM 节点，通过 transform 偏移和占位元素模拟滚动 |
| 缺点 | 场景设计题答案多样，参考实现仅是一种方案；Context + useReducer 在频繁更新场景下性能不如 Redux/Zustand |

### 1. 设计一个全局状态管理方案（Context + useReducer）

| 维度 | 内容 |
|------|------|
| 是什么 | 基于 React 原生 API（createContext + useReducer）构建的全局状态管理方案，无需第三方依赖 |
| 能做什么 | 实现用户认证、购物车、主题切换等全局状态管理，Action 类型定义清晰，状态变更可追溯 |
| 怎么用 | `<AppProvider><App /></AppProvider>`，组件内通过 `useAppContext()` 和 `useActions()` 访问 |
| 原理和工作流程 | 8 步构建：定义 Action 类型常量 → 定义初始状态 → 实现 appReducer 纯函数 → 创建 Context → Provider 组件用 useReducer 管理状态 → 自定义 Hook 封装 useContext → Action Creator 辅助函数封装 dispatch → 组件使用。用 useMemo 缓存 value 避免不必要的重渲染 |
| 缺点 | Context 值变化时所有订阅组件都会重渲染，不适用于频繁更新的状态；不如 Redux 有成熟的中间件和 DevTools 支持 |

### 2. 设计一个大型列表的虚拟滚动方案

| 维度 | 内容 |
|------|------|
| 是什么 | 一种只渲染可视区域内 DOM 节点的列表渲染优化方案，通过占位元素和偏移模拟原生滚动 |
| 能做什么 | 在 10000+ 条数据的列表场景中，将 DOM 节点数控制在几十个，避免页面卡顿 |
| 怎么用 | `<VirtualList itemHeight={50} containerHeight={600} data={data} renderItem={renderFn} />` |
| 原理和工作流程 | 核心 4 步：(1) 根据 scrollTop 和 containerHeight 计算可视范围起始索引；(2) 上下各预渲染 overscan 项避免滚动闪烁；(3) 用 `transform: translateY(offsetY)` 将可见项偏移到正确位置（GPU 加速避免重排）；(4) 用总高度 `data.length * itemHeight` 撑开容器模拟原生滚动条。固定高度场景计算简单，动态高度需额外维护高度缓存 |
| 缺点 | 要求每项固定高度（或需维护高度缓存），动态高度场景实现复杂；不支持原生滚动条精确位置；无障碍访问需额外处理 |

---

## 本章学习自检

本节为辅助内容，无五维表格。

---

> [返回原文](./04-React笔面试题集.md) | [返回模块目录](../README.md) | [返回知识导览](../知识导览.md)