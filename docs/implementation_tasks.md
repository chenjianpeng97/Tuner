# 项目开发任务清单（双工作流）

## 使用说明

- 目标:将需求拆分为两个可独立交付的部分
- Part A:动态在线表格组件（平台能力）
- Part B:需求管理动态模板（业务能力）
- 组织方式:按工作流 + 迭代，任务按 domain/application/infrastructure/presentation 拆分

## Workstream A：动态在线表格组件

### A0 基础资源模型

- A0-1 表格核心模型
  - domain:定义 Spreadsheet、Table、View、Column、Row、Cell
  - application:实现表/视图/行列单元格的基础命令与查询
  - infrastructure:新增 tables/views/columns/rows/cells 持久化模型
  - presentation:提供 `/spreadsheets` 基础 API
  - 验收标准:支持创建表、读取表视图、维护行列单元格

- A0-2 并发与幂等
  - domain:定义 version/etag 规则
  - application:写操作支持 expected_version 校验
  - infrastructure:版本字段与冲突检测
  - presentation:批量与上传类接口支持 idempotency_key
  - 验收标准:并发冲突可被识别，重试不产生重复写入

### A1 高级操作能力

- A1-1 批处理能力
  - application:实现 `:batch` 操作编排（atomic/dry_run）
  - infrastructure:批处理事务与结果回执
  - presentation:提供 `POST /tables/{id}:batch`
  - 验收标准:单次请求可执行多操作并返回逐项结果

- A1-2 视图能力
  - domain:定义 ViewType、过滤/排序/隐藏列配置
  - application:实现视图 CRUD
  - presentation:提供 views API
  - 验收标准:同一表支持多个视图及配置切换

- A1-3 资产挂接能力
  - domain:定义 Asset、AssetBinding、AssetFollow
  - application:上传、绑定、复制、跟随、同步
  - infrastructure:assets、asset_bindings、asset_relations
  - presentation:资产相关 API
  - 验收标准:支持先上传后绑定、复制跟随与分支

## Workstream B：需求管理动态模板

### B0 模板定义与实例化

- B0-1 预制模板定义
  - domain:定义 RequirementTemplate（模板键 + 固定列 + 可扩展列规则）
  - application:实现模板列表与实例化
  - presentation:模板查询与建表 API
  - 验收标准:至少包含两套模板
    - 项目跟踪视图（客户需求、设计资产、测试资产）
    - 产品需求列表（模块、子模块、L1-L9）

- B0-2 模板参数化
  - application:支持项目级层级名称配置（默认 L1/L2/L3，扩展至 L9）
  - infrastructure:项目模板配置持久化
  - 验收标准:同模板可按项目参数生成不同列定义

### B1 需求管理业务规则

- B1-1 客户需求与产品需求关系
  - domain:定义多对多关联规则
  - application:自动建联（下钻上下文）+ 手动关联/取消
  - infrastructure:关联表与索引
  - 验收标准:客户需求与产品需求稳定支持多对多

- B1-2 事项与研发需求统一
  - domain:客户需求实体 + label 规则
  - application:研发需求可下钻，事项仅标记跟踪
  - 验收标准:同实体可表达需求与事项，流程分叉正确

- B1-3 状态与审计
  - application:状态标签项目级配置，流转不约束
  - infrastructure:状态变更日志表
  - presentation:状态更新与日志查询 API
  - 验收标准:每次状态变更记录操作人和时间

- B1-4 业务统计规则
  - application:实现项目跟踪视图设计/测试统计
  - application:实现“父资产+跟随副本计一次，分支副本独立计数”
  - application:实现无关联资产统计
  - 验收标准:统计结果与需求文档规则一致

## 联调与测试任务

- A/B 联调
  - 模板实例化后可直接进入表格操作 API
  - 需求管理统计可直接读取表格与资产关系
- 测试
  - 单元:版本并发、批处理、跟随分支、统计口径
  - 集成:模板建表 -> 下钻 -> 资产绑定 -> 统计回流
  - HTTP 行为:spreadsheets API、templates API、业务统计 API

## 交付顺序建议

- 第 1 阶段（平台先行）
  - 完成 Workstream A 的 A0 + A1-1/A1-2
- 第 2 阶段（业务模板接入）
  - 完成 Workstream B 的 B0 + B1-1/B1-2
- 第 3 阶段（收敛）
  - 完成 B1-3/B1-4、联调测试与缺陷修复