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

🤖 Uso de IA Generativa
En este proyecto, la IA no fue solo un asistente de consulta, sino una herramienta de ingeniería. La utilicé activamente para: * Migración de Datos: Traducir la estructura inicial de almacenamiento en CSV hacia un modelo relacional en SQLite.

Resolución de Bugs de Despliegue: Diagnosticar y corregir falsos positivos en antivirus durante el empaquetado con Inno Setup.

Documentación Técnica: Optimizar la claridad de los comentarios en el código y la estructura de este repositorio.
