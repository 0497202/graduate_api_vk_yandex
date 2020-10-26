'''
This program downloads all photos in maximum resolution from the VKontakte
profile using the number of likes of the photo for the name, then sends the
selected number of photos to Yandex disk for this creates a new folder.
'''
# import of libraries
import datetime
import json
import os
import requests
from urllib.parse import urljoin

# Constans vk
V = '5.21'

# class VK User
class VKApiClient:
    BASE_URL = 'https://api.vk.com/method/'
    def __create_method_url(self, method):
        return urljoin(self.BASE_URL, method)

    # Initialise
    def __init__(self, id, count,  token, version=V):
        self.id = id
        self.count = count
        self.token = token
        self.version = version

    # Get photos from vk wall
    def get_vk_photos(self):
        response = requests.get(self.__create_method_url('photos.get'),
        params={
        'access_token': self.token,
        'v': self.version,
        'owner_id': self.id,
        'album_id': 'profile',
        'count': self.count,
        'extended': 1,
        'photo_sizes': 1
        })

        # Make full list
        full_list = []
        # Make list of sizes
        items = response.json()['response']['items']
        size_list = []
        for item in items:
            size_list.append(item['sizes'][-1])
        # Make list of likes
        like_list = []
        for item in items:
            if item['likes']['count'] in like_list:
                like_list.append(datetime.date.today())
            like_list.append(item['likes']['count'])
        # Make list of types
        type_list = []
        for item in items:
            type_list.append(item['sizes'][-1]['type'])

        # Put all lists in one full list
        full_list.append(size_list)
        full_list.append(like_list)
        full_list.append(type_list)

        return full_list    # [size_list, like_list, type_list]

    def save_vk_photos_pc(self, full_list):
        self.full_list = full_list
        # List of src
        photo_list = []
        for src in full_list[0]:
            photo_list.append(src['src'])
        # Write photos on PC
        for number, photo in enumerate(photo_list[: self.count]):
            r = requests.get(photo)
            print(f'{number + 1} - фотография скачана из вконтатке на ваш ПК')
            with open(f'{file_folder}/' + str(full_list[1][number]) + '.jpg', 'wb') as f:
                f.write(r.content)

# Class Yandex loader
class YaUploader:
    def __init__(self, token):
        self.token = token

    # Creat folder method
    def create_folder(self, dir_name):
        self.dir_name = dir_name
        response = requests.put('https://cloud-api.yandex.net/v1/disk/resources',\
        params={"path":self.dir_name},\
        headers={"Authorization": f"OAuth {TOKEN_YAN}"})
        print(f'\nпапка {self.dir_name} успешно создана.')

    # Upload photos on yandex disc
    def upload(self, dir_name, file_folder, file_name: str):
        self.dir_name = dir_name
        self.file_folder = file_folder
        self.file_name = file_name

        # Get response
        response = requests.get(\
        "https://cloud-api.yandex.net/v1/disk/resources/upload", \
        params={"path": f"{self.dir_name}/{self.file_name}"},\
        headers= {"Authorization": f"OAuth {self.token}"})

        # Paste file on yandex disc
        link = response.json()["href"]
        response = requests.put(link, \
        files={"file": open(f'{file_folder}/{file_name}', "rb")},\
        headers={"Authorization": f"OAuth {self.token}"})

        return f'Ваш {file_name} , был успешно загружен'

# JSON file create with result of programm
def json_create(photo_jpg, full_list):
    type_list = full_list[2]
    res = {}
    with open("result.json", "w") as write_file:
        for id, photo in enumerate(photo_jpg):
            res['file_name'] = photo_jpg[id]
            res['size'] = type_list[id]
            json.dump(res, write_file)
    print(f'Информация о загруженных файлах успешно записана в json файл.')

# Main programm
if __name__ == '__main__':
    # Input token
    TOKEN_VK = input('Введите токен ВКОНТАКТЕ: ')
    TOKEN_YAN = input('Введите токен Яндекс.диск: ')
    VK_ID = int(input('Введите ваш id вконтакте: '))

    # Count of photos to download from VK
    count_vk_photos = int(input('\nВведите количество фото которые хотите скачать из вк: '))

    # Creating instances of the classes
    vk_client = VKApiClient(VK_ID, count_vk_photos, TOKEN_VK, V)
    uploader = YaUploader(TOKEN_YAN)

    # Create vk_photos folder on yandex disc
    dir_name = input('Введите имя папки для создания на яндекс диске: ')
    while not dir_name:
        if not dir_name:
            print('\nИмя папки не задано!')
            dir_name = input('\n\nВведите имя папки для создания на яндекс диске: ')
    uploader.create_folder(dir_name)

    # Create folder on PC
    file_folder = input('Введите название папки куда сохранятся фото на ваш ПК: ')
    os.mkdir(file_folder)
    print(f'\n{file_folder} на компьютере успешно создана.')

    # Get full list
    full_list = vk_client.get_vk_photos()
    # Save all photos from vk
    vk_client.save_vk_photos_pc(full_list)

    # all files to list
    files = os.listdir(file_folder)

    # Filter list
    photo_jpg = []
    for photo in files:
        if photo.endswith('.jpg'):
            photo_jpg.append(photo)

    # Load to Yandex disc
    for photo in photo_jpg:
        result = uploader.upload(dir_name, file_folder, photo)
        print(result)
    print(f'\nВсе ваши файлы были успешно загружены в папку\
    {dir_name} на яндекс диске.')

    # Create JSON file on PC
    json_create(photo_jpg, full_list)
