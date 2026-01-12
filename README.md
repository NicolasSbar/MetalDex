# 🪙 MetalDex - Registro de Hallazgos

![Python](https://img.shields.io/badge/Python-3.10%2B-blue)
![Estado](https://img.shields.io/badge/Estado-Terminado-green)
![Tipo](https://img.shields.io/badge/Proyecto-Personal-orange)

**MetalDex** es una aplicación de escritorio diseñada para organizar, catalogar y visualizar hallazgos obtenidos en la actividad de detección de metales.

## 👨‍💻 Sobre el Proyecto

Este repositorio representa un hito importante en mi carrera como desarrollador: **es mi primer proyecto de software diseñado, codificado y desplegado al 100% fuera del entorno académico.**

Nació como una iniciativa puramente personal para resolver una necesidad propia (organizar mis hallazgos) y se convirtió en el desafío técnico ideal para aplicar 
conocimientos de Python en un entorno de producción real, enfrentando problemas que no suelen verse en la universidad, como el empaquetado de ejecutables, 
permisos de sistema en Windows y persistencia de datos local.

## ✨ Funcionalidades

La aplicación permite gestionar un "museo personal" digital con las siguientes capacidades:

- **🗺️ Geolocalización Interactiva:**
  - Integración de mapas satelitales (Google Maps/Folium).
  - Selector de coordenadas visual ("Map Picker") para marcar hallazgos con precisión.
  - Generación de reportes HTML navegables.
- **💾 Base de Datos Local:**
  - Sistema de almacenamiento persistente usando **SQLite**.
  - Gestión inteligente de archivos y rutas (uso de `%APPDATA%` para cumplir estándares de Windows).
- **📸 Galería Multimedia:**
  - Asociación de evidencia fotográfica a cada registro.
  - Visor de imágenes integrado.
- **🎨 Interfaz de Usuario:**
  - GUI moderna desarrollada con `CustomTkinter` (Modo Oscuro).
  - Filtros de búsqueda y ordenamiento dinámico.

## 🛠️ Tecnologías y Aprendizajes

Durante el desarrollo de MetalDex, profundicé en el uso de librerías modernas y herramientas de despliegue:

| Categoría | Tecnologías |
|-----------|-------------|
| **Lenguaje** | Python 3.10+ |
| **Interfaz (GUI)** | CustomTkinter |
| **Mapas & GIS** | TkinterMapView, Folium |
| **Base de Datos** | SQLite3 |
| **Manipulación Imágenes** | Pillow (PIL) |
| **Empaquetado** | PyInstaller, Inno Setup |

## 🤖 Desafíos Técnicos y Colaboración con IA

Este proyecto representó un reto de integración de diversas tecnologías. Debido a mi enfoque principal en la lógica de Python, utilicé IA Generativa de manera intensiva para cubrir áreas técnicas específicas:

Dominio de SQL: Partiendo de un conocimiento nulo en bases de datos relacionales, utilicé la IA para diseñar el esquema de la base de datos, gestionar la migración desde CSV y asegurar que la carga de múltiples imágenes por objeto fuera estable.

Complejidad de CustomTkinter: Aunque es una librería potente, la personalización de widgets y la gestión de capas en la interfaz resultó ser un proceso complejo. La IA fue clave para estructurar una UI limpia, funcional y libre de errores de renderizado.

Visualización en mapa (HTML): La creación del mapa interactivo requirió el uso de HTML y scripts que no forman parte de mi formación base. Delegué en la IA la generación de la estructura del mapa satelital y la lógica para que los marcadores mostraran información dinámica al pasar el cursor.

##💡 Reflexión del Autor

Este software es el resultado de mi capacidad para gestionar un proyecto de inicio a fin, utilizando la inteligencia artificial no solo para escribir código, sino para aprender e implementar tecnologías complejas (SQL, HTML, CustomTkinter) de forma acelerada y efectiva.
