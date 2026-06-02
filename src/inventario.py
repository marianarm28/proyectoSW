# src/inventario.py
from flask import Blueprint, request, jsonify, session, current_app
from .models import Activo
from .database import db
from .auth import requerir_rol

# Creamos el Blueprint para el módulo de inventario (Módulo DJ)
inventario_bp = Blueprint('inventario', __name__)

@inventario_bp.route('/api/activos', methods=['POST'])
def registrar_activo():
    """
    Mapea las historias: 
    - SCRUM-1: Registro de Activos (Guarda en BD)
    - SCRUM-2: Clasificación por Categorías (Recibe el campo categoría)
    - SCRUM-4: Estado de Disponibilidad (Por defecto inicia como 'Disponible')
    """
    # SCRUM-19: Protección por rol. Solo 'Administrador' u 'Operador' pueden registrar
    validacion = requerir_rol(['Administrador', 'Operador'])
    if not validacion.get('autorizado'):
        return jsonify({"status": "error", "message": validacion.get('error')}), validacion.get('status_code')

    with current_app.app_context():
        try:
            data = request.get_json()
            if not data or 'nombre' not in data or 'categoria' not in data:
                return jsonify({
                    "status": "error",
                    "message": "Faltan datos obligatorios (nombre o categoria)."
                }), 400

            # Creamos la nueva instancia del Activo mapeando los datos recibidos
            nuevo_activo = Activo(
                nombre=data['nombre'],
                categoria=data['categoria'], # SCRUM-2: Clasificación
                estado=data.get('estado', 'Disponible'), # SCRUM-4: Estado por defecto
                dias_periodo_mantenimiento=data.get('dias_periodo', 90)
            )

            # Guardamos el activo de forma física en la base de datos MySQL
            db.session.add(nuevo_activo)
            db.session.commit()

            return jsonify({
                "status": "success",
                "message": "Activo registrado exitosamente en el inventario.",
                "activo": {
                    "id": nuevo_activo.id,
                    "nombre": nuevo_activo.nombre,
                    "categoria": nuevo_activo.categoria,
                    "estado": nuevo_activo.estado
                }
            }), 201

        except Exception as e:
            db.session.rollback()
            return jsonify({
                "status": "error",
                "message": f"Error al registrar el activo: {str(e)}"
            }), 500


@inventario_bp.route('/api/activos', methods=['GET'])
def listar_activos():
    """
    Permite consultar todos los activos existentes en el sistema.
    Ayuda a verificar visualmente el estado del inventario.
    """
    # Cualquier usuario autenticado (Admin, Técnico u Operador) puede listar el inventario
    if 'usuario_id' not in session:
        return jsonify({"status": "error", "message": "Acceso denegado. No autenticado."}), 401

    with current_app.app_context():
        try:
            activos = Activo.query.all()
            lista_activos = []
            
            for activo in activos:
                lista_activos.append({
                    "id": activo.id,
                    "nombre": activo.nombre,
                    "categoria": activo.categoria,
                    "estado": activo.estado,
                    "fecha_ultimo_mantenimiento": str(activo.fecha_ultimo_mantenimiento) if activo.fecha_ultimo_mantenimiento else "Ninguno"
                })

            return jsonify({
                "status": "success",
                "activos": lista_activos
            }), 200

        except Exception as e:
            return jsonify({
                "status": "error",
                "message": f"Error al consultar el inventario: {str(e)}"
            }), 500
        
@inventario_bp.route('/api/activos/<int:id>', methods=['PUT'])
def modificar_activo(id):
    """
    Cubre la 'U' del CRUD (Actualización de datos básicos)
    """
    validacion = requerir_rol(['Administrador', 'Operador'])
    if not validacion.get('autorizado'):
        return jsonify({"status": "error", "message": validacion.get('error')}), validacion.get('status_code')

    with current_app.app_context():
        try:
            data = request.get_json()
            activo = Activo.query.get(id)
            if not activo:
                return jsonify({"status": "error", "message": "Activo no encontrado."}), 404

            activo.nombre = data.get('nombre', activo.nombre)
            activo.categoria = data.get('categoria', activo.categoria)
            activo.estado = data.get('estado', activo.estado)

            db.session.commit()
            return jsonify({"status": "success", "message": "Activo actualizado correctamente."}), 200
        except Exception as e:
            db.session.rollback()
            return jsonify({"status": "error", "message": str(e)}), 500

@inventario_bp.route('/api/activos/<int:id>', methods=['DELETE'])
def eliminar_activo(id):
    """
    Cubre la 'D' del CRUD (Eliminación física del activo)
    """
    validacion = requerir_rol(['Administrador'])
    if not validacion.get('autorizado'):
        return jsonify({"status": "error", "message": validacion.get('error')}), validacion.get('status_code')

    with current_app.app_context():
        try:
            activo = Activo.query.get(id)
            if not activo:
                return jsonify({"status": "error", "message": "Activo no encontrado."}), 404

            db.session.delete(activo)
            db.session.commit()
            return jsonify({"status": "success", "message": "Activo eliminado del sistema correctamente."}), 200
        except Exception as e:
            db.session.rollback()
            return jsonify({"status": "error", "message": str(e)}), 500