# src/app.py
from flask import Flask, jsonify, render_template, session, redirect, url_for
from .database import db, init_db
from .models import Usuario, Activo, Mantenimiento
from .auth import auth_bp
from .inventario import inventario_bp
# Importamos el módulo final de operaciones de mantenimiento (Módulo A)
from .mantenimiento import mantenimiento_bp

def create_app():
    app = Flask(__name__)
    
    # Llave secreta para manejo de sesiones seguras en las cookies del navegador
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
    # === RUTA PARA CREAR USUARIOS DE PRUEBA DESDE EL NAVEGADOR ===
    @app.route('/crear-usuario/<username>/<password>/<rol>')
    def crear_usuario_dinamico(username, password, rol):
        from src.models import Usuario
        from werkzeug.security import generate_password_hash
        from src.database import db

        with app.app_context():
            # Verificamos si ya existe el nombre para no duplicarlo
            if Usuario.query.filter_by(username=username).first():
                return f"<h3>El usuario '{username}' ya existe en Laragon.</h3>"

            # Creamos el nuevo usuario con el hash seguro
            nuevo = Usuario(
                username=username,
                password_hash=generate_password_hash(password),
                rol=rol # Recuerda poner: Administrador, Operador o Tecnico
            )
            db.session.add(nuevo)
            db.session.commit()
            return f"<h3>¡Éxito! Usuario '{username}' creado con el rol '{rol}'.</h3>"
        
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
    from src.models import Usuario
    from werkzeug.security import generate_password_hash
    from src.database import db

    with app.app_context():
        db.create_all()
        
        # 1. Aseguramos Administrador oficial
        if not Usuario.query.filter_by(username='admin_mm').first():
            admin = Usuario(
                username='admin_mm',
                password_hash=generate_password_hash('admin123'),
                rol='Administrador'
            )
            db.session.add(admin)
            
        # 2. Aseguramos Técnico oficial para las pruebas de Andrea
        tecnico_prueba = Usuario.query.filter_by(username='tecnico_a').first()
        if not tecnico_prueba:
            tec = Usuario(
                username='tecnico_a',
                password_hash=generate_password_hash('tecnico123'),
                rol='Tecnico' # <-- Coincide exactamente con la validación del backend
            )
            db.session.add(tec)
            db.session.commit()
            print("\n>>> Infraestructura lista: Creado 'admin_mm' y 'tecnico_a' con rol 'Tecnico' <<<\n")
        else:
            # Si ya existía, nos aseguramos de que su rol sea el correcto con mayúsculas
            tecnico_prueba.rol = 'Tecnico'
            db.session.commit()

    app.run(debug=True)
 