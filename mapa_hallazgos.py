# Este es mapa_hallazgos.py (Versión 2.0 con Satélite y Previews)

import folium
import webbrowser
import os
import base64
from io import BytesIO
from PIL import Image

from hallazgos_admin import HallazgosAdmin # Necesitamos esto para saber qué tipo de admin recibimos
from objeto import Objeto # Y esto para chequear la lista

class MapaHallazgos:
    """
    Se encarga de generar un mapa interactivo (HTML)
    con los marcadores de los hallazgos.
    """

    def __init__(self, admin: HallazgosAdmin):
        if not isinstance(admin, HallazgosAdmin):
            raise ValueError("Se necesita una instancia de HallazgosAdmin")
        
        self.admin = admin
        self.mapa = None

    # --- (Esta función _calcular_centro no cambia) ---
    def _calcular_centro(self) -> list[float]:
        if not self.admin.hallazgos:
            return [-34.60, -58.38]

        # Filtramos solo los que tienen coordenadas
        hallazgos_con_coords = [
            h for h in self.admin.hallazgos 
            if h.ubicacion is not None and h.ubicacion.coords is not None
        ]
        
        if not hallazgos_con_coords:
             print("Advertencia: No hay hallazgos con coordenadas válidas para calcular el centro. Usando centro por defecto.")
             return [-34.60, -58.38] # Default
        else:
            total_y = sum(h.ubicacion.coords.y for h in hallazgos_con_coords)
            total_x = sum(h.ubicacion.coords.x for h in hallazgos_con_coords)
            n = len(hallazgos_con_coords)
            return [total_y / n, total_x / n]

    # --- ¡FUNCIÓN GENERAR_Y_GUARDAR_MAPA MODIFICADA! ---
    def generar_y_guardar_mapa(self, nombre_archivo: str = "mapa_hallazgos.html", abrir_automaticamente: bool = True):
        """
        Crea el mapa con todos los marcadores y lo guarda como un archivo HTML.
        """
        
        centro_mapa = self._calcular_centro()
        
        # --- ¡CAMBIO 1: Mapa Satelital! ---
        # Agregamos tiles='Esri_WorldImagery'
    def generar_y_guardar_mapa(self, nombre_archivo: str = "mapa_hallazgos.html", abrir_automaticamente: bool = True):
        centro_mapa = self._calcular_centro()
        
        # --- ¡CAMBIO! Satélite forzado desde el inicio ---
        self.mapa = folium.Map(
            location=centro_mapa, 
            zoom_start=13,
            # Ponemos la URL de Google DIRECTAMENTE aquí como 'tiles'
            tiles='https://mt0.google.com/vt/lyrs=s,h&hl=en&x={x}&y={y}&z={z}&s=Ga',
            attr='Google Maps'
)

        
        print(f"\nGenerando mapa centrado en {centro_mapa}...")

        count = 0
        skipped = 0
        for hallazgo in self.admin.hallazgos:
            try:
                # Chequeamos si hay coordenadas (igual que antes)
                if hallazgo.ubicacion is not None and hallazgo.ubicacion.coords is not None:
                    coords_marcador = [
                        hallazgo.ubicacion.coords.y, 
                        hallazgo.ubicacion.coords.x
                    ]
                    
                    # Popup (igual que antes)
                    lugar_texto = f"{hallazgo.ubicacion.pueblo}, {hallazgo.ubicacion.provincia}" if hallazgo.ubicacion.pueblo else "Lugar Desconocido"
                    fecha_texto = str(hallazgo.fec_ad) if hallazgo.fec_ad else "?"
                    popup_html = f"""
                    <b>{hallazgo.nombre}</b><br> 
                    <i>{hallazgo.descripcion}</i><br><br>
                    Lugar: {lugar_texto}<br>
                    Fecha: {fecha_texto}
                    """
                    
                    # --- ¡CAMBIO 2: Preview en Tooltip! ---
                    tooltip_html = f"<b>{hallazgo.nombre}</b><br>{hallazgo.descripcion}" # Default por si no hay foto
                    
                    if hallazgo.imagen_preview and os.path.exists(hallazgo.imagen_preview):
                        try:
                            # 1. Abrimos la imagen con Pillow
                            img = Image.open(hallazgo.imagen_preview)
                            # 2. La achicamos (si no es enorme)
                            img.thumbnail((150, 150))
                            # 3. La guardamos en memoria
                            buffer = BytesIO()
                            img.save(buffer, format="JPEG")
                            # 4. La codificamos en Base64
                            img_base64 = base64.b64encode(buffer.getvalue()).decode()
                            
                            # 5. Creamos el HTML para el tooltip
                            tooltip_html = f'''
                            <div>
                                <img src="data:image/jpeg;base64,{img_base64}" width="150" alt="Preview"><br>
                                <b>{hallazgo.nombre}</b><br>{hallazgo.descripcion}
                            </div>
                            '''
                        except Exception as e:
                            print(f"No se pudo encodear la imagen {hallazgo.imagen_preview}: {e}")
                            # Si falla, usamos el tooltip de texto
                    
                    # --- FIN CAMBIO 2 ---
                    
                    folium.Marker(
                        location=coords_marcador,
                        popup=folium.Popup(popup_html, max_width=300),
                        # Usamos folium.Tooltip para que renderice el HTML
                        tooltip=folium.Tooltip(tooltip_html)
                    ).add_to(self.mapa)
                    
                    count += 1
                else:
                    skipped += 1
                    # (Ya no imprimimos la advertencia, para no llenar la consola)
                    # print(f"Advertencia: Omitiendo '{hallazgo.nombre}' del mapa por falta de coordenadas.")
                
            except Exception as e:
                print(f"Error agregando marcador para {hallazgo.descripcion}: {e}")
                skipped += 1

        # 3. Guardar el mapa (Corregido, sin el bloque duplicado)
        try:
            self.mapa.save(nombre_archivo)
            mensaje_final = f"¡Mapa guardado como '{nombre_archivo}'! ({count} marcadores)"
            if skipped > 0:
                mensaje_final += f" - Se omitieron {skipped} por falta de coordenadas."
            print(mensaje_final)

            if abrir_automaticamente:
                try:
                    url = 'file://' + os.path.realpath(nombre_archivo)
                    webbrowser.open(url)
                except Exception as e:
                    print(f"No se pudo abrir el navegador automáticamente: {e}")

        except IOError as e:
            print(f"Error al guardar el archivo del mapa: {e}")