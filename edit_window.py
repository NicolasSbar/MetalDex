import customtkinter as ctk
import tkinter.messagebox
import tkinter.filedialog
import os
import shutil
import datetime
from PIL import Image

from hallazgos_admin import HallazgosAdmin, resource_path
from objeto import Objeto
from coords import Coords
from ubicacion import ubicacion
from fecha import Fecha
from image_viewer import ImageViewer

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
            pass

        self.hallazgo_original = hallazgo_a_editar
        self.admin = admin
        self.on_close_callback = on_close_callback
        
        app_data_dir = os.getenv('APPDATA')
        self.image_storage_path = os.path.join(app_data_dir, "MetalDex", "user_images")
        self._crear_carpeta_imagenes()

        main_scroll_frame = ctk.CTkScrollableFrame(master=self)
        main_scroll_frame.pack(fill="both", expand=True, padx=10, pady=10)

        ctk.CTkLabel(main_scroll_frame, text="Datos del Hallazgo", font=("Arial", 16, "bold")).pack(pady=(10, 5))

        self.entry_nombre = ctk.CTkEntry(main_scroll_frame, placeholder_text="Nombre")
        self.entry_nombre.insert(0, hallazgo_a_editar.nombre)
        self.entry_nombre.pack(fill="x", pady=5)

        self.textbox_desc = ctk.CTkTextbox(main_scroll_frame, height=80)
        self.textbox_desc.insert("0.0", hallazgo_a_editar.descripcion)
        self.textbox_desc.pack(fill="x", pady=5)

        self.entry_pueblo = ctk.CTkEntry(main_scroll_frame, placeholder_text="Pueblo")
        self.entry_pueblo.insert(0, hallazgo_a_editar.ubicacion.pueblo if hallazgo_a_editar.ubicacion else "")
        self.entry_pueblo.pack(fill="x", pady=5)
        
        self.entry_provincia = ctk.CTkEntry(main_scroll_frame, placeholder_text="Provincia")
        self.entry_provincia.insert(0, hallazgo_a_editar.ubicacion.provincia if hallazgo_a_editar.ubicacion else "")
        self.entry_provincia.pack(fill="x", pady=5)
        
        coords_frame = ctk.CTkFrame(main_scroll_frame, fg_color="transparent")
        coords_frame.pack(fill="x", pady=5)
        
        self.entry_coord_y = ctk.CTkEntry(coords_frame, placeholder_text="Latitud")
        if hallazgo_a_editar.ubicacion and hallazgo_a_editar.ubicacion.coords:
            self.entry_coord_y.insert(0, str(hallazgo_a_editar.ubicacion.coords.y))
        self.entry_coord_y.pack(side="left", fill="x", expand=True, padx=(0, 5))
        
        self.entry_coord_x = ctk.CTkEntry(coords_frame, placeholder_text="Longitud")
        if hallazgo_a_editar.ubicacion and hallazgo_a_editar.ubicacion.coords:
            self.entry_coord_x.insert(0, str(hallazgo_a_editar.ubicacion.coords.x))
        self.entry_coord_x.pack(side="left", fill="x", expand=True, padx=5)

        self.entry_fecha = ctk.CTkEntry(main_scroll_frame, placeholder_text="DD/MM/AAAA")
        if hallazgo_a_editar.fec_ad:
            self.entry_fecha.insert(0, str(hallazgo_a_editar.fec_ad))
        self.entry_fecha.pack(fill="x", pady=5)

        ctk.CTkButton(main_scroll_frame, text="Guardar cambios", command=self._guardar_cambios).pack(pady=10)
        
        self.label_mensaje_edit = ctk.CTkLabel(main_scroll_frame, text="", text_color="green")
        self.label_mensaje_edit.pack(pady=5)

        ctk.CTkLabel(main_scroll_frame, text="Galería de Imágenes", font=("Arial", 16, "bold")).pack(pady=(20, 5))
        
        ctk.CTkButton(main_scroll_frame, text="➕ Añadir imagen...", command=self._seleccionar_imagen_archivo).pack(pady=5)

        self.frame_imagenes = ctk.CTkFrame(main_scroll_frame)
        self.frame_imagenes.pack(fill="both", expand=True, pady=10)

        self._refrescar_lista_imagenes()

    def _crear_carpeta_imagenes(self):
        if not os.path.exists(self.image_storage_path):
            os.makedirs(self.image_storage_path)

    def _guardar_cambios(self):
        nombre = self.entry_nombre.get()
        desc = self.textbox_desc.get("0.0", "end").strip()
        pueblo = self.entry_pueblo.get()
        prov = self.entry_provincia.get()
        fecha_str = self.entry_fecha.get()
        lat_str = self.entry_coord_y.get()
        lon_str = self.entry_coord_x.get()
        
        fecha_obj = None
        if fecha_str:
            try:
                d, m, a = map(int, fecha_str.split('/'))
                fecha_obj = Fecha(d, m, a)
            except ValueError:
                self.label_mensaje_edit.configure(text="Error fecha (DD/MM/AAAA)", text_color="red")
                return

        coords_obj = None
        if lat_str and lon_str:
            try:
                coords_obj = Coords(float(lon_str), float(lat_str))
            except ValueError:
                self.label_mensaje_edit.configure(text="Error coords", text_color="red")
                return
        
        ubi_obj = None
        if pueblo or prov or coords_obj:
            ubi_obj = ubicacion(pueblo, prov, coords_obj)

        obj_actualizado = Objeto(nombre, desc, ubi_obj, fecha_obj, id=self.hallazgo_original.id)
        
        if self.admin.editar_hallazgo(self.hallazgo_original.id, obj_actualizado):
            self.hallazgo_original = obj_actualizado
            self.label_mensaje_edit.configure(text="Cambios guardados", text_color="green")
            self.on_close_callback()
        else:
            self.label_mensaje_edit.configure(text="Error al actualizar", text_color="red")

    def _seleccionar_imagen_archivo(self):
        ruta_archivo = tkinter.filedialog.askopenfilename(
            title="Seleccionar imagen",
            filetypes=[("Imágenes", "*.jpg *.jpeg *.png *.bmp")]
        )
        if ruta_archivo:
            self._procesar_nueva_imagen(ruta_archivo)

    def _procesar_nueva_imagen(self, ruta_origen):
        try:
            nombre_archivo = f"img_{self.hallazgo_original.id}_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.jpg"
            ruta_destino = os.path.join(self.image_storage_path, nombre_archivo)
            
            shutil.copy(ruta_origen, ruta_destino)
            self.admin.agregar_imagen(self.hallazgo_original.id, ruta_destino)
            self._refrescar_lista_imagenes()
            
            if len(self.admin.obtener_imagenes(self.hallazgo_original.id)) == 1:
                id_nueva = self.admin.obtener_imagenes(self.hallazgo_original.id)[0]['id']
                self.admin.establecer_imagen_preview(self.hallazgo_original.id, id_nueva)
                self.on_close_callback()
                
        except Exception as e:
            print(f"Error copiando imagen: {e}")

    def _refrescar_lista_imagenes(self):
        for widget in self.frame_imagenes.winfo_children():
            widget.destroy()
            
        imagenes = self.admin.obtener_imagenes(self.hallazgo_original.id)
        
        if not imagenes:
            ctk.CTkLabel(self.frame_imagenes, text="No hay imágenes").pack(pady=10)
            return
            
        for img_data in imagenes:
            self._crear_fila_imagen(img_data)

    def _crear_fila_imagen(self, img_data):
        row = ctk.CTkFrame(self.frame_imagenes)
        row.pack(fill="x", pady=2, padx=5)
        
        btn_ver = ctk.CTkButton(
            row, text="👁️", width=30, fg_color="transparent", border_width=1,
            command=lambda: self._abrir_visor(img_data['ruta_imagen'])
        )
        btn_ver.pack(side="left", padx=5)

        lbl_nombre = ctk.CTkLabel(row, text=os.path.basename(img_data['ruta_imagen']), anchor="w")
        lbl_nombre.pack(side="left", fill="x", expand=True, padx=5)
        
        if img_data['es_preview']:
            ctk.CTkLabel(row, text="⭐ Principal", text_color="gold").pack(side="left", padx=5)
        else:
            ctk.CTkButton(row, text="Hacer Principal", width=80, height=24, font=("Arial", 10),
                          command=lambda: self._on_set_preview(img_data['id'])).pack(side="left", padx=5)

        ctk.CTkButton(row, text="🗑️", width=30, height=24, fg_color="red", hover_color="darkred",
                      command=lambda: self._on_delete_imagen(img_data['id'], img_data['ruta_imagen'])).pack(side="right", padx=5)

    def _abrir_visor(self, ruta_imagen_clickeada: str):
        ImageViewer(
            master=self,
            admin=self.admin,
            hallazgo_id=self.hallazgo_original.id,
            clicked_image_path=ruta_imagen_clickeada
        )

    def _on_set_preview(self, id_imagen: int):
        try:
            self.admin.establecer_imagen_preview(self.hallazgo_original.id, id_imagen)
            self._refrescar_lista_imagenes()
            self.on_close_callback()
        except Exception as e:
            print(f"Error al poner preview: {e}")

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
            self._refrescar_lista_imagenes()
            self.on_close_callback()
        except Exception as e:
            print(f"Error borrando archivo: {e}")