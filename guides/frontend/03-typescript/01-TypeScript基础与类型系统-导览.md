# 01-TypeScript基础与类型系统 导览

> 定位：五维框架浓缩提炼 01-TypeScript基础与类型系统.md 全部内容小节，快速查阅与复习。
> 用法：每个内容小节对应一张纵向表格，需要深入理解时跳转 [原文](./01-TypeScript基础与类型系统.md)。
> 前置知识：[语法基础与执行机制](../02-javascript-core/01-语法基础与执行机制-导览.md)

---

## 一、核心概念

### 1.1 什么是 TypeScript

| 维度 | 内容 |
|------|------|
| 是什么 | Microsoft 开发的 JavaScript 超集，在 JS 基础上添加静态类型系统，编译为纯 JavaScript 运行。 |
| 能做什么 | 在编译阶段发现类型错误，提供智能代码补全和重构支持，增强大型项目代码可维护性；渐进式迁移，JavaScript 代码可直接重命名为 .ts 文件。 |
| 怎么用 | `pnpm install -g typescript`，编写 `.ts` 文件，`tsc` 编译为 `.js`，类型注解如 `let name: string = 'hello';` |
| 原理和工作流程 | TS 编译器进行词法分析、语法分析和类型检查，生成 AST 并校验类型兼容性，通过后输出纯 JavaScript 代码，编译时类型信息会被擦除，不影响运行时性能。 |
| 缺点 | 增加学习成本和编译步骤；类型定义维护需要额外工作；小项目收益不明显。 |

### 1.2 安装与配置

| 维度 | 内容 |
|------|------|
| 是什么 | TypeScript 开发环境搭建，包括编译器安装、tsconfig.json 配置文件、编译命令。 |
| 能做什么 | 配置 TypeScript 编译选项、指定编译目标、模块系统、严格模式、输出目录等。 |
| 怎么用 | `pnpm install -g typescript`、`tsc --init` 生成 tsconfig.json、`tsc --watch` 监听编译 |
| 原理和工作流程 | tsconfig.json 是 TypeScript 项目配置文件，编译器读取配置决定编译行为。关键配置：target（编译目标 ES 版本）、module（模块系统）、strict（严格模式，推荐开启）、outDir（输出目录）。 |
| 缺点 | 配置选项繁多，初学者容易漏掉关键配置（如 strict: true）。 |

---

## 二、底层原理

### 2.1 原始类型

| 维度 | 内容 |
|------|------|
| 是什么 | TypeScript 支持 JavaScript 的 7 种原始类型：string、number、boolean、null、undefined、symbol、bigint，以及特殊类型 void 和 never。 |
| 能做什么 | 为变量、函数参数和返回值提供精确的类型约束，让编译器在调用时进行类型检查。 |
| 怎么用 | `let name: string = 'Bob';`、`let age: number = 25;`、`let isDone: boolean = false;`、`function fn(): void {}`、`function error(): never { throw new Error(); }` |
| 原理和工作流程 | 类型注解在编译时被编译器检查，运行时类型信息被擦除。void 表示函数无返回值，never 表示函数永远不会返回（抛异常或无限循环）。 |
| 缺点 | 类型注解增加代码量；null 和 undefined 是所有类型的子类型（strictNullChecks 关闭时）。 |

### 2.2 数组与元组

| 维度 | 内容 |
|------|------|
| 是什么 | 数组是同类型元素的有序集合，有两种声明方式；元组是固定长度和固定类型顺序的数组。 |
| 能做什么 | 数组约束元素类型，防止混入不同类型；元组精确控制每个位置的类型和数量，适合函数返回多值。 |
| 怎么用 | 数组：`let arr: number[] = [1, 2, 3];` 或 `let arr: Array<number> = [1, 2, 3];`；元组：`let tuple: [string, number] = ['hello', 42];` |
| 原理和工作流程 | 数组类型声明确保所有元素类型一致；元组利用索引映射类型，每个位置有独立类型，超出长度访问按联合类型处理。 |
| 缺点 | 元组越界访问不会报错但返回联合类型；元组长度固定可能导致使用不便。 |

### 2.3 枚举（Enum）

