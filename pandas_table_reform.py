import pandas as pd
import time

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

# mask = astra["Название ПО"].str.contains(", ")
# mask_result = astra[mask]
# astra_split = astra.assign(names_split=astra["Название ПО"].str.split(", "))
# astra = astra["Название ПО"] = astra_split["names_split"]
astra.to_excel("./data/ready.xlsx", sheet_name="Уязвимости", index=False)

clock = time.time() - clock
print(f"Работа с базой заняла {clock:.2f} секунд")
