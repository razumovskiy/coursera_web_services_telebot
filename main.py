import telebot

bot = telebot.TeleBot("842406090:AAFWJ1tgjbcn6nn7uPpscV-umysITtLXal4")

@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    bot.send_message(message.chat.id, "Привет. Я бот, который поможет тебе сохранять локации\n"
                                      "/add - Добавить локацию\n"
                                      "/list - Показать список сохраненных локаций\n"
                                      "/reset - Очистить все сохраненные ранее локации")

bot.polling()