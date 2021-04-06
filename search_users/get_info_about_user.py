import requests
import vk_api
import config
from pprint import pprint
import re


class VkUser:
    """Класс для работы с пользователем бота"""
    url = 'https://api.vk.com/method/'

    def __init__(self, token_vk, version, user_id):
        self.token = token_vk
        self.version = version
        self.user_id = user_id
        self.params = {
            'access_token': self.token,
            'v': self.version,
            'user_id': self.user_id,
            'fields': 'domain' # Возвращает короткий адрес страницы или id+user_id
        }
        self.owner_id = requests.get(self.url + 'users.get', self.params).json()['response'][0]['id']
        # self.owner_link = 'https://vk.com/' + requests.get(self.url + 'users.get', self.params).json()['response'][0]['domain']

    def get_main_info_about_user(self):
        """Получаем о юзере инфу: пол, город, дата рождения, семейное положение
        bdate Возвращается в формате D.M.YYYY или D.M (если год рождения скрыт).
            Если дата рождения скрыта целиком, поле отсутствует в ответе.
        sex 1 — женский; 2 — мужской; 0 — пол не указан.
        city возращает id и title. Если город не указан, то поле отсутствует в ответе.
        relation 1 — не женат/не замужем;
                2 — есть друг/есть подруга;
                3 — помолвлен/помолвлена;
                4 — женат/замужем;
                5 — всё сложно;
                6 — в активном поиске;
                7 — влюблён/влюблена;
                8 — в гражданском браке;
                0 — не указано.
        """
        user_url = self.url + 'users.get'
        user_params = {
            'user_ids': self.owner_id,
            'fields': ['bdate, sex, city, relation']
        }
        response_info_user_vk = requests.get(user_url, params={**self.params, **user_params})
        # pprint(response_info_user_vk.json())
        return response_info_user_vk.json()

    def identify_search_parametres(self, info):
        """Возвращает кортеж. 1 элемент - словарь параметров для поиска, 2 элемент - список недостоющих параметров"""
        list_first_iter = []
        list_of_missing_filters = []
        dict_params_for_search = {}
        # print(info)
        filters = ['bdate', 'city', 'relation']
        # Проверяем есть ли эти поля и добавляем их в список
        for filt, meaning in info['response'][0].items():
            if filt in filters:
                list_first_iter.append(filt)
            # Добавляем пол в параметры поиска или в отсутсвующие элементы
            if filt == 'sex':
                if meaning == 0:
                    list_of_missing_filters.append(filt)
                if meaning == 1:
                    dict_params_for_search[filt] = '2'
                if meaning == 2:
                    dict_params_for_search[filt] = '1'
            # Добавляем год в параметры поиска, если он есть
            elif filt == 'bdate':
                # оставляем регуляркой только год
                year = (re.findall('\d{4}', meaning))
                # Проверка на наличие года в данных
                if year:
                    dict_params_for_search[filt] = year[0]
                else:
                    list_of_missing_filters.append(filt)
            # Добавляем id города (тип строка) в параметры поиска, если он есть
            elif filt == 'city':
                dict_params_for_search[filt] = str(meaning['id'])
            # Добавляем семейное положение (тип строка) в параметры поиска, если он есть
            elif filt == 'relation':
                if meaning == 0:
                    list_of_missing_filters.append(filt)
                else:
                    dict_params_for_search[filt] = str(meaning)
        # print(list_first_iter)
        # print(dict_params_for_search) # Список параметров для поиска
        # Находим полностью отсутствующие поля
        for one_elem in filters:
            if one_elem not in list_first_iter:
                list_of_missing_filters.append(one_elem) # Список недоставющих элементов
        # print(list_of_missing_filters)
        return dict_params_for_search, list_of_missing_filters


if __name__ == '__main__':
    vk_client_1 = VkUser(config.vk_user_token, '5.130', '79932267')
    info_about_user = vk_client_1.get_main_info_about_user()
    print(vk_client_1.identify_search_parametres(info_about_user)[0])
    print(vk_client_1.identify_search_parametres(info_about_user)[1])

    params_for_search = vk_client_1.identify_search_parametres(info_about_user)[0]
    missing_params = vk_client_1.identify_search_parametres(info_about_user)[1]
    # Если список недостающих параметров не пуст, то ..., иначе ...
    if missing_params:
        print('aaaa')
    else:
        print('bbbb')




# def write_msg(user_id, message):
#     vk_bot.method('messages.send', {'user_id': user_id, 'message': message, 'random_id': randrange(10 ** 7), })

# vk_session = vk_api.VkApi('phone', 'password')
# vk_session.auth()
# vk = vk_session.get_api()
# def get_photos():
#     """Работающий метод получения фоток через vk_api"""
#     pprint(vk_session.method('photos.get', {'owner_id': '79932267', 'album_id': 'profile'}))

