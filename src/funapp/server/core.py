import logging


from nicegui import ui, app


logging.basicConfig(level=logging.INFO)
load_secret_config("pyintime.secret.config.oss")


@app.get("/status.taobao")
def check():
    return "success"


class FunApp(BaseServer):
    def __init__(self):
        super().__init__(server_name="pitserver")

    def update(self, args=None, **kwargs):
        pass

    def run(self, *args, **kwargs):
        try:
            from pyintime.server.online import start_server

            start_server()
        except Exception as e:
            print(e)

        try:
            from pyintime.models.tryon.manual.match import (
                start_server as tryon_start_server,
            )

            tryon_start_server()
        except Exception as e:
            print(e)

        try:
            from pyintime.web.api.oss import start_server as utils_oss_start_server

            utils_oss_start_server()
        except Exception as e:
            print(e)

        try:
            from pyintime.models.outfit.manual.match import (
                start_server as outfit_start_server,
            )

            outfit_start_server()
        except Exception as e:
            print(e)

        try:
            from pyintime.middleware.server import (
                start_server as middleware_start_server,
            )

            middleware_start_server()
        except Exception as e:
            print(e)

        try:
            from pyintime.analyse.web.service import (
                start_server as analyse_start_server,
            )

            analyse_start_server()
        except Exception as e:
            print(e)

        ui.run(show=False, reload=False, port=5678)


def pitserver():
    server = PitServer()
    parser = server_parser(server)
    args = parser.parse_args()
    params = vars(args)
    args.func(**params)
