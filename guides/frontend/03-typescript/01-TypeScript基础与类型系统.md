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

## 补充：类型守卫与类型收窄

### 1. 概念定义

**类型收窄（Narrowing）**：TypeScript 在控制流分析中，根据条件判断把一个「宽」类型（如联合类型 `string | number`）缩小为「窄」类型（如 `string`）的过程。收窄只发生在**编译期**，不会生成任何运行时代码。

**类型守卫（Type Guard）**：能够触发类型收窄的表达式或函数，可分为两类：

| 类别 | 形式 | 适用场景 |
|------|------|---------|
| 内置守卫 | `typeof`、`instanceof`、`in`、字面量相等比较、真值判断、`Array.isArray` | 判断基本类型、类实例、属性存在性 |
| 自定义守卫 | 类型谓词 `x is T`、断言函数 `asserts x is T` | 复杂业务判断（如「是不是合法的订单对象」） |

### 2. 底层原理

TypeScript 的类型检查器（Checker）在遍历 AST 时会为每个「引用」维护一个 **flow type**（控制流类型）。当代码出现分支（`if`、`switch`、`&&`、`??`、三元、`throw`、`return`）时，检查器按控制流图（Control Flow Graph，CFG）分别计算每个分支内的类型，这个过程就是收窄。

几个关键机制：

- `typeof` 守卫只识别固定的 8 个字符串：`"string"`、`"number"`、`"bigint"`、`"boolean"`、`"symbol"`、`"undefined"`、`"object"`、`"function"`。由于运行时 `typeof null === "object"`，所以 `typeof x === "object"` 只能把 `x` 收窄为 `object | null`。
- `in` 守卫要求左侧是属性名（字符串字面量），右侧是对象类型，它按「属性是否存在」把联合类型分流。
- `instanceof` 依赖构造函数的 `prototype`，因此只能用于类/构造函数，不能用于接口（接口没有运行时实体）。
- **可辨识联合（discriminated union）** 的判别属性必须是「单元类型」——字符串字面量、数字字面量、布尔字面量、`null`、`undefined`，或它们的联合（`boolean` 等价于 `true | false`，因此也可以作判别属性）。不能是 `string`、`number` 这类宽类型，否则无法分流。
- **断言函数**（TS 3.7+）与类型谓词的区别：类型谓词把判断结果返回给调用方，断言函数则在内部不满足条件时直接抛错，从而让**后续所有代码**都处于收窄后的类型中。
- TS 4.4+ 支持**别名条件（aliased conditions）**：把条件表达式存进 `const` 变量后，再用这个变量做判断同样能收窄；TS 4.6+ 还支持对解构出的判别属性做收窄。

### 3. 代码示例

```typescript
// ========== 1. typeof：用于基本类型 ==========
function format(value: string | number | boolean): string {
  if (typeof value === "string") {
    return value.toUpperCase(); // value: string
  }
  if (typeof value === "number") {
    return value.toFixed(2); // value: number
  }
  return value ? "真" : "假"; // value: boolean
}

// typeof null === "object"，所以 object 分支里仍然可能为 null
function readId(value: unknown): number | undefined {
  if (typeof value === "object") {
    // 此时 value 的类型是 object | null，必须先排除 null
    if (value !== null && "id" in value && typeof value.id === "number") {
      return value.id;
    }
  }
  return undefined;
}
```

```typescript
// ========== 2. instanceof：用于类实例 ==========
class ApiError extends Error {
  constructor(public status: number, message: string) {
    super(message);
  }
}

function handleError(err: unknown): string {
  if (err instanceof ApiError) {
    return `接口错误 ${err.status}: ${err.message}`; // err: ApiError
  }
  if (err instanceof Error) {
    return err.message; // err: Error
  }
  return String(err); // err: unknown
}
```

```typescript
// ========== 3. in：按属性存在性分流 ==========
interface Admin { name: string; permissions: string[] }
interface Guest { name: string; expiresAt: Date }

function describe(user: Admin | Guest): string {
  if ("permissions" in user) {
    return `管理员，权限数：${user.permissions.length}`; // user: Admin
  }
  return `访客，过期时间：${user.expiresAt.toISOString()}`; // user: Guest
}
```

```typescript
// ========== 4. 字面量收窄 / 真值收窄 / 相等收窄 ==========
type Status = "idle" | "loading" | "success" | "error";

function render(status: Status, data?: string): string {
  if (status === "success") {
    // status 收窄为 "success"（字面量收窄）
  }
  if (data) {
    // 真值收窄会剔除 undefined、null、0、NaN、""、false
    return data.toUpperCase(); // data: string
  }
  return status;
}

// Array.isArray 是内置类型守卫，常用于 unknown 入参
function normalize(input: string | string[]): string[] {
  if (Array.isArray(input)) {
    return input.map((s) => s.trim()); // input: string[]
  }
  return [input.trim()]; // input: string
}
```

