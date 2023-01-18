# импортируем библиотеки
import re
import os
import requests
import json
from bs4 import BeautifulSoup
import math
from datetime import date
import random
import time

headers = {"Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
"User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.45 Safari/537.36"
} #  заголовки для запроса
links_dict = {}
total = 1
region = '81'
year = str(date.today().year)[2:]
wordsForFind_list = [
    "text_prodnm=%F1%EE%F2%EE%E2%EE%E9",
    "text_pril=%F1%EE%F2%EE%E2%EE%E9",
    "text_prodnm=lte",
    "text_pril=lte"
                ]


# Поиск ссылок и формирование списка ссылок:
def get_url(wordForFind,  total):
    global links_dict
    # print(len(links_dict))
    url = f'http://fp.crc.ru/doc/?pg={total}&oper=s&rpp=1000&type=max&{wordForFind}&pril=on&text_n_state={region}&text_n_year={year}&use=1'
    if total == 1:
        print(url)
    while True:
        try:
            req = requests.get(url, headers=headers, timeout=20)  # отправляем запрос
            break
        except Exception:
            continue
    soup = BeautifulSoup(req.text, "lxml")  # создаем объект soup и передаем ему srs и парсер lxml
    if soup.find("noindex").find_next("br").find_previous_sibling():
        total_doc = soup.find("noindex").find_next("b").text  # находим количество документов
        total_pages = math.ceil(int(total_doc) / 1000)  # вычисляем количество страниц
        all_blocks = str(soup.find("noindex")).split("colspan=")
        for i, item in enumerate(all_blocks[1:]):
            bloks_soup = BeautifulSoup(item, "lxml")
            try:
                blank_number = bloks_soup.find("td", text=re.compile("([Тт]ипографский номер бланка)")).find_next("td").text.replace("\n", "").replace(' ', '')
            except Exception:
                blank_number = bloks_soup.find("td", text=re.compile("([Нн]омер заключения и дата)")).find_next("td").text.replace("\n", "").replace(' ', '')
            # print(blank_number)
            if re.search(re.compile('[^\d]'), blank_number.replace("\n", "")):
                blank_number = bloks_soup.find("td", text=re.compile("([Нн]омер заключения и дата)")).find_next("td").text.replace("\n", "").replace(' ', '')
                print(blank_number)
            if os.path.exists(f"data/data_{region}/{blank_number}.html"):
                # print("Данные ранее уже были записаны в файл ", blank_number, ".html", sep="")
                continue
            elif os.path.exists(f"data/data_{region}/data_without_attachment/{blank_number}.html"):
                # print("Данные ранее уже были записаны в файл ", blank_number, ".html в папке data_without_attachment", sep="")
                continue
            else:
                try:
                    link = "http://fp.crc.ru/doc/" + bloks_soup.find("a", text=re.compile("полный текст приложения")).get("href")
                    links_dict[blank_number] = link
                except Exception:
                    links_dict[blank_number] = None
        print("Всего страниц:", total_pages, ", всего документов:", total_doc, ", обработано страниц:", total, sep="")
        if total < total_pages:
            # next_page_link = soup.find("noindex").find_next("a", text=re.compile("([Сс]ледующая)"))  # находим ссылку на следующую страницу
            # next_page_url = "http://fp.crc.ru/doc/" + next_page_link.get("href")  # формируем url следующей страницы
            total += 1
            get_url(wordForFind, total)  # вызываем функцию загрузки следующей страницы результатов поиска
        else:
            print("Сбор ссылок закончен")
            print("Всего найдено новых записей реестра", len(links_dict), "в", total_doc, "документах")
            folder_name = f"data/data_{region}"
            if os.path.exists(folder_name):
                print("Папка региона существует!")
            else:
                os.mkdir(folder_name)
                print("Создана папка", folder_name)
        return
            # get_gps(total_doc)
    else:
        links_dict.clear()
        return


