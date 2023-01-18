import re
import os
import sqlite3
from bs4 import BeautifulSoup
import json
import sys
from make_pattern import make_pattern
from find_vendor import find_vendor

region = '04'
gps_dict = {}
data_list = []
list_files = []
dist_files_gps_with_garbage = {}
dist_files_only_one_gps = {}
dist_files_only_one_gps_in_name_project = {}
dist_files_gps_60_gps = {}


def convertCoordinates(gps_srs_dict):

    def convert(values):
        # print(values)
        lat_lng = []
        for item in values:
            # print(item)
            try:
                if len(item) == 2:
                    gps = float(item[0] + '.' + re.sub("[,.]", "", item[1]))
                    # print(gps)
                elif int(item[1]) > 60 or float((item[2]).replace(',', '.')) > 60:
                    lat_lng = []

                    for coord in values:
                        if len(coord) == 3:
                            gps = float(coord[0] + '.' + coord[1] + re.sub("[,.]", "", coord[2]))
                        else:
                            gps = float(coord[0] + '.' + re.sub("[,.]", "", coord[1]))
                        # print(gps)
                        if max(latList) > gps > min(latList) or max(lngList) > gps > min(lngList):
                            lat_lng.append(gps)
                    dist_files_gps_60_gps[project_name] = (values, lat_lng)
                    break
                else:
                    gps = float(item[0] + str('{:0.9f}'.format(float(item[1] + str(float(item[2].replace(',', '.')) / 60)[1:]) / 60))[1:])

                if max(latList) > gps > min(latList) or max(lngList) > abs(gps) > min(lngList):
                    lat_lng.append(gps)
            except Exception:
                print('Ошибка конвертации координат', project_name, ':', values)
        # print(lat_lng)
        return lat_lng

    # print(gps_srs_dict)
    for key, val in gps_srs_dict.items():
        for k, v in val.items():
            for keys, values in v.items():
                lat_lng = convert(values)

                if lat_lng:
                    gps_remove_copy = lat_lng
                    for i in range(len(lat_lng)):
                        for a in lat_lng[i + 1:]:
                            if abs(lat_lng[i] - a) <= 0.005:
                                gps_remove_copy.remove(a)
                    lat_lng = gps_remove_copy

                    if len(gps_remove_copy) > 2:
                        dist_files_gps_with_garbage[f'{project_name} {key}_{k}_{keys}'] = values
                        coord_list = []
                        for gps in gps_remove_copy:
                            if max(latList) > gps > min(latList):
                                coord_list.append(gps)
                                gps_remove_copy.remove(gps)
                                break
                        for gps in gps_remove_copy:
                            if max(lngList) > abs(gps) > min(lngList):
                                coord_list.append(gps)
                                break
                        lat_lng = coord_list

                    if len(lat_lng) == 2:
                        if key == 'name_data' or key == 'attachment_data':
                            return lat_lng
                        elif len(v) == 1 and len(val) == 1:
                            return lat_lng

                    elif len(lat_lng) == 1:
                        dist_files_only_one_gps[f'{project_name} {key}_{k}_{keys}'] = val
    # print(lat_lng)
    return lat_lng


def checkCoordinates(coordinates):
    if region in ('14', '03', '04', '17', '19', '22', '24', '25', '27', '28', '38', '41', '42', '45', '49',
                  '54', '55', '70', '72', '74', '75', '79', '87', '94') and abs(coordinates[0]) > abs(coordinates[1]):
        coordinates[0], coordinates[1] = coordinates[1], coordinates[0]

    elif region in (
    '01', '23', '18', '21', '10', '12', '13', '29', '31', '32', '33', '34', '35', '36', '39', '40', '43', '44', '46',
    '47', '48', '50', '51', '52', '53', '57', '58', '60', '61', '62', '67', '68', '69', '71', '73', '76', '77', '78', '82', '83') and \
            coordinates[0] < coordinates[1]:
        coordinates[0], coordinates[1] = coordinates[1], coordinates[0]

    listUnverifiedFiles = {}
    if max(latList) > coordinates[0] > min(latList) and max(lngList) > abs(coordinates[1]) > min(lngList):
        return coordinates
    else:
        listUnverifiedFiles[project_name] = coordinates
        if os.path.exists(f"data/data_{region}/dist_unverified_files.json"):
            with open(f"data/data_{region}/dist_unverified_files.json", "a") as file:
                json.dump(listUnverifiedFiles, file, indent=4, ensure_ascii=False)
        else:
            with open(f"data/data_{region}/dist_unverified_files.json", "w") as file:
                json.dump(listUnverifiedFiles, file, indent=4, ensure_ascii=False)
        return 0.0, 0.0


