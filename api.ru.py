from flask import Flask, request, jsonify
import sqlite3
from datetime import datetime

app = Flask(__name__)

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

@app.route('/logs', methods=['GET'])
def get_logs():
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    ip = request.args.get('ip')
    logs = query_logs(start_date, end_date, ip)
    return jsonify(logs)

if __name__ == '__main__':
    app.run(debug=True)