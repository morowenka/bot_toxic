import vk_api
import traceback
import requests
import torch
from vk_api.bot_longpoll import VkBotLongPoll, VkBotEventType
from vk_bot import VkBot
from info import ChatsInfo, UsersInfo
import warnings

warnings.filterwarnings('ignore')

RANDOM_STATE = 42
BUG_CHAT_ID = 378102106  # peer_id чата, в который будут приходить сообщения с ошибками
BOT_GROUP_ID = 214806981  # id группы с ботом
TOKEN = "vk1.a.zidAFdRn1-ggq9-c4xQJyvS6DPLMHmU3iSwW5Ew9esCKT7WvLgb3AmIZwwn5HUAcp-NelrV16icHDm-85T65xiZ0y_X9387hOG4opbOA-b_xpiGiMchMyP2oJdsduKsdkpXOWu8iE1JiB8BghgIUxPjt6XuwfychURy5Ga_ocVwXD9IpdNA4ieIkxnnSnnhT"


def main():
    chats, users = ChatsInfo(), UsersInfo()
    users.create_table()  # создадим сразу таблицу всех пользователей
    vk = vk_api.VkApi(token=TOKEN)
    vkbot = VkBot(vk, users, chats)

    while True:
        longpoll = VkBotLongPoll(vk, BOT_GROUP_ID)

        try:
            for event in longpoll.listen():
                if event.type == VkBotEventType.MESSAGE_NEW:
                    event_obj = event.obj.get('message')
                    user_id = event_obj.get('from_id')
                    peer_id = event_obj.get('peer_id')
                    message = event_obj.get('text')

                    if event.from_chat:
                        chats.create_table(peer_id)
                        if not chats.is_reg(peer_id, user_id):
                            chats.insert_user(peer_id, user_id)
                        if not users.is_reg(user_id):
                            users.insert_user(user_id)

                    if event.from_user:
                        if not users.is_reg(user_id):
                            users.insert_user(user_id)

                    vkbot.new_message(peer_id, user_id, message)

        except requests.exceptions.ReadTimeout as timeout:
            continue

        except Exception as e:
            error = f'&#9888; Ошибка: {e}\n\
                  &#128169; Пользователь: {vkbot.get_user_fullname(user_id)}\n\
                  &#129511; Беседа: {peer_id}\n\
                  &#128140; Текст сообщения: {message}\n\n\
                  &#9881; Описание ошибки:\n\n {traceback.format_exc()}'
            vkbot.send_message(BUG_CHAT_ID, error)


if __name__ == '__main__':
    main()
