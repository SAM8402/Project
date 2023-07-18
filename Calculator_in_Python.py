from tkinter import *

# Function to evaluate the expression
def evaluate():
    try:
        result = eval(entry.get())  # Evaluate the expression entered in the entry widget
        entry.delete(0, END)  # Clear the entry widget
        entry.insert(0, str(result))  # Display the result
    except:
        entry.delete(0, END)
        entry.insert(0, "Error")

# Create the GUI window
root = Tk()
root.title("Calculator")

# Create the entry widget to display the expression and result
entry = Entry(root, width=20, font=("Arial", 16))
entry.grid(row=0, column=0, columnspan=4, padx=10, pady=10)

# Create the number buttons
buttons = [
    ("7", 1, 0), ("8", 1, 1), ("9", 1, 2), ("/", 1, 3),
    ("4", 2, 0), ("5", 2, 1), ("6", 2, 2), ("*", 2, 3),
    ("1", 3, 0), ("2", 3, 1), ("3", 3, 2), ("-", 3, 3),
    ("0", 4, 0), (".", 4, 1), ("=", 4, 2), ("+", 4, 3),
]

# Create the number buttons and "=" button
for button_text, row, column in buttons:
    button = Button(root, text=button_text, width=5, height=2, font=("Arial", 16), command=lambda text=button_text: entry.insert(END, text))
    button.grid(row=row, column=column)

# Create the "=" button
equals_button = Button(root, text="=", width=5, height=2, font=("Arial", 16), command=evaluate)
equals_button.grid(row=4, column=2)

# Start the GUI event loop
root.mainloop()
