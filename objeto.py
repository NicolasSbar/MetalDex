from ubicacion import ubicacion
from fecha import Fecha

class Objeto:
    def __init__(self, nombre: str, descripcion: str, ubicacion: ubicacion = None, 
                 fecha_adquisicion: Fecha = None, id: int = None):
        self.id = id
        self.nombre = nombre
        self.descripcion = descripcion
        self.ubicacion = ubicacion
        self.fec_ad = fecha_adquisicion

    def __str__(self):
        return (f"Objeto(id={self.id}, nombre={self.nombre}, descripcion={self.descripcion}, "
                f"ubicacion={self.ubicacion}, fecha_adquisicion={self.fec_ad})")
    
    def __eq__(self, value):
        if not isinstance(value, Objeto):
            return False
        if self.id is not None and value.id is not None:
            return self.id == value.id
        
        return (self.nombre == value.nombre and 
                self.descripcion == value.descripcion and 
                self.ubicacion == value.ubicacion and 
                self.fec_ad == value.fec_ad)