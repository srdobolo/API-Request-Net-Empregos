from flask import Flask, request, jsonify
import random
import string

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

@app.route('/hrsmart_insert/', methods=['POST'])
def insert_job_offer():
    # Get JSON data from POST request
    data = request.get_json()

    # Validate the API access key
    access_key = data.get("access_key")
    if not validate_access_key(access_key):
        return jsonify({"error": "Invalid API key"}), 403

    # Validate REF if it is included in the request
    ref = data.get("ref")
    if ref and not validate_ref(ref):
        return jsonify({"error": "Invalid REF format"}), 400

    # Generate REF if not provided
    if not ref:
        ref = generate_ref()

    # Store the job offer in the simulated database (you can replace this with your actual database)
    job_offers[ref] = data

    return jsonify({"message": "Job offer inserted", "ref": ref}), 201

if __name__ == '__main__':
    app.run(debug=True)

# # Route to post a new job offer
# @app.route('/hrsmart_insert', methods=['POST'])
# def post_job():
#     access_key = request.args.get('ACCESS')
#     if not validate_access_key(access_key):
#         return jsonify({"error": "Invalid API key"}), 403

#     ref = request.args.get('REF')
#     if not validate_ref(ref):
#         return jsonify({"error": "Invalid REF. Must be alphanumeric and 20 characters long."}), 400

#     titulo = request.args.get('TITULO')
#     texto = request.args.get('TEXTO')
#     zona = request.args.get('ZONA')
#     categoria = request.args.get('CATEGORIA')
#     tipo = request.args.get('TIPO')

#     if not titulo or not texto or not zona or not categoria or not tipo:
#         return jsonify({"error": "Missing required parameters"}), 400

#     if ref in job_offers:
#         return jsonify({"error": "Job offer with this reference already exists"}), 409

#     job_offers[ref] = {
#         "titulo": titulo,
#         "texto": texto,
#         "zona": zona,
#         "categoria": categoria,
#         "tipo": tipo
#     }

#     return jsonify({"message": "Job offer posted successfully", "ref": ref}), 201

# # Route to generate a new REF
# @app.route('/generate_ref', methods=['GET'])
# def generate_ref_route():
#     ref = generate_ref()
#     return jsonify({"ref": ref}), 200

# if __name__ == '__main__':
#     app.run(debug=True)