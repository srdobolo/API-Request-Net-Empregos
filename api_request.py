import random
import string
from flask import Flask, request, jsonify
import traceback

app = Flask(__name__)

# API Access Key for authentication
API_ACCESS_KEY = "API_ACCESS_KEY"

# Simulated database for job offers
job_offers = {}

# Utility function to validate API key
def validate_access_key(access_key):
    return access_key == API_ACCESS_KEY

# Utility function to validate REF
def validate_ref(ref):
    return ref and len(ref) == 20 and ref.isalnum()

# Utility function to generate a valid REF
def generate_ref():
    return ''.join(random.choices(string.ascii_letters + string.digits, k=20))

# Route to post a new job offer
@app.route('/hrsmart_insert', methods=['POST'])
def post_job():
    try:
        access_key = request.args.get('ACCESS')
        if not validate_access_key(access_key):
            return jsonify({"error": "Invalid API key"}), 403

        ref = request.args.get('REF')
        if not validate_ref(ref):
            return jsonify({"error": "Invalid REF. Must be alphanumeric and 20 characters long."}), 400

        titulo = request.args.get('TITULO')
        texto = request.args.get('TEXTO')
        zona = request.args.get('ZONA')
        categoria = request.args.get('CATEGORIA')
        tipo = request.args.get('TIPO')

        if not titulo or not texto or not zona or not categoria or not tipo:
            return jsonify({"error": "Missing required parameters"}), 400

        if ref in job_offers:
            return jsonify({"error": "Job offer with this reference already exists"}), 409

        job_offers[ref] = {
            "titulo": titulo,
            "texto": texto,
            "zona": zona,
            "categoria": categoria,
            "tipo": tipo
        }

        return jsonify({"message": "Job offer posted successfully", "ref": ref}), 201
    except Exception as e:
        return jsonify({"error": f"An error occurred: {str(e)}", "trace": traceback.format_exc()}), 500

# Route to generate a new REF
@app.route('/generate_ref', methods=['GET'])
def generate_ref_route():
    try:
        ref = generate_ref()
        return jsonify({"ref": ref}), 200
    except Exception as e:
        return jsonify({"error": f"An error occurred: {str(e)}", "trace": traceback.format_exc()}), 500

if __name__ == '__main__':
    app.run(debug=True)