# Пробегаемся по списку ссылок и сохраняем данные по каждой ссылке в файл:
def scrap_data():
    global links_dict
    # print('def scrap_data')
    count = 0  # переменная для счетчика документов
    blank_numbers_with_attachment = []
    for key, value in links_dict.items():  # перебираем список url документов
        if value:
            while True:
                try:
                    req = requests.get(value, headers=headers, timeout=10)  # отправляем запрос
                    break
                except Exception:
                    continue
            soup = BeautifulSoup(req.text, "lxml")  # создаем объект soup и передаем ему srs и парсер lxml
            # print(req.text)
            try:
                project_name = soup.find("noindex").find_next("td", text=re.compile("([Тт]ипографский номер бланка)")).find_next("td").text.replace("\n", "").replace(' ', '')
            except Exception:
                project_name = soup.find("noindex").find_next("td", text=re.compile("([Нн]омер заключения и дата)")).find_next("td").text.replace("\n", "").replace(' ', '')
                # project_name = soup.find("noindex").find_next("td", text=re.compile("([Тт]ипографский номер бланка)")).find_next("td").text
            if re.search(re.compile('[^\d]'), project_name.replace("\n", "").replace(' ', '')):
                project_name = soup.find("noindex").find_next("td", text=re.compile("([Нн]омер заключения и дата)")).find_next("td").text.replace("\n", "").replace(' ', '')
            if os.path.exists(f"data/data_{region}/{project_name}.html"):
                print("Данные ранее уже были записаны в файл ", project_name, ".html", sep="")
            else:
                with open(f"data/data_{region}/{project_name}.html", "w", encoding='utf-8') as file:  # открываем файл на запись
                    file.write(req.text)  # и записываем полученный код страницы в файл
                print("Сохранен документ в файл: ", project_name, ".html", ", всего сохранено ", count + 1, ", осталось: ", len(links_dict) - (count + 1), sep="")
            count += 1
            blank_numbers_with_attachment.append(project_name)
        else:
            print("Нет приложения в файле ", key, ".html", sep="")
    for blank_number in blank_numbers_with_attachment:
        del links_dict[blank_number]
    return


def scrap_data_without_attachment():
    global links_dict
    # print('def scrap_data_without_attachment')
    folder_name = f"data/data_{region}/data_without_attachment"
    if os.path.exists(folder_name):
        print("Папка для документов без приложений уже существует!")
    else:
        os.mkdir(folder_name)
        print("Создана папка", folder_name)
    index = 0
    for key, value in links_dict.items():
        if re.search(re.compile('[^\d]'), key):
            continue
        if os.path.exists(f"data/data_{region}/data_without_attachment/{key}.html"):
            print("Данные ранее уже были записаны в файл", key, ".html")
        else:
            url = f"http://fp.crc.ru/doc/?oper=s&type=max&text_prodnm=&text_ff_firm=&text_pril=&pril=on&text_n_state=&text_n_org=&text_n_otdel=&text_n_okp=&text_n_currnumb=&text_n_char=&text_n_year=&text_serialnumb={key}&use=0"
            # time.sleep(random.randrange(1, 2))  # пауза
            while True:
                try:
                    req = requests.get(url, headers=headers, timeout=10)  # отправляем запрос
                    break
                except Exception:
                    continue
            with open(f"data/data_{region}/data_without_attachment/{key}.html", "w", encoding='utf-8') as file:  # открываем файл на запись
                file.write(req.text)  # и записываем полученный код страницы в файл
            print("Сохранен документ в файл: ", key, ".html", ", всего сохранено ", index + 1, ", осталось: ",
                  len(links_dict) - (index + 1), sep="")
        index += 1
    links_dict.clear()
    return ("Все данные по ссылкам записаны в файлы")


def main():
    for i, wordForFind in enumerate(wordsForFind_list):
        # find_url = base_url + f"&text_n_state={region}&text_n_org=&text_n_otdel=&text_n_okp=&text_n_currnumb=&text_n_char=&text_n_year={year}&text_serialnumb=&use=1"
        # print(find_url)
        print('Поисковый запрос №', i+1, ':', sep="")
        get_url(wordForFind, total)
        if links_dict:
            with open(f"data/data_{region}/{i}all_urls_list.json", "w") as file:
                json.dump(links_dict, file, indent=4, ensure_ascii=False)
            print("Список ссылок на документы и номера типографских бланков сохранены в",
                  f"data/data_{region}/{i}all_urls_list.json")
            scrap_data()
            if links_dict:
                with open(f"data/data_{region}/{i}blank_numbers_without_attachment_list.json", "w") as file:
                    json.dump(links_dict, file, indent=4, ensure_ascii=False)
                print("Список номеров типографских бланков без приложений сохранен в",
                          f"data/data_{region}/{i}blank_numbers_without_attachment_list.json")
                print(scrap_data_without_attachment())
            else:
                print("Документов без приложений нет. Все данные по ссылкам записаны в файлы")
        else:
            print('Новых документов не найдено!')
    change_region()


def change_region():
    global region
    region_number = int(region) + 1
    if region_number > 82:
        # region = '0'
        # time.sleep(604800 / 7)
        # change_region()
        exit()
    elif len(str(region_number)) < 2:
        region = f"0{region_number}"
    else:
        region = f"{region_number}"
    print('*'*120)
    print("Регион:", region)
    main()


if __name__ == "__main__":
    change_region()
