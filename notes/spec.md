# 项目VibeCoding SPEC


1. HUMAN:写出原始需求

2. SKILLS(to_be_imple):问问题澄清需求

3. HUMAN:配合澄清需求

4. SKILLS(to_be_imple):根据澄清后的需求，生成符合规范的 Gherkin 文件内容，并明确建议的文件保存路径。

5. SKILLS(to_be_imple):根据需求先勾勒出http接口，暂不实现接口逻辑

6. SKILLS(to_be_imple):实现behave --stage http的步骤定义，验证接口编排逻辑

6. SKILLS(to_be_imple):用skillS导出openapi.json接口文档

7. SKILLS(to_be_imple):前端通过json文档生成模型文件Orval生成schema文件，供前端调用

8. SKILLS(to_be_imple):前端根据接口文档和schemea文件用MSW生成mock组件

9. SKILL(to_be_imple):前端根据接口文档和schema实现前端功能

10. SKILL(to_be_imple):前端启用MSW mock服务，在feature下实现behave --stage ui 实现前端测试自动化

11. SKILL(to_be_imple):后端用TDD方法补全domain,application, infrastructure层实现接口逻辑，直到单元测试通过

12. SKILL(to_be_imple):同时启动前后端,前端连接后端接口，执行behave --stage ui完成测试