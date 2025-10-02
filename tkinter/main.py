from tkinter import *


#creating scree
window = Tk()
window.title("First GUI")
window.minsize(width=600, height=300)



#Label
my_label = Label(text="Pacman Game Multi Agent System", font=("Courier", 24, "bold"))
my_label.pack()
# my_label_sub = Label(text="System", font=("Courier", 18, "bold"))
# my_label_sub.pack(side="left")


# Create a button
def button_clicked():
    new_text = input.get()
    my_label.config(text=new_text)
    my_label.pack()


button = Button(text="Click Me", command=button_clicked)
button.pack()


new_button = Button(text="New Button")
new_button.grid(column=2, row=0)

# Data Entry
input = Entry(width=10)
input.pack()
print(input.get())
input.grid(column=3,row=2)

window.mainloop()
