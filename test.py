
import requests
import xml.etree.ElementTree as ET
import os
import json

FEED_URL = "https://recruit.zoho.eu/recruit/downloadjobfeed?clientid=da279e513762f8ff929094f0761b8d7028c9ede87d9cc749c7fc7c9ec526d541db96e9a00da67f84101be0a8e52f82b6"

# --- carregar mappings ---
with open("mapping.json", "r", encoding="iso-8859-1") as f:
    mappings = json.load(f)

zona_mapping = mappings["zona_mapping"]
categoria_mapping = mappings["categoria_mapping"]
tipo_mapping = mappings["tipo_mapping"]

# --- fetch feed ---
response = requests.get(FEED_URL, timeout=10)
response.raise_for_status()
root = ET.fromstring(response.content)

print(f"Found {len(root.findall('job'))} jobs in feed.\n")

# --- processar cada job ---
for job in root.findall("job"):
    title = job.findtext("title", "").strip()
    ref = job.findtext("referencenumber", "").strip()
    url = job.findtext("url", "").strip()
    description = job.findtext("description", "").strip()
    categoria_raw = job.findtext("category", "").strip()
    zona_raw = job.findtext("state", "").strip()
    tipo_raw = job.findtext("type", "Tempo Inteiro").strip()

    # --- aplicar mappings ---
    categoria = categoria_mapping.get(categoria_raw, "57")  # default: Call Center / Help Desk
    zona = zona_mapping.get(zona_raw, "29")                # default: Foreign - Others
    tipo = tipo_mapping.get(tipo_raw, "1")                 # default: Tempo Inteiro

    # --- construir payload ---
    payload = {
        "ACCESS": "API_KEY_TEST",  # apenas para teste
        "REF": ref,
        "TITULO": title,
        "TEXTO":    f"{description}<br><br><a href='{url}'>Clique aqui para se candidatar!</a>"
                    f"ou por email para info@recruityard.com",
        "ZONA": zona,
        "CATEGORIA": categoria,
        "TIPO": tipo,
    }

    # --- imprimir para testar ---
    print("----- TEST JOB -----")
    print(f"REF: {ref}")
    print(f"TITLE: {title}")
    print(f"ZONA: {zona} (raw: {zona_raw})")
    print(f"CATEGORIA: {categoria} (raw: {categoria_raw})")
    print(f"TIPO: {tipo} (raw: {tipo_raw})")
    print("PAYLOAD:", json.dumps(payload, indent=2, ensure_ascii=False))
    print("--------------------\n")