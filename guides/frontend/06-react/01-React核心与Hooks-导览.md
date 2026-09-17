# 01-React核心与Hooks 导览

> 定位：五维框架浓缩提炼 01-React核心与Hooks.md 全部内容小节，快速查阅与复习。
> 用法：每个内容小节对应一张纵向表格，需要深入理解时跳转 [原文](./01-React核心与Hooks.md)。
> 前置知识：[HTML核心与语义化](../01-html-css/01-HTML核心与语义化-导览.md)、[语法基础与执行机制](../02-javascript-core/01-语法基础与执行机制-导览.md)、[TypeScript基础与类型系统](../03-typescript/01-TypeScript基础与类型系统-导览.md)

---

## 一、核心概念

本节为辅助内容，无五维表格。

---

### 1.1 声明式编程

| 维度 | 内容 |
|------|------|
| 是什么 | React 采用声明式编程范式，开发者只需要描述 UI 当前应该是什么样子，React 负责将描述转化为 DOM 操作。 |
| 能做什么 | 当状态变化时，React 自动计算最小 DOM 更新，开发者无需手动处理 DOM 增删改查，降低心智负担。 |
| 怎么用 | `function Greeting({ name }) { return <h1>你好，{name}！</h1>; }` 描述 UI，状态变化时 React 自动更新。 |
| 原理和工作流程 | 开发者描述 UI 状态，React 管理从状态到 DOM 的映射；状态变化时生成新的虚拟 DOM 树，通过 Diff 算法找出最小变更，批量更新 DOM。 |
| 缺点 | 开发者无法直接控制 DOM 更新过程，对极致性能优化不够灵活；需要理解 Diff 算法才能写出高性能代码。 |

### 1.2 组件化

| 维度 | 内容 |
|------|------|
| 是什么 | React 将 UI 拆分为独立可复用的组件，每个组件封装自身的结构（JSX）、样式（CSS）和行为（逻辑），通过 props 传递数据。 |
| 能做什么 | 实现高内聚低耦合，便于独立开发、测试和维护；相同组件可以在不同场景复用。 |
| 怎么用 | `function Button({ onClick, children }) { return <button onClick={onClick}>{children}</button>; }` 独立封装按钮组件。 |
| 原理和工作流程 | 组件树与 UI 树结构对应，父组件通过 props 将数据传递给子组件；状态变化时从根组件重新渲染，子组件 props 变化时重新渲染。 |
| 缺点 | 组件拆分粒度过细会增加组件间通信复杂度；拆分不足会导致组件过大难以维护。 |

### 1.3 单向数据流

| 维度 | 内容 |
|------|------|
| 是什么 | React 中数据只能从父组件通过 props 单向传递给子组件，子组件不能直接修改 props，只能通过回调函数通知父组件更新。 |
| 能做什么 | 数据流向清晰，数据追踪简单，避免双向绑定带来的数据流向混乱问题。 |
| 怎么用 | `function Parent() { const [count, setCount] = useState(0); return <Child count={count} onIncrement={() => setCount(count + 1)} />; }`。 |
| 原理和工作流程 | 父组件状态更新 -> 父组件重新渲染 -> props 传递给子组件 -> 子组件重新渲染；子组件不能直接修改 props，需要调用父组件传递的回调函数通知父组件更新状态。 |
| 缺点 | 深层组件需要修改顶层状态时，props 需要逐层传递，产生 prop drilling 问题。 |

---

## 二、底层原理

### 2.1 JSX 的本质

| 维度 | 内容 |
|------|------|
| 是什么 | JSX 是 `React.createElement` 的语法糖，Babel 在编译时将 JSX 转换为 JavaScript 函数调用；React 17+ 引入新 JSX 转换，不再需要手动引入 React。 |
| 能做什么 | 用类似 HTML 的语法编写 React 组件，比手动调用 `React.createElement` 更简洁易读。 |
| 怎么用 | `const element = <h1 className="title">Hello</h1>;` 编译后变为 `jsx('h1', { className: 'title' }, 'Hello');`。 |
| 原理和工作流程 | Babel 在编译阶段将 JSX 语法转换为 React 运行时函数调用；React 运行时将函数调用转换为虚拟 DOM 对象；JSX 不是模板语言，就是 JavaScript 的语法扩展。 |
| 缺点 | 需要编译器（Babel）转换才能运行；初学者需要适应 JavaScript + HTML 混合语法。 |

