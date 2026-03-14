import flet as ft

from models.canvas_model import CanvasModel
from controllers.editor_controller import EditorController
from views.editor_view import EditorView


def main(page: ft.Page):

    model = CanvasModel(16, 16)
    controller = EditorController(model)

    view = EditorView(page, controller, model)
    view.build()   # важливо — викликати побудову UI


ft.run(main)