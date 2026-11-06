# Proyecto DB - Streetwear C2C (Versión MongoDB)

Plataforma e-commerce C2C (Consumer-to-Consumer) enfocada en la compra y venta de ropa *streetwear*. Esta rama del proyecto está adaptada para utilizar **MongoDB** como motor de base de datos principal, integrando todo el flujo de ventas, gestión de usuarios y catálogo mediante Django.

## 🚀 Características Principales

* **Catálogo y Productos:** Exploración de productos, vistas detalladas y sistema de publicación para vendedores.
* **Carrito de Compras:** Gestión del carrito y procesamiento de ventas.
* **Sistema de Usuarios:** Registro, login, perfiles de usuario y asignación de roles (administradores y clientes).
* **Chat Integrado:** Comunicación directa dentro de la plataforma (`chat.html`).
* **API RESTful:** Endpoints dedicados para consumo externo o asíncrono:
  * `api_articulos.py`: Gestión de catálogo.
  * `api_ventas.py`: Procesamiento de transacciones.
  * `api_auth.py`: Autenticación de usuarios.
* **Mockups Estáticos:** Carpeta independiente (`mockups/`) con las maquetas originales en HTML/CSS/JS.

## 🛠️ Stack Tecnológico

* **Backend:** Python 3, Django
* **Base de Datos:** MongoDB
* **Frontend:** HTML5, CSS3, Vanilla JavaScript (sin frameworks pesados)
* **Estilos:** Archivos estáticos modulares (`core/static/core/css/styles.css`)

## 📁 Estructura del Proyecto

El código está organizado en las siguientes aplicaciones y directorios clave:

* `streetwear_c2c/`: Configuración principal de Django (`settings.py`, `urls.py`, entorno asíncrono/síncrono).
* `core/`: Aplicación principal que contiene la lógica de negocio.
  * `models.py` / `views.py` / `urls.py`: Arquitectura MVT estándar de Django.
  * `templates/core/`: Plantillas HTML (catálogo, carrito, login, perfil, producto, publicar, chat).
  * `static/core/`: Assets estáticos (CSS, JS).
  * Archivos `api_*.py`: Controladores de la API REST.
* `mockups/`: Diseños frontend crudos de referencia.

## ⚙️ Instalación y Configuración

### 1. Clonar el repositorio y preparar el entorno
```bash
git clone <tu-repositorio>
cd proyecto_db-version-mongodb
python -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate
