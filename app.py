from flask import Flask, request, jsonify, render_template
import sqlite3

app = Flask(__name__)

def init_db():
    conn = sqlite3.connect("water_data.db")
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS water_levels (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            level REAL
        )
    """)
    conn.commit()
    conn.close()

init_db()

@app.route('/')
def home():
    return "Water Monitoring Backend Running"

@app.route('/data', methods=['POST'])
def receive_data():
    data = request.json
    level = data.get("water_level")

    conn = sqlite3.connect("water_data.db")
    cursor = conn.cursor()
    cursor.execute("INSERT INTO water_levels (level) VALUES (?)", (level,))
    conn.commit()
    conn.close()

    return jsonify({"status": "success"})

@app.route('/latest')
def latest_data():
    conn = sqlite3.connect("water_data.db")
    cursor = conn.cursor()
    cursor.execute("SELECT level FROM water_levels ORDER BY id DESC LIMIT 1")
    result = cursor.fetchone()
    conn.close()

    if result:
        return jsonify({"water_level": result[0]})
    else:
        return jsonify({"water_level": 0})

@app.route('/dashboard')
def dashboard():
    return render_template("dashboard.html")

@app.route('/history')
def history():
    conn = sqlite3.connect("water_data.db")
    cursor = conn.cursor()
    cursor.execute("SELECT level FROM water_levels")
    rows = cursor.fetchall()
    conn.close()

    levels = [row[0] for row in rows]
    return jsonify({"levels": levels})
if __name__ == '__main__':
    print("Starting Flask server...")
    app.run(host='0.0.0.0', port=5000, debug=True)