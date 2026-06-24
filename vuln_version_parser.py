import re
import time

import pandas as pd


def split_items(text: str) -> list[str]:
    """
    Splits a cell from 'Версия ПО' into separate records.
    Commas/semicolons inside parentheses are ignored.
    """
    if text is None or pd.isna(text):
        return []

    source = str(text).strip()
    if not source:
        return []

    items = []
    buffer = []
    depth = 0

    for ch in source:
        if ch == "(":
            depth += 1
        elif ch == ")" and depth > 0:
            depth -= 1

        if ch in ",;" and depth == 0:
            item = "".join(buffer).strip()
            if item:
                items.append(item)
            buffer = []
        else:
            buffer.append(ch)

    item = "".join(buffer).strip()
    if item:
        items.append(item)

    return items


def extract_trailing_parentheses(text: str) -> tuple[str | None, str]:
    """
    Extracts the software name from the final parentheses.
    Supports nested parentheses, for example:
    до 10.0 (Windows Server 2022, 23H2 Edition (Server Core installation))
    """
    source = str(text).strip()

    if not source.endswith(")"):
        return None, source

    depth = 0
    end = len(source) - 1

    for i in range(end, -1, -1):
        if source[i] == ")":
            depth += 1
        elif source[i] == "(":
            depth -= 1
            if depth == 0:
                software_name = source[i + 1 : end].strip()
                version_text = source[:i].strip()
                return software_name, version_text

    return None, source


def clean_spaces(value: str | None) -> str | None:
    if value is None:
        return None

    value = str(value).replace("\xa0", " ")
    value = re.sub(r"\s+", " ", value)
    return value.strip()


def clean_version(value: str | None) -> str | None:
    """
    Produces a simplified version string for matching.
    The original text is preserved separately in 'Исходный текст'.
    """
    if value is None:
        return None

    version = clean_spaces(value)

    if not version:
        return None

    version = re.sub(
        r"^\s*(?:верс(?:ия|ии)|version|release|релиз)\s+",
        "",
        version,
        flags=re.IGNORECASE,
    )
    version = re.sub(r"\s+включительно\s*$", "", version, flags=re.IGNORECASE)
    version = re.sub(r"\s+LTS\b", "", version, flags=re.IGNORECASE)
    version = re.sub(r"^v(?=\d)", "", version, flags=re.IGNORECASE)

    # 1.6 «Смоленск» -> 1.6
    version = re.sub(r"\s+[«\"].+[»\"]\s*$", "", version)

    version = version.strip(" .,:;")
    return version or None


def is_version_like(text: str | None) -> bool:
    if text is None:
        return False

    text = clean_spaces(text)
    return bool(re.match(r"^\d", text))


def make_record(
    raw_item: str,
    software_name: str | None,
    kind: str,
    operator: str | None = None,
    version: str | None = None,
    version_from: str | None = None,
    version_to: str | None = None,
    include_from: bool | None = None,
    include_to: bool | None = None,
    condition: str | None = None,
    pattern: str | None = None,
) -> dict:
    return {
        "Название ПО": software_name,
        "Тип": kind,
        "Оператор": operator,
        "Версия": clean_version(version),
        "Версия от": clean_version(version_from),
        "Версия до": clean_version(version_to),
        "Включая от": include_from,
        "Включая до": include_to,
        "Доп. условие": clean_spaces(condition),
        "Шаблон": pattern,
        "Разобрано": kind != "unknown",
        "Исходный текст": raw_item,
    }


