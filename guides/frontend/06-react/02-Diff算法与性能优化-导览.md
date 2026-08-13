# 02-Diff算法与性能优化 导览

> 定位：五维框架浓缩提炼 02-Diff算法与性能优化.md 全部内容小节，快速查阅与复习。
> 用法：每个内容小节对应一张纵向表格，需要深入理解时跳转 [原文](./02-Diff算法与性能优化.md)。
> 前置知识：[React核心与Hooks](./01-React核心与Hooks-导览.md)

---

## 一、核心概念

本节为辅助内容，无五维表格。

---

## 二、底层原理

### 2.1 Diff 算法三大策略

| 维度 | 内容 |
|------|------|
| 是什么 | React Diff 算法基于三个前提假设优化为 O(n) 复杂度：Tree Diff（只比较同级节点，跨层级移动视为删除+重建）、Component Diff（不同类型组件直接替换）、Element Diff（key 标识节点判断可复用性）。 |
| 能做什么 | 将传统树 Diff 的 O(n^3) 复杂度优化为 O(n)，在实际 UI 场景中性能足够。 |
| 怎么用 | 开发者只需要为列表项提供稳定的 key，React 自动执行 Diff 算法。 |
| 原理和工作流程 | Tree Diff：React 只对同一层级的节点进行比较，如果节点跨层级移动，不会尝试复用，直接删除旧节点在新位置重建；Component Diff：同类型组件继续 Diff 子节点，不同类型直接卸载旧组件挂载新组件；Element Diff：同一层级列表通过 key 匹配，判断节点是否可复用，执行移动、插入、删除操作。 |
| 缺点 | 跨层级移动会导致完整重建，性能较差；实际开发中应避免频繁跨层级移动节点。 |

### 2.2 key 的作用和最佳实践

| 维度 | 内容 |
|------|------|
| 是什么 | key 帮助 React 识别同一层级列表中的每个节点，判断节点是否变化、是否可复用，从而决定是移动、插入还是删除。 |
| 能做什么 | 减少不必要的 DOM 重建，提升 Diff 性能；保持组件状态正确。 |
| 怎么用 | 数据有唯一 ID 用 `item.id`，无唯一 ID 用 nanoid 生成，静态列表（不会重排）可用 index，绝对禁止用 `Math.random()`。 |
| 原理和工作流程 | Diff 算法遍历新列表，在旧列表中查找相同 key 的节点，如果找到就复用，根据索引位置判断是否需要移动；使用 index 作为 key 时，列表插入头部会导致所有节点 key 变化，全部更新。 |
| 缺点 | 使用不稳定 key（如 random、index 在重排场景）导致 Diff 结果错误，组件状态错乱，性能下降。 |

### 2.3 调和（Reconciliation）工作流程

| 维度 | 内容 |
|------|------|
| 是什么 | 调和是 React 确定哪些部分需要更新的过程，基于 Fiber 架构分为两个阶段：render 阶段（可中断，beginWork → completeWork 遍历树，标记副作用）和 commit 阶段（不可中断，执行 DOM 更新）。 |
| 能做什么 | 可中断渲染让高优先级任务先执行，减少用户感知卡顿；副作用链表批量处理 DOM 更新。 |
| 怎么用 | 开发者不需要手动参与调和流程，React 自动处理。 |
| 原理和工作流程 | beginWork 阶段：从根 Fiber 开始遍历，对比新旧 Fiber，标记副作用 flags；completeWork 阶段：向上归并，完成 Fiber 节点构建；生成 effectList 包含所有需要 DOM 操作的节点；commit 阶段分为 beforeMutation、mutation、layout 三个子阶段，依次执行 DOM 更新、调用生命周期钩子和 effect 回调。 |
| 缺点 | 调和过程复杂度高，理解和调试困难。 |

---

## 三、实战应用

### 3.1 性能优化手段

| 维度 | 内容 |
|------|------|
| 是什么 | 六种常见性能优化手段：React.memo 浅比较 props 跳过渲染、useMemo 缓存计算结果、useCallback 缓存函数引用、React.lazy + Suspense 代码分割、虚拟列表处理长列表、避免在 render 中创建新引用。 |
| 能做什么 | 减少不必要的重渲染，降低渲染耗时；减少首屏加载体积；处理万级以上长列表，保证滚动流畅。 |
| 怎么用 | `const ExpensiveChild = React.memo(function ExpensiveChild({ data }) { return <div>{/* 渲染 */}</div>; });`；`const filtered = useMemo(() => products.filter(p => p.category === filter), [products, filter]);`；`const handleClick = useCallback(() => setCount(c => c + 1), []);`；`const HeavyComponent = React.lazy(() => import('./HeavyComponent')); <Suspense fallback={<div>加载中...</div>}><HeavyComponent /></Suspense>`。 |
| 原理和工作流程 | React.memo 对 props 进行浅比较，props 不变跳过渲染；useMemo 依赖不变返回缓存计算结果；useCallback 缓存函数引用，配合 React.memo 避免重渲染；React.lazy 将组件拆分为独立 chunk，渲染时动态加载。 |
| 缺点 | React.memo 比较本身也有开销，如果组件每次渲染 props 一定变化，反而增加开销。 |

### 3.2 常见性能问题与解决