| 维度 | 内容 |
|------|------|
| 是什么 | 为一组数值赋予友好名称的数据类型，分为数字枚举（默认递增）、字符串枚举、常量枚举。 |
| 能做什么 | 定义一组有意义的命名常量集合，替代魔法数字，提高代码可读性。 |
| 怎么用 | 数字枚举：`enum Color { Red, Green, Blue }`（Red=0, Green=1, Blue=2）；字符串枚举：`enum Color { Red = 'red', Green = 'green' }`；常量枚举：`const enum Color { Red, Green }`（编译后内联无额外代码） |
| 原理和工作流程 | 数字枚举默认从 0 递增，可手动指定起始值；字符串枚举每个值必须初始化为字符串。编译后枚举会生成反向映射对象（数字枚举）。const enum 编译时直接内联值，不生成额外代码。 |
| 缺点 | 数字枚举反向映射增加编译产物大小；非 const enum 产生额外运行时代码；TypeScript 枚举与 JavaScript 语法不兼容。 |

### 2.4 对象类型（Object）

| 维度 | 内容 |
|------|------|
| 是什么 | 使用对象字面量语法或 interface/type 定义对象结构，包含属性名和对应的类型。 |
| 能做什么 | 精确约束对象属性类型，支持可选属性、只读属性、索引签名等。 |
| 怎么用 | `let obj: { name: string; age?: number; readonly id: number; } = { name: 'Bob', id: 1 };`；索引签名：`[key: string]: any` |
| 原理和工作流程 | 对象类型直接内联声明，编译器检查属性存在性和类型兼容性。可选属性（`?`）表示可不存在；readonly 表示初始化后不可修改；索引签名约束任意属性名对应的类型。 |
| 缺点 | 内联声明过于复杂时建议提取为 interface 或 type，提高复用性。 |

---

## 三、实战应用

### 3.1 接口（Interface）

| 维度 | 内容 |
|------|------|
| 是什么 | 定义对象结构契约的 TypeScript 核心特性，约束对象必须包含哪些属性和方法，支持继承、合并和函数类型。 |
| 能做什么 | 定义对象形状、类实现契约、函数类型；通过 extends 实现接口继承；同名接口自动合并；支持可选属性、只读属性、索引签名。 |
| 怎么用 | `interface User { name: string; age: number; sayHi(): void; }`、`interface Admin extends User { role: string; }`、`class Person implements User { ... }` |
| 原理和工作流程 | interface 在编译时进行结构化类型检查（鸭子类型），只要对象形状匹配就兼容，不要求显式声明实现。interface 可以合并声明，多次声明同一接口自动合并属性。 |
| 缺点 | 同名接口自动合并可能意外合并导致类型错误；interface 只能描述对象形状，不能描述联合类型等复杂类型。 |

### 3.2 类型别名（Type）

| 维度 | 内容 |
|------|------|
| 是什么 | 使用 `type` 关键字为任意类型（原始类型、联合类型、交叉类型、元组、函数类型等）创建别名。 |
| 能做什么 | 定义复杂类型（联合类型、交叉类型、映射类型）；简化重复类型书写；与 interface 相比更灵活，支持基本类型别名和联合类型。 |
| 怎么用 | `type ID = string;`、`type Status = 'pending' | 'active' | 'done';`、`type Point = { x: number; y: number; };`、`type User = { name: string } & { age: number };` |
| 原理和工作流程 | type 是类型别名，不创建新类型。联合类型是多个类型中任意一个；交叉类型是多个类型合并为一个。type 不能声明合并，定义后不能重复声明。 |
| 缺点 | 不能像 interface 那样声明合并；复杂交叉类型报错信息难以阅读；选择 interface 还是 type 是常见困惑。 |

### 3.3 Interface vs Type 选择策略

| 维度 | 内容 |
|------|------|
| 是什么 | 比较 interface 和 type 的差异，总结选择策略。 |
| 能做什么 | 指导在项目中何时使用 interface 何时使用 type。 |
| 怎么用 | 优先使用 interface（支持声明合并，面向对象场景更自然）；需要联合类型、交叉类型、映射类型时使用 type；对象形状用 interface，复杂类型用 type。 |
| 原理和工作流程 | interface 更面向对象，适合定义公共 API 和类实现；type 更灵活，适合组合类型和工具类型。两者大多数场景可互换，关键差异在于声明合并和联合类型支持。 |
| 缺点 | 没有统一标准，团队需要协商一致；很多场景两者都可用，过度纠结选择浪费时间。 |

---

