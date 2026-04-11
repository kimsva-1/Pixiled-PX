from PyQt6.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QPushButton
from PyQt6.QtGui import QPainter, QColor, QPen
from PyQt6.QtCore import Qt

PIXEL_SIZE = 25  # Розмір пікселя на екрані

class PixelCanvas(QWidget):
    def __init__(self, controller, model):
        super().__init__()
        self.controller = controller
        self.model = model
        # Встановлюємо жорсткий розмір віджета залежно від моделі
        self.setFixedSize(self.model.width * PIXEL_SIZE, self.model.height * PIXEL_SIZE)

    def paintEvent(self, event):
        """Метод перемальовування всього полотна"""
        painter = QPainter(self)
        for r in range(self.model.height):
            for c in range(self.model.width):
                # Отримуємо колір з моделі
                color_hex = self.model.get_pixel(r, c)
                painter.fillRect(c * PIXEL_SIZE, r * PIXEL_SIZE, PIXEL_SIZE, PIXEL_SIZE, QColor(color_hex))
                
                # Малюємо сітку
                painter.setPen(QPen(QColor("#E0E0E0"), 1))
                painter.drawRect(c * PIXEL_SIZE, r * PIXEL_SIZE, PIXEL_SIZE, PIXEL_SIZE)

    def mousePressEvent(self, event):
        self.process_mouse(event)

    def mouseMoveEvent(self, event):
        self.process_mouse(event)

    def process_mouse(self, event):
        # Вираховуємо координати кліку в індекси масиву
        col = int(event.position().x() // PIXEL_SIZE)
        row = int(event.position().y() // PIXEL_SIZE)
        
        if 0 <= row < self.model.height and 0 <= col < self.model.width:
            self.controller.paint_pixel(row, col)
            self.update() # Запит на перемальовування (викличе paintEvent)

class EditorView(QMainWindow):
    def __init__(self, controller, model):
        super().__init__()
        self.controller = controller
        self.model = model
        self.setWindowTitle("Pixiled PX - PyQt Edition")

        # Головний віджет
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        main_layout = QVBoxLayout(main_widget)

        # 1. Панель інструментів (Pencil, Eraser, Clear)
        tools_layout = QHBoxLayout()
        btn_pencil = QPushButton("✏ Pencil")
        btn_eraser = QPushButton("🧽 Eraser")
        btn_clear = QPushButton("🗑 Clear")

        btn_pencil.clicked.connect(lambda: self.controller.set_tool("pencil"))
        btn_eraser.clicked.connect(lambda: self.controller.set_tool("eraser"))
        btn_clear.clicked.connect(self.on_clear_click)

        tools_layout.addWidget(btn_pencil)
        tools_layout.addWidget(btn_eraser)
        tools_layout.addWidget(btn_clear)
        main_layout.addLayout(tools_layout)

        # 2. Палітра кольорів
        palette_layout = QHBoxLayout()
        colors = ["#000000", "#FF0000", "#00FF00", "#0000FF", "#FFFF00", "#FFFFFF"]
        
        for hex_color in colors:
            btn = QPushButton()
            btn.setFixedSize(35, 35)
            btn.setStyleSheet(f"background-color: {hex_color}; border: 1px solid #333; border-radius: 5px;")
            # Використовуємо замикання c=hex_color, щоб зберегти значення кольору
            btn.clicked.connect(lambda checked, c=hex_color: self.controller.set_color(c))
            palette_layout.addWidget(btn)
        
        palette_layout.addStretch() # Відсуваємо палітру вліво
        main_layout.addLayout(palette_layout)

        # 3. Полотно (Canvas)
        self.canvas = PixelCanvas(controller, model)
        main_layout.addWidget(self.canvas, alignment=Qt.AlignmentFlag.AlignCenter)
        
        # Відступи
        main_layout.addStretch()

    def on_clear_click(self):
        #Очищення моделі та оновлення екрана
        self.model.clear()
        self.canvas.update()