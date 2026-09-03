# funapp

基于 [nicegui](https://nicegui.io/) 的小型 Web 应用：内置登录页面、游戏/活动数据模型（SQLAlchemy）
以及若干便捷的本地工作入口（如一键打开商品详情页）。

## 安装

```bash
pip install funapp
```

## 快速开始

启动 nicegui 服务：

```python
from funapp.server.core import run

run()
```

服务启动后，可通过 `GET /status.taobao` 做健康检查，返回 `success` 表示存活。

数据模型定义在 `funapp.schema`，使用前需通过 `funsecret` 配置数据库连接串
（`funapp` / `mysql` / `url`），未配置时回落到本地开发默认值：

```python
from funapp.schema import User, create_tables

create_tables()
```

## 关于 farfarfun

[farfarfun](https://github.com/farfarfun) 是一个专注于实用工具库的开源组织，
涵盖云存储、数据处理、AI、多媒体与开发工具链等方向。

- 🏠 组织主页：<https://github.com/farfarfun>
- 📦 PyPI：<https://pypi.org/user/niuliangtao/>
- 📧 联系：farfarfun@qq.com

本项目基于 [MIT](LICENSE) 协议开源。
