from flask import Flask, render_template, request, redirect
import json
import datetime

app = Flask(__name__)

# 📂 Load data
def load_data():
    try:
        with open("parking_data.json", "r") as f:
            return json.load(f)
    except:
        return {
            "floors": {
                "1": {"2W": 5, "4W": 5},
                "2": {"2W": 5, "4W": 5}
            },
            "tickets": {},
            "queue": []
        }

# 💾 Save data
def save_data(data):
    with open("parking_data.json", "w") as f:
        json.dump(data, f, indent=4)

# 🔐 LOGIN
@app.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        return redirect("/dashboard")
    return render_template("login.html")

# 🖥️ DASHBOARD
@app.route("/dashboard")
def dashboard():
    data = load_data()

    # 🧭 Direction logic
    directions = {
        "LEFT": data["floors"]["1"]["4W"],
        "STRAIGHT": data["floors"]["2"]["4W"],
        "RIGHT": data["floors"]["1"]["2W"]
    }

    return render_template("dashboard.html", data=data, directions=directions)

# 🚗 ENTRY (Queue + Ticket)
@app.route("/entry", methods=["GET", "POST"])
def entry():
    data = load_data()

    if request.method == "POST":
        vehicle = request.form["vehicle"]
        vtype = request.form["type"]

        # ➕ Add to queue
        data["queue"].append(vehicle)

        # ⏳ Check if first
        if data["queue"][0] != vehicle:
            save_data(data)
            return f"Wait! Queue position: {len(data['queue'])}"

        # 🅿️ Allocate slot
        for floor in data["floors"]:
            if data["floors"][floor][vtype] > 0:
                data["floors"][floor][vtype] -= 1

                ticket_id = str(len(data["tickets"]) + 1)

                data["tickets"][ticket_id] = {
                    "vehicle": vehicle,
                    "type": vtype,
                    "floor": floor,
                    "time": str(datetime.datetime.now())
                }

                # ❌ Remove from queue
                data["queue"].pop(0)

                save_data(data)

                return f"✅ Ticket: {ticket_id} | Floor: {floor}"

        return "❌ Parking Full!"

    return render_template("entry.html")

# 🚪 EXIT
@app.route("/exit", methods=["GET", "POST"])
def exit():
    data = load_data()

    if request.method == "POST":
        ticket_id = request.form["ticket"]

        if ticket_id in data["tickets"]:
            info = data["tickets"].pop(ticket_id)

            # 🔄 Free slot
            data["floors"][info["floor"]][info["type"]] += 1

            save_data(data)

            return "✅ Exit Successful!"

        return "❌ Invalid Ticket!"

    return render_template("exit.html")

# ▶️ RUN
if __name__ == "__main__":
    app.run(debug=True)
