import threading
import socket

# Обработка подключений клиентов
def client_handler(client_socket, client_address):
    while True:
        try:
            data = client_socket.recv(1024)
            if not data:
                break
            message = data.decode('utf-8')
            if message.startswith("file|"):
                file_name = message.split("|")[1]
                # Обработка отправки файла
                # Добавьте код для сохранения файла или его передачи другому клиенту
            else:
                print(f"Получено сообщение от {client_address}: {message}")
                # Если сообщение начинается с '@', отправляем его конкретному клиенту
                if message.startswith("@"):
                    recipient = message.split()[0][1:]
                    message_text = " ".join(message.split()[1:])
                    send_direct_message(recipient, message_text, client_socket)
                else:
                    broadcast_message(message, client_socket)
        except ConnectionResetError:
            break
        except Exception as e:
            print(f"Ошибка: {e}")
            break
    clients.remove((client_socket, client_address))
    client_socket.close()

# Отправка сообщения всем клиентам, кроме отправителя
def broadcast_message(message, sender_socket):
    for client, address in clients:
        if client != sender_socket:
            client.send(message.encode('utf-8'))

# Отправка приватного сообщения конкретному клиенту
def send_direct_message(recipient, message, sender_socket):
    for client, address in clients:
        if address[1] == recipient:
            client.send(message.encode('utf-8'))
            return
    sender_socket.send(f"Клиент с именем '{recipient}' не найден".encode('utf-8'))

# Получение списка подключенных клиентов с их IP-адресами и именами
def get_clients_list():
    clients_list = "Список подключенных клиентов:\n"
    for _, address in clients:
        clients_list += f"{address[1]}: {address[0]}\n"
    return clients_list

# Конфигурация сервера
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind(('192.168.122.241', 12345))
server_socket.listen(5)

clients = []

print("Сервер запущен. Прослушивание порта 12345")

# Функция для запуска сервера
def start_server():
    while True:
        client_socket, client_address = server_socket.accept()
        print(f"Подключение от {client_address} установлено.")
        clients.append((client_socket, client_address))
        client_socket.send(get_clients_list().encode('utf-8'))
        # Канал связи с клиентом
        thread = threading.Thread(target=client_handler, args=(client_socket, client_address))
        thread.start()

# Основной цикл программы
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
