# TypeScript 基础与类型系统

> 模块：03-typescript（第3周 TypeScript）
> 定位：基础原理篇
> 推荐阅读时间：60分钟

---

## 一、核心概念

TypeScript 是 JavaScript 的超集，为 JavaScript 添加了静态类型检查，最终编译为纯 JavaScript 运行。它由微软开发和维护，解决了 JavaScript 在大型项目中的类型安全问题。

**TypeScript 的核心优势：**

1. **静态类型检查**：在编译阶段就能发现类型错误，而不是等到运行时才暴露问题
2. **更好的 IDE 支持**：智能提示、自动补全、重构能力大幅提升
3. **代码即文档**：类型本身就是最好的文档，阅读代码更清晰
4. **兼容性好**：完全兼容 JavaScript，可以逐步引入

> **生活化类比**：超市购物——TypeScript 是进门就检查购物清单（编译时类型检查），JavaScript 是结账时才发现拿错了（运行时类型错误）。提前检查省去很多麻烦，不至于推着一车错东西去结账。

---

## 二、底层原理

### 1. 基础类型

TypeScript 提供了 JavaScript 所有基本类型的类型标注：

```typescript
// 字符串
let name: string = "TypeScript";
// 数字
let age: number = 25;
// 布尔值
let isDone: boolean = false;
// 数组
let list: number[] = [1, 2, 3];
let list2: Array<number> = [1, 2, 3];
// 元组 - 固定长度和类型的数组
let tuple: [string, number] = ["hello", 10];
// 枚举
enum Color {
  Red,
  Green,
  Blue
}
let c: Color = Color.Green;
// void - 表示函数没有返回值
function log(): void {
  console.log("hello");
}
// null 和 undefined
let n: null = null;
let u: undefined = undefined;
// never - 表示永远不会发生的值的类型
function error(): never {
  throw new Error("error");
}
// unknown - 未知类型，比 any 安全
let value: unknown = 10;
// any - 任意类型，绕过类型检查
let anyValue: any = "any";
```

### 2. 联合类型和交叉类型

**联合类型（|）**：表示一个值可以是几种类型之一，需要通过类型收窄来使用具体方法。

```typescript
// 联合类型：值可以是 string 或 number
let id: string | number;
id = 123;
id = "abc";

// 需要类型收窄才能使用方法
function printId(id: string | number) {
  if (typeof id === "string") {
    // 这里 TypeScript 知道 id 是 string
    console.log(id.toUpperCase());
  } else {
    // 这里 id 是 number
    console.log(id);
  }
}
```

**交叉类型（&）**：将多个类型合并为一个，新类型拥有所有类型的特性。

```typescript
interface A {
  a: string;
}
interface B {
  b: number;
}
let ab: A & B = { a: "hello", b: 123 };
```

**区别和使用场景：**

| 类型 | 作用 | 使用场景 |
|------|------|----------|
| 联合类型 `|` | 表示"或"的关系 | 一个值可以是多种类型之一 |
| 交叉类型 `&` | 表示"且"的关系 | 合并多个类型，扩展接口 |

### 3. 类型别名 vs 接口

```typescript
// 类型别名
type Point = {
  x: number;
  y: number;
};

// 接口
interface PointInterface {
  x: number;
  y: number;
}
```

**核心区别：**

| 特性 | interface | type |
|------|-----------|------|
| 可以定义联合类型 | ❌ | ✅ |
| 可以定义元组 | ❌ | ✅ |
| 支持自动合并（声明合并） | ✅ | ❌ |
| 可以使用 extends 继承 | ✅ | ✅（使用 &） |
| 可以定义工具类型 | ❌ | ✅ |

**选择建议：**
- 定义对象/类的形状时，优先使用 `interface`
- 需要定义联合类型、元组、工具类型时，使用 `type`

### 4. 类型断言

类型断言告诉 TypeScript "相信我，我知道这个值的类型"。

```typescript
// as 语法（推荐，React JSX 中只能用这个）
let someValue: unknown = "this is a string";
let strLength: number = (someValue as string).length;

// 尖括号语法（不推荐，和 JSX 冲突）
let strLength2: number = (<string>someValue).length;

// const 断言 - 将字面量收窄到最窄类型，并且标记为 readonly
const obj = {
  text: "hello"
} as const;
// obj.text = "world"; // Error，只读
```

### 5. 枚举编译原理

```typescript
// 数字枚举 - 默认从 0 开始递增
enum Direction {
  Up,    // 0
  Down,  // 1
  Left,  // 2
  Right  // 3
}

// 也可以手动指定起始值
enum Direction2 {
  Up = 1,
  Down,  // 2
  Left,  // 3
  Right  // 4
}

// 字符串枚举
enum Direction3 {
  Up = "UP",
  Down = "DOWN",
  Left = "LEFT",
  Right = "RIGHT"
}
```

