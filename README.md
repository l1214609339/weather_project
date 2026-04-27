# 天气数据自动采集与预警系统

手动查天气效率不高，而且不能及时知道异常情况。写了一个自动脚本，定时抓取天气数据，处理后存到 MySQL 和 Excel，并通过钉钉机器人推送任务状态和告警。

## 主要功能
- 定时获取实时天气（温度、湿度、风速、降雨等）
- 数据存储到 MySQL（唯一索引防重）和 Excel
- 自动轮换代理 IP，请求失败自动重试（最多3次）
- 任务开始、成功、失败均通过钉钉机器人推送通知

## 依赖
- Python 3
- requests（API 调用、代理 IP）
- pandas（数据清洗：去重、时间拆分、类型转换）
- pymysql（数据库操作）
- 钉钉机器人（加签认证）

## 使用步骤

### 1. 克隆仓库
```bash
git clone https://github.com/l1214609339/weather_project.git
cd weather_project
2. 安装依赖
bash
pip install requests pandas pymysql
3. 配置文件
在项目根目录创建 config.json，按以下模板填写（替换方括号内容）：

json
{
    "api_key": "[你的天气API密钥]",
    "location_id": "[城市ID]",
    "api_host": "[API域名]",
    "db_host": "localhost",
    "db_port": 3306,
    "db_user": "[数据库用户名]",
    "db_password": "[数据库密码]",
    "db_name": "[数据库名]",
    "excel_path": "[Excel保存路径]",
    "link": "[代理IP获取接口]",
    "webhook": "[钉钉机器人webhook]",
    "access_token": "[可选]"
}
4. 运行
bash
python weather.py
脚本执行后，钉钉群会收到开始、成功（含温度和时间）、失败等消息。

技术点说明
代理 IP 池：每次请求前动态获取代理 IP，配合重试机制，降低被限频风险。

数据清洗：pandas 处理空值、重复记录、时间字段拆分、类型转换。

防重设计：MySQL 唯一索引，避免相同时间点的数据重复插入。

钉钉加签：使用 HMAC-SHA256 签名，提高接口安全性。

配置分离：敏感信息存放在 config.json，已加入 .gitignore 避免泄露。

后续计划
加入定时任务，实现完全无人值守

增加多城市监控

根据温度高低（超过35℃或低于0℃）推送紧急告警

遇到大雨或大风时也做相应提醒

项目地址
https://github.com/l1214609339/weather_project
