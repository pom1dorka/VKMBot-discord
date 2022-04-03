from vk_api import VkApi
from discord import FFmpegOpusAudio
from auth_data import VK_LOGIN, VK_TOKEN, APP_ID

vk = VkApi(login=VK_LOGIN, app_id=APP_ID, token=VK_TOKEN)


def get_song(query):  # функция, которая получает ссылку, исполнителя, и название песни с серверов вк по заданному запросу
    song = vk.method('audio.search', {'q': query, 'auto_complete': 1})
    if not song['items']:
        return None
    song_id = song['items'][0]['ads']['content_id']
    song_url = vk.method('audio.getById', {'audios': song_id})[0]['url']
    song_artist, song_title = song['items'][0]['artist'], song['items'][0]['title']
    return {'artist': song_artist, 'title': song_title, 'player': FFmpegOpusAudio(song_url, before_options='-y -reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 1')}