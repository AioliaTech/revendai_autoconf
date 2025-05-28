from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from unidecode import unidecode
from rapidfuzz import fuzz
from apscheduler.schedulers.background import BackgroundScheduler
from xml_fetcher import fetch_and_convert_xml
import json, os

app = FastAPI()

def normalizar(texto: str) -> str:
    return unidecode(texto).lower().replace("-", "").replace(" ", "").strip()

def converter_preco(valor_str):
    if valor_str is None:
        return None
    try:
        return float(valor_str)
    except ValueError:
        return None

def filtrar_veiculos(vehicles, filtros, valormax=None):
    campos_textuais = ["modelo", "versao", "marca", "cor", "categoria", "cambio", "combustivel"]
    vehicles_filtrados = vehicles.copy()

    for chave, valor in filtros.items():
        if not valor:
            continue
        termo_busca = normalizar(valor)
        resultados = []
        for v in vehicles_filtrados:
            match = False
            for campo in campos_textuais:
                conteudo = v.get(campo, "")
                if not conteudo:
                    continue
                texto = normalizar(str(conteudo))
                score = fuzz.partial_ratio(termo_busca, texto)
                if score >= 75:
                    match = True
                    break
            if chave == "categoria" and normalizar(v.get("categoria", "")) != termo_busca:
                match = False
            if match:
                resultados.append(v)
        vehicles_filtrados = resultados

    if valormax:
        try:
            teto = float(valormax)
            vehicles_filtrados = [
                v for v in vehicles_filtrados
                if "preco" in v and converter_preco(v["preco"]) is not None and converter_preco(v["preco"]) <= teto
            ]
        except:
            return []

    vehicles_filtrados.sort(
        key=lambda v: converter_preco(v["preco"]) if "preco" in v else 0,
        reverse=True
    )

    return vehicles_filtrados

@app.on_event("startup")
def agendar_tarefas():
    scheduler = BackgroundScheduler()
    scheduler.add_job(fetch_and_convert_xml, "cron", hour="0,12")
    scheduler.start()
    fetch_and_convert_xml()

@app.get("/api/data")
def get_data(request: Request):
    if not os.path.exists("data.json"):
        return {"error": "Nenhum dado disponível"}

    with open("data.json", "r", encoding="utf-8") as f:
        data = json.load(f)

    try:
        vehicles = data["veiculos"]
    except:
        return {"error": "Formato de dados inválido"}

    query_params = dict(request.query_params)
    valormax = query_params.pop("ValorMax", None)

    filtros = {
        "modelo": query_params.get("modelo"),
        "marca": query_params.get("marca")
    }

    resultado = filtrar_veiculos(vehicles, filtros, valormax)

    if resultado:
        return JSONResponse(content={
            "resultados": resultado,
            "total_encontrado": len(resultado)
        })

    alternativas = []

    alternativa1 = filtrar_veiculos(vehicles, filtros)
    if alternativa1:
        alternativas = alternativa1
    else:
        filtros_sem_marca = {"modelo": filtros.get("modelo")}
        alternativa2 = filtrar_veiculos(vehicles, filtros_sem_marca, valormax)
        if alternativa2:
            alternativas = alternativa2
        else:
            modelo = filtros.get("modelo")
            categoria_inferida = None
            for v in vehicles:
                if normalizar(v.get("modelo", "")) == normalizar(modelo or ""):
                    categoria_inferida = v.get("categoria")
                    break
            if categoria_inferida:
                filtros_categoria = {"categoria": categoria_inferida}
                alternativa3 = filtrar_veiculos(vehicles, filtros_categoria)
                if alternativa3:
                    alternativas = alternativa3

    if alternativas:
        alternativa = [
            {
                "modelo": v.get("modelo", ""),
                "ano": v.get("ano", ""),
                "preco": v.get("preco", "")
            }
            for v in alternativas
        ]

        return JSONResponse(content={
            "resultados": [],
            "total_encontrado": 0,
            "instrucao_ia": "Não encontramos veículos com os parâmetros informados. Veja estas opções mais próximas:",
            "alternativa": {
                "resultados": alternativa,
                "total_encontrado": len(alternativa)
            }
        })

    return JSONResponse(content={
        "resultados": [],
        "total_encontrado": 0,
        "instrucao_ia": "Não encontramos veículos com os parâmetros informados e também não encontramos opções próximas."
    })

@app.get("/api/status")
def get_status():
    if not os.path.exists("data.json"):
        return {"status": "Nenhum dado ainda foi gerado."}

    with open("data.json", "r", encoding="utf-8") as f:
        data = json.load(f)

    timestamp = data.get("_updated_at", "Desconhecido")
    return {"ultima_atualizacao": timestamp}

@app.get("/api/info")
def get_info():
    if not os.path.exists("data.json"):
        return {"status": "Nenhum dado disponível"}

    with open("data.json", "r", encoding="utf-8") as f:
        data = json.load(f)

    try:
        vehicles = data["veiculos"]
    except:
        return {"error": "Formato de dados inválido"}

    total = len(vehicles)
    marcas = set()
    anos = []
    precos = []

    for v in vehicles:
        if "marca" in v:
            marcas.add(v["marca"])
        if "ano" in v:
            try:
                anos.append(int(v["ano"]))
            except:
                pass
        if "preco" in v:
            try:
                preco = converter_preco(v["preco"])
                if preco is not None:
                    precos.append(preco)
            except:
                pass

    return {
        "total_veiculos": total,
        "marcas_diferentes": len(marcas),
        "ano_mais_antigo": min(anos) if anos else None,
        "ano_mais_novo": max(anos) if anos else None,
        "preco_minimo": min(precos) if precos else None,
        "preco_maximo": max(precos) if precos else None
    }
