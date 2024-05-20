import threading
import socket
import sqlite3
import bcrypt
import os

def init_db():
    conn = sqlite3.connect('chat.db')
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS messages (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        user TEXT,
                        message TEXT,
                        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP)''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS users (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        username TEXT UNIQUE,
                        password TEXT)''')
    conn.commit()
    conn.close()

def client_handler(client_socket, client_address):
    authenticated = False
    username = None
    while True:
        try:
            data = client_socket.recv(1024)
            if not data:
                break
            message = data.decode('utf-8')
            if not authenticated:
                if message.startswith("register|"):
                    parts = message.split('|')
                    if len(parts) == 3:
                        username = parts[1]
                        password = parts[2]
                        if register_user(username, password):
                            client_socket.send("REGISTER_SUCCESS".encode('utf-8'))
                        else:
                            client_socket.send("REGISTER_FAIL".encode('utf-8'))
                    else:
                        client_socket.send("REGISTER_FAIL".encode('utf-8'))
                else:
                    parts = message.split('|')
                    if len(parts) == 2:
                        username = parts[0]
                        password = parts[1]
                        if authenticate_user(username, password):
                            authenticated = True
                            client_socket.send("AUTH_SUCCESS".encode('utf-8'))
                        else:
                            client_socket.send("AUTH_FAIL".encode('utf-8'))
                    else:
                        client_socket.send("AUTH_FAIL".encode('utf-8'))
            else:
                if message.startswith("@request_clients_list"):
                    send_clients_list(client_socket)
                elif message.startswith("file|"):
                    parts = message.split("|")
                    file_name = parts[2]
                    file_size = int(parts[3])
                    receive_file(client_socket, file_name, file_size)
                else:
                    print(f"Получено сообщение от {client_address}: {message}")
                    save_message(username, message)
                    broadcast_message(f"{username}: {message}", client_socket)
        except ConnectionResetError:
            break
        except Exception as e:
            print(f"Ошибка: {e}")
            break
    clients.remove((client_socket, client_address))
    client_socket.close()

def broadcast_message(message, sender_socket):
    for client, address in clients:
        if client != sender_socket:
            client.send(message.encode('utf-8'))

def save_message(user, message):
    conn = sqlite3.connect('chat.db')
    cursor = conn.cursor()
    cursor.execute("INSERT INTO messages (user, message) VALUES (?, ?)", (user, message))
    conn.commit()
    conn.close()

def authenticate_user(username, password):
    conn = sqlite3.connect('chat.db')
    cursor = conn.cursor()
    cursor.execute("SELECT password FROM users WHERE username = ?", (username,))
    result = cursor.fetchone()
    conn.close()
    if result and bcrypt.checkpw(password.encode('utf-8'), result[0]):
        return True
    return False

def register_user(username, password):
    conn = sqlite3.connect('chat.db')
    cursor = conn.cursor()
    hashed = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
    try:
        cursor.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, hashed))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False
    finally:
        conn.close()

def receive_file(client_socket, file_name, file_size):
    with open(file_name, 'wb') as f:
        data = client_socket.recv(1024)
        total_received = len(data)
        f.write(data)
        while total_received < file_size:
            data = client_socket.recv(1024)
            total_received += len(data)
            f.write(data)
        print(f"Файл {file_name} получен")

def send_clients_list(client_socket):
    clients_list = [address[0] for _, address in clients]
    try:
        client_socket.sendall(f"@clients_list|{'|'.join(clients_list)}".encode())
    except Exception as e:
        print(f"Ошибка при отправке списка клиентов: {e}")

server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind(('10.128.0.17', 12345))
server_socket.listen(5)

clients = []

print("Сервер запущен. Прослушивание порта 12345")

init_db()

def start_server():
    while True:
        client_socket, client_address = server_socket.accept()
        print(f"Подключение от {client_address} установлено.")
        clients.append((client_socket, client_address))
        thread = threading.Thread(target=client_handler, args=(client_socket, client_address))
        thread.start()

while True:
    command = input("Введите команду (start/stop): ").strip().lower()
    if command == "start":
        start_server()
    elif command == "stop":
        server_socket.close()
        print("Сервер остановлен.")
        break
    else:
        print("Неверная команда. Попробуйте снова.")
