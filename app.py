from flask import Flask, render_template
from flask_socketio import SocketIO, emit
import threading
import subprocess
from collections import deque

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret_key'
socketio = SocketIO(app)

# Ruta para renderizar el archivo index.html
@app.route('/')
def index():
    return render_template('index.html')

def send_message():
    with open('text.txt', 'r') as file:
        buffer = deque(maxlen=10)  # Crear un búfer de longitud máxima 10
        for line in file:
            buffer.append(line.strip())  # Agregar cada línea al búfer
            if len(buffer) == 10:
                # Una vez que el búfer esté lleno, comenzar a emitir las líneas
                for line_to_emit in buffer:
                    socketio.emit('message', line_to_emit)
                buffer.clear()  # Limpiar el búfer

        # Después de procesar todas las líneas del archivo, emitir las líneas restantes en el búfer
        for line_to_emit in buffer:
            socketio.emit('message', line_to_emit)

    command = 'tail -f text.txt'
    process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)

    while True:
        output = process.stdout.readline().decode().strip()
        if output == '' and process.poll() is not None:
            break
        if output:
            socketio.emit('message', output)

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