def searchCoordinates (pattern_gps_list, data_srs_list, stage_two=False):
    gps_dict_br = {}
    # print(data_srs_list)
    def removeCopy (data_gps_list):
        gps_remove_copy = []
        for gps in data_gps_list:
            if gps not in gps_remove_copy:
                gps_remove_copy.append(gps)
        return gps_remove_copy

    for br, item in enumerate(data_srs_list, start=1):
        gps_dict_pattern = {}

        for count, pattern in enumerate(pattern_gps_list, start=1):
            ext_item = re.sub("Г(?![А-Яа-я])", "1'", item).replace("З", "3").replace("О", "0").replace("',", "'")
            gps_srs_list = re.findall(pattern.replace("\n", ""), re.sub(r'\s+', ' ', ext_item.replace("\n", "")))
            # print(ext_item)
            if gps_srs_list:
                gps_list = removeCopy(gps_srs_list)

                if len(gps_list) == 1 and len(gps_list[0]) == 2:
                    pattern = pattern_gps_list[1].replace('{5', '{2', 1)
                    print("\033[34m{}\033[0m".format(project_name), "\033[34m{}\033[0m".format('--->'), "\033[34m{}\033[0m".format(gps_list))
                    print("\033[34m{}\033[0m".format(pattern))
                    gps_srs_list = re.findall(pattern, re.sub(r'\s+', ' ', ext_item.replace("\n", "")))
                    gps_list = removeCopy(gps_srs_list)
                    print("\033[34m{}\033[0m".format(project_name), "\033[34m{}\033[0m".format('--->'), "\033[34m{}\033[0m".format(gps_list))

                gps_dict_pattern[count] = gps_list
        if gps_dict_pattern:
            gps_dict_br[br] = gps_dict_pattern
    # print(gps_dict_br)
    return gps_dict_br


def writeDB():
    # print(gps_list)
    data_list.extend((project_name, float(gps_list[0]), float(gps_list[1]), adress, region, date, ", ".join(vendor)))
    # print(data_list)
    cursor.execute(
        '''INSERT INTO cell_towers(number, lat, lng, adress, region, date, vendor) VALUES(?, ?, ?, ?, ?, ?, ?)''',
        data_list
    )
    data_list.clear()


try:
    with open(f"data/data_{region}/borders.txt") as file:
        borders = file.readlines()
        # print(borders)
except Exception as error:
    print(error)
    sys.exit('Не удалось прочитать файл границ')

latList = []
lngList = []
for item in borders:
    latList.append(float(item.split(',')[0].replace("\n", "").strip(' ')))
    lngList.append(float(item.split(',')[1].replace("\n", "").strip(' ')))

for root, dirs, files in os.walk(f"data/data_{region}"):  # берем список файлов из папки региона
    for filename in files:  # перебираем список
        index = filename.find('.')  # ищем разделитель расширения
        if filename[index:] == '.html':  # если расширение html
            list_files.append(filename[:index])  # то добавляем в список имя файла без расширения

    list_files.sort(reverse=True)  # сортируем список в обратном порядке, чтобы более новые файлы были в начале списка
print(len(list_files))

pattern_gps_list = make_pattern(region)

with open(f"patterns_vendor.txt", encoding='utf-8') as file:
    pattern_vendor_list = file.readlines()

# with open(f"data/data_{region}/patterns_gps.txt") as file:
#     pattern_gps_list = file.readlines()

with open(f"data/data_{region}/patterns_adress.txt", encoding='utf-8') as file:
    pattern_adress_list = file.readlines()

listPartsForReCompile = ['[Кк]оорд', '[ВвСс]\s*\.\s*[ДдШш]\s*\.', '[Мм]есто', 'WSG', '[Дд]олгот', '[Шш]ирот']
strForPartsForReCompile = ''
for part in listPartsForReCompile:
    strForPartsForReCompile = strForPartsForReCompile + '[^<]*' + part + '.+?(?:<br)[^<]*|'
