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
    if category == "Customer Service":
        category = "Call Center / Help Desk"  # Convert "Customer Service" to "Call Center / Help Desk"

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