# Este es el nuevo archivo: image_viewer.py

import customtkinter as ctk
from PIL import Image
import os
from hallazgos_admin import HallazgosAdmin

class ImageViewer(ctk.CTkToplevel):
    """
    Una ventana Toplevel para mostrar imágenes en grande
    con navegación de galería.
    """
    def __init__(self, master, admin: HallazgosAdmin, hallazgo_id: int, clicked_image_path: str):
        super().__init__(master)
        
        self.admin = admin
        self.hallazgo_id = hallazgo_id
        
        self.grab_set() # Bloquea la ventana principal
        self.title("Visor de Imágenes")
        self.geometry("800x600") # Un tamaño decente para empezar

        # 1. Obtenemos todas las imágenes de este hallazgo
        self.lista_imagenes = self.admin.obtener_imagenes(self.hallazgo_id)
        
        if not self.lista_imagenes:
            self.destroy() # Cerramos si por error no hay imágenes
            return
            
        # 2. Buscamos el índice de la imagen que se clickeó
        self.indice_actual = 0
        for i, img_dict in enumerate(self.lista_imagenes):
            if img_dict['ruta_imagen'] == clicked_image_path:
                self.indice_actual = i
                break
        
        # --- Configuración de la Interfaz ---
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # Label principal donde se mostrará la imagen
        self.img_label = ctk.CTkLabel(self, text="Cargando...")
        self.img_label.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        
        # Frame para los botones de navegación
        btn_frame = ctk.CTkFrame(self, fg_color="transparent")
        btn_frame.grid(row=1, column=0, pady=10)

        self.btn_anterior = ctk.CTkButton(btn_frame, text="< Anterior", command=self.mostrar_anterior)
        self.btn_anterior.pack(side="left", padx=20)

        # Label para mostrar info (ej: 1 / 5)
        self.ruta_label = ctk.CTkLabel(btn_frame, text="", font=ctk.CTkFont(size=10))
        self.ruta_label.pack(side="left", padx=20)

        self.btn_siguiente = ctk.CTkButton(btn_frame, text="Siguiente >", command=self.mostrar_siguiente)
        self.btn_siguiente.pack(side="left", padx=20)
        
        # Cargamos la primera imagen
        self.cargar_imagen_actual()

    def cargar_imagen_actual(self):
        """Carga la imagen en el self.img_label según el índice actual."""
        
        # Obtenemos la ruta de la imagen actual
        ruta_img_actual = self.lista_imagenes[self.indice_actual]['ruta_imagen']
        
        if not os.path.exists(ruta_img_actual):
            self.img_label.configure(text=f"Error: No se encontró la imagen:\n{ruta_img_actual}", image=None)
            self.ruta_label.configure(text="Imagen no encontrada")
            return

        try:
            # Abrimos con Pillow
            img_pil = Image.open(ruta_img_actual)
            
            # Achicamos la imagen para que entre en la ventana (800x600)
            # Dejamos márgenes de 20px (780) y espacio para botones (550)
            img_pil.thumbnail((780, 550), Image.Resampling.LANCZOS)
            
            # La convertimos a CTkImage
            img_tk = ctk.CTkImage(light_image=img_pil, dark_image=img_pil, size=img_pil.size)
            
            # La ponemos en el Label
            self.img_label.configure(text="", image=img_tk)
            self.img_label.image = img_tk # Guardamos la referencia
            
            # Actualizamos la info de abajo
            self.ruta_label.configure(text=f"{self.indice_actual + 1} / {len(self.lista_imagenes)}\n{os.path.basename(ruta_img_actual)}")

        except Exception as e:
            print(f"Error abriendo imagen {ruta_img_actual}: {e}")
            self.img_label.configure(text=f"Error al cargar la imagen:\n{ruta_img_actual}", image=None)
        
        # Actualizamos el estado de los botones
        self.btn_anterior.configure(state="normal" if self.indice_actual > 0 else "disabled")
        self.btn_siguiente.configure(state="normal" if self.indice_actual < len(self.lista_imagenes) - 1 else "disabled")

    def mostrar_anterior(self):
        """Va a la imagen anterior en la lista."""
        if self.indice_actual > 0:
            self.indice_actual -= 1
            self.cargar_imagen_actual()

    def mostrar_siguiente(self):
        """Va a la imagen siguiente en la lista."""
        if self.indice_actual < len(self.lista_imagenes) - 1:
            self.indice_actual += 1
            self.cargar_imagen_actual()