DEFAULT_COLOR = "#FFFFFF"

class CanvasModel:

    def __init__(self, width, height):
        self.width = width
        self.height = height

        self.pixels = [
            [DEFAULT_COLOR for _ in range(width)]
            for _ in range(height)
        ]

    def set_pixel(self, row, col, color):
        self.pixels[row][col] = color

    def get_pixel(self, row, col):
        return self.pixels[row][col]

    def clear(self):
        for r in range(self.height):
            for c in range(self.width):
                self.pixels[r][c] = DEFAULT_COLOR