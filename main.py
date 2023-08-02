import os
import pathlib
import random
import shutil

import requests
from dotenv import load_dotenv

VK_API_URL = 'https://api.vk.com/method/'


def check_stastus(response):
    if response.json()['error']:
        raise requests.HTTPError()
    return response.json()


def download_comics(comics_url, path):
    response = requests.get(comics_url)
    response.raise_for_status()
    with open(path, "wb") as file:
        file.write(response.content)


def get_comics(comic_number, path):
    page_url = f'https://xkcd.com/{comic_number}/info.0.json'

    response = requests.get(page_url)
    response.raise_for_status()

    comics_url = response.json()['img']

    download_comics(comics_url, path)

    comics_comment = response.json()['alt']
    return comics_comment


def upload_photo(path, url):
    with open(path, 'rb') as file:
        files = {
            'photo': file,
        }
        response = requests.post(url, files=files)

    response.raise_for_status()
    server_property = check_stastus(response)

    server = server_property['server']
    photo = server_property['photo']
    photo_hash = server_property["hash"]
    return server, photo, photo_hash


def get_upload_url(vk_access_token, version, vk_group_id):
    params = {
        'access_token': vk_access_token,
        'vk_group_id': vk_group_id,
        'v': version,
    }

    method = 'photos.getWallUploadServer'
    vk_method_url = f'{VK_API_URL}/{method}'

    response = requests.get(vk_method_url, params=params)
    response.raise_for_status()
    upload_url = check_stastus(response)['response']['upload_url']

    return upload_url


def save_wall_photo(server, photo, photo_hash, vk_access_token, version):
    params = {
        'access_token': vk_access_token,
        'server': server,
        'photo': photo,
        'hash': photo_hash,
        'v': version,
    }

    method = 'photos.saveWallPhoto'
    vk_method_url = f'{VK_API_URL}/{method}'

    response = requests.post(vk_method_url, params=params)
    response.raise_for_status()
    post_property = check_stastus(response)['response'][0]

    owner_id = post_property['owner_id']
    media_id = post_property['id']
    return f"photo{owner_id}_{media_id}"


def post_vk(attachments, vk_group_id, vk_access_token, version, comics_comment):
    params = {
        'access_token': vk_access_token,
        'attachments': attachments,
        'owner_id': f"-{vk_group_id}",
        'from_group': 1,
        'message': comics_comment,
        'v': version,
    }

    method = 'wall.post'
    vk_method_url = f'{VK_API_URL}/{method}'

    response = requests.post(vk_method_url, params=params)
    response.raise_for_status()
    check_stastus(response)


def main():
    load_dotenv()

    vk_access_token = os.getenv('VK_ACCESS_TOKEN')
    vk_group_id = os.getenv('VK_GROUP_ID')
    comic_count = 2786
    comic_number = random.randint(1, comic_count)
    file_name = f"{comic_number}.png"
    books_folder_name = 'comiks'

    path = os.path.join(books_folder_name, file_name)
    version = 5.313,
    try:
        pathlib.Path(books_folder_name).mkdir(parents=True, exist_ok=True)

        comics_comment = get_comics(comic_number, path)

        upload_url = get_upload_url(vk_access_token, version, vk_group_id)
        server, photo, photo_hash = upload_photo(path, upload_url)
        attachments = save_wall_photo(server, photo, photo_hash, vk_access_token, version)

        post_vk(attachments, vk_group_id, vk_access_token, version, comics_comment)

    finally:
        shutil.rmtree(books_folder_name)


if __name__ == '__main__':
    main()
