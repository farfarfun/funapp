"""登录页面的静态布局原型。

当前只有布局：输入框、链接和按钮都**没有绑定任何回调**，也没有接入认证逻辑，
`funapp.server.core.run()` 不会导入或挂载本模块。想预览这个页面时手动
`import funapp.ui.login`；真正可用的登录流程仍待实现。
"""

from nicegui import ui

with ui.element().classes("flex justify-center items-center h-full w-full"):  # noqa: SIM117
    with ui.element().classes("grid gap-8 w-full"):
        with ui.element().classes(
            "bg-gradient-to-r from-blue-500 to-purple-500 rounded-3xl"
        ):
            with ui.element().classes(
                "border-8 border-transparent rounded-xl bg-white dark:bg-gray-900 shadow-xl p-8 m-2"
            ):
                ui.label("Log in").classes(
                    "text-5xl font-bold text-center cursor-default dark:text-gray-300 text-gray-900"
                )
                with ui.element().classes("space-y-6"):
                    with ui.element().classes():
                        ui.label("Email").classes(
                            "block mb-2 text-lg dark:text-gray-300"
                        )
                        ui.input("Email").classes(
                            "border p-3 shadow-md dark:bg-indigo-700 dark:text-gray-300 dark:border-gray-700 border-gray-300 rounded-lg w-full focus:ring-2 focus:ring-blue-500 transition transform hover:scale-105 duration-300"
                        )
                    with ui.element().classes():
                        ui.label("Password").classes(
                            "block mb-2 text-lg dark:text-gray-300"
                        )
                        ui.input("password").classes(
                            "border p-3 shadow-md dark:bg-indigo-700 dark:text-gray-300 dark:border-gray-700 border-gray-300 rounded-lg w-full focus:ring-2 focus:ring-blue-500 transition transform hover:scale-105 duration-300"
                        )

                    ui.link("Forget your password?").classes(
                        "text-blue-400 text-sm transition hover:underline"
                    )
                    ui.button("LOG IN").classes(
                        "w-full p-3 mt-4 text-white bg-gradient-to-r from-blue-500 to-purple-500 rounded-lg hover:scale-105 transition transform duration-300 shadow-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                    )

                with ui.element().classes(  # noqa: SIM117
                    "flex flex-col mt-4 text-sm text-center dark:text-gray-300"
                ):
                    with ui.row():
                        ui.label("Don't have an account?")
                        ui.link("Sign up").classes(
                            "text-blue-400 transition hover:underline"
                        )
