import subprocess

import pandas as pd

software_to_pkg = {
    "firefox esr" : ["firefox-esr"]
}

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

def get_dpkg_list() -> pd.DataFrame:
        dpkg_result = subprocess.run(
        ['dpkg-query', '-W', "-f='${Package}\t${Version}\t${Architecture}\n'"],
        stdout=subprocess.PIPE,
        text=True
    )
        print(dpkg_result.stdout)

def load_version_list() -> pd.DataFrame:
    df = pd.read_csv("./data/parsed_versions.csv")
    df["Название ПО"] = df["Название ПО"].str.lower()  
    return df 



if __name__ == "__main__":
    #df_pkg = get_package_list()
    #df_lst = load_version_list()
    #test = df_pkg[df_pkg['name'].str.contains('fox')]
    #print(df_pkg[df_pkg['name'].str.contains('fox')])
    #print(df_lst[df_lst['Название ПО'].str.contains('fox')])
    get_dpkg_list()