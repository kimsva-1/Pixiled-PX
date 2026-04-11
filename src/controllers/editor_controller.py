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