### 3.4 函数类型定义

| 维度 | 内容 |
|------|------|
| 是什么 | 为函数参数和返回值添加类型注解，支持函数类型表达式、函数签名、可选参数和默认参数。 |
| 能做什么 | 约束函数调用时参数类型和数量，防止传递错误类型参数；函数表达式定义参数和返回值类型，约束赋值行为。 |
| 怎么用 | `function add(x: number, y: number): number { return x + y; }`、`const add: (x: number, y: number) => number = (x, y) => x + y;`、可选参数 `function fn(x: number, y?: string) {}` |
| 原理和工作流程 | 函数类型注解在编译时检查参数类型和数量，返回值类型通过控制流分析推断。可选参数必须放在必选参数后面。 |
| 缺点 | 过多参数类型注解使函数签名冗长；函数重载写法复杂，不如使用联合类型参数简洁。 |

### 3.5 函数重载

| 维度 | 内容 |
|------|------|
| 是什么 | 同一函数名对应多个函数签名，根据参数类型和数量调用不同的函数实现。 |
| 能做什么 | 为函数提供多种调用方式，精确约束不同参数组合下的返回值类型。 |
| 怎么用 | 写多个函数签名，最后写一个实现签名，实现签名中通过类型守卫区分参数类型。 |
| 原理和工作流程 | 编译器匹配函数调用时，从上到下依次检查函数签名，找到第一个匹配的就使用对应的返回值类型。实现签名不对外暴露，需要完整覆盖所有函数签名。 |
| 缺点 | 写法冗长，需要维护多个函数签名；实现签名中需要手动判断参数类型。 |

---

## 四、常见面试题

### 1. TypeScript 和 JavaScript 的区别

| 维度 | 内容 |
|------|------|
| 是什么 | 考查 TypeScript 相比 JavaScript 的核心差异：静态类型系统、编译时检查、IDE 支持。 |
| 能做什么 | 检验对 TypeScript 定位和价值的理解。 |
| 怎么用 | JS 是动态类型，运行时检查；TS 是静态类型，编译时检查。TS 是 JS 超集，提供类型系统、接口、泛型、枚举等特性，编译生成 JS 代码。 |
| 原理和工作流程 | TS 编译器在编译阶段进行类型检查，发现类型错误后编译失败，运行时类型信息被擦除。TS 利用类型系统提供更好的 IDE 智能提示和重构支持。 |
| 缺点 | 只说"类型检查"不够，需要说明编译时检查、IDE 支持、类型擦除等具体差异。 |

### 2. interface 和 type 的区别

| 维度 | 内容 |
|------|------|
| 是什么 | 考查 interface 和 type 在声明合并、类型支持、使用场景上的差异。 |
| 能做什么 | 检验对 TypeScript 类型系统核心概念的理解。 |
| 怎么用 | interface 支持声明合并，主要用于对象形状定义；type 支持联合类型、交叉类型、映射类型，更灵活。推荐策略：对象形状优先 interface，需要联合类型用 type。 |
| 原理和工作流程 | interface 声明合并允许同名接口自动合并属性；type 不支持声明合并。interface 不能表示联合类型，type 可以。两者在大部分对象形状场景可互换。 |
| 缺点 | 分不清声明合并和联合类型这两个关键差异。 |

### 3. any、unknown、never 的区别

| 维度 | 内容 |
|------|------|
| 是什么 | 考查 any、unknown、never 三种特殊类型在类型安全和使用场景上的差异。 |
| 能做什么 | 检验对 TypeScript 类型安全层次的理解。 |
| 怎么用 | any 关闭类型检查，任意赋值和访问；unknown 安全版本的 any，使用前必须类型守卫；never 表示永远不可到达的值，用于函数返回类型和穷举检查。 |
| 原理和工作流程 | any 是最宽松的类型，跳过所有类型检查；unknown 是 top type，可以接收任何值但必须类型收窄后才能使用；never 是 bottom type，不能赋值给任何类型，常用于确保 switch 穷举。 |
| 缺点 | 混淆 unknown 和 any 的使用场景，any 滥用导致类型安全退化。 |

---

## 五、避坑指南

