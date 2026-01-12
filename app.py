import customtkinter as ctk
import datetime 
import tkinter.messagebox
import os 
import sys
import ctypes
from PIL import Image 
from unidecode import unidecode

from hallazgos_admin import HallazgosAdmin
from mapa_hallazgos import MapaHallazgos
from coords import Coords       
from ubicacion import ubicacion
from fecha import Fecha
from objeto import Objeto
from edit_window import EditWindow
from image_viewer import ImageViewer
from map_picker_window import MapPickerWindow

ctk.set_appearance_mode("dark") 
ctk.set_default_color_theme("blue")

def resource_path(relative_path):
    if getattr(sys, 'frozen', False):
        application_path = os.path.dirname(sys.executable)
    else:
        application_path = os.path.abspath(".")
    return os.path.join(application_path, relative_path)

class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        
        # Configuración de AppID para barra de tareas en Windows
        myappid = 'metaldex.app.1.0' 
        try:
            ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)
        except Exception:
            pass

        self.title("Detectorium - Mi Museo Personal")
        self.geometry("1100x600")
        
        try:
            icon_path = resource_path("icon.ico")
            self.iconbitmap(icon_path)
        except Exception as e:
            print(f"Advertencia: No se pudo cargar el icono: {e}")

        try:
            self.admin = HallazgosAdmin("mis_hallazgos.csv")
        except Exception as e:
            print(f"Error fatal al cargar el admin: {e}")
            self.admin = None 
            tkinter.messagebox.showerror("Error", f"No se pudo iniciar la base de datos.\n{e}")

        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # --- Frame Izquierdo (Menú) ---
        self.frame_izquierdo = ctk.CTkFrame(self, width=200, corner_radius=0)
        self.frame_izquierdo.grid(row=0, column=0, sticky="nsew")
        self.frame_izquierdo.grid_rowconfigure(8, weight=1)

        self.label_titulo = ctk.CTkLabel(self.frame_izquierdo, text="Detectorium", font=ctk.CTkFont(size=20, weight="bold"))
        self.label_titulo.grid(row=0, column=0, padx=20, pady=(20, 10))

        self.entry_busqueda = ctk.CTkEntry(self.frame_izquierdo, placeholder_text="🔍 Buscar hallazgo...")
        self.entry_busqueda.grid(row=1, column=0, padx=20, pady=(10, 10))
        self.entry_busqueda.bind("<KeyRelease>", self._on_busqueda_change)

        self.label_ordenar = ctk.CTkLabel(self.frame_izquierdo, text="Ordenar por:", font=ctk.CTkFont(size=12, weight="bold"))
        self.label_ordenar.grid(row=2, column=0, padx=20, pady=(10, 5), sticky="w")
        
        self.radio_var = ctk.StringVar(value="reciente")
        
        opciones_orden = [
            ("Recientes", "reciente"),
            ("Antiguos", "antiguo"),
            ("Alfabético (A-Z)", "alfabetico"),
            ("Lugar (A-Z)", "lugar")
        ]
        
        for i, (texto, valor) in enumerate(opciones_orden):
            rb = ctk.CTkRadioButton(
                self.frame_izquierdo, 
                text=texto,
                variable=self.radio_var, 
                value=valor,
                command=self._on_orden_change
            )
            rb.grid(row=3+i, column=0, padx=20, pady=5, sticky="w")

        self.btn_mapa = ctk.CTkButton(
            self.frame_izquierdo, 
            text="🗺️ Generar mapa de hallazgos",
            command=self._on_generar_mapa_click
        )
        self.btn_mapa.grid(row=7, column=0, padx=20, pady=20)

        # --- Frame Central (Lista) ---
        self.frame_central = ctk.CTkFrame(self, corner_radius=0)
        self.frame_central.grid(row=0, column=1, sticky="nsew")
        self.frame_central.grid_columnconfigure(0, weight=1)
        self.frame_central.grid_rowconfigure(1, weight=1)

        self.label_lista = ctk.CTkLabel(self.frame_central, text="Mis Hallazgos", font=ctk.CTkFont(size=18, weight="bold"))
        self.label_lista.grid(row=0, column=0, padx=20, pady=(20, 10), sticky="w")

        self.scrollable_frame_hallazgos = ctk.CTkScrollableFrame(self.frame_central, label_text="Lista de Objetos")
        self.scrollable_frame_hallazgos.grid(row=1, column=0, padx=20, pady=20, sticky="nsew")
        self.scrollable_frame_hallazgos.grid_columnconfigure(0, weight=1)

        # --- Frame Derecho (Formulario) ---
        self.frame_derecha = ctk.CTkFrame(self, width=300, corner_radius=0)
        self.frame_derecha.grid(row=0, column=2, sticky="nsew")
        
        label_der = ctk.CTkLabel(master=self.frame_derecha, text="Agregar nuevo hallazgo", font=ctk.CTkFont(size=16, weight="bold"))
        label_der.pack(pady=20, padx=20)
        
        self.entry_nombre = ctk.CTkEntry(self.frame_derecha, placeholder_text="Nombre del objeto")
        self.entry_nombre.pack(pady=10, padx=20, fill="x")
        
        self.textbox_desc = ctk.CTkTextbox(self.frame_derecha, height=80)
        self.textbox_desc.insert("0.0", "Descripción...")
        self.textbox_desc.pack(pady=10, padx=20, fill="x")

        self.entry_pueblo = ctk.CTkEntry(self.frame_derecha, placeholder_text="Pueblo/Ciudad")
        self.entry_pueblo.pack(pady=5, padx=20, fill="x")
        
        self.entry_provincia = ctk.CTkEntry(self.frame_derecha, placeholder_text="Provincia")
        self.entry_provincia.pack(pady=5, padx=20, fill="x")
        
        self.frame_coords = ctk.CTkFrame(self.frame_derecha, fg_color="transparent")
        self.frame_coords.pack(pady=5, padx=20, fill="x")
        
        self.entry_coord_y = ctk.CTkEntry(self.frame_coords, placeholder_text="Latitud", width=90)
        self.entry_coord_y.pack(side="left", padx=(0, 5))
        
        self.entry_coord_x = ctk.CTkEntry(self.frame_coords, placeholder_text="Longitud", width=90)
        self.entry_coord_x.pack(side="left", padx=5)

        self.btn_pick_map = ctk.CTkButton(self.frame_coords, text="📍", width=30, command=self._abrir_selector_mapa)
        self.btn_pick_map.pack(side="left", padx=5)
        
        self.entry_fecha = ctk.CTkEntry(self.frame_derecha, placeholder_text="DD/MM/AAAA")
        self.entry_fecha.pack(pady=10, padx=20, fill="x")
        
        self.btn_guardar = ctk.CTkButton(
            self.frame_derecha, 
            text="💾 Guardar hallazgo", 
            command=self._on_guardar_click
        )
        self.btn_guardar.pack(pady=10, padx=20, fill="x")

        self.btn_guardar_y_foto = ctk.CTkButton(
            self.frame_derecha, 
            text="💾+📸 Guardar y añadir fotos", 
            command=self._on_guardar_y_foto_click,
            fg_color="green", hover_color="darkgreen"
        )
        self.btn_guardar_y_foto.pack(pady=5, padx=20, fill="x")
        
        self.label_mensaje = ctk.CTkLabel(self.frame_derecha, text="", text_color="green")
        self.label_mensaje.pack(pady=10)

        self._refrescar_lista_hallazgos()

    def _on_orden_change(self):
        valor = self.radio_var.get()
        mapa_orden = {
            "reciente": "fecha_reciente",
            "antiguo": "fecha_antigua",
            "alfabetico": "alfabetico",
            "lugar": "lugar"
        }
        if self.admin:
            self.admin.cargar_hallazgos(mapa_orden.get(valor))
            self._refrescar_lista_hallazgos()

    def _refrescar_lista_hallazgos(self):
        for widget in self.scrollable_frame_hallazgos.winfo_children():
            widget.destroy()
        
        if not self.admin:
            return

        termino_busqueda = self._normalizar_texto(self.entry_busqueda.get())
        
        for hallazgo in self.admin.hallazgos:
            mostrar = True
            if termino_busqueda:
                nombre_norm = self._normalizar_texto(hallazgo.nombre)
                desc_norm = self._normalizar_texto(hallazgo.descripcion)
                pueblo_norm = self._normalizar_texto(hallazgo.ubicacion.pueblo if hallazgo.ubicacion else "")
                
                if (termino_busqueda not in nombre_norm and 
                    termino_busqueda not in desc_norm and 
                    termino_busqueda not in pueblo_norm):
                    mostrar = False
            
            if mostrar:
                self._crear_tarjeta_hallazgo(hallazgo)

    def _crear_tarjeta_hallazgo(self, hallazgo: Objeto):
        card = ctk.CTkFrame(self.scrollable_frame_hallazgos, corner_radius=10, border_width=1, border_color="gray30")
        card.pack(fill="x", pady=5, padx=5)
        
        # Imagen Preview
        preview_frame = ctk.CTkFrame(card, width=60, height=60, corner_radius=5)
        preview_frame.pack(side="left", padx=10, pady=10)
        preview_frame.pack_propagate(False)

        if hallazgo.imagen_preview and os.path.exists(hallazgo.imagen_preview):
            try:
                img_pil = Image.open(hallazgo.imagen_preview)
                img_ctk = ctk.CTkImage(light_image=img_pil, dark_image=img_pil, size=(60, 60))
                lbl_img = ctk.CTkLabel(preview_frame, text="", image=img_ctk)
                lbl_img.pack(fill="both", expand=True)
            except Exception:
                ctk.CTkLabel(preview_frame, text="Error").pack(expand=True)
        else:
            ctk.CTkLabel(preview_frame, text="Sin\nFoto", font=("Arial", 9)).pack(expand=True)

        info_frame = ctk.CTkFrame(card, fg_color="transparent")
        info_frame.pack(side="left", fill="both", expand=True, padx=10, pady=5)
        
        titulo = ctk.CTkLabel(info_frame, text=hallazgo.nombre, font=ctk.CTkFont(size=14, weight="bold"), anchor="w")
        titulo.pack(fill="x")
        
        subtexto = ""
        if hallazgo.fec_ad:
            subtexto += f"📅 {hallazgo.fec_ad}  "
        if hallazgo.ubicacion:
            subtexto += f"📍 {hallazgo.ubicacion.pueblo}, {hallazgo.ubicacion.provincia}"
        
        lbl_sub = ctk.CTkLabel(info_frame, text=subtexto, font=ctk.CTkFont(size=12), text_color="gray70", anchor="w")
        lbl_sub.pack(fill="x")

        botones_frame = ctk.CTkFrame(card, fg_color="transparent")
        botones_frame.pack(side="right", padx=10, pady=10)

        btn_editar = ctk.CTkButton(botones_frame, text="✏️", width=40, command=lambda h=hallazgo: self._abrir_editor(h))
        btn_editar.pack(side="top", pady=2)
        
        btn_borrar = ctk.CTkButton(botones_frame, text="🗑️", width=40, fg_color="red", hover_color="darkred", command=lambda h=hallazgo: self._borrar_hallazgo(h))
        btn_borrar.pack(side="top", pady=2)

    def _borrar_hallazgo(self, hallazgo: Objeto):
        confirmacion = tkinter.messagebox.askyesno("Borrar", f"¿Estás seguro de borrar '{hallazgo.nombre}'?")
        if confirmacion:
            if self.admin.eliminar_hallazgo(hallazgo.id):
                self._refrescar_lista_hallazgos()
                print(f"Borrado: {hallazgo.nombre}")

    def _abrir_editor(self, hallazgo: Objeto):
        EditWindow(self, hallazgo, self.admin, on_close_callback=self._refrescar_lista_hallazgos)

    def _on_guardar_click(self):
        self._procesar_guardado(abrir_editor_fotos=False)

    def _on_guardar_y_foto_click(self):
        self._procesar_guardado(abrir_editor_fotos=True)

    def _procesar_guardado(self, abrir_editor_fotos: bool):
        nombre = self.entry_nombre.get()
        desc = self.textbox_desc.get("0.0", "end").strip()
        pueblo = self.entry_pueblo.get()
        prov = self.entry_provincia.get()
        fecha_str = self.entry_fecha.get()
        lat_str = self.entry_coord_y.get()
        lon_str = self.entry_coord_x.get()
        
        if not nombre:
            self.label_mensaje.configure(text="Error: El nombre es obligatorio", text_color="red")
            return

        fecha_obj = None
        if fecha_str:
            try:
                d, m, a = map(int, fecha_str.split('/'))
                fecha_obj = Fecha(d, m, a)
            except ValueError:
                self.label_mensaje.configure(text="Error: Formato de fecha incorrecto (DD/MM/AAAA)", text_color="red")
                return

        coords_obj = None
        if lat_str and lon_str:
            try:
                coords_obj = Coords(float(lon_str), float(lat_str))
            except ValueError:
                self.label_mensaje.configure(text="Error: Coordenadas deben ser números", text_color="red")
                return
        
        ubi_obj = None
        if pueblo or prov or coords_obj:
            ubi_obj = ubicacion(pueblo, prov, coords_obj)

        nuevo_hallazgo = Objeto(nombre, desc, ubi_obj, fecha_obj)
        
        nuevo_id = self.admin.agregar_hallazgo(nuevo_hallazgo)
        
        if nuevo_id is not None:
            self.label_mensaje.configure(text="¡Hallazgo guardado con éxito!", text_color="green")
            self._limpiar_formulario()
            self._refrescar_lista_hallazgos()
            
            if abrir_editor_fotos:
                self.after(500, lambda: self._abrir_editor_recien_creado(nuevo_id))
        else:
            self.label_mensaje.configure(text="Error al guardar en base de datos", text_color="red")
        
        self.after(3000, self._limpiar_mensaje)

    def _abrir_editor_recien_creado(self, nuevo_id: int):
        self.admin.cargar_hallazgos()
        hallazgo_guardado = next((h for h in self.admin.hallazgos if h.id == nuevo_id), None)
        if hallazgo_guardado:
            self._abrir_editor(hallazgo_guardado)

    def _limpiar_formulario(self):
        self.entry_nombre.delete(0, 'end')
        self.textbox_desc.delete("0.0", 'end')
        self.textbox_desc.insert("0.0", "Descripción...")
        self.entry_pueblo.delete(0, 'end')
        self.entry_provincia.delete(0, 'end')
        self.entry_coord_x.delete(0, 'end')
        self.entry_coord_y.delete(0, 'end')
        self.entry_fecha.delete(0, 'end')

    def _abrir_selector_mapa(self):
        MapPickerWindow(self, on_coords_selected_callback=self._actualizar_coords_desde_mapa)

    def _actualizar_coords_desde_mapa(self, coords_tuple):
        lat, lon = coords_tuple
        self.entry_coord_y.delete(0, "end")
        self.entry_coord_y.insert(0, f"{lat:.6f}")
        self.entry_coord_x.delete(0, "end")
        self.entry_coord_x.insert(0, f"{lon:.6f}")

    def _limpiar_mensaje(self):
        self.label_mensaje.configure(text="")
        
    def _on_busqueda_change(self, event):
        self._refrescar_lista_hallazgos()

    def _normalizar_texto(self, texto: str) -> str:
        if not texto:
            return ""
        return unidecode(texto).lower()
    
    def _on_generar_mapa_click(self):
        self.label_mensaje.configure(text="")
        if not self.admin or not self.admin.hallazgos:
            self.label_mensaje.configure(text="Error: No hay hallazgos para mostrar en el mapa.", text_color="red")
            self.label_mensaje.after(4000, self._limpiar_mensaje)
            return
        try:
            app_data_dir = os.getenv('APPDATA')
            user_data_folder = os.path.join(app_data_dir, "MetalDex")
            if not os.path.exists(user_data_folder):
                os.makedirs(user_data_folder)
            
            ruta_mapa = os.path.join(user_data_folder, "mi_mapa_de_hallazgos.html")
            
            mapa_gen = MapaHallazgos(admin=self.admin)
            mapa_gen.generar_y_guardar_mapa(
                nombre_archivo=ruta_mapa, 
                abrir_automaticamente=True
            )
            
            self.label_mensaje.configure(text="¡Mapa generado y abierto!", text_color="green")
            self.label_mensaje.after(2000, self._limpiar_mensaje)
        except Exception as e:
            print(f"Error al generar el mapa: {e}")
            tkinter.messagebox.showerror("Error de Mapa", f"No se pudo generar el mapa:\n{e}")
            self.label_mensaje.configure(text="Error al generar mapa.", text_color="red")
            self.label_mensaje.after(4000, self._limpiar_mensaje)

if __name__ == "__main__":
    app = App()
    app.mainloop()