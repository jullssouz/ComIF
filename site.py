from datetime import datetime, time
from functools import wraps
from flask import Flask, render_template, request, redirect, url_for, session, flash, abort
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.secret_key = 'omelhorteceirodetodos'

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///comif.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

class Nutricionista(db.Model):
    __tablename__ = 'nutricionista'
    
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    senha = db.Column(db.String(100), nullable=False)

class Cardapio(db.Model):
    __tablename__ = 'cardapio'
    
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    tipo = db.Column(db.String(50), nullable=False)
    ingredientes = db.Column(db.Text, nullable=False)
    data = db.Column(db.Date, nullable=False)       


@app.route('/')
def index():
    return render_template('login.html')

@app.route('/login', methods=['POST'])
def login():
    email = request.form.get('email')
    senha = request.form.get('senha')

    usuario = Nutricionista.query.filter_by(email=email).first()

    if usuario and usuario.senha == senha:
        session['usuario_id'] = usuario.id
        session['nome'] = usuario.nome
        session['tipo_usuario'] = 'nutricionista'
        
        return redirect(url_for('alunovisualizar'))
    else:
        flash('E-mail ou senha incorretos!', 'erro')
        return redirect(url_for('index'))

@app.route('/login-aluno')
def login_aluno():
    session['nome'] = 'Aluno'
    session['tipo_usuario'] = 'visualizador'
    
    return redirect(url_for('alunovisualizar'))

def nutricionista_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get('tipo_usuario') != 'nutricionista':
            flash('Acesso negado! Apenas nutricionistas podem realizar esta ação.', 'erro')
            return redirect(url_for('alunovisualizar'))
        return f(*args, **kwargs)
    return decorated_function

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

@app.route('/cardapio')
def alunovisualizar():
    if not session.get('tipo_usuario'):
        return redirect(url_for('index'))

    tipo_refeicao = request.args.get('tipo', 'cafe')

    cardapios_db = Cardapio.query.filter_by(tipo=tipo_refeicao).order_by(Cardapio.data.desc()).all()

    pode_editar = (session.get('tipo_usuario') == 'nutricionista')

    return render_template('alunovisualizar.html', cardapios=cardapios_db, tipo_refeicao=tipo_refeicao, pode_editar=pode_editar)

@app.route('/cardapio/cadastrar', methods=['GET', 'POST'])
@nutricionista_required
def cadastrar_cardapio():
    if request.method == 'POST':
        nome = request.form.get('nome')
        tipo = request.form.get('tipo')
        data_str = request.form.get('data')
        ingredientes = request.form.get('ingredientes')
        
        if not data_str:
            flash('Por favor, selecione uma data válida!', 'erro')
            return redirect(url_for('cadastrar_cardapio'))

        if tipo not in ['cafe', 'almoco']:
            flash('Por favor, selecione uma opção de refeição válida!', 'erro')
            return redirect(url_for('cadastrar_cardapio'))

        data_formatada = datetime.strptime(data_str, '%Y-%m-%d').date()

        novo_cardapio = Cardapio(
            nome=nome,
            tipo=tipo,
            data=data_formatada,
            ingredientes=ingredientes
        )

        db.session.add(novo_cardapio)
        db.session.commit()

        flash('Nova refeição cadastrada com sucesso!', 'sucesso')
        return redirect(url_for('alunovisualizar', tipo=tipo))

    return render_template('cadastrar_cardapio.html')

@app.route('/cardapio/editar/<int:id>', methods=['GET', 'POST'])
@nutricionista_required
def editar_cardapio(id):
    cardapio = Cardapio.query.get_or_404(id)

    if request.method == 'POST':
        cardapio.nome = request.form.get('nome')
        cardapio.tipo = request.form.get('tipo')
        cardapio.ingredientes = request.form.get('ingredientes')
        
        data_str = request.form.get('data')
        
        if not data_str:
            flash('Por favor, selecione uma data válida!', 'erro')
            return redirect(url_for('editar_cardapio', id=id))

        cardapio.data = datetime.strptime(data_str, '%Y-%m-%d').date()

        db.session.commit()
        flash('Cardápio atualizado com sucesso!', 'sucesso')

        return redirect(url_for('alunovisualizar', tipo=cardapio.tipo))

    return render_template('editar_cardapio.html', cardapio=cardapio)

@app.route('/cardapio/deletar/<int:id>')
@nutricionista_required
def deletar_cardapio(id):
    cardapio = Cardapio.query.get_or_404(id)
    tipo_antigo = cardapio.tipo

    agora = datetime.now()
    hoje = agora.date()
    hora_limite = time(10, 0)  

    if cardapio.data < hoje:
        flash('Não é possível excluir cardápios de datas passadas!', 'erro')
        return redirect(url_for('alunovisualizar', tipo=tipo_antigo))


    if cardapio.data == hoje and agora.time() >= hora_limite:
        flash('Não é possível excluir o cardápio do dia após as 10:00!', 'erro')
        return redirect(url_for('alunovisualizar', tipo=tipo_antigo))

    db.session.delete(cardapio)
    db.session.commit()

    flash('Refeição excluída com sucesso!', 'sucesso')
    return redirect(url_for('alunovisualizar', tipo=tipo_antigo))

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)