| 维度 | 内容 |
|------|------|
| 是什么 | 汇总 TypeScript 基础开发中 5 个高频错误：any 滥用、类型断言不匹配、可选属性 undefined、枚举类型混淆、strictNullChecks 配置。 |
| 能做什么 | 帮助开发者避免常见 TypeScript 类型错误，写出更安全的代码。 |
| 怎么用 | 避免滥用 any，优先使用 unknown 或具体类型；类型断言使用 as 语法和类型守卫；可选属性访问前检查；使用字符串枚举替代数字枚举；开启 strictNullChecks 防止 null 访问错误。 |
| 原理和工作流程 | any 滥用破坏类型安全，使 TypeScript 退化为 JavaScript；不开启 strictNullChecks 会导致 null/undefined 可以被赋值给任何类型，运行时可能报错。 |
| 缺点 | 严格模式可能增加开发工作量，但长期收益远大于成本。 |

---

## 补充：类型守卫与类型收窄

### 补1 内置类型守卫（typeof / instanceof / in / 字面量）

| 维度 | 内容 |
|------|------|
| 是什么 | 能触发类型收窄的内置表达式：`typeof`（基本类型）、`instanceof`（类实例）、`in`（属性存在性）、字面量相等比较与真值判断，以及 `Array.isArray`。收窄只发生在编译期，不产生运行时代码。 |
| 能做什么 | 把联合类型按条件分流到具体类型，使每个分支都能安全访问该类型独有的属性与方法；`unknown` 入参必须先经守卫收窄才能使用。 |
| 怎么用 | `if (typeof value === "string") { value.toUpperCase() }`；`if (err instanceof ApiError) { err.status }`；`if ("permissions" in user) { user.permissions }`；`if (data) { data.length }`；`if (Array.isArray(input)) { input.map(...) }`。 |
| 原理和工作流程 | 检查器为每个引用维护 flow type，遇到分支时按控制流图分别计算分支内类型。`typeof` 只识别 `"string"`、`"number"`、`"bigint"`、`"boolean"`、`"symbol"`、`"undefined"`、`"object"`、`"function"` 八个字符串；因运行时 `typeof null === "object"`，`typeof x === "object"` 只能收窄为 `object \| null`。真值收窄会剔除 `null`、`undefined`、`0`、`NaN`、`""`、`false`。`in` 要求左侧为属性名字面量、右侧为对象类型。 |
| 缺点 | `instanceof` 不能用于接口（接口没有运行时实体）；`typeof` 无法区分具体对象类型；真值收窄会把 `0` 和 `""` 一起剔除，容易误伤合法值；收窄不跨越函数边界，在异步回调中会失效。 |

### 补2 自定义类型守卫与断言函数

| 维度 | 内容 |
|------|------|
| 是什么 | 类型谓词 `function isX(v: unknown): v is X` 与断言函数 `function assertX(v: unknown): asserts v is X`（TS 3.7+），用于表达内置守卫覆盖不到的业务判断。 |
| 能做什么 | 谓词把判断结果返回调用方，收窄仅作用于 `if` 分支；断言函数在不满足条件时抛错，收窄作用于断言之后的全部代码，适合「参数校验后一路畅通」的场景。 |
| 怎么用 | 谓词：`function isCat(a: Cat \| Dog): a is Cat { return typeof (a as Cat).meow === "function" }`；断言：`function assertIsString(v: unknown): asserts v is string { if (typeof v !== "string") throw new TypeError(...) }`；`asserts x` 形态可断言真值。 |
| 原理和工作流程 | 谓词类型必须可赋值给参数类型（只能收窄、不能造类型），返回值必须是 `boolean`；TS **不校验函数体实现**，逻辑写错只会在运行时暴露。断言函数必须显式标注返回类型、不能返回值，且调用时实参必须是标识符或属性访问（不能是任意表达式）；箭头函数做断言函数时必须给变量显式标注类型。 |
| 缺点 | 守卫实现与谓词不一致时编译期无感知，是常见的运行时隐患；复杂结构建议改用 zod 等运行时校验库；断言函数会让「抛错」隐藏在调用处，需注意错误处理路径。 |

### 补3 可辨识联合与穷尽性检查

