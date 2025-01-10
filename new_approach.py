# import requests

# # URL of the endpoint
# url = "http://partner.net-empregos.com/hrsmart_insert.asp"

# # Data to be sent (same as the cURL form data)
# data = {
#     "ACCESS": "6F89DD1C1E8D4CD2",
#     "REF": "job001",
#     "TITULO": "Software Engineer",
#     "TEXTO": "We are looking for a skilled software engineer...",
#     "ZONA": "1",
#     "CATEGORIA": "10",
#     "TIPO": "1"
# }

# # Send POST request with form data
# response = requests.post(url, data=data)

# # Print the response from the server
# print(response.status_code)
# print(response.text)

########################################################

from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route('/hrsmart_insert/', methods=['POST'])
def insert_job_offer():
    # Get form data from the request
    access = request.form.get('ACCESS')
    ref = request.form.get('REF')
    titulo = request.form.get('TITULO')
    texto = request.form.get('TEXTO')
    zona = request.form.get('ZONA')
    categoria = request.form.get('CATEGORIA')
    tipo = request.form.get('TIPO')

    # Print the received data (just for testing)
    print(f"ACCESS: {access}")
    print(f"REF: {ref}")
    print(f"TITULO: {titulo}")
    print(f"TEXTO: {texto}")
    print(f"ZONA: {zona}")
    print(f"CATEGORIA: {categoria}")
    print(f"TIPO: {tipo}")

    # You can add your logic here, for example, saving the data to a database

    return jsonify({"message": "Job offer inserted successfully"}), 201

if __name__ == '__main__':
    app.run(debug=True)
