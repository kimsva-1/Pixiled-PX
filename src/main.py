import sys
from PyQt6.QtWidgets import QApplication
from views.editor_view import EditorView

def main():
    app = QApplication(sys.argv)
    view = EditorView() #створюється без аргументів 
    view.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()