### 2.2 虚拟 DOM

| 维度 | 内容 |
|------|------|
| 是什么 | 虚拟 DOM 是真实 DOM 的 JavaScript 对象表示，用对象描述 DOM 结构，包含标签名、属性、子节点等信息。 |
| 能做什么 | 通过 Diff 算法比较新旧虚拟 DOM 树，找出最小变更批量更新真实 DOM，减少昂贵的 DOM 操作；支持跨平台渲染（Web、Native、Canvas 等）。 |
| 怎么用 | 开发者编写 JSX，React 自动生成虚拟 DOM，开发者不需要手动创建。 |
| 原理和工作流程 | 状态变化时生成新的虚拟 DOM 树；与旧树通过 Diff 算法比较，计算出最小 DOM 变更；批量执行真实 DOM 更新。 |
| 缺点 | 首次渲染需要生成完整虚拟 DOM 树，性能不如直接操作 DOM；需要额外的 Diff 计算开销。 |

### 2.3 React 18 新特性

| 维度 | 内容 |
|------|------|
| 是什么 | React 18 核心新特性是并发渲染，包括 useTransition（标记非紧急更新）、useDeferredValue（延迟更新值）、自动批处理（所有场景下多次 setState 自动合并）、Suspense 改进。 |
| 能做什么 | 让 React 可以中断渲染，优先处理更紧急的更新，保持 UI 响应性；在耗时更新期间不阻塞用户输入。 |
| 怎么用 | `const [isPending, startTransition] = useTransition(); startTransition(() => setSearchResults(filtered));` 标记搜索结果更新为非紧急。 |
| 原理和工作流程 | 并发渲染允许 React 将渲染任务拆分为可中断的小单元；高优先级更新（如用户输入）可以抢占低优先级更新（如搜索结果渲染）；自动批处理将多次 setState 合并为一次渲染，减少渲染次数。 |
| 缺点 | 并发渲染改变了一些渲染行为，部分依赖同步渲染的旧代码可能需要调整。 |

### 2.4 Fiber 架构深度解析

| 维度 | 内容 |
|------|------|
| 是什么 | React 16 引入的可中断渲染架构，将渲染任务拆分为多个小工作单元（Fiber 节点），通过链表结构支持遍历中断和恢复，实现优先级调度。 |
| 能做什么 | 解决 React 15 Stack Reconciler 递归不可中断导致的长任务阻塞主线程问题，减少页面卡顿和掉帧。 |
| 怎么用 | 开发者无需手动配置，React 自动使用 Fiber 架构。 |
| 原理和工作流程 | Fiber 将树形结构转换为链表（child/sibling/return），使得遍历可以随时中断和恢复；维护两棵 Fiber 树：current（当前显示）和 workInProgress（正在构建）；工作循环分为 render 阶段（可中断，标记副作用）和 commit 阶段（不可中断，应用 DOM 变更）；基于优先级调度，紧急更新优先处理。 |
| 缺点 | 架构复杂度大幅提升；优先级调度本身有调度 overhead。 |

### 2.5 Hooks 原理

| 维度 | 内容 |
|------|------|
| 是什么 | Hooks 使用链表按调用顺序存储状态，每次渲染按顺序读取链表中的状态；不能在条件语句中使用 Hooks 因为条件调用会改变调用顺序导致状态错乱。 |
| 能做什么 | 在函数组件中使用状态和生命周期，替代类组件；通过自定义 Hook 复用状态逻辑。 |
| 怎么用 | 始终在函数组件顶层调用 Hooks，条件逻辑放在 Hooks 调用之后；`if (condition) { const [state, setState] = useState(0); }` → ❌ 错误。 |
| 原理和工作流程 | React 内部用 memoizedState 数组（或链表）存储每个 Hook 的状态，按调用顺序索引；每次渲染重新按顺序读取，条件调用导致索引错位，读取到错误的状态；useState 简化实现：维护状态数组和 cursor，每次渲染 cursor 递增。 |
| 缺点 | 规则限制较多，必须使用 ESLint 规则检查；闭包陷阱（useEffect 捕获过期 state）是常见问题。 |

