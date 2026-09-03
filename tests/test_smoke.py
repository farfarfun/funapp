"""funapp 轻量冒烟测试（smoke test）。

覆盖范围：
- 顶层包 ``funapp`` 及各子包（``work``、``server``、``schema``、``ui``）能否正常 import。
- ``funapp.schema`` 中定义的模型是否可以正常访问。
"""

import importlib


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
    """funapp.schema 应当能正常导出六个模型类。"""
    from funapp.schema import (
        Campaign,
        CampaignLevel,
        Game,
        GameInstance,
        Theme,
        User,
    )

    for model in (User, Theme, Game, Campaign, GameInstance, CampaignLevel):
        assert hasattr(model, "__tablename__")


def test_import_funapp_server_core():
    """funapp.server.core 应当能正常导入并暴露 run()。"""
    from funapp.server.core import run

    assert callable(run)


def test_import_funapp_work_quick():
    """funapp.work.quick 应当能正常导入 funshell.run_shell。"""
    from funapp.work.quick import quick_open_item

    assert callable(quick_open_item)


def test_import_funapp_ui_login():
    """funapp/ui/login.py 是脚本式模块：import 时会直接执行 nicegui 的声明式
    UI 组件搭建代码（label/input/button 等），不涉及真实网络连接、端口监听或
    数据库访问，因此无需 mock，只需验证 import 不抛异常即可完成冒烟。"""
    importlib.import_module("funapp.ui.login")
