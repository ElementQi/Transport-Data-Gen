
# Generate data for the air quality demo
python src/datagen.py --input_path data/air_demo.json --keys_path src/api_key.txt --output_path saves/tst_save.json --max_workers 4 --tag evolution

# format the generated data to alpaca format
python src/format.py --input_path saves/tst_save.json --output_path saves/tst_save_formatted.json