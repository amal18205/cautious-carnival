from flask import Flask, render_template, request, redirect

app = Flask(__name__)

tasks = []

@app.route("/")
def home():
    return render_template("index.html", tasks=tasks)

@app.route("/add", methods=["POST"])
def add():
    task = request.form["task"]
    tasks.append(task)
    return redirect("/")

@app.route("/delete/<int:id>")
def delete(id):
    tasks.pop(id)
    return redirect("/")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
