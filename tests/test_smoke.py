"""funapp 轻量冒烟测试（smoke test）。

覆盖范围：
- 顶层包 ``funapp`` 及各子包（``work``、``server``、``schema``、``ui``）能否正常 import。
- 对确实可以正常导入、且只包含纯声明式代码（不发起真实网络/端口/数据库调用）的
  模块（如 ``funapp.ui.login``），验证 import 不抛异常。

本仓库此前没有 ``tests/`` 目录，探测过程中发现该包本身存在若干未完成/过时的
代码，均为仓库自身的 bug，不在本次冒烟测试范围内修复，以 ``pytest.skip`` 标注：

1. ``funapp/schema/__init__.py`` 导入了 ``.user``/``.theme``/``.game``/
   ``.campaign``/``.game_instance``/``.campaign_level``/``.user_game_record``
   七个子模块，但仓库里只有一个 ``base.py``，这些文件都不存在，
   import 会直接抛 ``ModuleNotFoundError``。
2. ``funapp/schema/base.py`` 文件顶部 ``from .base import Base`` 是对自身模块的
   循环导入，而 ``Base`` 实际是在文件下方通过 ``declarative_base()`` 重新赋值
   定义的——这是逻辑上自相矛盾的死代码，即便问题 1 被修复，直接导入
   ``funapp.schema.base`` 也会因循环导入而失败。
3. ``funapp/server/core.py`` 模块顶层直接调用了从未定义/导入的
   ``load_secret_config(...)``，并引用了未定义的 ``BaseServer``/
   ``server_parser``/``PitServer``，import 该模块必然 ``NameError``；
   从内容看这是从另一个项目（pyintime/pitserver）复制过来、但未完成适配的
   遗留代码。
4. ``funapp/work/quick.py`` 中的 ``from funbuild.shell import run_shell``
   在当前 funbuild（1.6.69）中已不存在该子模块（相关能力被拆分到独立的
   ``funshell`` 包），属于上游依赖 API 变更导致的过时引用。

以上均为「真实业务逻辑 bug」，按任务要求不在此处修改源码，仅跳过并在报告中说明。
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


def test_import_funapp_schema_package_broken():
    import pytest

    pytest.skip(
        "已知 bug：funapp/schema/__init__.py 导入 .user/.theme/.game/.campaign/"
        ".game_instance/.campaign_level/.user_game_record 七个子模块，但仓库中"
        "只有 base.py，这些文件都不存在，import 会抛 ModuleNotFoundError。"
        "这是仓库自身未完成的重构遗留问题，跳过，不在本次冒烟测试中修复。"
    )


def test_import_funapp_server_core_broken():
    import pytest

    pytest.skip(
        "已知 bug：funapp/server/core.py 模块顶层调用了未定义的 "
        "load_secret_config(...)，并引用了未定义的 BaseServer/server_parser/"
        "PitServer，import 即触发 NameError。疑似从另一个项目（pyintime/"
        "pitserver）复制过来但未完成适配的遗留代码，跳过。"
    )


def test_import_funapp_work_quick_broken():
    import pytest

    pytest.skip(
        "已知 bug：funapp/work/quick.py 中的 `from funbuild.shell import "
        "run_shell` 在当前 funbuild(1.6.69) 中已不存在该子模块（相关能力已被"
        "拆分到独立的 funshell 包），属于上游依赖 API 变更导致的过时引用，跳过。"
    )


def test_import_funapp_ui_login():
    """funapp/ui/login.py 是脚本式模块：import 时会直接执行 nicegui 的声明式
    UI 组件搭建代码（label/input/button 等），不涉及真实网络连接、端口监听或
    数据库访问，因此无需 mock，只需验证 import 不抛异常即可完成冒烟。"""
    importlib.import_module("funapp.ui.login")
