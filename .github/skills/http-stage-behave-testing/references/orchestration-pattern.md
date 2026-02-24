# HTTP 编排验证模式

## 目标
用 `--stage http` 只验证控制器编排是否正确，不验证业务规则本身。

## 1) 先对齐控制器依赖边界
- 读取控制器函数签名，找出 `FromDishka[...]` 注入点。
- 只 mock 控制器可见的应用层类型（如 `CommandInteractor` / `QueryService`）。
- 不 mock port/gateway（这些属于应用层内部单测范围）。

## 2) 为每个注入点补齐测试 DI
在 `features/mock_app.py` 中同步两处：
- `MockRegistry._init_mocks()`：新增 `AsyncMock` 字段。
- `_MockProvider`：新增 `@provide` 方法返回该 mock。

如果新增了命令/查询拆分（例如 `SpreadsheetCommandInteractor` + `SpreadsheetQueryService`），必须同时接入两类 mock。

## 3) Step 定义采用“三段式”
- Given：仅准备上下文状态（ID、预置对象、关联关系），不发请求。
- When：
  - 构造 presentation 层 Pydantic request（`model_dump(mode="json")`）。
  - 配置 mock 返回（特别是 query 的响应数据）。
  - 发送真实 HTTP 请求（`context.client.<method>`）。
- Then：
  - 断言 HTTP 状态码。
  - 断言响应体关键字段。
  - 断言 mock 被调用的 `operation` 和关键 payload 子集。

## 4) 编排断言建议
建议在 step 文件内复用 helper：
- `_remember_expected_dispatch(operation, kind, payload_subset)`
- `_assert_expected_dispatch_called()`

断言最少包含：
- 调用目标：`command` 或 `query`。
- 业务操作名：如 `create_table_from_template`。
- 关键参数：如 `project_id/table_id`。

## 5) Query 场景要做“响应驱动”
对于读取类接口：
- 在 mock 中返回可被 response model 验证的数据。
- Then 断言响应结构与关键业务字段，而不是只断言 200。

## 6) 失败定位优先级
当 Behave 失败时按顺序排查：
1. step 正则匹配冲突/歧义；
2. 请求模型与控制器 schema 不一致；
3. mock 未注入或调用到了错误 interactor；
4. 枚举/VO 值不合法（如模板 key 别名问题）。

## 7) 回归执行顺序
1. 单场景回归：先跑失败场景。
2. 分组回归：跑对应 feature 文件。
3. 全量回归：跑全部 `--stage http` 目标。

推荐命令：
- `behave --stage http <feature> -n "<scenario>"`
- `behave --stage http <feature_or_dir>`
