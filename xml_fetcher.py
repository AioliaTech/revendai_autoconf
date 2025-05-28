import requests, xmltodict, json, os
from datetime import datetime
from unidecode import unidecode

XML_URL = os.getenv("XML_URL")
JSON_FILE = "data.json"

MAPEAMENTO_CATEGORIAS = {
    # Específicos primeiro
    "duster oroch": "Utilitário",

    # Hatch
    "gol": "Hatch", "uno": "Hatch", "palio": "Hatch", "celta": "Hatch", "ka": "Hatch",
    "fiesta": "Hatch", "march": "Hatch", "sandero": "Hatch", "onix": "Hatch",
    "hb20": "Hatch", "i30": "Hatch", "golf": "Hatch", "polo": "Hatch", "fox": "Hatch",
    "up": "Hatch", "fit": "Hatch", "city": "Hatch", "yaris": "Hatch", "etios": "Hatch",
    "clio": "Hatch", "corsa": "Hatch", "bravo": "Hatch", "punto": "Hatch", "208": "Hatch",
    "argo": "Hatch", "mobi": "Hatch", "c3": "Hatch", "picanto": "Hatch", "c30": "Hatch",
    "série1": "Hatch", "i3": "Hatch", "classe a": "Hatch", "classe b": "Hatch", "a1": "Hatch",

    # Volvo
    "xc60": "SUV", "xc40": "SUV", "xc90": "SUV", "c40": "SUV",
    "s60": "Sedan", "s90": "Sedan", "v60": "Station Wagon", "v90": "Station Wagon",

    # BMW
    "x1": "SUV", "x3": "SUV", "x4": "SUV", "x5": "SUV", "x6": "SUV", "x7": "SUV",
    "m3": "Sedan", "m5": "Sedan", "série3": "Sedan", "série5": "Sedan", "série7": "Sedan", "i4": "Sedan",
    "série2": "Coupe", "série4": "Coupe", "série6": "Coupe", "m2": "Coupe", "i8": "Coupe",
    "z4": "Conversível",

    # Audi
    "q2": "SUV", "q3": "SUV", "q5": "SUV", "q7": "SUV", "q8": "SUV",
    "a1": "Hatch", "a3": "Sedan", "a4": "Sedan", "a5": "Coupe", "a6": "Sedan", "a7": "Sedan", "a8": "Sedan",
    "tt": "Coupe", "rs3": "Sedan", "rs4": "Station Wagon", "rs5": "Coupe", "rs6": "Station Wagon",
    "rs7": "Sedan", "r8": "Coupe",

    # Mercedes-Benz
    "classe c": "Sedan", "classe e": "Sedan", "classe s": "Sedan",
    "cla": "Sedan", "gla": "SUV", "glb": "SUV", "glc": "SUV", "gle": "SUV", "gls": "SUV",
    "amg gt": "Coupe", "slk": "Conversível", "sl": "Conversível",

    # Porsche
    "macan": "SUV", "cayenne": "SUV", "panamera": "Sedan", "taycan": "Sedan",
    "911": "Coupe", "718": "Coupe",

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
    "camaro": "Coupe", "mustang": "Coupe", "supra": "Coupe",
    "370z": "Coupe", "rx8": "Coupe", "challenger": "Coupe", "corvette": "Coupe",

    # Conversível
    "boxster": "Conversível", "miata": "Conversível", "beetle cabriolet": "Conversível", "911 cabrio": "Conversível"
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

        for v in data_dict["ADS"]["AD"]:
            try:
                parsed = {
    "id": v.get("ID"),
    "versao": v.get("VERSION"),
    "marca": v.get("MAKE"),
    "modelo": v.get("MODEL"),
    "ano": v.get("YEAR"),
    "ano_fabricacao": v.get("FABRIC_YEAR"),
    "km": v.get("MILEAGE"),
    "cor": v.get("COLOR"),
    "combustivel": v.get("FUEL"),
    "cambio": v.get("GEAR"),
    "motor": v.get("MOTOR"),
    "portas": v.get("DOORS"),
    "categoria": v.get("BODY"),
    "preco": float(v.get("PRICE", "0").replace(",", "").strip()),
    "opcionais": v.get("FEATURES", {}).get("FEATURE", []),
    "fotos": {
        "url_fotos": v.get("IMAGES", {}).get("IMAGE_URL", [])
    }
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
