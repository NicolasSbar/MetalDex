# Este es app.py (Versión 5.0 con Map Picker)

import customtkinter as ctk
import datetime 
import tkinter.messagebox
import os 
import sys # <-- Importante para resource_path
import ctypes # <-- ¡NUEVO! Para el icono de la barra de tareas
from PIL import Image 
from unidecode import unidecode

# --- Importamos toda nuestra lógica ---
from hallazgos_admin import HallazgosAdmin
from mapa_hallazgos import MapaHallazgos
from coords import Coords       
from ubicacion import ubicacion
from fecha import Fecha
from objeto import Objeto
from edit_window import EditWindow
from image_viewer import ImageViewer
from map_picker_window import MapPickerWindow

# --- Configuración de apariencia ---
ctk.set_appearance_mode("dark") 
ctk.set_default_color_theme("blue")

# --- Función Helper ---
def resource_path(relative_path):
    if getattr(sys, 'frozen', False):
        application_path = os.path.dirname(sys.executable)
    else:
        application_path = os.path.abspath(".")
    return os.path.join(application_path, relative_path)


class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        
        # --- ¡CORRECCIÓN DE ÍCONO BARRA DE TAREAS! ---
        # Esto le dice a Windows: "Soy una app independiente, no soy Python genérico"
        myappid = 'metaldex.app.1.0' 
        try:
            ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)
        except Exception:
            pass
        # ---------------------------------------------

        self.title("MetalDex - Registro de hallazgos")
        self.geometry("1100x600")
        
        # --- ¡PONER EL ÍCONO EN LA VENTANA! ---
        try:
            icon_path = resource_path("icon.ico")
            self.iconbitmap(icon_path)
        except Exception as e:
            print(f"No se pudo cargar el icono de la ventana: {e}")

        try:
            self.admin = HallazgosAdmin("mis_hallazgos.csv")
            print(f"Admin cargado: {len(self.admin.hallazgos)} hallazgos encontrados.")
        except Exception as e:
            print(f"Error fatal al cargar el admin: {e}")
            self.admin = None 
        
        self.variable_orden = ctk.StringVar(value="fecha_reciente")
        
        self.grid_columnconfigure(0, weight=4)
        self.grid_columnconfigure(1, weight=6)
        self.grid_rowconfigure(0, weight=1)

        # (a) Frame Izquierdo (Lista)
        # ... (Todo el frame izquierdo: botones de orden, búsqueda, lista, etc. 
        # ... queda EXACTAMENTE IGUAL) ...
        self.frame_izquierda = ctk.CTkFrame(master=self, corner_radius=10)
        self.frame_izquierda.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
        label_izq = ctk.CTkLabel(master=self.frame_izquierda, text="Mis hallazgos", font=ctk.CTkFont(size=20, weight="bold"))
        label_izq.pack(pady=10, padx=10)
        self.boton_mapa = ctk.CTkButton(
            master=self.frame_izquierda,
            text="🗺️ Generar mapa de hallazgos",
            command=self._on_generar_mapa_click
        )
        self.boton_mapa.pack(fill="x", padx=10, pady=(0, 10))
        orden_frame = ctk.CTkFrame(master=self.frame_izquierda, fg_color="transparent")
        orden_frame.pack(fill="x", padx=10, pady=0)
        orden_frame.grid_columnconfigure((0, 1, 2, 3), weight=1)
        ctk.CTkRadioButton(
            master=orden_frame, 
            text="Recientes", 
            variable=self.variable_orden, 
            value="fecha_reciente",
            command=self._on_orden_change
        ).grid(row=0, column=0, sticky="w")
        ctk.CTkRadioButton(
            master=orden_frame, 
            text="Antiguos", 
            variable=self.variable_orden, 
            value="fecha_antigua",
            command=self._on_orden_change
        ).grid(row=0, column=1, sticky="w")
        ctk.CTkRadioButton(
            master=orden_frame, 
            text="Alfabético (A-Z)", 
            variable=self.variable_orden, 
            value="alfabetico",
            command=self._on_orden_change
        ).grid(row=0, column=2, sticky="w")
        ctk.CTkRadioButton(
            master=orden_frame, 
            text="Lugar (A-Z)", 
            variable=self.variable_orden, 
            value="lugar", 
            command=self._on_orden_change
        ).grid(row=0, column=3, sticky="w")
        self.entry_busqueda = ctk.CTkEntry(
            master=self.frame_izquierda,
            placeholder_text="🔎 Buscar por nombre o descripción..."
        )
        self.entry_busqueda.pack(fill="x", padx=10, pady=10)
        self.entry_busqueda.bind("<KeyRelease>", self._on_busqueda_change)
        self.scrollable_frame_lista = ctk.CTkScrollableFrame(master=self.frame_izquierda, corner_radius=5)
        self.scrollable_frame_lista.pack(fill="both", expand=True, padx=10, pady=(0, 10))


        # (b) Frame Derecho (Formulario de Agregar)
        self.frame_derecha = ctk.CTkFrame(master=self, corner_radius=10)
        self.frame_derecha.grid(row=0, column=1, padx=(0, 10), pady=10, sticky="nsew")
        label_der = ctk.CTkLabel(master=self.frame_derecha, text="Agregar nuevo hallazgo", font=ctk.CTkFont(size=20, weight="bold"))
        label_der.pack(pady=10, padx=10)
        
        form_frame = ctk.CTkFrame(master=self.frame_derecha, fg_color="transparent")
        form_frame.pack(fill="x", padx=20, pady=10)
        
        ctk.CTkLabel(master=form_frame, text="Nombre / ID (*):").pack(anchor="w")
        self.entry_nombre = ctk.CTkEntry(master=form_frame, placeholder_text="Ej: 'hebilla_01'")
        self.entry_nombre.pack(fill="x", pady=(0, 10))
        
        ctk.CTkLabel(master=form_frame, text="Descripción (*):").pack(anchor="w")
        self.entry_desc = ctk.CTkEntry(master=form_frame, placeholder_text="Ej: 'Hebilla de cinto, bronce'")
        self.entry_desc.pack(fill="x", pady=(0, 10))
        
        ctk.CTkLabel(master=form_frame, text="Pueblo / Paraje:").pack(anchor="w")
        self.entry_pueblo = ctk.CTkEntry(master=form_frame, placeholder_text="Ej: 'La Chamarrita'")
        self.entry_pueblo.pack(fill="x", pady=(0, 10))
        
        ctk.CTkLabel(master=form_frame, text="Provincia:").pack(anchor="w")
        self.entry_provincia = ctk.CTkEntry(master=form_frame, placeholder_text="Ej: 'Entre Ríos'")
        self.entry_provincia.pack(fill="x", pady=(0, 10))

        # --- ¡CAMBIO! Frame de Coordenadas ---
        coords_frame = ctk.CTkFrame(master=form_frame, fg_color="transparent")
        coords_frame.pack(fill="x", pady=(0, 10))
        # Hacemos 3 columnas: Lat, Lon, Botón
        coords_frame.grid_columnconfigure((0, 1), weight=1)
        coords_frame.grid_columnconfigure(2, weight=0) # Columna fija para el botón

        # Latitud (Y)
        ctk.CTkLabel(master=coords_frame, text="Coord Y (Lat):").grid(row=0, column=0, sticky="w")
        self.entry_coord_y = ctk.CTkEntry(master=coords_frame, placeholder_text="-31.4116")
        self.entry_coord_y.grid(row=1, column=0, sticky="ew", padx=(0, 5))

        # Longitud (X)
        ctk.CTkLabel(master=coords_frame, text="Coord X (Lon):").grid(row=0, column=1, sticky="w", padx=(5, 0))
        self.entry_coord_x = ctk.CTkEntry(master=coords_frame, placeholder_text="-58.0163")
        self.entry_coord_x.grid(row=1, column=1, sticky="ew", padx=(5, 0))

        # --- ¡NUEVO! Botón para abrir el mapa ---
        self.boton_abrir_mapa = ctk.CTkButton(
            master=coords_frame,
            text="🗺️", # Un emoji simple
            width=40,
            command=self._on_abrir_mapa_click
        )
        # Lo ponemos al lado de los campos de coords
        self.boton_abrir_mapa.grid(row=1, column=2, sticky="w", padx=(5, 0))
        # --- FIN CAMBIO ---

        # ... (Frame de Fecha, Botón de Guardar, Label de Mensaje ... 
        # ... quedan EXACTAMENTE IGUAL) ...
        fecha_frame = ctk.CTkFrame(master=form_frame, fg_color="transparent")
        fecha_frame.pack(fill="x", pady=10)
        fecha_frame.grid_columnconfigure((0, 1, 2), weight=1)
        hoy = datetime.date.today()
        ctk.CTkLabel(master=fecha_frame, text="Día:").grid(row=0, column=0, sticky="w")
        self.entry_dia = ctk.CTkEntry(master=fecha_frame)
        self.entry_dia.insert(0, str(hoy.day))
        self.entry_dia.grid(row=1, column=0, sticky="ew", padx=(0, 5))
        ctk.CTkLabel(master=fecha_frame, text="Mes:").grid(row=0, column=1, sticky="w", padx=5)
        self.entry_mes = ctk.CTkEntry(master=fecha_frame)
        self.entry_mes.insert(0, str(hoy.month))
        self.entry_mes.grid(row=1, column=1, sticky="ew", padx=5)
        ctk.CTkLabel(master=fecha_frame, text="Año:").grid(row=0, column=2, sticky="w", padx=5)
        self.entry_anio = ctk.CTkEntry(master=fecha_frame)
        self.entry_anio.insert(0, str(hoy.year))
        self.entry_anio.grid(row=1, column=2, sticky="ew", padx=(5, 0))
        
        self.boton_guardar = ctk.CTkButton(master=self.frame_derecha, text="💾 Guardar hallazgo", font=ctk.CTkFont(size=16, weight="bold"), command=self._on_guardar_click)
        self.boton_guardar.pack(fill="x", padx=20, pady=20)
        
        self.label_mensaje = ctk.CTkLabel(master=self.frame_derecha, text="", text_color="gray")
        self.label_mensaje.pack(fill="x", padx=20, pady=(0, 10))

        # --- 4. Carga inicial de datos ---
        self._refrescar_lista_hallazgos()
        
    # ... (Todas las funciones: _refrescar_lista_hallazgos, _on_guardar_click,
    # _on_generar_mapa_click, _on_borrar_click, _on_editar_click,
    # _on_preview_click, _limpiar_mensaje, _on_busqueda_change,
    # _normalizar_texto, _on_orden_change ... 
    # ... quedan EXACTAMENTE IGUAL) ...

    # Dentro de la clase App en app.py

    def _refrescar_lista_hallazgos(self):
        """
        Limpia el frame scroleable y vuelve a cargar los hallazgos
        filtrando por el término de búsqueda.
        """
        for widget in self.scrollable_frame_lista.winfo_children():
            widget.destroy()

        if not self.admin or not self.admin.hallazgos:
            label_vacia = ctk.CTkLabel(master=self.scrollable_frame_lista, text="No hay hallazgos registrados.")
            label_vacia.pack(pady=10, padx=10)
            return

        termino_busqueda = self.entry_busqueda.get()
        termino_norm = self._normalizar_texto(termino_busqueda)
        lista_completa = self.admin.hallazgos
        lista_a_mostrar = []

        if not termino_norm:
            lista_a_mostrar = lista_completa
        else:
            for hallazgo in lista_completa:
                nombre_norm = self._normalizar_texto(hallazgo.nombre)
                desc_norm = self._normalizar_texto(hallazgo.descripcion)
                if termino_norm in nombre_norm or termino_norm in desc_norm:
                    lista_a_mostrar.append(hallazgo)
        
        if not lista_a_mostrar:
            label_vacia = ctk.CTkLabel(master=self.scrollable_frame_lista, text="No se encontraron hallazgos.")
            label_vacia.pack(pady=10, padx=10)
            return

        try:
            for hallazgo in lista_a_mostrar:
                item_frame = ctk.CTkFrame(
                    master=self.scrollable_frame_lista, 
                    fg_color=("gray80", "gray20"),
                    border_width=1, # <-- Borde
                    border_color=("gray70", "gray30") # <-- Color del borde
                )
                item_frame.pack(fill="x", pady=4, padx=5)
                
                item_frame.grid_columnconfigure(0, weight=0, minsize=60)
                item_frame.grid_columnconfigure(1, weight=1)
                item_frame.grid_columnconfigure(2, weight=0)
                item_frame.grid_columnconfigure(3, weight=0)
                
                # --- Lógica de Preview (sin cambios) ---
                img_preview_label = None
                img_preview = None 
                ruta_preview = hallazgo.imagen_preview
                if ruta_preview and os.path.exists(ruta_preview):
                    try:
                        img = Image.open(ruta_preview)
                        img.thumbnail((50, 50))
                        img_preview = ctk.CTkImage(light_image=img, dark_image=img, size=(50, 50))
                        img_preview_label = ctk.CTkLabel(master=item_frame, text="", image=img_preview)
                    except Exception as e:
                        print(f"Error cargando preview {ruta_preview}: {e}")
                        img_preview_label = ctk.CTkLabel(master=item_frame, text="Error", width=50)
                else:
                    img_preview_label = ctk.CTkLabel(master=item_frame, text="📸", font=ctk.CTkFont(size=30), width=50)
                img_preview_label.bind(
                    "<Button-1>", 
                    lambda e, h=hallazgo: self._on_preview_click(h)
                )
                img_preview_label.configure(cursor="hand2")
                img_preview_label.grid(row=0, column=0, sticky="ns", padx=5, pady=5)
                # --- Fin Lógica Preview ---

                # --- ¡CAMBIO! Construcción del texto ---
                texto_linea1 = f"{hallazgo.nombre}: {hallazgo.descripcion}"
                
                # Armamos el texto del lugar
                texto_lugar = "Lugar: Desconocido"
                if hallazgo.ubicacion:
                    if hallazgo.ubicacion.pueblo and hallazgo.ubicacion.provincia:
                        texto_lugar = f"Lugar: {hallazgo.ubicacion.pueblo}, {hallazgo.ubicacion.provincia}"
                    elif hallazgo.ubicacion.pueblo:
                        texto_lugar = f"Lugar: {hallazgo.ubicacion.pueblo}"
                    elif hallazgo.ubicacion.provincia:
                        texto_lugar = f"Lugar: {hallazgo.ubicacion.provincia}"
                
                # Armamos el texto de la fecha
                texto_fecha = "Encontrado: ?"
                if hallazgo.fec_ad:
                    texto_fecha = f"Encontrado: {hallazgo.fec_ad}"
                    
                # Juntamos todo
                texto = f"{texto_linea1}\n{texto_lugar} ({texto_fecha})"
                # --- FIN CAMBIO ---
                
                item_label = ctk.CTkLabel(
                    master=item_frame, 
                    text=texto, 
                    justify="left", 
                    anchor="w",
                    wraplength=300 # Podés ajustar este valor si querés
                )
                item_label.grid(row=0, column=1, sticky="ew", padx=10, pady=5)
                
                # --- Botones (sin cambios) ---
                boton_editar = ctk.CTkButton(
                    master=item_frame, 
                    text="✏️",
                    width=40,
                    fg_color="transparent",
                    text_color=("black", "white"),
                    hover_color="blue",
                    command=lambda h=hallazgo: self._on_editar_click(h)
                )
                boton_editar.grid(row=0, column=2, sticky="e", padx=(0, 5))
                
                boton_borrar = ctk.CTkButton(
                    master=item_frame, 
                    text="❌",
                    width=40,
                    fg_color="transparent",
                    text_color=("black", "white"),
                    hover_color="red",
                    command=lambda h_id=hallazgo.id, h_nombre=hallazgo.nombre: self._on_borrar_click(h_id, h_nombre)
                )
                boton_borrar.grid(row=0, column=3, sticky="e", padx=(0, 10))

        except Exception as e:
            print(f"Error refrescando lista: {e}")
            label_error = ctk.CTkLabel(master=self.scrollable_frame_lista, text="Error al cargar hallazgos.")
            label_error.pack(pady=10, padx=10)

    def _on_guardar_click(self):
        try:
            nombre = self.entry_nombre.get()
            desc = self.entry_desc.get()
            pueblo = self.entry_pueblo.get()
            provincia = self.entry_provincia.get()
            try: coord_y = float(self.entry_coord_y.get()) if self.entry_coord_y.get() else None
            except ValueError: raise ValueError("Coordenada Y debe ser un número o estar vacío")
            try: coord_x = float(self.entry_coord_x.get()) if self.entry_coord_x.get() else None
            except ValueError: raise ValueError("Coordenada X debe ser un número o estar vacío")
            print(f"DEBUG UI (Agregar): Coords leídas: x={coord_x}, y={coord_y}")
            try: dia_str = self.entry_dia.get()
            except ValueError: raise ValueError("Día debe ser un número")
            try: mes_str = self.entry_mes.get()
            except ValueError: raise ValueError("Mes debe ser un número")
            try: anio_str = self.entry_anio.get()
            except ValueError: raise ValueError("Año debe ser un número")
            if not nombre or not desc:
                raise ValueError("Nombre y Descripción (*) no pueden estar vacíos")
            nuevas_coords = None
            if coord_x is not None and coord_y is not None:
                nuevas_coords = Coords(x=coord_x, y=coord_y)
            nueva_ubi = None
            if pueblo and provincia:
                 nueva_ubi = ubicacion(pueblo=pueblo, provincia=provincia, coords=nuevas_coords)
            elif nuevas_coords is not None:
                 print("Advertencia: Guardando coordenadas sin pueblo/provincia.")
                 nueva_ubi = ubicacion(pueblo="", provincia="", coords=nuevas_coords)
            nueva_fecha = None
            if dia_str and mes_str and anio_str:
                try:
                    dia = int(dia_str)
                    mes = int(mes_str)
                    anio = int(anio_str)
                    nueva_fecha = Fecha(dia=dia, mes=mes, anio=anio)
                except ValueError:
                    raise ValueError("Día, Mes y Año deben ser números válidos si se ingresan")
            nuevo_obj = Objeto(
                nombre=nombre, 
                descripcion=desc, 
                ubicacion=nueva_ubi, 
                fecha_adquisicion=nueva_fecha 
            )
            nuevo_id = self.admin.agregar_hallazgo(nuevo_obj)
            self._refrescar_lista_hallazgos()
            self.entry_nombre.delete(0, 'end')
            self.entry_desc.delete(0, 'end')
            self.entry_pueblo.delete(0, 'end')
            self.entry_provincia.delete(0, 'end')
            self.entry_coord_x.delete(0, 'end')
            self.entry_coord_y.delete(0, 'end')
            self.label_mensaje.configure(text=f"¡'{desc}' guardado con éxito!", text_color="green")
            self.label_mensaje.after(2000, self._limpiar_mensaje)
        except Exception as e:
            print(f"Error al guardar: {e}")
            self.label_mensaje.configure(text=f"Error: {e}", text_color="red")
            self.label_mensaje.after(4000, self._limpiar_mensaje)
            
    # En app.py

    def _on_generar_mapa_click(self):
        self.label_mensaje.configure(text="")
        if not self.admin or not self.admin.hallazgos:
            print("No hay hallazgos para mapear.")
            self.label_mensaje.configure(text="Error: No hay hallazgos para mostrar en el mapa.", text_color="red")
            self.label_mensaje.after(4000, self._limpiar_mensaje)
            return
        try:
            print("Generando mapa...")
            
            # --- ¡CAMBIO CRÍTICO! Guardar en AppData ---
            app_data_dir = os.getenv('APPDATA')
            user_data_folder = os.path.join(app_data_dir, "MetalDex")
            
            # Nos aseguramos de que la carpeta exista (por si acaso)
            if not os.path.exists(user_data_folder):
                os.makedirs(user_data_folder)
            
            # Definimos la ruta completa del archivo HTML
            ruta_mapa = os.path.join(user_data_folder, "mi_mapa_de_hallazgos.html")
            # -------------------------------------------

            mapa_gen = MapaHallazgos(admin=self.admin)
            
            # Le pasamos la ruta completa a la función
            mapa_gen.generar_y_guardar_mapa(
                nombre_archivo=ruta_mapa, 
                abrir_automaticamente=True
            )
            
            self.label_mensaje.configure(text=f"¡Mapa generado y abierto!", text_color="green")
            self.label_mensaje.after(2000, self._limpiar_mensaje)
        except Exception as e:
            print(f"Error al generar el mapa: {e}")
            self.label_mensaje.configure(text=f"Error al generar mapa: {e}", text_color="red")
            self.label_mensaje.after(4000, self._limpiar_mensaje)

    def _on_borrar_click(self, hallazgo_id: int, nombre_hallazgo: str): # <-- ¡ESTA LÍNEA ES LA QUE CAMBIA!
        """
        Se ejecuta al presionar el botón 'X' de un ítem.
        Pide confirmación antes de borrar.
        """
        print(f"Intento de borrado para: ID {hallazgo_id} ({nombre_hallazgo})")
        
        # Usamos el nombre solo para el mensaje
        confirmar = tkinter.messagebox.askyesno(
            title="Confirmar Borrado",
            message=f"¿Estás seguro de que querés borrar '{nombre_hallazgo}'?\n\n¡Esta acción no se puede deshacer!"
        )
        
        if not confirmar:
            print("Borrado cancelado.")
            return
            
        try:
            # ¡Ahora sí va a encontrar el hallazgo_id!
            exito = self.admin.eliminar_hallazgo(hallazgo_id)
            
            if exito:
                self.label_mensaje.configure(text=f"Hallazgo '{nombre_hallazgo}' eliminado.", text_color="green")
                self.label_mensaje.after(2000, self._limpiar_mensaje)
                self._refrescar_lista_hallazgos()
            else:
                self.label_mensaje.configure(text=f"Error: No se pudo encontrar '{nombre_hallazgo}'.", text_color="red")
                self.label_mensaje.after(4000, self._limpiar_mensaje)
        except Exception as e:
            print(f"Error al eliminar: {e}")
            self.label_mensaje.configure(text=f"Error al eliminar: {e}", text_color="red")
            self.label_mensaje.after(4000, self._limpiar_mensaje)

    def _on_editar_click(self, hallazgo_a_editar: Objeto):
        print(f"Intento de edición para: {hallazgo_a_editar.nombre}")
        edit_window = EditWindow(
            master=self, 
            hallazgo_a_editar=hallazgo_a_editar,
            admin=self.admin,
            on_close_callback=self._refrescar_lista_hallazgos
        )
    
    def _on_preview_click(self, hallazgo: Objeto):
        ruta_preview = hallazgo.imagen_preview
        if not ruta_preview or not os.path.exists(ruta_preview):
            print("Clic en placeholder o imagen no encontrada, abriendo editor...")
            self._on_editar_click(hallazgo)
            return
        print(f"Abriendo visor para hallazgo ID {hallazgo.id}, img: {ruta_preview}")
        ImageViewer(
            master=self,
            admin=self.admin,
            hallazgo_id=hallazgo.id,
            clicked_image_path=ruta_preview
        )
        
    # --- ¡NUEVAS FUNCIONES! ---
    def _on_abrir_mapa_click(self):
        """
        Abre la ventana Toplevel para seleccionar coordenadas.
        """
        print("Abriendo selector de mapa...")
        MapPickerWindow(
            master=self,
            # Le pasamos la función que tiene que llamar
            # cuando se seleccionen las coordenadas
            on_coords_selected_callback=self._actualizar_coords_desde_mapa
        )

    def _actualizar_coords_desde_mapa(self, coords_tuple):
        """
        Esta es la función 'callback'. Recibe las coordenadas
        desde la ventana del mapa y actualiza los campos.
        """
        lat, lon = coords_tuple
        print(f"Coords recibidas desde el mapa: Lat={lat}, Lon={lon}")
        
        # Formateamos a 6 decimales para que se vea bien
        lat_str = f"{lat:.6f}"
        lon_str = f"{lon:.6f}"
        
        # Borramos lo que haya y escribimos el valor nuevo
        self.entry_coord_y.delete(0, "end")
        self.entry_coord_y.insert(0, lat_str)
        
        self.entry_coord_x.delete(0, "end")
        self.entry_coord_x.insert(0, lon_str)
    # --- FIN NUEVAS FUNCIONES ---
        
    def _limpiar_mensaje(self):
        self.label_mensaje.configure(text="")
        
    def _on_busqueda_change(self, event):
        self._refrescar_lista_hallazgos()

    def _normalizar_texto(self, texto: str) -> str:
        if not texto:
            return ""
        return unidecode(texto).lower()
        
    def _on_orden_change(self):
        nuevo_orden = self.variable_orden.get()
        print(f"Cambiando orden a: {nuevo_orden}")
        self.admin.cargar_hallazgos(ordenar_por=nuevo_orden)
        self._refrescar_lista_hallazgos()

# --- Bucle principal ---
if __name__ == "__main__":
    app = App()
    app.mainloop()