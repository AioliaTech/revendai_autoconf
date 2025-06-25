import requests, xmltodict, json, os
from datetime import datetime
from unidecode import unidecode

XML_URL = os.getenv("XML_URL")
JSON_FILE = "data.json"

def converter_preco_xml(valor_str):
    if not valor_str:
        return None
    try:
        valor = str(valor_str).replace("R$", "").replace(".", "").replace(",", ".").strip()
        return float(valor)
    except ValueError:
        return None

def fetch_and_convert_xml():
    try:
        if not XML_URL:
            raise ValueError("Variável XML_URL não definida")

        response = requests.get(XML_URL)
        data_dict = xmltodict.parse(response.content)

        parsed_vehicles = []

        for v in data_dict["ADS"].get("AD", []):
            if not isinstance(v, dict):
                continue
            try:
                opcionais_raw = v.get("FEATURES", {})
                imagens_raw = v.get("IMAGES", {})

                opcionais = []
                if isinstance(opcionais_raw, dict):
                    itens = opcionais_raw.get("FEATURE", [])
                    if isinstance(itens, dict):  # Caso tenha só um FEATURE
                        itens = [itens]
                    opcionais = [f.get("FEATURE") for f in itens if isinstance(f, dict)]

                fotos = []
                if isinstance(imagens_raw, dict):
                    imagens = imagens_raw.get("IMAGE", [])
                    if isinstance(imagens, dict):  # Caso tenha só uma imagem
                        imagens = [imagens]
                    fotos = [img.get("IMAGE_URL") for img in imagens if isinstance(img, dict)]

                parsed = {
                    "id": v.get("ID"),
                    "tipo": v.get("CATEGORY"),
                    "versao": v.get("VERSION"),
                    "marca": v.get("MAKE"),
                    "modelo": v.get("MODEL"),
                    "ano": v.get("YEAR"),
                    "ano_fabricacao": v.get("FABRIC_YEAR"),
                    "km": v.get("MILEAGE"),
                    "cor": v.get("COLOR"),
                    "combustivel": v.get("FUEL"),
                    "cambio": v.get("gear"),
                    "motor": v.get("MOTOR"),
                    "portas": v.get("DOORS"),
                    "categoria": v.get("BODY"),
                    "preco": converter_preco_xml(v.get("PRICE")),
                    "opcionais": opcionais,
                    "fotos": {
                        "url_fotos": fotos
                    }
                }

                parsed_vehicles.append(parsed)

            except Exception as e:
                print(f"[ERRO ao converter veículo ID {v.get('ID')}] {e}")

        data_dict = {
            "veiculos": parsed_vehicles,
            "_updated_at": datetime.now().isoformat()
        }

        with open(JSON_FILE, "w", encoding="utf-8") as f:
            json.dump(data_dict, f, ensure_ascii=False, indent=2)

        print("[OK] Dados atualizados com sucesso.")
        return data_dict

    except Exception as e:
        print(f"[ERRO] Falha ao converter XML: {e}")
        return {}