### 2.6 useMemo 和 useCallback

| 维度 | 内容 |
|------|------|
| 是什么 | useMemo 缓存计算结果，依赖不变时返回缓存值；useCallback 缓存函数引用，依赖不变时返回同一个函数引用；useCallback 是 useMemo 的语法糖。 |
| 能做什么 | 配合 React.memo 使用，避免子组件不必要的重渲染；缓存昂贵计算结果避免每次渲染重复计算。 |
| 怎么用 | `const expensiveValue = useMemo(() => compute(count), [count]);`；`const handleClick = useCallback(() => setCount(c => c + 1), []);`。 |
| 原理和工作流程 | useMemo 在依赖不变时直接返回上一次计算结果；依赖变化时重新计算并缓存新结果；useCallback 缓存函数引用，依赖不变时函数引用不变，React.memo 浅比较 props 不会判定为变化，跳过重渲染。 |
| 缺点 | 缓存本身有内存开销，滥用会降低性能；每个 Hook 都需要维护依赖数组，增加代码复杂度。 |

---

## 三、实战应用

### 3.1 自定义 Hook 封装

| 维度 | 内容 |
|------|------|
| 是什么 | 将可复用的状态逻辑提取到自定义 Hook 中，如 `useLocalStorage` 封装 localStorage 读写，每个组件调用时创建独立状态。 |
| 能做什么 | 在多个组件间复用状态逻辑，比 HOC 和 Render Props 更简洁，没有组件嵌套。 |
| 怎么用 | `function useLocalStorage(key, initialValue) { const [value, setValue] = useState(() => { const item = localStorage.getItem(key); return item ? JSON.parse(item) : initialValue; }); useEffect(() => localStorage.setItem(key, JSON.stringify(value)), [key, value]); return [value, setValue]; }`。 |
| 原理和工作流程 | 自定义 Hook 是普通函数，可以调用其他 Hooks；每个组件调用自定义 Hook 时，获得独立的状态和副作用，不会共享状态；Hooks 规则同样适用于自定义 Hook。 |
| 缺点 | 自定义 Hook 不能使用条件判断，和普通 Hooks 规则一样；多个自定义 Hook 嵌套时调试复杂。 |

### 3.2 并发特性实战

| 维度 | 内容 |
|------|------|
| 是什么 | useTransition 标记非紧急更新，保持 UI 在耗时搜索和过滤更新期间仍然响应，用户输入不会卡顿。 |
| 能做什么 | 让紧急更新（用户输入）优先响应，非紧急更新（搜索结果渲染）可以延迟，提升交互体验。 |
| 怎么用 | `const [query, setQuery] = useState(''); const [isPending, startTransition] = useTransition(); const [results, setResults] = useState([]); function handleChange(e) { setQuery(e.target.value); startTransition(() => setResults(filterData(query)); }`。 |
| 原理和工作流程 | useTransition 将 startTransition 包裹的更新标记为低优先级，React 可以被更紧急的更新抢占；低优先级更新在后台进行，显示 pending 状态给用户反馈；不会阻塞用户输入。 |
| 缺点 | 并发特性仅在 React 18+ 支持；低优先级更新可能被频繁打断，一直得不到完成。 |

---

## 四、常见面试题

### Q1：React 18 中 setState 是同步还是异步的