```typescript
// ========== 5. 自定义类型守卫（x is T）==========
interface Cat { meow(): void }
interface Dog { bark(): void }

// 返回值必须是 boolean；谓词类型必须可赋值给参数类型
// 注意：TS 不会校验函数体实现是否正确，写错会埋下运行时隐患
function isCat(animal: Cat | Dog): animal is Cat {
  return typeof (animal as Cat).meow === "function";
}

function play(animal: Cat | Dog): void {
  if (isCat(animal)) {
    animal.meow(); // animal: Cat
  } else {
    animal.bark(); // animal: Dog（else 分支被排除 Cat）
  }
}

// 入参是 unknown 时，谓词把类型"注入"进来，这是最常用的形态
function isNonNullString(value: unknown): value is string {
  return typeof value === "string" && value.length > 0;
}
```

```typescript
// ========== 6. 断言函数（asserts x is T）==========
// 必须显式标注返回类型，函数不能有返回值（返回 void）
function assertIsString(value: unknown): asserts value is string {
  if (typeof value !== "string") {
    throw new TypeError(`期望 string，实际收到 ${typeof value}`);
  }
}

function handleInput(input: unknown): string {
  assertIsString(input);
  // 断言之后，后面的所有代码都把 input 当作 string
  return input.toUpperCase();
}

// asserts x（不带 is）：只断言真值，剔除 null/undefined/0/""/false
function assertTruthy<T>(value: T): asserts value is NonNullable<T> {
  if (value === null || value === undefined) {
    throw new Error("值不能为空");
  }
}

// 箭头函数也能做断言函数，但必须给变量显式标注类型
const assertIsNumber: (value: unknown) => asserts value is number = (value) => {
  if (typeof value !== "number") throw new TypeError("不是数字");
};
```

```typescript
// ========== 7. 可辨识联合与穷尽性检查 ==========
interface Circle { kind: "circle"; radius: number }
interface Square { kind: "square"; size: number }
interface Rect { kind: "rect"; width: number; height: number }

type Shape = Circle | Square | Rect;

function area(shape: Shape): number {
  switch (shape.kind) {
    case "circle":
      return Math.PI * shape.radius ** 2; // shape: Circle
    case "square":
      return shape.size ** 2; // shape: Square
    case "rect":
      return shape.width * shape.height; // shape: Rect
    default:
      // 若上面漏掉某个分支，shape 不会收敛为 never，这一行会编译报错
      const exhaustive: never = shape;
      throw new Error(`未处理的形状：${JSON.stringify(exhaustive)}`);
  }
}

// 把穷尽性检查抽成工具函数，可读性更好
function assertNever(value: never): never {
  throw new Error(`未处理的分支：${JSON.stringify(value)}`);
}

// TS 4.4+ 别名条件：条件存进 const 变量后依然能收窄
function isRound(shape: Shape): boolean {
  const round = shape.kind === "circle";
  if (round) {
    return shape.radius > 0; // shape 已收窄为 Circle
  }
  return true;
}
```

### 4. 面试常见问法

- **Q1：`typeof` 能收窄哪些类型？为什么 `typeof x === "object"` 之后还要判 `null`？**
  A：`typeof` 只识别 `"string"`、`"number"`、`"bigint"`、`"boolean"`、`"symbol"`、`"undefined"`、`"object"`、`"function"` 八个字符串。因为运行时 `typeof null === "object"`，TS 只能把类型收窄为 `object | null`，所以还要排除 `null`。

- **Q2：自定义类型守卫和断言函数有什么区别？**
  A：类型谓词 `x is T` 返回布尔值，由调用方自己写 `if`，收窄只作用于该分支；断言函数 `asserts x is T` 在条件不满足时抛错，收窄作用于断言之后的全部代码。断言函数必须显式标注返回类型，且调用时实参必须是标识符或属性访问（不能是任意表达式）。

- **Q3：什么是可辨识联合？判别属性有什么要求？**
  A：联合的每个成员都拥有一个同名、类型为不同字面量的属性，TS 借此把联合拆分成互斥分支。判别属性必须是单元类型（字面量或其联合），且必须是成员共同拥有的属性，不能是可选属性。

- **Q4：为什么 `switch` 的 `default` 里要写 `const _: never = shape`？**
  A：利用 `never` 是底层类型、只能接受 `never` 的特性，实现编译期穷尽性检查。一旦新增联合成员而没有新增分支，赋值就会失败，从而在编译期而不是运行时暴露遗漏。

- **Q5：类型收窄会影响运行时性能吗？**
  A：不会。收窄完全是编译期行为，所有类型信息在编译后被擦除；真正影响性能的是手写的类型守卫函数体本身（例如逐字段校验大对象）。

### 5. 易错点

