
# make sure there is no `progress.json` in `augmented` folder

# single worker version
python data_gen.py --api_key "your_api_key" --target_count 20 --percentage_of_data 0.01

## evolution method
python data_gen.py --api_key "your_api_key" --target_count 20 --percentage_of_data 0.01 --method evolution


# multi workers version
python data_gen.py --api_key "your_api_key" --target_count 50 --percentage_of_data 0.01 --max_workers 4