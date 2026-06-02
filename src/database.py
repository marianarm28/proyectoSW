# src/database.py
from flask_sqlalchemy import SQLAlchemy

# Inicializamos la extensión SQLAlchemy que manejará los modelos de datos
db = SQLAlchemy()

def init_db(app):
    """
    Configura la conexión a MySQL usando los parámetros predeterminados de Laragon:
    - Usuario: root
    - Contraseña: (vacía)
    - Host: localhost (127.0.0.1)
    - Base de datos: scrum_inventario
    """
    app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:@localhost/scrum_inventario'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    # Vinculamos la base de datos con nuestra aplicación de Flask
    db.init_app(app)