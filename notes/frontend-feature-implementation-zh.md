---
name: frontend-feature-implementation（前端功能实现）
description: 将后端 openapi.json 的端点翻译为 TypeScript 类型、API 客户端、MSW mock 处理器、React Query 钩子、Zustand 商店和页面组件的端到端工作流指南。
---

# 前端功能实现（中文翻译）

## 概述

将后端 API 端点（定义在 `docs/openapi.json`）翻译为具有 MSW mock 支持的完整前端功能，遵循用户管理和认证流程中既定的约定。

## 技术栈

- React 19 + Vite 7 + TypeScript（strict）
- TanStack Router（基于文件） + TanStack Query + TanStack Table
- Zustand 用于认证状态，React Query 用于服务端状态
- axios 与共享客户端（`src/api/client.ts`）
- shadcn/ui（Radix UI） + Tailwind CSS 4
- MSW 2（浏览器 service worker）用于 mock 模式
- openapi-typescript 用于类型生成

## 工作流程

### 步骤 0：从 openapi.json 生成 TypeScript 类型

在 `frontend/` 下运行：

```bash
npx openapi-typescript ../docs/openapi.json -o src/api/generated/schema.d.ts
```

这会生成 `components['schemas']` 类型，所有端点文件都从中导入。在 `openapi.json` 更改后需重新生成。

### 步骤 1：定义 API 端点函数

在 `src/api/endpoints/` 中创建或更新文件。每个文件按相关端点分组。

模板：

```typescript
import { apiClient } from '../client'
import { type components } from '../generated/schema'

// ---- 从 openapi schema 推导的类型 ----
export type MyRequest = components['schemas']['MyRequest']
export type MyResponse = components['schemas']['MyResponse']

// ---- API 函数 ----
export async function myEndpoint(data: MyRequest): Promise<MyResponse> {
  const res = await apiClient.post<MyResponse>('/api/v1/...', data)
  return res.data
}
```

约定：
- 在文件顶部从 `components['schemas']` 导出类型别名。
- 返回 `res.data`（解包 axios 响应）。
- 对于 204 No Content 的端点，返回类型使用 `void`。
- 始终使用 `apiClient`（位于 `src/api/client.ts`）作为唯一 HTTP 层；不要直接导入 axios。

参考：`src/api/endpoints/account.ts`, `src/api/endpoints/users.ts`。

### 步骤 2：编写 MSW mock handler

在 `src/mocks/handlers/` 中创建 handler 文件，每个文件对应一个端点文件。

模板：

```typescript
import { http, HttpResponse } from 'msw'
import { BASE_URL } from '../config'
import { db } from '../data/db'

export const myHandlers = [
  http.get(`${BASE_URL}/api/v1/...`, ({ cookies }) => {
    if (!cookies.access_token) {
      return HttpResponse.json({ error: 'Not authenticated.' }, { status: 401 })
    }
    // ... 对内存 db 的业务逻辑
    return HttpResponse.json(responseData, { status: 200 })
  }),
]
```

约定：
- 路径前缀必须使用 `${BASE_URL}`（来自 `src/mocks/config.ts`）。MSW 匹配 axios 发出的绝对 URL，而非相对路径。
- MSW 的 service worker 响应无法通过 `Set-Cookie` 设置 `document.cookie`。对于认证流程，当 `VITE_ENABLE_MSW === 'true'` 时，前端钩子必须手动调用 `setCookie()`。
- 在 `src/mocks/handlers/index.ts` 中注册新的 handler 数组。
- `src/mocks/data/db.ts` 中的种子数据应匹配 feature 文件中的 Given 条件。
- 认证守卫模式：同时检查 `cookies.access_token && db.getCurrentUser()`，以应对前端重启导致的内存 db 重置但浏览器 cookie 仍然存在的情况。

参考：`src/mocks/handlers/account.ts`, `src/mocks/handlers/users.ts`, `src/mocks/data/db.ts`。

### 步骤 3：创建 React Query 钩子

将钩子放在 `src/features/<domain>/api/` 下。

Query 钩子示例：

```typescript
import { useQuery } from '@tanstack/react-query'
import { myEndpoint, type MyParams } from '@/api/endpoints/my'

export const MY_QUERY_KEY = 'my-resource'

export function useMyResource(params?: MyParams) {
  return useQuery({
    queryKey: [MY_QUERY_KEY, params],
    queryFn: () => myEndpoint(params),
  })
}
```

Mutation 钩子示例：

```typescript
import { useMutation, useQueryClient } from '@tanstack/react-query'
import { toast } from 'sonner'
import { createResource, type CreateRequest } from '@/api/endpoints/my'
import { MY_QUERY_KEY } from './use-my-resource'

export function useCreateResource() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: (data: CreateRequest) => createResource(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: [MY_QUERY_KEY] })
      toast.success('Resource created.')
    },
  })
}
```

