import vk_api
import traceback
import requests
from vk_api.bot_longpoll import VkBotLongPoll, VkBotEventType
from vk.vk_bot import VkBot
import info
from info import ChatsInfo, UsersInfo
import os
import mysql
import warnings

warnings.filterwarnings('ignore')

RANDOM_STATE = 42
BOT_GROUP_ID = os.environ.get('VK_BOT_GROUP_ID')  # id группы с ботом
BUG_CHAT_ID = os.environ.get('VK_BUG_CHAT_ID')  # peer_id чата, в который будут приходить сообщения с ошибками
TOKEN = os.environ.get('VK_TOKEN')


def main():
    chats, users = ChatsInfo(), UsersInfo()
    users.create_table()  # создадим сразу таблицу всех пользователей
    vk = vk_api.VkApi(token=TOKEN)
    vkbot = VkBot(vk, users, chats)

    while True:
        try:
            longpoll = VkBotLongPoll(vk, BOT_GROUP_ID)
            print('Bot is ready to start')

            for event in longpoll.listen():
                if event.type == VkBotEventType.MESSAGE_NEW:
                    event_obj = event.obj.get('message')
                    user_id = event_obj.get('from_id')
                    peer_id = event_obj.get('peer_id')
                    message = event_obj.get('text')

                    if event.from_group:
                        continue
                    elif event.from_chat:
                        chats.create_table(peer_id)
                        if not chats.is_reg(peer_id, user_id):
                            chats.insert_user(peer_id, user_id)
                        if not users.is_reg(user_id):
                            users.insert_user(**vkbot.get_all_user_data(user_id))
                    elif event.from_user:
                        if not users.is_reg(user_id):
                            users.insert_user(**vkbot.get_all_user_data(user_id))

                    vkbot.new_message(peer_id, user_id, message)

        except (requests.exceptions.ReadTimeout, requests.exceptions.ConnectionError) as timeout:
            continue

        except mysql.connector.errors.OperationalError:
            info.refresh_connection()
            continue

        except Exception as e:
            error = f'&#9888; Ошибка: {e}\n\
                  &#128169; Пользователь: {vkbot.get_user_fullname(user_id)}\n\
                  &#129511; Беседа: {peer_id}\n\
                  &#128140; Текст сообщения: {message}\n\n\
                  &#9881; Описание ошибки:\n\n {traceback.format_exc()}'
            vkbot.send_message(BUG_CHAT_ID, error)
            continue


if __name__ == '__main__':
    main()