| 易错点 | 现象 | 原因 | 解决方案 |
|--------|------|------|----------|
| 自定义守卫的实现与谓词不一致 | 编译通过，运行时访问属性报错 | TS 不校验守卫函数体的逻辑 | 守卫函数内必须做真实校验；复杂结构用 zod 等运行时校验库 |
| `typeof x === "object"` 后直接取属性 | 编译报错「对象可能为 null」 | `typeof null === "object"`，收窄结果是 `object \| null` | 追加 `x !== null` 判断 |
| 谓词类型比参数类型更宽 | 报错「A type predicate's type must be assignable to its parameter's type」 | 谓词只能收窄、不能凭空造类型 | 把参数类型放宽为 `unknown` 或公共基类 |
| 断言函数没写返回类型标注 | 报错「Assertions require every name in the call target to be declared with an explicit type annotation」 | 断言函数依赖显式类型标注 | 写 `const assertX: (v: unknown) => asserts v is T = ...` |
| 判别属性用了宽类型 | `switch` 无法分流，类型不收敛 | `string` / `number` 不是单元类型 | 用字面量联合类型（必要时配合 `as const`） |
| `switch` 漏写 `default` | 穷尽性检查形同虚设 | 没有触发 `never` 赋值 | 必须补 `default` 分支并赋值给 `never` |
| 用 `as` 断言代替类型收窄 | 绕过检查，运行时仍可能崩 | 断言不产生任何运行时校验 | 优先用类型守卫，断言只用在确实掌握更多信息时 |
| 在异步回调里依赖外部收窄 | 回调内类型报错或判断失效 | 收窄不跨越函数边界（尤其对 `let` 变量） | 先把值复制到 `const` 局部变量，再进回调 |
| 认为收窄会"记住"跨分支状态 | 后续代码类型又变宽 | 赋值、`await` 之后的控制流会重置部分收窄 | 在需要的地方重新判断，或改用 `const` 变量 |

---

## 补充：函数重载

### 1. 概念定义

**函数重载（Function Overload）** 指同一个函数名对应多个**重载签名（overload signature）**，调用时根据实参匹配最合适的签名，从而得到精确的参数约束与返回值类型。

重载由两部分组成：

- **重载签名**：只有参数列表和返回类型，没有函数体，可以有多个，是暴露给调用方的「接口」。
- **实现签名**：只有一个，包含函数体；它对调用方**不可见**，只用于检查函数体内部与各重载签名是否兼容。

### 2. 底层原理

- **匹配规则**：编译器在解析调用表达式时，**从上到下**依次用实参去匹配重载签名，命中第一个兼容的签名即停止，并用该签名的返回类型作为调用结果的类型。因此签名顺序直接决定结果。
- **实现签名的约束**：实现签名必须「足够宽」——它的参数类型要能接受所有重载签名的参数（参数位置按兼容性放宽），返回类型要能被所有重载签名的返回类型覆盖（通常写成它们的联合）。否则报错 `This overload signature is not compatible with its implementation signature`。
- **实现签名不可调用**：调用方只能看到重载签名。如果实参不匹配任何重载签名，即使匹配实现签名也会报 `No overload matches this call`。
- **运行时不存在重载**：JS 只有一个函数对象，重载信息在编译后被完全擦除。因此**分派逻辑必须自己写在函数体里**（通常用类型守卫或参数个数判断）。
- **重载与联合类型的取舍**：如果「参数相同、只是类型不同，且返回类型与入参类型一一对应」，用重载能拿到更精确的返回值；如果只需要「接受多种类型、返回统一类型」，用联合类型更简洁。

### 3. 代码示例

```typescript
// ========== 1. 基础：重载签名 + 实现签名 ==========
function createElement(tag: "a"): HTMLAnchorElement;
function createElement(tag: "canvas"): HTMLCanvasElement;
function createElement(tag: string): HTMLElement;
// 实现签名：参数放宽到 string，返回类型取各重载返回值的父类型
function createElement(tag: string): HTMLElement {
  return document.createElement(tag);
}

const a = createElement("a"); // HTMLAnchorElement
const c = createElement("canvas"); // HTMLCanvasElement
const d = createElement("div"); // HTMLElement
```

```typescript
// ========== 2. 参数个数不同的重载 ==========
function query(sql: string): Promise<unknown[]>;
function query(sql: string, params: unknown[]): Promise<unknown[]>;
function query(sql: string, params?: unknown[]): Promise<unknown[]> {
  return db.execute(sql, params ?? []); // 实现签名里统一处理
}

query("select 1"); // ✅ 命中第一个签名
query("select * from t where id = ?", [1]); // ✅ 命中第二个签名
```

```typescript
// ========== 3. 返回值随参数类型变化（重载最典型的用途）==========
function parse(input: string): string[];
function parse(input: string[]): string;
function parse(input: string | string[]): string | string[] {
  if (typeof input === "string") {
    return input.split(","); // 运行时靠类型守卫分派
  }
  return input.join(",");
}

const arr = parse("a,b,c"); // string[]
const str = parse(["a", "b"]); // string
// 若改用联合类型签名 `parse(input: string | string[]): string[] | string`，
// 调用方拿到的就是宽联合，必须自己再收窄——这正是重载的价值
```

```typescript
// ========== 4. 接口 / 类中的方法重载 ==========
interface Formatter {
  format(value: string): string;
  format(value: number): string;
}

class CsvFormatter implements Formatter {
  // 类中只能有一份实现，不能写多个函数体
  format(value: string | number): string {
    return typeof value === "number" ? value.toFixed(2) : value.trim();
  }
}
```