| 维度 | 内容 |
|------|------|
| 是什么 | React 18 中，所有场景下 setState 都是异步批处理，多次 setState 会自动合并为一次更新；如果需要同步获取最新状态，可以使用 `flushSync`。 |
| 能做什么 | 自动批处理减少不必要的重渲染，提升性能；flushSync 满足需要同步获取最新状态的特殊场景。 |
| 怎么用 | `flushSync(() => setCount(c => c + 1)); console.log(count);` 此时 DOM 已更新。 |
| 原理和工作流程 | React 18 引入自动批处理，无论在 setTimeout、Promise 还是原生事件中，多次 setState 都会自动批处理，只触发一次渲染；flushSync 强制 React 立即同步执行更新。 |
| 缺点 | flushSync 强制同步更新会打断批处理优化，降低性能。 |

### Q2：Fiber 架构中 render 阶段和 commit 阶段的区别

| 维度 | 内容 |
|------|------|
| 是什么 | render 阶段是可中断的，React 遍历 Fiber 树并标记副作用（增删改）；commit 阶段是不可中断的，React 将标记的副作用应用到真实 DOM。 |
| 能做什么 | render 阶段可中断让高优先级任务优先执行；commit 阶段不可中断保证 UI 一致性，不会出现半更新状态。 |
| 怎么用 | 开发者无需手动干预，React 自动分阶段执行。 |
| 原理和工作流程 | render 阶段遍历 Fiber 树，进行 Diff 对比，标记每个 Fiber 节点的副作用（Placement、Update、Deletion）；commit 阶段根据副作用标记执行真实 DOM 操作，调用生命周期钩子和 useEffect 回调。 |
| 缺点 | render 阶段可能被多次中断重新执行，增加了总执行时间。 |

### Q3：如何避免 useEffect 中的闭包陷阱

| 维度 | 内容 |
|------|------|
| 是什么 | useEffect 捕获渲染时的 state 值，如果依赖数组遗漏，会一直使用初始值，导致拿到过期 state 称为闭包陷阱。 |
| 能做什么 | 三种解决方案：将依赖变量加入依赖数组；使用函数式更新 `setCount(c => c + 1)`；使用 `useRef` 保存最新值。 |
| 怎么用 | `// 方案一：函数式更新 setInterval(() => setCount(c => c + 1), 1000); // 方案二：useRef 保存 const countRef = useRef(count); countRef.current = count; useEffect(() => { const timer = setInterval(() => setCount(countRef.current + 1), 1000); }, []);`。 |
| 原理和工作流程 | useEffect 闭包捕获的是渲染时的作用域变量；依赖不变 effect 不会重新执行，所以一直捕获旧值；函数式更新基于上一次状态计算新状态，不需要依赖；useRef 的 current 可以保存最新值，每次读取都是最新。 |
| 缺点 | 依赖数组遗漏导致的问题在开发模式下有 ESLint 警告，需要开启警告才能尽早发现。 |

---

## 五、避坑指南

| 维度 | 内容 |
|------|------|
| 是什么 | 聚合了 React Hooks 开发中八个常见错误：条件语句中使用 Hooks、useEffect 依赖数组遗漏、useEffect 回调直接 async、useCallback 依赖空数组但使用 state、滥用 useMemo 缓存简单计算、每次 render 都创建新对象/函数、useLayoutEffect 执行耗时操作、Context 值变化导致全局重渲染。 |
| 能做什么 | 快速对照排查：始终在函数顶层调用 Hooks；开启 ESLint `react-hooks/exhaustive-deps` 规则检查；useEffect 内部定义 async 函数再调用；将状态加入依赖数组；仅对昂贵计算使用 useMemo；使用 useMemo/useCallback 缓存对象和函数；耗时操作移到 useEffect；拆分 Context 避免全局重渲染。 |
| 怎么用 | `const [a, setA] = useState(0); const [b, setB] = useState(0); if (condition) { // ❌ if 中调用 Hooks }` → 正确：`const [a, setA] = useState(0); const [b, setB] = useState(0); if (condition) { // 使用 a 和 b， Hooks 已经声明 }`。 |
| 原理和工作流程 | Hooks 依赖调用顺序存储在链表中，条件调用导致顺序变化，索引错位读取错误状态；useEffect 要求回调返回清理函数，async 函数返回 Promise 不是清理函数；每次 render 创建新对象/函数，React.memo 浅比较判定为变化导致重渲染。 |
| 缺点 | 需要开发者遵守 Hooks 规则，规则违反导致的问题不易调试。 |

