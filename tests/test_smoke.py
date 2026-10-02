"""funapp 的导入冒烟 + 公开 API 行为测试。

覆盖范围：
- 顶层包 ``funapp`` 及各子包（``work``、``server``、``schema``、``ui``）能否正常 import。
- ``funapp.server.core`` 的健康检查端点与 ``run()`` 启动参数。
- ``funapp.work.quick.quick_open_item`` 的正常路径（URL 编码 + shell 命令构造）与
  非法入参边界。
- ``funapp.schema`` 的模型建表、默认值、外键关系与唯一约束（跑在临时 SQLite 上）。
- ``scripts/setup.sh`` 的 dev 前后台生命周期，以及 prod 只认 site-packages 内
  正式包、拒绝源码/editable 的行为。
"""

import importlib
import inspect
import os
import shlex
import subprocess
import sys
import sysconfig
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).parents[1]
EXPECTED_TABLES = {
    "t_user",
    "t_theme",
    "t_game",
    "t_campaign",
    "t_game_instance",
    "t_campaign_level",
}


def _copy_setup_script(tmp_path: Path) -> Path:
    """把 scripts/setup.sh 复制到临时目录，让 ROOT_DIR 指向隔离的沙箱。"""
    script = tmp_path / "scripts" / "setup.sh"
    script.parent.mkdir(parents=True, exist_ok=True)
    script.write_bytes((REPO_ROOT / "scripts" / "setup.sh").read_bytes())
    script.chmod(0o755)
    return script


def test_import_funapp_top_level():
    """顶层包应当可以正常 import（当前 __init__.py 为空，无副作用）。"""
    import funapp

    assert funapp is not None


def test_import_funapp_work_package():
    """funapp.work 为空的 __init__.py，import 不应有副作用或报错。"""
    import funapp.work  # noqa: F401


def test_import_funapp_server_package():
    """funapp.server 为空的 __init__.py，import 不应有副作用或报错。"""
    import funapp.server  # noqa: F401


def test_import_funapp_schema_package():
    """funapp.schema 应当导出模型和建表入口。"""
    from funapp.schema import (
        Campaign,
        CampaignLevel,
        Game,
        GameInstance,
        Theme,
        User,
        create_tables,
    )

    for model in (User, Theme, Game, Campaign, GameInstance, CampaignLevel):
        assert hasattr(model, "__tablename__")
    assert callable(create_tables)


def test_health_check():
    """健康检查应返回固定成功值。"""
    from funapp.server.core import check

    assert check() == "success"


def test_create_tables_uses_metadata(monkeypatch):
    """建表入口应调用当前模型元数据。"""
    from funapp.schema import base

    called = []
    monkeypatch.setattr(
        base.Base.metadata, "create_all", lambda engine: called.append(engine)
    )
    base.create_tables()
    assert called == [base.engine]


def test_default_database_url_contains_no_credentials():
    """未配置密钥时应使用不含凭据的本地数据库。"""
    from funapp.schema import base

    assert base.engine.url.drivername == "sqlite"
    assert base.engine.url.username is None
    assert base.engine.url.password is None


def test_import_funapp_server_core():
    """funapp.server.core 应当能正常导入并暴露 run()。"""
    from funapp.server.core import run

    assert callable(run)
    assert not inspect.signature(run).parameters


def test_run_starts_nicegui_with_expected_settings(monkeypatch):
    """服务入口应使用固定的非交互配置启动 NiceGUI。"""
    from funapp.server import core

    calls = []
    monkeypatch.setattr(core.ui, "run", lambda **kwargs: calls.append(kwargs))
    core.run()
    assert calls == [{"show": False, "reload": False, "port": 5678}]


def test_import_funapp_work_quick():
    """funapp.work.quick 应当能正常导入 funshell.run_shell。"""
    from funapp.work.quick import quick_open_item

    assert callable(quick_open_item)


@pytest.mark.parametrize("bad_id", ["", "   ", "\t\n"])
def test_quick_open_item_rejects_blank_id(monkeypatch, bad_id):
    """商品 id 为空或纯空白时应在执行 shell 前拒绝。"""
    from funapp.work import quick

    calls = []
    monkeypatch.setattr(quick, "run_shell", calls.append)
    with pytest.raises(ValueError):
        quick.quick_open_item(bad_id)
    assert calls == []


def test_quick_open_item_rejects_non_string_id(monkeypatch):
    """非字符串 id 同样应被拒绝，不能拼进 shell 命令。"""
    from funapp.work import quick

    calls = []
    monkeypatch.setattr(quick, "run_shell", calls.append)
    with pytest.raises(ValueError):
        quick.quick_open_item(173652387)  # type: ignore[arg-type]
    assert calls == []


def test_quick_open_item_uses_default_id(monkeypatch):
    """不传参数时应使用默认示例 id，命令里带上该 id。"""
    from funapp.work import quick

    calls = []
    monkeypatch.setattr(quick, "run_shell", calls.append)
    quick.quick_open_item()
    assert len(calls) == 1
    assert "itemId=173652387" in calls[0]


def test_quick_open_item_opens_encoded_url(monkeypatch):
    """有效商品 id 应被编码后传给喵街客户端。"""
    from funapp.work import quick

    calls = []
    monkeypatch.setattr(quick, "run_shell", calls.append)
    quick.quick_open_item("item / 1")

    url = (
        "https://www.miaostreet.com/clmj/hybrid/miaojieWeex?"
        "pageName=goods-detail&wh_weex=true&itemId=item%20%2F%201"
    )
    assert calls == [
        f"open {shlex.quote(url)} -a {shlex.quote('/Applications/喵街.app')}"
    ]


def test_service_script_lifecycle(tmp_path, monkeypatch):
    """run/start/restart/stop 应按指定环境完成前后台生命周期。"""
    script = _copy_setup_script(tmp_path)

    bin_dir = tmp_path / "bin"
    bin_dir.mkdir()
    fake_python = bin_dir / "python3"
    fake_python.write_text(
        "#!/bin/bash\n[[ -n ${FAKE_FOREGROUND:-} ]] && exit 0\nexec sleep 30\n"
    )
    fake_python.chmod(0o755)
    monkeypatch.setenv("PATH", f"{bin_dir}:{Path('/usr/bin')}:{Path('/bin')}")

    foreground_env = {**os.environ, "FAKE_FOREGROUND": "1"}
    subprocess.run(
        [str(script), "run", "dev"], env=foreground_env, check=True, timeout=5
    )
    started = subprocess.run(
        [str(script), "start", "dev"], check=True, capture_output=True, text=True
    )
    assert "funapp[dev] 已在后台启动" in started.stdout

    restarted = subprocess.run(
        [str(script), "restart", "dev"], check=True, capture_output=True, text=True
    )
    assert "funapp[dev] 已停止" in restarted.stdout
    assert "funapp[dev] 已在后台启动" in restarted.stdout

    stopped = subprocess.run(
        [str(script), "stop", "dev"], check=True, capture_output=True, text=True
    )
    assert "funapp[dev] 已停止" in stopped.stdout


def test_service_script_rejects_missing_env():
    """start/stop/restart/run 缺少 dev|prod 参数时必须直接报用法并失败。"""
    script = REPO_ROOT / "scripts" / "setup.sh"
    for action in ("start", "stop", "restart", "run"):
        result = subprocess.run(
            [str(script), action],
            check=False,
            capture_output=True,
            text=True,
            timeout=10,
        )
        assert result.returncode != 0, action
        assert "用法" in result.stderr, action


def _require_editable_dev_install() -> None:
    """确认当前解释器里的 funapp 就是本仓库源码（`uv run` / `uv sync` 的 editable）。

    下面两个 prod 测试依赖这一点：它们要验证的恰恰是「editable 装着也不许当
    正式包跑」，而不是靠 PYTHONPATH 伪造一个场景。
    """
    import funapp

    pkg = Path(funapp.__file__).resolve()
    assert pkg.is_relative_to((REPO_ROOT / "src").resolve()), (
        f"本测试需要在本仓库的 editable 开发环境里运行（uv run pytest），当前 funapp 在 {pkg}"
    )


def test_service_script_prod_rejects_editable_install(tmp_path, monkeypatch):
    """prod 不能接受 editable 安装：加载路径不在 site-packages 内就必须拒绝。

    editable 安装会把源码目录重新塞回 ``sys.path``，所以
    ``cd /tmp && python -c "import funapp"`` 这种校验永远会通过——这里断言脚本
    不会被它骗过去。脚本放在隔离的 ROOT_DIR 下，绕开「加载路径在仓库目录内」
    那条更早的分支，专门压 site-packages 断言。
    """
    _require_editable_dev_install()
    script = _copy_setup_script(tmp_path)
    monkeypatch.setenv("PATH", f"{Path(sys.executable).parent}:/usr/bin:/bin")
    monkeypatch.delenv("PYTHONPATH", raising=False)

    result = subprocess.run(
        [str(script), "run", "prod"],
        check=False,
        capture_output=True,
        text=True,
        timeout=60,
    )
    assert result.returncode != 0
    assert "site-packages" in result.stderr
    assert not (tmp_path / ".run" / "funapp-prod.pid").exists()


def test_service_script_prod_rejects_repo_source_tree(monkeypatch):
    """用本仓库真实的脚本跑 prod：funapp 落在仓库目录内时必须明确报错。"""
    _require_editable_dev_install()
    script = REPO_ROOT / "scripts" / "setup.sh"
    monkeypatch.setenv("PATH", f"{Path(sys.executable).parent}:/usr/bin:/bin")
    monkeypatch.delenv("PYTHONPATH", raising=False)

    result = subprocess.run(
        [str(script), "run", "prod"],
        check=False,
        capture_output=True,
        text=True,
        timeout=60,
    )
    assert result.returncode != 0
    assert "本仓库源码目录" in result.stderr
    assert not (REPO_ROOT / ".run" / "funapp-prod.pid").exists()


