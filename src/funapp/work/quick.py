from funbuild.shell import run_shell
from nicegui import app


@app.get("/work/item")
def quick_open_item(item_id="173652387"):
    cmd = f"open 'https://www.miaostreet.com/clmj/hybrid/miaojieWeex?pageName=goods-detail&wh_weex=true&itemId={item_id}' -a '/Applications/喵街.app'"
    run_shell(cmd)
