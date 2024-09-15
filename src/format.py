import json
import argparse

file_path = "TransGPT-sft.json"
output_file ="TransGPT-sft-formatted.json"

def format_json(file_path, output_file):
    with open(file_path, 'r', encoding='utf-8') as file:
        raw_data = file.readlines()

    json_data = "[" + ",".join(raw_data) + "]"

    formatted_data = json.loads(json_data)
    parsed_data = [json.loads(entry) for entry in formatted_data]

    json.dump(parsed_data, open(output_file, 'w', encoding='utf-8',), indent=2, ensure_ascii=False)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Process JSON files concurrently.")
    parser.add_argument(
        "--input_path", default="saves/tst_save.json" ,type=str, required=True, help="Path to the input JSON file."
    )
    parser.add_argument(
        "--output_path", default="saves/tst_save_formatted.json" , type=str, required=True, help="Path to the output JSON file."
    )

    args = parser.parse_args()
    file_path = args.input_path
    output_file = args.output_path

    format_json(file_path, output_file)
