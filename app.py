from flask import Flask, render_template, request, redirect, jsonify
import sqlite3
import os

app = Flask(__name__)

DB_NAME = "day.db"

# ----------------------
# DB接続
# ----------------------
def get_db():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn

# ----------------------
# DB初期化
# ----------------------
def init_db():
    conn = get_db()
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS activities (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            minutes INTEGER NOT NULL,
            sort_order INTEGER NOT NULL
        )
    """)
    conn.commit()
    conn.close()



# ----------------------
# 画面表示
# ----------------------
@app.route("/")
def index():
    return render_template("index.html")

# ----------------------
# データ取得（JSON）
# ----------------------
@app.route("/data")
def get_data():
    conn = get_db()
    cur = conn.cursor()
    cur.execute(
        "SELECT id, name, minutes FROM activities ORDER BY sort_order"
    )
    rows = cur.fetchall()
    conn.close()

    return jsonify([[r["id"], r["name"], r["minutes"]] for r in rows])

# ----------------------
# データ追加
# ----------------------
@app.route("/add", methods=["POST"])
def add():
    name = request.form.get("name")
    minutes = request.form.get("minutes")

    conn = get_db()
    cur = conn.cursor()

    cur.execute("SELECT COALESCE(MAX(sort_order), 0) + 1 FROM activities")
    next_order = cur.fetchone()[0]

    cur.execute(
        "INSERT INTO activities (name, minutes, sort_order) VALUES (?, ?, ?)",
        (name, int(minutes), next_order)
    )

    conn.commit()
    conn.close()
    return redirect("/")


# ----------------------
# データ削除
# ----------------------
@app.route("/delete/<int:id>")
def delete(id):
    conn = get_db()
    cur = conn.cursor()
    cur.execute(
        "DELETE FROM activities WHERE id = ?",
        (id,)
    )
    conn.commit()
    conn.close()

    return redirect("/")

@app.route("/reorder", methods=["POST"])
def reorder():
    order = request.json  # [id, id, id...]

    conn = get_db()
    cur = conn.cursor()

    for index, item_id in enumerate(order):
        cur.execute(
            "UPDATE activities SET sort_order = ? WHERE id = ?",
            (index, item_id)
        )

    conn.commit()
    conn.close()
    return "", 204


# ----------------------
# 起動
# ----------------------
if __name__ == "__main__":
    init_db()
    app.run()
