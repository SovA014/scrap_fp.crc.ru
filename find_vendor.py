import re
from bs4 import BeautifulSoup
import json


region = '82'
project_data = []
project_name = '2076896'


def find_vendor(project_data, region):
    try:
        with open(f"data/data_{region}/patterns_vendor.json", 'r', encoding='utf-8') as f:
            vendor_dict = json.load(f)
    except Exception:
        with open(f"patterns_vendor.json", 'r', encoding='utf-8') as f:
            vendor_dict = json.load(f)
    # print(project_data)
    vendor_list = []
    for data_src in project_data:
        # print(data_src)
        for vend, pattern_vendor in vendor_dict.items():
            # print(vendor_dict)
            data_vendor = re.findall(re.compile(pattern_vendor.replace("\n", "")), str(data_src))
            # print(data_vendor)
            if data_vendor:
                vendor_list.append(vend.strip(' '))
    vendor = []
    for operator in vendor_list:
        if operator not in vendor:
            vendor.append(operator)
    # print(gps_remove_copy)
    if len(vendor) == 0:
        vendor = ["оператор не найден"]
    return vendor


if __name__ == "__main__":
    try:
        # print(f"data/data_{region}/{project_name}.html")
        with open(f"data/data_{region}/{project_name}.html", encoding='utf-8') as file:  # открываем файл
            srs = file.read()  # читаем файл в srs
    except Exception as err:
        # print(err)
        with open(f"data/data_{region}/data_without_attachment/{project_name}.html",
                  encoding='utf-8') as file:  # открываем файл
            srs = file.read()  # читаем файл в srs
    soup = BeautifulSoup(srs, "lxml")
    try:
        project_data = re.sub(r'\s+', ' ', soup.find("noindex").find_next("table").find_next("td", text=re.compile(
            "([Пп]роектная документация)")).find_next("td").find(
            "b").text)  # собираем информацию, чтобы вытащить данные

    except Exception:
        print("Не удалось извлечь название проектной документации из файла", f"{project_name}.html")

    try:
        attachment_data = soup.find("noindex").find_next("table").find_next("td", text=re.compile(
            "([Пп]риложение)")).find_all_next("td")  # собираем информацию, чтобы вытащить данные

    except Exception:
        # print("нет приложения в файле", f"{project_name}.html")
        attachment_data = []

    # vendor = find_vendor(project_data.split('^') + attachment_data, region)
    print(find_vendor(project_data.split('^') + attachment_data, region))

