import flet as ft

PIXEL_SIZE = 15


class EditorView:

    def __init__(self, page, controller, model):
        self.page = page
        self.controller = controller
        self.model = model
        self.pixel_controls = []
        self.mouse_down = False

    def color_button(self, color):
        return ft.Container(
            width=30,
            height=30,
            bgcolor=color,
            border=ft.border.all(1, "#000000"),
            on_click=lambda e: self.controller.set_color(color)
        )

    def build(self):

        grid_rows = []

        for r in range(self.model.height):

            row_controls = []
            row_ui = []

            for c in range(self.model.width):

                pixel = ft.Container(
                    width=PIXEL_SIZE,
                    height=PIXEL_SIZE,
                    bgcolor=self.model.get_pixel(r, c),
                    border=ft.border.all(0.5, "#CCCCCC"),
                    data=(r, c),
                    on_click=self.on_pixel_click,
                    on_hover=self.on_pixel_hover
                )

                row_controls.append(pixel)
                row_ui.append(pixel)

            self.pixel_controls.append(row_controls)
            grid_rows.append(ft.Row(row_ui, spacing=0))

        grid = ft.Column(grid_rows, spacing=0)

        palette = ft.Row([
            self.color_button("#000000"),
            self.color_button("#FF0000"),
            self.color_button("#00FF00"),
            self.color_button("#0000FF"),
            self.color_button("#FFFF00"),
            self.color_button("#FFFFFF"),
        ])

        tools = ft.Row([
            ft.ElevatedButton(
                "✏ Pencil",
                on_click=lambda e: self.controller.set_tool("pencil")
            ),
            ft.ElevatedButton(
                "🧽 Eraser",
                on_click=lambda e: self.controller.set_tool("eraser")
            ),
        ])

        canvas = ft.GestureDetector(
            content=grid,
            on_pan_start=self.on_mouse_down,
            on_pan_end=self.on_mouse_up
        )

        self.page.add(
            ft.Column([
                tools,
                palette,
                canvas
            ])
        )

    def on_mouse_down(self, e):
        self.mouse_down = True

    def on_mouse_up(self, e):
        self.mouse_down = False

    def on_pixel_click(self, e):
        self.paint_pixel(e)

    def on_pixel_hover(self, e):
        if self.mouse_down:
            self.paint_pixel(e)

    def paint_pixel(self, e):

        row, col = e.control.data

        self.controller.paint_pixel(row, col)

        color = self.model.get_pixel(row, col)

        e.control.bgcolor = color
        e.control.update()   # дуже швидко