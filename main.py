import telebot

bot_key = open("bot_key.txt", "r").read()
bot = telebot.TeleBot(bot_key)

@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    bot.send_message(message.chat.id, "Привет. Я бот, который поможет тебе сохранять локации\n"
                                      "/add - Добавить локацию\n"
                                      "/list - Показать список сохраненных локаций\n"
                                      "/reset - Очистить все сохраненные ранее локации")

bot.polling()