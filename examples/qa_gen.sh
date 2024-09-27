
# Generate data for the air travel QA task
python src/datagen.py --model_name gpt-4o-mini --base_url https://one-api.s.metames.cn:38443/v1 --input_path chunk_gen/title_context_pairs.json --keys_path src/api_key.txt --output_path saves/air_qa_pairs.json --max_workers 4 --tag question_answer_gen

# format the generated data to alpaca format
python src/format.py --input_path saves/air_qa_pairs.json --output_path saves/air_qa_pairs_formatted.json

# data augmentation for QA-pairs
python src/datagen.py --model_name gpt-4o-mini --base_url https://one-api.s.metames.cn:38443/v1 --input_path saves/air_qa_pairs_formatted.json --keys_path src/api_key.txt --output_path saves/air_qa_pairs_augmented.json --max_workers 4 --tag evolution

# format the augmentation for QA-pairs data to alpaca format
python src/format.py --input_path saves/air_qa_pairs_augmented.json --output_path saves/air_qa_pairs_augmented_formatted.json