| 维度 | 内容 |
|------|------|
| 是什么 | 可辨识联合指联合的每个成员都拥有一个同名、类型为不同字面量的判别属性，TS 借此把联合拆分为互斥分支；穷尽性检查借助 `never` 在编译期发现「漏掉的分支」。 |
| 能做什么 | 让 `switch (shape.kind)` 的每个 `case` 精确收窄到对应成员；新增联合成员时通过 `never` 赋值报错，把遗漏从运行时提前到编译期；TS 4.6+ 还支持对解构出的判别属性做收窄。 |
| 怎么用 | `type Shape = Circle \| Square \| Rect`，成员分别带 `kind: "circle" \| "square" \| "rect"`；`switch` 的 `default` 分支写 `const exhaustive: never = shape; throw new Error(...)`，或抽成 `function assertNever(v: never): never`。 |
| 原理和工作流程 | 判别属性必须是单元类型（字符串/数字/布尔字面量、`null`、`undefined` 或它们的联合；`boolean` 等价于 `true \| false` 也可用），不能是 `string`、`number` 这类宽类型，也不能是可选属性。`never` 是底层类型，只能接受 `never`，因此遗漏分支时赋值失败并报错。TS 4.4+ 的别名条件（把条件存进 `const` 变量）同样能收窄。 |
| 缺点 | 需要为每个类型手工加判别属性，侵入数据结构；判别属性若被重新赋值或来自泛型参数，收窄可能失效；`never` 检查必须真的写进 `default`，漏写则完全失效。 |

---

## 补充：函数重载

### 补1 重载签名与实现签名

| 维度 | 内容 |
|------|------|
| 是什么 | 同一函数名对应多个「重载签名」（只有参数与返回类型、无函数体），外加一个「实现签名」（有函数体，对调用方不可见）。 |
| 能做什么 | 为同一函数提供多种调用形态，并在不同形态下返回精确类型（如 `createElement("a")` 返回 `HTMLAnchorElement`）；支持参数个数不同、返回值随入参类型变化等场景。 |
| 怎么用 | `function parse(input: string): string[];` + `function parse(input: string[]): string;` + `function parse(input: string \| string[]): string \| string[] { ... }`；类/接口中的重载只在声明处写多份签名，实现只有一份。 |
| 原理和工作流程 | 调用匹配**从上到下**取第一个兼容的重载签名，并用它的返回类型作为结果类型，因此签名顺序决定结果。实现签名必须「足够宽」：参数能接受所有重载的参数，返回值能覆盖所有重载的返回类型，否则报 `This overload signature is not compatible with its implementation signature`。运行时不存在重载，编译后只有一个普通函数，分派逻辑必须写在函数体内。 |
| 缺点 | 写法冗长、需要维护多份签名；签名之间若存在完全覆盖关系，TS 不报警，容易出现永远匹配不到的死签名；箭头函数不能直接写重载，只能用接口/函数类型标注变量。 |

### 补2 重载 vs 联合类型

| 维度 | 内容 |
|------|------|
| 是什么 | 两种表达「一个函数接受多种类型」的方案：重载（多份签名）与联合类型参数（一份签名 + 联合类型 + 联合返回类型）。 |
| 能做什么 | 需要「返回值随入参类型精确变化」或「参数个数不同」时用重载；只需要「接受多种类型、返回统一类型」时用联合类型，代码更短。 |
| 怎么用 | 重载：`parse("a,b")` 得到 `string[]`、`parse(["a"])` 得到 `string`；联合类型：`function parse(input: string \| string[]): string \| string`，调用方必须自己再收窄返回值。 |
| 原理和工作流程 | 重载在类型层建立「参数 → 返回类型」的一一映射，编译器按调用实参选出对应签名；联合类型只有一份签名，返回类型只能是各分支的并集，精度丢失。二者在运行时都不产生额外代码。 |
| 缺点 | 重载的精确性以代码冗长为代价；联合类型写法更简洁但调用方需要额外收窄；过度使用重载会让类型错误信息变得难以阅读。 |

---

## 补充：类与继承

### 补1 访问修饰符与私有字段

