---

**名称**：backend-feature-implementation (后端功能实现)

**描述**：在此 FastAPI 整洁架构（Clean-Architecture）仓库中实现后端功能的端到端工作流。用于将需求转化为跨领域层（Domain）、应用层（Application）、基础设施层（Infrastructure）和表现层（Presentation）的协调变更，并编排各层特定的实现技能。

---

# 后端功能实现

## 概述

将功能需求转化为具体的代码实现，同时保持整洁架构的边界，并遵循 `backend/README.md` 中说明的仓库规范和用户管理示例。

## 工作流

1.  **阅读需求并映射为行为**
    - 识别命令（Command，写操作）和查询（Query，读操作）、参与者（Actors）以及权限。
    - 区分业务不变性（Invariants）/领域规则与输入验证。

2.  **审查本地规范和示例**
    - 阅读 `backend/README.md` 以了解各层职责和依赖规则。
    - 以用户管理作为参考流程：`domain/services/user.py`（领域层）、`application/commands/create_user.py`（应用层命令）、`application/queries/list_users.py`（应用层查询）、`presentation/http/controllers/users/create_user.py`（表现层）。

3.  **按层拆分任务并调用子技能**
    - **领域规则、实体、值对象和领域服务**：使用 `domain-layer-implementation` 技能。
    - **交互器（Interactors）、端口（Ports）、DTO、事务和授权**：使用 `application-layer-implementation` 技能。
    - **基础设施适配器（数据映射器、读取器、认证适配器）和表现层控制器**：除非创建了专用技能，否则在此步骤完成。

4.  **实现基础设施和表现层的装配**
    - 根据需要添加或更新 `application/common/ports` 中的端口。
    - 在 `infrastructure/adapters` 中添加适配器，并在 `infrastructure/auth` 中添加处理器（若需要）。
    - 在 `presentation/http/controllers` 中添加控制器和请求模型。
    - 在 `setup/ioc/domain.py` 和 `setup/ioc/application.py` 中注册 Provider（依赖注入）。

5.  **验证错误流和契约**
    - 确保领域和应用层的异常在控制器中被映射为 HTTP 错误。
    - 保持 Pydantic 模型仅存在于表现层；确保领域/应用层不依赖具体框架。

6.  **添加或更新测试**
    - 优先为领域规则和应用层交互器编写单元测试；如果引入了新的基础设施行为，则添加集成测试。

## 输出清单

- **领域层 (Domain)**：实体（Entities）、值对象（Value Objects）、枚举（Enums）、异常（Exceptions）、服务（Services）以及必要的端口（Ports）。
- **应用层 (Application)**：请求/响应 DTO、交互器或查询服务、端口接口、权限检查、事务处理和数据刷新（Flush）处理。
- **基础设施层 (Infrastructure)**：针对端口的适配器、数据映射器/读取器、认证适配器、数据库模型或映射配置。
- **表现层 (Presentation)**：HTTP 控制器、请求 Schema 模型、错误映射表。
- **装配 (Wiring)**：`setup/ioc` 中的 Provider 注册，如果是新端点，还需注册路由。

## 准则 (Guardrails)

- **保持依赖方向**：内层绝对不能导入外层代码。
- **验证位置**：业务规则验证应放在领域/应用层，而非控制器中。
- **一致性**：尽早使用值对象来校验领域类型，确保数据一致性。
- **类型偏好**：响应契约优先使用 `TypedDict`，请求契约优先使用 `dataclass`。
