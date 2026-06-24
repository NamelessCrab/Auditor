import subprocess

import pandas as pd

def get_package_list() -> pd.DataFrame:
    apt_result = subprocess.run(
        ['apt', 'list', '--installed'],
        stdout=subprocess.PIPE,
        text=True
        )
    package_dict = {
        'name': [],
        'version': []
    }   
    for line in apt_result.stdout.splitlines()[1:]:
        if '/' in line:
            package_dict['name'].append(line.split('/')[0])
            version = line.split('/')[1]
            version = version.split(' ')[1]
            version = version.split(' ')[0]
            package_dict['version'].append(version)
    return pd.DataFrame(package_dict)

    
def load_version_list() -> pd.DataFrame:
    return pd.read_csv(".\data\parsed_versions.csv")   


if __name__ == "__main__":
    df_pkg = get_package_list()
    df_lst = load_version_list()
    test = df_pkg[df_pkg['name'].str.contains('fox')]
    df_lst["Название ПО"] = df_lst[df_lst['Название ПО'].str.lower]
    print(df_lst[df_lst['Название ПО'].str.contains('firefox-esr')])