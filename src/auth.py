# src/auth.py
from flask import Blueprint, request, jsonify, session, current_app
from werkzeug.security import check_password_hash
from .models import Usuario
from .database import db

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/api/login', methods=['POST'])
def login():
    """
    Mapea la historia: SCRUM-18 (Autenticación Segura)
    """
    with current_app.app_context():
        try:
            if request.is_json:
                data = request.get_json()
            else:
                data = request.form

            if not data or 'username' not in data or 'password' not in data:
                return jsonify({
                    "status": "error", 
                    "message": "Faltan datos de ingreso (username o password)."
                }), 400

            username_input = data['username']
            password_input = data['password']

            # Buscamos el usuario en MySQL
            usuario = Usuario.query.filter_by(username=username_input).first()

            # --- VALIDACIÓN CRUCIAL ---
            if usuario and check_password_hash(usuario.password_hash, password_input):
                # Si entra aquí, guardamos los datos en la sesión
                session['usuario_id'] = usuario.id
                session['username'] = usuario.username
                session['rol'] = usuario.rol

                # RETORNAMOS ÉXITO DE INMEDIATO Y DETENEMOS LA FUNCIÓN (Evita seguir derecho)
                return jsonify({
                    "status": "success",
                    "message": f"Autenticación exitosa. Bienvenido {usuario.username}.",
                    "user": {
                        "username": usuario.username,
                        "rol": usuario.rol
                    }
                }), 200
            
            # Si no entra al IF de arriba, significa que sí son inválidas
            return jsonify({
                "status": "error",
                "message": "Credenciales inválidas. Intente nuevamente."
            }), 401

        except Exception as e:
            return jsonify({
                "status": "error",
                "message": f"Error de base de datos: {str(e)}"
            }), 500



@auth_bp.route('/api/logout', methods=['POST'])
def logout():
    session.clear()
    return jsonify({
        "status": "success",
        "message": "Sesión cerrada correctamente."
    }), 200


def requerir_rol(roles_permitidos):
    if 'usuario_id' not in session:
        return {"autorizado": False, "error": "Acceso denegado. No autenticado.", "status_code": 401}
    if session.get('rol') not in roles_permitidos:
        return {"autorizado": False, "error": "Acceso denegado. Permisos insuficientes.", "status_code": 403}
    return {"autorizado": True}