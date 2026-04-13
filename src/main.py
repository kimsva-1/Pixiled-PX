import sys
from PyQt6.QtWidgets import QApplication
from models.canvas_model import CanvasModel
from controllers.editor_controller import EditorController
from views.editor_view import EditorView, NewCanvasDialog # Імпортуємо діалог

def main():
    app = QApplication(sys.argv)
    
    # 1. Показуємо діалогове вікно
    dialog = NewCanvasDialog()
    if dialog.exec():  # Якщо користувач натиснув "Створити"
        width, height = dialog.get_values()
        
        # 2. Створюємо модель з отриманими розмірами
        model = CanvasModel(width, height)
        controller = EditorController(model)
        view = EditorView(controller, model)
        
        view.show()
        sys.exit(app.exec())
    else:
        # Якщо користувач закрив діалог, просто виходимо
        sys.exit(0)

if __name__ == "__main__":
    main()