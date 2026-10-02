# CHANGELOG

## 1.1.6

### 修复

- `scripts/setup.sh` 的 `stop` / `restart` 分支调用 `do_stop` 时没有传入环境参数，
  在 `set -u` 下直接报 `$1: unbound variable`，`stop dev` / `restart dev` 完全不可用。
- `scripts/setup.sh` 的 prod 校验此前只比对加载路径是否在仓库目录内，`uv sync`
  装的 editable（`.pth` 把源码目录塞回 `sys.path`）能绕过它。现在额外断言
  `funapp.__file__` 落在 `site-packages` 内，并在校验前清掉 `PYTHONPATH`，
  editable 安装与路径注入一律报错退出，不再悄悄跑源码。
- `funapp.schema` 的六个模型主键声明为 `BigInteger` + `autoincrement`，而 SQLite
  只认 `INTEGER PRIMARY KEY` 作为自增列，导致默认的本地 SQLite 连接串一插入就
  报 `NOT NULL constraint failed`。主键改为在 SQLite 上降级成 `INTEGER`，
  MySQL 等其他方言仍按 `BIGINT` 建表。
- `tests/test_smoke.py` 未通过 `ruff format`。

### 变更

- `funapp.server.core.run()` 去掉了从未被使用的 `*args` / `**kwargs`，签名改为
  无参。此前传入的参数会被静默丢弃，不存在依赖它的可用行为。
- `funapp.schema` 未配置 `funsecret` 密钥时的回落连接串，由含占位用户名/密码的
  `mysql+pymysql://username:password@localhost/dbname` 改为不含任何凭据的
  `sqlite:///funapp.db`。旧默认值是无法连通的占位串，不具备可依赖的行为。
- `pyproject.toml` 的 `description` 由占位值 `funapp` 改为据实描述；移除残留的
  空 `[tool.setuptools]`（构建后端是 hatchling）；补充
  `[tool.hatch.build.targets.wheel]`、`[tool.ruff]` 配置与 `ruff` 开发依赖。
- README 改为据实描述：列出 `/status.taobao` 与 `/work/item` 两个实际入口，并
  明确说明 `funapp.ui.login` 只是未接线的静态布局原型。
- `scripts/setup.sh` 启动服务时统一把工作目录切到 `.run/`，`farlog` 生成的相对
  `logs/` 因此落在 `.run/logs/`，不再污染仓库根目录。

### 新增

- `src/funapp/ui/__init__.py`：`funapp.ui` 此前缺 `__init__.py`，只是命名空间包。
- `tests/test_smoke.py` 补齐行为测试：`quick_open_item` 的正常路径/默认值/空白与
  非字符串入参边界、`run()` 的启动参数、HTTP 路由注册、模型在临时 SQLite 上的
  建表/默认值/外键关系/唯一约束、无效连接串的失败路径，以及 `scripts/setup.sh`
  的 dev 前后台生命周期与 prod 的「拒绝源码 / 拒绝 editable / 接受 site-packages
  安装」三条分支。

## 1.1.5

### 修复

- `funapp/schema/__init__.py` 此前导入 `.user`/`.theme`/`.game`/`.campaign`/
  `.game_instance`/`.campaign_level`/`.user_game_record` 七个不存在的子模块，
  改为直接从现有的 `base.py` 导入 `User`/`Theme`/`Game`/`Campaign`/
  `GameInstance`/`CampaignLevel` 六个模型。`UserGameRecord` 模型尚未实现，
  留给后续按实际业务补充。
- `funapp/schema/base.py` 顶部存在对自身模块的循环导入（`from .base import
  Base`），已移除；数据库连接串改为通过 `funsecret` 下发，不再硬编码明文账号密码。
- `funapp/server/core.py` 中引用了未定义的 `load_secret_config`/`BaseServer`/
  `server_parser`/`PitServer`（疑似从其他项目复制但未完成适配的遗留代码），
  已移除，替换为可用的健康检查端点与 `run()` 启动函数。
- `funapp/work/quick.py` 中 `from funbuild.shell import run_shell` 在当前
  `funbuild` 版本中已不存在该子模块，改为 `from funshell import run_shell`。
- `pyproject.toml` 依赖补齐版本下限，并补充实际用到但此前遗漏声明的
  `farlog`/`funsecret`/`funshell`。

### 新增

- 补充 `scripts/setup.sh` 作为服务启停统一入口。
- 补充 `tests/test_smoke.py` 冒烟测试，覆盖各子包 import 与模型定义。
