import flet as ft
import requests
import re
import os
from functools import partial


class ProductCard(ft.Container):
    def __init__(self, img_src, title, sub_title, price, rating):
        super().__init__(

            expand=True,
            border_radius=10,
            padding=10,
            margin=ft.margin.symmetric(vertical=5),
            bgcolor="red",
            content=ft.Row(
                controls=[

                    ft.Container(
                        width=100,
                        height=100,
                        border_radius=10,
                        content=ft.Image(
                            src=f"C:\\Users\\Felipe\\Downloads\\APP_FLASK\\APP_BRAFEL\\assets\\images\\{
                                img_src}.png",
                            fit=ft.ImageFit.CONTAIN,
                        ),
                    ),
                   
                    ft.Column(
                        expand=True,
                        spacing=5,
                        controls=[
                            ft.Text(title, weight="bold", color="white"),
                            ft.Text(sub_title, color="#5a5a5a"),
                            ft.Row(
                                controls=[
                                    ft.Icon(ft.icons.STAR, color="#b9894b"),
                                    ft.Text(f"{rating}", color="white"),
                                    ft.Text(f"${price}",
                                            color="green", weight="bold"),
                                ]
                            ),
                        ],
                    ),
                ],
            ),
        )


def main(page: ft.Page):
    page.title = "BRAFEL"
    page.window.width = 450
    page.window.height = 750
    page.window.resizable = False
    page.window.center()
    page.icon = "https://cdn-icons-png.flaticon.com/512/2910/2910765.png"

    page.fonts = {
        "Mifuente": "APP_BRAFEL\Montserrat.ttf"
    }

    """if os.path.exists(fuente):
        print(f"La fuente {fuente} fue encontrada.")
    else:
        print(f"La fuente {fuente} NO fue encontrada.")"""

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

        page.window.center()

        products = [
            {"img_src": "cajonera", "title": "Cajonera",
                "sub_title": "Nogal clásico", "price": 4300, "rating": 4.9},
            {"img_src": "sofa", "title": "Sofá",
                "sub_title": "Confort y diseño", "price": 5500, "rating": 4.7},
            {"img_src": "mesa", "title": "Mesa",
                "sub_title": "Para comedor", "price": 3200, "rating": 4.5},
        ]

        product_cards = [
            ProductCard(
                img_src=product["img_src"],
                title=product["title"],
                sub_title=product["sub_title"],
                price=product["price"],
                rating=product["rating"],
            )
            for product in products
        ]

        product_list = ft.ListView(
            expand=True,
            controls=product_cards,
        )

        container_1 = ft.Container(
            expand=True,
            padding=10,
            offset=ft.transform.Offset(0, 0),
            content=ft.Column(
                expand=True,
                controls=[

                    ft.Row(
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                        controls=[
                            ft.IconButton(ft.icons.MENU, icon_color="white"),
                            ft.Container(
                                ft.Image(src="", height=30), border_radius=10
                            ),
                        ],
                    ),

                    ft.Text(
                        "Encuentra el mejor \n estilo para tu hogar",
                        font_family="Mifuente",
                        size=25,
                        weight="bold",
                        color="white",
                    ),

                    ft.TextField(
                        prefix=ft.Icon(name=ft.icons.SEARCH, color="white"),
                        hint_text=" Encuentra tu mueble",
                        border_radius=10,
                        bgcolor="#141821",
                        border_color="transparent",
                        on_change=filter_products,
                        color="white",
                        hint_style=ft.TextStyle(color="white"),
                    ),

                    ft.Container(
                        expand=True,
                        
                        
                        content=ft.Tabs(
                            expand=True,  
                            selected_index=0,
                            indicator_color="transparent",
                            label_color="#b9894b",
                            unselected_label_color="white",
                            tabs=[

                                ft.Tab(
                                    text="Todos",
                                    content=ft.Container(
                                        expand=True,
                                        content=product_list,
                                    ),
                                ),

                                ft.Tab(
                                    text="Salas",
                                    content=ft.GridView(
                                        runs_count=2,
                                        child_aspect_ratio=0.6,
                                        controls=[],
                                    ),
                                ),
                                ft.Tab(
                                    text="Comedores",
                                    content=ft.GridView(
                                        runs_count=2,
                                        child_aspect_ratio=0.6,
                                        controls=[],
                                    ),
                                ),
                                ft.Tab(
                                    text="Recamaras",
                                    content=ft.GridView(
                                        runs_count=2,
                                        child_aspect_ratio=0.6,
                                        controls=[],
                                    ),
                                ),
                                ft.Tab(
                                    text="Sanitarios",
                                    content=ft.GridView(
                                        runs_count=2,
                                        child_aspect_ratio=0.6,
                                        controls=[],
                                    ),
                                ),
                            ],
                        ),
                    ),
                ],
            ),
        )

        container2 = ft.Container(

            offset=ft.transform.Offset(-2, 0),
            content=ft.Column(

                expand=True,
                alignment=ft.MainAxisAlignment.CENTER,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                controls=[
                    ft.Text("Tienda", size=20, color="white"),
                    ft.Container(
                        alignment=ft.alignment.center,
                        content=ft.Image(
                            src="C:\\Users\\Felipe\\Downloads\\APP_FLASK\\APP_BRAFEL\\assets\\images\\shop.gif", fit=ft.ImageFit.CONTAIN, width=100)


                    )


                ]


            )


        )

        container3 = ft.Container(

            offset=ft.transform.Offset(-2, 0),
            content=ft.Column(

                expand=True,
                alignment=ft.MainAxisAlignment.CENTER,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                controls=[
                    ft.Text("Notificaciones", size=20, color="white"),
                    ft.Container(
                        alignment=ft.alignment.center,
                        content=ft.Image(
                            src="C:\\Users\\Felipe\\Downloads\\APP_FLASK\\APP_BRAFEL\\assets\\images\\notification.gif", fit=ft.ImageFit.CONTAIN, width=120)


                    )


                ]


            )


        )

        container4 = ft.Container(

            offset=ft.transform.Offset(-2, 0),
            content=ft.Column(

                expand=True,
                alignment=ft.MainAxisAlignment.CENTER,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                controls=[
                    ft.Text("Favoritos", size=20, color="white"),
                    ft.Container(
                        alignment=ft.alignment.center,
                        content=ft.Image(
                            src="C:\\Users\\Felipe\\Downloads\\APP_FLASK\\APP_BRAFEL\\assets\\images\\favorite.gif", fit=ft.ImageFit.CONTAIN, width=120)


                    )


                ]


            )


        )

        selected = ft.Container(

            shape=ft.BoxShape.CIRCLE,
            offset=ft.transform.Offset(-0.38, 0),
            bgcolor="#18191b",
            alignment=ft.alignment.center,
            margin=ft.margin.only(top=5),
            height=50,
            content=ft.Icon(ft.icons.HOME_FILLED, color="#b9894b")


        )

        def change_position(e):

            if e.control.data == "1":
                selected.offset = ft.transform.Offset(-0.38, 0)
                selected.content = ft.Icon(
                    name=ft.icons.HOME_FILLED, color="#b9894b")
                container_1.offset = ft.transform.Offset(0, 0)
                container2.offset = ft.transform.Offset(-2, 0)
                container3.offset = ft.transform.Offset(-2, 0)
                container4.offset = ft.transform.Offset(-2, 0)

            if e.control.data == "2":
                selected.offset = ft.transform.Offset(-0.12, 0)
                selected.content = ft.Icon(
                    name=ft.icons.SHOPPING_BAG_ROUNDED, color="#b9894b")
                container_1.offset = ft.transform.Offset(-2, 0)
                container2.offset = ft.transform.Offset(0, 0)
                container3.offset = ft.transform.Offset(-2, 0)
                container4.offset = ft.transform.Offset(-2, 0)

            if e.control.data == "3":
                selected.offset = ft.transform.Offset(0.12, 0)
                selected.content = ft.Icon(
                    name=ft.icons.FAVORITE, color="#b9894b")
                container_1.offset = ft.transform.Offset(-2, 0)
                container2.offset = ft.transform.Offset(-2, 0)
                container3.offset = ft.transform.Offset(0, 0)
                container4.offset = ft.transform.Offset(-2, 0)

            if e.control.data == "4":
                selected.offset = ft.transform.Offset(0.38, 0)
                selected.content = ft.Icon(
                    name=ft.icons.NOTIFICATIONS, color="#b9894b")
                container_1.offset = ft.transform.Offset(-2, 0)
                container2.offset = ft.transform.Offset(-2, 0)
                container3.offset = ft.transform.Offset(-2, 0)
                container4.offset = ft.transform.Offset(0, 0)

            page.update()

        nav = ft.Container(

            bgcolor="#18191b",
            alignment=ft.alignment.center,
            border_radius=10,
            padding=0,
            height=50,
            margin=ft.margin.only(top=5),
            content=ft.Row(
                alignment=ft.MainAxisAlignment.SPACE_AROUND,
                controls=[
                    ft.IconButton(ft.icons.HOME_FILLED, data="1",
                                  icon_color="white", icon_size=24, on_click=change_position),
                    ft.IconButton(ft.icons.SHOPPING_BAG_ROUNDED, data="2",
                                  icon_color="white", icon_size=24, on_click=change_position),
                    ft.IconButton(ft.icons.FAVORITE, data="3",
                                  icon_color="white", icon_size=24, on_click=change_position),
                    ft.IconButton(ft.icons.NOTIFICATIONS, data="4",
                                  icon_color="white", icon_size=24, on_click=change_position)


                ]


            )


        )

        page.views.append(

            ft.View(
                "/contenido",
                bgcolor="#0c0f14",

                controls=[

                    ft.Stack(
                        expand=True,
                        controls=[

                            container_1,
                            container2,
                            container3,
                            container4

                        ]

                    ),

                    ft.Stack(
                        expand=True,
                        height=60,
                        alignment=ft.alignment.bottom_center,
                        controls=[
                            nav,
                            selected

                        ]

                    )

                ]

            )

        )

        page.go("/contenido")

    def filter_products(e):
        pass

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

                show_snackbar(f'Error al conectar con el servidor: {
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