strForPartsForReCompile = strForPartsForReCompile.rstrip('|')
# print(strForPartsForReCompile)

try:
    # conn = sqlite3.connect('data_cell_towers.db')
    conn = sqlite3.connect(f"data/data_{region}/data_cell_towers_{region}.db")
    cursor = conn.cursor()
    cursor.execute(
        '''CREATE TABLE IF NOT EXISTS cell_towers (
                                        number INTEGER,
                                        lat REAL,
                                        lng REAL,
                                        adress TEXT,
                                        region INTEGER NOT NULL,
                                        date  DATE TEXT,
                                        vendor TEXT);'''
    )
except sqlite3.Error as error:
    print(error)
    sys.exit("Ошибка при подключении к базе данных")

for project_name in list_files[0:]:  # перебираем список
    # project_name = '1828455'
    gps_srs_dict = {}
    vendor = []
    date = []
    adress = []
    try:
        # print(f"data/data_{region}/{project_name}.html")
        with open(f"data/data_{region}/{project_name}.html", encoding='utf-8') as file:  # открываем файл
            srs = file.read()  # читаем файл в srs
    except Exception as err:
        # print(err)
        with open(f"data/data_{region}/data_without_attachment/{project_name}.html", encoding='utf-8') as file:  # открываем файл
            srs = file.read()  # читаем файл в srs

    soup = BeautifulSoup(srs, "lxml")  # создаем объект soup и передаем ему srs и парсер lxml

    try:
        project_data = soup.find("noindex").find_next("table").find_next("td", text=re.compile(
            "([Нн]омер заключения)")).find_next("td").find(
            "b").text  # собираем информацию чтобы вытащить данные
        date = re.search(re.compile('[0-3]\d\.[0-1]\d\.20[0-2]\d'), project_data.replace("\n", "")).group()

    except Exception:
        date = "нет даты"
        print("Не удалось извлечь дату из номера заключения в файле", f"{project_name}.html")

    try:
        project_data = re.sub(r'\s+', ' ', soup.find("noindex").find_next("table").find_next("td", text=re.compile(
            "([Пп]роектная документация)")).find_next("td").find("b").text)  # собираем информацию, чтобы вытащить данные

    except Exception:
        print("Не удалось извлечь название проектной документации из файла", f"{project_name}.html")
        project_data = []
    # print(project_data.split('^'))
    adress = ()
    try:
        try:
            data_adress = re.sub(r'\s+', ' ', re.search(re.compile(pattern_adress_list[0].replace("\n", "")),
                                                        project_data.replace("\n", "")
                                                        .replace(re.search(re.compile(
                                                            pattern_adress_list[1].replace("\n", "")),
                                                            project_data.replace("\n",
                                                                                 "")).group(),
                                                                 "")).group())
            adress_list_srs = re.findall(re.compile(pattern_adress_list[2].replace("\n", "")), data_adress)

            if len(adress_list_srs) >= 2:
                adress = re.search(re.compile(pattern_adress_list[0].replace("\n", "")),
                                   data_adress.replace(adress_list_srs[0], "", 1)).group()
            else:
                adress = data_adress

        except Exception:
            data_adress = re.sub(r'\s+', ' ', re.search(re.compile(pattern_adress_list[0].replace("\n", "")),
                                                        project_data.replace("\n", "")).group())
            adress_list_srs = re.findall(re.compile(pattern_adress_list[2].replace("\n", "")), data_adress)

            if len(adress_list_srs) >= 2:
                adress = re.search(re.compile(pattern_adress_list[0].replace("\n", "")),
                                   data_adress.replace(adress_list_srs[0], "", 1)).group()
            else:
                adress = data_adress

    except Exception:
        adress = ("нет адреса")

    data_gps_list = searchCoordinates(pattern_gps_list, project_data.split('^'))
    if data_gps_list:
        gps_srs_dict['name_data'] = data_gps_list
    # print(gps_srs_dict)
    #     print("\033[34m{}\033[0m".format(project_name), "\033[34m{}\033[0m".format('==>'), "\033[34m{}\033[0m".format(data_gps_list))
    try:
        attachment_data = soup.find("noindex").find_next("table").find_next("td", text=re.compile(
            "([Пп]риложение)")).find_all_next("td")  # собираем информацию, чтобы вытащить данные

    except Exception:
        # print("нет приложения в файле", f"{project_name}.html")
        attachment_data = []
    # print(attachment_data)
    for tag_string in attachment_data:  # перебираем список собранной информации
        data_srs_list = str(tag_string).split("br")  # делим на части по тегу <br> и создаем список из полученных частей
        # print(data_srs_list)
        for item in data_srs_list:
            # print(item)
            if adress != "нет адреса":
                break
            else:
                try:
                    adress = re.sub(r'\s+', ' ', re.search(re.compile(pattern_adress_list[0].replace("\n", "")),
                                                           item.replace("\n", "")).group())
                except Exception:
                    adress = "нет адреса"

        if adress == "нет адреса":
            print("\033[34m{}\033[0m".format("Нет адреса в файле"), "\033[34m{}\033[0m".format(f"{project_name}.html"))

        try:
            if len(gps_srs_dict['name_data'][1][1]) >= 2:
                pass
            else:
                raise KeyError
        except KeyError:
            data_gps = re.findall(re.compile(strForPartsForReCompile), re.sub(r'\s+', ' ', str(tag_string).replace("\n", "")))
            data_gps_list = searchCoordinates(pattern_gps_list, data_gps)
            if data_gps_list:
                gps_srs_dict['attachment_data'] = data_gps_list

    if not gps_srs_dict:
        data_srs_list = re.sub(r'\s+', ' ', str(attachment_data).replace("\n", "")).split("br")
        data_gps_list = searchCoordinates(pattern_gps_list[0:3], data_srs_list[0:10])
        if data_gps_list:
            gps_srs_dict['all_attachment_data'] = data_gps_list
            # print(gps_srs_dict)

    if gps_srs_dict:
        gps_list = convertCoordinates(gps_srs_dict)
        if gps_list:
            if len(gps_list) == 2:
                gps_dict[project_name] = gps_list
                gps_list = checkCoordinates(gps_list)
                print(project_name, '---->', gps_list)
            else:
                gps_list = [0.0, 0.0]
        else:
            gps_list = [0.0, 0.0]
    else:
        gps_list = [0.0, 0.0]

    vendor = find_vendor(project_data.split('^') + attachment_data, region)
    # print(vendor)
    writeDB()
    # print(project_name, ":", gps_convert_list, ":", date, ":", vendor, ":", adress)

