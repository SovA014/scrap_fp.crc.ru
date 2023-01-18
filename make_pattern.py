import sys

region = '63'
region_dict = {}


def make_pattern(region):
    pattern_gps_list = []

    def make_DD(minGPS, maxGPS):
        # print(minGPS, maxGPS)
        dd_list = []
        if int(minGPS[0]) == int(maxGPS[0]):
            dd = f'{minGPS[0]}[{minGPS[1]}-{maxGPS[1]}]'
            dd_list.append(dd)
        elif int(maxGPS) - int(minGPS) >= 9:
            if int(minGPS[1]) != 0 and int(minGPS[1]) != 9:
                dd = f'{minGPS[0]}[{minGPS[1]}-9]'
                dd_list.append(dd)
            elif int(minGPS[1]) == 9:
                dd = f'{minGPS[0]}{minGPS[1]}'
                dd_list.append(dd)
            else:
                dd = f'{minGPS[0]}\d'
                dd_list.append(dd)
            if int(maxGPS[1]) != 0 and int(maxGPS[1]) != 9:
                dd = f'{maxGPS[0]}[0-{maxGPS[1]}]'
                dd_list.append(dd)
            elif int(maxGPS[1]) == 9:
                dd = f'{maxGPS[0]}\d'
                dd_list.append(dd)
            else:
                dd = f'{maxGPS[0]}{maxGPS[1]}'
                dd_list.append(dd)
            if int(minGPS[0]) + 1 < int(maxGPS[0]) - 1:
                dd = f'[{int(minGPS[0]) + 1}-{int(maxGPS[0]) - 1}]\d'
                dd_list.append(dd)
            elif int(minGPS[0]) + 1 == int(maxGPS[0]) - 1:
                dd = f'{int(minGPS[0]) + 1}\d'
                dd_list.append(dd)
        elif maxGPS[1] == '0' and minGPS[1] == '9':
            dd = f'{minGPS[0]}{minGPS[1]}'
            dd_list.append(dd)
            dd = f'{maxGPS[0]}{maxGPS[1]}'
            dd_list.append(dd)
        elif maxGPS[1] == '0':
            dd = f'{maxGPS[0]}{maxGPS[1]}'
            dd_list.append(dd)
            dd = f'{minGPS[0]}[{minGPS[1]}-9]'
            dd_list.append(dd)
        elif minGPS[1] == '9':
            dd = f'{minGPS[0]}{minGPS[1]}'
            dd_list.append(dd)
            dd = f'{maxGPS[0]}[0-{maxGPS[1]}]'
            dd_list.append(dd)
        else:
            dd = f'{minGPS[0]}[{minGPS[1]}-9]'
            dd_list.append(dd)
            dd = f'{maxGPS[0]}[0-{maxGPS[1]}]'
            dd_list.append(dd)
        # print(dd_list)
        return dd_list

    try:
        with open(f"patterns_gps.txt", encoding='utf-8') as file:
            pattern_list = file.readlines()
    except Exception as error:
        print(error)
        sys.exit('Не удалось прочитать файл паттернов')

    try:
        with open(f"data/data_{region}/borders.txt", encoding='utf-8') as file:
            borders = file.readlines()
            # print(borders)
    except Exception as error:
        print(error)
        sys.exit('Не удалось прочитать файл границ')

    latList = []
    lngList = []
    for item in borders:
        latList.append(int(item.split(',')[0].split('.')[0]))
        lngList.append(int(item.split(',')[1].split('.')[0]))
    print(min(latList), max(latList))
    print(min(lngList), max(lngList), '\n')
    dd = ''
    if min(lngList) > 99 and max(lngList) < 179:
        dd_lat_list = make_DD(str(min(latList)), str(max(latList)))
        dd_lng_list = make_DD(str(min(lngList))[1:], str(max(lngList))[1:])
        for s in dd_lat_list:
            dd = dd + s + '|'
        for s in dd_lng_list:
            dd = dd + '1' + s + '|'
        dd = dd.rstrip('|')
    elif max(lngList) == 179:
        dd_lat_list = make_DD(str(min(latList)), str(max(latList)))
        dd_lng_list = make_DD(str(min(lngList))[1:], str(max(lngList))[1:])
        for s in dd_lat_list:
            dd = dd + s + '|'
        for s in dd_lng_list:
            dd = dd + '-?1' + s + '|'
        dd = dd.rstrip('|')
    elif min(lngList) < 99 < max(lngList):
        # print(make_DD(str(min(latList)), str(max(latList))))
        dd_lat_list = make_DD(str(min(latList)), str(max(latList)))
        dd_lng_list = make_DD(str(min(lngList)), "99")
        dd_lng_list_over_100 = make_DD("00", str(max(lngList))[1:])
        for s in dd_lat_list:
            dd = dd + s + '|'
        for s in dd_lng_list:
            dd = dd + s + '|'
        for s in dd_lng_list_over_100:
            dd = dd + '1' + s + '|'
        dd = dd.rstrip('|')
    else:
        # print(make_DD(str(min(latList)), str(max(latList))))
        dd_lat_list = make_DD(str(min(latList)), str(max(latList)))
        dd_lng_list = make_DD(str(min(lngList)), str(max(lngList)))
        for s in dd_lat_list:
            dd = dd + s + '|'
        for s in dd_lng_list:
            dd = dd + s + '|'
        dd = dd.rstrip('|')
    print(dd)
    for item in pattern_list:
        pattern_gps_list.append(f'{item.split("dd")[0]}{dd}{item.split("dd")[1]}'.replace("\n", ""))
    # print(pattern_gps_list)
    return pattern_gps_list

if __name__ == "__main__":
    make_pattern(region)
