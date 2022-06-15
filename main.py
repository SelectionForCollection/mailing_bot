import telebot
import re
import os


bot = telebot.TeleBot('5502039945:AAFf6awspHw9bRMYk5PqObtCPQx6Pg2GdAs')
BOT_ID = 5502039945
CHANNEL_REGEXP = re.compile(r'@[a-zA-Z][a-zA-z_]{,31}')

CHANNEL_NAMES = []
file = open('channels_names.txt', 'r')
for line in file:
    CHANNEL_NAMES.append(line)
file.close()

@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(message.chat.id, 'Привет, ' + message.chat.first_name + '.')

@bot.message_handler(commands=['check_channels'])
def check_channels(message):
    response = ""
    if len(CHANNEL_NAMES) != 0:
        for channel in CHANNEL_NAMES:
            try:
                admins = bot.get_chat_administrators(channel)
                for admin in admins:
                    if admin.user.id == BOT_ID:
                        response += "В " + channel + " я админ, все ок\n"
            except Exception:
                response += "В " + channel + " я НЕ админ, это не гуд\n"
                CHANNEL_NAMES.remove(channel)
        bot.send_message(message.chat.id, response + '\n\nКаналы, где я не админ, в список подключенных каналов не попадают. Рекомендую отправить /mailing_channels.')
    else:
        bot.send_message(message.chat.id, 'Бот пока не подключени ни к одному каналу')


@bot.message_handler(commands=['mailing_channels'])
def mailing_channels(message):
    bot.send_message(message.chat.id, 'Подключенные каналы: ' + str(CHANNEL_NAMES))
    os.system(r' >channels_names.txt')
    file = open('channels_names.txt', 'w')
    for channel in CHANNEL_NAMES:
        file.write(channel + '\n')
    file.close()


@bot.message_handler(commands=['add_mailing_channel'])
def helper_add_mailing_channel(message):
    send = bot.send_message(message.chat.id, 'Отправляй.\nМожешь отправить сразу несколько, только тогда пиши их с новой строки.')
    bot.register_next_step_handler(send, add_mailing_channel)

def add_mailing_channel(message):
    buff = message.text.split('\n')
    for el in buff:
        el = el.replace(' ', '')
        if CHANNEL_REGEXP.match(el):
            CHANNEL_NAMES.append(el)
    bot.send_message(message.chat.id, 'Распознаны каналы: ' + str(CHANNEL_NAMES) + '\n\nРекомендуется выполнить проверку /check_channels')


@bot.message_handler(commands=['new_mailing'])
def new_mailing(message):
    send = bot.send_message(message.chat.id, 'Cлушаю')
    bot.register_next_step_handler(send, remail)

def remail(message):
    for channel in CHANNEL_NAMES:
        match message.content_type:
            case 'text':
                bot.send_message(channel, message.text)
            case 'photo':
                bot.send_photo(channel, message.photo[-1].file_id, caption=message.caption)
            case 'video':
                bot.send_video(channel, message.video.file_id, caption=message.caption)
            case 'voice':
                bot.send_audio(channel, message.voice.file_id)
            case 'audio':
                bot.send_audio(channel, message.audio.file_id, caption=message.caption)
            case 'document':
                bot.send_document(channel, message.document.file_id, caption=message.caption)
            case 'sticker':
                bot.send_sticker(channel, message.sticker.file_id)
    bot.send_message(message.chat.id, 'Отправил, епта')

bot.polling(none_stop=True)
