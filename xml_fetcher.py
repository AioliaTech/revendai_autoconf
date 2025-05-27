import requests, xmltodict, json, os
from datetime import datetime
from unidecode import unidecode

XML_URL = os.getenv("XML_URL")
JSON_FILE = "data.json"

MAPEAMENTO_CATEGORIAS = {
    # Hatch
    "gol": "Hatch", "uno": "Hatch", "palio": "Hatch", "celta": "Hatch", "ka": "Hatch",
    "fiesta": "Hatch", "march": "Hatch", "sandero": "Hatch", "onix": "Hatch",
    "hb20": "Hatch", "i30": "Hatch", "golf": "Hatch", "polo": "Hatch", "fox": "Hatch",
    "up": "Hatch", "fit": "Hatch", "city": "Hatch", "yaris": "Hatch", "etios": "Hatch",
    "clio": "Hatch", "corsa": "Hatch", "bravo": "Hatch", "punto": "Hatch", "208": "Hatch",
    "argo": "Hatch", "mobi": "Hatch", "c3": "Hatch", "picanto": "Hatch",

    # Sedan
    "civic": "Sedan", "corolla": "Sedan", "sentra": "Sedan", "versa": "Sedan", "jetta": "Sedan",
    "fusca": "Sedan", "prisma": "Sedan", "voyage": "Sedan", "siena": "Sedan", "grand siena": "Sedan",
    "cruze": "Sedan", "cobalt": "Sedan", "logan": "Sedan", "fluence": "Sedan", "cerato": "Sedan",
    "elantra": "Sedan", "virtus": "Sedan", "accord": "Sedan", "altima": "Sedan", "fusion": "Sedan",
    "mazda3": "Sedan", "mazda6": "Sedan", "passat": "Sedan",

    # SUV
    "duster": "SUV", "ecosport": "SUV", "hrv": "SUV", "compass": "SUV", "renegade": "SUV",
    "tracker": "SUV", "kicks": "SUV", "captur": "SUV", "creta": "SUV", "tucson": "SUV",
    "santa fe": "SUV", "sorento": "SUV", "sportage": "SUV", "outlander": "SUV",
    "asx": "SUV", "pajero": "SUV", "tr4": "SUV", "aircross": "SUV", "tiguan": "SUV",
    "t-cross": "SUV", "rav4": "SUV", "cx5": "SUV", "forester": "SUV", "wrx": "SUV",
    "land cruiser": "SUV", "cherokee": "SUV", "grand cherokee": "SUV", "xtrail": "SUV",
    "murano": "SUV", "cx9": "SUV", "edge": "SUV",

    # Caminhonete
    "hilux": "Caminhonete", "ranger": "Caminhonete", "s10": "Caminhonete", "l200": "Caminhonete",
    "triton": "Caminhonete", "saveiro": "Utilitário", "strada": "Utilitário", "montana": "Utilitário",
    "oroch": "Utilitário", "toro": "Caminhonete", "frontier": "Caminhonete", "amarok": "Caminhonete",
    "gladiator": "Caminhonete", "maverick": "Caminhonete", "colorado": "Caminhonete", "dakota": "Caminhonete",

    # Utilitário
    "kangoo": "Utilitário", "partner": "Utilitário", "doblo": "Utilitário", "fiorino": "Utilitário",
    "berlingo": "Utilitário", "express": "Utilitário", "combo": "Utilitário",

    # Furgão
    "master": "Furgão", "sprinter": "Furgão", "ducato": "Furgão", "daily": "Furgão",
    "jumper": "Furgão", "boxer": "Furgão", "trafic": "Furgão", "transit": "Furgão",

    # Coupe
    "camaro": "Coupe", "mustang": "Coupe", "tt": "Coupe", "supra": "Coupe",
    "370z": "Coupe", "rx8": "Coupe", "challenger": "Coupe", "corvette": "Coupe",

    # Conversível
    "z4": "Conversível", "boxster": "Conversível", "miata": "Conversível",
    "beetle cabriolet": "Conversível", "slk": "Conversível", "911 cabrio": "Conversível",

    # Minivan / Station Wagon
    "spin": "Minivan", "livina": "Minivan", "caravan": "Minivan", "touran": "Minivan",
    "parati": "Station Wagon", "quantum": "Station Wagon", "sharan": "Minivan",
    "zafira": "Minivan", "picasso": "Minivan", "grand c4": "Minivan",

    # Off-road
    "wrangler": "Off-road", "troller": "Off-road", "defender": "Off-road", "bronco": "Off-road",
    "samurai": "Off-road", "jimny": "Off-road", "land cruiser": "Off-road"
}

def inferir_categoria(modelo):
    if not modelo:
        return None
    modelo_norm = unidecode(modelo).lower().replace("-", "").replace(" ", "").strip()
    for mapeado, categoria in MAPEAMENTO_CATEGORIAS.items():
        if mapeado in modelo_norm:
            return categoria
    return None

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

        for v in data_dict["estoque"]["veiculo"]:
            try:
                parsed = {
                    "id": v.get("idveiculo"),
                    "marca": v.get("marca"),
                    "modelo": v.get("modelo"),
                    "categoria": inferir_categoria(v.get("modelo")),
                    "ano": v.get("anomodelo"),
                    "km": v.get("quilometragem"),
                    "cor": v.get("cor"),
                    "combustivel": v.get("combustivel"),
                    "cambio": v.get("cambio"),
                    "portas": v.get("numeroportas"),
                    "preco": converter_preco_xml(v.get("preco")),
                    "opcionais": v.get("opcionais").get("opcional") if v.get("opcionais") else None,
                    "fotos": [
                        img["url"].split("?")[0]
                        for img in v.get("fotos", {}).get("foto", [])
                        if isinstance(img, dict) and "url" in img
                    ]
                }
                parsed_vehicles.append(parsed)
            except Exception as e:
                print(f"[ERRO ao converter veículo ID {v.get('idveiculo')}] {e}")

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