def parse_item(item: str, fallback_software: str | None = None) -> dict:
    """
    Parses one part of a 'Версия ПО' cell.
    """
    raw_item = clean_spaces(item)
    extracted_software, body = extract_trailing_parentheses(raw_item)

    software_name = extracted_software or fallback_software
    text = clean_spaces(body)

    if not text or text.lower() in {"nan", "none"}:
        return make_record(raw_item, software_name, "empty", pattern="empty")

    if text in {"-", "—", "–", "нет данных", "н/д"}:
        return make_record(raw_item, software_name, "empty", pattern="empty")

    if re.fullmatch(r"(?:все|любые)\s+версии", text, flags=re.IGNORECASE):
        return make_record(
            raw_item,
            software_name,
            "all",
            operator="any",
            pattern="all_versions",
        )

    # от A до B / с A до B
    match = re.match(
        r"^(?:от|с)\s+(.+?)\s+до\s+(.+?)(?:\s+включительно)?$",
        text,
        flags=re.IGNORECASE,
    )
    if match:
        return make_record(
            raw_item,
            software_name,
            "range",
            operator="between",
            version_from=match.group(1),
            version_to=match.group(2),
            include_from=True,
            include_to=True,
            pattern="from_to",
        )

    # Исправление редкой опечатки из таблицы: от A о B
    match = re.match(
        r"^от\s+(.+?)\s+о\s+(.+?)(?:\s+включительно)?$",
        text,
        flags=re.IGNORECASE,
    )
    if match:
        return make_record(
            raw_item,
            software_name,
            "range",
            operator="between",
            version_from=match.group(1),
            version_to=match.group(2),
            include_from=True,
            include_to=True,
            pattern="typo_from_o_to",
        )

    # Исправление редкой опечатки из таблицы: от A от B включительно
    match = re.match(
        r"^от\s+(.+?)\s+от\s+(.+?)(?:\s+включительно)?$",
        text,
        flags=re.IGNORECASE,
    )
    if match:
        return make_record(
            raw_item,
            software_name,
            "range",
            operator="between",
            version_from=match.group(1),
            version_to=match.group(2),
            include_from=True,
            include_to=True,
            pattern="typo_from_from_to",
        )

    # Enterprise от A до B / Community Edition от A до B
    match = re.match(
        r"^(.+?)\s+(?:от|с)\s+(.+?)\s+до\s+(.+?)(?:\s+включительно)?$",
        text,
        flags=re.IGNORECASE,
    )
    if match:
        return make_record(
            raw_item,
            software_name,
            "range",
            operator="between",
            version_from=match.group(2),
            version_to=match.group(3),
            include_from=True,
            include_to=True,
            condition=match.group(1),
            pattern="condition_from_to",
        )

    # 18.3 до 18.4.5
    match = re.match(
        r"^(.+?)\s+до\s+(.+?)(?:\s+включительно)?$",
        text,
        flags=re.IGNORECASE,
    )
    if match and is_version_like(match.group(1)):
        return make_record(
            raw_item,
            software_name,
            "range",
            operator="between",
            version_from=match.group(1),
            version_to=match.group(2),
            include_from=True,
            include_to=True,
            pattern="version_to_version",
        )

    # до B / по B
    match = re.match(
        r"^(до|по)\s+(.+?)(?:\s+включительно)?$",
        text,
        flags=re.IGNORECASE,
    )
    if match:
        word = match.group(1).lower()
        include_to = word == "по" or bool(
            re.search(r"\bвключительно\b", text, flags=re.IGNORECASE)
        )
        return make_record(
            raw_item,
            software_name,
            "max",
            operator="<=" if include_to else "<",
            version_to=match.group(2),
            include_to=include_to,
            pattern="to",
        )

    # AEM Cloud Service до 2025.5 / Enterprise до 1.10.11
    match = re.match(
        r"^(.+?)\s+до\s+(.+?)(?:\s+включительно)?$",
        text,
        flags=re.IGNORECASE,
    )
    if match:
        include_to = bool(re.search(r"\bвключительно\b", text, flags=re.IGNORECASE))
        return make_record(
            raw_item,
            software_name,
            "max",
            operator="<=" if include_to else "<",
            version_to=match.group(2),
            include_to=include_to,
            condition=match.group(1),
            pattern="condition_to",
        )

    # от A / с A / начиная с A
    match = re.match(
        r"^(?:от|с|начиная\s+с)\s+(.+?)$",
        text,
        flags=re.IGNORECASE,
    )
    if match:
        return make_record(
            raw_item,
            software_name,
            "min",
            operator=">=",
            version_from=match.group(1),
            include_from=True,
            pattern="from",
        )

    # A и выше / A или новее
    match = re.match(
        r"^(.+?)\s+(?:и\s+выше|или\s+выше|и\s+новее|или\s+новее)$",
        text,
        flags=re.IGNORECASE,
    )
    if match:
        return make_record(
            raw_item,
            software_name,
            "min",
            operator=">=",
            version_from=match.group(1),
            include_from=True,
            pattern="and_above",
        )

    # A и ниже / A или старее
    match = re.match(
        r"^(.+?)\s+(?:и\s+ниже|или\s+ниже|и\s+старее|или\s+старее)$",
        text,
        flags=re.IGNORECASE,
    )
    if match:
        return make_record(
            raw_item,
            software_name,
            "max",
            operator="<=",
            version_to=match.group(1),
            include_to=True,
            pattern="and_below",
        )

    # <= A / >= A / < A / > A / = A
    match = re.match(r"^(<=|>=|<|>|==|=)\s*(.+?)$", text, flags=re.IGNORECASE)
    if match:
        operator = match.group(1)
        version = match.group(2)

        if operator in {"=", "=="}:
            return make_record(
                raw_item,
                software_name,
                "exact",
                operator="==",
                version=version,
                version_from=version,
                version_to=version,
                include_from=True,
                include_to=True,
                pattern="operator_exact",
            )

        if operator in {">", ">="}:
            return make_record(
                raw_item,
                software_name,
                "min",
                operator=operator,
                version_from=version,
                include_from=(operator == ">="),
                pattern="operator_min",
            )

        return make_record(
            raw_item,
            software_name,
            "max",
            operator=operator,
            version_to=version,
            include_to=(operator == "<="),
            pattern="operator_max",
        )

    # не выше A / не новее A
    match = re.match(r"^(?:не\s+выше|не\s+новее)\s+(.+?)$", text, flags=re.IGNORECASE)
    if match:
        return make_record(
            raw_item,
            software_name,
            "max",
            operator="<=",
            version_to=match.group(1),
            include_to=True,
            pattern="not_above",
        )

    # ниже A / меньше A / старее A
    match = re.match(r"^(?:ниже|меньше|старее)\s+(.+?)$", text, flags=re.IGNORECASE)
    if match:
        return make_record(
            raw_item,
            software_name,
            "max",
            operator="<",
            version_to=match.group(1),
            include_to=False,
            pattern="below",
        )

    # выше A / больше A / новее A
    match = re.match(r"^(?:выше|больше|новее)\s+(.+?)$", text, flags=re.IGNORECASE)
    if match:
        return make_record(
            raw_item,
            software_name,
            "min",
            operator=">",
            version_from=match.group(1),
            include_from=False,
            pattern="above",
        )

    # A - B / A – B. Разбирается только если по обе стороны тире текст похож на версию.
    match = re.match(r"^(.+?)\s+[-–—]\s+(.+?)$", text, flags=re.IGNORECASE)
    if match and is_version_like(match.group(1)) and is_version_like(match.group(2)):
        return make_record(
            raw_item,
            software_name,
            "range",
            operator="between",
            version_from=match.group(1),
            version_to=match.group(2),
            include_from=True,
            include_to=True,
            pattern="dash_range",
        )

    if software_name:
        return make_record(
            raw_item,
            software_name,
            "exact",
            operator="==",
            version=text,
            version_from=text,
            version_to=text,
            include_from=True,
            include_to=True,
            pattern="exact",
        )

    return make_record(raw_item, software_name, "unknown", pattern="unknown")


