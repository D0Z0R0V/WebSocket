import socket
import threading
import ssl

# обработка подключений клиентов
def client_handler(client_socket):
    while True:
        try:
            # Получение сообщений от клиента
            message = client_socket.recv(1024).decode('utf-8')
            if not message:
                break
            print(f"Получено сообщение: {message}")
            # Пересылка сообщения всем подключенным клиентам
            for client in clients:
                if client != client_socket:
                    client.send(message.encode('utf-8'))
        except ConnectionResetError:
            break
        except Exception as e:
            print(f"Ошибка: {e}")
            break
    clients.remove(client_socket)
    client_socket.close()

# SSL 
context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
context.load_cert_chain(certfile="server.crt", keyfile="server.key")

# Конфиг сервера
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind(('localhost', 12345))
server_socket.listen(5)
server_socket = context.wrap_socket(server_socket, server_side=True)

clients = []

print("Сервер запущен. Просушивание порта 12345")

while True:
    client_socket, client_address = server_socket.accept()
    print(f"Connection from {client_address} established.")
    clients.append(client_socket)
    # канал связи с клиентом
    thread = threading.Thread(target=client_handler, args=(client_socket,))
    thread.start()
