from PyQt6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                            QPushButton, QFileDialog, QDialog, QLabel, 
                            QSpinBox, QScrollArea, QFrame, QColorDialog, QSlider)
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
        self.resize(700, 650)
        
        central = QWidget()
        self.setCentralWidget(central)
        
        self.root_layout = QVBoxLayout(central)
        
        # 1. Палітра зверху
        self.palette_layout = QHBoxLayout()
        self.palette_layout.setAlignment(Qt.AlignmentFlag.AlignLeft)
        self.root_layout.addLayout(self.palette_layout)
        
        # 2. Робоча область
        self.work_area = QHBoxLayout()
        self.root_layout.addLayout(self.work_area)
        
        # Панель інструментів (вертикальна)
        self.tools_layout = QVBoxLayout()
        self.tools_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.work_area.addLayout(self.tools_layout)
        
        # Холст
        self.scroll = QScrollArea()
        self.scroll.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.scroll.setStyleSheet("background-color: #2b2b2b; border: 1px solid #111;")
        self.work_area.addWidget(self.scroll)
        
        QTimer.singleShot(100, self.open_new_project_dialog)

    def toggle_on_top(self, checked):
        """Зміна режиму закріплення вікна поверх інших"""
        if checked:
            self.setWindowFlags(self.windowFlags() | Qt.WindowType.WindowStaysOnTopHint)
        else:
            self.setWindowFlags(self.windowFlags() & ~Qt.WindowType.WindowStaysOnTopHint)
        self.show()

    def change_opacity(self, value):
        """Метод зміни прозорості всього вікна (value йде від 20 до 100)"""
        opacity = value / 100.0
        self.setWindowOpacity(opacity)

    def open_new_project_dialog(self):
        dialog = NewCanvasDialog(self)
        if dialog.exec():
            w, h = dialog.get_values()
            self.setup_editor(w, h)

    def setup_editor(self, w, h):
        self.model = CanvasModel(w, h)
        self.controller = EditorController(self.model)
        
        # Очищуємо попередні віджети
        while self.tools_layout.count():
            item = self.tools_layout.takeAt(0)
            if item.widget(): item.widget().deleteLater()
            elif item.spacerItem(): self.tools_layout.removeItem(item)

        while self.palette_layout.count():
            item = self.palette_layout.takeAt(0)
            if item.widget(): item.widget().deleteLater()

        # --- Інструменти зверху ---
        tools = [("✏", "pencil", "Кисть"), ("🧽", "eraser", "Ластик")]
        for icon, tool_id, tip in tools:
            btn = QPushButton(icon)
            btn.setFixedSize(50, 50)
            btn.setToolTip(tip)
            btn.clicked.connect(lambda ch, t=tool_id: self.controller.set_tool(t))
            self.tools_layout.addWidget(btn)
        
        # Кнопка Clear
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

        # Пружина штовхає наступні кнопки в самий низ
        self.tools_layout.addStretch()

        # --- Повзунок прозорості вікна ---
        opacity_label = QLabel("Прозорість")
        opacity_label.setStyleSheet("color: #aaa; font-size: 10px;")
        opacity_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.tools_layout.addWidget(opacity_label)

        self.opacity_slider = QSlider(Qt.Orientation.Horizontal)
        self.opacity_slider.setRange(20, 100) 
        self.opacity_slider.setValue(100)     
        self.opacity_slider.setFixedWidth(50) 
        self.opacity_slider.setToolTip("Регулювання прозорості вікна")
        self.opacity_slider.valueChanged.connect(self.change_opacity)
        self.tools_layout.addWidget(self.opacity_slider)

        # --- Кнопка-Checkbox для закріплення вікна ---
        self.pin_checkbox = QPushButton("📌")
        self.pin_checkbox.setFixedSize(20, 20)
        self.pin_checkbox.setCheckable(True)
        self.pin_checkbox.setToolTip("Закріпити поверх усіх вікон")
        self.pin_checkbox.setStyleSheet("""
            QPushButton { background-color: #f0f0f0; border: 1px solid #999; border-radius: 5px; }
            QPushButton:checked { background-color: #aaffaa; border: 2px solid #00aa00; }
        """)
        self.pin_checkbox.toggled.connect(self.toggle_on_top)
        self.tools_layout.addWidget(self.pin_checkbox)

        # --- Палітра ---
        colors = ["#000000", "#FF0000", "#00FF00", "#0000FF", "#FFFF00", "#FFFFFF", "#FF00FF", "#00FFFF"]
        for c in colors:
            btn = QPushButton()
            btn.setFixedSize(30, 30)
            btn.setStyleSheet(f"background-color: {c}; border: 2px solid #555;")
            btn.clicked.connect(lambda ch, col=c: self.controller.set_color(col))
            self.palette_layout.addWidget(btn)

        # --- Кнопка для власного кольору ---
        self.custom_color_btn = QPushButton("🌈")
        self.custom_color_btn.setFixedSize(30, 30)
        self.custom_color_btn.setToolTip("Обрати свій колір")
        self.custom_color_btn.setStyleSheet("background-color: #e0e0e0; border: 2px dashed #555;")
        self.custom_color_btn.clicked.connect(self.open_color_picker)
        self.palette_layout.addWidget(self.custom_color_btn)

        self.canvas = PixelCanvas(self.controller, self.model)
        self.scroll.setWidget(self.canvas)

    def open_color_picker(self):
        # Відкриваємо стандартне вікно вибору кольору PyQt
        color = QColorDialog.getColor()
        
        # Якщо користувач вибрав колір і натиснув "ОК" (а не "Скасувати")
        if color.isValid():
            hex_color = color.name() # Перетворюємо колір у формат "#RRGGBB"
            self.controller.set_color(hex_color)
            
            # Візуально змінюємо фон кнопки на обраний колір, щоб було видно, що зараз активно
            self.custom_color_btn.setStyleSheet(f"background-color: {hex_color}; border: 2px solid #fff;")

    def on_clear(self):
        self.model.clear()
        self.canvas.update()

    def on_save(self):
        path, selected_filter = QFileDialog.getSaveFileName(
            self, "Зберегти малюнок", "", 
            "PNG Image (*.png);;JPEG Image (*.jpg)"
        )
        if path:
            if not path.endswith(('.png', '.jpg', '.jpeg')):
                ext = ".png" if "PNG" in selected_filter else ".jpg"
                path += ext
            self.controller.save_image(path)