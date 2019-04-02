import telebot
#import logging
import json
import redis
from enum import Enum

bot_key = open("bot_key.txt", "r").read().strip()
bot = telebot.TeleBot(bot_key)
redis_db = redis.Redis(host="localhost", port=6379)

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
    states[message.chat.id] = StateWithInfo(State.NO_STATE, None)

@bot.message_handler(commands=['abort'])
def abort(message):
    states[message.chat.id] = StateWithInfo(State.NO_STATE, None)

@bot.message_handler(commands=['add'])
def add_location(message):
    bot.send_message(message.chat.id, "Добавление нового места.\n"
                                      "Пришлите его локацию")
    states[message.chat.id] = StateWithInfo(State.WAIT_FOR_LOCATION, None)

@bot.message_handler(commands=['list'])
def list(message):
    locations_number_str = redis_db.get("locations_bot:{chat_id}:locations_number".format(chat_id=message.chat.id))
    if locations_number_str is None:
        bot.send_message(message.chat.id, "No stored locations")
        return
    
    locations_number = int(locations_number_str)
    start_from_location_n = max(0, locations_number - 10)
    for loc_n in range(start_from_location_n, locations_number):
        location_key = "locations_bot:{}:location_{}".format(message.chat.id, loc_n)

        name = redis_db.get(location_key + ":name")
        bot.send_message(message.chat.id, name)

        location_str = redis_db.get(location_key + ":loc")
        jloc = json.loads(location_str)
        bot.send_location(message.chat.id, latitude=jloc["latitude"], longitude=jloc["longitude"])

@bot.message_handler(commands=['reset'])
def reset(message):
    keys = redis_db.keys('locations_bot:{}*'.format(message.chat.id))
    for k in keys:
        redis_db.delete(k)
    bot.send_message(message.chat.id, "Deleted")


@bot.message_handler(content_types=["location"])
def add_location_get_location(message):
    if message.location is None or message.content_type != "location":
        bot.send_message(message.chat.id, "Все еще жду геоданные места\n"
                                          "/abort - чтобы отменить операцию добавления локации")
        return
    states[message.chat.id] = StateWithInfo(State.WAIT_FOR_LOCATION_NAME, message.location)
    bot.send_message(message.chat.id, "Теперь введите название локации")

@bot.message_handler(func=lambda message: states[message.chat.id].state == State.WAIT_FOR_LOCATION_NAME)
def add_location_get_name(message):
    if message.content_type != "text":
        bot.send_message(message.chat.id, "Получил что-то не то. Жду название локации\n"
                                          "/abort - тобы отменить операцию добавления локации")
        return

    location = states[message.chat.id].info
    name = message.text

    chat_key = "locations_bot:{}".format(message.chat.id)
    locations_number_key = chat_key + ':locations_number'

    if not redis_db.exists(locations_number_key):
        redis_db.set(locations_number_key, 0)

    location_id = redis_db.incr(locations_number_key) - 1

    location_key = chat_key + ":location_{}".format(location_id)

    redis_db.set(location_key + ":id", location_id)

    location_str = json.dumps({
        "latitude": location.latitude,
        "longitude": location.longitude
    })
    redis_db.set(location_key + ":loc", location_str)
    redis_db.set(location_key + ":name", name)

    bot.send_message(message.chat.id, "Добавлено")
    states[message.chat.id] = StateWithInfo(State.NO_STATE, None)

#telebot.logger.setLevel(logging.DEBUG)
bot.polling()