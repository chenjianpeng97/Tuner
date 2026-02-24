# WSL 网络代理排查记录（npm + Codex CLI）

## 1. 问题现象

- `npm install -g @fission-ai/openspec@latest --registry https://registry.npmmirror.com` 超时（`ETIMEDOUT`）
- 报错显示请求走到了 `172.23.64.1:7890`
- `openspec: command not found`（本质是安装失败导致）
- `codex` 使用时也出现网络连通性问题

## 2. 根因总结

不是 npm 源本身问题，而是 **shell 启动时自动注入了失效代理**：

- `~/.profile` 中存在：
	- `export HTTP_PROXY="http://172.23.64.1:7890"`
	- `export HTTPS_PROXY="http://172.23.64.1:7890"`
- 该地址在当前 WSL 网络环境不可用，导致 npm/codex 请求被强制走坏代理并超时。

另外确认到当前可用代理端点是：`172.20.208.1:7890`。

---

## 3. 标准排查流程（可复用）

### 步骤 A：确认 npm 配置和环境变量

```bash
npm config get proxy
npm config get https-proxy
npm config get registry
env | grep -Ei '^(http|https|all)_proxy=|^no_proxy='
```

判断要点：

- 若 npm `proxy/https-proxy` 为 `null`，但环境变量有 `HTTP_PROXY/HTTPS_PROXY`，说明是 shell 环境在影响。

### 步骤 B：验证“关代理后”镜像可达

```bash
env -u HTTP_PROXY -u HTTPS_PROXY -u ALL_PROXY npm view @fission-ai/openspec version --registry https://registry.npmmirror.com
```

若能返回版本号（如 `1.1.1`），说明镜像和包都正常，问题是代理链路。

### 步骤 C：确认是否真的安装成功

```bash
command -v openspec
npm prefix -g
npm root -g
ls -l ~/.nvm/versions/node/*/bin/openspec
```

也可直接查包暴露的二进制名：

```bash
npm view @fission-ai/openspec bin --registry https://registry.npmmirror.com
# 预期：{ openspec: 'bin/openspec.js' }
```

### 步骤 D：定位 WSL 下可用代理地址

```bash
ip route | grep default
cat /etc/resolv.conf | grep nameserver

for h in 127.0.0.1 172.23.64.1 172.20.208.1 $(awk '/nameserver/{print $2; exit}' /etc/resolv.conf); do
	echo "== $h:7890 =="
	timeout 2 bash -lc "</dev/tcp/$h/7890" >/dev/null 2>&1 && echo OPEN || echo CLOSED
done
```

再测实际转发能力（以 OpenAI API 为例）：

```bash
for h in 127.0.0.1 172.23.64.1 172.20.208.1 $(awk '/nameserver/{print $2; exit}' /etc/resolv.conf); do
	echo "--- via $h ---"
	HTTP_PROXY=http://$h:7890 HTTPS_PROXY=http://$h:7890 curl -I --max-time 8 https://api.openai.com 2>&1 | tail -n 2
done
```

---

## 4. 修复策略（已验证）

### 4.1 原则

- **不要在登录 shell 自动开代理**（避免污染所有命令）
- 改为 **按需开启/关闭代理**

### 4.2 实施内容

1. `~/.profile`

- 移除自动导出：
	- `HTTP_PROXY`
	- `HTTPS_PROXY`
- 保留 `NO_PROXY`

2. `~/.bashrc`

- 新增函数：
	- `proxy_on`：设置 `HTTP_PROXY/HTTPS_PROXY/ALL_PROXY` 及小写同名变量
	- `proxy_off`：全部 `unset`
- 保留兼容别名：
	- `alias proxy='proxy_on'`
	- `alias unproxy='proxy_off'`

当前统一代理地址：`172.20.208.1:7890`

---

## 5. 日常使用建议

### npm 安装国内包（默认关代理）

```bash
proxy_off
npm config set registry https://registry.npmmirror.com
npm config delete proxy
npm config delete https-proxy
npm install -g <package>
```

### Codex CLI（需要外网时开代理）

```bash
proxy_on
codex
```

不用时关闭：

```bash
proxy_off
```

---

## 6. 快速自检清单（1 分钟）

```bash
# 1) 代理变量状态
env | grep -Ei '^(http|https|all)_proxy=' || echo 'no proxy vars'

# 2) codex 是否可执行
command -v codex && codex --version

# 3) openspec 是否可执行
command -v openspec && openspec --version

# 4) 代理开关是否生效
proxy_on
curl -I --max-time 8 https://api.openai.com | head -n 1
proxy_off
```

如果第 4 步失败，优先检查：

- Windows 代理软件是否已启动
- 监听端口是否为 `7890`
- WSL 可达地址是否变化（重跑“步骤 D”）

