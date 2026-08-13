# Prompt 工程与代码生成

> 模块：11-ai-assisted（AI 辅助前端开发）
> 知识点：Prompt 工程、Few-shot 提示、结构化输出、前端 Prompt 模板、复杂表单 Prompt、AI 幻觉避免
> 前置知识：[AI 编程工具与工作流](./01-AI编程工具与工作流.md)

---

## 一、核心概念

Prompt 是与 AI 编程工具交互的核心接口。同样的 AI 模型，不同的 Prompt 会产生截然不同的代码质量。掌握 Prompt 工程意味着能精确控制 AI 的输出，让 AI 成为你的"高级代码生成器"。

**核心概念要点：**

1. **Prompt 是精确指令，不是聊天**：不要用模糊的自然语言描述，要像写需求文档一样精确
2. **上下文决定输出质量**：AI 不能猜测你的项目结构、技术栈、编码规范，必须显式提供
3. **Few-shot 是质量加速器**：提供 1-3 个示例，AI 的准确率可提升 50% 以上
4. **结构化输出是可控性的关键**：要求 JSON Schema、Markdown 表格等固定格式，减少"幻觉"空间

---

## 二、Prompt 工程核心原则

### 2.1 五要素 Prompt 模板

一个高质量的 Prompt 应包含以下五个要素：

```
[角色设定] 你是一名资深前端工程师，精通 Vue 3 和 TypeScript
[任务描述] 创建一个可复用的搜索表单组件，包含以下功能：
          - 关键字搜索（支持防抖 300ms）
          - 分类下拉筛选
          - 日期范围选择
          - 搜索/重置按钮
[上下文信息] 项目使用 Vue 3 Composition API + TypeScript + Element Plus
          组件放置在 src/components/common/SearchForm.vue
          请参考项目中已有的 form 组件风格
[输出格式] 输出完整的 .vue 单文件组件，包含 <template>、<script setup lang="ts">、<style scoped>
[约束条件] - 使用 defineProps 和 defineEmits
          - 搜索参数通过 emit 事件向外传递
          - 防抖使用 lodash-es 的 debounce
          - 所有文本使用中文
```

### 2.2 角色设定（Role Prompting）

为 AI 设定明确的角色，可以引导其输出符合期望的专业水平：

| 角色 | 适用场景 |
|------|---------|
| "资深前端工程师" | 代码生成、组件设计 |
| "前端架构师" | 技术方案设计、架构决策 |
| "代码审查员" | 代码审查、质量检查 |
| "测试工程师" | 测试用例编写 |
| "技术文档撰写者" | README、API 文档 |

**角色设定进阶技巧**：不只设定角色，还要设定其"思维模式"：

```
你是一名以"代码可维护性"为核心价值观的前端工程师。
在写每一行代码时，你都会考虑：
1. 六个月后的自己能否看懂这段代码
2. 新同事能否在 10 分钟内理解这个函数
3. 这段代码是否容易被单元测试覆盖
```

### 2.3 上下文注入

上下文是决定 AI 输出质量的第一要素。以下内容应作为上下文注入：

| 上下文类型 | 示例 | 注入方式 |
|-----------|------|---------|
| 项目技术栈 | Vue 3 + TypeScript + Pinia + Element Plus | 在 Prompt 中明确说明 |
| 文件路径 | src/components/common/SearchForm.vue | 指定输出位置 |
| 现有代码风格 | 项目中已有的组件示例 | @file 引用或粘贴代码片段 |
| 编码规范 | ESLint 配置、命名约定 | 规则文件或 Prompt 中列出 |
| 类型定义 | 接口/类型文件 | @file 引用 |
| 依赖版本 | Vue 3.4+、Element Plus 2.5+ | 避免 AI 生成过时 API |

### 2.4 Few-shot 示例引导

Few-shot 是提升 AI 输出质量最有效的方法。提供一个"输入→输出"示例，AI 会模仿其格式和风格：

**示例：生成 Vue 组件的 Few-shot Prompt**

```
请按照以下格式生成组件：

【示例输入】
创建一个用户头像组件，显示头像图片和用户名，点击时触发事件

【示例输出】
```vue
<template>
  <div class="user-avatar" @click="handleClick">
    <img :src="avatar" :alt="name" class="avatar-img" />
    <span class="avatar-name">{{ name }}</span>
  </div>
