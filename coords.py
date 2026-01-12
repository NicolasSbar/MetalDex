class Coords:
    def __init__(self, x: float, y: float):
        self.x = x
        self.y = y
    
    def __str__(self):
        return f"coords(x={self.x}, y={self.y})"
    
    def __eq__(self, value):
        if not isinstance(value, Coords):
            return False
        return self.x == value.x and self.y == value.y