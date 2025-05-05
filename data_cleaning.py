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
        # ... other mappings ...
    }

    print(f"Raw category: {category}")
    if category in category_mappings:
        category = category_mappings[category]
    else:
        category = category  # Leave as is if not found
    print(f"Mapped category: {category}")

    # Normalize category string to avoid whitespace/encoding issues
    category = category.strip()

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
    # Debug the category mapping
    print(f"Looking up category '{category}' in categoria_mapping")
    categoria = mappings["categoria_mapping"].get(category, "8")  # Default to "8"
    print(f"Final categoria: {categoria}")
    tipo = mappings["tipo_mapping"].get(type, "0")

    return formatted_description, zona, categoria, tipo