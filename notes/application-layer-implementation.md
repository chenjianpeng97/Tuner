---

**名称**：application-layer-implementation (应用层实现)

**描述**：在此仓库中实现应用层交互器（Interactors）、查询服务、端口（Ports）和 DTO。用于通过端口编排领域逻辑、授权、事务和数据访问，同时保持应用层与框架无关。

---

# 应用层实现

## 概述

构建应用级用例处理器（Use Case Handlers），通过端口（Ports）协调领域逻辑、授权和持久化操作。

## 工作流

1.  **将用例识别为命令（Commands）或查询（Queries）**
    - 命令用于改变状态；查询是经过优化的读取操作。
    - 示例：`application/commands/create_user.py`，`application/queries/list_users.py`。

2.  **定义请求和响应 DTO**
    - 请求输入使用带有 `slots` 的 `dataclass`。
    - 对于跨越层边界的响应，使用 `TypedDict`。

3.  **实现交互器（Interactor）或查询服务**
    - 使用 `application/common/services/authorization` 验证权限。
    - 通过 `application/common/services/current_user` 获取当前用户。
    - 调用领域服务和端口，**禁止**调用基础设施层。

4.  **使用端口处理外部影响（External Effects）**
    - **命令侧**：`application/common/ports/user_command_gateway`、刷新器（Flusher）、事务管理器（Transaction Manager）。
    - **查询侧**：`application/common/ports/user_query_gateway`。

5.  **控制事务和错误流**
    - 执行刷新（Flush）、处理预期的领域错误，然后提交（Commit）。
    - 在函数签名中保留基础设施异常，以便控制器（Controllers）进行错误映射。

6.  **在 IoC 中注册 Provider**
    - 更新 `setup/ioc/application.py`，添加新的交互器、查询服务和端口绑定。

## 准则 (Guardrails)

- **框架无关**：禁止在此层导入 FastAPI、SQLAlchemy 或其他基础设施框架。
- **使用领域对象**：利用领域值对象进行校验和标准化。
- **无状态性**：保持交互器无状态且可独立调用。
- **避免交互器间调用**：避免一个交互器直接调用另一个交互器；如有需要，将共享逻辑提取到服务（Services）中。

## 审查清单

- DTO 是否是纯粹且可序列化的？
- 是否在敏感操作执行前进行了授权检查？
- 端口是否仅表达依赖关系（具体实现应留在基础设施层）？
- 事务边界是否清晰且一致？
