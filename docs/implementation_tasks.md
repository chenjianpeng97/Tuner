# 项目管理功能开发任务清单（MVP）

## 使用说明

- 目标:将 docs/requirements.md 转换为可直接排期与开发的任务清单
- 范围:MVP，仅覆盖项目跟踪视图、产品需求视图、需求资产、状态与标签、统计回流
- 任务组织方式:按迭代分组，每个任务按 domain/application/infrastructure/presentation 拆分

## 迭代 0：基础模型与配置能力

- T0-1 项目级配置模型（需求层级、状态标签、资产标签）
  - domain
    - 定义 ProjectSetting 聚合
    - 定义 RequirementLevelConfig（默认 L1/L2/L3，可扩展至 L9）
    - 定义 StatusLabelConfig（可配置、无流转约束）
    - 定义 AssetTagConfig（标签可复用）
  - application
    - 实现创建/更新/查询项目配置用例
  - infrastructure
    - 新增项目配置表与读写仓储
  - presentation
    - 提供项目配置 API（读/写）
  - 验收标准
    - 可在项目级保存层级名称并扩展到 L9
    - 可保存任意状态标签与资产标签

- T0-2 客户需求实体扩展（统一需求/事项）
  - domain
    - CustomerRequirement 增加 labels、status、schedule、audit 字段
    - 定义“研发需求”标签判定规则
  - application
    - 实现客户需求创建/更新/打标签/改状态用例
  - infrastructure
    - 扩展 customer_requirements 表字段
  - presentation
    - 提供客户需求录入与标签/状态更新 API
  - 验收标准
    - 同一实体可标记为研发需求或事项
    - 非研发事项不可进入产品需求拆解入口

## 迭代 1：产品需求下钻与多对多关联

- T1-1 产品需求层级化建模
  - domain
    - 定义 ProductRequirement（支持 L1-L9 动态层级值）
    - 定义 ModulePath（模块/子模块）
  - application
    - 实现产品需求创建/更新/查询用例
  - infrastructure
    - 新增 product_requirements、requirement_modules 表
  - presentation
    - 提供产品需求 CRUD API
  - 验收标准
    - 可按项目层级配置录入并查询 L1-L9 内容

- T1-2 客户需求-产品需求多对多关联
  - domain
    - 定义 TraceLink 关联实体与约束
  - application
    - 实现手动关联/取消关联
    - 实现下钻上下文创建产品需求自动建联
  - infrastructure
    - 新增 trace_links 关联表（多对多）
  - presentation
    - 提供关联管理 API
  - 验收标准
    - 一个客户需求可关联多个产品需求
    - 一个产品需求可关联多个客户需求
    - 下钻新建产品需求后自动建立关联

- T1-3 下钻视图查询
  - application
    - 实现按 customer_requirement_id 过滤的产品需求查询
  - presentation
    - 提供下钻查询 API（仅返回当前客户需求关联数据）
  - 验收标准
    - 点击客户需求下钻仅返回相关产品需求

## 迭代 2：资产管理（预上传、复制跟随、统计口径）

- T2-1 资产基础能力
  - domain
    - 定义 Asset（必须归属 project_id）
    - 支持可选关联 customer_requirement_id、product_requirement_id
  - application
    - 实现资产创建/编辑/删除/查询
    - 实现预上传资产（先无需求关联）
  - infrastructure
    - 新增 assets 表与基础索引
  - presentation
    - 提供资产管理 API
  - 验收标准
    - 资产可在项目内先上传，后补关联
    - 不允许无 project_id 资产写入

- T2-2 资产标签与多标签
  - domain
    - 定义 AssetTag 关系（多对多）
  - application
    - 实现资产打多标签与按标签筛选
  - infrastructure
    - 新增 asset_tags、asset_tag_links 表
  - presentation
    - 提供标签绑定/解绑与筛选 API
  - 验收标准
    - 单个资产可绑定多个标签
    - 可按标签统计设计/测试资产

- T2-3 资产复制与跟随
  - domain
    - 定义父子资产关系（parent_asset_id）
    - 定义跟随策略 follow_mode（follow / detached）
  - application
    - 实现复制资产到其他产品需求
    - 实现父资产变更后的副本同步选择逻辑
  - infrastructure
    - 扩展 assets 表字段（parent_asset_id、follow_mode、branch_version）
  - presentation
    - 提供复制与跟随策略 API
  - 验收标准
    - 可复制资产并选择是否跟随父级
    - 脱离跟随后形成独立分支

- T2-4 统计引擎（含去重与分支计数）
  - application
    - 实现客户需求维度统计：设计总数、测试总数、无关联资产总数
    - 实现计数规则：同一父资产+跟随副本计一次，脱离分支独立计数
  - infrastructure
    - 增加统计查询仓储与必要索引
  - presentation
    - 提供项目跟踪视图统计 API
  - 验收标准
    - 项目跟踪视图设计/测试列数值与规则一致
    - 无需求关联资产可独立展示

## 迭代 3：项目跟踪视图与状态审计

- T3-1 项目跟踪视图聚合查询
  - application
    - 聚合客户需求、排期、状态、设计数、测试数
  - presentation
    - 提供 tracking-view API（分页、筛选、排序）
  - 验收标准
    - 默认返回“需求、设计、测试”列
    - 支持扩展排期列展示

- T3-2 状态更新与审计
  - domain
    - 定义状态变更事件（不限制流转路径）
  - application
    - 实现状态更新并记录操作人、时间
  - infrastructure
    - 新增 status_change_logs 表
  - presentation
    - 提供状态更新 API 与日志查询 API
  - 验收标准
    - 任意状态间可切换
    - 每次变更均可追溯操作人和时间

## 测试任务（并行执行）

- 单元测试
  - 层级配置（L1-L9）校验
  - 多对多关联约束与自动建联
  - 资产复制/跟随/脱离分支规则
  - 统计去重与分支计数规则

- 集成测试
  - 客户需求下钻 -> 产品需求查询链路
  - 预上传资产 -> 补关联 -> 统计回流链路
  - 状态更新 -> 审计日志链路

- HTTP 行为测试
  - 项目配置 API
  - 跟踪视图 API
  - 资产复制跟随 API

## 交付顺序建议

- 第 1 周
  - 完成迭代 0 + 迭代 1（先打通下钻和关联主链路）
- 第 2 周
  - 完成迭代 2（资产标签、复制跟随、统计规则）
- 第 3 周
  - 完成迭代 3 + 回归测试 + 缺陷修复

## 风险与前置决策

- 统计性能风险
  - 风险:客户需求、产品需求、资产多表聚合后查询变慢
  - 应对:优先增加组合索引，必要时引入增量统计表

- 复制跟随一致性风险
  - 风险:父资产频繁更新导致副本同步冲突
  - 应对:同步动作记录版本号，冲突时提供手动确认策略

- 标签治理风险
  - 风险:项目标签膨胀导致筛选混乱
  - 应对:项目级标签配置支持停用与归档