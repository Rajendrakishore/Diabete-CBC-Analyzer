from flask import Flask, render_template, request

app = Flask(__name__)

# ----------------- Helpers -----------------
def normal_ranges(sex):
    sex = (sex or "").lower()
    if sex.startswith("m"):
        return {
            "RBC": (4.7, 6.1),
            "Hemoglobin": (13.5, 17.5),
            "WBC": (4000, 11000),
            "Platelets": (150000, 450000),
        }
    else:
        return {
            "RBC": (4.2, 5.4),
            "Hemoglobin": (12.0, 15.5),
            "WBC": (4000, 11000),
            "Platelets": (150000, 450000),
        }

def deviation_severity(value, low, high):
    if value is None:
        return 0
    if low <= value <= high:
        return 0
    if value < low:
        gap = (low - value) / max(1e-9, low)
    else:
        gap = (value - high) / max(1e-9, high)
    return 1 if gap <= 0.10 else 2

def assess_cbc(rbc, wbc, platelets, hb, sex):
    ranges = normal_ranges(sex)
    components = {
        "RBC": rbc,
        "WBC": wbc,
        "Platelets": platelets,
        "Hemoglobin": hb,
    }
    severities = []
    for key, val in components.items():
        low, high = ranges[key]
        sev = deviation_severity(val, low, high)
        severities.append(sev)
    max_sev = max(severities)
    return max_sev

def classify_glycemic(hba1c, fbs, pp):
    scores = []
    if hba1c:
        if hba1c < 5.7: scores.append(0)
        elif hba1c < 6.5: scores.append(1)
        else: scores.append(2)
    if fbs:
        if fbs < 100: scores.append(0)
        elif fbs < 126: scores.append(1)
        else: scores.append(2)
    if pp:
        if pp < 140: scores.append(0)
        elif pp < 200: scores.append(1)
        else: scores.append(2)

    if not scores: return "Insufficient"
    return ["Normal","Pre-diabetic","Diabetic"][max(scores)]

def complication_risk(hba1c, cbc_severity):
    if hba1c:
        if hba1c >= 8.0 or cbc_severity == 2:
            return "High Complication risk"
        if hba1c >= 7.0 or cbc_severity == 1:
            return "Poorly Controlled diabetes"
        return "Controlled diabetes"
    else:
        if cbc_severity == 2: return "High Complication risk"
        if cbc_severity == 1: return "Poorly Controlled diabetes"
        return "Controlled diabetes"

# ----------------- Routes -----------------
@app.route("/", methods=["GET", "POST"])
def index():
   result = None
   error = None
   if request.method == "POST":
    try:
        name = (request.form.get("name") or "").strip()
        age_str = (request.form.get("age") or "").strip()
        sex = (request.form.get("sex") or "").strip()

        if not age_str.isdigit():
            error = "⚠️ Please enter a valid age"
            return render_template("index.html", result=None, error=error)

        age = int(age_str)

        # CBC
        def to_float(key):
            val = request.form.get(key)
            return float(val) if val not in (None, "",) else 0.0

        rbc = to_float("rbc")
        wbc = to_float("wbc")
        platelets = to_float("platelets")
        hb = to_float("hb")

        # Glycemic (optional fields)
        def to_opt_float(key):
            val = request.form.get(key)
            return float(val) if val not in (None, "",) else None

        hba1c = to_opt_float("hba1c")
        fbs = to_opt_float("fbs")
        pp = to_opt_float("pp")

        # ---- Your helper functions here (import or define above) ----
        cbc_sev = assess_cbc(rbc, wbc, platelets, hb, sex)
        diabetes_status = classify_glycemic(hba1c, fbs, pp)
        risk = complication_risk(hba1c, cbc_sev)

        result = {
            "name": name or "N/A",
            "age": age,
            "sex": sex or "N/A",
            "diabetes_status": diabetes_status,
            "risk": risk,
        }

    except Exception as e:
        # Show the error on the page instead of returning None
        error = f"Unexpected error: {e}"
        return render_template("index.html", result=None, error=error)

# ALWAYS return a response
   return render_template("index.html", result=result, error=error)
 

if __name__ == "__main__":
    app.run(debug=True, use_reloader=False)

