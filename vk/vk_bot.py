import torch.nn.functional as F
from vk_api.utils import get_random_id
from transformers import BertTokenizer, BertForSequenceClassification
import torch
from datetime import date

DEVICE = 'cuda' if torch.cuda.is_available() else 'cpu'

try:
    tokenizer = BertTokenizer.from_pretrained('tokenizer')
except:
    tokenizer = BertTokenizer.from_pretrained('SkolkovoInstitute/russian_toxicity_classifier')
    tokenizer.save_pretrained('tokenizer')
try:
    model = BertForSequenceClassification.from_pretrained('model').to(DEVICE)
except:
    model = BertForSequenceClassification.from_pretrained('SkolkovoInstitute/russian_toxicity_classifier').to(DEVICE)
    model.save_pretrained('model')


class VkBot:
    def __init__(self, vk, users, chats):
        self.COMMANDS = ('>команды', '>чек', '>моя стата', '>юзеры', '>топ общий', '>топ беседы')
        self.vk = vk
        self.users = users
        self.chats = chats

    def new_message(self, peer_id, user_id, message):
        if message.lower() == self.COMMANDS[0]:
            self.send_message(peer_id, ', '.join(self.COMMANDS))

        elif message.lower()[:4] == self.COMMANDS[1]:
            message = message.lower()[4:]
            toxicity_class, toxicity_level = self.compute_toxicity(message)
            emoji = ['&#128545;', '&#128522;'][toxicity_level < 50]
            self.send_message(peer_id, f'{self.get_user_name(user_id)}, ваше сообщение является {toxicity_class} {emoji}.\n\
                                  Уровень токсичности: {toxicity_level:.2f}%.')

        elif message.lower() == self.COMMANDS[2]:
            rating = self.rating_calc(self.users.get_toxic_comments(user_id), self.users.get_all_comments(user_id))
            if peer_id != user_id:
                chat_rating = self.rating_calc(self.chats.get_toxic_comments(peer_id, user_id),
                                               self.chats.get_all_comments(peer_id, user_id))
                self.send_message(peer_id, f'{self.get_user_name(user_id)}, ваша статистика:\n\n\
                                    &#9993; Всего сообщений: {self.users.get_all_comments(user_id)}.\n\
                                    &#128545; Всего токсичных сообщений: {self.users.get_toxic_comments(user_id)}.\n\
                                    &#127942; Общий рейтинг токсичности: {rating:.2f}\n\
                                    &#9993; Сообщений в этой беседе: {self.chats.get_all_comments(peer_id, user_id)}.\n\
                                    &#128545; Токсичных сообщений в этой беседе: {self.chats.get_toxic_comments(peer_id, user_id)}.\n\
                                    &#127942; Рейтинг токсичности в этой беседе: {chat_rating:.2f}')
            else:
                self.send_message(peer_id, f'{self.get_user_name(user_id)}, ваша статистика:\n\n\
                                    &#9993; Всего сообщений: {self.users.get_all_comments(user_id)}.\n\
                                    &#128545; Всего токсичных сообщений: {self.users.get_toxic_comments(user_id)}.\n\
                                    &#127942; Общий рейтинг токсичности: {rating:.2f}')

        elif message.lower() == self.COMMANDS[3]:
            all_users_count = self.users.rows()

            # проверка окончания
            def ending_check(num):
                match num % 10:
                    case 1:
                        return 'ь'
                    case 2 | 3 | 4:
                        return 'я'
                    case _:
                        return 'ей'

            if peer_id != user_id:
                chat_users_count = self.chats.rows(peer_id)
                self.send_message(peer_id,
                                  f'Всего на данный момент зарегестрировано {all_users_count} пользовател{ending_check(all_users_count)}.\n\
                                    Всего в этой беседе зарегестрировано {chat_users_count} пользовател{ending_check(chat_users_count)}.')
            else:
                self.send_message(peer_id,
                                  f'Всего на данный момент зарегестрировано {all_users_count} пользовател{ending_check(all_users_count)}.')

        elif message.lower() == self.COMMANDS[4]:
            msg = 'Топ токсичных пользователей за все время\n[&#128545; токсичные | &#9993; все | &#127942; рейтинг токсичности]\n'
            top = self.users.get_top_n(10)
            data = self.vk.method('users.get', {'user_ids': ', '.join([str(i[0]) for i in top])})
            for i, value in enumerate(top):
                name = data[i].get('first_name') + ' ' + data[i].get('last_name')
                msg += f'{i + 1}. @id{value[0]} ({name}): {value[1]} | {value[2]} | {(value[3] if value[3] else 0):.2f}\n'
            self.send_message(peer_id, msg)

        elif message.lower() == self.COMMANDS[5]:
            if peer_id != user_id:
                msg = 'Топ токсичных пользователей этой беседы за все время\n[&#128545; токсичные | &#9993; все | &#127942; рейтинг токсичности]\n'
                top = self.chats.get_top_n(peer_id, 10)
                data = self.vk.method('users.get', {'user_ids': ', '.join([str(i[0]) for i in top])})
                for i, value in enumerate(top):
                    name = data[i].get('first_name') + ' ' + data[i].get('last_name')
                    msg += f'{i + 1}. @id{value[0]} ({name}): {value[1]} | {value[2]} | {(value[3] if value[3] else 0):.2f}\n'
                self.send_message(peer_id, msg)
            else:
                self.send_message(peer_id, f'чел.. это не беседа. никто не виноват, что у тебя нет друзей')
        else:
            toxicity_class, toxicity_level = self.compute_toxicity(message)
            if peer_id != user_id:
                self.users.update(user_id, toxicity_level > 50)
                self.chats.update(peer_id, user_id, toxicity_level > 50)

    def send_message(self, peer_id, message):
        self.vk.method('messages.send', {'peer_id': peer_id,
                                         'random_id': get_random_id(),
                                         'message': message})

    def rating_calc(self, toxic, all):
        return pow(toxic, 2) / all if all != 0 else 0

    def get_user_name(self, user_id):
        return f'@id{user_id} ({self.vk.method("users.get", {"user_ids": user_id})[0].get("first_name")})'

    def get_user_fullname(self, user_id):
        user_data = self.vk.method('users.get', {'user_ids': user_id})[0]
        return f'@id{user_id} ({user_data.get("first_name") + " " + user_data.get("last_name")})'

    def get_user_data(self, user_id):
        user_data = self.vk.method('users.get', {'user_ids': user_id,
                                                 'fields': 'first_name, last_name, sex, bdate, '
                                                           'country, city, personal, relation'})[0]
        user_dict_data = {
            'user_id': user_id,
            'user_name': user_data.get('first_name'),
            'user_surname': user_data.get('last_name'),
            'user_first_login_date': date.isoformat(date.today()),
            'user_sex': user_data.get('sex'),
            'user_bdate': '-'.join(user_data.get('bdate').split('.')[::-1]) if user_data.get('bdate') else None,
            'user_country': user_data.get('country').get('title') if user_data.get('country') else None,
            'user_city': user_data.get('city').get('title') if user_data.get('city') else None,
            'user_political': user_data.get('personal').get('political') if user_data.get('personal') else None,
            'user_religion': user_data.get('personal').get('religion') if user_data.get('personal') else None,
            'user_relation': user_data.get('relation'),
            'user_people_main': user_data.get('personal').get('people_main') if user_data.get('personal') else None,
            'user_life_main': user_data.get('personal').get('life_main') if user_data.get('personal') else None,
            'user_smoking': user_data.get('personal').get('smoking') if user_data.get('personal') else None,
            'user_alcohol': user_data.get('personal').get('alcohol') if user_data.get('personal') else None,
        }
        return user_dict_data

    def compute_toxicity(self, message):
        input = tokenizer.encode(message, return_tensors='pt')
        output = F.softmax(model(input).logits.data, dim=1)[0, 1]
        toxicity_class = ['нетоксичным', 'токсичным'][output > 0.5]
        return toxicity_class, float(output) * 100
