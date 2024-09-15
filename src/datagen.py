import jsonlines
from concurrent.futures import ThreadPoolExecutor
from tqdm import tqdm
import os
import argparse
from baseGPT import BaseGPT
import json


def gpt_datagen(args):
    gptGen = BaseGPT(model_name=args.model_name, keys_path=args.keys_path, base_url=args.base_url)

    def process_item(text: dict):
        tag = args.tag
        from template import TEMPLATES
        template = TEMPLATES[tag]
        formatted_text = template.format(**text)
        # since should result in json format, should use try catch
        content = gptGen(*formatted_text)
        return content

    output_path = args.output_path
    input_path = args.input_path

    # simple way to check unprocessed data, may not be accurate
    processed_ids = set()
    if os.path.exists(output_path):
        with jsonlines.open(output_path, "r") as f:
            for id, item in enumerate(f):
                processed_ids.add(id)

    text_to_process = []

    with open(input_path, "r", encoding="utf-8") as f:
        data = json.load(f)
        for id, text in enumerate(data):
            if id not in processed_ids:
                # every text is a dict, according to alpaca format
                # instruction, output

                text_to_process.append(text)

    # multi-threaded parallel processing
    with jsonlines.open(
        output_path, "a" if os.path.exists(output_path) else "w"
    ) as writer:
        with ThreadPoolExecutor(max_workers=args.max_workers) as executor:
            futures = {
                executor.submit(process_item, text): text for text in text_to_process
            }
            # Use tqdm to display progress
            for future in tqdm(
                futures,
                total=len(text_to_process),
                desc=f"Processing {input_path} texts",
            ):
                try:
                    item = future.result()
                    if len(item) > 5:
                        writer.write(item)
                except Exception as e:
                    print(f"\nError processing entry: {str(e)}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Process JSON files concurrently.")
    parser.add_argument(
        "--model_name",
        type=str,
        default="deepseek-chat",
        help="Name of the OpenAIGPT model to use.",
    )
    parser.add_argument(
        "--base_url",
        type=str,
        default="https://api.deepseek.com/v1",
        required=False,
        help="API url for the OpenAIGPT service.",
    )
    parser.add_argument(
        "--keys_path",
        type=str,
        default="api_key.txt",
        required=False,
        help="API key for the OpenAIGPT service.",
    )
    parser.add_argument(
        "--input_path", type=str, required=True, help="Path to the input JSON file."
    )
    parser.add_argument(
        "--output_path", type=str, required=True, help="Path to the output JSON file."
    )
    parser.add_argument(
        "--max_workers",
        type=int,
        default=4,
        help="Maximum number of workers for concurrent processing.",
    )
    parser.add_argument(
        "--tag",
        type=str,
        default="evolution",
        required=True,
        help="The mode for GPT generation.",
    )

    args = parser.parse_args()
    gpt_datagen(args)
