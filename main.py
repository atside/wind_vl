import requests
import json
import filework
import settings
import datetime
import time
from threading import Thread
import telebot
from telebot import types
from datetime import timedelta, timezone
# import logging
# logging.basicConfig(
#     level=logging.DEBUG,
#     filename='mylog.log',
#     format="%(asctime)s - %(module)s - %(levelname)s - %(funcName)s: %(lineno)d - %(message)s",
#     datefmt='%H:%M:%S')


offset = timezone(timedelta(hours=10))


dt_format = '%y-%m-%d %H:%M:%S'
ships_count = 5

areas_list = {
    1: ['Токаревский маяк', 'https://www.marinetraffic.com/getData/get_data_json_4/z:14/X:7095/Y:3007/station:0'],
    2: ['Патрокл', 'https://www.marinetraffic.com/getData/get_data_json_4/z:14/X:7099/Y:3007/station:0'],
    3: ['Славянка', 'https://www.marinetraffic.com/getData/get_data_json_4/z:12/X:1771/Y:753/station:0']}

all_areas_data = filework.read_data_file('shipsdata.txt')

# def show_users_stats():
#     st = filework.read_data_file('users')
#     res = 'user: requests, last_request (UTC)\n'
#     for key, value in st.items():
#         res += f'{key}: {value[0]}, {datetime.datetime.utcfromtimestamp(value[1])}\n'
#     return res

# def check_user(message, filename):
#
#     users_bd = filework.read_data_file(filename)
#     user = message.from_user.username
#     if user not in users_bd:
#         users_bd[user] = [1, message.date]
#     else:
#         users_bd[user][0] += 1
#         users_bd[user][1] = message.date
#     filework.save_data_file(users_bd, filename)

def wind_direction(deg):
    if type(deg) is not int:
        return 'что-то пошло не так'
    if (340 < deg <= 360) or (0 <= deg < 20):
        return 'северный'
    if 20 <= deg <= 70:
        return 'северо-восточный'
    if 71 <= deg <= 110:
        return 'восточный'
    if 111 <= deg <= 160:
        return 'юго-восточный'
    if 161 <= deg <= 200:
        return 'южный'
    if 201 <= deg <= 250:
        return 'юго-западный'
    if 251 <= deg <= 290:
        return 'западный'
    if 291 <= deg <= 340:
        return 'северо-западный'

    def knots_to_ms(knots):
        return knots * 0.514

def extract_data_str(num):
    wind_data = filework.read_data_file('wind_data.txt')[num]
    # print(wind_data)
    res = f'Данные по району {wind_data[-1]}\n(на {wind_data[-2]})\n'
    try:
        for data in wind_data[:-2]:
            res += f'{data[0]}:\n'
            res += f'{data[1]} гр. ({wind_direction(data[1])}), {str(round(data[2] * 0.514, 1))} м/с\n'
            res += '\n'
    except Exception:
        pass
    return res

def get_ships_data(sleeptime):
    headers = {
        "accept": "application/json",
        "accept-encoding": "gzip, deflate",
        "user-agent": "Mozilla/5.0",
        "x-requested-with": "XMLHttpRequest"
    }
    while True:
        for area in areas_list.keys():
            url = areas_list[area][1]
            try:
                # print(f'ищем район {areas_list[area][0]} по адресу {areas_list[area][1]}')
                response = requests.get(url=url, headers=headers)
                res1 = response.text
                # print(res1)
                b = json.loads(res1)
                ships_in_area = []
                # print(b["data"]["rows"][0]["SHIP_ID"])
                for x in range(len(b["data"]["rows"])):
                    ships_in_area.append(b["data"]["rows"][x]["SHIP_ID"])
                current_time_str = datetime.datetime.strftime(datetime.datetime.now(offset), dt_format)
                ships_in_area.append(current_time_str) # добавляем метку времени
                # print('получено: ', ships_in_area[-ships_count - 1:])
                #filework.save_data_file(ships_in_area[:5], 'shipsdata.txt', areas[area_num][0])
                all_areas_data[area] = ships_in_area[-ships_count - 1:]
            except Exception:
                pass  # print('не удалось загрузить данные по району')
            time.sleep(10)
        filework.save_data_file(all_areas_data, 'shipsdata.txt') # сохраняем всё в файл после цикла
        try:
            wind_data = filework.read_data_file('wind_data.txt')
            for area_num in areas_list: # сохраняем данные по ветру
                wind_data[area_num] = get_wind_data(area_num)
                time.sleep(10)
            filework.save_data_file(wind_data, 'wind_data.txt')
        except Exception:
            pass  # print('ошибка обновления данных по ветру')

        time.sleep(sleeptime)

def get_wind_data(area):
    headers = {
        "accept": "application/json",
        "accept-encoding": "gzip, deflate",
        "user-agent": "Mozilla/5.0",
        "x-requested-with": "XMLHttpRequest"
    }
    res = []
    ships_ids = filework.read_data_file('shipsdata.txt')[area]
    for ship in ships_ids[:-1]:
        try:
            url1 = f'https://www.marinetraffic.com/en/vesselDetails/vesselInfo/shipid:{ship}'
            url2 = f'https://www.marinetraffic.com/vesselDetails/latestPosition/shipid:{ship}'
            response_name = requests.get(url1, headers=headers)
            response_data = requests.get(url2, headers=headers)
            js_name = json.loads(response_name.text)
            js_data = json.loads(response_data.text)
            wind_angle = js_data["windAngle"]
            res.append([js_name['name'], wind_angle, js_data["windSpeed"]])
        except Exception:
            pass
    res.append(ships_ids[-1])
    res.append(areas_list[area][0])
    return res

def main():
    bot = telebot.TeleBot(settings.API_KEY)
    @bot.message_handler(commands=['start', 'help'])
    def start(message):
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        btn1 = types.KeyboardButton('Токаревский маяк')
        btn2 = types.KeyboardButton('Патрокл')
        btn3 = types.KeyboardButton('Славянка')
        markup.add(btn1, btn2, btn3)
        title = f'Выберите район:'  #\n{areas_for_user_input()}'
        bot.send_message(message.chat.id, title, reply_markup=markup)
    @bot.message_handler()
    def get_user_text(message):
        if message.text == 'Токаревский маяк':
            bot.send_message(message.chat.id, extract_data_str(1))
        elif message.text == 'Патрокл':
            bot.send_message(message.chat.id, extract_data_str(2))
        elif message.text == 'Славянка':
            bot.send_message(message.chat.id, extract_data_str(3))
        elif message.text.lower().strip() == 'show stats 717':
            pass
            # bot.send_message(message.chat.id, show_users_stats())
        else:
            bot.send_message(message.chat.id, 'Не понимаю команду((')

    t1 = Thread(target=get_ships_data, args=(60,))
    t1.start()
    while True:
        try:
            bot.polling(none_stop=True)
        except Exception as e:
            print(e)
            time.sleep(4)
if __name__ == '__main__':
    main()
