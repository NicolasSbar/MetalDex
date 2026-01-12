from datetime import date

class Fecha:
    def __init__(self, dia: int, mes: int, anio: int):
        self.fecha = date(anio, mes, dia)

    def __str__(self):
        return self.fecha.strftime("%d/%m/%Y")
    
    def __eq__(self, value):
        if not isinstance(value, Fecha):
            return False
        return self.fecha == value.fecha
    
    def fecha_actual(self) -> date:
        return date.today()

    