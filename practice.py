class products_card(ft.Container):

    def __init__(self, page, img_src, title, sub_title, price, rating):

        super().__init__(
            alignment=ft.alignment.center,
            width=150,
            height=150,
             border_radius=10,
            bgcolor="#141821",
            margin=ft.margin.only(top=10)

        )

        self.page = page
        self.img_src = img_src
        self.title = title
        self.sub_title = sub_title
        self.price = price
        self.rating = rating
        self.color_coffee = "#b9894b"
        self.bg_color = "#0c0f14"
        self.container_color = "#141821"

        self.content = ft.Column(expand=True,
                                 spacing=0,
                                 controls=[

                                     ft.Stack(

                                         controls=[

                                             ft.Container(border_radius=10,

                                                          content=ft.Image(
                                                              src="C:\\Users\\Felipe\\Downloads\\APP_FLASK\\APP_BRAFEL\\assets\\images\\{self.img_src}.png",
                                                              width=300,
                                                              fit=ft.ImageFit.COVER,
                                                              height=100),


                                                          ),

                                             ft.Container(

                                                 width=60,
                                                 alignment=ft.alignment.center,
                                                 border_radius=ft.border_radius.only(
                                                     top_left=10, bottom_right=10),
                                                 bgcolor=ft.colors.with_opacity(
                                                     0.6, "black"),
                                                 content=ft.Row(
                                                     spacing=5,
                                                     controls=[ft.Icon(ft.icons.STAR, color=self.color_coffee),
                                                               ft.Text(f"{self.rating}",
                                                                       weight="bold")


                                                               ])

                                             )


                                         ]),

                                     ft.Text(value=self.title, weight="bold"),
                                     ft.Text(value=self.sub_title,
                                             color="#5a5a5a"),
                                     ft.Row(

                                     )


                                 ])