---

**名称**：backend-testing (后端测试)

**描述**：在此仓库中添加并运行后端测试。用于在 `backend/tests` 下编写单元测试、集成测试或性能测试，以及通过 `Makefile` 目标指令运行 `pytest` 和测试覆盖率（Coverage）统计。

---

# 后端测试

## 概述

遵循现有的 `pytest` 结构添加测试，并使用 `Makefile` 中的目标指令来执行测试和生成覆盖率报告。

## 测试结构

- **单元测试**：`tests/app/unit/{domain,application,infrastructure,setup}`
- **集成测试**：`tests/app/integration`
- **性能测试**：`tests/app/performance`（使用 `slow` 等标记）
- **工厂与辅助工具**：`tests/app/unit/factories`（用于生成测试数据）

## 工作流

1.  **选择测试类型和位置**
    - **领域规则**：`tests/app/unit/domain`
    - **应用服务**：`tests/app/unit/application`
    - **基础设施适配器**：`tests/app/unit/infrastructure`
    - **配置/安装设置**：`tests/app/unit/setup`
    - **跨边界行为**：`tests/app/integration`

2.  **遵循现有的 pytest 模式**
    - 异步函数使用 `@pytest.mark.asyncio`。
    - 对于规则矩阵（多组输入测试），使用 `@pytest.mark.parametrize`。
    - 使用工厂（Factories）来生成一致的值对象和实体。

3.  **断言领域不变性（Invariants）和错误行为**
    - 示例：验证值对象校验是否抛出 `DomainTypeError`。
    - 示例：验证领域服务在角色无效时是否抛出 `RoleAssignmentNotPermittedError`。

4.  **基础设施测试应聚焦于适配器行为**
    - 对于耗时的哈希计算或 I/O 操作，使用 `slow` 等标记。
    - 验证适配器是否正确实现了端口（Port）的预期功能，并返回了领域类型。

5.  **使用 Makefile 目标运行测试**
    - **运行单元测试**：`make code.test`（执行 `pytest -v`）
    - **生成覆盖率**：`make code.cov`（执行测试并合并覆盖率报告）
    - **生成 HTML 报告**：`make code.cov.html`（生成可视化的覆盖率报告）

## 准则 (Guardrails)

- **对齐层级边界**：确保测试逻辑与所属的架构层级保持一致。
- **优先使用工厂**：避免手动构建复杂的领域对象，优先使用工厂方法。
- **稳定断言**：对领域错误（Domain Errors）进行稳定的类型断言，而不是匹配易变的错误字符串。

## 审查清单

- 新功能是否在其对应的层级拥有单元测试覆盖？
- 所有的异步测试是否都包含了 `@pytest.mark.asyncio` 标记？
- 涉及重型性能消耗的测试是否已标记为 `slow`？
- 覆盖率统计运行正常，且核心层测试未导入任何基础设施代码？
