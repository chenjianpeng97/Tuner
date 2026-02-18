---

**名称**：domain-layer-implementation (领域层实现)

**描述**：在此仓库中实现领域层组件。用于定义实体、值对象、枚举、领域服务、异常和领域端口，同时保持业务规则独立于框架和基础设施。

---

# 领域层实现

## 概述

将业务规则和不变性（Invariants）建模为领域类型和服务，确保领域层与框架无关且保持稳定。

## 工作流

1.  **从需求中提取领域概念和不变性**
    - 识别实体（具有唯一标识）、值对象（无唯一标识）和领域服务。
    - 区分哪些规则属于业务不变性（Invariants），哪些属于过程性策略（Procedural Policies）。

2.  **创建或更新值对象 (Value Objects)**
    - 将校验（Validation）和标准化（Normalization）逻辑放在值对象的构造函数中。
    - 示例：`domain/value_objects/username.py`。

3.  **创建或更新实体 (Entities)**
    - 保持实体字段使用值对象和枚举进行类型标注。
    - 示例：`domain/entities/user.py`。

4.  **为不属于单一实体的行为添加领域服务 (Domain Services)**
    - 示例：`domain/services/user.py`，用于处理用户创建、密码操作以及角色/激活状态的变更。

5.  **为外部能力定义端口 (Ports)**
    - 在 `domain/ports` 中定义 ID 生成器或哈希计算等外部依赖的接口。
    - 示例：`domain/ports/user_id_generator.py`，`domain/ports/password_hasher.py`。

6.  **添加领域异常 (Domain Exceptions) 和枚举 (Enums)**
    - 保持错误粒度具体化，且仅在违反业务不变性时抛出。
    - 示例：`domain/exceptions/user.py`，`domain/enums/user_role.py`。

## 准则 (Guardrails)

- **禁止外部依赖**：在领域层中不得导入基础设施层代码、FastAPI、SQLAlchemy 或其他框架。
- **偏好充血值对象**：通过富值对象（Rich Value Objects）保持校验逻辑的本地化和一致性。
- **同步优先**：仅在端口（Port）明确要求时使用 `async`；纯领域逻辑应保持同步（Synchronous）。
- **使用领域异常**：使用专门的领域异常，而不是 HTTP 错误或数据库异常。

## 审查清单

- 实体和值对象是否使用了领域类型并强制执行了业务不变性？
- 领域服务是否仅依赖于其他领域类型和端口？
- 端口是否仅代表外部影响（Effect）的抽象，且此处不包含具体实现？
- 异常是否映射到了违反的业务规则，而非基础设施层面的失败？
