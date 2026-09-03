from farlog import getLogger
from nicegui import app, ui

logger = getLogger(__name__)


@app.get("/status.taobao")
def check():
    """健康检查端点，返回 success 表示服务存活。"""
    return "success"


def run(*args, **kwargs) -> None:
    """启动 funapp 的 nicegui 服务。"""
    ui.run(show=False, reload=False, port=5678)
