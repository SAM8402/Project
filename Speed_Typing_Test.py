import tkinter as tk
import time

def start_test():
    global start_time
    start_time = time.time() # Record the start time

def end_test():
    end_time = time.time() # Record the end time
    total_time = end_time - start_time # Calculate the total time taken
    wpm = calculate_wpm(total_time) # Calculate words per minute
    result_label.config(text=f"Your typing speed: {wpm} WPM")

def calculate_wpm(total_time):
    # Assume an average word length of 5 characters
    average_word_length = 5
    characters_typed = len(textbox.get("1.0", tk.END)) - 1 # Exclude newline character
    words_typed = characters_typed / average_word_length
    minutes_elapsed = total_time / 60
    wpm = words_typed / minutes_elapsed
    return round(wpm)

# Create the GUI
window = tk.Tk()
window.title("Speed Typing Test")

instruction_label = tk.Label(window, text="Type the following sentence:")
instruction_label.pack()

sentence_label = tk.Label(window, text="The quick brown fox jumps over the lazy dog.")
sentence_label.pack()

textbox = tk.Text(window, height=10, width=50)
textbox.pack()

start_button = tk.Button(window, text="Start Test", command=start_test)
start_button.pack()

end_button = tk.Button(window, text="End Test", command=end_test)
end_button.pack()

result_label = tk.Label(window)
result_label.pack()

window.mainloop()
