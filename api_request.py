from flask import Flask, request, jsonify

app = Flask(__name__)

# API Access Key for authentication
API_ACCESS_KEY = "API_ACCESS_KEY"

# Simulated database for job offers
job_offers = {}

# Utility function to validate API key
def validate_access_key(access_key):
    return access_key == API_ACCESS_KEY

# Route to post a new job offer
@app.route('/hrsmart_insert', methods=['POST'])
def post_job():
    access_key = request.args.get('ACCESS')
    if not validate_access_key(access_key):
        return jsonify({"error": "Invalid API key"}), 403

    ref = request.args.get('REF')
    titulo = request.args.get('TITULO')
    texto = request.args.get('TEXTO')
    zona = request.args.get('ZONA')
    categoria = request.args.get('CATEGORIA')
    tipo = request.args.get('TIPO')

    if not ref or not titulo or not texto or not zona or not categoria or not tipo:
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

# Route to edit an existing job offer
@app.route('/hrsmart_update', methods=['POST'])
def update_job():
    access_key = request.args.get('ACCESS')
    if not validate_access_key(access_key):
        return jsonify({"error": "Invalid API key"}), 403

    ref = request.args.get('REF')
    if ref not in job_offers:
        return jsonify({"error": "Job offer not found"}), 404

    titulo = request.args.get('TITULO', job_offers[ref]['titulo'])
    texto = request.args.get('TEXTO', job_offers[ref]['texto'])
    zona = request.args.get('ZONA', job_offers[ref]['zona'])
    categoria = request.args.get('CATEGORIA', job_offers[ref]['categoria'])
    tipo = request.args.get('TIPO', job_offers[ref]['tipo'])

    job_offers[ref] = {
        "titulo": titulo,
        "texto": texto,
        "zona": zona,
        "categoria": categoria,
        "tipo": tipo
    }

    return jsonify({"message": "Job offer updated successfully", "ref": ref}), 200

# Route to remove an existing job offer
@app.route('/hrsmart_remove', methods=['POST'])
def remove_job():
    access_key = request.args.get('ACCESS')
    if not validate_access_key(access_key):
        return jsonify({"error": "Invalid API key"}), 403

    ref = request.args.get('REF')
    if ref not in job_offers:
        return jsonify({"error": "Job offer not found"}), 404

    del job_offers[ref]
    return jsonify({"message": "Job offer removed successfully", "ref": ref}), 200

if __name__ == '__main__':
    app.run(debug=True)
