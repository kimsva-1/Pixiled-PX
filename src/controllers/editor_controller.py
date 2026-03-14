class EditorController:

    def __init__(self, model):
        self.model = model
        self.current_color = "#000000"
        self.current_tool = "pencil"

    def set_color(self, color):
        self.current_color = color

    def set_tool(self, tool):
        self.current_tool = tool

    def paint_pixel(self, row, col):
        if self.current_tool == "pencil":
            self.model.set_pixel(row, col, self.current_color)

        elif self.current_tool == "eraser":
            self.model.set_pixel(row, col, "#FFFFFF")
