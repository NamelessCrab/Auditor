import subprocess
import re

import pandas as pd

from data.match import lst_to_pkg


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
    df = pd.read_csv("./data/parsed_versions.csv")
    df["Название ПО"] = df["Название ПО"].str.lower()  
    return df 

def normalize_version(version: str) -> str:
    version = (version or "").strip()
    v_match = re.match(r"^\s*(\d+)(?:\.(\d+))?(?:\.(\d+))?", version)
    if not v_match:
        return version
    major, minor, patch = v_match.group(1), v_match.group(2), v_match.group(3)
    if patch is not None:
        return f"{major}.{minor}.{patch}"
    if minor is not None:
        return f"{major}.{minor}"
    return major

def compare_versions(version_pkg: str, version_lst: str, operator: str) -> bool:
    result = subprocess.run(
        ["dpkg", "--compare-versions", version_pkg, operator, version_lst],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL
    )
    return result.returncode == 0

def check_vuln(vuln: pd.Series, ver: "str"):
    """
    operator:
    lt  <
    le  <=
    eq  ==
    ge  >=
    gt  >
    """
    type = vuln['Тип']
    match type:
        case "exact":
            pass
        case "max":
            pass
            print("И сюда скачался...")
        case "min":
            pass
        case "range":
            pass
        case "empty":
            pass



def base_check(pkg: pd.DataFrame, lst: pd.DataFrame):
    matched_names = []
    for _, pkg in pkg.iterrows():
        name = pkg['name']
        version = pkg['version']

        false_names = [] 
        for key, pattern in lst_to_pkg.items():
            for pattern_name in pattern:
                if pattern_name == name:
                    matched_names.append(key)
                else:
                    false_names.append(name)

        if not matched_names:
            continue
    
    matched_names = set(matched_names)
    matched_vuln = lst[lst['Название ПО'].isin(matched_names)]
    print(matched_names, '\n\n\n', matched_vuln)
    
    return matched_names
'''
    for _, vuln in matched_vuln.iterrows(): #Название ПО \ Тип \ Оператор \ Версия \ Версия от \ Версия до
        pass
'''
    
        



if __name__ == "__main__":
    df_pkg = get_package_list() # name, version
    df_lst = load_version_list()
    base_check(df_pkg, df_lst)

    
