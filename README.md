# 项目框架功能

## 功能列表

### 1. 项目启动
- [ ] CLI运行生成自动化测试项目目录
- [ ] 用户登录
- [ ] 用户角色管理
- [ ] 接口单元测试类karate使用体验
### 2. 组件封装
- [ ] request封装
    - [ ] ......
- [x] database操作封装
    - [x] 执行sql file 
    - [x] 执行带参sql file
- [ ] logging封装
    - [ ] requests发送后logging记录实际请求，实际返回
    - [ ] dboperation执行sql后，记录实际sql statement
- [ ] reqscriptobject封装
    - [x] 读取抓包生成的.py脚本,增删改查params payload headers等元素
    - [ ] reqscripts目录放config.ini文件,批量设置接口auth信息
### 3. ......
- [ ] ......
- [ ] ......
- [ ] ......

### 4. 平台化
- [ ] 类Cucumber Studio的平台化管理
    - [ ] 增加DSL名词提示


## 使用方法
### Request Script Object模式
#### 已抓取的requests脚本存放目录如下
```shell
project/
├── test_dir/
│   ├── __init__.py
│   └── login.py
│   └── logout.py
└── main.py
```
#### main中加载
```python
from tuner.rsloader import ReqScriptObject, load_api_objects
# 加载所有requests脚本
# 生成ReqScriptObject实例
# 以api_objects[{{filename}}]访问
api_objects = load_api_objects('./test_dir')
login = api_objects['login']
# 当要用不一样的username登录时
responses = login.update(params={'username':'new_username'})
# responses内容为以new_username登录,password与原脚本中参数一致
assert responses.json()['status'] == 200
```