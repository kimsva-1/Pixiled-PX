DEFAULT_COLOR = "#FFFFFF"

class CanvasModel:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.pixels = [
            [DEFAULT_COLOR for _ in range(width)]
            for _ in range(height)
        ]

    # Методи для роботи з пікселями
    def set_pixel(self, row, col, color):
        if 0 <= row < self.height and 0 <= col < self.width:
            self.pixels[row][col] = color

    def get_pixel(self, row, col):
        if 0 <= row < self.height and 0 <= col < self.width:
            return self.pixels[row][col]
        return DEFAULT_COLOR

    def clear(self):
        for r in range(self.height):
            for c in range(self.width):
                self.pixels[r][c] = DEFAULT_COLOR