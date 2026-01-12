from coords import Coords

class ubicacion:
    def __init__(self, pueblo: str, provincia: str, coords: Coords):
        self.pueblo = pueblo
        self.provincia = provincia
        self.coords = coords

    def __str__(self):
        return f"ubicacion(pueblo={self.pueblo}, provincia={self.provincia}, coords={self.coords})"
    
    def __eq__(self, value):
        if not isinstance(value, ubicacion):
            return False
        return (self.pueblo == value.pueblo and 
                self.provincia == value.provincia and 
                self.coords == value.coords)
    
    def distancia(self, otra_ubicacion) -> float:
        if not isinstance(otra_ubicacion, ubicacion):
            raise ValueError("El argumento debe ser una instancia de ubicacion")
        
        dx = self.coords.x - otra_ubicacion.coords.x
        dy = self.coords.y - otra_ubicacion.coords.y
        return (dx**2 + dy**2) ** 0.5