import tkinter as tk
from tkinter import filedialog
import socket
import threading
import os

MAX_FILE_SIZE = 5 * 1024 * 1024  # 5 мегабайт

def send_message():
    message = entry.get()
    if message:
        client_socket.sendall(message.encode())
        entry.delete(0, tk.END)

def send_file():
    file_path = filedialog.askopenfilename()
    if file_path:
        file_size = os.path.getsize(file_path)
        if file_size > MAX_FILE_SIZE:
            text.insert(tk.END, "Ошибка: Файл слишком велик для отправки\n", "red")
            return
        file_name = os.path.basename(file_path)
        client_socket.send(f"file|{file_name}".encode())
        with open(file_path, "rb") as file:
            file_data = file.read(1024)
            while file_data:
                client_socket.send(file_data)
                file_data = file.read(1024)
        # Отправляем подтверждение о доставке сообщения
        text.insert(tk.END, "Сообщение успешно доставлено\n", "green")

def receive_message():
    while True:
        data = client_socket.recv(1024)
        if not data:
            break
        received_message = data.decode()
        if received_message.startswith("file|"):
            file_name = received_message.split("|")[1]
            with open(file_name, "wb") as file:
                while True:
                    file_data = client_socket.recv(1024)
                    if not file_data:
                        break
                    file.write(file_data)
                print(f"Файл '{file_name}' получен.")
        else:
            text.insert(tk.END, received_message + '\n')

def start_client():
    receive_thread = threading.Thread(target=receive_message)
    receive_thread.start()

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
text = tk.Text(root, width=50, height=20)
text.pack(pady=10)

# Стили для отображения подтверждения доставки сообщения
root.tk_setPalette(background="#FFFFFF", foreground="#000000", activeBackground="#CCCCCC", activeForeground="#000000")
text.tag_configure("green", foreground="green")
text.tag_configure("red", foreground="red")

# Подключение к серверу
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.connect(('192.168.122.241', 12345))
start_client()

# Запуск главного цикла обработки событий
root.mainloop()

# Закрытие сокета после закрытия окна
client_socket.close()
