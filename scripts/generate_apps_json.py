import os
import json
import yaml
from collections import defaultdict

def main():
    apps_dir = 'apps'
    output_file = 'apps.json'
    data_structure = defaultdict(lambda: defaultdict(list))

    for app_dir_name in sorted(os.listdir(apps_dir)):
        app_path = os.path.join(apps_dir, app_dir_name)
        manifest_path = os.path.join(app_path, 'manifest.yaml')

        if os.path.isdir(app_path) and os.path.exists(manifest_path):
            with open(manifest_path, 'r') as f:
                manifest = yaml.safe_load(f)
                app_data = {
                    'appId': app_dir_name,
                    'appName': manifest.get('appName'),
                    'description': manifest.get('description'),
                    'version': manifest.get('version'),
                    'cpu': manifest.get('cpu'),
                    'memory': manifest.get('memory')
                }
                category = manifest.get('category', 'Uncategorized')
                subcategory = manifest.get('subcategory')

                if subcategory:
                    data_structure[category][subcategory].append(app_data)
                else:
                    data_structure[category]['__apps__'].append(app_data)

    final_list = []
    for category, sub_data in sorted(data_structure.items()):
        subcategories_list = []
        if '__apps__' in sub_data:
            for app in sorted(sub_data['__apps__'], key=lambda x: x['appName']):
                subcategories_list.append(app)
        for subcategory, apps in sorted(sub_data.items()):
            if subcategory == '__apps__':
                continue
            sorted_apps = sorted(apps, key=lambda x: x['appName'])
            subcategories_list.append({ 'subcategory': subcategory, 'apps': sorted_apps })

        final_list.append({ 'category': category, 'items': subcategories_list })

    with open(output_file, 'w') as f:
        json.dump(final_list, f, indent=2)

    print(f"Successfully generated {output_file} with nested subcategories.")

if __name__ == '__main__':
    main()
