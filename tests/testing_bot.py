import unittest
from time import sleep
from search_users.get_info_about_user import VkUser
from search_users.get_profiles import Finder
from config import vk_user_token


class TestFunctions(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        print("method setUpClass")

    def setUp(self):
        self.VkUser_test = VkUser(vk_user_token, '5.130', '79932267')
        self.Finder_test = Finder(vk_user_token, '5.130')
        print("method setUp")

    def tearDown(self):
        print("method tearDown")

    @classmethod
    def tearDownClass(cls):
        print("method tearDownClass")

    # Проверка на то, что возвращается не пустой список
    def test_get_main_info_about_user(self):
        sleep(1)
        self.assertTrue(self.VkUser_test.get_main_info_about_user())

    # Проверка на то, что список параметров для поиска не пуст
    def test_identify_search_parametres(self):
        sleep(1)
        info_about_user = self.VkUser_test.get_main_info_about_user()
        self.assertTrue(self.VkUser_test.identify_search_parametres(info_about_user)[0])

    # Проверка на ожидаемое значение списка параметров (но они могут и измениться)
    def test_identify_search_parametres_meaning(self):
        sleep(1)
        info_about_user = self.VkUser_test.get_main_info_about_user()
        profile_dict = {'sex': '1', 'bdate': '1998', 'city': '2', 'relation': '6'}
        self.assertEqual(profile_dict, self.VkUser_test.identify_search_parametres(info_about_user)[0])

    # Проверка на наличие результатов поиска (при 4-ёх параметрах и даекватных данных всегда должен тест проходить)
    def test_search_users(self):
        sleep(1)
        user_info = self.VkUser_test.get_main_info_about_user()
        params_for_search = self.VkUser_test.identify_search_parametres(user_info)[0]
        self.assertTrue(self.Finder_test.search_users(params_for_search)[0])

    # Проверка на ожидаемое значение количества фотографий (но они могут и измениться)
    def test_get_photos_count(self):
        sleep(1)
        self.assertEqual(5, self.Finder_test.get_photos('79932267')['response']['count'])

    # Проверка на наличие фотографий (но они могут и измениться)
    def test_get_photos(self):
        sleep(1)
        self.assertTrue(self.Finder_test.get_photos('79932267'))


if __name__ == '__main__':
    unittest.main()
