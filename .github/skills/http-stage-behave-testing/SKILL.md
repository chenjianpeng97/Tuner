---
name: http-stage-behave-testing
description: Implement Behave HTTP-stage tests for FastAPI controllers with mocked Dishka DI, focusing on controller orchestration assertions (operation/payload dispatch) and response-contract checks. Use when adding or refactoring HTTP endpoints, turning Gherkin features into runnable --stage http tests, and building generic component smoke suites in demo-style modules.
---

# HTTP-Stage Behave Testing

## 目标

用 Behave `--stage http` 验证控制器层编排：路由、请求反序列化、DI 注入、异常映射、响应契约。

不要在这里验证业务规则、数据库行为、外部服务集成。

## 核心工作流

1. 将需求拆成可运行的 Feature/Rule/Scenario（`features/`）。
2. 在 `features/mock_app.py` 为新增注入类型补齐 `AsyncMock` + `@provide`。
3. 在 `features/http_environment.py` 保持每场景隔离（`reset_all()` + 新 `TestClient`）。
4. 在 `features/http_steps/` 按 Given/When/Then 实现真实 HTTP 调用。
5. Then 中同时断言：状态码、响应体关键字段、dispatch（operation/payload 子集）。
6. 先跑失败场景，再跑分组，最后跑全量 `--stage http`。

## 本仓库关键文件

- `features/mock_app.py`
- `features/http_environment.py`
- `features/http_steps/step_*.py`
- `app/presentation/http/controllers/**/router.py`

## 参考文档（按需读取）

- 编排验证细则（command/query 拆分、dispatch 断言、回归顺序）：
  - `references/orchestration-pattern.md`
- generic 组件冒烟模式（demo 模块、plain table、smoke 最小路径）：
  - `references/generic-smoke-pattern.md`

## 快速检查清单

- 只 mock 控制器注入边界（interactor/query service/handler）。
- When 阶段使用 presentation 层 Pydantic request 构造请求体。
- Query 场景必须校验响应模型字段，不只断言 200。
- `behave --stage http --dry-run` 无未匹配步骤。
- 回归结果为 0 failed / 0 error。
