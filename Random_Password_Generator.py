import random
import string
import tkinter as tk

def generate_password():
    password_length = int(length_entry.get())
    password_characters = string.ascii_letters + string.digits + string.punctuation
    password = ''.join(random.choice(password_characters) for _ in range(password_length))
    view_pass.set(password)

def copy_to_clipboard():
    password = view_pass.get()
    if password:
        root.clipboard_clear()
        root.clipboard_append(password)

root = tk.Tk()
root.title("Random Password Generator")

length_label = tk.Label(root, text="Password Length:")
length_label.pack()

length_entry = tk.Entry(root)
length_entry.pack()

generate_button = tk.Button(root, text="Generate Password", command=generate_password)
generate_button.pack(pady=20)

password_label = tk.Label(root, text="Generated Password:")
password_label.pack()

view_pass = tk.StringVar()
password_entry = tk.Entry(root, textvariable=view_pass, state='readonly')
password_entry.pack()

copy_button = tk.Button(root, text="Copy to Clipboard", command=copy_to_clipboard)
copy_button.pack(pady=20)

root.mainloop()