```typescript
// ========== 5. 箭头函数无法直接写重载，用函数类型代替 ==========
interface ParseFn {
  (input: string): string[];
  (input: string[]): string;
}

const parseArrow: ParseFn = (input: string | string[]) => {
  return typeof input === "string" ? input.split(",") : input.join(",");
};

const result = parseArrow("a,b"); // string[]
```

```typescript
// ========== 6. 顺序很关键：具体签名必须写在前面 ==========
function pickValue(source: { name: string }, key: "name"): string;
function pickValue(source: { name: string }, key: string): unknown;
function pickValue(source: { name: string }, key: string): unknown {
  return source[key as "name"];
}

pickValue({ name: "张三" }, "name"); // string（命中第一个签名）

// 反例：如果把宽签名写在前面，pickValue(..., "name") 会先命中它，返回 unknown
```

### 4. 面试常见问法

- **Q1：重载和联合类型参数怎么选？**
  A：需要「返回值随入参类型精确变化」或「参数个数不同」时用重载；只需要「接受多种类型、返回统一类型」时用联合类型。联合类型代码更短，重载类型更精确。

- **Q2：实现签名为什么不能被调用？**
  A：实现签名是给编译器检查函数体用的，不进入调用方的候选签名列表。调用方只能看到重载签名，所以不匹配任何重载的调用会直接报错。

- **Q3：重载在运行时是怎么实现的？**
  A：不存在运行时的重载，编译后只有一个普通函数。分派逻辑必须自己写在函数体内（`typeof`、`in`、参数个数判断等）。

- **Q4：重载签名的顺序为什么重要？**
  A：匹配是从上到下取第一个兼容的签名，宽泛的签名写在前面会把后面的具体签名「吃掉」，导致返回类型不符合预期。

- **Q5：重载有什么代价？**
  A：写法冗长、需要维护多份签名；各签名之间若存在完全覆盖关系，TS 不会报警，容易出现「永远匹配不到」的死签名。

### 5. 易错点

| 易错点 | 现象 | 原因 | 解决方案 |
|--------|------|------|----------|
| 实现签名参数写窄 | 报错 `This overload signature is not compatible with its implementation signature` | 实现签名必须能接受所有重载的参数 | 参数放宽为联合类型或更宽的父类型 |
| 直接调用实现签名的形态 | 报错 `No overload matches this call` | 实现签名对调用方不可见 | 把需要暴露的形态写进重载签名列表 |
| 重载顺序颠倒 | 返回类型与预期不符 | 从上到下取第一个匹配 | 具体签名在前、宽泛签名在后 |
| 认为重载有运行时代价 | 不敢用重载 | 类型重载在编译后被完全擦除 | 放心使用，但要自己写运行时分派 |
| 箭头函数直接写重载 | 语法报错 | 重载签名只能出现在函数声明、方法或接口中 | 用接口 / 函数类型标注变量 |
| 重载签名互相覆盖 | 某个签名永远匹配不到，TS 不报错 | 前面的签名已覆盖后面的签名 | 人工检查签名集合是否有多余项 |
| 用重载实现可选参数 | 签名数量爆炸 | 参数只是可选时不需要重载 | 用 `?` 可选参数或默认值 |
| 实现体里忘记处理所有分支 | 编译通过但运行时返回错误值 | 重载只做类型检查，不做运行时校验 | 在实现体里用类型守卫覆盖每个重载分支 |

---

## 补充：类与继承

### 1. 概念定义

| 概念 | 说明 |
|------|------|
| `public` / `protected` / `private` | TypeScript 的访问修饰符，**编译期**可见性约束 |
| `#field` | ES2022 的私有字段，**运行时**真私有 |
| `readonly` | 只能在声明处或构造函数中赋值 |
| `static` | 挂在构造函数上的成员，不属于实例 |
| `abstract` | 抽象类 / 抽象成员，只能被继承、不能被实例化 |
| `implements` | 类对接口的「结构契约」检查，不继承实现 |
| `extends` | 类的继承，产生原型链与运行时代码 |
| `override` | 显式标记「覆写基类成员」，配合 `noImplicitOverride` 使用 |
| 参数属性 | `constructor(public readonly id: string)` 的语法糖 |
| `this` 类型 | 成员中表示「当前类或其子类」，用于多态链式调用 |

### 2. 底层原理

