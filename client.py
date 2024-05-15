import tkinter as tk
import socket
import threading

MAX_FILE_SIZE = 5 * 1024 * 1024  # 5 мегабайт

def send_message():
    message = entry.get()
    if message:
        client_socket.sendall(message.encode())
        entry.delete(0, tk.END)

def send_file():
    # Реализуйте функцию отправки файла
    pass

def receive_message():
    while True:
        data = client_socket.recv(1024)
        if not data:
            break
        received_message = data.decode()
        text.insert(tk.END, received_message + '\n')

# Создание окна
root = tk.Tk()
root.title("Chat Client")

# Поле для ввода сообщения
entry = tk.Entry(root, width=50)
entry.pack(pady=10)

# Кнопка для отправки сообщения
send_button = tk.Button(root, text="Отправить", command=send_message)
send_button.pack(pady=5)

# Кнопка для отправки файла
file_button = tk.Button(root, text="Отправить файл", command=send_file)
file_button.pack(pady=5)

# Окно для отображения информации
text = tk.Text(root, width=30, height=20)
text.pack(pady=10)

# Подключение к серверу
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.connect(('192.168.122.241', 12345))
receive_thread = threading.Thread(target=receive_message)
receive_thread.start()

# Запуск главного цикла обработки событий
root.mainloop()

# Закрытие сокета после закрытия окна
client_socket.close()
