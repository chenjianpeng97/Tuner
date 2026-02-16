# git-setup

## 目标

- 前后端均从某个开源template开始，进行二次开发
- backend和frontend两个仓库可以分别获取开源模板的更新

## 操作方法

1. GitHub上分别fork前后端开源模板
2. git 配置submodule

```bash
git submodule add <YOUR_BACKEND_FORK_URL> backend
git submodule add <YOUR_FRONTEND_FORK_URL> frontend
git submodule status
# 初始化
git submodule update --init --recursive
# 拉取上游更新
git submodule update --remote --merge
# 子模块配置upstream
cd backend
git remote add upstream <ORIGINAL_BACKEND_URL>
git remote -v
cd ../frontend
git remote add upstream <ORIGINAL_FRONTEND_URL>
git remote -v
cd ..
# 以后更新三方上游代码流程
cd backend
git fetch upstream
git checkout main
git merge upstream/main
git push origin main
cd ../frontend
git fetch upstream
git checkout main
git merge upstream/main
git push origin main
cd ..
```