---

## React Server Components（RSC）

| 维度 | 内容 |
|------|------|
| 是什么 | React Server Components（RSC）是 React 18 引入的一种新组件类型，在服务端渲染为特殊的 RSC Payload 格式（JSON），流式传输到客户端后由 React 调和更新 DOM，无需水合（Hydration）。与 SSR 互补而非替代。 |
| 能做什么 | 服务端组件可直接访问数据库和文件系统，减少客户端 JS Bundle（零 KB），简化数据获取（不用 useEffect/useState）；`'use client'` 指令标记客户端组件边界；与 Next.js 13+ App Router 深度集成。 |
| 怎么用 | 默认所有组件为服务端组件，需要交互时添加 `'use client'` 指令；服务端组件直接 `async/await` 获取数据；客户端组件通过 `'use client'` 声明后可使用全部 Hooks 和事件处理器。 |
| 原理和工作流程 | 服务端渲染 RSC → 生成 RSC Payload 流 → 流式传输到客户端 → React 客户端运行时解析 Payload、渲染客户端组件、调和 DOM。服务端组件不能使用 Hooks/事件/浏览器 API，Props 必须可序列化。 |
| 缺点 | 增加了组件模型的复杂度（需要区分服务端/客户端组件）；`'use client'` 边界规则需要学习成本；服务端组件无法传递函数等不可序列化的值给客户端组件。 |

---

## React 19 新特性

### use() API

| 维度 | 内容 |
|------|------|
| 是什么 | React 19 引入的全新 API，可在渲染期间读取 Promise 和 Context，打破了 Hooks 必须在顶层调用的限制，可在条件语句和循环中使用。 |
| 能做什么 | 读取 Promise 时配合 Suspense 实现声明式数据获取，无需 useEffect + useState 组合；读取 Context 时不受调用位置限制，简化条件渲染逻辑。 |
| 怎么用 | `const user = use(fetchUser(id))` 读取 Promise（Promise 未 resolve 时 Suspense 显示 fallback）；`const theme = use(ThemeContext)` 读取 Context，可在 if 语句中调用。 |
| 原理和工作流程 | `use()` 接收 Promise 时，React 在 Promise resolve 前暂停该组件的渲染，最近的 Suspense 边界显示 fallback；Promise resolve 后恢复渲染。读取 Context 类似 useContext，但不受 Hooks 规则限制。 |
| 缺点 | 需要配合 Suspense 使用，不熟悉的开发者可能产生多层 Suspense 嵌套；与 React 18 之前的渲染模式不兼容。 |

### useOptimistic() 乐观更新

| 维度 | 内容 |
|------|------|
| 是什么 | React 19 内置的乐观更新 Hook，在异步操作完成前立即更新 UI 显示预期结果，操作失败时 React 自动回滚到原始状态，无需手动管理临时状态和回滚逻辑。 |
| 能做什么 | 实现即时 UI 反馈（发送消息、点赞、更新配置等），代码量大幅减少，不再需要手动 try/catch 回滚。 |
| 怎么用 | `const [optimisticState, addOptimistic] = useOptimistic(state, (currentState, optimisticValue) => [...currentState, optimisticValue])`；调用 `addOptimistic(newValue)` 立即更新乐观状态；请求成功后用 `setState` 替换真实数据。 |
| 原理和工作流程 | 用户触发操作 → `addOptimistic()` 立即更新乐观状态（临时覆盖层）→ 同时发起异步请求 → 请求成功用 `setState()` 替换为真实数据 → 请求失败 React 自动回滚乐观状态。乐观状态不影响真实 state。 |
| 缺点 | 只适用于更新操作，不适用于创建和删除场景的状态回滚；需要确保乐观更新的数据格式与真实数据一致。 |

### useActionState() 和 useFormStatus()

