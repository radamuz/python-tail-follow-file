from flask import Flask, render_template
from flask_socketio import SocketIO, emit
import threading
import subprocess
from collections import deque

file_path = "text.txt"

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret_key'
socketio = SocketIO(app)

connected = False  # Variable global para verificar la conexión
send_thread = None  # Referencia al hilo send_message

# Ruta para renderizar el archivo index.html
@app.route('/')
def index():
    return render_template('index.html')

def send_message():
    command = f'tail -f {file_path}'
    process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)

    while True:
        if not connected:
            break

        output = process.stdout.readline().decode().strip()
        if output == '' and process.poll() is not None:
            break
        if output:
            socketio.emit('message', output)

# Ruta para la conexión del socket
@socketio.on('connect')
def handle_connect():
    global connected, send_thread
    connected = True  # Establecer la variable global en True cuando se conecta el socket

    # Enviar las primeras líneas del archivo
    with open(file_path, 'r') as file:
        lines = file.readlines()
        for line in lines:
            socketio.emit('message', line.strip())

    if send_thread is None or not send_thread.is_alive():
        # Si no hay un hilo en ejecución, o el hilo anterior ha finalizado, crear uno nuevo
        send_thread = threading.Thread(target=send_message)
        send_thread.daemon = True  # Hacer que el hilo se detenga cuando se detenga el servidor Flask
        send_thread.start()

@socketio.on('disconnect')
def handle_disconnect():
    global connected
    connected = False  # Establecer la variable global en False cuando se desconecta el socket

# Iniciar la aplicación Flask con SocketIO
if __name__ == '__main__':
    socketio.run(app, host="0.0.0.0")
