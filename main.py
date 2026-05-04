import tkinter as tk
from tkinter import ttk, messagebox
import random
import string
import json
import os

# --- Конфигурация ---
HISTORY_FILE = 'history.json'
MIN_LENGTH = 4
MAX_LENGTH = 32

# --- Логика генерации и работы с историей ---
def generate_password(length, use_digits, use_letters, use_special):
    """Генерирует пароль на основе выбранных параметров."""
    if length < 1:
        raise ValueError("Длина пароля должна быть больше 0.")
    
    chars = ''
    if use_digits:
        chars += string.digits
    if use_letters:
        chars += string.ascii_letters
    if use_special:
        chars += string.punctuation

    if not chars:
        raise ValueError("Необходимо выбрать хотя бы один тип символов (цифры, буквы или спецсимволы).")
    
    return ''.join(random.choices(chars, k=length))

def load_history():
    """Загружает историю паролей из файла JSON."""
    if not os.path.exists(HISTORY_FILE):
        return []
    try:
        with open(HISTORY_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except (json.JSONDecodeError, FileNotFoundError):
        return []

def save_history(history):
    """Сохраняет историю паролей в файл JSON."""
    with open(HISTORY_FILE, 'w', encoding='utf-8') as f:
        json.dump(history, f, ensure_ascii=False, indent=2)

def add_to_history(password):
    """Добавляет новый пароль в историю."""
    history = load_history()
    history.append(password)
    save_history(history)

# --- Класс графического интерфейса ---
class PasswordGeneratorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Генератор случайных паролей")
        self.root.geometry("450x500")
        
        self.create_widgets()
        self.update_history_table()

    def create_widgets(self):
        # --- Рамка настроек ---
        settings_frame = tk.LabelFrame(self.root, text="Настройки пароля", padx=10, pady=10)
        settings_frame.pack(pady=10, fill='x', padx=20)

        # Длина пароля (Ползунок)
        tk.Label(settings_frame, text="Длина:").grid(row=0, column=0, sticky='e')
        self.length_var = tk.IntVar(value=12)
        self.length_scale = tk.Scale(settings_frame, from_=MIN_LENGTH, to=MAX_LENGTH,
                                     orient=tk.HORIZONTAL, variable=self.length_var)
        self.length_scale.grid(row=0, column=1, sticky='ew', columnspan=2)

        # Чекбоксы для выбора символов
        self.use_digits_var = tk.BooleanVar(value=True)
        self.use_letters_var = tk.BooleanVar(value=True)
        self.use_special_var = tk.BooleanVar(value=True)

        tk.Checkbutton(settings_frame, text="Цифры (0-9)", variable=self.use_digits_var).grid(row=1, column=0, columnspan=3, sticky='w')
        tk.Checkbutton(settings_frame, text="Буквы (a-zA-Z)", variable=self.use_letters_var).grid(row=2, column=0, columnspan=3, sticky='w')
        tk.Checkbutton(settings_frame, text="Спецсимволы (!@#)", variable=self.use_special_var).grid(row=3, column=0, columnspan=3, sticky='w')

        # Кнопка генерации и поле вывода пароля
        btn_frame = tk.Frame(self.root)
        btn_frame.pack(pady=10)
        
        self.generate_btn = tk.Button(btn_frame, text="Сгенерировать", command=self.generate_password_action)
        self.generate_btn.pack()

        self.password_entry = tk.Entry(self.root, font=('Consolas', 12), width=35)
        self.password_entry.pack(pady=10)
        
        # Кнопка копирования в буфер обмена
        copy_btn = tk.Button(self.root, text="Копировать", command=self.copy_to_clipboard)
        copy_btn.pack(pady=5)

        # --- Рамка истории ---
        history_frame = tk.LabelFrame(self.root, text="История", padx=10, pady=10)
        history_frame.pack(pady=10, fill='both', expand=True, padx=20)

        self.history_tree = ttk.Treeview(history_frame, columns=("password",), show="headings")
        self.history_tree.heading("password", text="Пароль")
        
        # Полоса прокрутки для истории
        scrollbar = ttk.Scrollbar(history_frame, orient="vertical", command=self.history_tree.yview)
        self.history_tree.configure(yscrollcommand=scrollbar.set)
        
        self.history_tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

    def generate_password_action(self):
        """Обработчик нажатия кнопки 'Сгенерировать'."""
        try:
            length = self.length_var.get()
            password = generate_password(
                length,
                self.use_digits_var.get(),
                self.use_letters_var.get(),
                self.use_special_var.get()
            )
            self.password_entry.delete(0, tk.END)
            self.password_entry.insert(0, password)
            
            add_to_history(password)
            self.update_history_table()
            
            messagebox.showinfo("Готово", "Пароль успешно сгенерирован!")
            
        except ValueError as e:
            messagebox.showerror("Ошибка ввода", str(e))

    def update_history_table(self):
        """Обновляет таблицу истории в GUI."""
        for item in self.history_tree.get_children():
            self.history_tree.delete(item)
        
        for pwd in load_history():
            self.history_tree.insert("", "end", values=(pwd,))

    def copy_to_clipboard(self):
        """Копирует сгенерированный пароль в буфер обмена."""
        password = self.password_entry.get()
        if password:
            self.root.clipboard_clear()
            self.root.clipboard_append(password)
            messagebox.showinfo("Скопировано", "Пароль скопирован в буфер обмена.")

# --- Точка входа ---
if __name__ == "__main__":
    root = tk.Tk()
    app = PasswordGeneratorApp(root)
    root.mainloop()