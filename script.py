import os
import sqlite3
import re
import json
from datetime import datetime
import tkinter as tk
from tkinter import ttk, messagebox

# загрузка конф. из вынесенного файлика
with open('config.json', 'r') as f:
    config = json.load(f)

log_dir = config.get('files_dir', '.')
log_ext = config.get('ext', 'log')
log_format = config.get('format', '%h %l %t "%r" %>s %b')

# регулярное для парсера
log_pattern = re.compile(r'(?P<ip>\S+) \S+ \S+ \[(?P<date>.+)\] "(?P<request>.+)" (?P<status>\d{3}) (?P<size>\d+)')

# тут все манипуляции с бд
conn = sqlite3.connect('logs.db')
c = conn.cursor()
c.execute('''CREATE TABLE IF NOT EXISTS logs (ip TEXT, date TEXT, request TEXT, status INTEGER, size INTEGER)''')
conn.commit()

def parse_log_file(file_path):
    with open(file_path, 'r') as f:
        for line in f:
            match = log_pattern.match(line)
            if match:
                log_data = match.groupdict()
                log_data['date'] = datetime.strptime(log_data['date'], '%d/%b/%Y:%H:%M:%S %z')
                c.execute("INSERT INTO logs (ip, date, request, status, size) VALUES (?, ?, ?, ?, ?)",
                          (log_data['ip'], log_data['date'], log_data['request'], log_data['status'], log_data['size']))
    conn.commit()

def parse_logs():
    for root, dirs, files in os.walk(log_dir):
        for file in files:
            if file.endswith(log_ext):
                parse_log_file(os.path.join(root, file))

def query_logs(start_date=None, end_date=None, ip=None):
    conn = sqlite3.connect('logs.db')
    c = conn.cursor()
    query = "SELECT * FROM logs WHERE 1=1"
    params = []
    if start_date:
        query += " AND date >= ?"
        params.append(start_date)
    if end_date:
        query += " AND date <= ?"
        params.append(end_date)
    if ip:
        query += " AND ip = ?"
        params.append(ip)
    c.execute(query, params)
    logs = c.fetchall()
    conn.close()
    return logs

def on_parse():
    parse_logs()
    messagebox.showinfo("Информация", "Логи успешно распарсены и сохранены в базу данных.")

def on_view():
    start_date = start_date_entry.get()
    end_date = end_date_entry.get()
    ip = ip_entry.get()
    logs = query_logs(start_date, end_date, ip)
    result_text.delete(1.0, tk.END)
    for log in logs:
        result_text.insert(tk.END, str(log) + "\n")

#интерфеейс 

root = tk.Tk()
root.title("Apache Log Aggregator")

mainframe = ttk.Frame(root, padding="10 10 10 10")
mainframe.grid(column=0, row=0, sticky=(tk.W, tk.E, tk.N, tk.S))

ttk.Label(mainframe, text="Start Date (YYYY-MM-DD):").grid(column=1, row=1, sticky=tk.W)
start_date_entry = ttk.Entry(mainframe, width=20)
start_date_entry.grid(column=2, row=1, sticky=(tk.W, tk.E))

ttk.Label(mainframe, text="End Date (YYYY-MM-DD):").grid(column=1, row=2, sticky=tk.W)
end_date_entry = ttk.Entry(mainframe, width=20)
end_date_entry.grid(column=2, row=2, sticky=(tk.W, tk.E))

ttk.Label(mainframe, text="IP Address:").grid(column=1, row=3, sticky=tk.W)
ip_entry = ttk.Entry(mainframe, width=20)
ip_entry.grid(column=2, row=3, sticky=(tk.W, tk.E))

ttk.Button(mainframe, text="Parse Logs", command=on_parse).grid(column=1, row=4, sticky=tk.W)
ttk.Button(mainframe, text="View Logs", command=on_view).grid(column=2, row=4, sticky=tk.W)

result_text = tk.Text(mainframe, width=80, height=20)
result_text.grid(column=1, row=5, columnspan=2, sticky=(tk.W, tk.E))

for child in mainframe.winfo_children():
    child.grid_configure(padx=5, pady=5)

root.mainloop()


conn.close()
