# data_cleaning.py

def clean_job_data(data, mappings):
    # Clean up the description text
    raw_description = data.get('description', 'No description provided.')
    formatted_description = raw_description.replace("<br>", "\n")

    # Extract values
    location = data.get('jobLocation', {}).get('address', {}).get('addressLocality', 'Foreign - Others')
    category = data.get('industry', {}).get('value', 'Unknown')  
    type = data.get('employmentType', 'Unknown')  

    if data.get('jobLocationType', {}) == 'TELECOMMUTE':
        type = 'Remote'

    # Handle special cases on Location
    if location == "Lisbon":
        location = "Lisboa"  # Convert "Lisbon" to "Lisboa"

    # Handle special cases on Category
    category_mappings = {
    "Telecommunications": "Telecomunicações",
    "Programming": "Informática ( Programação )",
    "Industry / Production": "Indústria / Produção",
    "Media / Communications": "Comunicação Social / Media",
    "Hospitality / Tourism": "Hotelaria / Turismo",
    "Education / Training": "Educação / Formação",
    "Real Estate": "Imobiliário",
    "Healthcare / Medicine / Nursing": "Saúde / Medicina / Enfermagem",
    "Accounting / Finance": "Contabilidade / Finanças",
    "Banking / Insurance / Financial Services": "Banca / Seguros / Serviços Financeiros",
    "Public Relations": "Relações Públicas",
    "Advertising / Marketing": "Publicidade / Marketing",
    "Architecture / Design": "Arquitectura / Design",
    "Civil Construction": "Construção Civil",
    "Engineering (Mechanical)": "Engenharia ( Mecanica )",
    "Business Management / Economics": "Gestão de Empresas / Economia",
    "Sports / Gyms": "Desporto / Ginásios",
    "Secretariat / Administration": "Secretariado / Administração",
    "Shops / Commerce / Counter": "Lojas / Comércio / Balcão",
    "HR Management": "Gestão RH",
    "IT Training": "Informática ( Formação )",
    "IT (Internet)": "Informática ( Internet )",
    "IT (Multimedia)": "Informática ( Multimedia )",
    "IT (Network Management)": "Informática ( Gestão de Redes )",
    "IT (Systems Analysis)": "Informática ( Analise de Sistemas )",
    "Agriculture / Forests / Fisheries": "Agricultura / Florestas / Pescas",
    "Arts / Entertainment / Media": "Artes / Entretenimento / Media",
    "Pharmacy / Biotechnology": "Farmácia / Biotecnologia",
    "Restaurants / Bars / Pastry Shops": "Restauração / Bares / Pastelarias",
    "Transport / Logistics": "Transportes / Logística",
    "Law / Justice": "Direito / Justiça",
    "Engineering (Civil)": "Engenharia ( Civil )",
    "Engineering (Electrotechnical)": "Engenharia ( Eletrotecnica )",
    "Beauty / Fashion / Wellbeing": "Beleza / Moda / Bem Estar",
    "IT (Hardware Technician)": "Informática ( Técnico de Hardware )",
    "Engineering (Chemical / Biological)": "Engenharia ( Química / Biologia )",
    "Conservation / Maintenance / Technical": "Conservação / Manutenção / Técnica",
    "Technical Services": "Serviços Técnicos",
    "Commercial / Sales": "Comercial / Vendas",
    "Engineering (Environmental)": "Engenharia ( Ambiente )",
    "Social Services": "Serviços Sociais",
    "IT (Sales/Account Manager)": "Informática (Comercial/Gestor de Conta)",
    "Customer Service": "Call Center / Help Desk",
    "Cleaning / Domestic": "Limpezas / Domésticas"
    }

    # Now you can use this mapping dynamically:
    if category in category_mappings:
        category = category_mappings[category]
    else:
        category = category  # Leave the category as it is if not found in the mapping

    # Handle special cases on Type
    if type == "FULL_TIME":
        type = "Tempo Inteiro" 
    if type == "PART_TIME":
        type = "Part-Time"  
    if type == "INTERN":
        type = "Estágio" 
    if type == "Remote": 
        type = "Teletrabalho"  
    
    # Map the category to its corresponding value in the mapping
    zona = mappings["zona_mapping"].get(location, "0")  # Default to "Unknown" if not found
    categoria = mappings["categoria_mapping"].get(category, "0")  # Default to "0" if not found
    tipo = mappings["tipo_mapping"].get(type, "0")  # Default to "0" if not found

    return formatted_description, zona, categoria, tipo