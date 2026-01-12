import customtkinter as ctk
from PIL import Image
import os
from hallazgos_admin import HallazgosAdmin

class ImageViewer(ctk.CTkToplevel):
    """
    Ventana Toplevel para mostrar imágenes en tamaño completo.
    """
    def __init__(self, master, admin: HallazgosAdmin, hallazgo_id: int, clicked_image_path: str):
        super().__init__(master)
        
        self.admin = admin
        self.hallazgo_id = hallazgo_id
        
        self.grab_set()
        self.title("Visor de Imágenes")
        self.geometry("800x600")

        self.lista_imagenes = self.admin.obtener_imagenes(self.hallazgo_id)
        
        if not self.lista_imagenes:
            self.destroy()
            return
            
        self.indice_actual = 0
        for i, img_dict in enumerate(self.lista_imagenes):
            if img_dict['ruta_imagen'] == clicked_image_path:
                self.indice_actual = i
                break
        
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)
        
        self.img_label = ctk.CTkLabel(self, text="")
        self.img_label.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        
        controls_frame = ctk.CTkFrame(self, height=50)
        controls_frame.grid(row=1, column=0, sticky="ew", padx=10, pady=10)
        
        self.btn_anterior = ctk.CTkButton(controls_frame, text="< Anterior", command=self.mostrar_anterior)
        self.btn_anterior.pack(side="left", padx=20, pady=10)
        
        self.ruta_label = ctk.CTkLabel(controls_frame, text="", text_color="gray70")
        self.ruta_label.pack(side="left", expand=True)
        
        self.btn_siguiente = ctk.CTkButton(controls_frame, text="Siguiente >", command=self.mostrar_siguiente)
        self.btn_siguiente.pack(side="right", padx=20, pady=10)
        
        self.cargar_imagen_actual()

    def cargar_imagen_actual(self):
        data_actual = self.lista_imagenes[self.indice_actual]
        ruta_img_actual = data_actual['ruta_imagen']
        
        try:
            img_pil = Image.open(ruta_img_actual)
            
            max_w = self.winfo_width() - 40
            max_h = self.winfo_height() - 100
            if max_w < 200: max_w = 800
            if max_h < 200: max_h = 600
            
            img_pil.thumbnail((max_w, max_h), Image.Resampling.LANCZOS)
            
            img_tk = ctk.CTkImage(light_image=img_pil, dark_image=img_pil, size=img_pil.size)
            
            self.img_label.configure(text="", image=img_tk)
            self.img_label.image = img_tk
            
            self.ruta_label.configure(text=f"{self.indice_actual + 1} / {len(self.lista_imagenes)}\n{os.path.basename(ruta_img_actual)}")

        except Exception as e:
            self.img_label.configure(text=f"Error al cargar imagen:\n{ruta_img_actual}", image=None)
        
        self.btn_anterior.configure(state="normal" if self.indice_actual > 0 else "disabled")
        self.btn_siguiente.configure(state="normal" if self.indice_actual < len(self.lista_imagenes) - 1 else "disabled")

    def mostrar_anterior(self):
        if self.indice_actual > 0:
            self.indice_actual -= 1
            self.cargar_imagen_actual()

    def mostrar_siguiente(self):
        if self.indice_actual < len(self.lista_imagenes) - 1:
            self.indice_actual += 1
            self.cargar_imagen_actual()