</template>

<script setup lang="ts">
interface Props {
  avatar: string;
  name: string;
}

const props = defineProps<Props>();
const emit = defineEmits<{
  click: [name: string];
}>();

const handleClick = () => {
  emit('click', props.name);
};
</script>

<style scoped>
.user-avatar { display: flex; align-items: center; gap: 8px; cursor: pointer; }
.avatar-img { width: 40px; height: 40px; border-radius: 50%; }
.avatar-name { font-size: 14px; color: #333; }
</style>
```

【现在请生成】
创建一个商品卡片组件，显示商品图片、名称、价格、评分，支持"加入购物车"按钮
```

### 2.5 结构化输出约束

要求 AI 按固定格式输出，可以大幅减少幻觉和提高可解析性：

**JSON Schema 输出**：

```
输出格式要求：返回一个 JSON 对象，schema 如下：
{
  "componentName": "string - 组件名称（PascalCase）",
  "props": [{ "name": "string", "type": "string", "required": "boolean", "description": "string" }],
  "emits": [{ "name": "string", "payload": "string", "description": "string" }],
  "template": "string - 完整的 <template> 代码",
  "script": "string - 完整的 <script setup lang=\"ts\"> 代码",
  "style": "string - 完整的 <style scoped> 代码"
}
```

**Markdown 表格输出**：

```
请以 Markdown 表格输出以下信息：
| 文件名 | 组件名 | 功能描述 | 依赖 |
|--------|--------|---------|------|
```

> 📖 **参考链接**：
> - [OpenAI - Prompt 工程指南](https://platform.openai.com/docs/guides/prompt-engineering)
> - [OpenAI - Few-shot Prompting](https://platform.openai.com/docs/guides/prompt-engineering#few-shot-prompting)
> - [OpenAI - Chain of Thought Prompting](https://platform.openai.com/docs/guides/prompt-engineering#chain-of-thought-prompting)

---

## 三、前端专用 Prompt 模板库

### 3.1 生成组件

```
你是一名 Vue 3 前端工程师。请生成一个 [组件名称] 组件。

## 功能需求
[详细描述组件功能、交互行为、边界情况]

## 技术约束
- 框架：Vue 3 Composition API + TypeScript
- UI 库：[Element Plus / Ant Design Vue / Naive UI]
- 状态管理：[Pinia / 组件内部状态]
- 样式方案：[scoped CSS / Tailwind CSS]

## Props 定义
| 属性名 | 类型 | 必填 | 默认值 | 说明 |
|--------|------|:--:|--------|------|
| ... | ... | ... | ... | ... |

## Events 定义
| 事件名 | 参数 | 触发时机 |
|--------|------|---------|
| ... | ... | ... |

## 输出要求
- 完整的 .vue 单文件组件
- 包含 TypeScript 类型定义
- 包含必要的错误处理和加载状态
- 包含基础的可访问性（aria 属性）
```

### 3.2 生成单元测试

```
请为以下组件生成单元测试，使用 Vitest + Vue Test Utils：

[粘贴组件代码]

## 测试要求
- 覆盖所有 props 的正常值和边界值
- 覆盖所有 emit 事件
- 覆盖所有用户交互（点击、输入、键盘事件）
- 覆盖异步操作（loading、error 状态）
- 使用 describe/it 组织测试用例
- 每个测试用例包含清晰的描述

## 输出格式
```typescript
import { describe, it, expect, vi } from 'vitest';
import { mount } from '@vue/test-utils';
// ... 完整测试代码
```
```

### 3.3 重构代码

```
请重构以下代码，遵循以下原则：
1. 单一职责：每个函数只做一件事
2. 提取可复用逻辑：重复代码抽取为 composable
3. 类型安全：补充完整的 TypeScript 类型
4. 错误处理：添加必要的 try/catch 和边界处理
5. 性能优化：避免不必要的重渲染和计算

[粘贴原始代码]

请在重构后的代码中使用注释标注关键改动。
```

### 3.4 审查代码

```
请审查以下代码，从以下维度逐一检查：

1. **类型安全**：是否有 any 类型滥用、缺少类型守卫
2. **竞态条件**：异步操作是否处理了取消（AbortController）、cleanup
3. **内存泄漏**：事件监听/定时器是否在组件卸载时清理
4. **安全漏洞**：是否有 XSS 风险（v-html 未过滤）、敏感信息泄露
5. **性能问题**：是否有不必要的重渲染、大列表未虚拟化
6. **可访问性**：是否缺少 aria 属性、键盘导航支持
7. **代码风格**：是否符合项目规范

对每个问题标注严重程度（高/中/低）和修复建议。
```

---

## 四、复杂场景 Prompt 实战

### 4.1 几百个字段的复杂表单

面对几百个字段的复杂表单，需要将 Prompt 拆解为多个层次：

**第一层：状态管理架构 Prompt**

```
你是一名前端架构师。我们需要管理一个包含 200+ 字段的复杂表单，请设计状态管理方案。

## 业务背景
- 表单分布：基础信息(30字段)、业务配置(50字段)、权限设置(20字段)、高级选项(100字段)
- 字段间存在复杂依赖：A 字段的值决定 B 字段的显示/隐藏/可选值
- 需要支持草稿保存、表单校验、分步提交

## 设计要求
1. 使用 Pinia 按业务模块拆分为多个 store
2. 使用 shallowRef 减少深度响应式的性能开销
3. 设计字段依赖关系的声明式配置方案
4. 草稿自动保存到 localStorage，防抖 2 秒
5. 表单提交时合并所有模块的 store 数据

## 输出格式
- 架构图（Markdown 层级结构）
- Pinia store 的 TypeScript 类型定义
- 字段依赖配置的数据结构
- 草稿保存/恢复的核心逻辑
```

**第二层：依赖规则引擎 Prompt**

```
基于以下字段依赖关系，实现一个声明式的表单联动规则引擎：

## 依赖规则示例
```typescript
const rules = [
  {
    // 当"业务类型"为"电商"时，显示"支付方式"字段组
    trigger: 'businessType',
    condition: (val) => val === 'ecommerce',
    action: 'show',
    targets: ['paymentMethod', 'paymentGateway', 'refundPolicy']
  },
  {
    // 当"用户等级"为"VIP"时，"折扣率"字段可选范围变为 0.5-0.9
    trigger: 'userLevel',
    condition: (val) => val === 'vip',
    action: 'updateRules',
    targets: {
      field: 'discountRate',
      rules: { min: 0.5, max: 0.9 }
    }
  }
];
```

## 实现要求
- 支持 trigger/condition/action/targets 四要素规则配置
- 支持级联规则（规则 A 触发规则 B）
- 使用 TypeScript 提供完整的类型推导
- 支持规则的动态添加/移除
```

### 4.2 避免 AI 幻觉的 Prompt 技巧

AI 幻觉（Hallucination）是指 AI 生成看似合理但实际不存在的内容——如胡编 API、虚构库版本、编造配置项。以下是避免幻觉的核心技巧：

**技巧一：约束 API 使用范围**

```
请使用以下已知库生成代码，不要使用任何不在列表中的库或 API：

允许使用的库：
- Vue 3.4+（Composition API、defineComponent、ref、computed、watch）
- Vue Router 4.x（useRouter、useRoute）
- Pinia 2.x（defineStore、storeToRefs）
- Element Plus 2.5+（ElForm、ElInput、ElSelect 等）
- lodash-es 4.x（debounce、throttle、cloneDeep）

如果功能无法用上述库实现，请明确说明"此功能需要额外引入 [库名]"，而不是编造不存在的 API。
```

**技巧二：要求引用官方文档**

```
请为每个使用的 API 添加注释，注明其来源（如 "// Vue 3 官方文档 - ref"）。
如果 API 是你推测的，请标注 "// 需验证 - 请查阅 [文档链接]"。
```

**技巧三：分步生成 + 验证**

```
请分三步完成任务：
步骤 1：列出实现方案和将使用的 API 清单（5-10 个），不要写代码
步骤 2：我确认 API 清单无误后，再生成完整代码
步骤 3：生成代码后，用注释标注每个关键 API 调用的作用
```

---

## 五、常见问题与避坑指南

| 问题 | 原因 | 解决方案 |
|------|------|---------|
| AI 使用过时的 API（如 Vue 2 语法） | 训练数据时间跨度大 | 在 Prompt 中明确版本号（如"Vue 3.4+，使用 `<script setup>` 语法"） |
| AI 编造不存在的库 | 训练数据包含虚构/错误内容 | 限定允许使用的库列表，要求引用来源 |
| AI 生成的代码缺少错误处理 | 默认生成"快乐路径"代码 | 在 Prompt 中要求"必须包含 loading、error、empty 三种状态" |
| Few-shot 示例被 AI 直接复制 | 示例与任务过于相似 | 使用不同领域的示例，体现"格式"而非"内容" |
| 长对话中 AI 遗忘早期约束 | 上下文窗口限制 | 在每轮对话开始时重申关键约束 |
| 复杂表单 Prompt 太长大 AI 抓不住重点 | 信息密度过高 | 拆解为多个子 Prompt，分步生成 |

---

> **学习导航**：下一步阅读 [03-AI代码审查与质量管控](./03-AI代码审查与质量管控.md) 学习如何建立 AI 代码的质量防线。

---

## 常见面试题

### 1. Prompt 工程的五要素是什么？每个要素在前端代码生成中如何应用？

一个高质量的 Prompt 包含五个核心要素，每个要素在前端代码生成中有其特定的应用方式：

**五要素定义与前端的应用：**

| 要素 | 定义 | 前端代码生成中的应用示例 |
|------|------|------------------------|
| **角色设定** | 为 AI 设定专业身份和思维模式 | "你是一名资深 Vue 3 前端工程师，擅长组件抽象和 TypeScript 类型设计" |
| **任务描述** | 清晰说明要完成的具体任务 | "创建一个可复用的搜索表单组件，包含关键字搜索（防抖 300ms）、分类下拉筛选、日期范围选择" |
| **上下文信息** | 提供项目技术栈、文件路径、现有代码风格 | "项目使用 Vue 3 Composition API + TypeScript + Element Plus，组件放置在 src/components/common/，参考 @file:src/components/common/BaseForm.vue 的风格" |
| **输出格式** | 约束输出结构和格式 | "输出完整的 .vue 单文件组件，包含 `<template>`、`<script setup lang="ts">`、`<style scoped>` 三个部分" |
| **约束条件** | 限制技术选型、编码规范、边界条件 | "使用 defineProps 和 defineEmits、防抖使用 lodash-es 的 debounce、所有文本使用中文、必须处理 loading/error/empty 三种状态" |

**为什么五要素缺一不可？**

- **缺少角色设定**：AI 可能输出初级水平的代码，缺少架构思维
- **缺少任务描述**：AI 会自由发挥，输出与需求不匹配
- **缺少上下文**：AI 可能使用错误的技术栈（如 Vue 2 语法、Ant Design 而非 Element Plus）
- **缺少输出格式**：AI 可能输出散乱的代码片段，无法直接使用
- **缺少约束条件**：AI 可能生成无错误处理、无类型定义、不符合项目规范的代码

**实战对比：**

```
❌ 低质量 Prompt（缺少 4 个要素）：
"写一个搜索组件"

✅ 高质量 Prompt（五要素齐全）：
"你是一名资深 Vue 3 前端工程师（角色设定）。
请创建一个搜索表单组件（任务描述），
项目使用 Vue 3 + TypeScript + Element Plus，放在 src/components/common/（上下文），
输出完整的 .vue 单文件组件（输出格式），
使用 Composition API、defineProps/defineEmits，搜索框防抖 300ms，处理 loading/error 状态（约束条件）。"
```

---

### 2. Few-shot 示例在 Prompt 中起什么作用？如何构造有效的 Few-shot 示例？

**Few-shot 的核心作用：**

Few-shot（少样本示例）是通过提供 1-3 个"输入-输出"示例，让 AI 模仿示例的格式、风格和质量标准。研究表明，Few-shot 可以将 AI 输出的准确率提升 50% 以上。

它在 Prompt 工程中扮演三个关键角色：

1. **格式校准**：通过示例明确输出格式，减少格式错误
2. **风格对齐**：让 AI 理解期望的代码风格（命名规范、缩进、注释风格等）
3. **质量基准**：示例的质量直接决定输出的质量——"垃圾进，垃圾出"

**构造有效 Few-shot 示例的四个原则：**

**原则一：示例与任务同领域、不同内容**

```
✅ 正确做法：
任务：生成商品卡片组件
示例：用户头像组件（展示"格式"，内容不同）

❌ 错误做法：
任务：生成商品卡片组件
示例：商品卡片组件（AI 会直接复制示例内容）
```

**原则二：示例必须包含完整结构**

```
❌ 不完整的示例（AI 会模仿残缺结构）：
```vue
<template>
  <div>{{ name }}</div>
</template>
```

✅ 完整的示例：
```vue
<template>
  <div class="user-card">
    <img :src="avatar" :alt="name" />
    <span>{{ name }}</span>
  </div>
</template>

<script setup lang="ts">
interface Props { avatar: string; name: string; }
const props = defineProps<Props>();
</script>

<style scoped>
.user-card { display: flex; align-items: center; }
</style>
```
```

**原则三：示例数量控制在 1-3 个**

```
1 个示例：适合简单格式对齐（如生成测试用例）
2 个示例：适合中等复杂度（如生成组件，展示不同复杂度的写法）
3 个示例：适合高复杂度（如生成多种变体，展示不同场景的处理方式）
超过 3 个：收益递减，且消耗大量上下文窗口
```

**原则四：示例覆盖边界情况**

```typescript
// 示例中展示边界处理，AI 会在生成时模仿
const handleSubmit = async () => {
  if (loading.value) return;           // 防止重复提交
  loading.value = true;
  try {
    await submitForm(props.data);
    emit('success');
  } catch (err) {
    error.value = err.message;         // 错误处理
  } finally {
    loading.value = false;             // 状态重置
  }
};
```

**面试要点：** 面试官关注的是你是否理解 Few-shot 的"模仿机制"——AI 不会创新，只会模仿。示例决定输出质量，因此构造示例是 Prompt 工程中最需要投入精力的环节。

---

### 3. AI 幻觉（Hallucination）在代码生成中如何表现？有哪些防范策略？

**AI 幻觉在代码生成中的四种典型表现：**

| 幻觉类型 | 具体表现 | 实际案例 |
|---------|---------|---------|
| **虚构 API** | 调用不存在的库方法、属性、配置项 | `Vue.set()`（Vue 3 中已移除）、`ElementPlus.Message.success()`（不存在的方法名） |
| **过时语法** | 使用已在当前版本中废弃的 API 或语法 | 在 Vue 3 中使用 `this.$emit`、`filters`、`Vue.extend()` |
| **虚构导入路径** | 导出来自不存在的路径的模块 | `import { useForm } from 'element-plus/es/form'`（实际路径不同） |
| **逻辑错误** | 代码"看起来正确"但运行时行为错误 | 忘记 cleanup 导致竞态条件、未处理 Promise rejection |

**系统化防范策略（从 Prompt 到 CI 的多层防线）：**

**第一层：Prompt 层约束（源头控制）**

```
策略 1：限定 API 使用范围
"请使用以下已知库生成代码，不要使用任何不在列表中的库或 API：
- Vue 3.4+（ref、computed、watch、defineComponent 等）
- Element Plus 2.5+（ElForm、ElInput、ElSelect 等）
- lodash-es 4.x（debounce、throttle、cloneDeep）
如果功能无法用上述库实现，请明确说明而非编造 API。"

策略 2：要求标注 API 来源
"为每个使用的 API 添加注释，注明其来源（如 '// Vue 3 官方文档 - ref'）。
如果 API 是你推测的，请标注 '// 需验证'。"

策略 3：分步生成 + 验证
"请分三步完成任务：
步骤 1：列出将要使用的 API 清单（5-10 个），不要写代码
步骤 2：我确认 API 清单无误后，再生成完整代码
步骤 3：生成代码后，用注释标注每个关键 API 调用"
```

**第二层：ESLint 规则拦截（自动检测）**

```javascript
// eslint.config.mjs - 拦截 AI 幻觉 API
import tseslint from 'typescript-eslint';

export default [
  ...tseslint.configs.recommended,
  {
    rules: {
      // 拦截 Vue 3 中不存在的 Vue 2 API
      'no-restricted-imports': ['error', {
        patterns: ['vue/composition-api', '@vue/composition-api']
      }],
      // 拦截未处理的 Promise（AI 经常遗漏）
      '@typescript-eslint/no-floating-promises': 'error',
      // 拦截过时的 Vue API
      'no-restricted-properties': ['error', {
        object: 'Vue', property: 'set', message: 'Vue 3 中不存在 Vue.set()'
      }]
    }
  }
];
```

**第三层：自定义 AST 规则（深度拦截）**

```javascript
// 自定义 ESLint 规则：拦截 AI 幻觉 API 调用
module.exports = {
  rules: {
    'no-fake-api': {
      create(context) {
        return {
          CallExpression(node) {
            if (node.callee.type === 'MemberExpression') {
              const fullPath = `${node.callee.object.name}.${node.callee.property.name}`;
              const blockedAPIs = ['Vue.set', 'Vue.delete', 'Vue.extend', 'Vue.filter'];
              if (blockedAPIs.includes(fullPath)) {
                context.report({
                  node,
                  message: `疑似 AI 幻觉 API：'${fullPath}' 在 Vue 3 中不存在`
                });
              }
            }
          }
        };
      }
    }
  }
};
```

**第四层：TypeScript 类型检查（编译时拦截）**

```typescript
// TypeScript 会拦截不存在的 API 调用
// 例如：AI 生成的代码可能调用不存在的类型
import { NonExistentType } from 'vue'; // TS 编译错误！
```

**面试要点：** 面试官期望听到的是"多层防线"的思路——不是单一策略，而是从 Prompt 约束到 CI 检查的完整链路。重点强调"Prompt 层约束是最经济的手段，ESLint 自定义规则是最可靠的拦截"。

---

### 4. 面对几百个字段的复杂表单，如何设计 Prompt 策略？

面对 200+ 字段的复杂表单，一次性 Prompt 会让 AI 丢失上下文焦点，输出质量大幅下降。需要采用"分层 Prompt + 规则引擎"的策略。

**策略一：架构先行（第一层 Prompt）**

先让 AI 设计状态管理架构，而非直接生成代码：

```
你是一名前端架构师。我们需要管理一个包含 200+ 字段的复杂表单，请设计状态管理方案。

## 业务背景
- 表单分布：基础信息(30字段)、业务配置(50字段)、权限设置(20字段)、高级选项(100字段)
- 字段间存在复杂依赖：A 字段决定 B 字段的显示/隐藏/可选值
- 需要支持草稿保存、分步校验、分步提交

## 设计要求
1. 使用 Pinia 按业务模块拆分为多个 store
2. 使用 shallowRef 减少深度响应式开销
3. 设计字段依赖关系的声明式配置方案
4. 草稿自动保存到 localStorage，防抖 2 秒
```

**策略二：依赖规则引擎（第二层 Prompt）**

分离"字段依赖关系"和"UI 渲染"，让 AI 生成声明式规则配置：

```typescript
// 让 AI 生成这种声明式规则，而非嵌套的 if/else
const formRules = [
  {
    trigger: 'businessType',          // 触发字段
    condition: (val) => val === 'ecommerce', // 触发条件
    action: 'show',                    // 动作：显示/隐藏/禁用/更新选项
    targets: ['paymentMethod', 'paymentGateway', 'refundPolicy']
  },
  {
    trigger: 'userLevel',
    condition: (val) => val === 'vip',
    action: 'updateRules',
    targets: {
      field: 'discountRate',
      rules: { min: 0.5, max: 0.9 }
    }
  }
];
```

**策略三：模块化拆分 Prompt**

将 200+ 字段按业务模块拆分，每个模块独立生成：

```
模块 1 Prompt：生成"基础信息"表单（30 字段）
模块 2 Prompt：生成"业务配置"表单（50 字段）
模块 3 Prompt：生成"权限设置"表单（20 字段）
模块 4 Prompt：生成"高级选项"表单（100 字段）
模块 5 Prompt：生成"表单容器"组件（整合所有模块 + 步骤导航 + 草稿/提交）
```

**策略四：性能优化 Prompt**

```typescript
// 在 Prompt 中明确性能要求
"对于 200+ 字段的表单，请使用以下性能优化策略：
1. 使用 shallowRef 替代 ref，减少深度响应式开销
2. 使用 v-memo 缓存不变化的字段组
3. 分步渲染：只渲染当前步骤的字段，其余使用 v-if 延迟渲染
4. 表单校验按步骤执行，避免全量校验"
```

**全套 Prompt 策略总结：**

```
第一层：架构设计 Prompt（状态管理方案）
第二层：规则引擎 Prompt（字段依赖声明式配置）
第三层：模块拆分 Prompt（按业务模块逐个生成子表单）
第四层：容器整合 Prompt（步骤导航 + 草稿 + 提交）
第五层：性能优化 Prompt（shallowRef + v-memo + 分步渲染）
```

---

### 5. 如何构造一个能生成高质量 Vue 3 组件的 Prompt？

以下是一个可直接使用的、经过实战验证的 Vue 3 组件生成 Prompt 模板，每个部分都有明确的设计意图：

```markdown
你是一名资深 Vue 3 前端工程师，以"代码可维护性"为核心价值观。
请生成一个 [组件名称] 组件。

## 功能需求
[详细描述组件功能、交互行为、边界情况]
- 正常状态：XXX
- 加载状态：显示骨架屏
- 空状态：显示空数据提示
- 错误状态：显示错误信息 + 重试按钮
- 边界情况：XXX

## 技术约束
- 框架：Vue 3.4+ Composition API + `<script setup lang="ts">`
- UI 库：Element Plus 2.5+
- 状态管理：Pinia 2.x（如需跨组件共享状态）
- 样式方案：scoped CSS + CSS Variables
- 类型定义：使用 TypeScript interface 定义 Props/Emits

## Props 定义
| 属性名 | 类型 | 必填 | 默认值 | 说明 |
|--------|------|:--:|--------|------|
| ... | ... | ... | ... | ... |

## Events 定义
| 事件名 | 参数 | 触发时机 |
|--------|------|---------|
| ... | ... | ... |

## 输出要求
1. 完整的 .vue 单文件组件
2. 使用 `defineProps<T>()` 和 `defineEmits<T>()` 定义类型
3. 包含 JSDoc 注释（组件用途、Props 说明）
4. 覆盖 loading / error / empty 三种状态
5. 包含基础的可访问性（aria-label、role 属性）
6. 异步操作使用 try/catch + AbortController
7. 所有事件处理函数有明确的命名（handle + 动词 + 名词）
```

**Prompt 设计要点解析：**

| 设计要点 | 为什么重要 | 示例 |
|---------|-----------|------|
| 角色设定中的"价值观" | 引导 AI 从可维护性角度思考，而非只是"能跑就行" | "以代码可维护性为核心价值观" |
| 明确四种状态 | AI 默认只生成"快乐路径"，必须显式要求 | loading / error / empty / normal |
| Props/Events 表格 | 用表格格式约束输入，AI 不会遗漏 | 必填/默认值/说明三列 |
| 具体的技术约束 | 避免 AI 使用过时 API 或错误版本 | "Vue 3.4+ Composition API + `<script setup>`" |
| 可访问性要求 | AI 默认忽略 a11y，必须显式要求 | aria-label、role 属性 |
| 异步操作规范 | AI 默认忽略 cleanup 和错误处理 | try/catch + AbortController |

**进阶技巧：附加 Few-shot 示例**

在 Prompt 末尾附加一个 10-20 行的组件示例，展示期望的代码风格和质量标准——这比任何文字描述都更有效。

---

## 本章学习自检

请逐项检查自己是否掌握了以下知识点：

- [ ] 我能说出 Prompt 工程的五要素（角色设定、任务描述、上下文信息、输出格式、约束条件），并能在前端场景中逐一应用
- [ ] 我理解 Few-shot 示例的作用（格式校准、风格对齐、质量基准），并能构造 1-3 个有效的示例
- [ ] 我能识别 AI 幻觉的四种典型表现（虚构 API、过时语法、虚构导入路径、逻辑错误），并掌握多层防范策略
- [ ] 面对 200+ 字段的复杂表单，我能设计分层 Prompt 策略（架构先行、规则引擎、模块拆分、容器整合）
- [ ] 我能独立构造一个生成高质量 Vue 3 组件的完整 Prompt，包含四种状态处理和可访问性要求
- [ ] 我掌握了结构化输出约束技巧（JSON Schema、Markdown 表格），能减少 AI 输出的随意性
- [ ] 我理解"分步生成 + 验证"的策略，知道何时该让 AI 先出方案再出代码
- [ ] 我能在自己的日常开发中使用本章提供的 Prompt 模板库（组件生成、测试生成、代码重构、代码审查）