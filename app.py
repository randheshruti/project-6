from flask import Flask, request, jsonify
import sqlite3

app = Flask(__name__)
DB = "tasks.db"

def connect():
    return sqlite3.connect(DB)

with connect() as con:
    con.execute("""
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            completed INTEGER DEFAULT 0
        )
    """)

@app.route("/tasks", methods=["POST"])
def create_task():
    data = request.get_json()
    if not data or not data.get("title"):
        return jsonify({"error": "Title required"}), 400
    with connect() as con:
        cur = con.execute(
            "INSERT INTO tasks (title) VALUES (?)",
            (data["title"],)
        )
        task_id = cur.lastrowid
    return jsonify({"id": task_id, **data}), 201

@app.route("/tasks", methods=["GET"])
def get_tasks():
    with connect() as con:
        rows = con.execute(
            "SELECT id, title, completed FROM tasks"
        ).fetchall()
    tasks = [
        {"id": r[0], "title": r[1], "completed": bool(r[2])}
        for r in rows
    ]
    return jsonify(tasks), 200

@app.route("/tasks/<int:task_id>", methods=["PUT"])
def update_task(task_id):
    data = request.get_json()
    if not data:
        return jsonify({"error": "No data provided"}), 400
    with connect() as con:
        existing = con.execute(
            "SELECT id FROM tasks WHERE id = ?", (task_id,)
        ).fetchone()
        if not existing:
            return jsonify({"error": "Task not found"}), 404
        title = data.get("title")
        completed = data.get("completed")
        if title is not None:
            con.execute(
                "UPDATE tasks SET title = ? WHERE id = ?",
                (title, task_id)
            )
        if completed is not None:
            con.execute(
                "UPDATE tasks SET completed = ? WHERE id = ?",
                (1 if completed else 0, task_id)
            )
    return jsonify({"id": task_id, **data}), 200

@app.route("/tasks/<int:task_id>", methods=["DELETE"])
def delete_task(task_id):
    with connect() as con:
        cur = con.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
        if cur.rowcount == 0:
            return jsonify({"error": "Task not found"}), 404
    return jsonify({"message": "Task deleted"}), 200

if __name__ == "__main__":
    app.run(debug=True)