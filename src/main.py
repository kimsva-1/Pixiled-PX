import sys
from PyQt6.QtWidgets import QApplication
from models.canvas_model import CanvasModel
from controllers.editor_controller import EditorController
from views.editor_view import EditorView

def main():
    app = QApplication(sys.argv)
    
    model = CanvasModel(16, 16)
    controller = EditorController(model)
    view = EditorView(controller, model)
    
    view.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()