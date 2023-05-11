from flask import Flask, render_template
from flask_socketio import SocketIO, emit
import time
import threading
import subprocess
import json
import tailer

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret_key'
socketio = SocketIO(app)

# Ruta para renderizar el archivo index.html
@app.route('/')
def index():
    return render_template('index.html')

def send_message():
    # process = subprocess.Popen(['tail', '-f', 'text.txt'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    for line in tailer.follow(open('text.txt')):
        socketio.emit('message', line.strip())


# Ruta para la conexión del socket
@socketio.on('connect')
def handle_connect():
    # Iniciar el hilo para enviar mensajes
    send_thread = threading.Thread(target=send_message)
    send_thread.daemon = True  # Hacer que el hilo se detenga cuando se detenga el servidor Flask
    send_thread.start()

# Iniciar la aplicación Flask con SocketIO
if __name__ == '__main__':
    socketio.run(app)