| 维度 | 内容 |
|------|------|
| 是什么 | TS 的 `public` / `protected` / `private` / `readonly` 是**编译期**访问约束；ES2022 的 `#field` 是**运行时**真私有字段；参数属性简写（`constructor(public readonly id: string)`）是「声明字段 + 赋值」的语法糖。 |
| 能做什么 | 控制成员的可见范围、禁止重新赋值（`readonly`）、实现真正的封装（`#`）；参数属性简写显著减少样板代码。 |
| 怎么用 | `constructor(public readonly id: string, private balance: number) {}`；真私有：`class Vault { #secret = "token" }`；只声明类型不生成字段：`declare version: string`。 |
| 原理和工作流程 | 修饰符在编译后完全消失，只保留在类型信息里，因此 `(obj as any).privateProp` 可以绕过并真的读到值——`private` 是约定与检查，不是安全边界；`#` 由语言保证，编译后仍不可访问。在 `target: ES2022+` 或 `useDefineForClassFields: true` 时类字段采用 `Object.defineProperty` 语义，字段声明会把原型上的同名 getter/setter 覆盖为 `undefined`。`strictPropertyInitialization` 要求字段在声明处或构造函数中初始化。 |
| 缺点 | `private` 容易被误解为安全机制；`#` 与 TS 的部分语法（如参数属性）不能混用；`useDefineForClassFields` 的字段语义与旧版 `target` 不一致，跨版本升级时可能改变运行行为。 |

### 补2 implements / extends / override

| 维度 | 内容 |
|------|------|
| 是什么 | `implements` 是类对接口的结构契约检查；`extends` 是类的继承；`override`（TS 4.3+）显式标记覆写基类成员。 |
| 能做什么 | `implements` 校验类是否满足接口（可同时实现多个接口，不继承实现、不产生运行时代码）；`extends` 继承实现与原型链（单继承，产生运行时代码）；`override` 配合 `noImplicitOverride` 防止基类改名导致覆写静默失效。 |
| 怎么用 | `class UserDto implements Serializable { serialize() { ... } }`；`class AdminDto extends BaseDto {}`；`override log(msg: string): void { ... }`。 |
| 原理和工作流程 | `implements` 只在类型层比较结构，接口不提供任何实现，所以类必须自己写全部成员（除非声明为 `abstract`）；`extends` 生成运行时原型链，派生类构造函数中必须先 `super()` 才能访问 `this`。开启 `noImplicitOverride` 后，漏写 `override` 或覆写不存在的成员都会编译报错。抽象类不能被实例化，抽象成员必须由非抽象子类实现；`abstract new (...)` 可用来约束「某个类的构造函数」。 |
| 缺点 | `implements` 不提供代码复用，容易写成大量重复成员；`extends` 造成强耦合，深继承链难以维护（组合优于继承）；`noImplicitOverride` 对存量项目有改造量。 |

### 补3 this 类型与多态 this

| 维度 | 内容 |
|------|------|
| 是什么 | 在类或接口的成员位置，`this` 类型表示「当前类型或其子类类型」；此外函数还可以声明 `this` 参数（`function f(this: T) {}`）来约束调用上下文。 |
| 能做什么 | 让链式调用的返回值保持调用者的实际类型（`new UserQuery().where().limit()`）；给独立函数约束 `this` 指向，避免把方法赋给对象后上下文丢失。 |
| 怎么用 | `where(cond: string): this { ...; return this }`；`function handleClick(this: Clickable): void { if (this.disabled) return; this.onClick() }`，调用时用 `handleClick.call(btn)`。 |
| 原理和工作流程 | `this` 类型是「多态 this」，等价于一个隐含的类型参数，实例化时替换为实际调用者的类型，因此子类实例上的链式调用会返回子类类型。`this` 类型只在类/接口的成员位置可用；静态成员中的 `this` 指构造函数类型。`this` 参数只做编译期检查，编译后不产生额外参数，直接调用会因 `this` 上下文为 `void` 而报错。 |
| 缺点 | 返回 `this` 会限制返回值的可替换性，某些场景下反而不便（需要返回固定基类类型时要显式标注）；`this` 参数对箭头函数无效（箭头函数没有自己的 `this`）；`this` 类型与泛型组合时错误信息较难阅读。 |

---

## 补充：类型兼容性

### 补1 结构化类型与多余属性检查

