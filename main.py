import telebot
from enum import Enum

bot_key = open("bot_key.txt", "r").read()
bot = telebot.TeleBot(bot_key)

class State(Enum):
    NO_STATE = 0
    WAIT_FOR_LOCATION = 1
    WAIT_FOR_LOCATION_NAME = 2

class StateWithInfo:
    def __init__(self, state, info):
        self.state = state
        self.info = info

states = dict()


@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    bot.send_message(message.chat.id, "Привет. Я бот, который поможет тебе сохранять локации\n"
                                      "/add - Добавить локацию\n"
                                      "/list - Показать список сохраненных локаций\n"
                                      "/reset - Очистить все сохраненные ранее локации")

@bot.message_handler(commands=['abort'])
def abort(message):
    states[message.chat.id] = StateWithInfo(State.NO_STATE, None)

@bot.message_handler(commands=['add'])
def add_location(message):
    bot.send_message(message.chat.id, "Добавление нового места.\n"
                                      "Пришлите его локацию")
    states[message.chat.id] = StateWithInfo(State.WAIT_FOR_LOCATION, None)

@bot.message_handler(content_types=["location"])
def add_location_get_location(message):
    print("add_location_get_location")
    if message.location is None or message.content_type != "location":
        bot.send_message(message.chat.id, "Все еще жду геоданные места\n"
                                          "/abort - чтобы отменить операцию добавления локации")
        return
    print(message.location)
    states[message.chat.id] = StateWithInfo(State.WAIT_FOR_LOCATION_NAME, message.location)
    bot.send_message(message.chat.id, "Теперь введите название локации")

@bot.message_handler(func=lambda message: states[message.chat.id].state == State.WAIT_FOR_LOCATION_NAME)
def add_location_get_name(message):
    if message.content_type != "text":
        bot.send_message(message.chat.id, "Получил что-то не то. Жду название локации\n"
                                          "/abort - тобы отменить операцию добавления локации")
        return
    print(states[message.chat.id].info)
    print(message.text)
    bot.send_message(message.chat.id, "Добавлено")
    states[message.chat.id] = StateWithInfo(State.NO_STATE, None)



bot.polling()