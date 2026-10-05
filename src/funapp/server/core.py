from farlog import getLogger
from nicegui import app, ui

# Importing the route module registers the documented local-work endpoint.
from funapp.work import quick  # noqa: F401

logger = getLogger(__name__)


@app.get("/status.taobao")
def check() -> str:
    """健康检查端点，返回 success 表示服务存活。"""
    return "success"


def run() -> None:
    """启动 funapp 的 nicegui 服务。"""
    ui.run(show=False, reload=False, port=5678)
