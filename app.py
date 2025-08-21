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
    if request.method == "POST":
        name = request.form.get("name")
        age_str = request.form.get("age", "").strip()
        if age_str.isdigit():
            age = int(age_str)
        else:
            return render_template("index.html", error="⚠️ Please enter a valid age")
        sex = request.form.get("sex")

        # CBC
        rbc = float(request.form.get("rbc") or 0)
        wbc = float(request.form.get("wbc") or 0)
        platelets = float(request.form.get("platelets") or 0)
        hb = float(request.form.get("hb") or 0)

        # Glycemic
        hba1c = request.form.get("hba1c")
        hba1c = float(hba1c) if hba1c else None
        fbs = request.form.get("fbs")
        fbs = float(fbs) if fbs else None
        pp = request.form.get("pp")
        pp = float(pp) if pp else None

        cbc_sev = assess_cbc(rbc,wbc,platelets,hb,sex)
        diabetes_status = classify_glycemic(hba1c,fbs,pp)
        risk = complication_risk(hba1c,cbc_sev)

        result = {
            "name": name,
            "age": age,
            "sex": sex,
            "diabetes_status": diabetes_status,
            "risk": risk
       
         return render_template("index.html", result=result) }

if __name__ == "__main__":
    app.run(debug=True, use_reloader=False)

