import sqlite3
import csv
import os
import sys
import datetime
import shutil
from objeto import Objeto
from ubicacion import ubicacion
from coords import Coords
from fecha import Fecha

def resource_path(relative_path):
    """
    Obtiene la ruta absoluta al recurso, compatible con entornos de desarrollo
    y ejecutables empaquetados con PyInstaller.
    """
    if getattr(sys, 'frozen', False):
        application_path = os.path.dirname(sys.executable)
    else:
        application_path = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(application_path, relative_path)

class HallazgosAdmin:
    """
    Controlador principal para la gestión de hallazgos e imágenes.
    Maneja la conexión a SQLite y el sistema de archivos en AppData.
    """

    def __init__(self, archivo_csv_original: str):
        # Configuración de rutas en AppData para persistencia de datos
        app_data_dir = os.getenv('APPDATA')
        self.user_data_folder = os.path.join(app_data_dir, "MetalDex")
        
        if not os.path.exists(self.user_data_folder):
            os.makedirs(self.user_data_folder)
            
        self.db_path = os.path.join(self.user_data_folder, "hallazgos.db")
        
        # Lógica de inicialización de la base de datos
        # Si no existe en AppData, intenta copiar una versión base si está disponible en el paquete
        db_original_en_instalador = resource_path("hallazgos.db")
        
        if not os.path.exists(self.db_path):
            if os.path.exists(db_original_en_instalador):
                try:
                    shutil.copy(db_original_en_instalador, self.db_path)
                except Exception as e:
                    print(f"Error al copiar la base de datos base: {e}")
            else:
                print("Iniciando con base de datos nueva.")
        
        self.csv_path = archivo_csv_original
        self.hallazgos = []
        self.orden_actual = "fecha_reciente"
        
        try:
            with self._conectar_db() as conn:
                conn.execute("PRAGMA foreign_keys = ON;")
                self._crear_tabla_hallazgos(conn)
                self._crear_tabla_imagenes(conn)
            
            self._migrar_csv_a_db()
            self.cargar_hallazgos()
        except sqlite3.OperationalError as e:
             print(f"Error crítico al iniciar SQLite: {e}")
             raise

    def _conectar_db(self):
        return sqlite3.connect(self.db_path)

    def _crear_tabla_hallazgos(self, conn: sqlite3.Connection):
        try:
            cursor = conn.cursor()
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS hallazgos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nombre TEXT NOT NULL,
                descripcion TEXT,
                pueblo TEXT,
                provincia TEXT,
                coord_x REAL,
                coord_y REAL,
                fecha_adq TEXT
            )
            """)
            conn.commit()
        except Exception as e:
            print(f"Error creando tabla hallazgos: {e}")

    def _crear_tabla_imagenes(self, conn: sqlite3.Connection):
        try:
            cursor = conn.cursor()
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS imagenes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                id_hallazgo INTEGER NOT NULL,
                ruta_imagen TEXT NOT NULL,
                es_preview INTEGER DEFAULT 0,
                FOREIGN KEY (id_hallazgo) 
                    REFERENCES hallazgos (id) 
                    ON DELETE CASCADE
            )
            """)
            conn.commit()
        except Exception as e:
            print(f"Error creando tabla imagenes: {e}")

    def _migrar_csv_a_db(self):
        """Importa datos desde CSV si la base de datos está vacía."""
        db_existe_y_poblada = False
        if os.path.exists(self.db_path):
             try:
                 with self._conectar_db() as conn:
                     cursor = conn.cursor()
                     cursor.execute("SELECT COUNT(*) FROM hallazgos")
                     conteo = cursor.fetchone()[0]
                     if conteo > 0:
                         db_existe_y_poblada = True
             except Exception:
                 pass
        
        if db_existe_y_poblada:
            return

        path_csv_real = resource_path(self.csv_path)

        if not db_existe_y_poblada and os.path.exists(path_csv_real):
            try:
                with self._conectar_db() as conn:
                     cursor = conn.cursor()
                     self._crear_tabla_hallazgos(conn)
                     self._crear_tabla_imagenes(conn)
                     
                     with open(path_csv_real, 'r', newline='', encoding='utf-8') as f:
                        reader = csv.DictReader(f)
                        for fila in reader:
                            try:
                                fecha_obj = datetime.date(
                                    int(fila['fecha_adq_anio']),
                                    int(fila['fecha_adq_mes']),
                                    int(fila['fecha_adq_dia'])
                                )
                                fecha_iso = fecha_obj.isoformat()
                                cursor.execute("""
                                INSERT INTO hallazgos (nombre, descripcion, pueblo, provincia, coord_x, coord_y, fecha_adq)
                                VALUES (?, ?, ?, ?, ?, ?, ?)
                                """, (
                                    fila['nombre'], fila['descripcion'],
                                    fila['pueblo'], fila['provincia'],
                                    float(fila['coord_x']), float(fila['coord_y']),
                                    fecha_iso
                                ))
                            except Exception:
                                pass
                        conn.commit()
            except Exception as e:
                 print(f"Error durante la migración CSV: {e}")

    def cargar_hallazgos(self, ordenar_por: str = None):
        self.hallazgos.clear()
        
        if ordenar_por is not None:
            self.orden_actual = ordenar_por
            
        clausula_order_by = ""
        if self.orden_actual == "alfabetico":
            clausula_order_by = "ORDER BY h.nombre COLLATE NOCASE ASC"
        elif self.orden_actual == "fecha_antigua":
            clausula_order_by = "ORDER BY h.fecha_adq ASC, h.id ASC"
        elif self.orden_actual == "lugar":
            clausula_order_by = "ORDER BY h.pueblo COLLATE NOCASE ASC, h.id ASC"
        else: 
            clausula_order_by = "ORDER BY h.fecha_adq DESC, h.id DESC"

        try:
            with self._conectar_db() as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                
                query = f"""
                SELECT 
                    h.*, 
                    i.ruta_imagen as imagen_preview_path
                FROM hallazgos h
                LEFT JOIN imagenes i ON h.id = i.id_hallazgo AND i.es_preview = 1
                {clausula_order_by}
                """
                
                cursor.execute(query)
                filas = cursor.fetchall()
                
                for fila in filas:
                    try:
                        coords_obj = None
                        if fila['coord_x'] is not None and fila['coord_y'] is not None:
                             try:
                                 coords_obj = Coords(x=float(fila['coord_x']), y=float(fila['coord_y']))
                             except (ValueError, TypeError):
                                 coords_obj = None

                        u = None
                        if fila['pueblo'] is not None and fila['provincia'] is not None:
                             u = ubicacion(pueblo=fila['pueblo'], provincia=fila['provincia'], coords=coords_obj)
                        elif coords_obj is not None:
                             u = ubicacion(pueblo="", provincia="", coords=coords_obj)
                        
                        f_adq = None
                        if fila['fecha_adq']:
                             fecha_db = datetime.date.fromisoformat(fila['fecha_adq'])
                             f_adq = Fecha(dia=fecha_db.day, mes=fecha_db.month, anio=fecha_db.year)

                        obj = Objeto(
                            id=fila['id'], 
                            nombre=fila['nombre'],
                            descripcion=fila['descripcion'],
                            ubicacion=u,
                            fecha_adquisicion=f_adq 
                        )
                        
                        obj.imagen_preview = fila['imagen_preview_path']
                        self.hallazgos.append(obj)
                        
                    except Exception as e: 
                        print(f"Error cargando objeto ID {fila['id']}: {e}")
        except Exception as e:
            print(f"Error al cargar hallazgos: {e}")

    def agregar_hallazgo(self, nuevo_objeto: Objeto):
        if not isinstance(nuevo_objeto, Objeto):
             raise ValueError("El argumento debe ser una instancia de Objeto")
        try:
             with self._conectar_db() as conn:
                 cursor = conn.cursor()
                 fecha_iso = nuevo_objeto.fec_ad.fecha.isoformat() if nuevo_objeto.fec_ad else None
                 pueblo = nuevo_objeto.ubicacion.pueblo if nuevo_objeto.ubicacion else None
                 provincia = nuevo_objeto.ubicacion.provincia if nuevo_objeto.ubicacion else None
                 coord_x = nuevo_objeto.ubicacion.coords.x if nuevo_objeto.ubicacion and nuevo_objeto.ubicacion.coords else None
                 coord_y = nuevo_objeto.ubicacion.coords.y if nuevo_objeto.ubicacion and nuevo_objeto.ubicacion.coords else None

                 cursor.execute("""
                 INSERT INTO hallazgos (nombre, descripcion, pueblo, provincia, coord_x, coord_y, fecha_adq)
                 VALUES (?, ?, ?, ?, ?, ?, ?)
                 """, (
                     nuevo_objeto.nombre, nuevo_objeto.descripcion,
                     pueblo, provincia,
                     coord_x, coord_y,
                     fecha_iso
                 ))
                 nuevo_id = cursor.lastrowid
                 conn.commit()
                 self.cargar_hallazgos()
                 return nuevo_id
        except Exception as e:
             print(f"Error al guardar hallazgo: {e}")
             return None

    def eliminar_hallazgo(self, hallazgo_id: int) -> bool:
        try:
            with self._conectar_db() as conn:
                cursor = conn.cursor()
                cursor.execute("DELETE FROM hallazgos WHERE id = ?", (hallazgo_id,))
                conn.commit()
                if cursor.rowcount == 0:
                    return False
                self.cargar_hallazgos()
                return True
        except Exception as e:
            print(f"Error al eliminar hallazgo: {e}")
            return False

    def editar_hallazgo(self, hallazgo_id: int, objeto_actualizado: Objeto) -> bool:
        try:
            with self._conectar_db() as conn:
                cursor = conn.cursor()
                fecha_iso = objeto_actualizado.fec_ad.fecha.isoformat() if objeto_actualizado.fec_ad else None
                pueblo = objeto_actualizado.ubicacion.pueblo if objeto_actualizado.ubicacion else None
                provincia = objeto_actualizado.ubicacion.provincia if objeto_actualizado.ubicacion else None
                coord_x = objeto_actualizado.ubicacion.coords.x if objeto_actualizado.ubicacion and objeto_actualizado.ubicacion.coords else None
                coord_y = objeto_actualizado.ubicacion.coords.y if objeto_actualizado.ubicacion and objeto_actualizado.ubicacion.coords else None
                
                cursor.execute("""
                UPDATE hallazgos 
                SET nombre = ?, descripcion = ?, pueblo = ?, provincia = ?, 
                    coord_x = ?, coord_y = ?, fecha_adq = ?
                WHERE id = ?
                """, (
                    objeto_actualizado.nombre, objeto_actualizado.descripcion,
                    pueblo, provincia,
                    coord_x, coord_y,
                    fecha_iso,
                    hallazgo_id
                ))
                conn.commit()

                if cursor.rowcount == 0:
                    return False
                
                self.cargar_hallazgos()
                return True
        except Exception as e:
            print(f"Error al editar hallazgo: {e}")
            return False

    def agregar_imagen(self, id_hallazgo: int, ruta_imagen: str):
        try:
            with self._conectar_db() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "INSERT INTO imagenes (id_hallazgo, ruta_imagen) VALUES (?, ?)",
                    (id_hallazgo, ruta_imagen)
                )
                conn.commit()
        except Exception as e:
            print(f"Error al agregar imagen: {e}")

    def obtener_imagenes(self, id_hallazgo: int) -> list:
        try:
            with self._conectar_db() as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM imagenes WHERE id_hallazgo = ?", (id_hallazgo,))
                imagenes = cursor.fetchall()
                return [dict(img) for img in imagenes]
        except Exception as e:
            print(f"Error al obtener imágenes: {e}")
            return []

    def establecer_imagen_preview(self, id_hallazgo: int, id_imagen: int):
        try:
            with self._conectar_db() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "UPDATE imagenes SET es_preview = 0 WHERE id_hallazgo = ?",
                    (id_hallazgo,)
                )
                cursor.execute(
                    "UPDATE imagenes SET es_preview = 1 WHERE id = ? AND id_hallazgo = ?",
                    (id_imagen, id_hallazgo)
                )
                conn.commit()
                self.cargar_hallazgos()
        except Exception as e:
            print(f"Error al establecer preview: {e}")
    
    def eliminar_imagen(self, id_imagen: int) -> str:
        ruta_a_borrar = None
        try:
            with self._conectar_db() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT ruta_imagen FROM imagenes WHERE id = ?", (id_imagen,))
                resultado = cursor.fetchone()
                if resultado:
                    ruta_a_borrar = resultado[0]
                cursor.execute("DELETE FROM imagenes WHERE id = ?", (id_imagen,))
                conn.commit()
                self.cargar_hallazgos()
        except Exception as e:
            print(f"Error al eliminar imagen: {e}")
        return ruta_a_borrar