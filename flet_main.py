import flet as ft
import requests
import re


def main(page: ft.Page):
    page.title = "BRAFEL"
    page.window.width = 500
    page.window.height = 700
    page.window.resizable = False
    page.window.center()
    page.icon = "https://cdn-icons-png.flaticon.com/512/2910/2910765.png"

    def show_snackbar(message, color="green"):
        page.snack_bar = ft.SnackBar(
            content=ft.Text(message, color="white"),
            bgcolor=color,
            duration=3000,
        )
        page.snack_bar.open = True
        page.update()

    def go_back():

        if len(page.views) > 1:
            page.views.pop()
            page.go(page.views[-1].route)

    def new_window_register(e):

        def register_view(page: ft.Page):

            def get_information_user(e):
                nombre = name_input.value
                correo = email_input.value
                contraseña = password_input.value
                rol = role_dropdown.value

                def validate_email(email):
                    email_regex = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
                    return re.match(email_regex, email)

                if not validate_email(correo):
                    show_snackbar(
                        "El correo electrónico no tiene el formato correcto", color="red")
                    page.update()
                    return

                elif not (nombre and correo and contraseña):
                    show_snackbar(
                        "Todos los campos son obligatorios", color="red")
                    page.update()
                    return

                try:
                    response = requests.post(
                        "http://127.0.0.1:5000/sitio/registro",
                        json={"nombre": nombre,
                              "correo": correo,
                              "contraseña": contraseña,
                              "rol": rol

                              },
                    )

                    if response.status_code == 200:
                        show_snackbar(
                            "Registro exitoso, puedes iniciar sesión", color="green"
                        )
                        page.go("/")

                    else:

                        show_snackbar(
                            "Este correo ya fue registrado anteriormente", color="red")

                except Exception as ex:
                    show_snackbar("Error al conectar el servidor", color="red")

            title = ft.Text("Registro de Usuario", size=24,
                            weight="bold", color="green")
            name_input = ft.TextField(
                label="Nombre", width=300, icon=ft.icons.PERSON)
            email_input = ft.TextField(
                label="Correo", width=300, icon=ft.icons.EMAIL)
            password_input = ft.TextField(
                label="Contraseña",  password=True, can_reveal_password=True, width=300, icon=ft.icons.LOCK
            )
            role_dropdown = ft.Dropdown(
                label="Rol",
                width=300,
                options=[
                    ft.dropdown.Option("cliente"),
                    ft.dropdown.Option("empleado"),
                    ft.dropdown.Option("administrador"),
                ],
                value="cliente",
            )
            register_button = ft.ElevatedButton(
                "Registrarse", icon=ft.icons.APP_REGISTRATION, width=150, on_click=get_information_user
            )
            back_button = ft.ElevatedButton(
                "Volver", icon=ft.icons.ARROW_BACK, on_click=lambda _: go_back()
            )
            status_message = ft.Text(value="", color="red")

            page.views.append(
                ft.View(
                    "/registro",
                    [
                        ft.Column(
                            [
                                title,
                                ft.Divider(),
                                name_input,
                                email_input,
                                password_input,
                                role_dropdown,
                                register_button,
                                back_button,
                                status_message,
                            ],
                            alignment=ft.MainAxisAlignment.CENTER,
                            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                            spacing=20,
                        )
                    ],
                )
            )
            page.go("/registro")

        register_view(page)

    def login_page(page: ft.Page):

        page.window.width = 1300
        page.window.height = 700
        page.window.resizable = False
        page.window.center()
        menu_visible = False

        def view_menu(e):
            nonlocal menu_visible
            menu_visible = not menu_visible
            menu_container.visible = menu_visible
            page.update()

        title = ft.Text("Bienvenido a BRAFEL", size=24,
                        weight="bold", color="green")

        def navigation(page_name):

            page.controls.clear()

            if page_name == "Productos":
                view_products(page)

                page.update()

        menu_options = [

            {"label": "Inicio", "page": "Inicio"},
            {"label": "Productos", "page": "Productos"},
            {"label": "Servicios", "page": "Servicios"},
            {"label": "Contacto", "page": "Contacto"}


        ]

        menu_items = [
            ft.TextButton(
                text=option["label"],
                on_click=lambda e, page=option["page"]: navigation(page)
            ) for option in menu_options
        ]

        menu_container = ft.Column(
            controls=menu_items,
            visible=False,
            spacing=10

        )

        hamburguer_icon = ft.IconButton(

            icon=ft.icons.MENU,
            on_click=view_menu,


        )

        logout_button = ft.ElevatedButton(
            "Cerrar Sesión",
            icon=ft.icons.LOGOUT,
            width=150,
            on_click=lambda _: page.go("/"),
        )

        page.views.append(
            ft.View(
                "/contenido",
                [
                    ft.Column(
                        [
                            title,
                            ft.Divider(),
                            hamburguer_icon,
                            menu_container,
                            ft.Text(
                                "Aquí va el contenido principal de tu aplicación"),
                            logout_button,
                        ],
                        alignment=ft.MainAxisAlignment.CENTER,
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                        spacing=20,
                    )
                ],
            )
        )
        page.go("/contenido")

    def view_products(page: ft.Page):

        page.window.width = 1300
        page.window.height = 700
        page.window.resizable = False
        page.window.center()

        texto = ft.Text("Pagina de productos")

        page.views.append(ft.View("/productos",
                          [ft.Column(
                              [texto],
                              alignment=ft.MainAxisAlignment.CENTER,
                              horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                              spacing=20




                          )]))
        page.go("/productos")

    def login_view(page: ft.Page):

        def get_login_information(e):

            correo = correo_input.value
            contraseña = password_input.value

            if not (correo and contraseña):
                show_snackbar(
                    'Todos los campos son obligatorios!', color="Red")
                page.update()
                return

            def validate_email(email):
                email_regex = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
                return re.match(email_regex, email)

            if not validate_email(correo):
                show_snackbar(
                    "El correo electrónico no tiene el formato correcto", color="red")
                page.update()
                return

            try:

                response = requests.post(

                    "http://127.0.0.1:5000/sitio/login",
                    json={"correo": correo, "contraseña": contraseña},

                )

                if response.status_code == 200:
                    data = response.json()

                    succes_value = data.get("success")

                    if succes_value in [True, "True", 1]:
                        show_snackbar(
                            "Inicio de sesion exitoso", color="green")
                        login_page(page)

                    elif succes_value in [False, "False", 0]:
                        show_snackbar("Datos incorrectos", color="red")

            except Exception as ex:

                show_snackbar(f'Error al conectar con el servidor; {
                    str(ex)}', color="red")

        titulo = ft.Text("Iniciar Sesión", size=24,
                         weight="bold", color="green")
        correo_input = ft.TextField(
            label="Correo", width=300, icon=ft.icons.PERSON)
        password_input = ft.TextField(
            label="Contraseña",  password=True, can_reveal_password=True, width=300, icon=ft.icons.LOCK
        )

        login_button = ft.ElevatedButton(
            "Ingresar", icon=ft.icons.LOGIN, width=150, on_click=get_login_information)
        register_button = ft.ElevatedButton(
            "Registrarse", icon=ft.icons.APP_REGISTRATION, width=150, on_click=new_window_register
        )

        page.views.append(
            ft.View(
                "/",
                [
                    ft.Column(
                        [
                            titulo,
                            ft.Divider(),
                            correo_input,
                            password_input,
                            ft.Row(
                                [login_button, register_button],
                                alignment=ft.MainAxisAlignment.CENTER,
                            ),
                        ],
                        alignment=ft.MainAxisAlignment.CENTER,
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                        spacing=20,
                    )
                ],
            )
        )
        page.go("/")

    login_view(page)


ft.app(target=main)
