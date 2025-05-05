# data_cleaning.py
def clean_job_data(data, mappings):
    # Clean up the description text
    raw_description = data.get('description', 'No description provided.')
    formatted_description = raw_description.replace("<br>", "\n")

    # Extract values
    location = data.get('jobLocation', {}).get('address', {}).get('addressLocality', 'Unknown')
    category = data.get('industry', {}).get('value', 'Unknown')
    type = data.get('employmentType', 'Unknown')

    if data.get('jobLocationType') == 'TELECOMMUTE':
        type = 'Remote'

    # Handle special cases on Location
    if location == "Lisbon":
        location = "Lisboa"
    if location == "Portugal":
        location = "( Todas as Zonas )"
    if location not in mappings["zona_mapping"]:
        location = "Foreign - Others"

    # Handle special cases on Category
    category_mappings = {
        "Telecommunications": "Telecomunicações",
        "Programming": "Informática ( Programação )",
        "Industry / Production": "Indústria / Produção",
        "Media / Communications": "Comunicação Social / Media",
        "Hospitality / Tourism": "Hotelaria / Turismo",
        "Education / Training": "Educação / Formação",
        "Real Estate": "Imobiliário",
        "Healthcare": "Saúde / Medicina / Enfermagem",
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

    print(f"Raw category: {category}")
    if category in category_mappings:
        category = category_mappings[category]
    else:
        category = category  # Leave as is if not found
    print(f"Mapped category: {category}")

    # Handle special cases on Type
    if type == "FULL_TIME":
        type = "Tempo Inteiro"
    if type == "PART_TIME":
        type = "Part-Time"
    if type == "INTERN":
        type = "Estágio"
    if type == "Remote":
        type = "Teletrabalho"

    # Map to IDs
    zona = mappings["zona_mapping"].get(location, "0")
    categoria = mappings["categoria_mapping"].get(category, "8")
    tipo = mappings["tipo_mapping"].get(type, "0")

    print(f"Final categoria: {categoria}")
    return formatted_description, zona, categoria, tipo