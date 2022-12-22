#!/usr/bin/env python3

import requests

RASA_TOKEN='rasaToken'

VERB = "PUT"
MODEL_PUT_URL = f"https://rasa.cluster.issel.ee.auth.gr/model"

MODEL_FILE_PATH = '/app/models/20221222-144003-moderato-starling.tar.gz'

headers = {
  'Content-Type': 'application/json'
}

body_params = {
    'model_file': MODEL_FILE_PATH,
}

query_params = {
    'token': 'rasaToken',
}

response = requests.request(VERB, MODEL_PUT_URL, headers=headers,
                            json=body_params, params=query_params,
                            verify=False)

print(response.headers)
