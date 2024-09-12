import json
from tqdm import tqdm
from openai import OpenAI
from concurrent.futures import ThreadPoolExecutor, as_completed
import argparse
from augment_utils import default, evolution


def parse_args():
    parser = argparse.ArgumentParser(description='Generate new instruction-output pairs using OpenAI API.')
    
    parser.add_argument('--api_key', type=str, required=True, help='API key for OpenAI.')
    parser.add_argument('--base_url', type=str, default='https://one-api.s.metames.cn:38443/v1', help='Base URL for OpenAI API.')
    parser.add_argument('--input_file', type=str, default='mine/air_travel_combined.json', help='Input file with instruction-output pairs.')
    parser.add_argument('--output_file', type=str, default='augmented/air_travel_augmented.json', help='Output file to save generated pairs.')
    parser.add_argument('--progress_file', type=str, default='augmented/progress.json', help='Progress file for saving intermediate results.')
    parser.add_argument('--target_count', type=int, default=32, help='Number of instruction-output pairs to generate.')
    parser.add_argument('--max_workers', type=int, default=1, help='Number of parallel workers for API requests.')
    parser.add_argument('--save_every', type=int, default=8, help='Save progress every n entries.')

    # debug only: set to 1 in production
    parser.add_argument('--percentage_of_data', type=float, default=0.01, help='Percentage of data to use from the input file.')
    parser.add_argument('--method', type=str, default="default", help='default method generating')

    return parser.parse_args()



def main():
    args = parse_args()
    # use the corresponding method
    try:
        generate_new_instructions = eval(args.method)
    except Exception as e:
        print(f"Error when loading method {str(e)}")
    
    client = OpenAI(api_key=args.api_key, base_url=args.base_url)

    with open(args.input_file, 'r', encoding='utf-8') as f:
        data = json.load(f)

    num_samples = int(len(data) * args.percentage_of_data)
    selected_data = data[:num_samples]


    new_data = []
    progress_bar = tqdm(total=args.target_count)

    # load progress if exists
    try:
        with open('augmented/progress.json', 'r', encoding='utf-8') as f:
            new_data = json.load(f)
            progress_bar.update(len(new_data))
    except FileNotFoundError:
        pass  # restart if we do not have the progress file

    if args.max_workers == 1:
        try:
            for idx, entry in enumerate(selected_data):
                result = generate_new_instructions(entry, idx, client)
                new_data.extend(result)
                progress_bar.update(len(result))

                if len(new_data) % args.save_every == 0:
                    with open(args.progress_file, 'w', encoding='utf-8') as f:
                        json.dump(new_data, f, ensure_ascii=False, indent=2)

                # end condition: reach args.target_count
                if len(new_data) >= args.target_count:
                    break

        except Exception as e:
            print(f"Error processing entry {idx}: {str(e)}")

    # multi workers
    else:
        with ThreadPoolExecutor(max_workers=args.max_workers) as executor:
            try:
                future_to_idx = {executor.submit(generate_new_instructions, entry, idx, client): idx for idx, entry in enumerate(selected_data)}

                # if don't set timeout, the program seems not to be able to exit
                for future in as_completed(future_to_idx, timeout=120):
                    try:
                        result = future.result(timeout=120)
                        new_data.extend(result)
                        progress_bar.update(len(result))

                        if len(new_data) % args.save_every == 0:
                            with open('augmented/progress.json', 'w', encoding='utf-8') as f:
                                json.dump(new_data, f, ensure_ascii=False, indent=2)

                        # end condition: reach args.target_count
                        if len(new_data) >= args.target_count:
                            break

                    except Exception as e:
                        print(f"Error processing entry {future_to_idx[future]}: {str(e)}")
            finally:
                executor.shutdown(wait=True)  # make sure all threads are done

    with open('augmented/air_travel_augmented.json', 'w', encoding='utf-8') as f:
        json.dump(new_data, f, ensure_ascii=False, indent=2)

    progress_bar.close()

if __name__ == '__main__':
    main()