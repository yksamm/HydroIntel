from flask import Flask, request, jsonify, render_template
import sqlite3

app = Flask(__name__)

# ---------------- DATABASE SETUP ---------------- #

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

# ---------------- ALERT LOGIC ---------------- #

def get_alert(level):
    if level < 30:
        return "SAFE"
    elif level < 60:
        return "WARNING"
    elif level < 80:
        return "CRITICAL"
    else:
        return "EMERGENCY"

# ---------------- ROUTES ---------------- #

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
        level = result[0]
        alert = get_alert(level)
        return jsonify({
            "water_level": level,
            "alert": alert
        })
    else:
        return jsonify({
            "water_level": 0,
            "alert": "SAFE"
        })

@app.route('/history')
def history():
    conn = sqlite3.connect("water_data.db")
    cursor = conn.cursor()
    cursor.execute("SELECT level FROM water_levels")
    rows = cursor.fetchall()
    conn.close()

    levels = [row[0] for row in rows]
    return jsonify({"levels": levels})

@app.route('/dashboard')
def dashboard():
    return render_template("dashboard.html")

if __name__ == '__main__':
    print("Starting Flask server...")
    app.run(host='0.0.0.0', port=5000, debug=True)