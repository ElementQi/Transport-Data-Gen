
# Run with combine flag to combine contexts
python pre.py --data_modes train valid --output_file mine/air_travel_combined.json --combine

# Run without combining, and clean up questions
python pre.py --data_modes train valid --output_file mine/air_travel.json
