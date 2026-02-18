---

**名称**：http-stage-behave-testing (HTTP 阶段 Behave 测试)

**描述**：实现 Behave 的 HTTP 阶段步骤定义（Step Definitions），用于隔离测试表现层控制器。将 Gherkin 特性文件（Feature Files）转化为可运行的测试，通过模拟的 Dishka 依赖注入（DI）运行 FastAPI 路由（无需数据库、认证基础设施或外部服务）。

---

# HTTP 阶段 Behave 测试

## 概述

通过使用 `AsyncMock` 实例替换所有 Dishka 注入的交互器（Interactors）和处理器（Handlers），隔离测试 HTTP 控制器的编排逻辑。请求通过 FastAPI 的 `TestClient` 运行，并对 HTTP 状态码和响应体进行断言。

**此方法验证：**

- 控制器路由和请求反序列化。
- `error_map` 中的异常到 HTTP 状态码的转换。
- 错误和成功案例下的响应体格式。
- 中间件行为（例如 `ASGIAuthMiddleware` 的 Cookie 处理）。

**此方法不测试：** 业务逻辑、数据库访问或外部服务。

## 关键文件

| 文件                                 | 用途                                                             |
| :----------------------------------- | :--------------------------------------------------------------- |
| `features/<name>.feature`            | Gherkin 场景（领域语言描述）                                     |
| `features/mock_app.py`               | `MockRegistry` + `_MockProvider` + `create_test_app()`           |
| `features/http_environment.py`       | Behave `--stage http` 钩子（`before_all`, `before_scenario` 等） |
| `features/http_steps/step_<name>.py` | 步骤定义（Given/When/Then）                                      |

## 工作流

1.  **编写或接收 `.feature` 文件**
    - 存放在 `features/` 目录下。
    - 遵循规则驱动结构（`Feature` → `Rule` → `Scenario` → `Given/When/Then`）。

2.  **创建或扩展 `features/mock_app.py`**
    - 定义 `MockRegistry`：为每个 Dishka 提供的交互器/处理器设置一个 `AsyncMock` 属性。
    - 定义 `_MockProvider(Provider)`：每个类型对应一个 `@provide` 方法，从注册表中返回相应的 Mock。
    - 定义 `create_test_app(registry)`：构建一个包含生产路由和中间件但使用模拟 DI 容器的 `FastAPI` 应用。

    ```python
    # 示例代码结构
    class MockRegistry:
        def __init__(self) -> None:
            self._init_mocks()
        def _init_mocks(self) -> None:
            self.create_user: AsyncMock = AsyncMock() # 每个交互器一个
        def reset_all(self) -> None:
            self._init_mocks()
    ```

3.  **创建或扩展 `features/http_environment.py`**
    - 将 `features/` 和 `backend/src` 添加到 `sys.path`。
    - `before_all`：实例化 `MockRegistry` 并创建测试应用，存入 `context`。
    - `before_scenario`：重置所有 Mock，初始化空状态字典，并创建全新的 `TestClient`。
    - `after_scenario`：关闭 `TestClient`。

4.  **在 `features/http_steps/` 下实现步骤定义**
    遵循三阶段模式：
    - **Given（假设）**：仅记录场景状态（填充 `context.users` 等）。**不**进行 HTTP 调用，**不**配置 Mock。
    - **When（当）**：配置 Mock 行为，然后发起 HTTP 请求：
      - 异常场景：设置 `side_effect = <DomainException>(...)`。
      - 成功场景：设置 `return_value = <value>`。
      - 通过 `context.client` 发送请求。
    - **Then（那么）**：断言 `context.response.status_code` 和响应内容。

5.  **运行验证**
    ```bash
    behave --stage http --dry-run  # 验证步骤匹配
    behave --stage http           # 执行测试
    ```

## 向测试套件添加新控制器

1.  在 `MockRegistry._init_mocks()` 中添加 `AsyncMock` 属性。
2.  在 `_MockProvider` 中添加对应的 `@provide` 方法。
3.  在步骤定义文件中导入相关的领域/基础设施异常。
4.  按照三阶段模式编写 Given/When/Then 步骤。
5.  查看控制器的 `error_map` 以确定预期的 HTTP 状态码。

## 如何发现 Mock 目标

识别哪些类型需要 Mock：

1.  查看 `app/setup/ioc/` 中的 Dishka Provider —— 每个 `@provide` 定义了一个返回类型。
2.  查看控制器函数签名 —— `FromDishka[<Type>]` 参数就是注入点。
3.  **仅 Mock 直接注入控制器的类型**（交互器、查询服务）。**不要** Mock 端口（网关、刷新器等），因为它们对表现层是透明的。

## 准则 (Guardrails)

- **Mock 边界**：在“交互器/处理器”边界进行 Mock，而不是端口/网关级别。表现层只应感知交互器。
- **不要测试逻辑**：不要在 HTTP 步骤中测试业务逻辑，那是单元测试的任务。
- **保持步骤简洁**：Given 记录状态，When 配置 Mock 并发请求，Then 执行断言。
- **使用生产常量**：从生产代码中导入领域异常和常量，不要重复定义错误字符串。
- **API 路径一致性**：步骤文件中的路径常量必须与路由器的层级结构完全匹配。

## 审查清单

- 被测控制器使用的每个 Dishka 注入类型是否都在 `MockRegistry` 和 `_MockProvider` 中有对应项？
- 步骤定义是否是从生产模块导入的领域异常？
- `before_scenario` 是否重置了 Mock 并创建了新的 `TestClient`？
- 状态码断言是否参考了控制器的 `error_map`？
- `behave --stage http --dry-run` 是否显示所有步骤均已匹配？