编译后的 JavaScript 结果：

```javascript
// 数字枚举会生成反向映射
var Direction;
(function (Direction) {
    Direction[Direction["Up"] = 0] = "Up";
    Direction[Direction["Down"] = 1] = "Down";
    Direction[Direction["Left"] = 2] = "Left";
    Direction[Direction["Right"] = 3] = "Right";
})(Direction || (Direction = {}));

// 字符串枚举不会生成反向映射
var Direction3;
(function (Direction3) {
    Direction3["Up"] = "UP";
    Direction3["Down"] = "DOWN";
    Direction3["Left"] = "LEFT";
    Direction3["Right"] = "RIGHT";
})(Direction3 || (Direction3 = {}));
```

结论：数字枚举有反向映射，字符串枚举没有反向映射。

### 6. 泛型基础

泛型让我们创建可以支持多种类型的组件，而不是提前指定好类型。

```typescript
// 泛型函数
function identity<T>(value: T): T {
  return value;
}
// 使用
let output = identity<string>("myString");
let output2 = identity("myString"); // 类型推断

// 泛型接口
interface GenericIdentityFn<T> {
  (arg: T): T;
}

// 泛型约束 - 限制 T 必须满足某个条件
interface Lengthwise {
  length: number;
}
function loggingIdentity<T extends Lengthwise>(arg: T): T {
  console.log(arg.length); // 现在可以访问 length 属性
  return arg;
}

// 泛型默认值
interface Container<T = string> {
  value: T;
}
```

### 7. any vs unknown

| 对比点 | any | unknown |
|--------|-----|---------|
| 类型检查 | 完全关闭 | 保留类型检查 |
| 是否可以直接调用方法 | ✅ | ❌（必须先类型收窄）|
| 安全性 | 不安全 | 相对安全 |

```typescript
let value: any = 10;
value.foo.bar; // OK，不报错，但运行时可能出错

let value2: unknown = 10;
value2.foo.bar; // Error，Object is of type 'unknown'

// unknown 需要类型收窄
if (typeof value2 === "number") {
  // 这里可以安全使用
  console.log(value2.toFixed(2));
}
```

### 8. never 类型使用场景

`never` 表示永远不会发生的值的类型。

场景1：函数永远不会返回（比如抛出错误）

```typescript
function throwError(message: string): never {
  throw new Error(message);
}
```

场景2：穷举检查，确保所有情况都被处理

```typescript
type Shape = Circle | Square | Rectangle;

function getArea(shape: Shape): number {
  switch (shape.type) {
    case "circle":
      return Math.PI * shape.radius ** 2;
    case "square":
      return shape.size ** 2;
    case "rectangle":
      return shape.width * shape.height;
    default:
      // 如果有新增类型没处理，这里会报类型错误
      const _exhaustiveCheck: never = shape;
      throw new Error(`Unknown shape: ${_exhaustiveCheck}`);
  }
}
```

### TypeScript 编译流程

```mermaid
%%{init: {'themeVariables': {'fontSize': '16px'}}}%%
flowchart LR
    A["TS 源码"] --> B["词法分析（Lexer）"]
    B --> C["语法分析（Parser）"]
    C --> D["类型检查（Type Checker）"]
    D --> E["生成 JS 代码（Emitter）"]
    E --> F["输出 .js 文件"]
```

TypeScript 编译过程首先对源码进行**词法分析**，将字符流拆分为 Token；然后通过**语法分析**构建抽象语法树（AST）；接着执行**类型检查**，这也是 TypeScript 相比 JavaScript 最核心的差异环节——在此阶段进行静态类型校验并报告错误；最后通过**代码生成器**将 AST 转换为 JavaScript 代码并输出。类型检查仅在编译时生效，不会影响最终生成的 JS 运行时行为。

