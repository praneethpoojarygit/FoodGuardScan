from flask import Flask, request, jsonify, render_template
from werkzeug.utils import secure_filename
import requests
import os

API_KEY = 'K84046083688957'

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

harmful_ingredients = {
    "sugar": "Common sweetener, high in calories.",
    "salt": "Essential for human health, but excessive intake can lead to health issues.",
    "peanut": "Common allergen, can cause severe reactions.",
    "milk": "Common allergen, can cause lactose intolerance in some individuals.",
    "wheat": "Common allergen, can cause celiac disease in sensitive individuals.",
    "soy": "Common allergen, often found in processed foods.",
    "aspartame": "Artificial sweetener linked to headaches and other symptoms.",
    "sodium benzoate": "Preservative; can form harmful compounds when combined with vitamin C.",
    "potassium sorbate": "Preservative; can cause allergic reactions and skin irritation.",
    "sodium metabisulphite": "Preservative; can cause asthma and allergic reactions in sensitive individuals.",
    "benzoic acid": "Preservative; linked to skin irritation and allergic reactions.",
    "BHA": "Preservative; known carcinogen and endocrine disruptor.",
    "BHT": "Preservative; potential carcinogen.",
    "calcium propionate": "Preservative; can cause headaches and allergic reactions.",
    "cyclamate": "Banned in some countries but used in India; linked to cancer.",
    "sucralose": "Artificial sweetener; linked to digestive issues.",
    "saccharin": "Artificial sweetener; associated with bladder cancer risk in animal studies.",
    "tartrazine (yellow 5)": "Artificial colorant; causes hyperactivity and allergic reactions in children.",
    "sunset yellow (yellow 6)": "Artificial colorant; linked to allergic reactions and hyperactivity.",
    "brilliant blue (blue 1)": "Artificial colorant; possible carcinogen.",
    "red 40": "Artificial colorant; linked to hyperactivity and behavioral problems in children.",
    "carmine": "Red coloring agent; can cause allergic reactions.",
    "MSG": "Flavor enhancer; causes headaches, sweating, and chest pain in sensitive individuals.",
    "hydrolyzed vegetable protein": "Flavor enhancer; may cause headaches and allergic reactions.",
    "autolyzed yeast extract": "Flavor enhancer; can cause migraines and allergic reactions.",
    "titanium dioxide": "Whitening agent; can cause gastrointestinal issues and possible cancer.",
    "artificial flavors": "Common in snacks and candies; may cause allergic reactions.",
    "phthalates": "Chemical used in food packaging; disrupts the endocrine system and causes reproductive issues.",
    "acrylamide": "Byproduct of frying and baking at high temperatures; linked to cancer.",
    "sodium nitrite": "Preservative used in processed meats; linked to cancer.",
    "aluminum": "Used in food packaging; linked to neurological issues and Alzheimer’s disease.",
    "lecithin (e322)": "Emulsifier; can cause allergic reactions in sensitive individuals, commonly found in chocolates and margarines.",
    "mono- and diglycerides": "Emulsifiers; may cause allergic reactions in sensitive individuals.",
    "sodium chloride": "Excessive intake can cause high blood pressure and kidney problems.",
    "glutamate": "Flavor enhancer; can cause headaches and other symptoms in sensitive individuals.",
    "corn syrup": "Sweetener; linked to obesity and diabetes.",
    "high-fructose corn syrup": "Sweetener; linked to obesity, insulin resistance, and fatty liver disease.",
    "palm oil": "Common in processed foods; high in saturated fats, which can contribute to heart disease.",
    "hydrogenated oils": "Trans fats; linked to heart disease and stroke.",
    "artificial sweeteners": "Used in diet foods; may cause headaches, digestive problems, and cancer.",
    "sodium carbonate": "Used in processed foods; can cause digestive issues and high blood pressure.",
    "potassium chloride": "Used as a salt substitute; can cause high potassium levels leading to kidney damage.",
    "acetic acid": "Used in pickling; excessive consumption may cause digestive issues.",
    "butylated hydroxyanisole (BHA)": "Preservative; linked to cancer in animal studies.",
    "butylated hydroxytoluene (BHT)": "Preservative; may cause liver and kidney damage with prolonged use.",
    "diacetyl": "Flavouring agent; linked to lung disease when inhaled in large quantities.",
    "parabens": "Preservatives used in cosmetics and food; can disrupt hormonal function.",
    "propyl gallate": "Preservative; linked to cancer in animal studies.",
    "azo dyes": "Artificial colorants; linked to hyperactivity and allergic reactions.",
    "benzoic acid": "Preservative; associated with allergic reactions and skin irritation.",
    "ethyl vanillin": "Artificial flavoring; may cause allergic reactions.",
    "ferrous gluconate": "Iron supplement; may cause digestive discomfort.",
    "tetrasodium pyrophosphate": "Used as a preservative; can cause digestive upset.",
    "propylene glycol": "Used in food and cosmetics; linked to skin irritation and organ damage.",
    "sodium bicarbonate": "Baking soda; excessive consumption can lead to kidney issues and high blood pressure."
}

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/scan', methods=['POST'])
def scan_ingredients():
    if 'image' not in request.files:
        return jsonify({'error': 'No file uploaded'}), 400

    file = request.files['image']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400

    filename = secure_filename(file.filename)
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    file.save(filepath)

    try:
        with open(filepath, 'rb') as image_file:
            response = requests.post(
                'https://api.ocr.space/parse/image',
                files={'file': image_file},
                data={'apikey': API_KEY}
            )

        result = response.json()

        if result.get('OCRExitCode') != 1:
            os.remove(filepath)
            return jsonify({'error': 'Failed to extract text from the image'}), 500

        extracted_text = result['ParsedResults'][0]['ParsedText']

        found_harmful = {}
        for ingredient, info in harmful_ingredients.items():
            if ingredient.lower() in extracted_text.lower():
                found_harmful[ingredient] = info

    except Exception as e:
        os.remove(filepath)
        return jsonify({'error': f'Failed to process the image: {str(e)}'}), 500

    os.remove(filepath)

    return jsonify({
        'extracted_text': extracted_text.strip(),
        'harmful_ingredients': found_harmful
    })

if __name__ == '__main__':
    app.run(debug=True)
