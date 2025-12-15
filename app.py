from flask import Flask, render_template, request, jsonify
from pathlib import Path
import json
import os
import google.generativeai as genai

genai.configure(api_key=os.environ.get("GEMINI_API_KEY"))
model = genai.GenerativeModel("gemini-pro")


app = Flask(__name__)

# Load medicines from JSON
DATA_PATH = Path(__file__).parent / "medicine.json"
with open(DATA_PATH, "r", encoding="utf-8") as f:
  MEDICINES = json.load(f)

def ai_explain_medicine(med_name, lang):
    prompt = f"""
    You are a medical information assistant.

    Explain what "{med_name}" is generally used for.
    Do NOT give dosage.
    Do NOT give medical advice.
    Keep it simple.
    End with: "Consult a doctor or pharmacist before use."

    Language: {lang}
    """

    response = model.generate_content(prompt)
    return response.text



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
def find_medicine(search_text):
    search_text = search_text.lower().strip()

    for med in MEDICINES:
        # check key
        if search_text == med.get("key", "").lower():
            return med

        # check English name
        if search_text in med["en"]["name"].lower():
            return med

    return None


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/api/medicine")
def get_medicine():
    search = request.args.get("q", "").strip()
    lang = request.args.get("lang", "en")

    if not search:
        return jsonify({"error": "No search query"}), 400

    med = find_medicine(search)

    # ✅ STEP 6 STARTS HERE
    # If medicine NOT found → use AI
    if not med:
        ai_text = ai_explain_medicine(search, lang)
        return jsonify({
            "name": search,
            "description": ai_text,
            "source": "ai"
        })

    # If medicine found → use database
    lang_data = med.get(lang, med["en"])
    return jsonify({
        "name": lang_data["name"],
        "description": lang_data["description"],
        "price": med["price"],
        "source": "database"
    })


if __name__ == "__main__":
    app.run(debug=True)
