import json

# https://simplemaps.com/gis/country/ru#admin1

def rename_regions():

    # Загрузка файла со сопоставлением (mapping.json)
    with open("regions/names_mapping.json", "r", encoding="utf-8") as f:
        mapping_data = json.load(f)

    # Формируем словарь: ключ – id региона, значение – русское название (region_ru)
    region_ru_mapping = {item["name"]: item["region_ru"] for item in mapping_data}

    # Загружаем исходный файл GeoJSON
    with open("regions/ru_regions_base.json", "r", encoding="utf-8") as f:
        geojson_data = json.load(f)

    # Для каждого элемента (feature) в GeoJSON заменяем значение поля "name"
    for feature in geojson_data.get("features", []):
        props = feature.get("properties", {})
        region_name = props.get("name")
        if region_name in region_ru_mapping:
            props["name"] = region_ru_mapping[region_name]
            # При желании можно сохранить новое поле отдельно
            props["region_ru"] = region_ru_mapping[region_name]

    # Сохраняем обновлённый GeoJSON в новый файл
    with open("regions/ru_regions_updated.json", "w", encoding="utf-8") as f:
        json.dump(geojson_data, f, ensure_ascii=False, indent=2)

    print("Названия регионов успешно обновлены и сохранены в файл ru_regions_updated.json")