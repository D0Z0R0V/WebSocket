import tkinter as tk
from tkinter import ttk
from tkinter import filedialog, messagebox
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
        file_name = os.path.basename(file_path)
        file_size = os.path.getsize(file_path)
        if file_size <= MAX_FILE_SIZE:
            client_socket.sendall(f"file|{file_name}|{file_size}".encode())
            with open(file_path, 'rb') as f:
                while True:
                    data = f.read(1024)
                    if not data:
                        break
                    client_socket.sendall(data)
            text.insert(tk.END, f"Файл {file_name} отправлен\n")
        else:
            text.insert(tk.END, "Файл слишком большой для отправки\n")

def receive_message():
    while True:
        data = client_socket.recv(1024)
        if not data:
            break
        received_message = data.decode()
        text.insert(tk.END, received_message + '\n')

def authenticate(username, password):
    client_socket.sendall(f"{username}|{password}".encode('utf-8'))
    response = client_socket.recv(1024).decode()
    if response == "AUTH_SUCCESS":
        return True
    else:
        return False

def register_user(username, password):
    client_socket.sendall(f"register|{username}|{password}".encode('utf-8'))
    response = client_socket.recv(1024).decode()
    if response == "REGISTER_SUCCESS":
        return True
    else:
        return False

def show_register_window():
    register_window = tk.Toplevel(root)
    register_window.title("Регистрация")

    tk.Label(register_window, text="Имя пользователя").pack(pady=5)
    reg_username_entry = tk.Entry(register_window)
    reg_username_entry.pack(pady=5)

    tk.Label(register_window, text="Пароль").pack(pady=5)
    reg_password_entry = tk.Entry(register_window, show='*')
    reg_password_entry.pack(pady=5)

    def attempt_register():
        reg_username = reg_username_entry.get()
        reg_password = reg_password_entry.get()
        if register_user(reg_username, reg_password):
            register_window.destroy()
            messagebox.showinfo("Успех", "Регистрация прошла успешно")
        else:
            messagebox.showerror("Ошибка", "Ошибка регистрации")

    tk.Button(register_window, text="Зарегистрироваться", command=attempt_register).pack(pady=10)

root = tk.Tk()
root.title("Chat Client")

entry = ttk.Entry(root, width=50)
entry.pack(pady=10)

send_button = ttk.Button(root, text="Отправить", command=send_message)
send_button.pack(pady=5)

file_button = ttk.Button(root, text="Отправить файл", command=send_file)
file_button.pack(pady=5)

text = tk.Text(root, width=50, height=20)
text.pack(pady=10)

client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.connect(('192.168.122.241', 12345))

login_window = tk.Toplevel(root)
login_window.title("Вход")

tk.Label(login_window, text="Имя пользователя").pack(pady=5)
username_entry = tk.Entry(login_window)
username_entry.pack(pady=5)

tk.Label(login_window, text="Пароль").pack(pady=5)
password_entry = tk.Entry(login_window, show='*')
password_entry.pack(pady=5)

def attempt_login():
    username = username_entry.get()
    password = password_entry.get()
    if authenticate(username, password):
        login_window.destroy()
        receive_thread = threading.Thread(target=receive_message)
        receive_thread.start()
    else:
        messagebox.showerror("Ошибка", "Ошибка аутентификации")

tk.Button(login_window, text="Войти", command=attempt_login).pack(pady=10)
tk.Button(login_window, text="Зарегистрироваться", command=show_register_window).pack(pady=5)

root.mainloop()

client_socket.close()
