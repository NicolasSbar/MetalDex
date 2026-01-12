import folium
import webbrowser
import os
import base64
from io import BytesIO
from PIL import Image

from hallazgos_admin import HallazgosAdmin
from objeto import Objeto

class MapaHallazgos:
    """
    Genera un mapa interactivo HTML con marcadores y vista satelital.
    """

    def __init__(self, admin: HallazgosAdmin):
        if not isinstance(admin, HallazgosAdmin):
            raise ValueError("Se necesita una instancia de HallazgosAdmin")
        
        self.admin = admin
        self.mapa = None

    def _calcular_centro(self) -> list[float]:
        if not self.admin.hallazgos:
            return [-34.60, -58.38]

        hallazgos_con_coords = [
            h for h in self.admin.hallazgos 
            if h.ubicacion is not None and h.ubicacion.coords is not None
        ]
        
        if not hallazgos_con_coords:
             return [-34.60, -58.38]

        lat_promedio = sum([h.ubicacion.coords.y for h in hallazgos_con_coords]) / len(hallazgos_con_coords)
        lon_promedio = sum([h.ubicacion.coords.x for h in hallazgos_con_coords]) / len(hallazgos_con_coords)
        
        return [lat_promedio, lon_promedio]

    def _codificar_imagen_base64(self, ruta_imagen: str) -> str:
        try:
            if not os.path.exists(ruta_imagen):
                return None
            
            img = Image.open(ruta_imagen)
            img.thumbnail((200, 200))
            
            buffer = BytesIO()
            img.save(buffer, format="JPEG")
            img_str = base64.b64encode(buffer.getvalue()).decode("utf-8")
            return f"data:image/jpeg;base64,{img_str}"
        except Exception as e:
            print(f"Error codificando imagen {ruta_imagen}: {e}")
            return None

    def generar_y_guardar_mapa(self, nombre_archivo: str = "mapa_hallazgos.html", abrir_automaticamente: bool = True):
        centro_mapa = self._calcular_centro()
        
        self.mapa = folium.Map(
            location=centro_mapa, 
            zoom_start=13,
            tiles='https://mt0.google.com/vt/lyrs=s,h&hl=en&x={x}&y={y}&z={z}&s=Ga',
            attr='Google Maps'
        )
        
        count = 0
        skipped = 0
        
        for hallazgo in self.admin.hallazgos:
            try:
                if (hallazgo.ubicacion and 
                    hallazgo.ubicacion.coords and 
                    hallazgo.ubicacion.coords.x is not None and 
                    hallazgo.ubicacion.coords.y is not None):
                    
                    html_content = f"<b>{hallazgo.nombre}</b><br>{hallazgo.descripcion}<br>"
                    
                    if hallazgo.imagen_preview:
                         base64_img = self._codificar_imagen_base64(hallazgo.imagen_preview)
                         if base64_img:
                             html_content += f'<br><img src="{base64_img}" width="150"><br>'
                    
                    if hallazgo.fec_ad:
                        html_content += f"<i>{hallazgo.fec_ad}</i>"

                    tooltip_html = f"{hallazgo.nombre}"

                    popup_html = folium.Html(html_content, script=True)

                    folium.Marker(
                        location=[hallazgo.ubicacion.coords.y, hallazgo.ubicacion.coords.x],
                        popup=folium.Popup(popup_html, max_width=300),
                        tooltip=folium.Tooltip(tooltip_html)
                    ).add_to(self.mapa)
                    
                    count += 1
                else:
                    skipped += 1
                
            except Exception as e:
                print(f"Error agregando marcador para {hallazgo.descripcion}: {e}")
                skipped += 1

        try:
            self.mapa.save(nombre_archivo)
            print(f"Mapa generado exitosamente en: {nombre_archivo}")

            if abrir_automaticamente:
                try:
                    url = 'file://' + os.path.realpath(nombre_archivo)
                    webbrowser.open(url)
                except Exception as e:
                    print(f"No se pudo abrir el navegador automáticamente: {e}")

        except IOError as e:
            print(f"Error al guardar el archivo del mapa: {e}")
            raise