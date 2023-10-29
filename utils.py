import os
import json
import pandas as pd


def get_geo_info(content: dict) -> dict:
    record = {}
    for lvl in content['fathers']:
        record[f"lvl_{int(lvl['level'])}"] = lvl['name']
    return record


INTERESTING_KEYS = ['census', 'electores', 'sobres', 'nulos', 'recurridos', 'blancos', 'comando', 'impugnados',
                    'totalVotos', 'afirmativos', 'abstencion', 'valid']


def get_desk_data(content: dict) -> dict:
    return {key: value for key, value in content.items() if key in INTERESTING_KEYS}


ACRONYMS = {
    'UNION POR LA PATRIA': "UXP",
    'JUNTOS POR EL CAMBIO': "JXC",
    'LA LIBERTAD AVANZA': "LLA",
    'HACEMOS POR NUESTRO PAIS': "HXNP",
    'FRENTE DE IZQUIERDA Y DE TRABAJADORES - UNIDAD': "FIT"
}


def get_votes_per_party(content: dict) -> dict:
    record = {}
    for party in content['partidos']:
        record[ACRONYMS[party['name']]] = party['votos']
    return record


def process_desk_response(content: dict) -> dict:
    return {**get_geo_info(content), **get_desk_data(content), **get_votes_per_party(content)}


def request_desk_info(desk_code):
    response = requests.get(BASE_URL.format(desk_code=desk_code))
    if response.ok:
        content = response.json()
        with open(f'../data/raw/mesas/{desk_code}.json', 'w') as file:
            json.dump(content, file)
        return True, process_desk_response(response.json())
    else:
        return False, response.reason


def load_desk_into_df():
    desk_raw_dir = "../data/raw/mesas"
    records = []
    for desk_file in os.listdir(desk_raw_dir):
        if not desk_file.endswith("X.json"):
            continue
        with open(os.path.join(desk_raw_dir, desk_file), "r") as file:
            desk_json = json.load(file)
            record = process_desk_response(desk_json)
            record["id_mesa"] = desk_file.replace(".json", "")
            records.append(record)
    return pd.DataFrame(records)
