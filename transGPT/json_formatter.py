import json

file_path = "TransGPT-sft.json"
output_file ="TransGPT-sft-formatted.json"

with open(file_path, 'r', encoding='utf-8') as file:
    raw_data = file.readlines()

json_data = "[" + ",".join(raw_data) + "]"

formatted_data = json.loads(json_data)
parsed_data = [json.loads(entry) for entry in formatted_data]

json.dump(parsed_data, open(output_file, 'w', encoding='utf-8',), indent=2, ensure_ascii=False)