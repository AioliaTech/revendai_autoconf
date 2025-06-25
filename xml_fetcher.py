import requests, xmltodict, json, os
from datetime import datetime

XML_URL   = os.getenv("XML_URL")
JSON_FILE = "data.json"


def converter_preco_xml(valor_str: str | None) -> float | None:
    if not valor_str:
        return None
    try:
        valor = str(valor_str).replace("R$", "").replace(".", "").replace(",", ".").strip()
        return float(valor)
    except ValueError:
        return None


def _to_list(obj):
    """Garante que o objeto seja sempre uma lista."""
    if obj is None:
        return []
    return obj if isinstance(obj, list) else [obj]


def fetch_and_convert_xml():
    try:
        if not XML_URL:
            raise ValueError("Variável XML_URL não definida")

        resp = requests.get(XML_URL, timeout=30)
        resp.raise_for_status()
        data_dict = xmltodict.parse(resp.content)

        vehicles = []
        for v in data_dict.get("ADS", {}).get("AD", []):
            try:
                # Fotos
                fotos = []
                for img in _to_list(v.get("IMAGES")):
                    url = img.get("IMAGE_URL") if isinstance(img, dict) else img
                    if url:
                        fotos.append(url)

                # Opcionais
                opcionais = []
                for feat in _to_list(v.get("FEATURES")):
                    val = feat.get("FEATURE") if isinstance(feat, dict) else feat
                    if val:
                        opcionais.append(val)

                vehicles.append(
                    {
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
                        "fotos": {"url_fotos": fotos},
                    }
                )
            except Exception as e:
                print(f"[ERRO] veículo ID {v.get('ID')}: {e}")

        resultado = {
            "veiculos": vehicles,
            "_updated_at": datetime.now().isoformat()
        }

        with open(JSON_FILE, "w", encoding="utf-8") as f:
            json.dump(resultado, f, ensure_ascii=False, indent=2)

        print("[OK] Dados atualizados com sucesso.")
        return resultado

    except Exception as e:
        print(f"[ERRO] Falha ao converter XML: {e}")
        return {}
