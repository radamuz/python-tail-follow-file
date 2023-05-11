from flask import Flask, render_template
from flask_socketio import SocketIO, emit
import threading
import time
import os

file_path = "text.txt"

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret_key'
socketio = SocketIO(app)

connected = False  # Variable global para verificar la conexión
send_thread = None  # Referencia al hilo send_message
last_modified_time = None  # Último tiempo de modificación del archivo
lines_sent = set()  # Conjunto de líneas ya enviadas

def send_message():
    while True:
        if not connected:
            break

        try:
            current_modified_time = get_modified_time(file_path)
            if current_modified_time != last_modified_time:
                last_modified_time = current_modified_time
                lines = get_new_lines()
                for line in lines:
                    if line not in lines_sent:
                        lines_sent.add(line)
                        socketio.emit('message', line.strip())
        except FileNotFoundError:
            pass

        time.sleep(1)

def get_modified_time(file_path):
    try:
        return os.path.getmtime(file_path)
    except FileNotFoundError:
        return None

def get_new_lines():
    with open(file_path, 'r') as file:
        all_lines = file.readlines()
        new_lines = []

        for line in all_lines:
            if line.strip() not in lines_sent:
                new_lines.append(line.strip())

        return new_lines

# Ruta para renderizar el archivo index.html
@app.route('/')
def index():
    return render_template('index.html')

# Ruta para la conexión del socket
@socketio.on('connect')
def handle_connect():
    global connected, send_thread, last_modified_time, lines_sent
    connected = True  # Establecer la variable global en True cuando se conecta el socket

    # Enviar las primeras líneas del archivo
    with open(file_path, 'r') as file:
        lines = file.readlines()
        for line in lines:
            socketio.emit('message', line.strip())
            lines_sent.add(line.strip())

    last_modified_time = get_modified_time(file_path)

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
