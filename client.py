import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import socket
import threading
import os

MAX_FILE_SIZE = 5 * 1024 * 1024  # 5 мегабайт

def send_message():
    message = entry.get()
    selected_client = selected_client_var.get()
    if message:
        try:
            client_socket.sendall(f"@{selected_client} {message}".encode())
            entry.delete(0, tk.END)
        except Exception as e:
            print(f"Ошибка при отправке сообщения: {e}")
            messagebox.showerror("Ошибка", "Ошибка при отправке сообщения")

def send_file():
    file_path = filedialog.askopenfilename()
    if file_path:
        file_name = os.path.basename(file_path)
        file_size = os.path.getsize(file_path)
        if file_size <= MAX_FILE_SIZE:
            selected_client = selected_client_var.get()
            try:
                client_socket.sendall(f"file|{selected_client}|{file_name}|{file_size}".encode())
                with open(file_path, 'rb') as f:
                    while True:
                        data = f.read(1024)
                        if not data:
                            break
                        client_socket.sendall(data)
                text.insert(tk.END, f"Файл {file_name} отправлен\n")
            except Exception as e:
                print(f"Ошибка при отправке файла: {e}")
                messagebox.showerror("Ошибка", "Ошибка при отправке файла")
        else:
            text.insert(tk.END, "Файл слишком большой для отправки\n")

def receive_message():
    while True:
        try:
            data = client_socket.recv(1024)
            if not data:
                break
            received_message = data.decode()
            if received_message.startswith("@clients_list|"):
                clients = received_message.split("|")[1:]
                update_clients_menu(clients)
            else:
                text.insert(tk.END, received_message + '\n')
        except Exception as e:
            print(f"Ошибка при приеме сообщения: {e}")
            break

def update_clients_menu(clients):
    menu = client_menu['menu']
    menu.delete(0, 'end')
    for client in clients:
        menu.add_command(label=client, command=lambda c=client: selected_client_var.set(c))

def request_clients_list():
    try:
        client_socket.sendall("@request_clients_list".encode())
    except Exception as e:
        print(f"Ошибка при запросе списка клиентов: {e}")

def authenticate():
    username = username_entry.get()
    password = password_entry.get()
    try:
        client_socket.sendall(f"{username}|{password}".encode())
        response = client_socket.recv(1024).decode()
        if response == "AUTH_SUCCESS":
            messagebox.showinfo("Успех", "Аутентификация прошла успешно")
            request_clients_list()
        else:
            messagebox.showerror("Ошибка", "Неверный логин или пароль")
    except Exception as e:
        print(f"Ошибка при отправке данных для аутентификации: {e}")
        messagebox.showerror("Ошибка", "Ошибка при отправке данных для аутентификации")

def register():
    username = username_entry.get()
    password = password_entry.get()
    try:
        client_socket.sendall(f"register|{username}|{password}".encode())
        response = client_socket.recv(1024).decode()
        if response == "REGISTER_SUCCESS":
            messagebox.showinfo("Успех", "Регистрация прошла успешно")
        else:
            messagebox.showerror("Ошибка", "Ошибка при регистрации")
    except Exception as e:
        print(f"Ошибка при отправке данных для регистрации: {e}")
        messagebox.showerror("Ошибка", "Ошибка при отправке данных для регистрации")

def on_closing():
    try:
        client_socket.close()
    except Exception as e:
        print(f"Ошибка при закрытии сокета: {e}")
    root.destroy()

root = tk.Tk()
root.title("Chat Client")

login_frame = ttk.Frame(root)
login_frame.pack(pady=10)

username_label = ttk.Label(login_frame, text="Логин:")
username_label.grid(row=0, column=0, padx=5, pady=5, sticky="e")

username_entry = ttk.Entry(login_frame, width=30)
username_entry.grid(row=0, column=1, padx=5, pady=5)

password_label = ttk.Label(login_frame, text="Пароль:")
password_label.grid(row=1, column=0, padx=5, pady=5, sticky="e")

password_entry = ttk.Entry(login_frame, width=30, show="*")
password_entry.grid(row=1, column=1, padx=5, pady=5)

login_button = ttk.Button(login_frame, text="Войти", command=authenticate)
login_button.grid(row=2, column=1, pady=5)

register_button = ttk.Button(login_frame, text="Зарегистрироваться", command=register)
register_button.grid(row=2, column=0, pady=5)

entry = ttk.Entry(root, width=50)
entry.pack(pady=10)

send_button = ttk.Button(root, text="Отправить", command=send_message)
send_button.pack(pady=5)

file_button = ttk.Button(root, text="Отправить файл", command=send_file)
file_button.pack(pady=5)

text = tk.Text(root, width=50, height=20)
text.pack(pady=10)

clients = []
selected_client_var = tk.StringVar(root)

client_menu = ttk.OptionMenu(root, selected_client_var, "Выберите клиента", *clients)
client_menu.pack()

client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.connect(('51.250.48.26', 12345))

receive_thread = threading.Thread(target=receive_message)
receive_thread.start()

root.protocol("WM_DELETE_WINDOW", on_closing)
root.mainloop()
