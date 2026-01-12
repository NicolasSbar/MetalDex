import customtkinter as ctk
import tkinter.messagebox
import tkinter.filedialog
import os
import shutil
import datetime
from PIL import Image
from hallazgos_admin import HallazgosAdmin, resource_path  # <-- Agregá resource_path aquí
from objeto import Objeto
from hallazgos_admin import HallazgosAdmin
from coords import Coords
from ubicacion import ubicacion
from fecha import Fecha
from image_viewer import ImageViewer  # <-- ¡NUEVA IMPORTACIÓN!

class EditWindow(ctk.CTkToplevel):
    """
    Ventana pop-up para editar un hallazgo y administrar sus imágenes.
    """
    def __init__(self, master, hallazgo_a_editar: Objeto, admin: HallazgosAdmin, on_close_callback):
        super().__init__(master)
        
        self.transient(master)
        self.grab_set()
        self.title(f"Editando: {hallazgo_a_editar.nombre}")
        self.geometry("500x750")

        try:
            self.iconbitmap(resource_path("icon.ico"))
        except Exception:
            pass # Si falla, no rompemos nada

        self.hallazgo_original = hallazgo_a_editar
        self.admin = admin
        self.on_close_callback = on_close_callback
        
        # --- ¡CAMBIO! Guardamos fotos en AppData ---
        app_data_dir = os.getenv('APPDATA')
        self.image_storage_path = os.path.join(app_data_dir, "MetalDex", "user_images")
        # ------------------------------------------
        
        self._crear_carpeta_imagenes()

        # --- Frame Principal Scroleable ---
        main_scroll_frame = ctk.CTkScrollableFrame(master=self)
        main_scroll_frame.pack(fill="both", expand=True, padx=10, pady=10)

        # --- Frame Contenedor ---
        container_frame = ctk.CTkFrame(master=main_scroll_frame, fg_color="transparent")
        container_frame.pack(fill="x", expand=True)

        # --- Sección 1: Formulario de Datos ---
        form_frame = ctk.CTkFrame(master=container_frame, fg_color="transparent")
        form_frame.pack(fill="x", padx=0, pady=0)

        # (El resto del formulario es igual)
        ctk.CTkLabel(master=form_frame, text="Nombre / ID:").pack(anchor="w")
        self.entry_nombre = ctk.CTkEntry(master=form_frame)
        self.entry_nombre.insert(0, self.hallazgo_original.nombre)
        self.entry_nombre.pack(fill="x", pady=(0, 10))
        
        ctk.CTkLabel(master=form_frame, text="Descripción:").pack(anchor="w")
        self.entry_desc = ctk.CTkEntry(master=form_frame)
        self.entry_desc.insert(0, self.hallazgo_original.descripcion)
        self.entry_desc.pack(fill="x", pady=(0, 10))

        ctk.CTkLabel(master=form_frame, text="Pueblo / Paraje:").pack(anchor="w")
        self.entry_pueblo = ctk.CTkEntry(master=form_frame)
        self.entry_pueblo.insert(0, self.hallazgo_original.ubicacion.pueblo if self.hallazgo_original.ubicacion else "")
        self.entry_pueblo.pack(fill="x", pady=(0, 10))
        
        ctk.CTkLabel(master=form_frame, text="Provincia:").pack(anchor="w")
        self.entry_provincia = ctk.CTkEntry(master=form_frame)
        self.entry_provincia.insert(0, self.hallazgo_original.ubicacion.provincia if self.hallazgo_original.ubicacion else "")
        self.entry_provincia.pack(fill="x", pady=(0, 10))

        coords_frame = ctk.CTkFrame(master=form_frame, fg_color="transparent")
        coords_frame.pack(fill="x")
        coords_frame.grid_columnconfigure((0, 1), weight=1)
        ctk.CTkLabel(master=coords_frame, text="Coord Y (Lat):").grid(row=0, column=0, sticky="w")
        self.entry_coord_y = ctk.CTkEntry(master=coords_frame)
        self.entry_coord_y.insert(0, str(self.hallazgo_original.ubicacion.coords.y) if self.hallazgo_original.ubicacion and self.hallazgo_original.ubicacion.coords else "")
        self.entry_coord_y.grid(row=1, column=0, sticky="ew", padx=(0, 5))
        ctk.CTkLabel(master=coords_frame, text="Coord X (Lon):").grid(row=0, column=1, sticky="w", padx=(5, 0))
        self.entry_coord_x = ctk.CTkEntry(master=coords_frame)
        self.entry_coord_x.insert(0, str(self.hallazgo_original.ubicacion.coords.x) if self.hallazgo_original.ubicacion and self.hallazgo_original.ubicacion.coords else "")
        self.entry_coord_x.grid(row=1, column=1, sticky="ew", padx=(5, 0))
        
        fecha_frame = ctk.CTkFrame(master=form_frame, fg_color="transparent")
        fecha_frame.pack(fill="x", pady=10)
        fecha_frame.grid_columnconfigure((0, 1, 2), weight=1)
        fecha_obj = self.hallazgo_original.fec_ad.fecha if self.hallazgo_original.fec_ad else None
        ctk.CTkLabel(master=fecha_frame, text="Día:").grid(row=0, column=0, sticky="w")
        self.entry_dia = ctk.CTkEntry(master=fecha_frame)
        self.entry_dia.insert(0, str(fecha_obj.day) if fecha_obj else "")
        self.entry_dia.grid(row=1, column=0, sticky="ew", padx=(0, 5))
        ctk.CTkLabel(master=fecha_frame, text="Mes:").grid(row=0, column=1, sticky="w", padx=5)
        self.entry_mes = ctk.CTkEntry(master=fecha_frame)
        self.entry_mes.insert(0, str(fecha_obj.month) if fecha_obj else "")
        self.entry_mes.grid(row=1, column=1, sticky="ew", padx=5)
        ctk.CTkLabel(master=fecha_frame, text="Año:").grid(row=0, column=2, sticky="w", padx=5)
        self.entry_anio = ctk.CTkEntry(master=fecha_frame)
        self.entry_anio.insert(0, str(fecha_obj.year) if fecha_obj else "")
        self.entry_anio.grid(row=1, column=2, sticky="ew", padx=(5, 0))
        
        self.boton_guardar_cambios = ctk.CTkButton(
            master=container_frame,
            text="💾 Guardar Cambios de Texto",
            font=ctk.CTkFont(size=16, weight="bold"),
            command=self._guardar_cambios_texto
        )
        self.boton_guardar_cambios.pack(fill="x", padx=10, pady=10)
        
        self.label_mensaje_edit = ctk.CTkLabel(master=container_frame, text="", text_color="gray")
        self.label_mensaje_edit.pack(fill="x", padx=10, pady=(0, 10))

        ctk.CTkLabel(master=container_frame, text="").pack()
        ctk.CTkFrame(master=container_frame, height=2, fg_color="gray50").pack(fill="x", padx=10)
        
        ctk.CTkLabel(master=container_frame, text="Administrar Imágenes", font=ctk.CTkFont(size=20, weight="bold")).pack(pady=10)
        
        ctk.CTkButton(
            master=container_frame,
            text="➕ Añadir Imagen...",
            command=self._on_anadir_imagen
        ).pack(fill="x", padx=10)

        self.image_scroll_frame = ctk.CTkScrollableFrame(master=container_frame, height=250, fg_color=("gray90", "gray10"))
        self.image_scroll_frame.pack(fill="x", expand=True, padx=10, pady=10)

        self._refrescar_lista_imagenes()

    # ... ( _crear_carpeta_imagenes, _guardar_cambios_texto, 
    #       _normalizar_nombre_archivo, _on_anadir_imagen ...
    #       quedan EXACTAMENTE IGUAL ) ...
    def _crear_carpeta_imagenes(self):
        if not os.path.exists(self.image_storage_path):
            os.makedirs(self.image_storage_path)
            print(f"Carpeta '{self.image_storage_path}' creada.")
            
    def _guardar_cambios_texto(self):
        try:
            nombre_original = self.hallazgo_original.nombre
            nombre_nuevo = self.entry_nombre.get()
            desc_nuevo = self.entry_desc.get()
            pueblo_nuevo = self.entry_pueblo.get()
            provincia_nueva = self.entry_provincia.get()
            
            coord_x_str = self.entry_coord_x.get()
            coord_y_str = self.entry_coord_y.get()
            coord_x_nuevo = None
            coord_y_nuevo = None
            if coord_x_str:
                try: coord_x_nuevo = float(coord_x_str)
                except ValueError: raise ValueError("Coordenada X debe ser un número o estar vacío")
            if coord_y_str:
                try: coord_y_nuevo = float(coord_y_str)
                except ValueError: raise ValueError("Coordenada Y debe ser un número o estar vacío")

            print(f"DEBUG UI (Editar): Coords leídas: x={coord_x_nuevo}, y={coord_y_nuevo}")

            dia_str = self.entry_dia.get()
            mes_str = self.entry_mes.get()
            anio_str = self.entry_anio.get()
            dia_nuevo, mes_nuevo, anio_nuevo = None, None, None
            if dia_str and mes_str and anio_str:
                 try: 
                     dia_nuevo = int(dia_str)
                     mes_nuevo = int(mes_str)
                     anio_nuevo = int(anio_str)
                 except ValueError: raise ValueError("Día, Mes y Año deben ser números válidos si se ingresan")
            elif dia_str or mes_str or anio_str:
                 raise ValueError("Debe ingresar Día, Mes y Año completos, o dejar los tres vacíos")

            if not nombre_nuevo or not desc_nuevo:
                raise ValueError("Nombre y Descripción no pueden estar vacíos")

            nuevas_coords = None
            if coord_x_nuevo is not None and coord_y_nuevo is not None:
                nuevas_coords = Coords(x=coord_x_nuevo, y=coord_y_nuevo)
            
            nueva_ubi = None
            if pueblo_nuevo and provincia_nueva:
                 nueva_ubi = ubicacion(pueblo=pueblo_nuevo, provincia=provincia_nueva, coords=nuevas_coords)
            elif nuevas_coords is not None:
                 print("Advertencia: Guardando coordenadas sin pueblo/provincia.")
                 nueva_ubi = ubicacion(pueblo="", provincia="", coords=nuevas_coords)

            nueva_fecha = None
            if dia_nuevo and mes_nuevo and anio_nuevo:
                nueva_fecha = Fecha(dia=dia_nuevo, mes=mes_nuevo, anio=anio_nuevo)
            
            objeto_actualizado = Objeto(
                id=self.hallazgo_original.id, 
                nombre=nombre_nuevo,
                descripcion=desc_nuevo,
                ubicacion=nueva_ubi,
                fecha_adquisicion=nueva_fecha
            )

            exito = self.admin.editar_hallazgo(self.hallazgo_original.id, objeto_actualizado)

            if exito:
                self.title(f"Editando: {nombre_nuevo}")
                self.hallazgo_original.nombre = nombre_nuevo
                
                self.on_close_callback()

                self.destroy()
            else:
                raise Exception("El admin no pudo guardar la edición.")

        except Exception as e:
            print(f"Error al guardar edición: {e}")
            self.label_mensaje_edit.configure(text=f"Error: {e}", text_color="red")
            self.label_mensaje_edit.after(4000, lambda: self.label_mensaje_edit.configure(text=""))
            
    def _normalizar_nombre_archivo(self, ruta_original: str) -> str:
        _, extension = os.path.splitext(ruta_original)
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S_%f")
        return f"{timestamp}{extension}"

    def _on_anadir_imagen(self):
        ruta_origen = tkinter.filedialog.askopenfilename(
            title="Seleccionar una imagen",
            filetypes=[("Imágenes", "*.jpg *.jpeg *.png *.bmp *.gif")]
        )
        
        if not ruta_origen:
            return
            
        try:
            nombre_archivo_nuevo = self._normalizar_nombre_archivo(ruta_origen)
            ruta_destino = os.path.join(self.image_storage_path, nombre_archivo_nuevo)
            
            shutil.copy(ruta_origen, ruta_destino)
            
            self.admin.agregar_imagen(self.hallazgo_original.id, ruta_destino)
            
            self._refrescar_lista_imagenes()
            
        except Exception as e:
            print(f"Error al añadir imagen: {e}")
            self.label_mensaje_edit.configure(text=f"Error al añadir imagen: {e}", text_color="red")

    # --- FUNCIÓN MODIFICADA ---
    def _refrescar_lista_imagenes(self):
        for widget in self.image_scroll_frame.winfo_children():
            widget.destroy()
            
        imagenes = self.admin.obtener_imagenes(self.hallazgo_original.id)
        
        if not imagenes:
            ctk.CTkLabel(master=self.image_scroll_frame, text="No hay imágenes para este hallazgo.").pack()
            return
            
        for img_dict in imagenes:
            ruta = img_dict['ruta_imagen']
            id_img = img_dict['id']
            es_preview = img_dict['es_preview']

            img_frame = ctk.CTkFrame(master=self.image_scroll_frame)
            img_frame.pack(fill="x", padx=5, pady=5)
            img_frame.grid_columnconfigure(0, weight=0, minsize=60)
            img_frame.grid_columnconfigure(1, weight=1)
            
            label_thumb = None # Definimos la variable
            try:
                img_pil = Image.open(ruta)
                img_pil.thumbnail((50, 50))
                img_tk = ctk.CTkImage(light_image=img_pil, dark_image=img_pil, size=(50, 50))
                label_thumb = ctk.CTkLabel(master=img_frame, text="", image=img_tk)
                label_thumb.image = img_tk
                label_thumb.grid(row=0, column=0, rowspan=2, padx=5, pady=5)
            except Exception as e:
                print(f"No se pudo cargar la miniatura de {ruta}: {e}")
                label_thumb = ctk.CTkLabel(master=img_frame, text="Error\nFoto", width=50)
                label_thumb.grid(row=0, column=0, rowspan=2, padx=5, pady=5)
            
            # --- ¡NUEVO! Hacemos la miniatura clickeable ---
            if label_thumb: # Solo si el label se creó
                label_thumb.bind(
                    "<Button-1>",
                    lambda e, r=ruta: self._on_thumbnail_click(r)
                )
                label_thumb.configure(cursor="hand2")
            # --- FIN NUEVO ---

            nombre_corto = os.path.basename(ruta)
            label_nombre = ctk.CTkLabel(master=img_frame, text=nombre_corto, justify="left", anchor="w")
            label_nombre.grid(row=0, column=1, sticky="ew", padx=5)

            botones_frame = ctk.CTkFrame(master=img_frame, fg_color="transparent")
            botones_frame.grid(row=1, column=1, sticky="ew", padx=5)

            boton_preview = ctk.CTkButton(
                master=botones_frame, 
                text="Poner como Preview", 
                height=25,
                command=lambda id_img=id_img: self._on_set_preview(id_img)
            )
            boton_preview.pack(side="left", padx=(0, 5))
            
            if es_preview:
                boton_preview.configure(text="✅ Es Preview", state="disabled", fg_color="green")

            boton_borrar = ctk.CTkButton(
                master=botones_frame, 
                text="Borrar", 
                height=25,
                fg_color="red", 
                hover_color="darkred",
                command=lambda id_img=id_img, ruta=ruta: self._on_delete_imagen(id_img, ruta)
            )
            boton_borrar.pack(side="left", padx=5)
            
    # --- ¡NUEVA FUNCIÓN! ---
    def _on_thumbnail_click(self, ruta_imagen_clickeada: str):
        """
        Abre el visor de imágenes al hacer clic en una miniatura.
        """
        print(f"Abriendo visor desde editor para img: {ruta_imagen_clickeada}")
        ImageViewer(
            master=self, # El master es la ventana de Edición
            admin=self.admin,
            hallazgo_id=self.hallazgo_original.id,
            clicked_image_path=ruta_imagen_clickeada
        )
    # --- FIN NUEVA FUNCIÓN ---

    def _on_set_preview(self, id_imagen: int):
        try:
            self.admin.establecer_imagen_preview(self.hallazgo_original.id, id_imagen)
            self._refrescar_lista_imagenes()
            self.on_close_callback()
        except Exception as e:
            print(f"Error al poner preview: {e}")
            self.label_mensaje_edit.configure(text=f"Error al poner preview: {e}", text_color="red")

    def _on_delete_imagen(self, id_imagen: int, ruta_imagen: str):
        confirmar = tkinter.messagebox.askyesno(
            title="Confirmar Borrado",
            message=f"¿Estás seguro de que querés borrar esta imagen?\n\n{ruta_imagen}"
        )
        if not confirmar:
            return
        try:
            ruta_a_borrar_confirmada = self.admin.eliminar_imagen(id_imagen)
            if ruta_a_borrar_confirmada and os.path.exists(ruta_a_borrar_confirmada):
                os.remove(ruta_a_borrar_confirmada)
                print(f"Archivo '{ruta_a_borrar_confirmada}' borrado del disco.")
            self._refrescar_lista_imagenes()
            self.on_close_callback()
        except Exception as e:
            print(f"Error al borrar imagen: {e}")
            self.label_mensaje_edit.configure(text=f"Error al borrar imagen: {e}", text_color="red")