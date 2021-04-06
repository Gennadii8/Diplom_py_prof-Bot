import requests
import config
from pprint import pprint
from time import sleep
from search_users.get_info_about_user import VkUser


class Finder:
    """Класс для поиск людей и их фоток"""
    url = 'https://api.vk.com/method/'

    def __init__(self, token_vk, version):
        self.token = token_vk
        self.version = version
        self.params = {
            'access_token': self.token,
            'v': self.version,
            'fields': 'domain'  # Возвращает короткий адрес страницы или id+user_id
        }

    def search_users(self, searching_par, indent=0):
        """Ищет подходящих людей с незакрытыми аккаунтами и возращает кортеж,
        в котором [0] - это список id подошедших людей из первой тысячи (возвращается обычный список, в котором нулевой
        элемент это id найденного человека, а первый элемент это параметр is_closed в булевом формате, и так далее),
        а [1] - это общее количество найденных людей (включая закрытые аккаунты)"""
        list_of_free_persons = []
        dict_of_persons = {}
        list_of_all_persons = []  # Сначала идёт id, потом bool закрыт ли профиль True - закрыт
        user_search_url = self.url + 'users.search'
        user_search_params = {
            'sort': '0',  # Сортировка 0 - по популярности, 1 - по дате регистрации
            'city': searching_par.get('city'),
            'sex': searching_par.get('sex'),
            'status': searching_par.get('relation'),
            'birth_year': (searching_par.get('bdate')),
            'has_photo': '1',
            'offset': indent,
            'count': '1000'  # кол-во выводимых профилей
        }
        response_user_search = requests.get(user_search_url, params={**self.params, **user_search_params})
        # pprint(response_user_search.json())
        info = response_user_search.json()
        number_of_persons = info['response']['count']
        for one_person in info['response']['items']:
            list_of_all_persons.append(one_person['id'])
            list_of_all_persons.append(one_person['is_closed'])
        return list_of_all_persons, number_of_persons

    def get_photos(self, user_id):
        photos_url = self.url + 'photos.get'
        photos_params = {
            'owner_id': user_id,
            'extended': '1',
            'album_id': 'profile',
            'rev': '1'
        }
        response_photo_vk = requests.get(photos_url, params={**self.params, **photos_params})
        # print('Info about photos was loaded from vk')
        # pprint(response_photo_vk.json())
        return response_photo_vk.json()

    def change_vk_response(self, response_vk):
        """Изменяем ответа на нужный тип списка:
        ссылки на 3 самых популярных фотки в формате под вложение к письму вк и ссылка на пользователя"""
        list_of_dict_pic = []
        dict_height_size = {}
        list_pic_likes = []
        list_pic_url = []
        final_list = []
        for one_pic in response_vk['response']['items']:
            dict_info_one_pic = {}
            # print(pic_date)
            pic_likes = one_pic['likes']['count']
            dict_info_one_pic['pic_likes'] = pic_likes
            owner_id = one_pic['owner_id']
            dict_info_one_pic['owner_id'] = owner_id
            photo_id = one_pic['id']
            dict_info_one_pic['photo_id'] = photo_id
            # print(pic_likes)
            list_of_dict_pic.append(dict_info_one_pic)
        # Создаём списки, а далее ищём наибольшее кол-во лайков, удаляя их из списков и добавляя их в новый список
        for one_photo in list_of_dict_pic:
            list_pic_likes.append(one_photo['pic_likes'])
            list_pic_url.append(one_photo['photo_id'])
        # Находим ссылки на самые три популярных фото
        numb_of_profile_photos = len(list_pic_likes)
        # Проверяем, что в профиле вообще 3 фотки
        if numb_of_profile_photos > 3:
            numb_of_profile_photos = 3
        if numb_of_profile_photos == 0:
            final_list.append('Фотографий в профиле нет')
        if list_pic_likes:
            for i in range(0, numb_of_profile_photos):
                if list_pic_likes:
                    max_likes = max(list_pic_likes)
                    counter = -1
                    for one_like in list_pic_likes:
                        counter += 1
                        if max_likes == one_like:
                            list_pic_likes.remove(one_like)
                            return_counter = counter
                    final_list.append(list_pic_url[return_counter])
                    list_pic_url.pop(return_counter)
        # Вставляем в начало id найденного человека
        final_list.insert(0, list_of_dict_pic[0]['owner_id'])
        return final_list


if __name__ == '__main__':
    vk_client_2 = VkUser(config.vk_user_token, '5.130', '79932267')
    user_info = vk_client_2.get_main_info_about_user()
    params_for_search = vk_client_2.identify_search_parametres(user_info)[0]
    vk_search = Finder(config.vk_user_token, '5.130')
    founded_persons_id = vk_search.search_users(params_for_search)[0]
    count_founded_pers = vk_search.search_users(params_for_search)[1]
    free_ids = []
    for count in range(0, 20, 2):
        if not founded_persons_id[count+1]:
            free_ids.append(founded_persons_id[count])
    # Получаем ссылки и фотки первых 10 человек
    for numb in range(0, len(free_ids)):
        photos_garbage = vk_search.get_photos(free_ids[numb])
        changed_photos = vk_search.change_vk_response(photos_garbage)
        pprint(changed_photos)
        sleep(0.5)






