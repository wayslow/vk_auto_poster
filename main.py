import os
import pathlib
import random
import shutil

import requests
from dotenv import load_dotenv


def download_comics(comics_url, path):
    response = requests.get(comics_url)
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


def grt_upload_url(params, group_id, vk_api_url):
    params_update = {
        'group_id': group_id,
    }
    params.update(params_update)

    method = 'photos.getWallUploadServer'
    vk_method_url = f'{vk_api_url}/{method}'

    response = requests.get(vk_method_url, params=params)
    response.raise_for_status()

    response_info = response.json()
    url = response_info['response']['upload_url']
    return url


def get_server_info(path, url):
    with open(path, 'rb') as file:
        files = {
            'photo': file,
        }

        response = requests.post(url, files=files)
        response.raise_for_status()

        server_info = response.json()

    return server_info


def get_info_for_post(vk_api_url, params, path, group_id):
    url = grt_upload_url(params, group_id, vk_api_url)

    server_info = get_server_info(path, url)

    server = server_info['server']
    photo = server_info['photo']
    photo_hash = server_info["hash"]

    params_update = {
        'server': server,
        'photo': photo,
        'hash': photo_hash
    }
    params.update(params_update)

    method = 'photos.saveWallPhoto'
    vk_method_url = f'{vk_api_url}/{method}'

    response = requests.post(vk_method_url, params=params)
    response.raise_for_status()

    post_info = response.json()['response'][0]
    owner_id = post_info['owner_id']
    media_id = post_info['id']
    return f"photo{owner_id}_{media_id}"


def post_vk(vk_api_url, group_id, params, path, comics_comment):
    attachments = get_info_for_post(vk_api_url, params, path, group_id)

    params_update = {
        'attachments': attachments,
        'owner_id': -group_id,
        'from_group': 1,
        'message': comics_comment,
    }
    params.update(params_update)

    method = 'wall.post'
    vk_method_url = f'{vk_api_url}/{method}'

    response = requests.post(vk_method_url, params=params)
    response.raise_for_status()


def main():
    load_dotenv()

    access_token = os.getenv('ACCESS_TOKEN')
    vk_api_url = 'https://api.vk.com/method/'
    group_id = os.getenv('GROUP_ID')
    comic_number = random.randint(1, 2786)
    file_name = f"{str(comic_number)}.png"
    books_folder_name = 'comiks'

    path = os.path.join(books_folder_name, file_name)

    params = {
        'access_token': access_token,
        'v': 5.313,
    }

    pathlib.Path(books_folder_name).mkdir(parents=True, exist_ok=True)

    comics_comment = get_comics(comic_number, path)

    post_vk(vk_api_url, group_id, params, path, comics_comment)

    shutil.rmtree(books_folder_name)


if __name__ == '__main__':
    main()