- **修饰符是编译期的**：`private`、`protected`、`readonly` 在生成的 JS 中完全消失，只保留在类型信息里。因此 `(obj as any).privateProp` 可以绕过检查并真的读到值——`private` 是「约定 + 检查」，不是安全边界。
- **`#` 是真私有**：ES2022 的私有字段是语言级特性，外部（包括 `as any`）无法访问，编译后依然保留私有语义。
- **`implements` vs `extends`**：`implements` 只做结构检查、不产生任何运行时代码，一个类可以实现多个接口；`extends` 产生运行时的原型链继承，一个类只能继承一个父类，派生类构造函数中必须先调用 `super()` 才能访问 `this`。
- **参数属性简写**：`constructor(public readonly id: string)` 等价于「声明字段 + 在构造函数中赋值」。注意在 `target: ES2022+` 或 `useDefineForClassFields: true` 时，类字段采用 `Object.defineProperty` 语义，**字段声明会把原型上的同名 getter/setter 覆盖为 `undefined`**；此时若只是想做类型声明而不想产生字段，应使用 `declare` 修饰。
- **`this` 类型**：在类或接口的成员位置，`this` 表示「当前类型或其子类类型」。返回 `this` 就能让链式调用在子类上保持子类类型，这是 Fluent API 的标准写法。`this` 类型只在成员位置可用，静态成员里的 `this` 指构造函数类型。
- **`override` 的意义**：TS 4.3+ 引入。开启 `noImplicitOverride` 后，所有覆写基类成员的成员都必须写 `override`，编译期就能发现「基类方法改名导致子类覆写悄悄失效」。
- **字段初始化检查**：`strictPropertyInitialization`（`strict` 的一部分）要求每个字段在声明处或构造函数中被初始化；确由外部注入时用明确赋值断言 `!`，但应尽量避免滥用。

### 3. 代码示例

```typescript
// ========== 1. 访问修饰符与参数属性简写 ==========
class Account {
  // 参数属性简写：等价于「声明字段 + 构造函数中 this.id = id」
  constructor(
    public readonly id: string,
    private balance: number,
    protected owner: string,
  ) {}

  deposit(amount: number): void {
    this.balance += amount; // 类内部可访问 private
  }
}

const acc = new Account("A001", 100, "张三");
console.log(acc.id); // ✅ public
// acc.balance;          // ❌ 编译错误：属性 "balance" 为私有属性
// (acc as any).balance; // ⚠️ 编译能过、运行时也能读到：private 只是编译期约束
```

```typescript
// ========== 2. # 真私有字段（ES2022）==========
class Vault {
  #secret = "token"; // 编译后仍保留私有语义，外部无法访问

  reveal(): string {
    return this.#secret;
  }
}

const vault = new Vault();
vault.reveal(); // ✅
// vault.#secret; // ❌ 语法层面就不允许，as any 也绕不过
```

```typescript
// ========== 3. abstract：抽象类不能被实例化 ==========
abstract class Shape {
  abstract area(): number; // 只有签名，没有实现

  describe(): string {
    // 抽象类里可以有已实现的方法，供子类复用
    return `面积：${this.area().toFixed(2)}`;
  }
}

class Circle extends Shape {
  constructor(private radius: number) {
    super(); // 派生类必须先调用 super
  }
  area(): number {
    return Math.PI * this.radius ** 2;
  }
}

// new Shape(); // ❌ 无法创建抽象类的实例

// 抽象构造签名：用来约束"某个类的构造函数"
type ShapeCtor = abstract new (radius: number) => Shape;
function createShape(Ctor: ShapeCtor): Shape {
  return new Ctor(1);
}
```

```typescript
// ========== 4. implements vs extends ==========
interface Serializable {
  serialize(): string;
}

// implements：只检查结构，不继承实现，也不生成任何运行时代码
class UserDto implements Serializable {
  constructor(private name: string) {}
  serialize(): string {
    return JSON.stringify({ name: this.name });
  }
}

class BaseDto {
  serialize(): string {
    return JSON.stringify(this);
  }
}

// extends：继承实现与原型链；一个类只能 extends 一个父类，但可以 implements 多个接口
class AdminDto extends BaseDto {
  // 直接拥有父类的 serialize 实现
}
```

```typescript
// ========== 5. override 与 noImplicitOverride ==========
class Logger {
  log(msg: string): void {
    console.log(msg);
  }
}

class TimedLogger extends Logger {
  // 开启 noImplicitOverride 后必须写 override，否则报错
  override log(msg: string): void {
    console.log(new Date().toISOString(), msg);
  }
}

// class WrongLogger extends Logger {
//   override logs(msg: string): void {} // ❌ 基类没有 logs，override 直接报错，防止手滑改名
// }
```

```typescript
// ========== 6. 多态 this 与链式调用 ==========
class QueryBuilder {
  protected conditions: string[] = [];

  where(cond: string): this {
    // 返回 this 而不是 QueryBuilder
    this.conditions.push(cond);
    return this;
  }
}

class UserQuery extends QueryBuilder {
  limit(n: number): this {
    this.conditions.push(`limit ${n}`);
    return this;
  }
}

// 因为返回的是 this 类型，子类实例能继续链式调用子类方法
new UserQuery().where("age > 18").limit(10); // ✅ 类型为 UserQuery
```

```typescript
// ========== 7. this 参数：给独立函数约束调用上下文 ==========
interface Clickable {
  disabled: boolean;
  onClick(): void;
}

function handleClick(this: Clickable): void {
  if (this.disabled) return;
  this.onClick();
}

// handleClick(); // ❌ this 上下文类型为 void，不能直接调用
const btn: Clickable = { disabled: false, onClick: () => console.log("clicked") };
handleClick.call(btn); // ✅
```

