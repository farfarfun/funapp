# CHANGELOG

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
