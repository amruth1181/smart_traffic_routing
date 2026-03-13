import os
import glob

replacements = {
    '/Users/amruth/smart_traffic_routing/pems_5min_cleaned_with_location.csv': '/Users/amruth/smart_traffic_routing/pems_5min_cleaned_with_location.csv',
    'file:///Users/amruth/smart_traffic_routing/streaming/spark-checkpoints/': 'file:///Users/amruth/smart_traffic_routing/streaming/spark-checkpoints/',
    '/Users/amruth/smart_traffic_routing/models/traffic_speed_model.pkl': '/Users/amruth/smart_traffic_routing/models/traffic_speed_model.pkl'
}

files_to_check = glob.glob('/Users/amruth/smart_traffic_routing/**/*.py', recursive=True)

for file in files_to_check:
    with open(file, 'r') as f:
        content = f.read()
    
    new_content = content
    for old, new in replacements.items():
        new_content = new_content.replace(old, new)
        
    if new_content != content:
        with open(file, 'w') as f:
            f.write(new_content)
        print(f"Updated {file}")
