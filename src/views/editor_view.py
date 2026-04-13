from PyQt6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                            QPushButton, QFileDialog, QDialog, QLabel, 
                            QSpinBox, QScrollArea, QFrame)
from PyQt6.QtGui import QPainter, QColor, QPen
from PyQt6.QtCore import Qt, QPointF, QTimer
from models.canvas_model import CanvasModel
from controllers.editor_controller import EditorController

class NewCanvasDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Новий проект")
        layout = QVBoxLayout(self)
        
        layout.addWidget(QLabel("Ширина (8-128):"))
        self.w_input = QSpinBox()
        self.w_input.setRange(8, 128)
        self.w_input.setValue(32)
        layout.addWidget(self.w_input)

        layout.addWidget(QLabel("Висота (8-128):"))
        self.h_input = QSpinBox()
        self.h_input.setRange(8, 128)
        self.h_input.setValue(32)
        layout.addWidget(self.h_input)

        btn = QPushButton("Створити")
        btn.clicked.connect(self.accept)
        layout.addWidget(btn)

    def get_values(self):
        return self.w_input.value(), self.h_input.value()

class PixelCanvas(QWidget):
    def __init__(self, controller, model):
        super().__init__()
        self.controller = controller
        self.model = model
        self.last_pos = None
        
        max_dim = max(model.width, model.height)
        self.pixel_size = max(4, min(25, 600 // max_dim))
        self.setFixedSize(model.width * self.pixel_size, model.height * self.pixel_size)

    def paintEvent(self, event):
        painter = QPainter(self)
        ps = self.pixel_size
        for r in range(self.model.height):
            for c in range(self.model.width):
                color = self.model.get_pixel(r, c)
                painter.fillRect(c * ps, r * ps, ps, ps, QColor(color))
                if ps > 5:
                    painter.setPen(QPen(QColor("#D0D0D0"), 1))
                    painter.drawRect(c * ps, r * ps, ps, ps)

    def mousePressEvent(self, event):
        self.last_pos = event.position()
        self.paint_at(self.last_pos)

    def mouseMoveEvent(self, event):
        curr_pos = event.position()
        if self.last_pos:
            self.draw_line(self.last_pos, curr_pos)
        self.last_pos = curr_pos

    def mouseReleaseEvent(self, event):
        self.last_pos = None

    def draw_line(self, start, end):
        dist = max(abs(end.x() - start.x()), abs(end.y() - start.y()))
        steps = int(dist // (self.pixel_size / 2)) + 1
        for i in range(steps):
            ix = start.x() + (end.x() - start.x()) * i / steps
            iy = start.y() + (end.y() - start.y()) * i / steps
            self.paint_at(QPointF(ix, iy))

    def paint_at(self, pos):
        col = int(pos.x() // self.pixel_size)
        row = int(pos.y() // self.pixel_size)
        if 0 <= row < self.model.height and 0 <= col < self.model.width:
            self.controller.paint_pixel(row, col)
            self.update()

class EditorView(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Pixiled PX")
        self.resize(1100, 850)
        
        central = QWidget()
        self.setCentralWidget(central)
        
        # Головний вертикальний лейаут (Палітра зверху, під нею все інше)
        self.root_layout = QVBoxLayout(central)
        
        # 1. Палітра (Зверху, горизонтально по лівому краю)
        self.palette_layout = QHBoxLayout()
        self.palette_layout.setAlignment(Qt.AlignmentFlag.AlignLeft)
        self.root_layout.addLayout(self.palette_layout)
        
        # 2. Основна робоча область (Інструменти зліва, Холст справа)
        self.work_area = QHBoxLayout()
        self.root_layout.addLayout(self.work_area)
        
        # Панель інструментів (Вертикально)
        self.tools_layout = QVBoxLayout()
        self.tools_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.work_area.addLayout(self.tools_layout)
        
        # Холст
        self.scroll = QScrollArea()
        self.scroll.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.scroll.setStyleSheet("background-color: #2b2b2b; border: 1px solid #111;")
        self.work_area.addWidget(self.scroll)
        
        QTimer.singleShot(100, self.open_new_project_dialog)

    def open_new_project_dialog(self):
        dialog = NewCanvasDialog(self)
        if dialog.exec():
            w, h = dialog.get_values()
            self.setup_editor(w, h)

    def setup_editor(self, w, h):
        self.model = CanvasModel(w, h)
        self.controller = EditorController(self.model)
        
        # Очищуємо попередні віджети
        for layout in [self.tools_layout, self.palette_layout]:
            while layout.count():
                item = layout.takeAt(0)
                if item.widget(): item.widget().deleteLater()

        # --- Інструменти (Вертикально, квадратні) ---
        tools = [("✏", "pencil", "Кисть"), ("🧽", "eraser", "Ластик")]
        for icon, tool_id, tip in tools:
            btn = QPushButton(icon)
            btn.setFixedSize(50, 50)  # Робимо квадратними
            btn.setToolTip(tip)
            btn.clicked.connect(lambda ch, t=tool_id: self.controller.set_tool(t))
            self.tools_layout.addWidget(btn)
        
        # Кнопка Clear (Повернули)
        btn_clear = QPushButton("🗑")
        btn_clear.setFixedSize(50, 50)
        btn_clear.setToolTip("Очистити")
        btn_clear.clicked.connect(self.on_clear)
        self.tools_layout.addWidget(btn_clear)
        
        # Кнопка Save
        btn_save = QPushButton("💾")
        btn_save.setFixedSize(50, 50)
        btn_save.setToolTip("Зберегти")
        btn_save.clicked.connect(self.on_save)
        self.tools_layout.addWidget(btn_save)

        # --- Палітра (Горизонтально) ---
        colors = ["#000000", "#FF0000", "#00FF00", "#0000FF", "#FFFF00", "#FFFFFF", "#FF00FF", "#00FFFF"]
        for c in colors:
            btn = QPushButton()
            btn.setFixedSize(30, 30)
            btn.setStyleSheet(f"background-color: {c}; border: 2px solid #555;")
            btn.clicked.connect(lambda ch, col=c: self.controller.set_color(col))
            self.palette_layout.addWidget(btn)

        self.canvas = PixelCanvas(self.controller, self.model)
        self.scroll.setWidget(self.canvas)

    def on_clear(self):
        self.model.clear()
        self.canvas.update()

    def on_save(self):
        # Додано вибір PNG або JPG
        path, selected_filter = QFileDialog.getSaveFileName(
            self, "Зберегти малюнок", "", 
            "PNG Image (*.png);;JPEG Image (*.jpg)"
        )
        if path:
            # Якщо користувач забув дописати розширення, додаємо його з фільтра
            if not path.endswith(('.png', '.jpg', '.jpeg')):
                ext = ".png" if "PNG" in selected_filter else ".jpg"
                path += ext
            self.controller.save_image(path)