from flask import Flask, request, render_template, url_for, redirect, session, jsonify, flash
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from werkzeug.security import generate_password_hash, check_password_hash
import os
from werkzeug.utils import secure_filename
from datetime import datetime

# Configuración inicial de la aplicación Flask
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'f6354bd9cc93da36b81ed71d9a8f4cb715d876e346d99cd7' # Cambia esto por una clave secreta real

# Configuración para la subida de imágenes
UPLOAD_FOLDER = 'static/images/profiles'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Inicialización de la base de datos SQLAlchemy
db = SQLAlchemy(app)
migrate = Migrate(app, db)

# Definición del modelo User para la base de datos
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    ips = db.relationship('UserIP', backref='user', lazy=True)
    profile_image = db.Column(db.String(200), default='default-profile.png')
    dob = db.Column(db.Date, nullable=True)
    phone = db.Column(db.String(20), nullable=True)
    phone_prefix = db.Column(db.String(5), nullable=True)

    def __repr__(self):
        return f'<User {self.email}>'

class UserIP(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    ip = db.Column(db.String(45), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    def __repr__(self):
        return f'<UserIP {self.ip}>'

# Función para obtener la IP del cliente
def get_client_ip():
    if request.headers.get('X-Forwarded-For'):
        return request.headers.get('X-Forwarded-For').split(',')[0]
    return request.remote_addr

# Función para verificar las extensiones de archivo permitidas
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Ruta principal y de index que renderiza la plantilla index.html
@app.route('/index')
def home():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    user = User.query.get(session['user_id'])
    return render_template('index.html', user=user)

# Ruta de registro de usuarios, acepta métodos GET y POST
@app.route('/registro', methods=['GET', 'POST'])
def registro():
    if request.method == 'POST':
        nombre = request.form.get('nombre')
        email = request.form.get('email')
        password = request.form.get('password')

        # Verificar si el correo electrónico ya está registrado
        user = User.query.filter_by(email=email).first()
        if user:
            return jsonify({"error": "El correo electrónico ya está registrado"}), 409

        # Crear un hash de la contraseña y registrar al nuevo usuario
        hashed_password = generate_password_hash(password)
        new_user = User(nombre=nombre, email=email, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()

        print(f"Usuario registrado: {nombre}, {email}, {hashed_password}")
        return jsonify({"message": "Usuario registrado con éxito, por favor haga click en Iniciar Sesión"})
    return render_template('registro.html')

# Ruta de inicio de sesión de usuarios, acepta métodos GET y POST
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        print(f"Intentando iniciar sesión con email: {email}")
        user = User.query.filter_by(email=email).first()
        if user:
            print(f"Usuario encontrado: {user.email}")
            print(f"Hash almacenado: {user.password}")
            if check_password_hash(user.password, password):
                # Obtener la IP del cliente
                client_ip = get_client_ip()
                # Verificar si la IP ya está registrada para el usuario
                user_ips = UserIP.query.filter_by(user_id=user.id).all()
                user_ips_str = [user_ip.ip for user_ip in user_ips]
                if client_ip not in user_ips_str:
                    if len(user_ips_str) >= 2:
                        return jsonify({"error": "Se ha alcanzado el máximo de 2 IPs"}), 403
                    new_user_ip = UserIP(ip=client_ip, user_id=user.id)
                    db.session.add(new_user_ip)
                    db.session.commit()

                session['user_id'] = user.id
                session['profile_image'] = user.profile_image
                print(f"Inicio de sesión exitoso para el usuario: {user.email} desde IP: {client_ip}")
                return jsonify({"redirect": url_for('home')})
            else:
                print("Contraseña incorrecta")
                return jsonify({"error": "Credenciales inválidas"}), 401
        else:
            print("Usuario no encontrado")
            return jsonify({"error": "Credenciales inválidas"}), 401

    return render_template('login.html')

# Ruta para el perfil del usuario
@app.route('/profile', methods=['GET', 'POST'])
def profile():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    user = User.query.get(session['user_id'])

    if request.method == 'POST':
        if 'profile_pic' in request.files:
            file = request.files['profile_pic']
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                file.save(file_path)
                user.profile_image = filename
                session['profile_image'] = filename
        user.nombre = request.form.get('name', user.nombre)
        user.email = request.form.get('email', user.email)
        dob = request.form.get('dob')
        user.dob = datetime.strptime(dob, '%Y-%m-%d').date() if dob else None
        user.phone = request.form.get('phone')
        user.phone_prefix = request.form.get('phone_prefix')

        db.session.commit()
        flash('Perfil actualizado con éxito', 'success')
        return redirect(url_for('profile'))

    return render_template('perfil.html', user=user)

# Ruta para cerrar sesión
@app.route('/logout')
def logout():
    # Eliminar el ID del usuario de la sesión
    session.pop('user_id', None)
    session.pop('profile_image', None)
    # Redirigir a la página de inicio de sesión
    return redirect(url_for('login'))

@app.route('/clases_en_vivo')
def clases_en_vivo():
    return render_template('clases_en_vivo.html')

@app.route('/mi_curso')
def mi_curso():
    return render_template('mi_curso.html')

@app.route('/herramientas')
def herramientas():
    return render_template('herramientas.html')

# Inicialización de la base de datos y ejecución de la aplicación
if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
    