| 维度 | 内容 |
|------|------|
| 是什么 | 解决两种常见性能问题：Context 值变化导致所有消费者重渲染、useEffect 依赖数组导致死循环和遗漏依赖。 |
| 能做什么 | Context 拆分避免全局重渲染；正确处理 useEffect 依赖数组避免死循环。 |
| 怎么用 | 拆分 Context：`const ThemeContext = createContext(); const UserContext = createContext();`；或者 `const value = useMemo(() => ({ theme, setTheme, user, setUser }), [theme, user]);` 缓存 value。 |
| 原理和工作流程 | 单个 Context 中任一字段变化都会通知所有订阅该 Context 的组件重渲染；拆分 Context 后，只有订阅变化 Context 的组件重渲染；useMemo 缓存 Context value，引用不变则不会触发重渲染。 |
| 缺点 | Context 拆分增加了代码复杂度，多个 Context 嵌套也影响可读性。 |

---

## 四、常见面试题

### Q1：React 的 Diff 算法为什么是 O(n) 复杂度

| 维度 | 内容 |
|------|------|
| 是什么 | React 通过三个前提假设将 Diff 算法优化为 O(n)：只比较同级节点（Tree Diff）、不同类型组件直接替换（Component Diff）、通过 key 标识节点复用（Element Diff）。 |
| 能做什么 | 在绝大多数实际 UI 场景中，Diff 性能足够好，比传统 O(n^3) 快很多。 |
| 怎么用 | 开发者只需要提供稳定的 key，React 自动应用 Diff 算法。 |
| 原理和工作流程 | 详见原文。 |
| 缺点 | 跨层级移动节点会导致删除重建，性能不如传统 Diff；但实际开发中跨层级移动较少，该优化策略符合实际场景。 |

### Q2：为什么列表渲染需要 key，且不能用 index

| 维度 | 内容 |
|------|------|
| 是什么 | key 帮助 React 识别节点，判断节点是否可复用；使用 index 作为 key，列表顺序变化（如头部插入）会导致所有节点 key 变化，全部重新渲染，组件状态错乱。 |
| 能做什么 | 稳定的 key 帮助 Diff 算法正确识别节点复用，减少 DOM 操作，保持组件状态正确。 |
| 怎么用 | `<div key={item.id}>{item.name}</div>`；`{items.map((item, index) => <div key={index}>{item.name}</div>)}` 只有静态列表（不会重排）可接受。 |
| 原理和工作流程 | 头部插入新项导致原有每个节点的 index 都 +1，key 全部变化，React 认为所有节点都变化，需要全部重建；使用稳定 id 作为 key 只有新增节点需要创建，原有节点复用。 |
| 缺点 | 要求数据有唯一 id，没有 id 需要额外生成，增加开发成本。 |

### Q3：React.memo 和 useMemo 有什么区别

| 维度 | 内容 |
|------|------|
| 是什么 | React.memo 是高阶组件，包裹整个组件，对 props 浅比较，props 不变跳过渲染；useMemo 是 Hook，在组件内部缓存计算结果，依赖不变返回缓存值。 |
| 能做什么 | React.memo 避免子组件不必要的重渲染；useMemo 避免每次渲染重复昂贵计算。 |
| 怎么用 | `const MemoComponent = React.memo(Component);`；`const value = useMemo(() => compute(a, b), [a, b]);`。 |
| 原理和工作流程 | React.memo 在组件更新时浅比较新旧 props，相等则复用上次渲染结果；useMemo 比较依赖数组，依赖不变返回缓存计算结果。 |
| 缺点 | 浅比较本身有开销，不必要的使用反而降低性能。 |

---

## 五、避坑指南

| 维度 | 内容 |
|------|------|
| 是什么 | 聚合了 Diff 与性能优化开发中八个常见错误：使用 index 作为 key、随机数作为 key、在 render 中创建新对象/函数、滥用 useMemo/useCallback、Context 未拆分、useEffect 依赖数组不完整、将整个组件树用 React.memo 包裹、未使用生产模式构建。 |
| 能做什么 | 快速对照排查：使用数据唯一 id 作为 key；使用稳定标识；用 useMemo/useCallback 缓存对象和函数；按业务领域拆分 Context；诚实填写依赖数组；只对渲染开销大的组件使用 React.memo；生产环境构建关闭开发模式检查。 |
| 怎么用 | `<Item key={item.id} data={item} />`；`const style = useMemo(() => ({ color: 'red' }), []);`；`const onClick = useCallback(() => doSomething(), []);`；`const ThemeContext = createContext(); const UserContext = createContext();`。 |
| 原理和工作流程 | index 不稳定，顺序变化导致 key 对应关系错乱，全部重新渲染；随机数每次渲染 key 都变化，全部重建；每次 render 创建新对象/函数，React.memo 浅比较认为变化，导致子组件重渲染；Context 未拆分，一个字段变化所有订阅组件都重渲染。 |
| 缺点 | 性能问题需要 profiling 才能确定，过度优化比不优化更差。 |

---

## 本章学习自检

本节为辅助内容，无五维表格。

---

> [返回原文](./02-Diff算法与性能优化.md) | [返回模块目录](../README.md) | [返回知识导览](../知识导览.md)