import subprocess
import re

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


if __name__ == "__main__":
    #df_pkg = get_package_list()
    #df_lst = load_version_list()
    print(compare_versions("140.4.0esr-1~deb13u1", "140.4", "eq"))
