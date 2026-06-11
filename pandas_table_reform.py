import time
import re

import pandas as pd



clock = time.time()

data_frame = pd.read_excel(
    "./data/vullist.xlsx",
    sheet_name="Уязвимости",
    skiprows=2,
    index_col="Идентификатор",
)

data_frame["Уровень опасности уязвимости"] = data_frame[
    "Уровень опасности уязвимости"
].fillna("Не указано")
astra = data_frame[
    data_frame["Наименование ОС и тип аппаратной платформы"].str.contains("Астра")
]

astra = astra[
    [
        "Наименование уязвимости",
        "Название ПО",
        "Версия ПО",
        "Наименование ОС и тип аппаратной платформы",
        "Возможные меры по устранению",
        "Уровень опасности уязвимости",
    ]
]

py_test = astra['Версия ПО'].iloc[129]

reform = []
for line in py_test.split(', '):
    version, name = line.split("(")
    version = re.sub(r'[^0-9.]', '',version)
    name = name.rstrip(')')
    print(name, version)



#astra.to_excel("./data/ready.xlsx", sheet_name="Уязвимости", index=True)

clock = time.time() - clock
print(f"Работа с базой заняла {clock:.2f} секунд")


def make_lists(df):
    mask = df["Название ПО"].str.contains(", ")
    mask_result = df[mask]
    df_split = df.assign(names_split=df["Название ПО"].str.split(", "))
    df = df["Название ПО"] = df_split["names_split"]

def save_txt(text, name):
    with open(name, "w", encoding="utf-8") as file:
        for name, version in text:
            file.write(f"{name} {version}\n")