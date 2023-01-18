import sqlite3
import sys
import json
region = '0'


def statistic_for_4pda():
    print(f'[spoiler=[b][i][u][color=red]{region} {region_dict[region]}[/color][/u][/i][/b]]')
    print('*' * 120)
    print('[b]', region, region_dict[region], '[/b]')
    cursor.execute(f'SELECT number FROM cell_towers WHERE region = {region}')
    print('Всего найдено проектов БС в реестре fp.crc.ru: [b][color=blue]', len(cursor.fetchall()), 'шт.[/color][/b]')
    cursor.execute(
        'SELECT number, lat, lng, date, vendor FROM cell_towers WHERE lat !=? and lng !=? and region = ?', (0, 0, region)
    )
    print('проектов БС с координатами (отображаемые на карте): [b][color=green]', len(cursor.fetchall()), 'шт.[/color][/b]')
    print('*' * 120, '[/spoiler]')
    change_region()


def statistic_for_site():
    print('<p>', '*' * 120, '</p>')
    print('<p>', region, region_dict[region], '</p>')
    cursor.execute(f'SELECT number FROM cell_towers WHERE region = {region}')
    print('<p>Всего найдено проектов БС в реестре fp.crc.ru:', len(cursor.fetchall()), 'шт.</p>')
    cursor.execute(
        'SELECT number, lat, lng, date, vendor FROM cell_towers WHERE lat !=? and lng !=? and region = ?', (0, 0, region)
    )
    print('<p>проектов БС с координатами (отображаемые на карте):', len(cursor.fetchall()), 'шт.</p>')
    change_region()


def change_region():
    global region
    region_number = int(region) + 1
    if region_number > 99:
        conn.commit()
        conn.close()
        # region = '0'
        # time.sleep(604800 / 7)
        # change_region()
        exit()
    elif len(str(region_number)) < 2:
        region = f"0{region_number}"
    else:
        region = f"{region_number}"

    # statistic_for_site()
    statistic_for_4pda()


if __name__ == "__main__":
    try:
        conn = sqlite3.connect('data_cell_towers.db')
        # conn = sqlite3.connect(f"data/data_{region}/data_cell_towers_{region}.db")
        cursor = conn.cursor()
        # change_region()

    except sqlite3.Error as error:
        print(error)
        sys.exit("Ошибка при подключении к базе данных")

    with open(f"region_dict.json", 'r', encoding='utf-8') as f:
        region_dict = json.load(f)

    change_region()