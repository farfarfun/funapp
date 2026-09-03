from funshell import run_shell
from nicegui import app


@app.get("/work/item")
def quick_open_item(item_id: str = "173652387") -> None:
    """在本机浏览器/App 里打开喵街商品详情页。

    参数：
        item_id: 商品 id，默认值为示例 id。
    """
    cmd = f"open 'https://www.miaostreet.com/clmj/hybrid/miaojieWeex?pageName=goods-detail&wh_weex=true&itemId={item_id}' -a '/Applications/喵街.app'"
    run_shell(cmd)
