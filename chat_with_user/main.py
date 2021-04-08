from random import randrange
import config
import vk_api
from vk_api.longpoll import VkLongPoll, VkEventType
from database.work_with_db import *
from search_users.get_info_about_user import VkUser
from search_users.get_profiles import Finder
from time import sleep

vk_bot = vk_api.VkApi(token=config.bot_token)
# Работа с сообщениями (тип-класс)
longpoll = VkLongPoll(vk_bot)


def write_msg_bot(user_id, message, attach=None):
    vk_bot.method('messages.send', {'user_id': user_id,
                                    'message': message,
                                    'random_id': randrange(10 ** 7),
                                    'attachment': attach})


def ask_for_info(person_id, lacking_params):
    params = {'sex': 'пол', 'bdate': 'год рождения', 'relation': 'семейное положение'}
    write_msg_bot(person_id, "У вас введены не все необходимые параметры")
    for param in lacking_params:
        changed_one_par = params.get(param)
        write_msg_bot(person_id, f"Введите {changed_one_par}")
    write_msg_bot(person_id, "Напишете какой параметр хотите указать и его значение, например "
                             "напечатайте команду (без пробела после знака равно): пол=1. "
                             "При вводе пола, команда пол=1 значит, что ваш пол женский, пол=2 значит ваш пол мужской."
                             "Для ввода семейного положения введите команду: семейное положение=1. "
                             "Где 1 — не женат/не замужем; 5 — всё сложно; 6 — в активном поиске.")


def ask_for_city(bot_user_id):
    write_msg_bot(bot_user_id, "Укажите свой город в настройках Вконтакте https://vk.com/edit?act=contacts."
                               "(В разделе настроек Контанты сначала укажите Страну, а потом и город) "
                               "После этого снова напишите боту: поиск")


if __name__ == '__main__':
    dict_users_and_search_number = {}
    command_words = 'город, пол, год рождения, семейное положение'
    list_of_users = []
    list_of_searched_users = []
    for event in longpoll.listen():
        # Если пришло новое сообщение
        if event.type == VkEventType.MESSAGE_NEW:

            # Если оно имеет метку для меня(то есть бота)
            if event.to_me:
                # Получаем id пользователя, написавшего боту
                talking_user_id = event.user_id
                # Сообщение от пользователя
                request = event.text
                # Приваиваем переменной мусор, чтобы она была определена и
                # разбиение строки работало лишь в нужный момент
                parameter_name = '000000'
                if '=' in request:
                    parameter_sense = request.split('=')[1]
                    parameter_name = request.split('=')[0]
                if request == "привет":
                    write_msg_bot(event.user_id, f"Хай, {event.user_id}")
                elif request == "пока":
                    write_msg_bot(event.user_id, "Пока((")
                elif request == "поиск" or request == "Поиск":
                    # Если вызывается впервые, то запрашиваем инфу о пользователе, иначе работаем с изменённой
                    if event.user_id not in list_of_users:
                        list_of_users.append(event.user_id)
                        # Добавляем id пользователя в таблицу
                        add_user(event.user_id)
                        vk_user = VkUser(config.vk_user_token, '5.130', event.user_id)
                        info_about_user = vk_user.get_main_info_about_user()
                        output_identify_par = vk_user.identify_search_parametres(info_about_user)
                        params_for_search = output_identify_par[0]
                        missing_params = output_identify_par[1]
                    # Если список недостающих параметров не пуст, то ..., иначе ...
                    if missing_params:
                        # Смотрим, есть ли город в недостающих параметрах
                        if 'city' in missing_params:
                            # Делаем запрос на проверку города (может юзер уже внёс его в настроки)
                            city_id = vk_user.get_user_city()
                            # Если город прописан в настройках, то удаляем город из недостающих параметров
                            if city_id:
                                missing_params.remove('city')
                                params_for_search['city'] = city_id
                                # После удаления нужно проверить наличие остальных параметров
                                if missing_params:
                                    ask_for_info(event.user_id, missing_params)
                                else:
                                    write_msg_bot(event.user_id, "Все параметры приняты, введите, "
                                                                 "пожалуста, ещё раз команду: поиск")
                            # Иначе снова просим вписать
                            else:
                                ask_for_city(event.user_id)
                        else:
                            ask_for_info(event.user_id, missing_params)
                    elif not missing_params:
                        if event.user_id not in list_of_searched_users:
                            list_of_searched_users.append(event.user_id)
                            dict_users_and_search_number[event.user_id] = 0
                        vk_search = Finder(config.vk_user_token, '5.130')
                        result_of_search_users = vk_search.search_users(params_for_search,
                                                                        indent=dict_users_and_search_number.get(event.user_id))
                        founded_persons_id = result_of_search_users[0]
                        count_founded_pers = result_of_search_users[1]
                        # Находим незакрытые аккаунты
                        free_ids = []
                        for count in range(0, 20, 2):
                            if not founded_persons_id[count + 1]:
                                free_ids.append(founded_persons_id[count])
                        # Получаем ссылки и фотки первых 10 человек (если у всех открыты профили, иначе выдаём меньше)
                        add_founded_pers(event.user_id, free_ids)
                        for numb in range(0, len(free_ids)):
                            photos_garbage = vk_search.get_photos(free_ids[numb])
                            changed_photos = vk_search.change_vk_response(photos_garbage)
                            person_id_vk = changed_photos[0]
                            link = 'https://vk.com/id' + str(person_id_vk)
                            changed_photos.pop(0)
                            str_photos_link = ''
                            for one_elem in changed_photos:
                                photo_link = 'photo' + str(person_id_vk) + '_' + str(one_elem)
                                if str_photos_link:
                                    str_photos_link += ',' + photo_link
                                else:
                                    str_photos_link += photo_link
                            write_msg_bot(event.user_id, link, attach=str_photos_link)
                            sleep(0.5)
                        dict_users_and_search_number[event.user_id] += 10
                elif parameter_name in command_words:
                    parameters = {'пол': 'sex', 'год рождения': 'bdate', 'семейное положение': 'relation'}
                    missing_params.remove(parameters.get(parameter_name))
                    params_for_search[parameters.get(parameter_name)] = parameter_sense
                    write_msg_bot(event.user_id, "После ввода всех параметров, снова введите команду поиск")
                else:
                    write_msg_bot(event.user_id, "Не поняла вашего ответа...")