> 📖 **参考链接**：
> - [TypeScript官方文档 - 从零开始认识TypeScript](https://www.typescriptlang.org/docs/handbook/typescript-from-scratch.html)
> - [TypeScript官方文档 - 类型推断](https://www.typescriptlang.org/docs/handbook/type-inference.html)
> - [TypeScript官方文档 - 类型收窄（Narrowing）](https://www.typescriptlang.org/docs/handbook/2/narrowing.html)
> - [TypeScript官方文档 - 泛型（Generics）](https://www.typescriptlang.org/docs/handbook/2/generics.html)

---

## 三、实战应用

### 在项目中使用 TypeScript

1. **函数参数类型标注**：给所有函数参数和返回值标注类型

```typescript
function add(a: number, b: number): number {
  return a + b;
}
```

2. **API 响应类型定义**：提前定义接口结构

```typescript
interface User {
  id: number;
  name: string;
  email: string;
  avatar?: string; // 可选属性
}

async function getUser(id: number): Promise<User> {
  const response = await fetch(`/api/users/${id}`);
  return response.json();
}
```

3. **使用联合类型处理多种情况**

```typescript
type Result = SuccessResult | ErrorResult;

interface SuccessResult {
  success: true;
  data: User;
}

interface ErrorResult {
  success: false;
  error: string;
}

function handleResult(result: Result) {
  if (result.success) {
    // 这里可以安全访问 result.data
    console.log(result.data);
  } else {
    // 这里可以访问 result.error
    console.error(result.error);
  }
}
```

4. **泛型在工具函数中的应用**

```typescript
// 通用的请求函数
async function request<T>(url: string): Promise<T> {
  const response = await fetch(url);
  return response.json() as Promise<T>;
}

// 使用
const user = await request<User>("/api/user/1");
```

---

## 四、常见面试题

### Q1: any 和 unknown 的区别是什么？

A: any 完全关闭类型检查，可以任意调用方法，不安全；unknown 保留类型检查，必须经过类型收窄后才能调用方法，更安全。项目中尽量少用 any，优先使用 unknown。

### Q2: interface 和 type 有什么区别？

A: interface 支持声明合并，可以被类实现，可以 extends；type 可以定义联合类型、元组、基本类型别名，不支持声明合并。定义对象形状优先 interface，定义联合/工具类型用 type。

### Q3: 什么是泛型？为什么需要泛型？

A: 泛型是指在定义函数、接口、类的时候不预先指定具体类型，使用的时候再指定类型的一种特性。它可以让组件支持多种类型，同时保持类型安全，避免写重复代码。

### Q4: never 类型有哪些使用场景？

A: 两个主要场景：1) 表示永远不会返回的函数（比如一直循环或抛出错误）；2) 用于穷举检查，确保 switch 处理了所有情况。

### Q5: 联合类型和交叉类型的区别？

A: 联合类型是"或"的关系，一个值可以是几种类型之一；交叉类型是"且"的关系，合并多个类型，需要同时满足所有类型。

---

## 五、避坑指南

| 常见错误 | 现象 | 原因 | 解决方案 |
|---------|------|------|----------|
| 滥用 any | 所有类型都标 any，TypeScript 变成 AnyScript，失去类型检查意义 | 图省事，懒得定义类型 | 尽量用 unknown 代替 any，定义具体类型 |
| 类型断言滥用 | 到处用 `as any` 绕过类型检查 | 类型定义不准确，懒得修正 | 修正类型定义，尽量少用断言 |
| 枚举滥用 | 所有状态都用 enum，增加编译产物 | 习惯用枚举，不知道其他方案 | 简单场景可以用联合类型字面量：`type Color = 'red' | 'green' | 'blue'` |
| 不理解 never | 函数抛出错误还返回 void | 对 never 的语义不理解 | 抛出错误/永远不返回的函数返回值类型用 never |
| 泛型约束错误 | `T extends any` 其实等于没约束，T 还是任意类型 | 误以为需要默认继承 any | 需要什么约束就写什么，不需要就直接 `<T>` |
| const 断言位置错 | `const arr = [1, 2] as const` 正确，`const arr: readonly [1, 2] = ...` 麻烦 | 不知道 as const 的便捷性 | 推荐使用 as const 快速声明只读元组/字面量 |
| 元组越界不报错 | TypeScript 允许越界访问元组（旧版本） | 元组类型设计问题 | TypeScript 3.x+ 已默认禁止元组越界访问，无需额外配置 |
| 联合类型忘记收窄 | 直接调用联合类型上不存在的方法，报类型错误 | 没有让 TypeScript 确认具体类型 | 使用 typeof/instanceof/in 做类型收窄 |

---

> **学习导航**：
> - 返回 [学习路线总览](../README.md)
> - 下一篇：[02-高级类型与工程配置](./02-高级类型与工程配置.md)
> - 面试练习：[TypeScript笔面试题集](./03-TypeScript笔面试题集.md)

---

## 六、本章学习自检

请检查你是否掌握了以下知识点：

- [ ] 理解 TypeScript 的定位和优势
- [ ] 能正确写出所有基础类型的用法
- [ ] 清楚联合类型和交叉类型的区别和使用场景
- [ ] 掌握类型别名和接口的区别，知道什么时候用哪个
- [ ] 理解类型断言和 const 断言的用法
- [ ] 知道枚举的编译结果，清楚数字枚举和字符串枚举的区别
- [ ] 理解泛型的概念，会写泛型函数和泛型约束
- [ ] 清楚 any 和 unknown 的区别，知道为什么 unknown 更安全
- [ ] 掌握 never 类型的两种使用场景
- [ ] 能在实际项目中合理运用这些基础类型知识
