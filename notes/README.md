---
description: 本项目笔记将记录在Tuner项目中对react和python clean architecture的理解和实践，与一些环境搭建和工具使用相关记录
---

# Tuner项目笔记

## 整体工作流
- 用户写需求到requirements.md中
- 

## AI工作流

**AI提交git**:应在每次确认文件变更操作后，使用git commit 记录变更内容，commit应遵循 conventional commits

**解决问题**:1.有时候一个session未被确认vsc异常一些写好的代码会被回退,git commit保证记录这些变更 2.记录变更说明，以供追溯

## uv配置

**背景**:在Tuner项目中，使用uv作为python环境管理工具，来管理项目的依赖和虚拟环境；遇到的第一个问题是，因为feature文件作为需求文档的一部分，逻辑上应放在工作区的根目录下，但backend下又有自己独立的pyproject.toml文件，所以需要在uv中配置workspace来管理根目录和backend目录的依赖

**细节**:
## git

### git配置

**背景**:因决定将项目放在一个repo中管理，且 frontend 和 backend 使用开源项目的 template repo 基础上进行开发，所以需要在git中配置submodule来管理frontend和backend的代码

**笔记**:[git submodule 操作步骤](./git_setup.md)


### AI agent git 工作流

- 新增功能时使用新的分支(feature/,fix/等)，当单元测试，集成测试，端到端验收测试通过后再merge到main上

## BDD

**背景**:在Tuner项目中，加入BDD的工程实践,使用Behave框架将requiremens转换为feature文件

### 细节

### feature file 编写

- feature 文件的结构参考cucumberstudio的导出结构,即顶层feature如果需要有subfolder的话,则feature同级加一个与.feature文件同名文件夹，将子场景写在subfolder中，文件结构示例

```bash

-features/
-user.feature
-user/
-user_auth.feature
-user_ui.feature

```

### stage=http的测试实现细节

- step 实现使用behave的stage参数,来实现不同层的测试实现，如behave --stage ui来实现UI层测试,behave --stage http 来实现fastapi接口层测试，behave --stage domain 来实现领域层测试
- **stage = http的测试实现细节**
- **env**使用fastapi TestClient来模拟http请求，测试接口层的实现
- **env**使用 mock 来模拟 fastapi app 启动需要的依赖，用，dishka 进行依赖注入生成testapp
- **env**mock掉所有接口直接依赖@inject的函数
- **given**将前置条件放入context中，供后面步骤使用
- **when**使用 mock.return_value 和 mock.side_effect 来模拟不同的接口函数的返回结果
- **when**用 fastapi TestClient 引用presentation层的RequestPydantic模型来构造接口请求，
- **then**断言接口返回值和code,对应fastapi errormap的定义
example:

```python
from http import HTTPStatus
# given设置前置条件
@given('an existing user with username "{username}"')
def given_existing_user(context, username):
"""Record that *username* already exists (for duplicate-check scenarios)."""
context.users[username] = {"id": str(uuid.uuid4()), "is_active": True}
context.current_username = username
# when中mock接口
@when('an actor creates a user with username "{username}"')
def when_actor_creates_user(context, username):
"""`POST /api/v1/users/` — admin endpoint.

If *username* was recorded in a Given step the mock raises
``UsernameAlreadyExistsError`` which the controller's error_map
translates to **409 Conflict**.
"""
mocks = context.mocks
# mock接口@inject处理方法
if username in context.users:
mocks.create_user.execute.side_effect = UsernameAlreadyExistsError(
    username,
)
else:
mocks.create_user.execute.return_value = CreateUserResponse(
    id=uuid.uuid4(),
)
# 引用RequestPydantic模型构造接口请求
request_body = CreateUserRequestPydantic(
username=username,
password="testpass1",
role=UserRole.USER,
)
# 使用fastapi TestClient模拟接口请求，并将response保存在context中供后续步骤使用
context.response = context.client.post(
API_USERS,
json=request_body.model_dump(mode="json"),
cookies=AUTH_COOKIES,
)
context.current_username = username
@then('the request is rejected with a "user already exists" error')
def then_request_rejected_duplicate(context):
"""``UsernameAlreadyExistsError`` → **409** (create_user error_map)."""
# 这里引用http.HTTPStatus来断言接口返回状态码
assert context.response.status_code == STATUS_CONFLICT, (
f"Expected {STATUS_CONFLICT}, got {context.response.status_code}: "
f"{context.response.text}"
)
body = context.response.json()
assert "already exists" in body.get("error", "").lower(), (
f"Error body missing domain message: {body}"
)
```