| 维度 | 内容 |
|------|------|
| 是什么 | React 19 为表单处理引入的两个专用 Hook：`useActionState` 管理表单 Action 的完整状态（state、pending、error），`useFormStatus` 在子组件中读取父级 `<form>` 的提交状态。 |
| 能做什么 | `useActionState` 替代手动 onSubmit + useState 的表单管理模式；`useFormStatus` 允许将提交按钮提取为独立组件，仍然能获取表单的 pending 状态。 |
| 怎么用 | `useActionState`：`const [state, formAction, isPending] = useActionState(updateProfile, initialState)`，action 函数接收 `(prevState, formData)`；`useFormStatus`：`const { pending, data, method } = useFormStatus()`（必须在 `<form>` 子组件中调用）。 |
| 原理和工作流程 | `useActionState` 包装 action 函数，自动管理 pending 状态和返回值；`useFormStatus` 通过 React 内部 context 读取最近的 `<form>` 提交状态，返回 pending、data、method、action 四个字段。 |
| 缺点 | `useActionState` 需要配合 `<form action>` 使用；`useFormStatus` 必须在 `<form>` 的子组件中调用，有一定的组件结构限制。 |

### Server Actions（'use server'）

| 维度 | 内容 |
|------|------|
| 是什么 | React 19 引入的服务端函数调用机制，使用 `'use server'` 指令标记的函数可以直接在客户端组件中调用，由 React 和框架自动处理序列化和网络传输，无需手动创建 API 路由。 |
| 能做什么 | 零 API 层实现客户端到服务端的函数调用，直接在服务端操作数据库、文件系统；支持 form action 和程序化调用（startTransition + async）两种方式；自动处理 CSRF 安全令牌。 |
| 怎么用 | 定义：`'use server'; export async function createPost(formData) { ... }`；表单调用：`<form action={createPost}>`；程序化调用：`startTransition(() => createPost(formData))`；传参：`deletePost.bind(null, postId)`。 |
| 原理和工作流程 | 客户端调用时 React 将函数参数序列化后通过 POST 请求发送到服务端；服务端执行函数后将结果序列化返回；form action 支持渐进式增强，JS 加载前仍可提交；配合 `revalidatePath` 实现缓存更新。 |
| 缺点 | 目前主要依赖 Next.js 等框架支持，独立使用时需要自定义 RSC 服务器；不适合需要实时响应的场景（如 WebSocket）。 |

### React 19 与 React 18 对比

| 维度 | 内容 |
|------|------|
| 是什么 | React 19 在 React 18 基础上新增了 `use()`、`useOptimistic()`、`useActionState()`、`useFormStatus()`、Server Actions 等特性，并优化了水合错误报告、ref 转发、资源预加载、Document Metadata 等方面。 |
| 能做什么 | 简化异步数据获取（`use()` 替代 useEffect）、内置乐观更新、声明式表单管理、无 API 层的全栈调用；ref 直接作为 prop 传递无需 forwardRef；内置 `<title>` `<meta>` 组件替代 react-helmet。 |
| 怎么用 | 升级 `react` 和 `react-dom` 到 19.x；新项目直接使用 `createRoot` 渲染；逐步采用 `use()` 替代 useEffect 数据获取，表单场景使用 `useActionState` + `useFormStatus`。 |
| 原理和工作流程 | React 19 保持 React 18 的并发渲染架构，新增服务端函数调用协议（Server Actions）、渲染期间读取 Promise 的能力（`use()`）、乐观状态管理（`useOptimistic()`）。10 项关键改进涵盖异步数据、表单、全栈、ref、样式、资源加载等。 |
| 缺点 | 部分新特性需要框架支持（如 Next.js 14+）；`use()` 的 Suspense 模式需要团队适应；React 19 生态尚在完善中，部分第三方库可能未完全适配。 |

---

## 错误边界、Portals 与进阶 Hooks

### 错误边界（Error Boundary）

