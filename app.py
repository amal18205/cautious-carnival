from flask import Flask, render_template, request, redirect
import psycopg2
import time

app = Flask(__name__)

import os

def get_db():
    return psycopg2.connect(
        host=os.getenv("DB_HOST", "database"),
        database=os.getenv("DB_NAME", "tasksdb"),
        user=os.getenv("DB_USER", "devops"),
        password=os.getenv("DB_PASSWORD", "password")
    )

def init_db():
    conn = get_db()
    cur = conn.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS tasks (
            id SERIAL PRIMARY KEY,
            name TEXT NOT NULL
        )
    """)

    conn.commit()
    cur.close()
    conn.close()


@app.route("/")
def home():

    conn = get_db()
    cur = conn.cursor()

    cur.execute("SELECT id, name FROM tasks")
    tasks = cur.fetchall()

    cur.close()
    conn.close()

    return render_template("index.html", tasks=tasks)


@app.route("/add", methods=["POST"])
def add():

    task = request.form["task"]

    conn = get_db()
    cur = conn.cursor()

    cur.execute(
        "INSERT INTO tasks(name) VALUES(%s)",
        (task,)
    )

    conn.commit()

    cur.close()
    conn.close()

    return redirect("/")


@app.route("/delete/<int:id>")
def delete(id):

    conn = get_db()
    cur = conn.cursor()

    cur.execute(
        "DELETE FROM tasks WHERE id=%s",
        (id,)
    )

    conn.commit()

    cur.close()
    conn.close()

    return redirect("/")


if __name__ == "__main__":
    time.sleep(10)
    init_db()
    app.run(host="0.0.0.0", port=5000)
