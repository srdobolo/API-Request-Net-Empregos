# data_cleaning.py

def clean_job_data(data, mappings):
    # Clean up the description text
    raw_description = data.get('description', 'No description provided.')
    formatted_description = raw_description.replace("<br>", "\n")

    # Extract values
    location = data.get('jobLocation', {}).get('address', {}).get('addressLocality', 'Unknown')
    category = data.get('industry', {}).get('value', 'Unknown')  # Adjust according to where the category comes from
    type = data.get('employmentType', 'Unknown')  # Placeholder: Update with logic for employmentType

    # Handle special cases
    if location == "Lisbon":
        location = "Lisboa"  # Convert "Lisbon" to "Lisboa"

    if category == "Customer Service":
        category = "Call Center / Help Desk"  # Convert "Customer Service" to "Call Center / Help Desk"

    if type == "FULL_TIME":
        type = "Tempo Inteiro"  # Convert "FULL_TIME" to "Tempo Inteiro"

    # Map the category to its corresponding value in the mapping
    zona = mappings["zona_mapping"].get(location, "0")  # Default to "Unknown" if not found
    categoria = mappings["categoria_mapping"].get(category, "0")  # Default to "0" if not found
    tipo = mappings["tipo_mapping"].get(type, "0")  # Default to "0" if not found

    return formatted_description, zona, categoria, tipo