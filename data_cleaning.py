# data_cleaning.py

def clean_job_data(data, mappings):
    # Clean up the description text
    raw_description = data.get('description', 'No description provided.')
    formatted_description = raw_description.replace("<br>", "\n")

    # Extract values
    location = data.get('jobLocation', {}).get('address', {}).get('addressLocality', 'Unknown')
    category = data.get('industry', {}).get('value', 'Unknown')  # Adjust according to where the category comes from
    type = data.get('employmentType', 'Unknown')  # Placeholder: Update with logic for employmentType

    # Handle special cases on Location
    if location == "Lisbon":
        location = "Lisboa"  # Convert "Lisbon" to "Lisboa"

    # Handle special cases on Category
    category_mappings = {
        "Telecomunicações": "Telecommunications",
        "Informática ( Programação )": "Programming",
        "Indústria / Produção": "Industry / Production",
        "Comunicação Social / Media": "Media / Communications",
        "Hotelaria / Turismo": "Hospitality / Tourism",
        "Educação / Formação": "Education / Training",
        "Imobiliário": "Real Estate",
        "Saúde / Medicina / Enfermagem": "Healthcare / Medicine / Nursing",
        "Contabilidade / Finanças": "Accounting / Finance",
        "Banca / Seguros / Serviços Financeiros": "Banking / Insurance / Financial Services",
        "Relações Públicas": "Public Relations",
        "Publicidade / Marketing": "Advertising / Marketing",
        "Arquitectura / Design": "Architecture / Design",
        "Construção Civil": "Civil Construction",
        "Engenharia ( Mecanica )": "Engineering (Mechanical)",
        "Gestão de Empresas / Economia": "Business Management / Economics",
        "Desporto / Ginásios": "Sports / Gyms",
        "Secretariado / Administração": "Secretariat / Administration",
        "Lojas / Comércio / Balcão": "Shops / Commerce / Counter",
        "Gestão RH": "HR Management",
        "Informática ( Formação )": "IT Training",
        "Informática ( Internet )": "IT (Internet)",
        "Informática ( Multimedia )": "IT (Multimedia)",
        "Informática ( Gestão de Redes )": "IT (Network Management)",
        "Informática ( Analise de Sistemas )": "IT (Systems Analysis)",
        "Agricultura / Florestas / Pescas": "Agriculture / Forests / Fisheries",
        "Artes / Entretenimento / Media": "Arts / Entertainment / Media",
        "Farmácia / Biotecnologia": "Pharmacy / Biotechnology",
        "Restauração / Bares / Pastelarias": "Restaurants / Bars / Pastry Shops",
        "Transportes / Logística": "Transport / Logistics",
        "Direito / Justiça": "Law / Justice",
        "Engenharia ( Civil )": "Engineering (Civil)",
        "Engenharia ( Eletrotecnica )": "Engineering (Electrotechnical)",
        "Beleza / Moda / Bem Estar": "Beauty / Fashion / Wellbeing",
        "Informática ( Técnico de Hardware )": "IT (Hardware Technician)",
        "Engenharia ( Química / Biologia )": "Engineering (Chemical / Biological)",
        "Conservação / Manutenção / Técnica": "Conservation / Maintenance / Technical",
        "Serviços Técnicos": "Technical Services",
        "Comercial / Vendas": "Commercial / Sales",
        "Engenharia ( Ambiente )": "Engineering (Environmental)",
        "Serviços Sociais": "Social Services",
        "Informática (Comercial/Gestor de Conta)": "IT (Sales/Account Manager)",
        "Call Center / Help Desk": "Customer Service",
        "Limpezas / Domésticas": "Cleaning / Domestic"
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
    if type == " ": # YET TO BE DEFINED
        type = "Teletrabalho"  
    
    # Map the category to its corresponding value in the mapping
    zona = mappings["zona_mapping"].get(location, "0")  # Default to "Unknown" if not found
    categoria = mappings["categoria_mapping"].get(category, "0")  # Default to "0" if not found
    tipo = mappings["tipo_mapping"].get(type, "0")  # Default to "0" if not found

    return formatted_description, zona, categoria, tipo