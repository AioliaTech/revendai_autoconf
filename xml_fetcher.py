import requests, xmltodict, json, os
from datetime import datetime

XML_URL = os.getenv("XML_URL")
JSON_FILE = "data.json"

def fetch_and_convert_xml():
    try:
        if not XML_URL:
            raise ValueError("Variável XML_URL não definida")
        response = requests.get(XML_URL)
        data_dict = xmltodict.parse(response.content)

        parsed_vehicles = []

        for v in data_dict["estoque"]["veiculo"]:
            try:
                parsed = {
                    "id": v.get("idveiculo"),
                    "marca": v.get("marca"),
                    "modelo": v.get("modelo"),
                    "ano": v.get("anomodelo"),
                    "km": v.get("quilometragem"),
                    "cor": v.get("cor"),
                    "combustivel": v.get("combustivel"),
                    "cambio": v.get("cambio"),
                    "portas": v.get("numeroportas"),
                    "preco": v.get("preco"),
                    "opcionais": v.get("opcionais").get("opcional"),
                    "imagens": v.get("fotos", {}).get("foto", [])
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
