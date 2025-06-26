import os
import json
import yaml
from collections import defaultdict

def main():
    apps_dir = 'apps'
    output_file = 'apps.json'

    # This will be a nested structure: categories -> subcategories -> apps
    data_structure = defaultdict(lambda: defaultdict(list))

    for app_dir_name in sorted(os.listdir(apps_dir)):
        app_path = os.path.join(apps_dir, app_dir_name)
        manifest_path = os.path.join(app_path, 'manifest.yaml')

        if os.path.isdir(app_path) and os.path.exists(manifest_path):
            print(f"Processing {manifest_path}...")
            with open(manifest_path, 'r') as f:
                manifest = yaml.safe_load(f)

                app_data = {
                    'appId': app_dir_name,
                    'appName': manifest.get('appName'),
                    'description': manifest.get('description'),
                    'version': manifest.get('version')
                }

                category = manifest.get('category', 'Uncategorized')
                subcategory = manifest.get('subcategory') # Can be None

                if subcategory:
                    data_structure[category][subcategory].append(app_data)
                else:
                    # Use a special key for apps directly under a category
                    data_structure[category]['__apps__'].append(app_data)

    # Convert the nested defaultdict to a sorted list structure for JSON
    final_list = []
    for category, sub_data in sorted(data_structure.items()):
        subcategories_list = []

        # Apps directly under the category go first
        if '__apps__' in sub_data:
            for app in sorted(sub_data['__apps__'], key=lambda x: x['appName']):
                subcategories_list.append(app)

        # Then add subcategories
        for subcategory, apps in sorted(sub_data.items()):
            if subcategory == '__apps__':
                continue
            sorted_apps = sorted(apps, key=lambda x: x['appName'])
            subcategories_list.append({
                'subcategory': subcategory,
                'apps': sorted_apps
            })

        final_list.append({
            'category': category,
            'items': subcategories_list
        })

    with open(output_file, 'w') as f:
        json.dump(final_list, f, indent=2)

    print(f"Successfully generated {output_file} with nested subcategories.")

if __name__ == '__main__':
    main()
