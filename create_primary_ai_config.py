import json

aiconfig = {'config_id': 1, 'ai_model': 'models/gemini-2.0-flash', 'ai_role': 'model', 'ai_temperature': 0.4, 'ai_top_p': 1, 'ai_top_k': 1, 'ai_max_out': 2048}

with open('ai_config.json', 'w') as jf:
    json.dump(aiconfig, jf, indent=4)