| 维度 | 内容 |
|------|------|
| 是什么 | 一个类组件，用于捕获其**子组件树**在渲染、生命周期方法和构造函数中抛出的错误并渲染降级 UI，避免整页白屏；依赖 `static getDerivedStateFromError` 和 `componentDidCatch` 两个生命周期。 |
| 能做什么 | 隔离局部错误，出错时只卸载出错子树并展示 fallback；在 `componentDidCatch` 中做错误上报，配合全局 `window.onerror` 形成双层防护。 |
| 怎么用 | `class ErrorBoundary extends React.Component { static getDerivedStateFromError(e) { return { hasError: true }; } componentDidCatch(e, info) { report(e, info.componentStack); } render() { return this.state.hasError ? <Fallback /> : this.props.children; } }`；或用 `react-error-boundary` 的 `<ErrorBoundary FallbackComponent={Fallback} onError={...} onReset={...}>`。 |
| 原理和工作流程 | 子树渲染抛错后沿组件树向上冒泡，找到最近的错误边界；React 先调用 render 阶段的静态方法 `getDerivedStateFromError` 拿到降级 state（必须是纯函数），再在 commit 阶段调用 `componentDidCatch` 执行上报副作用。若整棵树都没有边界，React 卸载整棵树。**函数组件无法实现**：错误边界需要在组件自身 render 之前介入，而 Hooks 在 render 内部执行，且官方没有等价的 `useErrorBoundary`。 |
| 缺点 | 捕获不到事件处理器错误、异步代码（`setTimeout` / `Promise`）、SSR 错误、边界自身抛出的错误以及水合不匹配；只能包裹子树，粒度需要人工规划；每个边界都要处理 reset，否则用户只能刷新页面。 |

### Portals（传送门）

| 维度 | 内容 |
|------|------|
| 是什么 | `createPortal(children, domNode, key?)` 把子节点渲染到 DOM 树中另一个位置的节点下，但在 React 组件树中仍保留在原位置。 |
| 能做什么 | 让模态框、抽屉、Tooltip、下拉菜单、Toast 脱离父级 `overflow: hidden` / `transform` / `z-index` 层叠上下文的裁剪与限制；Context、props、ref 仍按 React 树正常传递。 |
| 怎么用 | `import { createPortal } from 'react-dom'; createPortal(<div className="modal-mask" onClick={onClose}>{children}</div>, document.body)`。 |
| 原理和工作流程 | Fiber 树记录组件关系，真实 DOM 的挂载位置由 `domNode` 决定，React 在 commit 的 mutation 子阶段把 Portal 子树的 DOM 插入 `domNode`。React 17+ 把事件监听器统一挂在 root container 上、通过 Fiber 树模拟冒泡，因此 **Portal 内的事件仍沿 React 组件树冒泡**到父组件，而不是沿真实 DOM 树。 |
| 缺点 | 事件冒泡行为与 DOM 直觉相反，需要在浮层内 `stopPropagation`；CSS 继承链从 `document.body` 重新开始，父级字体 / 颜色可能丢失；SSR 下 `document` 不存在需做守卫；无障碍焦点管理（焦点陷阱、Esc 关闭）需自行实现。 |

### useImperativeHandle

| 维度 | 内容 |
|------|------|
| 是什么 | `useImperativeHandle(ref, createHandle, dependencies?)` 自定义暴露给父组件的 ref 值，把默认的「暴露真实 DOM 节点」替换为「暴露一组受控的命令式方法」。 |
| 能做什么 | 在保持内部 DOM 封装的前提下，向父组件暴露聚焦、滚动、播放控制、Canvas 绘制等一次性动作能力。 |
| 怎么用 | `const FancyInput = forwardRef((props, ref) => { const inputRef = useRef(null); useImperativeHandle(ref, () => ({ focus: () => inputRef.current.focus() }), []); return <input ref={inputRef} {...props} />; });` 父组件通过 `inputApi.current.focus()` 调用。 |
| 原理和工作流程 | 必须配合 `forwardRef`（React 19 起 ref 可直接作为 prop 传递），执行时机与 `useLayoutEffect` 相同，在 layout 子阶段把 `createHandle()` 的返回值赋给父组件的 `ref.current`，因此父组件拿到的是自定义对象而非 DOM 节点。 |
| 缺点 | 绕过单向数据流，父组件可直接调用子组件方法，调用顺序敏感、可测试性差；`createHandle` 依赖数组写错会捕获过期值；只适合表达「一次性动作」，不适合表达「持续状态」，滥用会让组件难以维护。 |

