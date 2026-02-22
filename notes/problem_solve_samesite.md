## 标题
开发环境中发现的 SameSite 导致的 Cookie/鉴权问题 — 诊断与解决步骤

### 简介
记录一次在本项目开发过程中出现的：浏览器在前端发起的请求中未携带用于会话的 cookie，导致后端接口返回 `Not authorized` 的问题。该文档包含发现过程、根本原因分析、临时修复和长期建议以及复现/验证步骤。

### 发现过程（证据）
- 后端使用基于 cookie 的 JWT 会话（见 `backend/src/app/presentation/http/auth/asgi_middleware.py`）。
- 前端 axios 已配置 `withCredentials: true`（见 `frontend/src/api/client.ts`）。
- 本地配置允许 CORS 凭据（`backend/config/local/config.toml` 中 `ALLOW_CREDENTIALS = true`）。
- 在浏览器中手动操作时：登录可以（通过某些 GET 型请求），但 `create user` POST 请求返回 `Not authorized`。

### 根本原因分析
- 浏览器的 SameSite 策略会影响跨站点请求是否携带 cookie。默认或 Lax 策略会阻止某些跨站点 POST/XHR 请求携带 cookie。
- 即使后端允许凭据并且前端开启 `withCredentials`，浏览器仍会根据 cookie 的 SameSite/secure 属性决定是否发送。开发环境中 cookie 未被显式配置为跨站点允许（也未在安全的 HTTPS 环境下使用 `SameSite=None; Secure`），因此在跨域请求时 cookie 没被发送，后端无法识别会话。

### 临时解决（开发时）
1. 在前端 dev server（Vite）中添加代理，把 `/api` 转发到后端（例如 `http://127.0.0.1:8000`），使浏览器认为请求为同源，从而正常发送 cookie。已在 `frontend/vite.config.ts` 中添加该 proxy。此为开发环境最简单可靠的方式。

### 长期/生产环境建议
- 若确实需要跨站点 cookie（前端与 API 在不同域）：
  - 强制使用 HTTPS，并将 cookie 设置为 `SameSite=None; Secure`。
  - 在后端配置中将 `SECURE=true`，并确保 cookie 写入逻辑（ASGI 中间件）包含 `samesite=None`（或按需求配置）。
  - CORS 端点必须允许凭据：`Access-Control-Allow-Credentials: true`，且前端要使用 `withCredentials`。
- 或者将前端与后端部署到同一域（或通过反向代理），避免跨站点问题。

### 复现与验证步骤
1. 启动后端（`uvicorn` 或项目的启动脚本）。
2. 在 `frontend` 目录启动 Vite（或 `pnpm dev` / `npm run dev`），确保 `vite.config.ts` 中有 `/api` → `http://127.0.0.1:8000` 的 proxy。 
3. 在浏览器访问前端（默认 `http://127.0.0.1:5173`），先执行登录，再执行 `create user`。若代理生效且 cookie 正常，同样的请求不再报 `Not authorized`。

### 相关文件
- `frontend/vite.config.ts` （添加 dev proxy）
- `frontend/src/api/client.ts` （axios withCredentials）
- `backend/src/app/presentation/http/auth/asgi_middleware.py` （cookie 写入/删除逻辑）
- `backend/config/local/config.toml` （CORS 与 cookie SECURE 配置）

### 注意事项
- 不要在生产环境下简单地将 cookie 设置为 `SameSite=None` 而不使用 HTTPS；否则会带来安全风险。
- 为了兼容浏览器行为，开发时使用代理能避免很多跨站点测试问题，但最终部署必须按安全规范配置 cookie 与 TLS。

----
已记录：若需要我把文档移动到 `notes/` 目录或同步到项目文档中（如 README），我可以继续。 
