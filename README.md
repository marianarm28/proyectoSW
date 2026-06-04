# Sistema de Gestión de Activos y Mantenimiento Preventivo (SGAMP)
> **Asignatura:** Ingeniería de Software I  
> **Sprint 1:** Autenticación Segura, Gestión de Inventario y Control de Mantenimiento.

---

## 👥 Integrantes del Equipo y Mapeo Scrum
* **Mariana Romero.** (Módulo de Autenticación Segura y Roles - SCRUM-18 & SCRUM-19)
* **David Lopez.** (Módulo de Gestión de Inventario  - SCRUM-1, SCRUM-2 & SCRUM-4)
* **Andrea Castro.** (Módulo de Mantenimiento - SCRUM-8, SCRUM-12 & SCRUM-13)

---

## 🛠️ Stack Tecnológico e Infraestructura
* **Backend:** Python 3.10+ con **Flask** (Micro-framework)
* **Base de Datos:** **MySQL** gestionado localmente mediante **Laragon**
* **ORM:** Flask-SQLAlchemy (Mapeo Objeto-Relacional para consultas seguras)
* **Seguridad:** Encriptación criptográfica de contraseñas mediante `Werkzeug` (`pbkdf2:sha256`)
* **Frontend:** HTML5, CSS3 (Bootstrap 5) y JavaScript Asíncrono (Fetch API en formato JSON)



## 🚀 Guía de Instalación y Ejecución Local

Sigue estos pasos exactos para desplegar el entorno de desarrollo en tu máquina:

### 1. Requisitos Previos
* Tener instalado Laragon o XAMPP con el motor de MySQL encendido.
* Tener instalado Python 3.10 o superior.

### 2. Configuración de la Base de Datos
1. Abre Laragon y presiona **Iniciar todo**.
2. Entra a la herramienta de base de datos (HeidiSQL o phpMyAdmin).
3. Crea una base de datos vacía llamada exactamente: `scrum_inventario`.
> *Nota: El sistema implementa la persistencia automática. Las tablas (`usuarios`, `activos`, `mantenimientos`) se crearán solas la primera vez que se ejecute el backend.*

### 3. Clonar el Repositorio e Instalar Dependencias 

Abre tu terminal en VS Code y ejecuta:
``bash
# Clonar el proyecto
* git clone https://github.com/marianarm28/proyectoSW.git
* cd proyectoSW

# Instalar las librerías necesarias
pip install flask flask-sqlalchemy pymysql cryptography werkzeug
---
### 4. Ejecución del Servidor
* Para levantar el servidor de desarrollo en la dirección local http://127.0.0.1:5000, ejecuta el comando modular:
* python -m src.app

## 🔐 Credenciales de Prueba

* admin_mm
* admin123

## 📌 Arquitectura del Proyecto (Patrón de Diseño)
El proyecto implementa un patrón de diseño Fábrica de Aplicaciones (Application Factory) combinado con Blueprints, permitiendo la escalabilidad modular requerida en metodologías ágiles:


* proyectoSW/
* │
* ├── src/
* │  
* │   ├── app.py               # Punto de entrada, inicialización e inyección de datos de prueba
* │   ├── database.py          # Configuración del pool de conexiones a MySQL (SQLAlchemy)
* │   ├── models.py            # Modelos del sistema (Tablas de base de datos relacional)
* │   ├── auth.py              # Controlador API y Vistas de Seguridad (Mariana)
* │   ├── inventario.py        # Controlador API y Vistas de Inventario (David)
* │   └── mantenimiento.py     # Controlador API y Vistas de Mantenimiento (Andrea)
* │
* └── templates/               # Capa de presentación (Frontend)
*     ├── login.html           # Interfaz de acceso
*     ├── inventario.html      # Panel de administración de activos médicos
*     └── mantenimiento.html   # Monitor de alertas e informes técnicos
