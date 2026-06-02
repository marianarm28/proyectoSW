# src/app.py
from flask import Flask, jsonify, render_template, session, redirect, url_for
from .database import db, init_db
from .models import Usuario, Activo, Mantenimiento
from .auth import auth_bp
from .inventario import inventario_bp
from .mantenimiento import mantenimiento_bp

def create_app():
    app = Flask(__name__)
    
    app.config['SECRET_KEY'] = 'clave_secreta_scrum_sprint1_2026'

    init_db(app)

    # --- REGISTRO DE TODOS LOS BLUEPRINTS (MÓDULOS JIRA) ---
    app.register_blueprint(auth_bp)         # Seguridad (MM)
    app.register_blueprint(inventario_bp)   # Inventario (DJ)
    app.register_blueprint(mantenimiento_bp) # Mantenimiento (A)

    # --- RUTAS DE NAVEGACIÓN PRINCIPALES (FRONTEND) ---
    @app.route('/', methods=['GET'])
    def index():
        if 'usuario_id' in session:
            return redirect(url_for('vista_inventario'))
        return render_template('login.html')

    @app.route('/inventario', methods=['GET'])
    def vista_inventario():
        if 'usuario_id' not in session:
            return redirect(url_for('index'))
        return render_template('inventario.html')

    @app.route('/mantenimiento', methods=['GET'])
    def vista_mantenimiento():
        """
        Carga la pantalla visual de control de mantenimientos y alertas (Módulo A).
        """
        if 'usuario_id' not in session:
            return redirect(url_for('index'))
        return render_template('mantenimiento.html')

    # Ruta de verificación del estado de la conexión
    @app.route('/api/healthcheck', methods=['GET'])
    def healthcheck():
        try:
            primer_usuario = Usuario.query.first()
            if primer_usuario:
                return jsonify({
                    "status": "success",
                    "message": "Conexión a MySQL exitosa de forma directa",
                    "database": "scrum_inventario",
                    "test_user": primer_usuario.username
                }), 200
            return jsonify({"status": "warning", "message": "Tabla usuarios vacía."}), 200
        except Exception as e:
            return jsonify({"status": "error", "message": f"Fallo en BD: {str(e)}"}), 500

    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)