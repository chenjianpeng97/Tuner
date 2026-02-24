---
name: requirements-clarifier
description: "Clarify ambiguous product requirements through targeted questioning, then produce two structured outputs: a normalized requirements document and an implementation task list. Use when users provide raw ideas, incomplete specs, evolving需求，或希望将模糊需求快速收敛为可执行输入。"
---

# Requirements Clarifier

## Overview

Transform loose需求描述 into可执行输入。
先问关键澄清问题，再输出结构化需求文档与结构化开发任务清单。

## Workflow

1. 收敛输入上下文
	- 读取用户给出的原始需求、已存在文档、当前约束（MVP、优先级、时间/人力）。
	- 标记信息状态：`已明确`、`有冲突`、`缺失`。

2. 执行最小充分澄清
	- 按优先级提问：范围边界 > 核心实体与关系 > 关键流程 > 约束与验收。
	- 每轮问题控制在 3-7 个，优先单选/可判定问题，减少开放题。
	- 发现冲突时先做“冲突对齐问题”，不直接进入任务拆解。

3. 形成澄清结论
	- 输出 `澄清摘要`：目标、非目标、术语定义、关键规则、开放问题。
	- 对未决项打标：`[OPEN]`，并给出默认假设（仅在用户允许时使用）。

4. 生成结构化需求文档
	- 使用 `references/requirements_doc_template.md` 模板。
	- 以规则驱动描述业务，不写实现细节。
	- 对每个功能点保持 `能力描述 + 规则` 结构。

5. 生成结构化开发任务列表
	- 使用 `references/implementation_tasks_template.md` 模板。
	- 按迭代或主题组织，任务拆分方式根据项目架构自适应（如按模块、分层、前后端、数据/接口）。
	- 每个任务必须包含验收标准，并可直接映射到后续实现与测试。

6. 输出交付建议
	- 推荐保存路径与下一步动作（如 feature 拆解、接口草图、测试设计、原型验证）。
	- 如果开放问题影响实现，阻止进入下一步并明确需要用户确认。

## Clarification Focus

- 目标与边界：本期必须做什么、明确不做什么。
- 角色与权限：谁发起、谁审批、谁查看、谁修改。
- 实体与关系：核心对象、关联关系、生命周期。
- 关键流程：主流程、分支流程、异常流程。
- 数据口径：统计口径、去重规则、边界定义。
- 非功能约束：并发、幂等、可追溯性、性能预算。

完整问题库见 `references/clarification_question_bank.md`。

## Output Contract

1. 输出一份结构化需求文档
	- 建议路径：`docs/requirements.md`（可按项目调整）
	- 格式：背景/目标 + 功能模块 + 每项规则。

2. 输出一份结构化开发任务清单
	- 建议路径：`docs/implementation_tasks.md`（可按项目调整）
	- 格式：按阶段/主题组织；每项含负责人视角、实现动作、验收标准。

3. 输出“待确认问题”清单
	- 列出会阻断设计或实现的 `[OPEN]` 项。
	- 每个 `[OPEN]` 提供 1 个默认选项，等待用户确认。

## Resources

- 问题库：`references/clarification_question_bank.md`
- 需求文档模板：`references/requirements_doc_template.md`
- 开发任务模板：`references/implementation_tasks_template.md`

按需读取 references，避免把大段模板直接塞进主流程上下文。