```typescript
// ========== 8. 明确赋值断言与 declare 字段 ==========
class Config {
  // strictPropertyInitialization 下必须初始化；
  // 确由外部注入时可断言，但要谨慎使用
  name!: string;

  // declare：只声明类型，不生成字段（避免覆盖原型上的 getter/setter）
  declare version: string;
}
```

### 4. 面试常见问法

- **Q1：TS 的 `private` 和 JS 的 `#` 私有字段有什么区别？**
  A：`private` 是编译期检查，生成的 JS 里没有任何痕迹，`as any` 即可绕过；`#` 是语言级真私有，运行时不可访问。需要真正封装（如内部状态、敏感数据）时用 `#`。

- **Q2：`implements` 和 `extends` 的区别？**
  A：`implements` 只做结构契约检查，不继承实现、不产生运行时代码，且可以同时实现多个接口；`extends` 继承实现与原型链、产生运行时代码，只能继承一个父类。

- **Q3：什么是参数属性简写？编译后是什么样？**
  A：在构造函数参数前加访问修饰符或 `readonly`，TS 会自动声明同名类字段并在构造函数中赋值。编译后等价于「声明字段 + `this.x = x`」，属于 TS 特有语法（`erasableSyntaxOnly` 下会报错）。

- **Q4：`override` 关键字解决什么问题？**
  A：防止基类成员改名后子类的「覆写」悄悄变成新增方法。配合 `noImplicitOverride`，漏写 `override` 或覆写不存在的成员都会在编译期报错。

- **Q5：`this` 类型有什么用？**
  A：在多态场景下让返回值保持「调用者的实际类型」，从而实现链式调用在子类上继续可用（`new UserQuery().where().limit()`）。

- **Q6：抽象类和接口怎么选？**
  A：接口描述「能力/契约」，可多实现、无实现代码；抽象类描述「是什么」，能包含共享实现与状态，只能单继承。需要复用实现时用抽象类，只定义契约时用接口。

### 5. 易错点

| 易错点 | 现象 | 原因 | 解决方案 |
|--------|------|------|----------|
| 把 `private` 当安全边界 | 敏感字段仍能被 `(obj as any).x` 读到 | `private` 只是编译期约束 | 真正需要封装时用 `#field` |
| 用 `implements` 却期望继承实现 | 报错「类错误地实现接口」 | `implements` 不提供任何实现 | 需要复用实现就 `extends`，或把公共逻辑抽成 mixin / 基类 |
| 派生类构造函数中先访问 `this` | 编译或运行时报错 | 必须先调用 `super()` 才能访问 `this` | 把 `super(...)` 放在最前面 |
| 字段声明覆盖原型上的 getter/setter | 访问属性得到 `undefined` | `useDefineForClassFields` / `target: ES2022+` 使用 `Object.defineProperty` 语义 | 用 `declare` 声明纯类型字段，或显式赋值 |
| `strictPropertyInitialization` 报错 | 属性未初始化 | 未在声明处或构造函数中赋值 | 给默认值、在构造函数赋值，或确有外部注入时用 `!` |
| 漏写 `override` | 基类改名后覆写静默失效 | 没有开启 `noImplicitOverride` | 开启 `noImplicitOverride`，覆写一律写 `override` |
| 非抽象子类未实现抽象成员 | 编译报错 | 抽象成员必须被实现 | 补全实现，或把子类也声明为 `abstract` |
| 静态成员引用类泛型参数 | 编译报错 | 静态成员属于构造函数，不在实例泛型作用域内 | 把泛型参数移到方法上 |
| 用类当接口用（只想要形状） | 多出运行时开销与继承耦合 | 类既有类型也有运行时实体 | 只需要形状时用 `interface` / `type` |

---

## 补充：类型兼容性

### 1. 概念定义

TypeScript 采用**结构化类型系统（structural typing）**，也叫「鸭子类型」：类型之间是否兼容，只看**成员结构**是否匹配，而不看是否显式声明了继承关系。这与 Java、C# 的**名义类型系统（nominal typing）**不同——后者要求显式 `implements` / `extends`。

描述类型关系的四个术语：

| 术语 | 含义 | 方向 |
|------|------|------|
| 协变（covariant） | 子类型关系与容器/返回值方向一致 | `Dog` → `Animal` 成立，则 `Dog[]` → `Animal[]` 也成立 |
| 逆变（contravariant） | 子类型关系与参数方向相反 | 参数位置：能处理 `Animal` 的函数可赋给需要处理 `Dog` 的函数类型 |
| 双变（bivariant） | 两个方向都允许（不安全的放宽） | TS 中「方法语法」声明的函数参数默认双变 |
| 不变（invariant） | 只允许完全相同 | 可变属性/可变数组本应如此，但 TS 为了易用做了放宽 |

### 2. 底层原理

