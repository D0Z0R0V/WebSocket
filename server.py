import threading
import socket

# Обработка подключений клиентов
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

# Конфигурация сервера
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind(('localhost', 12345))
server_socket.listen(5)

clients = []

print("Сервер запущен. Просушивание порта 12345")

# Функция для запуска сервера
def start_server():
    while True:
        client_socket, client_address = server_socket.accept()
        print(f"Подключение от {client_address} установлено.")
        clients.append(client_socket)
        # Канал связи с клиентом
        thread = threading.Thread(target=client_handler, args=(client_socket,))
        thread.start()

# Функция для остановки сервера
def stop_server():
    server_socket.close()
    print("Сервер остановлен.")

# Основной цикл программы
while True:
    command = input("Введите команду (start/stop): ").strip().lower()
    if command == "start":
        start_server()
    elif command == "stop":
        stop_server()
        break
    else:
        print("Неверная команда. Попробуйте снова.")