约定：
- 导出查询键常量以便缓存失效使用。
- Mutation 在 `onSuccess` 中失效相关查询键。
- 使用 `sonner` 的 `toast` 做成功/错误提示。

### 步骤 4：更新 Zustand store（如需）

认证状态位于 `src/stores/auth-store.ts`。仅在与认证相关的功能中修改。

对于服务端状态（列表、CRUD），优先使用 React Query，不要在 Zustand 中重复保存。

### 步骤 5：构建页面与功能组件

- 路由位于 `src/routes/`（TanStack Router 文件路由）。
- 功能组件位于 `src/features/<domain>/components/`。
- 表格列等数据模式位于 `src/features/<domain>/data/`。

受保护的路由嵌套在 `src/routes/_authenticated/` 下。`_authenticated/route.tsx` 中的路由守卫会检查 `access_token` cookie 并通过调用 `getMe()` 来 hydrate 认证 store。

约定：
- 使用 `src/components/ui/` 中的 shadcn/ui 组件。
- 使用 `useListX` 钩子进行数据获取并处理 loading/error 状态。
- 使用 `useMutationX` 处理表单提交。
- 遵循现有对话框模式：provider 上下文 + 对话框组件。

### 步骤 6：验证

1. TypeScript 检查：`npx tsc --noEmit`
2. 生产构建：`npx vite build`
3. Mock 模式：`pnpm dev:mock` — 使用 MSW 验证完整流程
4. API 模式：`pnpm dev:api` — 与真实后端验证

## MSW / 真后端 切换

| 模式 | 命令 | 环境文件 | `VITE_ENABLE_MSW` |
|------|------|----------|------------------|
| Mock | `pnpm dev:mock` | `.env.mock` | `true` |
| 真 API | `pnpm dev:api` | `.env.api` | `false` |
| 默认开发 | `pnpm dev` | `.env.development` | `true` |

MSW 在 `src/main.tsx` 中通过 `enableMocking()` 条件启动。

## 关键注意事项

- **MSW URL 匹配**：axios 发送绝对 URL（例如 `http://localhost:8000/api/v1/...`）。handler 必须使用 `${BASE_URL}/api/v1/...`，而非相对路径 `/api/v1/...`。
- **MSW 无法设置 Cookie**：Service Worker 拦截的响应不会写入 `document.cookie`。当使用 mock 时，钩子需要手动调用 `setCookie()`/`removeCookie()`。
- **跨重启的陈旧 cookie**：浏览器 cookie 会持久化，但 MSW 的内存 db 会重置。认证守卫应同时检查 cookie 和 db 状态。
- **mock 中的 204 vs 200**：若真实后端返回 204（无内容），mock 也应返回 204。如果前端需要响应体数据，请新增单独的查询端点（例如 `GET /me`），而不是在 mock 中改变返回体。
- **类型生成**：在 `openapi.json` 更改后务必重新生成 `schema.d.ts`，不要手动编辑生成的类型。

## 目录结构参考

```
src/
├── api/
│   ├── client.ts                     # 共享 axios 实例
│   ├── generated/schema.d.ts         # 从 openapi.json 自动生成
│   └── endpoints/                    # API 函数文件
│       ├── account.ts
│       └── users.ts
├── mocks/
│   ├── browser.ts                    # setupWorker
│   ├── config.ts                     # handler 路径的 BASE_URL
│   ├── data/db.ts                    # 内存 mock DB + 种子数据
│   └── handlers/                     # MSW handler 文件
│       ├── index.ts                  # handler 注册
│       ├── account.ts
│       └── users.ts
├── features/<domain>/
│   ├── api/                          # React Query 钩子
│   │   ├── use-list-*.ts
│   │   └── use-create-*.ts
│   ├── components/                   # UI 组件
│   └── data/                         # 表格 schema、常量
├── stores/
│   └── auth-store.ts                 # Zustand 认证状态
└── routes/
    ├── _authenticated/               # 受保护路由
    │   └── route.tsx                 # 认证守卫 + getMe() hydrate
    └── (auth)/                       # 公开认证页面
        ├── sign-in.tsx
        └── sign-up.tsx
```

## 输出清单

- [ ] `schema.d.ts` 已从最新 `openapi.json` 生成
- [ ] 在 `src/api/endpoints/` 中新增或更新端点函数并使用正确类型
- [ ] 在 `src/mocks/handlers/` 中添加 MSW handlers，并使用 `BASE_URL` 前缀
- [ ] 在 `src/mocks/data/db.ts` 中准备与 feature 文件相符的种子数据
- [ ] 在 `src/mocks/handlers/index.ts` 中注册 handler
- [ ] 在 `src/features/<domain>/api/` 中添加 React Query 钩子
- [ ] 页面组件使用钩子并处理 loading/error 状态
- [ ] 通过 `npx tsc --noEmit`
- [ ] `vite build` 构建通过
- [ ] `pnpm dev:mock` 的 mock 流程端到端可用
