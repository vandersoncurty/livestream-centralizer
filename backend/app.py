from flask import Flask, request, jsonify
import sqlite3
import os

app = Flask(__name__)

# Banco de dados
DB_PATH = "/etc/rtmp/destinations.db"
os.makedirs("/etc/rtmp", exist_ok=True)

# Cria tabela caso não exista
def init_db():
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute("""
        CREATE TABLE IF NOT EXISTS destinations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            stream_type TEXT NOT NULL,
            server TEXT NOT NULL,
            key TEXT NOT NULL
        )
        """)
init_db()

# Rota para atualizar destinos
@app.route('/update', methods=['POST'])
def update_destinations():
    data = request.json
    stream_type = data.get("type")  # horizontal ou vertical
    destinations = data.get("destinations")  # Lista de dicts com server e key

    if stream_type not in ["horizontal", "vertical"]:
        return jsonify({"error": "Invalid stream type"}), 400

    # Atualiza banco de dados
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute(f"DELETE FROM destinations WHERE stream_type = ?", (stream_type,))
        conn.executemany(
            f"INSERT INTO destinations (stream_type, server, key) VALUES (?, ?, ?)",
            [(stream_type, d["server"], d["key"]) for d in destinations]
        )

    # Atualiza arquivos
    file_path = f"/etc/rtmp/{stream_type}_destinations"
    with open(file_path, "w") as f:
        f.write("\n".join([f'rtmp://{d["server"]}/{d["key"]}' for d in destinations]))

    return jsonify({"message": "Destinations updated"}), 200

# Rota para listar destinos
@app.route('/destinations', methods=['GET'])
def list_destinations():
    with sqlite3.connect(DB_PATH) as conn:
        rows = conn.execute("SELECT stream_type, server, key FROM destinations").fetchall()
    return jsonify([{"type": r[0], "server": r[1], "key": r[2]} for r in rows])

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
