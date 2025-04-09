import json
import os
import yaml
import pandas as pd
from typing import Optional

BASE_DIR = os.environ.get('SITEPARSE3_PROJECT_DIR', os.path.dirname(os.path.dirname(__file__)))
SCP3_ENV = os.environ.get('SCP3_ENV', 'agents_dev')


def get_prompt(key: Optional[str]):
    filepath = BASE_DIR + f'/config/prompts.yaml'
    return get_configuration_from_filepath(filepath=filepath, key=key)


def get_configuration(key: Optional[str], module: str = None):
    module = module or SCP3_ENV
    filepath = BASE_DIR + f'/config/{module}.yaml'

    return get_configuration_from_filepath(filepath=filepath, key=key)


def get_configuration_from_filepath(filepath: str, key: Optional[str], encoding: str = 'utf-8') -> dict | None:
    with open(filepath, 'r', encoding=encoding) as fr:
        configuration = yaml.safe_load(fr)
    return configuration.get(key) if key else configuration


def read_excel(filepath: str, sheet: str = None):
    filepath = BASE_DIR + f'/config/{filepath}.xlsx'
    df = pd.read_excel(filepath, sheet_name=sheet, engine='openpyxl')
    json_data = df.to_json(orient='records', force_ascii=False)
    return json.loads(json_data)