- **可赋值性判断规则**：判断源类型 `S` 能否赋值给目标类型 `T` 时，编译器逐项检查——对 `T` 的每个必需属性，`S` 必须有同名属性且类型可赋值；函数类型还要额外比较参数与返回值。多余的属性不影响赋值（`S` 是 `T` 的子类型）。
- **对象字面量的多余属性检查（excess property check）**：为了避免拼写错误，直接写在赋值位置的对象字面量不允许出现目标类型未声明的属性。这是人为加上的严格规则，把字面量先赋给变量即可绕过。
- **类的私有成员使类型「名义化」**：如果类含有 `private` 或 `#` 成员，那么只有来自**同一个声明**的类才能互相赋值，结构相同也不行。
- **函数参数：逆变 + 方法语法双变**。开启 `strictFunctionTypes` 后，用**函数类型语法**（如 `(x: T) => void`、函数类型属性）声明的参数按逆变检查；而用**方法语法**（`method(x: T): void`）声明的参数仍然双变。这个例外是为了兼容 DOM、`Array.prototype` 等大量既有 API。
- **数组是不安全协变的**：`Dog[]` 可以赋值给 `Animal[]`，因为数组方法（`push` 等）的参数按双变处理。这会导致「往 `Animal[]` 里 push 一个非 `Dog` 也编译通过」的不安全行为。`readonly Dog[]` 才是安全协变（无法写入）。
- **特殊类型**：`never` 是底层类型（可赋值给任何类型）、`unknown` 是顶层类型（任何类型都可赋值给它）、`any` 双向可赋值并会污染后续推导。
- **`void` 返回值的特例**：`() => void` 可以接受任何返回值的函数，因为返回值会被忽略（`forEach` 的回调最典型）。
- **弱类型检测**：如果目标类型的所有属性都是可选的（weak type），源类型必须至少有一个同名属性，否则报错——这是为了拦截「拼错属性名」。
- **`strictNullChecks`** 决定 `null` / `undefined` 能否赋值给其他类型，是兼容性判断中最常踩的开关。

### 3. 代码示例

```typescript
// ========== 1. 结构化类型：形状一致即可赋值 ==========
interface Point {
  x: number;
  y: number;
}

class Vector {
  constructor(public x: number, public y: number) {}
}

// Vector 没有 implements Point，但结构满足，因此可以赋值
const p: Point = new Vector(1, 2);

// 多余的属性不影响变量之间的赋值（子类型关系）
const p3 = { x: 1, y: 2, z: 3 };
const p4: Point = p3; // ✅
```

```typescript
// ========== 2. 对象字面量的多余属性检查 ==========
// ❌ 直接写字面量时，多出的 z 会报错（防止拼写错误）
// const p5: Point = { x: 1, y: 2, z: 3 };

// 绕过方式（不建议滥用）：先赋给中间变量
const temp = { x: 1, y: 2, z: 3 };
const p5: Point = temp; // ✅

// 弱类型检测：目标所有属性都是可选的
interface Options {
  timeout?: number;
  retries?: number;
}
const bad: Options = { retry: 3 }; // ❌ 与 Options 没有任何共同属性（很可能是拼错）
const good: Options = { retries: 3 }; // ✅
```

```typescript
// ========== 3. 私有成员让类变成名义类型 ==========
class A {
  private secret = 1;
  public value = 1;
}
class B {
  private secret = 1;
  public value = 1;
}

let a: A = new A();
// a = new B();
// ❌ 报错：类型 "B" 不能赋值给类型 "A"，它们有各自的私有属性 "secret" 声明
```

```typescript
// ========== 4. 协变：返回值与只读位置 ==========
type Animal = { name: string };
type Dog = { name: string; bark(): void };

let animal: Animal;
const dog: Dog = { name: "旺财", bark: () => {} };
animal = dog; // ✅ 协变：Dog 是 Animal 的子类型，向上赋值安全

// 数组的协变是不安全的（TS 有意为之，为了可用性）
const dogs: Dog[] = [dog];
const animals: Animal[] = dogs; // ✅ 允许
animals.push({ name: "咪咪" }); // ⚠️ 编译通过，但 dogs 里混进了没有 bark 的对象
// 需要安全协变时用只读数组
const readonlyAnimals: readonly Animal[] = dogs; // ✅ 安全，因为无法写入
```

```typescript
// ========== 5. 函数参数：逆变与方法语法的双变例外 ==========
type Handler = (e: Animal) => void;

const handleAnimal: Handler = (a) => console.log(a.name);
const handleDog: (d: Dog) => void = handleAnimal; // ✅ 逆变：能处理更宽的 Animal，就能处理 Dog

// strictFunctionTypes 开启后，下面这种"更窄参数"的赋值会被拒绝（不安全）
// const h2: Handler = (d: Dog) => {}; // ❌ 参数类型不兼容

// 方法语法声明的参数始终按双变处理（即便开启 strictFunctionTypes）
interface Comparer {
  compare(a: Animal, b: Animal): number; // 方法语法：双变
}
interface ComparerFn {
  compare: (a: Animal, b: Animal) => number; // 函数属性语法：逆变
}

// 想主动放宽为双变时，可以用方法语法"包装"
type BivariantHandler<T> = {
  bivarianceHack(e: T): void;
}["bivarianceHack"];
```

