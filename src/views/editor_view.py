from PyQt6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                            QPushButton, QFileDialog, QDialog, QLabel, QSpinBox, 
                            QScrollArea
                            )
from PyQt6.QtGui import QPainter, QColor, QPen
from PyQt6.QtCore import Qt

class NewCanvasDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Налаштування проекту")
        layout = QVBoxLayout(self)

        # Збільшуємо поріг до 256
        layout.addWidget(QLabel("Ширина (8-256):"))
        self.width_spin = QSpinBox()
        self.width_spin.setRange(8, 256) 
        self.width_spin.setValue(32)
        layout.addWidget(self.width_spin)

        layout.addWidget(QLabel("Висота (8-256):"))
        self.height_spin = QSpinBox()
        self.height_spin.setRange(8, 256)
        self.height_spin.setValue(32)
        layout.addWidget(self.height_spin)

        self.btn_ok = QPushButton("Створити")
        self.btn_ok.clicked.connect(self.accept)
        layout.addWidget(self.btn_ok)

    def get_values(self):
        return self.width_spin.value(), self.height_spin.value()

class PixelCanvas(QWidget):
    def __init__(self, controller, model):
        super().__init__()
        self.controller = controller
        self.model = model
        self.last_pos = None  # Для збереження попередньої точки

        # Налаштовуємо розмір: зробимо піксель трохи меншим (20 замість 25), 
        # щоб 25x25 точно влізло без прокрутки
        self.pixel_size = 20 
        self.setFixedSize(self.model.width * self.pixel_size, self.model.height * self.pixel_size)

    def paintEvent(self, event):
        painter = QPainter(self)
        ps = self.pixel_size
        for r in range(self.model.height):
            for c in range(self.model.width):
                color_hex = self.model.get_pixel(r, c)
                painter.fillRect(c * ps, r * ps, ps, ps, QColor(color_hex))
                painter.setPen(QPen(QColor("#E0E0E0"), 1))
                painter.drawRect(c * ps, r * ps, ps, ps)

    def mousePressEvent(self, event):
        # При натисканні фіксуємо першу точку
        curr_pos = event.position()
        self.last_pos = curr_pos
        self.process_mouse(curr_pos)

    def mouseMoveEvent(self, event):
        if self.last_pos is not None:
            curr_pos = event.position()
            # Малюємо лінію між минулою і поточною точкою
            self.draw_line(self.last_pos, curr_pos)
            self.last_pos = curr_pos
            self.update()

    def mouseReleaseEvent(self, event):
        self.last_pos = None

    def draw_line(self, start, end):
        """Алгоритм для заповнення проміжків між подіями миші"""
        steps = int(max(abs(end.x() - start.x()), abs(end.y() - start.y())) // (self.pixel_size / 2))
        steps = max(steps, 1)
        
        for i in range(steps + 1):
            x = start.x() + (end.x() - start.x()) * i / steps
            y = start.y() + (end.y() - start.y()) * i / steps
            self.process_mouse(x, y)

    def process_mouse(self, x_or_pos, y=None):
        # Підтримка двох форматів (координати або об'єкт точки)
        if y is None:
            x, y = x_or_pos.x(), x_or_pos.y()
        else:
            x = x_or_pos

        col = int(x // self.pixel_size)
        row = int(y // self.pixel_size)
        
        if 0 <= row < self.model.height and 0 <= col < self.model.width:
            self.controller.paint_pixel(row, col)

class EditorView(QMainWindow):
    def __init__(self, controller, model):
        super().__init__()
        self.controller = controller
        self.model = model
        self.setWindowTitle("Pixiled PX")
        # Встановлюємо мінімальний розмір вікна
        self.setMinimumSize(600, 700)

        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        main_layout = QVBoxLayout(main_widget)

        # 1. Панель інструментів
        tools_layout = QHBoxLayout()
        btn_pencil = QPushButton("✏ Pencil")
        btn_eraser = QPushButton("🧽 Eraser")
        btn_clear = QPushButton("🗑 Clear")
        btn_save = QPushButton("💾 Save PNG")

        btn_pencil.clicked.connect(lambda: self.controller.set_tool("pencil"))
        btn_eraser.clicked.connect(lambda: self.controller.set_tool("eraser"))
        btn_clear.clicked.connect(self.on_clear_click)
        btn_save.clicked.connect(self.on_save_click)

        for btn in [btn_pencil, btn_eraser, btn_clear, btn_save]:
            tools_layout.addWidget(btn)
        main_layout.addLayout(tools_layout)

        # 2. Палітра кольорів
        palette_layout = QHBoxLayout()
        colors = ["#000000", "#FF0000", "#00FF00", "#0000FF", "#FFFF00", "#FFFFFF"]
        for hex_color in colors:
            btn = QPushButton()
            btn.setFixedSize(35, 35)
            btn.setStyleSheet(f"background-color: {hex_color}; border: 1px solid #333; border-radius: 5px;")
            btn.clicked.connect(lambda checked, c=hex_color: self.controller.set_color(c))
            palette_layout.addWidget(btn)
        palette_layout.addStretch()
        main_layout.addLayout(palette_layout)

        # 3. Область прокрутки для великих холстів
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QScrollArea.Shape.NoFrame) # Прибирає рамку, що їсть місце
        
        self.canvas = PixelCanvas(controller, model)
        scroll.setWidget(self.canvas)
        main_layout.addWidget(scroll)

    def on_clear_click(self):
        self.model.clear()
        self.canvas.update()

    def on_save_click(self):
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Зберегти малюнок", "", "PNG Files (*.png);;All Files (*)"
        )
        if file_path:
            self.controller.save_image(file_path)