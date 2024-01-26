from flask import Flask, render_template, request, redirect, url_for
from app.models import Sujeto


app = Flask(__name__, template_folder='app/templates', static_folder='app/static')

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        nombre = request.form['nombre']
        apellido = request.form['apellido']
        edad = request.form['edad']
        return redirect(url_for('embed', nombre=nombre, apellido=apellido, edad=edad))
    return render_template('index.html')

@app.route('/gaze-tracking')
def embed():
    nombre = request.args.get('nombre')
    apellido = request.args.get('apellido')
    edad = request.args.get('edad')
    return render_template('embed.html', nombre=nombre, apellido=apellido, edad=edad)

if __name__ == '__main__':
    app.run(debug=True, ssl_context=('cert.pem', 'key.pem'))
