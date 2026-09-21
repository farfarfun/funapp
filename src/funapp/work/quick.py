import shlex
from urllib.parse import quote

from funshell import run_shell
from nicegui import app


@app.get("/work/item")
def quick_open_item(item_id: str = "173652387") -> None:
    """在本机浏览器/App 里打开喵街商品详情页。

    参数：
        item_id: 商品 id，默认值为示例 id。
    """
    if not isinstance(item_id, str) or not item_id.strip():
        raise ValueError("item_id 不能为空")
    url = "https://www.miaostreet.com/clmj/hybrid/miaojieWeex?" + (
        "pageName=goods-detail&wh_weex=true&itemId=" + quote(item_id, safe="")
    )
    cmd = f"open {shlex.quote(url)} -a {shlex.quote('/Applications/喵街.app')}"
    run_shell(cmd)
