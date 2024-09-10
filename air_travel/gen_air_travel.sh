
# Without combining contexts (default behavior):
python pre.py --data_modes train valid --output_file mine/air_travel.txt

# With combining contexts (use `--combine` flag):
python pre.py --data_modes train valid --output_file mine/air_travel_combined.txt --combine