conn.commit()
conn.close()

print("Всего найдено координат в", len(gps_dict), "файлах")

if dist_files_gps_60_gps:
    print("Обнаружены координаты с минутами или секундами больше 60 в", len(dist_files_gps_60_gps), "файлах")

    with open(f"data/data_{region}/dist_files_gps_60_gps.json", "w") as file:
        json.dump(dist_files_gps_60_gps, file, indent=4, ensure_ascii=False)

    # for keys, values in dist_files_gps_60_gps.items():
    #     print(keys, values)

if dist_files_gps_with_garbage:
    print("Больше двух координат обнаружено в", len(dist_files_gps_with_garbage), "файлах")

    with open(f"data/data_{region}/dist_files_gps_with_garbage.json", "w") as file:
        json.dump(dist_files_gps_with_garbage, file, indent=4, ensure_ascii=False)

    # for keys, values in dist_files_gps_with_garbage.items():
    #     print(keys, values)

if dist_files_only_one_gps:
    print("Только одна координата обнаружена в", len(dist_files_only_one_gps), "файлах")

    with open(f"data/data_{region}/dist_files_only_one_gps.json", "w") as file:
        json.dump(dist_files_only_one_gps, file, indent=4, ensure_ascii=False)
    # print(list_files)
    # for keys, values in dist_files_only_one_gps.items():
    #     print(keys, values)

if dist_files_only_one_gps_in_name_project:
    print("Только с одной координатой в названии проекта", len(dist_files_only_one_gps_in_name_project), "файла")

    with open(f"data/data_{region}/dist_files_only_one_gps_in_name_project.json", "w") as file:
        json.dump(dist_files_only_one_gps_in_name_project, file, indent=4, ensure_ascii=False)
    # print(list_files)
    # for keys, values in dist_files_only_one_gps_in_name_project.items():
    #     print(keys, values)

