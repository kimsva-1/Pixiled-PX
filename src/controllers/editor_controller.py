from PyQt6.QtGui import QImage, QColor
from PyQt6.QtCore import Qt # Додайте цей імпорт

class EditorController:
    def __init__(self, model):
        self.model = model
        self.current_color = "#000000"
        self.current_tool = "pencil"

    def set_color(self, color_hex):
        self.current_color = color_hex

    def set_tool(self, tool):
        self.current_tool = tool

    def paint_pixel(self, row, col):
        color = self.current_color if self.current_tool == "pencil" else "#FFFFFF"
        self.model.set_pixel(row, col, color)

    def save_image(self, file_path):
        if not file_path:
            return
            
        width = self.model.width
        height = self.model.height
        
        # 1. Створюємо оригінальне маленьке зображення
        image = QImage(width, height, QImage.Format.Format_ARGB32)
        for r in range(height):
            for c in range(width):
                color_hex = self.model.get_pixel(r, c)
                image.setPixelColor(c, r, QColor(color_hex))

        # 2. МАСШТАБУВАННЯ: якщо картинка менша за 512px, збільшуємо її
        # FastTransformation зберігає чіткі пікселі (без розмиття)
        if width < 512 or height < 512:
            image = image.scaled(512, 512, 
                                Qt.AspectRatioMode.KeepAspectRatio, 
                                Qt.TransformationMode.FastTransformation)

        image.save(file_path)