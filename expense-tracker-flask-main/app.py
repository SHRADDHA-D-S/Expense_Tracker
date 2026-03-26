from flask import Flask, render_template, request, redirect, send_file
import json, os, csv
from datetime import datetime

app = Flask(__name__)

EXP_FILE = "expenses.json"
LIMIT_FILE = "limit.json"


def load_expenses():
    if os.path.exists(EXP_FILE):
        with open(EXP_FILE, "r") as f:
            return json.load(f)
    return []


def save_expenses(data):
    with open(EXP_FILE, "w") as f:
        json.dump(data, f, indent=4)


def load_limit():
    if os.path.exists(LIMIT_FILE):
        with open(LIMIT_FILE, "r") as f:
            return json.load(f)["limit"]
    return 0


def save_limit(limit_val):
    with open(LIMIT_FILE, "w") as f:
        json.dump({"limit": limit_val}, f)


@app.route("/", methods=["GET", "POST"])
def index():
    expenses = load_expenses()
    limit_val = load_limit()

    if request.method == "POST":
        if "set_limit" in request.form:
            save_limit(float(request.form["limit"]))
            return redirect("/")

        expenses.append({
            "amount": float(request.form["amount"]),
            "category": request.form["category"],
            "note": request.form["note"],
            "date": datetime.now().strftime("%Y-%m")
        })

        save_expenses(expenses)
        return redirect("/")

    total = sum(float(e["amount"]) for e in expenses)

    category_total = {}
    for e in expenses:
        category_total[e["category"]] = category_total.get(e["category"], 0) + float(e["amount"])


    alert = total > limit_val and limit_val > 0

    return render_template(
        "index.html",
        expenses=expenses,
        total=total,
        category_total=category_total,
        limit=limit_val,
        alert=alert
    )


@app.route("/delete/<int:index>")
def delete(index):
    expenses = load_expenses()
    if 0 <= index < len(expenses):
        expenses.pop(index)
        save_expenses(expenses)
    return redirect("/")


@app.route("/download")
def download():
    expenses = load_expenses()
    file = "expenses.csv"
    with open(file, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["Amount", "Category", "Note", "Month"])
        for e in expenses:
            writer.writerow([e["amount"], e["category"], e["note"], e["date"]])
    return send_file(file, as_attachment=True)


if __name__ == "__main__":
    app.run(debug=True)
