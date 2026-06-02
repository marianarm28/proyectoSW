# src/mantenimiento.py
from flask import Blueprint, request, jsonify, session, current_app
from .models import Activo, Mantenimiento, Usuario
from .database import db
from .auth import requerir_rol
from datetime import datetime, date


mantenimiento_bp = Blueprint('mantenimiento', __name__)

@mantenimiento_bp.route('/api/mantenimiento/alertas', methods=['GET'])
def alertas_tiempo():
    """
    Mapea la historia: SCRUM-8 (Alertas por Tiempo)
    Calcula qué activos necesitan mantenimiento con base en los días transcurridos 
    desde su último registro o si nunca han recibido uno.
    """
    if 'usuario_id' not in session:
        return jsonify({"status": "error", "message": "No autenticado."}), 401

    with current_app.app_context():
        try:
            activos = Activo.query.all()
            alertas = []
            hoy = date.today()

            for activo in activos:
                necesita_mantenimiento = False
                dias_transcurridos = None

                if activo.fecha_ultimo_mantenimiento:
                    # Calculamos la diferencia de días entre hoy y el último mantenimiento
                    dias_transcurridos = (hoy - activo.fecha_ultimo_mantenimiento).days
                    if dias_transcurridos >= activo.dias_periodo_mantenimiento:
                        necesita_mantenimiento = True
                else:
                    # Si nunca ha tenido mantenimiento, requiere uno de forma preventiva inmediata
                    necesita_mantenimiento = True
                    dias_transcurridos = "Ninguno"

                if necesita_mantenimiento:
                    alertas.append({
                        "id": activo.id,
                        "nombre": activo.nombre,
                        "categoria": activo.categoria,
                        "estado": activo.estado,
                        "dias_transcurridos": dias_transcurridos,
                        "limite_dias": activo.dias_periodo_mantenimiento
                    })

            return jsonify({"status": "success", "alertas": alertas}), 200
        except Exception as e:
            return jsonify({"status": "error", "message": f"Error al calcular alertas: {str(e)}"}), 500


@mantenimiento_bp.route('/api/mantenimiento/asignar', methods=['POST'])
def asignar_responsable():
    """
    Mapea la historia: SCRUM-12 (Asignación de Responsable)
    Permite vincular a un técnico a un activo y cambia el estado del equipo a 'En Mantenimiento'.
    """
    # Protección por rol: Operadores o Administradores gestionan las asignaciones
    validacion = requerir_rol(['Administrador', 'Operador'])
    if not validacion.get('autorizado'):
        return jsonify({"status": "error", "message": validacion.get('error')}), validacion.get('status_code')

    with current_app.app_context():
        try:
            data = request.get_json()
            if not data or 'activo_id' not in data or 'tecnico_id' not in data:
                return jsonify({"status": "error", "message": "Faltan datos (activo_id o tecnico_id)."}), 400

            activo = Activo.query.get(data['activo_id'])
            tecnico = Usuario.query.filter_by(id=data['tecnico_id'], rol='Tecnico').first()

            if not activo:
                return jsonify({"status": "error", "message": "El activo especificado no existe."}), 404
            if not tecnico:
                return jsonify({"status": "error", "message": "El usuario asignado no existe o no cuenta con el rol de Tecnico."}), 400

            # SCRUM-4: Actualizamos dinámicamente el estado del activo a 'En Mantenimiento'
            activo.estado = 'En Mantenimiento'

            # Guardamos el registro base de la asignación de mantenimiento
            nueva_orden = Mantenimiento(
                activo_id=activo.id,
                tecnico_id=tecnico.id,
                descripcion_intervencion="Asignado. Pendiente por informe técnico."
            )

            db.session.add(nueva_orden)
            db.session.commit()

            return jsonify({
                "status": "success",
                "message": f"Activo '{activo.nombre}' asignado correctamente al técnico {tecnico.username}."
            }), 200

        except Exception as e:
            db.session.rollback()
            return jsonify({"status": "error", "message": f"Error en la asignación: {str(e)}"}), 500


@mantenimiento_bp.route('/api/mantenimiento/informe', methods=['POST'])
def registrar_informe():
    """
    Mapea la historia: SCRUM-13 (Informe de Intervención Técnica)
    Permite al Técnico describir qué reparaciones hizo, guarda el reporte y devuelve el activo a 'Disponible'.
    """
    # Protección por rol: Solo los usuarios con rol 'Tecnico' ejecutan y cierran la orden
    validacion = requerir_rol(['Tecnico', 'Administrador'])
    if not validacion.get('autorizado'):
        return jsonify({"status": "error", "message": validacion.get('error')}), validacion.get('status_code')

    with current_app.app_context():
        try:
            data = request.get_json()
            if not data or 'activo_id' not in data or 'descripcion' not in data:
                return jsonify({"status": "error", "message": "Faltan campos obligatorios (activo_id o descripcion)."}), 400

            # Buscamos el último mantenimiento abierto para ese activo
            mantenimiento = Mantenimiento.query.filter_by(activo_id=data['activo_id']).order_by(Mantenimiento.id.desc()).first()
            activo = Activo.query.get(data['activo_id'])

            if not activo:
                return jsonify({"status": "error", "message": "El activo no existe."}), 404

            # Guardamos la descripción técnica de la intervención (SCRUM-13)
            if mantenimiento:
                mantenimiento.descripcion_intervencion = data['descripcion']
                mantenimiento.fecha_intervencion = datetime.utcnow()
            else:
                # Si no había orden previa, creamos una directa para dejar el historial asentado
                mantenimiento = Mantenimiento(
                    activo_id=activo.id,
                    tecnico_id=session['usuario_id'],
                    descripcion_intervencion=data['descripcion']
                )
                db.session.add(mantenimiento)

            # Actualizamos metadatos del activo para limpiar alertas por tiempo
            activo.estado = 'Disponible'
            activo.fecha_ultimo_mantenimiento = date.today()

            db.session.commit()

            return jsonify({
                "status": "success",
                "message": "Informe técnico guardado exitosamente. El activo vuelve a estar Disponible."
            }), 200

        except Exception as e:
            db.session.rollback()
            return jsonify({"status": "error", "message": f"Error al registrar informe: {str(e)}"}), 500