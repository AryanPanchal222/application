from flask import Flask, render_template, request, jsonify
from pathlib import Path
import json

app = Flask(__name__)

# Load medicines from JSON
DATA_PATH = Path(__file__).parent / "medicine.json"
with open(DATA_PATH, "r", encoding="utf-8") as f:
  MEDICINES = json.load(f)


def search_medicines(query_text: str):
    """
    Search by:
    - medicine key
    - English name
    - uses (symptoms) like 'fever', 'allergy'
    Returns a list of matching medicines.
    """
    q = query_text.lower().strip()
    results = []

    for m in MEDICINES:
        name_en = m["en"]["name"].lower()
        uses_lower = [u.lower() for u in m.get("uses", [])]

        if (
            m["key"] in q
            or q in name_en
            or any(q in u for u in uses_lower)
        ):
            results.append(m)

    return results


def generate_ai_style_text(med, lang_code):
    """
    Placeholder for AI explanation.
    Right now it just returns the stored description.
    Later, you can call a real AI API here.
    """
    lang_data = med.get(lang_code, med["en"])
    base_desc = lang_data["description"]
    # You could modify this text a bit if you want, but keep it safe.
    return base_desc


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/api/medicine")
def get_medicine():
    search = request.args.get("q", "").strip()
    lang = request.args.get("lang", "en")
    use_ai = request.args.get("ai", "0") in ("1", "true", "yes")

    if not search:
        return jsonify({"error": "No query"}), 400

    matches = search_medicines(search)
    if not matches:
        return jsonify({"error": "Medicine not found"}), 404

    items = []
    for med in matches:
        lang_data = med.get(lang, med["en"])
        description = (
            generate_ai_style_text(med, lang)
            if use_ai
            else lang_data["description"]
        )

        items.append({
            "name": lang_data["name"],
            "description": description,
            "price": med["price"],
            "uses": med.get("uses", [])
        })

    return jsonify({"items": items})


if __name__ == "__main__":
    app.run(debug=True)
