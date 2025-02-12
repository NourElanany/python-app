from tkinter import *
from tkinter import ttk, messagebox
import sqlite3
from datetime import datetime

# الألوان الرئيسية
BG_COLOR = "#2E3440"  # خلفية داكنة
FG_COLOR = "#D8DEE9"  # نص فاتح
ACCENT_COLOR = "#5E81AC"  # لون مميز
ENTRY_COLOR = "#4C566A"  # لون حقل الإدخال
BUTTON_COLOR = "#434C5E"  # لون الأزرار

root = Tk()
root.title("To-Do List Pro")
root.geometry("600x600")
root.configure(bg=BG_COLOR)

# إعداد خط عام
FONT = ("Helvetica", 12)

# إعداد قاعدة البيانات
conn = sqlite3.connect('todolist.db')
c = conn.cursor()

# التحقق من وجود الجدول وإضافته إذا لم يكن موجودًا
c.execute('''CREATE TABLE IF NOT EXISTS tasks
             (id INTEGER PRIMARY KEY, task TEXT NOT NULL, date TEXT)''')

# إضافة حقل "date" إذا لم يكن موجودًا بالفعل
try:
    c.execute("SELECT date FROM tasks LIMIT 1")
except sqlite3.OperationalError:
    # إذا لم يكن هناك حقل "date"، نقوم بإضافته
    c.execute("ALTER TABLE tasks ADD COLUMN date TEXT")

# تأكد من أن جميع المهام القديمة لها تاريخ
c.execute("UPDATE tasks SET date = ? WHERE date IS NULL", (datetime.now().strftime("%Y-%m-%d %H:%M:%S"),))
conn.commit()

def add_task():
    task = task_entry.get().strip()
    if task:
        current_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        c.execute("INSERT INTO tasks (task, date) VALUES (?, ?)", (task, current_date))
        conn.commit()
        task_entry.delete(0, END)
        populate_tasks()
    else:
        messagebox.showwarning("تحذير", "الرجاء إدخال مهمة قبل الإضافة")

def delete_task():
    try:
        selected_task = task_list.get(task_list.curselection())
        task_id = selected_task.split('.')[0]
        c.execute("DELETE FROM tasks WHERE id=?", (task_id,))
        conn.commit()
        populate_tasks()
    except:
        messagebox.showwarning("تحذير", "الرجاء اختيار مهمة للحذف")

def populate_tasks():
    task_list.delete(0, END)
    c.execute("SELECT * FROM tasks ORDER BY date DESC")  # فرز المهام حسب التاريخ
    tasks = c.fetchall()
    for task in tasks:
        task_list.insert(END, f"{task[0]}. {task[1]} | {task[2]}")

# إطار الإدخال
input_frame = Frame(root, bg=BG_COLOR)
input_frame.pack(pady=20)

task_entry = Entry(
    input_frame,
    width=40,
    font=FONT,
    bg=ENTRY_COLOR,
    fg=FG_COLOR,
    insertbackground=FG_COLOR,
    relief=FLAT
)
task_entry.grid(row=0, column=0, padx=5)

add_task_button = Button(
    input_frame,
    text="➕ إضافة",
    command=add_task,
    bg=BUTTON_COLOR,
    fg=FG_COLOR,
    activebackground=ACCENT_COLOR,
    activeforeground=FG_COLOR,
    relief=FLAT,
    font=FONT,
    padx=15
)
add_task_button.grid(row=0, column=1)

# إطار قائمة المهام
list_frame = Frame(root, bg=BG_COLOR)
list_frame.pack()

scrollbar = Scrollbar(list_frame, orient=VERTICAL)
task_list = Listbox(
    list_frame,
    width=70,
    height=15,
    font=("Helvetica", 11),
    bg=ENTRY_COLOR,
    fg=FG_COLOR,
    yscrollcommand=scrollbar.set,
    selectbackground=ACCENT_COLOR,
    activestyle="none",
    relief=FLAT
)
scrollbar.config(command=task_list.yview)
task_list.grid(row=0, column=0)
scrollbar.grid(row=0, column=1, sticky=NS)

# إطار الأزرار
button_frame = Frame(root, bg=BG_COLOR)
button_frame.pack(pady=15)

delete_task_button = Button(
    button_frame,
    text="🗑️ حذف المحددة",
    command=delete_task,
    bg=BUTTON_COLOR,
    fg=FG_COLOR,
    activebackground=ACCENT_COLOR,
    activeforeground=FG_COLOR,
    relief=FLAT,
    font=FONT,
    padx=20
)
delete_task_button.grid(row=0, column=0, padx=10)

# إضافة تأثيرات hover للأزرار
def on_enter(e):
    e.widget['background'] = ACCENT_COLOR

def on_leave(e):
    e.widget['background'] = BUTTON_COLOR

for btn in [add_task_button, delete_task_button]:
    btn.bind("<Enter>", on_enter)
    btn.bind("<Leave>", on_leave)

# تهيئة القائمة عند البدء
populate_tasks()

# إغلاق الاتصال عند الخروج
def on_closing():
    conn.close()
    root.destroy()

root.protocol("WM_DELETE_WINDOW", on_closing)
root.mainloop()