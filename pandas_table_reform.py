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
        #"Наименование уязвимости",
        #"Название ПО",
        "Версия ПО"
        #"Наименование ОС и тип аппаратной платформы",
        #"Возможные меры по устранению",
        #"Уровень опасности уязвимости",
    ]
]
astra['Идентификатор'] = astra.index
items = astra['Версия ПО'].str.split(r'\s*,\s*', regex=True)
exp = astra[['Идентификатор']].join(items.rename('ITEM')).explode('ITEM').reset_index(drop=True)
exp['item']
#Дальше необходимо разделить на ВЕРСИЯ\ИМЯ, почистить их и объединить.

print(exp.head(2))

clock = time.time() - clock
print(f"Работа с базой заняла {clock:.2f} секунд")
