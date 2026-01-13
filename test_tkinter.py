import tkinter as tk

print("Starting Tkinter test...")
root = tk.Tk()
root.title("Tkinter Test")
root.geometry("300x200")

label = tk.Label(root, text="Tkinter is working!")
label.pack(pady=50)

# 添加一个按钮来关闭窗口
def close_window():
    root.destroy()
    print("Window closed")

button = tk.Button(root, text="Close", command=close_window)
button.pack()

print("Tkinter window created, entering mainloop...")
root.mainloop()
print("Tkinter test completed")