### useSyncExternalStore

| 维度 | 内容 |
|------|------|
| 是什么 | `useSyncExternalStore(subscribe, getSnapshot, getServerSnapshot?)` 用于订阅 React 之外的外部数据源，并保证在并发渲染下读到一致快照，避免 tearing（撕裂）。 |
| 能做什么 | 安全订阅浏览器 API（`navigator.onLine`、`matchMedia`、`localStorage`）与自定义 store；是 `react-redux` v8+ `useSelector`、Zustand 等库订阅机制的底层实现；天然支持 SSR 快照。 |
| 怎么用 | `useSyncExternalStore(subscribe, () => navigator.onLine, () => true)`；`subscribe` 需定义在组件外保证引用稳定，`getSnapshot` 必须返回缓存过的不可变值，`getServerSnapshot` 用于 SSR。 |
| 原理和工作流程 | 并发渲染下一次渲染可能被拆成多个时间片，若中途外部 store 变化，同一次渲染的不同部分会读到不同值（tearing）。`useSyncExternalStore` 在渲染期间持续比对 `getSnapshot()` 返回值，发现变化就丢弃当前渲染重新开始，保证同一帧所有组件读到同一份快照；相比 `useEffect` 订阅，它在渲染阶段即可取值，无首屏闪烁，且订阅引用稳定时不会反复订阅。 |
| 缺点 | 快照变化时可能触发同步强制更新，牺牲部分并发收益；`getSnapshot` 返回新对象会导致无限渲染；`subscribe` 每次渲染传新函数会反复订阅；比 `useState` + `useEffect` 写法更繁琐，只适合外部数据源。 |

### 受控组件与非受控组件

| 维度 | 内容 |
|------|------|
| 是什么 | 受控组件的值由 React state 驱动（`value` + `onChange`，React 是唯一数据源）；非受控组件的值由 DOM 自己维护，React 通过 `ref` 读取，初始值用 `defaultValue` / `defaultChecked` 指定。 |
| 能做什么 | 受控适合实时校验、输入联动、字符计数、按钮禁用等需要每次输入拿到最新值的场景；非受控适合一次性提交的大型表单、`<input type="file" />`、集成第三方非 React 组件、性能敏感的高频输入。 |
| 怎么用 | 受控：`<input value={v} onChange={e => setV(e.target.value)} />`；非受控：`<input name="x" defaultValue="张三" />` + `new FormData(formRef.current)`；重置非受控表单用 `<form key={formVersion}>` 强制重建。 |
| 原理和工作流程 | 受控组件每次输入触发 `setState` → 组件重渲染 → 新 `value` 写回 DOM，React 内部用 value tracker 记录 DOM 值以避免重复设置造成光标跳动；只传 `value` 不传 `onChange` 时 React 会将其设为只读并告警。`defaultValue` / `defaultChecked` 仅在首次挂载生效，之后 prop 变化不会同步到 DOM。性能优化方向：state 下沉到字段级组件、`useDeferredValue` / `useTransition` 降优先级、`React.memo` 拆分字段、改用非受控 + ref、使用 `react-hook-form`。 |
| 缺点 | 受控组件每次按键都触发重渲染，字段多或 state 提升过高时输入卡顿；非受控组件状态不受 React 掌控，无法做实时校验与联动，`defaultValue` 后续变化不生效容易踩坑；受控 / 非受控混用时状态来源分散，提交时需用 `FormData` 与 state 分别读取。 |

---

## 本章学习自检

本节为辅助内容，无五维表格。

---

> [返回原文](./01-React核心与Hooks.md) | [返回模块目录](../README.md) | [返回知识导览](../知识导览.md)