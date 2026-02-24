# Generic 组件冒烟测试模式

## 目标
为“基础能力”提供稳定、快速的冒烟入口，优先验证：
- 路由可达；
- 请求模型可反序列化；
- 控制器编排可调用到正确 command/query；
- 响应契约稳定。

## 推荐结构
- demo 控制器：承载与业务模板解耦的最小能力（例如 plain table）。
- smoke feature：只保留 1~3 条高价值路径。
- make 目标：一键执行 smoke。

## 设计原则
- 不引入业务语义（模板、复杂规则）。
- 请求体尽量小，但覆盖核心字段（名称、列、作用域 ID）。
- Then 中必须包含 dispatch 断言，避免“仅状态码通过”的假阳性。

## 示例场景（plain table）
1. Given demo project 存在。
2. When 创建不带模板的在线表格。
3. Then 返回创建成功。
4. And 断言 `spreadsheet_command.execute` 收到 `create_plain_table`。

## 执行建议
- 本地开发：每次改动控制器后先跑 smoke。
- 提交前：跑 smoke + 当前需求相关 feature。

可选命令约定：
- `make bdd-http-generic-smoke`
