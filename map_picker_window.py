import customtkinter as ctk
import tkintermapview
from PIL import Image, ImageTk 
import os
import sys

def resource_path(relative_path):
    if getattr(sys, 'frozen', False):
        application_path = os.path.dirname(sys.executable)
    else:
        application_path = os.path.abspath(".")
    return os.path.join(application_path, relative_path)

class MapPickerWindow(ctk.CTkToplevel):
    """
    Ventana Toplevel con mapa interactivo para selección de coordenadas.
    """
    def __init__(self, master, on_coords_selected_callback):
        super().__init__(master)
        
        self.on_coords_selected_callback = on_coords_selected_callback
        self.selected_coords = None 
        self.marker = None 

        self.grab_set() 
        self.title("Seleccionar Ubicación")
        self.geometry("800x650")
        
        try:
            self.iconbitmap(resource_path("icon.ico"))
        except Exception:
            pass

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=0)

        self.marker_icon = None
        icon_path = resource_path("OIP.ico") 
        
        if os.path.exists(icon_path):
            try:
                original_img = Image.open(icon_path)
                icon_size = (30, 30) 
                original_img.thumbnail(icon_size, Image.Resampling.LANCZOS)
                
                new_height = icon_size[1] * 2
                offset_img = Image.new("RGBA", (icon_size[0], new_height), (0, 0, 0, 0))
                offset_img.paste(original_img, (0, 0))
                
                self.marker_icon = ImageTk.PhotoImage(offset_img)
            except Exception as e:
                print(f"Error al cargar el icono del marcador: {e}")
                self.marker_icon = None 

        self.map_widget = tkintermapview.TkinterMapView(
            self,
            width=800,
            height=600,
            corner_radius=0
        )
        self.map_widget.grid(row=0, column=0, sticky="nsew")

        self.map_widget.add_left_click_map_command(self._on_left_click)
        
        self.map_widget.set_tile_server("https://mt0.google.com/vt/lyrs=s,h&hl=en&x={x}&y={y}&z={z}&s=Ga", max_zoom=22)
        self.map_widget.set_position(-31.39, -58.02)
        self.map_widget.set_zoom(12)
        
        controls_frame = ctk.CTkFrame(self)
        controls_frame.grid(row=1, column=0, sticky="ew", padx=10, pady=10)
        controls_frame.grid_columnconfigure(0, weight=1)
        controls_frame.grid_columnconfigure(1, weight=0)
        
        label_ayuda = ctk.CTkLabel(
            controls_frame, 
            text="Haz clic en el mapa para mover el marcador. Presiona 'Confirmar'.",
            text_color=("gray20", "gray80")
        )
        label_ayuda.grid(row=0, column=0, sticky="w", padx=10)

        self.btn_confirmar = ctk.CTkButton(
            controls_frame,
            text="Confirmar Ubicación",
            command=self._on_confirm,
            state="disabled"
        )
        self.btn_confirmar.grid(row=0, column=1, sticky="e", padx=10)

    def _on_left_click(self, coords_tuple):
        lat, lon = coords_tuple
        self.selected_coords = (lat, lon)
        
        if self.marker is not None:
            self.marker.delete()

        self.marker = self.map_widget.set_marker(
            lat, lon, 
            text="", 
            icon=self.marker_icon 
        )
            
        self.btn_confirmar.configure(state="normal")

    def _on_confirm(self):
        if self.selected_coords:
            self.on_coords_selected_callback(self.selected_coords)
            self.destroy()