def parse_versions_cell(
    cell: str,
    vulnerability_id: str | None = None,
    fallback_software: str | None = None,
    source_row: int | None = None,
    level: str | None = None
) -> list[dict]:
    """
    Parses one cell from 'Версия ПО'.
    Returns a list because one cell can contain many products/versions.
    """
    records = []

    for item in split_items(cell):
        parsed = parse_item(item, fallback_software=fallback_software)
        parsed["Идентификатор"] = vulnerability_id
        parsed["Исходная строка"] = source_row
        parsed["Уровень опасности уязвимости"] = level
        records.append(parsed)

    return records


def parse_vulnerability_dataframe(
    df: pd.DataFrame,
    id_col: str = "Идентификатор",
    software_col: str = "Название ПО",
    version_col: str = "Версия ПО",
) -> pd.DataFrame:
    """
    Normalizes a vulnerability dataframe:
    one source row with many versions -> many parsed rows.
    """
    all_records = []

    for index, row in df.iterrows():
        vulnerability_id = row.get(id_col)
        fallback_software = row.get(software_col)
        versions = row.get(version_col)
        danger_level = row.get('Уровень опасности уязвимости')

        records = parse_versions_cell(
            versions,
            vulnerability_id=vulnerability_id,
            fallback_software=fallback_software,
            source_row=index,
            level=danger_level,
        )
        all_records.extend(records)

    return pd.DataFrame(all_records)


def parse_excel(
    path: str,
    sheet_name: str = "Уязвимости",
    header: int = 0,
    id_col: str = "Идентификатор",
    software_col: str = "Название ПО",
    version_col: str = "Версия ПО",
) -> pd.DataFrame:
    df = pd.read_excel(path, sheet_name=sheet_name, header=header, skiprows=2)
    df = df[df["Наименование ОС и тип аппаратной платформы"].str.contains("Астра")]
    return parse_vulnerability_dataframe(
        df,
        id_col=id_col,
        software_col=software_col,
        version_col=version_col,
    )


if __name__ == "__main__":
    clock = time.time()
    input_file = "./data/vullist.xlsx"

    parsed = parse_excel(input_file, sheet_name="Уязвимости", header=0)
    parsed.to_csv("./data/parsed_versions.csv", index=False, encoding="utf-8-sig")

    clock = time.time() - clock
    print(f"Работа с базой заняла {clock:.2f} секунд")

    # print("Parsed rows:", len(parsed))
    # print(parsed["Тип"].value_counts(dropna=False))
    # print("Unknown rows:", len(parsed[parsed["Тип"] == "unknown"]))