```typescript
// ========== 6. void 返回值的特例 ==========
type Callback = () => void;

const withReturn: Callback = () => 42; // ✅ 返回值被忽略，允许

const nums = [1, 2, 3];
nums.forEach((n) => n.toString()); // 回调返回 string 也没问题
```

```typescript
// ========== 7. any / unknown / never 的可赋值性 ==========
let anything: any = 1;
const s1: string = anything; // ✅ any 可赋给任何类型（危险，会污染）
anything = "str"; // ✅ 任何类型可赋给 any

const u: unknown = 1; // ✅ 任何类型可赋给 unknown
// const s2: string = u; // ❌ unknown 不能直接赋给具体类型
const s3: string = u as string; // 需要收窄或断言

declare const neverValue: never;
const s4: string = neverValue; // ✅ never 可赋给任何类型
// anything = neverValue; // ✅ 同样成立
```

### 4. 面试常见问法

- **Q1：TypeScript 是结构化类型还是名义类型？**
  A：结构化类型（鸭子类型），只要成员结构兼容就能赋值。例外是含 `private` / `#` 成员的类，它们退化为名义类型，必须来自同一处声明。

- **Q2：什么是协变、逆变、双变？TS 里函数参数属于哪一种？**
  A：协变指子类型方向与赋值方向一致，逆变相反，双变是两者都允许。TS 的**函数类型语法**参数在 `strictFunctionTypes` 下按逆变检查，而**方法语法**参数保持双变。

- **Q3：`strictFunctionTypes` 做了什么？为什么方法参数是例外？**
  A：它把函数类型参数的检查从双变改为逆变，拦截「用窄参数函数冒充宽参数函数」的不安全赋值。方法语法保持双变是为了兼容 DOM、`Array.prototype` 等历史 API，避免大面积类型报错。

- **Q4：为什么 `Dog[]` 能赋值给 `Animal[]`？这是安全的吗？**
  A：TS 为了可用性把数组设计为协变，实际是不安全的——可以通过 `Animal[]` 往 `Dog[]` 里写入非 `Dog` 对象。要安全就用 `readonly Animal[]`。

- **Q5：什么是多余属性检查？怎么绕过？**
  A：直接赋值的对象字面量不允许出现目标类型未声明的属性（防拼写错误）。把字面量先赋给中间变量、或用类型断言即可绕过，但不建议滥用。

- **Q6：为什么 `() => number` 能赋给 `() => void`？**
  A：返回值在 `void` 上下文里被忽略，这是为了让 `forEach` 这类 API 的回调写起来更自然。

### 5. 易错点

| 易错点 | 现象 | 原因 | 解决方案 |
|--------|------|------|----------|
| 以为 TS 是名义类型 | 没 `implements` 也能赋值，误以为漏了检查 | TS 按结构比较 | 记住结构化类型；需要名义约束时给类加 `private` / `#` 成员 |
| 对象字面量多写属性 | 报错「对象字面量只能指定已知属性」 | 多余属性检查是刻意设计的严格规则 | 检查是否拼错；确有多余属性就先赋给变量 |
| 往协变数组里写数据 | 编译通过、运行时出现「缺方法」的对象 | 数组协变不安全 | 用 `readonly T[]`，或避免把子类型数组当父类型数组写 |
| 混淆方法语法与函数属性语法 | 同样的参数类型，一个报错一个不报 | `strictFunctionTypes` 只对函数类型语法生效 | 需要严格逆变就用函数属性语法 |
| 用 `any` 做「兼容性补丁」 | 类型检查形同虚设，错误扩散 | `any` 双向可赋值且会污染推导 | 改用 `unknown` + 收窄，或写精确类型 |
| 弱类型只传一个错拼属性 | 报错「与类型没有任何共同属性」 | 弱类型检测拦截拼写错误 | 修正属性名；确需动态属性就加索引签名 |
| 以为 `readonly` 会影响可赋值性 | 可变对象能赋给 `readonly` 属性类型 | 属性上的 `readonly` 不参与可赋值性检查 | 用只读数组 / 只读元组来表达真正的只读约束 |
| 关闭 `strictNullChecks` 后类型"变宽" | `null` 能赋给任何类型，运行时崩 | 严格空值检查被关闭 | 始终开启 `strict: true` |
| 依赖私有成员做兼容性判断 | 结构完全相同的两个类互不兼容 | 含私有成员的类按名义类型比较 | 抽出公共接口，让两个类都 `implements` 该接口 |

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
- [ ] 能用 typeof / instanceof / in / 字面量收窄联合类型，知道 `typeof null === "object"` 的坑
- [ ] 会写类型谓词（`x is T`）和断言函数（`asserts x is T`），知道二者的区别与限制
- [ ] 能设计可辨识联合并用 `never` 做穷尽性检查
- [ ] 会写函数重载，理解重载顺序、实现签名的约束与「运行时无重载」
- [ ] 能说出 `private` 与 `#` 私有字段的区别，理解 `implements` / `extends` / `override` 的用途
- [ ] 理解多态 `this` 类型与 `this` 参数的用法
- [ ] 能解释结构化类型、多余属性检查，以及协变 / 逆变 / 双变在 TS 中的具体表现
