import socket
import ssl

# SSL
context = ssl.create_default_context(ssl.Purpose.SERVER_AUTH)
context.load_verify_locations('server.crt')

client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket = context.wrap_socket(client_socket, server_hostname='localhost')
client_socket.connect(('localhost', 12345))

while True:
    message = input("Введите ваше сообщение: ")
    if message.lower() == 'exit':
        break
    client_socket.sendall(message.encode())

    data = client_socket.recv(1024)
    print(f"Получено от сервера: {data.decode()}")

client_socket.close()
