import os
from flask import Flask, render_template, request, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.secret_key = os.urandom(24)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
db = SQLAlchemy(app)

# Modelo de usuário
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)

# Modelo de configurações
class Config(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    stream_type = db.Column(db.String(80), nullable=False)
    destinations = db.Column(db.Text, nullable=False)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()

        if user and user.password == password:
            session['user_id'] = user.id
            return redirect(url_for('index'))
        else:
            return 'Invalid username or password', 403

    return render_template('login.html')

@app.route('/')
def index():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    horizontal_config = Config.query.filter_by(stream_type='horizontal').first()
    vertical_config = Config.query.filter_by(stream_type='vertical').first()
    
    return render_template('index.html', horizontal=horizontal_config, vertical=vertical_config)

@app.route('/settings', methods=['GET', 'POST'])
def settings():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    if request.method == 'POST':
        # Processa os destinos horizontais
        horizontal_servers = request.form.getlist('horizontal_server[]')
        horizontal_keys = request.form.getlist('horizontal_key[]')
        
        horizontal_destinations = []
        for server, key in zip(horizontal_servers, horizontal_keys):
            horizontal_destinations.append(f"{server} - {key}")
        
        horizontal_destinations_str = "\n".join(horizontal_destinations)

        # Processa os destinos verticais
        vertical_servers = request.form.getlist('vertical_server[]')
        vertical_keys = request.form.getlist('vertical_key[]')
        
        vertical_destinations = []
        for server, key in zip(vertical_servers, vertical_keys):
            vertical_destinations.append(f"{server} - {key}")
        
        vertical_destinations_str = "\n".join(vertical_destinations)

        # Atualiza ou cria os registros de destinos no banco de dados
        horizontal_config = Config.query.filter_by(stream_type='horizontal').first()
        if horizontal_config:
            horizontal_config.destinations = horizontal_destinations_str
        else:
            new_config = Config(stream_type='horizontal', destinations=horizontal_destinations_str)
            db.session.add(new_config)

        vertical_config = Config.query.filter_by(stream_type='vertical').first()
        if vertical_config:
            vertical_config.destinations = vertical_destinations_str
        else:
            new_config = Config(stream_type='vertical', destinations=vertical_destinations_str)
            db.session.add(new_config)

        db.session.commit()
        return redirect(url_for('index'))

    horizontal_config = Config.query.filter_by(stream_type='horizontal').first()
    vertical_config = Config.query.filter_by(stream_type='vertical').first()
    
    return render_template('settings.html', horizontal=horizontal_config, vertical=vertical_config)


# Iniciar o contexto da aplicação para a criação do banco de dados
if __name__ == "__main__":
    with app.app_context():
        db.create_all()  # Cria as tabelas se ainda não existirem
    app.run(host='0.0.0.0', port=5000)
