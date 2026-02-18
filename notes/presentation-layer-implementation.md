---

**名称**：presentation-layer-implementation (表现层实现)

**描述**：在此仓库中实现表现层控制器和请求模型。用于添加 HTTP 路由、校验 Schema、错误映射以及将外部请求适配到应用交互器（Interactors）的控制器装配。

---

# 表现层实现

## 概述

添加 HTTP 控制器和请求模型，用于验证输入、调用交互器或查询服务，并将错误映射为 HTTP 响应。

## 工作流

1.  **定位控制器区域**
    - 按上下文分组，在 `app/presentation/http/controllers` 中管理路由器（Routers）。
    - 遵循 `users/create_user.py` 和 `account/change_password.py` 中的模式。

2.  **定义请求模型**
    - 使用 Pydantic 模型进行请求校验和 OpenAPI Schema 生成。
    - 保持模型为不可变（Frozen）且极简；避免在模型中包含业务规则。

3.  **创建路由函数**
    - 使用 `ErrorAwareRouter` 及其错误映射表（Error Maps）处理领域和基础设施异常。
    - 使用 `@inject` 和 `FromDishka` 进行依赖注入。
    - 对于需要身份验证的端点，使用 `Security(cookie_scheme)`。

4.  **将请求映射到应用层 DTO**
    - 将 Pydantic 输入模型转换为应用层的 `dataclass` 请求对象。
    - 从交互器或查询服务接收并返回 `TypedDict` 类型的响应。

5.  **注册路由器**
    - 将路由器添加到相应的模块中，确保其被包含在应用的初始化设置中。

## 准则 (Guardrails)

- **保持控制器“薄”**：控制器应只负责校验和数据转换。
- **禁止反向导入**：严禁在此层导入 SQLAlchemy 模型或基础设施适配器。
- **异常处理位置**：将异常到 HTTP 状态码的映射保留在控制器层，而不是核心层（领域/应用层）。
- **校验职责隔离**：不要在 Pydantic 校验器（Validators）中嵌入业务规则。

## 审查清单

- 请求/响应的映射是否显式且极简？
- 错误映射表是否覆盖了相关的领域异常和基础设施异常？
- 错误码映射是否准确：授权错误映射为 403，认证错误为 401，验证错误为 400 或 422？
- 控制器是否仅调用了应用层的交互器或查询服务？
