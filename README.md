# Plataforma Web C2C para Moda Urbana (Streetwear)

Este proyecto corresponde a la Etapa 1 de la Asignatura ICI324 - Bases de Datos y Programación Web. Es una plataforma e-commerce tipo marketplace C2C diseñada para centralizar el catálogo de moda urbana entre particulares, automatizar el filtrado de productos y facilitar transacciones seguras mediante un chat integrado.

**Desarrollado por el Grupo N° 14:** Pedro Jeria, Diego Valenzuela y Anais Muñoz.
## Stack Tecnológico
* **Backend:** Python 3.9+ / Django 5.x
* **Base de Datos:** PostgreSQL 15+ (vía OrbStack / Docker) / Django ORM
* **Frontend:** Plantillas HTML de Django (Arquitectura MVT)

## Estructura del Proyecto

El código está estructurado separando las responsabilidades de la lógica del sistema, la base de datos y la interfaz, para asegurar una alta mantenibilidad

* `core/models.py`: Implementación del Modelo Relacional con todas las entidades (Usuario, Artículo, Venta, Chat, etc.) e integridad referencial (CASCADE, RESTRICT, SET NULL).
* `core/views.py`: Lógica principal de la aplicación, incluyendo el filtrado obligatorio (categoría y precio) y opcional del catálogo.
* `core/views_ventas.py`: Módulo separado que maneja la lógica transaccional de las ventas y la actualización de stock en la base de datos.
* `core/templates/core/`: Interfaces de usuario responsivas renderizadas desde el servidor.
* `consultas_rubricas.sql`: Script exigido para la evaluación que contiene más de 10 consultas operativas (Selects con JOIN, CRUD, agrupaciones) que demuestran la trazabilidad del modelo.
* `poblar_datos.sql`: Script SQL para la carga inicial de registros de prueba (usuarios, categorías, artículos).
* `sincronizar_secuencias_postgres.sql`: Script de mantenimiento para sincronizar los índices autoincrementales (`AutoField`) de PostgreSQL tras la inserción manual de datos.

## Guía de Instalación y Despliegue Local

### 1. Clonar y preparar el entorno
```bash
git clone https://github.com/Titowo/proyecto_db.git
cd streetwear_c2c

# Crear y activar entorno virtual
python3 -m venv venv
source venv/bin/activate

# Instalar dependencias (Django, psycopg2-binary, etc.)
pip install -r requirements.txt
