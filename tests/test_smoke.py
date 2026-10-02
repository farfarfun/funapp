"""funapp 轻量冒烟测试（smoke test）。

覆盖范围：
- 顶层包 ``funapp`` 及各子包（``work``、``server``、``schema``、``ui``）能否正常 import。
- ``funapp.schema`` 中定义的模型是否可以正常访问。
"""

import importlib
import inspect
import os
import shlex
import subprocess
from pathlib import Path


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


def test_quick_open_item_rejects_empty_id():
    """商品 id 为空时应在执行 shell 前拒绝。"""
    import pytest

    from funapp.work.quick import quick_open_item

    with pytest.raises(ValueError):
        quick_open_item("")


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
    assert calls == [f"open {shlex.quote(url)} -a {shlex.quote('/Applications/喵街.app')}"]


def test_service_script_lifecycle(tmp_path, monkeypatch):
    """run/start/restart/stop 应按指定环境完成前后台生命周期。"""
    source = Path(__file__).parents[1] / "scripts" / "setup.sh"
    script = tmp_path / "scripts" / "setup.sh"
    script.parent.mkdir()
    script.write_bytes(source.read_bytes())
    script.chmod(0o755)

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


def test_import_funapp_ui_login():
    """funapp/ui/login.py 是脚本式模块：import 时会直接执行 nicegui 的声明式
    UI 组件搭建代码（label/input/button 等），不涉及真实网络连接、端口监听或
    数据库访问，因此无需 mock，只需验证 import 不抛异常即可完成冒烟。"""
    importlib.import_module("funapp.ui.login")
