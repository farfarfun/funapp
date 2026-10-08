# funapp

基于 [nicegui](https://nicegui.io/) 的小型 Web 应用，提供健康检查、游戏/活动数据模型（SQLAlchemy）
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

服务启动后监听 `5678` 端口，提供两个 HTTP 入口：

| 入口 | 说明 |
| --- | --- |
| `GET /status.taobao` | 健康检查，返回 `success` 表示存活 |
| `GET /work/item?item_id=<id>` | 在本机用喵街 App 打开指定商品详情页（依赖 macOS 的 `open`） |

`funapp.ui.login` 只是登录页的静态布局原型：按钮和链接都没有绑定回调，`run()`
也不会挂载它，可用的登录流程仍待实现。

数据模型定义在 `funapp.schema`，使用前需通过 `funsecret` 配置数据库连接串
（`funapp` / `mysql` / `url`）。未配置时使用不含凭据的本地
`sqlite:///funapp.db` 数据库：

```python
from funapp.schema import User, create_tables

create_tables()
```

## 服务启停

长期运行的 nicegui 服务统一通过 `scripts/setup.sh` 启停：

```bash
scripts/setup.sh install-dev           # 构建并安装当前源码
scripts/setup.sh install-prod [版本]   # 从正式源安装最新或指定版本
scripts/setup.sh run                   # 前台运行已安装版本
scripts/setup.sh start                 # 后台运行已安装版本
scripts/setup.sh status                # 查看运行状态和已安装版本
scripts/setup.sh stop                  # 停止
scripts/setup.sh restart               # 重启
scripts/setup.sh publish               # 通过 funbuild 发布正式包
```

PID 与日志统一放在 `.run/`。安装阶段决定使用本地开发包还是正式包；运行命令不接受
`dev` / `prod` 参数，只调用当前环境中已安装的 `funapp` CLI，不会回退到仓库源码。

---

## 关于 farfarfun

[farfarfun](https://github.com/farfarfun) 是一个专注于实用工具库的开源组织，
涵盖云存储、数据处理、AI、多媒体与开发工具链等方向。

- 🏠 组织主页：<https://github.com/farfarfun>
- 📦 PyPI：<https://pypi.org/user/niuliangtao/>
- 📧 联系：farfarfun@qq.com

本项目基于 [MIT](LICENSE) 协议开源。
