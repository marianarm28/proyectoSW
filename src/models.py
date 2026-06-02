# src/models.py
from .database import db
from datetime import datetime

class Usuario(db.Model):
    """
    Modelo para la tabla 'usuarios'
    Mapea las historias: SCRUM-18 (Autenticación Segura) y SCRUM-19 (Roles de Acceso)
    """
    __tablename__ = 'usuarios'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    rol = db.Column(db.String(20), nullable=False) # 'Administrador', 'Tecnico', 'Operador'

    # Relación para saber qué mantenimientos tiene asignados este técnico
    mantenimientos_asignados = db.relationship('Mantenimiento', backref='tecnico', lazy=True)


class Activo(db.Model):
    """
    Modelo para la tabla 'activos'
    Mapea las historias: SCRUM-1 (Registro), SCRUM-2 (Categorías) y SCRUM-4 (Disponibilidad)
    """
    __tablename__ = 'activos'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nombre = db.Column(db.String(100), nullable=False)
    categoria = db.Column(db.String(50), nullable=False) # Ej: 'Maquinaria', 'Computo'
    estado = db.Column(db.String(30), default='Disponible') # Ej: 'Disponible', 'En Mantenimiento'
    fecha_ultimo_mantenimiento = db.Column(db.Date, nullable=True)
    dias_periodo_mantenimiento = db.Column(db.Integer, default=90) # Para Alertas por Tiempo (SCRUM-8)

    # CORRECCIÓN: Vinculamos correctamente con el nombre de la clase 'Mantenimiento'
    historial_mantenimientos = db.relationship('Mantenimiento', backref='activo', lazy=True, cascade="all, delete-orphan")


class Mantenimiento(db.Model):
    """
    Modelo para la tabla 'mantenimientos'
    Mapea las historias: SCRUM-8 (Alertas), SCRUM-12 (Asignación) y SCRUM-13 (Informe Técnico)
    """
    __tablename__ = 'mantenimientos'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    activo_id = db.Column(db.Integer, db.ForeignKey('activos.id', ondelete='CASCADE'), nullable=False)
    tecnico_id = db.Column(db.Integer, db.ForeignKey('usuarios.id', ondelete='CASCADE'), nullable=False)
    descripcion_intervencion = db.Column(db.Text, nullable=True) # Informe técnico
    fecha_intervencion = db.Column(db.DateTime, default=datetime.utcnow)