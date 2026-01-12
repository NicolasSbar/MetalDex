# Este es el nuevo objeto.py

from ubicacion import ubicacion
from fecha import Fecha

class Objeto:
    def __init__(self, nombre: str, descripcion: str, ubicacion: ubicacion = None, 
                 fecha_adquisicion: Fecha = None, id: int = None): # <-- ¡CAMBIO!
        self.id = id  # <-- ¡CAMBIO!
        self.nombre = nombre
        self.descripcion = descripcion
        self.ubicacion = ubicacion
        self.fec_ad = fecha_adquisicion

    def __str__(self):
        return (f"Objeto(id={self.id}, nombre={self.nombre}, descripcion={self.descripcion}, " # <-- ¡CAMBIO!
                f"ubicacion={self.ubicacion}, fecha_adquisicion={self.fec_ad})")
    
    def __eq__(self, value):
        if not isinstance(value, Objeto):
            return False
        # El ID es la forma de verdad de comparar
        if self.id is not None and value.id is not None:
            return self.id == value.id
        
        # Si no tienen ID, comparamos por valor (como antes)
        return (self.nombre == value.nombre and 
                self.descripcion == value.descripcion and 
                self.ubicacion == value.ubicacion and 
                self.fec_ad == value.fec_ad)
    
    def mover(self, nueva_ubicacion: ubicacion):
        if not isinstance(nueva_ubicacion, ubicacion):
            raise ValueError("El argumento debe ser una instancia de ubicacion")
        self.ubicacion = nueva_ubicacion

    def tiempo_desde_adquisicion(self, fecha_actual: Fecha) -> int:
        if not isinstance(fecha_actual, Fecha):
            raise ValueError("El argumento debe ser una instancia de Fecha")
        
        delta = fecha_actual.fecha - self.fec_ad.fecha
        return delta.days