| 维度 | 内容 |
|------|------|
| 是什么 | TS 采用结构化类型系统（鸭子类型）：类型兼容性只看成员结构，不看是否显式声明继承；「多余属性检查」则对直接赋值的对象字面量额外严格。 |
| 能做什么 | 让没有显式继承关系的类型也能互相赋值（如 `class Vector` 直接赋给 `interface Point`）；用多余属性检查拦截拼写错误；用弱类型检测拦截「一个属性都对不上」的赋值。 |
| 怎么用 | `const p: Point = new Vector(1, 2)`；多余属性绕过：`const temp = { x: 1, y: 2, z: 3 }; const p: Point = temp;`；弱类型：目标属性全可选时源类型必须至少命中一个同名属性。 |
| 原理和工作流程 | 判断 `S` 能否赋值给 `T` 时，编译器逐项检查 `T` 的每个必需属性在 `S` 中是否存在且类型可赋值，源类型多出的属性不影响赋值（`S` 是 `T` 的子类型）。对象字面量直接出现在赋值位置时会触发多余属性检查——这是为防拼写错误而人为加上的规则。含 `private` / `#` 成员的类退化为名义类型，必须来自同一处声明才能互相赋值。 |
| 缺点 | 结构化类型让「意外的兼容」难以察觉（结构恰好相同就被认为兼容）；多余属性检查只对字面量生效，把字面量先赋给变量即可绕过，规则略显不一致；私有成员造成「结构相同却互不兼容」的困惑。 |

### 补2 协变 / 逆变 / 双变

| 维度 | 内容 |
|------|------|
| 是什么 | 描述子类型关系在类型构造器中的传播方向：协变（方向一致）、逆变（方向相反）、双变（两个方向都允许）、不变（必须完全相同）。 |
| 能做什么 | 解释「为什么 `Dog[]` 能赋给 `Animal[]`」「为什么能处理 `Animal` 的函数可以赋给需要处理 `Dog` 的函数类型」；指导如何用 `readonly` 和函数属性语法写出更安全的类型。 |
| 怎么用 | 协变：`const a: Animal = dog`；逆变：`const handleDog: (d: Dog) => void = handleAnimal`；双变包装：`type BivariantHandler<T> = { bivarianceHack(e: T): void }["bivarianceHack"]`；安全协变：`const list: readonly Animal[] = dogs`。 |
| 原理和工作流程 | 返回值位置协变（返回子类型更安全）、参数位置逆变（接受更宽类型更安全）。TS 的**函数类型语法**参数在 `strictFunctionTypes` 下按逆变检查，而**方法语法**参数保持双变——这个例外是为了兼容 DOM、`Array.prototype` 等历史 API。数组因为方法参数双变而整体表现为不安全协变，因此 `Dog[]` 可赋给 `Animal[]` 并可写入非 `Dog` 对象。 |
| 缺点 | 双变是类型系统的不安全放宽，可能引入运行时错误；数组协变让「看起来安全」的赋值暗藏风险；协变/逆变的概念抽象，容易与 `readonly`、`in`/`out` 变型标注混淆。 |

### 补3 strictFunctionTypes 与可赋值性规则

| 维度 | 内容 |
|------|------|
| 是什么 | `strictFunctionTypes` 是 `strict` 家族的一员，把函数类型参数的检查从双变收紧为逆变；可赋值性规则则涵盖 `any` / `unknown` / `never` / `void` / `null` 等特殊类型的处理方式。 |
| 能做什么 | 拦截「用窄参数函数冒充宽参数函数」的不安全赋值；明确 `unknown` 只能收窄后使用、`never` 可赋给任何类型、`() => void` 可接受任何返回值的函数；用 `strictNullChecks` 阻止 `null` 赋值给其他类型。 |
| 怎么用 | `"strict": true` 一键开启；`const u: unknown = 1` 后必须收窄才能使用；`type Callback = () => void` 可接受 `() => 42`；`nums.forEach((n) => n.toString())` 返回值被忽略。 |
| 原理和工作流程 | 函数类型兼容性同时比较参数与返回值：参数按逆变（方法语法双变）、返回值按协变。`void` 返回值位置是特例——返回值在 `void` 上下文被忽略，因此任何返回值的函数都可赋给 `() => void`。`any` 双向可赋值且会污染后续推导；`unknown` 是顶层类型、`never` 是底层类型；`strictNullChecks` 决定 `null` / `undefined` 的可赋值性，是兼容性判断中最常踩的开关。 |
| 缺点 | 开启 `strict` 后存量代码报错较多，需要逐步修复；`void` 返回值的放宽规则容易被误用（回调里写错返回值不会报错）；`any` 一旦引入就难以追踪污染范围。 |

---

## 本章学习自检

本节为辅助内容，无五维表格。

---

> [返回原文](./01-TypeScript基础与类型系统.md) | [返回模块目录](../README.md) | [返回知识导览](../知识导览.md)