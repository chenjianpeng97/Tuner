---

**名称**：infrastructure-layer-implementation (基础设施层实现)

**描述**：在此仓库中实现基础设施适配器和服务。用于将端口与具体实现（数据库、身份验证、哈希计算、I/O）进行挂载，映射持久化模型，并添加基础设施异常或处理器，同时保持核心层不受影响。

---

# 基础设施层实现

## 概述

为应用层和领域层的端口（Ports）构建具体的适配器（Adapters），处理集成细节，并确保基础设施代码与核心逻辑隔离。

## 工作流

1.  **从应用层或领域层识别所需的端口**
    - 命令侧（Command side）使用数据映射器（Data Mappers）和刷新器（Flusher）；查询侧（Query side）使用读取器（Readers）。
    - 身份认证（Auth）使用访问撤销器（Access Revokers）和身份提供者（Identity Providers）。

2.  **实现适配器**
    - 在 `app/infrastructure/adapters` 下添加持久化和 I/O 适配器。
    - 在 `app/infrastructure/auth/adapters` 下添加认证相关的适配器。
    - 确保每个适配器都实现了 `application/common/ports` 或 `domain/ports` 中定义的特定端口接口。

3.  **将存储模型映射为领域类型**
    - 将 SQLAlchemy 或外部 SDK 的特定细节保留在基础设施层内部。
    - 在将数据返回给应用层之前，将原始数据转换为领域值对象和实体。

4.  **定义基础设施异常**
    - 使用基础设施异常来表示集成失败（例如：数据库不可用、哈希计算器繁忙）。
    - 仅在数据库约束强制执行的是领域规则时，才重新抛出（Re-raise）领域特定的错误。

5.  **在 IoC 中注册适配器**
    - 在 `setup/ioc/application.py` 或 `setup/ioc/domain.py` 中将适配器绑定到对应的端口。

## 准则 (Guardrails)

- **禁止反向导入**：严禁在应用层或领域层中导入基础设施层代码。
- **依赖隔离**：将外部 SDK、SQLAlchemy 模型和 FastAPI 依赖保留在此层。
- **数据解耦**：确保适配器返回的是领域类型或查询模型，**而不是** ORM 实体（如 SQLAlchemy 的 Model 实例）。
- **副作用控制**：确保副作用（Side Effects）仅局限于适配器的方法内部。

## 审查清单

- 所有定义的端口是否在基础设施层中都有具体的实现？
- 适配器是否在边界处进行了数据转换并隐藏了实现细节？
- 异常是否进行了明确的分层（基础设施级 vs 领域级），并由表现层控制器负责映射？
- IoC Provider 是否已更新以完成端口与适配器的绑定？
