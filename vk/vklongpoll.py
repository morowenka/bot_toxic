from vk_api.bot_longpoll import VkBotLongPoll

class MyVkBotLongPoll(VkBotLongPoll):
    def listen(self):
        while True:
            try:
                for event in self.check():
                    yield event
            except Exception as e:
                print('VK Longpoll Error:', e)
                continue
