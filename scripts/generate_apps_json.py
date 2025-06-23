import os
import json
import yaml
from collections import defaultdict

def main():
    apps_dir = 'apps'
    output_file = 'apps.json'

    categorized_apps = defaultdict(list)

    # Walk through each directory in the apps folder
    for app_name in sorted(os.listdir(apps_dir)): # Sort app directories
        app_path = os.path.join(apps_dir, app_name)
        manifest_path = os.path.join(app_path, 'manifest.yaml')

        if os.path.isdir(app_path) and os.path.exists(manifest_path):
            print(f"Processing {manifest_path}...")
            with open(manifest_path, 'r') as f:
                manifest = yaml.safe_load(f)

                app_data = {
                    'appName': manifest.get('appName'),
                    'description': manifest.get('description'),
                    'version': manifest.get('version')
                }

                category = manifest.get('category', 'Uncategorized')
                categorized_apps[category].append(app_data)

    # Format the data into the final list structure
    final_list = []
    # Sort categories alphabetically
    for category in sorted(categorized_apps.keys()):
        # Sort apps within each category alphabetically by appName
        sorted_apps = sorted(categorized_apps[category], key=lambda x: x['appName'])
        final_list.append({
            'category': category,
            'apps': sorted_apps
        })

    # Write the final JSON file
    with open(output_file, 'w') as f:
        json.dump(final_list, f, indent=2)

    print(f"Successfully generated {output_file} with sorted data.")

if __name__ == '__main__':
    main()