## 前端实现工作流

**背景**：前端基于 shadcn-admin 模板搭建（React 19 + Vite + TanStack Router/Query/Table + Zustand + Zod + axios），模板自带 mock 数据和 Clerk 认证。当前端 agent 拿到 `docs/openapi.json` 接口文档和 `features/` 需求文档后，按以下顺序实施：

### 输入物

| 文件                   | 用途                                                                 |
| ---------------------- | -------------------------------------------------------------------- |
| `docs/openapi.json`    | 后端接口契约，定义所有 endpoint、request/response schema、error code |
| `features/*.feature`   | 业务场景与验收条件，指导页面行为与边界 case                          |
| `docs/requirements.md` | 原始需求描述                                                         |

### Step 0: 从 openapi.json 生成 TypeScript 类型

- 使用 `openapi-typescript` 从 `docs/openapi.json` 生成类型文件
- 生成产物放在 `src/api/generated/schema.d.ts`，作为前后端类型契约的 single source of truth
- 后续所有 API 调用、zod schema、表单类型均从此文件派生，不手写重复类型

```bash
pnpm add -D openapi-typescript
pnpx openapi-typescript ../docs/openapi.json -o src/api/generated/schema.d.ts
```

### Step 1: 搭建 API 基础设施 + Mock Server

由于此阶段后端可能尚未实现（仅完成了 presentation 层定义并导出 openapi.json），前端需要自建 mock 来独立开发调试。

#### 1a. 搭建 API Client

按顺序创建以下文件：

1. **`src/api/client.ts`** — Axios 实例
- `baseURL` 从环境变量读取（`VITE_API_BASE_URL`）
- `withCredentials: true`（后端使用 cookie-based JWT `access_token`，浏览器自动携带，前端不需手动管理 token）
- response interceptor：统一将后端 `SimpleErrorResponseModel.error` 提取为 error message
- 不在 axios 层做 401 跳转（已在 `main.tsx` QueryCache.onError 中处理）

2. **`src/api/endpoints/`** — 按 openapi tag 分文件的 raw API 函数
- `account.ts`：signup / login / logout / changePassword
- `users.ts`：createUser / listUsers / setUserPassword / grantAdmin / revokeAdmin / activateUser / deactivateUser
- `health.ts`：healthCheck
- 每个函数参数和返回值类型从 Step 0 生成的类型中 import

#### 1b. 从 openapi.json 生成 Mock Server（MSW）