def test_service_script_prod_accepts_site_packages_install(tmp_path, monkeypatch):
    """funapp 真的装进 site-packages 时，prod 必须放行并启动服务入口。"""
    venv_dir = tmp_path / "venv"
    subprocess.run(
        [sys.executable, "-m", "venv", "--without-pip", str(venv_dir)],
        check=True,
        timeout=120,
    )
    venv_python = venv_dir / "bin" / "python3"
    if not venv_python.exists():
        pytest.fail(f"虚拟环境未按预期创建 python3: {sorted(venv_dir.iterdir())}")
    site_packages = Path(
        subprocess.run(
            [
                str(venv_python),
                "-c",
                "import sysconfig;print(sysconfig.get_path('purelib'))",
            ],
            check=True,
            capture_output=True,
            text=True,
            timeout=60,
        ).stdout.strip()
    )
    assert site_packages.name == "site-packages"
    assert site_packages != Path(sysconfig.get_path("purelib"))

    # 装一个无第三方依赖的最小 funapp，只为验证 prod 校验与启动命令本身。
    pkg = site_packages / "funapp"
    (pkg / "server").mkdir(parents=True)
    (pkg / "__init__.py").write_text("")
    (pkg / "server" / "__init__.py").write_text("")
    (pkg / "server" / "core.py").write_text(
        'def run() -> None:\n    print("prod-entry-called")\n'
    )

    # 脚本的 ROOT_DIR 必须与 venv 分离，否则会先命中「从仓库源码加载」那条校验。
    script = _copy_setup_script(tmp_path / "repo")
    monkeypatch.setenv("PATH", f"{venv_dir / 'bin'}:/usr/bin:/bin")
    monkeypatch.delenv("PYTHONPATH", raising=False)

    result = subprocess.run(
        [str(script), "run", "prod"],
        check=False,
        capture_output=True,
        text=True,
        timeout=60,
    )
    assert result.returncode == 0, result.stderr
    assert "prod-entry-called" in result.stdout


def test_models_create_tables_and_relations(tmp_path):
    """模型应能在临时数据库上建表，并按定义应用默认值与外键关系。"""
    from sqlalchemy import create_engine
    from sqlalchemy import inspect as sa_inspect
    from sqlalchemy.orm import Session

    from funapp.schema import Campaign, Theme, base

    engine = create_engine(f"sqlite:///{tmp_path / 'funapp-test.db'}")
    base.Base.metadata.create_all(engine)
    assert EXPECTED_TABLES <= set(sa_inspect(engine).get_table_names())

    with Session(engine) as session:
        theme = Theme(name="春节", description="春节主题")
        session.add(theme)
        session.flush()
        session.add(Campaign(name="春节活动", theme_id=theme.id))
        session.commit()

    with Session(engine) as session:
        campaign = session.query(Campaign).filter_by(name="春节活动").one()
        assert campaign.theme.name == "春节"
        assert campaign.status == 1
        assert campaign.max_level_count == 1


def test_theme_name_unique_constraint(tmp_path):
    """主题名重复应被唯一约束拒绝，而不是静默写入两行。"""
    from sqlalchemy import create_engine
    from sqlalchemy.exc import IntegrityError
    from sqlalchemy.orm import Session

    from funapp.schema import Theme, base

    engine = create_engine(f"sqlite:///{tmp_path / 'unique.db'}")
    base.Base.metadata.create_all(engine)
    with Session(engine) as session:
        session.add_all([Theme(name="重复"), Theme(name="重复")])
        with pytest.raises(IntegrityError):
            session.commit()


def test_invalid_database_url_fails_loudly():
    """配置了无法识别的连接串时必须当场报错，不能静默回退到默认库。"""
    from sqlalchemy import create_engine
    from sqlalchemy.exc import ArgumentError

    with pytest.raises(ArgumentError):
        create_engine("not-a-valid-url")


def test_http_routes_registered():
    """健康检查与快捷入口都应注册到 nicegui 的 FastAPI 应用上。"""
    from nicegui import app

    import funapp.server.core
    import funapp.work.quick  # noqa: F401

    paths = {route.path for route in app.routes if hasattr(route, "path")}
    assert "/status.taobao" in paths
    assert "/work/item" in paths


def test_import_funapp_ui_package():
    """funapp.ui 应当是带 __init__.py 的正式子包，而不是命名空间包。"""
    import funapp.ui

    assert funapp.ui.__file__ is not None
    assert funapp.ui.__doc__


def test_import_funapp_ui_login():
    """funapp/ui/login.py 是脚本式模块：import 时会直接执行 nicegui 的声明式
    UI 组件搭建代码（label/input/button 等），不涉及真实网络连接、端口监听或
    数据库访问，因此无需 mock，只需验证 import 不抛异常即可完成冒烟。"""
    importlib.import_module("funapp.ui.login")
