import requests

url = "http://rasa.cluster.issel.ee.auth.gr/model/train?token=rasaToken"

payload = "actions:\n- action_ask_form1_form_city_slot\n- action_ask_form1_form_time_slot\n- validate_form1_form\n- action_answer_back\nentities:\n- Doctor\nforms:\n  form1_form:\n    required_slots:\n    - city_slot\n    - time_slot\n    - answer\nintents:\n- ask_weather\n- ask_weather_2\nsession_config:\n  carry_over_slots_to_new_session: false\n  session_expiration_time: 5\nslots:\n  answer:\n    influence_conversation: false\n    mappings:\n    - conditions:\n      - active_loop: form1_form\n        requested_slot: answer\n      type: custom\n    type: text\n  city_slot:\n    influence_conversation: false\n    mappings:\n    - conditions:\n      - active_loop: form1_form\n        requested_slot: city_slot\n      entity: LOC\n      type: from_entity\n    type: text\n  slotA:\n    influence_conversation: false\n    initial_value: 10\n    mappings:\n    - type: custom\n    type: any\n  slotB:\n    influence_conversation: false\n    initial_value: asdas\n    mappings:\n    - type: custom\n    type: any\n  slotC:\n    influence_conversation: false\n    mappings:\n    - type: custom\n    type: any\n  time_slot:\n    influence_conversation: false\n    mappings:\n    - conditions:\n      - active_loop: form1_form\n        requested_slot: time_slot\n      entity: Doctor\n      type: from_entity\n    type: text\nversion: '3.1'\n\nlanguage: en\npipeline:\n- name: WhitespaceTokenizer\n- name: RegexFeaturizer\n- name: CRFEntityExtractor\n- name: LexicalSyntacticFeaturizer\n- name: CountVectorsFeaturizer\n- analyzer: char_wb\n  max_ngram: 4\n  min_ngram: 1\n  name: CountVectorsFeaturizer\n- epochs: 200\n  name: DIETClassifier\n- name: EntitySynonymMapper\n- epochs: 100\n  name: ResponseSelector\npolicies:\n- name: MemoizationPolicy\n- epochs: 200\n  max_history: 5\n  name: TEDPolicy\n- name: RulePolicy\nrecipe: default.v1\n\nnlu:\n- examples: '- Tell me the weather please\n\n    - I want to tell me the weather\n\n    '\n  intent: ask_weather\n- examples: '- I want to tell me the weather for\n\n    - Tell me the weather for\n\n    - Tell me the weather please for\n\n    '\n  intent: ask_weather_2\n\nstories:\n- steps:\n  - intent: ask_weather\n  - action: form1_form\n  - active_loop: form1_form\n  - active_loop: null\n  - action: action_answer_back\n  story: weather_dialogue - ask_weather\n- steps:\n  - intent: ask_weather_2\n  - action: form1_form\n  - active_loop: form1_form\n  - active_loop: null\n  - action: action_answer_back\n  story: weather_dialogue - ask_weather_2\n\nrules:\n- rule: Activate form1_form with ask_weather\n  steps:\n  - intent: ask_weather\n  - action: form1_form\n  - active_loop: form1_form\n- rule: Activate form1_form with ask_weather_2\n  steps:\n  - intent: ask_weather_2\n  - action: form1_form\n  - active_loop: form1_form\n- condition:\n  - active_loop: form1_form\n  rule: Submit form1_form\n  steps:\n  - active_loop: null\n  - action: action_answer_back\n"
headers = {
  'Content-Type': 'application/yaml'
}

response = requests.request("POST", url, headers=headers, data=payload,
                            verify=False)

with open("model-trained.tar.gz", "wb") as f:
    f.write(response.content)