使用 [Mock Service Worker (MSW)](https://mswjs.io/) 在浏览器 service worker 层拦截请求，无需修改任何业务代码即可在后端就绪后无缝切换。

**安装与初始化**：

```bash
pnpm add -D msw
pnpx msw init public/ --save   # 将 service worker 脚本写入 public/
```

**文件结构**：

```
src/mocks/
browser.ts          # setupWorker 入口
handlers/
index.ts          # 汇总导出所有 handlers
account.ts        # Account tag 的 mock handlers
users.ts          # Users tag 的 mock handlers
data/
db.ts             # 内存数据库（Map/Array），mock 数据的 single source
fixtures.ts       # 初始 seed 数据，从 feature 文件的 Given 条件派生
```

**编写 handler 的规范**：

1. **从 openapi.json 逐接口编写** — 每个 handler 对应一个 operationId，request/response 类型引用 Step 0 生成的类型
2. **内存数据库** — 用简单的 `Map<string, User>` 等结构模拟持久化，支持 CRUD
3. **覆盖成功与错误路径** — 参照 feature 文件的 Scenario 实现：
- Happy path：正常返回 200/201/204
- 错误 path：username 重复 → 409、用户不存在 → 404、未认证 → 401、权限不足 → 403
- 返回体严格遵循 `SimpleErrorResponseModel` 格式 `{ "error": "..." }`
4. **认证模拟** — mock 的 login handler 在 response 中 set cookie `access_token=mock-jwt`；后续 handler 检查该 cookie 存在即视为已认证；可根据 seed 数据中的 role 模拟权限校验

**示例 handler**（`src/mocks/handlers/users.ts`）：

```typescript
import { http, HttpResponse } from "msw";
import { db } from "../data/db";

export const usersHandlers = [
// POST /api/v1/users/ — Create User
http.post("/api/v1/users/", async ({ request, cookies }) => {
if (!cookies.access_token) {
return HttpResponse.json(
{ error: "Not authenticated." },
{ status: 401 },
);
}
const body = await request.json();
if (db.users.has(body.username)) {
return HttpResponse.json(
{ error: `Username "${body.username}" already exists.` },
{ status: 409 },
);
}
const id = crypto.randomUUID();
db.users.set(body.username, {
id_: id,
username: body.username,
role: body.role ?? "user",
is_active: true,
});
return HttpResponse.json({ id }, { status: 201 });
}),

// GET /api/v1/users/ — List Users
http.get("/api/v1/users/", ({ cookies, request }) => {
if (!cookies.access_token) {
return HttpResponse.json(
{ error: "Not authenticated." },
{ status: 401 },
);
}
const url = new URL(request.url);
const limit = Number(url.searchParams.get("limit") ?? 20);
const offset = Number(url.searchParams.get("offset") ?? 0);
const all = Array.from(db.users.values());
return HttpResponse.json({
users: all.slice(offset, offset + limit),
total: all.length,
});
}),
];
```

**条件启动**（`src/main.tsx`）：

```typescript
async function enableMocking() {
if (import.meta.env.VITE_ENABLE_MSW !== "true") return;
const { worker } = await import("./mocks/browser");
return worker.start({ onUnhandledRequest: "bypass" });
}

enableMocking().then(() => {
// 原有 ReactDOM.createRoot(...) 逻辑
});
```

在 `.env.development` 中设置 `VITE_ENABLE_MSW=true`，后端就绪后改为 `false` 即可无缝切换，**业务代码零改动**。

### Step 2: 替换认证体系（移除 Clerk → 自有 Cookie Auth）

1. **移除 `@clerk/clerk-react` 依赖**及所有 Clerk 相关 import
2. **改造 `src/stores/auth-store.ts`**：
- 移除本地 cookie token 管理逻辑（后端 set-cookie 自动管理 `access_token`）
- 保留 `user` 状态，类型对齐 `UserQueryModel`（id\_, username, role, is_active）
- 添加 `fetchCurrentUser` action（如后端有 /me 接口），或从 login response 解析用户信息
- `reset()` 只清空 zustand 内存状态，不操作 cookie
3. **改造 Auth 页面**（`src/features/auth/`）：
- `sign-in/` → 调用 `POST /api/v1/account/login`，成功后跳转 `redirect` 或 `/`
- `sign-up/` → 调用 `POST /api/v1/account/signup`，成功后引导登录
- 表单 zod schema 对齐 `LogInRequest` / `SignUpRequest`
4. **改造路由守卫**（`src/routes/_authenticated/route.tsx`）：
- `beforeLoad` 中检查 auth 状态，无认证则 redirect 到 `/sign-in`
- 用 `auth.user.role` 做页面级权限控制（admin 路由守卫）

### Step 3: 实现 React Query Hooks

在 `src/features/<feature>/api/` 下按功能创建 hooks：

```
src/features/
auth/
api/
use-login.ts          # useMutation → POST /login
use-signup.ts         # useMutation → POST /signup
use-logout.ts         # useMutation → DELETE /logout
use-change-password.ts # useMutation → PUT /password
users/
api/
use-list-users.ts     # useQuery → GET /users/
use-create-user.ts    # useMutation → POST /users/
use-set-user-password.ts
use-grant-admin.ts
use-revoke-admin.ts
use-activate-user.ts
use-deactivate-user.ts
```

**规范**：

- `useQuery` hooks 暴露 `queryKey` 常量，便于 mutation 后 `invalidateQueries`
- `useMutation` 的 `onSuccess` 中 invalidate 相关 query + toast 成功消息
- `onError` 交由全局 `handleServerError` 处理，特殊 case（如 409 Conflict）在 mutation `onError` 中单独处理并显示业务错误

### Step 4: 按 Feature 改造页面（连接真实数据）

对每个 feature 执行以下子步骤：

#### 4a. 对齐数据模型

- 将模板中的 mock zod schema（如 `features/users/data/schema.ts`）替换为与后端 `UserQueryModel` 一致的定义
- 删除 `features/*/data/` 下的 mock 数据文件

#### 4b. 改造列表/查询页

- 将硬编码 `data={users}` 替换为 React Query hook（如 `useListUsers`）
- 接入服务端分页参数（`limit`, `offset`, `sorting_field`, `sorting_order`）与 TanStack Table 的 pagination/sorting 状态同步
- 处理 loading / error / empty 状态

#### 4c. 改造表单/操作

- 用 react-hook-form + zod 构建表单，schema 与后端 request body 一一对应
- 表单提交调用对应 `useMutation` hook
- 对齐后端 error code 的 UI 反馈：

| 后端 Status             | UI 行为                                     |
| ----------------------- | ------------------------------------------- |
| 400 Bad Request         | toast 错误信息                              |
| 401 Unauthorized        | 全局跳转 /sign-in（已在 QueryCache 中实现） |
| 403 Forbidden           | toast "权限不足"                            |
| 404 Not Found           | toast 或页面提示                            |
| 409 Conflict            | 表单级错误提示（如"用户名已存在"）          |
| 422 Validation Error    | 映射到表单字段级错误                        |
| 503 Service Unavailable | toast "服务暂不可用"                        |

#### 4d. 参照 Feature 文件验收

- 对照 `features/*.feature` 中的 Scenario，逐个检查 UI 是否覆盖：
- 正常路径（happy path）
- 错误路径（duplicate username → 409、deactivated user can't login 等）
- 权限边界（non-admin 看不到管理页面）

### Step 5: 全局收尾与增强

1. **错误处理统一** — 改造 `src/lib/handle-server-error.ts`，从 `error.response.data.error`（对应 `SimpleErrorResponseModel`）提取消息
2. **权限 UI 控制** — 根据 `user.role` 控制：
- 导航菜单的可见性（admin-only 页面对 user 角色隐藏）
- 操作按钮的可见性/禁用状态（如普通 user 不显示"创建用户"按钮）
3. **环境配置** — `.env.development` / `.env.production` 配置 `VITE_API_BASE_URL`
4. **移除模板残留** — 删除不需要的模板 feature（tasks, chats, apps 等无关模块）

### 实施原则

- **类型从 openapi 生成，不手写** — 保证前后端契约一致性
- **MSW mock 与真实 API 零切换** — mock handlers 在 service worker 层拦截，业务代码始终调用真实 endpoint 函数；通过环境变量 `VITE_ENABLE_MSW` 切换，后端就绪后关闭即可，无需改业务代码
- **mock 场景从 feature 文件派生** — seed 数据和错误分支直接参照 `.feature` 的 Given/When/Then，保证 mock 与验收条件一致
- **Cookie auth 浏览器自动管理** — 前端只需 `withCredentials: true`，不存不取 token
- **feature 文件夹结构保持** — 每个业务功能在 `src/features/<name>/` 下自包含（components/api/data/hooks）
- **先通 happy path，再补边界** — 每个 feature 先跑通正常场景，再对照 .feature 文件补全错误处理
- **每完成一个 feature 可独立验收** — 前端按 feature 粒度交付，可独立运行验证

## 后端组件

### dishka

### fastapi errormap

### fastapi

**导出openapi.json**：完成presentation层定义后，可以先导出openapi.json文件，来给前端使用

```sh
mkdir -p ./docs && curl -fSL http://127.0.0.1:8000/openapi.json -o ./docs/openapi.json
```

## WSL环境配置

**加速uv安装**:一般来说用uv安装一些python包会比较慢，采用wsl走win上的clash代理来加速安装[参考](https://www.zhihu.com/question/435906813/answer/3379440145)

```sh
vim ~/.bashrc #bash
# 添加以下内容
alias proxy='export all_proxy=http://[ip地址]:7890'# ip从powershell中运行`ipconfig`命令查看，clash默认端口7890
alias unproxy='unset all_proxy'
# 运行curl 测试
curl www.google.com
```

## TODO LIST

[] 完整开发一个新的功能
[] 开发一个