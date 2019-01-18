from telegram import (ReplyKeyboardMarkup, ReplyKeyboardRemove)
from telegram.ext import (Updater, CommandHandler, MessageHandler, Filters, RegexHandler,
                          ConversationHandler)

import logging
import pandas as pd
db = 0

def load_db(file):
    global db
    xl = pd.ExcelFile(file)
    db = xl.parse('Sheet1')

def map_word_to_number(word):
    map = {
        'یک': 1,
        'دو': 2,
        'سه': 3,
        'چهار': 4,
        'پنج': 5,
        'شش': 6,
        'هفت': 7,
        'هشت': 8,
        'نه': 9,
        'ده': 10,
        'یازده': 11,
        'دوازده': 12,
        'سیزده': 13,
        'چهارده': 14,
        'پانزده': 15,
        'شانزده': 16,
        'هفده': 17,
        'هجده': 18
    }
    return map[word]

def find_mobiles(data):
    res = db.copy()
    if 'name' in data:
        res = res[res.name == data['name']]
    if 'brand' in data:
        res = res[res.brand == data['brand']]
    if 'price' in data:
        valid_prices = range(data['price'], data['price']+1000000)
        res = res[res.toman.isin(valid_prices)]
    if 'size' in data:
        minsize, maxsize = data['size'].split('-')
        res = res[(res['size'] >= float(minsize)) & (res['size'] < float(maxsize))]
    if 'storage' in data:
        res = res[res.storage == data['storage']]
    if len(res) > 0 and 'color' in data:
        res.color.iloc[[0]] = data['color']
    return res

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)

BRAND, PRICE, COLOR, SIZE, STORAGE, NAME = range(6)
brands = [['سامسونگ', 'اپل', 'ال جی', 'گوگل'],['هواوی', 'اچ تی سی', 'نوکیا', 'شیائومی']]

def start(bot, update):

    update.message.reply_text(
        'سلام. من ربات تلگرام پیشنهاد دهنده‌ی موبایلم!\n'
        'چه برند موبایلی مد نظرتونه؟',
        reply_markup=ReplyKeyboardMarkup(brands, one_time_keyboard=True))

    return BRAND

def brand(bot, update, user_data):
    user_data.clear()
    user = update.message.from_user
    logger.info("Brand of %s: %s", user.first_name, update.message.text)
    user_data['brand'] = update.message.text
    update.message.reply_text('حالا محدوده‌ی قیمتی که مد نظرته رو بهم بگو!',
                              reply_markup=ReplyKeyboardRemove())

    return PRICE


def price(bot, update, user_data):
    user = update.message.from_user
    logger.info("Price of %s: %s", user.first_name, update.message.text)
    milion = update.message.text.split()[0]

    if (milion == 'زیر یک میلیون'):
        user_data['price'] = 0
    else:
        user_data['price'] = map_word_to_number(milion)*1000000

    res = find_mobiles(data=user_data)
    if len(res) == 0:
        update.message.reply_text('موبایل مورد نظر شما پیدا نشد. یه محدوده‌ی قیمت جدید بهم بگو',
                                  )
        return PRICE
    elif len(res) == 1:
        colors = res.iloc[0]['color']
        colors = [colors.replace(' ', '').split(',')]
        user_data['valid_colors'] = colors[0]
        update.message.reply_text('موبایل مورد نظر شما پیدا شد:\n'+
                                  res.iloc[0]['name']+'\n'+
                                  'چه رنگی مد نظر شماست؟',
                                  reply_markup=ReplyKeyboardMarkup(colors, one_time_keyboard=True)
                                  )
        return COLOR
    else:
        update.message.reply_text('چه سایزی مد نظر شماست؟',
                                  reply_markup=ReplyKeyboardRemove())
        return SIZE

def color(bot, update, user_data):
    user = update.message.from_user
    logger.info("Color of %s: %s", user.first_name, update.message.text)
    user_data['color'] = update.message.text
    if user_data['color'] not in user_data['valid_colors']:
        update.message.reply_text('موبایل مورد نظر شما پیدا نشد. یه رنگ جدید از اونایی که بهت پیشنهاد دادم بهم بگو',
                                  )
        return COLOR

    res = find_mobiles(data=user_data)
    res = (res.to_dict('records')[0])
    ans = ''
    for key in res:
        if key not in ['Unnamed: 9', 'Conversion rate']:
            ans += key + ": " + str(res[key]) + '\n'
    update.message.reply_text('موبایل مورد نظر شما:\n'+
                              ans,
                              )
    return ConversationHandler.END

def size(bot, update, user_data):
    user = update.message.from_user
    logger.info("Size of %s: %s", user.first_name, update.message.text)
    inch = update.message.text

    if inch == '4':
        user_data['size'] = '4-5'
    elif inch == '5':
        user_data['size'] = '5-6'
    elif inch == '6':
        user_data['size'] = '6-8'
    elif inch == '8':
        user_data['size'] = '8-10'
    elif inch == '10':
        user_data['size'] = '10-100'
    res = find_mobiles(data=user_data)
    if len(res) == 0:
        update.message.reply_text('موبایل مورد نظر شما پیدا نشد. یه سایز جدید بهم بگو')
        return SIZE
    elif len(res) == 1:
        colors = res.iloc[0]['color']
        colors = [colors.replace(' ', '').split(',')]
        user_data['valid_colors'] = colors[0]
        update.message.reply_text('موبایل مورد نظر شما پیدا شد:\n'+
                                  res.iloc[0]['name']+'\n'+
                                  'چه رنگی مد نظر شماست؟',
                                  reply_markup=ReplyKeyboardMarkup(colors, one_time_keyboard=True)
                                  )
        return COLOR
    else:
        storages = set(list(res['storage']))
        storages = [(str(i) for i in storages)]
        update.message.reply_text('چه مقدار حافظه داخلی مد نظر شماست؟',
                                  reply_markup=ReplyKeyboardMarkup(storages, one_time_keyboard=True))
        return STORAGE

def storage(bot, update, user_data):
    user = update.message.from_user
    logger.info("Storage of %s: %s", user.first_name, update.message.text)
    user_data['storage'] = int(update.message.text)

    res = find_mobiles(data=user_data)
    if len(res) == 0:
        update.message.reply_text('موبایل مورد نظر شما پیدا نشد. یک حافظه‌ی مورد نظر جدید از اونایی که بهت پیشنهاد دادم بهم بگو.')
        return STORAGE
    elif len(res) == 1:
        colors = res.iloc[0]['color']
        colors = [colors.replace(' ', '').split(',')]
        user_data['valid_colors'] = colors[0]
        update.message.reply_text('موبایل مورد نظر شما پیدا شد:\n'+
                                  res.iloc[0]['name']+'\n'+
                                  'چه رنگی مد نظر شماست؟',
                                  reply_markup=ReplyKeyboardMarkup(colors, one_time_keyboard=True)
                                  )
        return COLOR
    else:
        names = [list(res['name'])]
        update.message.reply_text('گوشی مورد نظر خود را انتخاب کنید.',
                                  reply_markup=ReplyKeyboardMarkup(names, one_time_keyboard=True))
        return NAME

def name(bot, update, user_data):
    user = update.message.from_user
    logger.info("Name of %s: %s", user.first_name, update.message.text)
    user_data['name'] = update.message.text

    res = find_mobiles(data=user_data)
    if (len(res) == 0):
        update.message.reply_text('موبایل مورد نظر شما پیدا نشد. یک اسم جدید از اونایی که بهت پیشنهاد دادم بهم بگو.')
        return NAME
    colors = res.iloc[0]['color']
    colors = [colors.replace(' ', '').split(',')]
    user_data['valid_colors'] = colors[0]
    update.message.reply_text('موبایل مورد نظر شما پیدا شد:\n'+
                              res.iloc[0]['name']+'\n'+
                              'چه رنگی مد نظر شماست؟',
                              reply_markup=ReplyKeyboardMarkup(colors, one_time_keyboard=True)
                              )
    return COLOR


def cancel(bot, update):
    user = update.message.from_user
    logger.info("User %s canceled the conversation.", user.first_name)
    update.message.reply_text('تا دیدار بعدی :)',
                              reply_markup=ReplyKeyboardRemove())

    return ConversationHandler.END


def error(bot, update, error):
    """Log Errors caused by Updates."""
    logger.warning('Update "%s" caused error "%s"', update, error)


def main():

    request_kwargs = {'proxy_url':'socks5://localhost:9150/'}

    # Create the EventHandler and pass it your bot's token.
    updater = Updater("791720819:AAHV2QyuFOC3KQZQ0Mdfb3T6e4XFjE96Caw", request_kwargs=request_kwargs)

    # Get the dispatcher to register handlers
    dp = updater.dispatcher

    # Add conversation handler with the states GENDER, PHOTO, LOCATION and BIO
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            BRAND: [RegexHandler('^(سامسونگ|اپل|ال جی|گوگل|هواوی|اچ تی سی|نوکیا|شیائومی)$', brand, pass_user_data=True)],
            # BRAND: [MessageHandler(Filters.text, brand, pass_user_data=True)],

            PRICE: [MessageHandler(Filters.text, price, pass_user_data=True)],

            COLOR: [MessageHandler(Filters.text, color, pass_user_data=True)],

            SIZE: [MessageHandler(Filters.text, size, pass_user_data=True)],

            STORAGE: [MessageHandler(Filters.text, storage, pass_user_data=True)],

            NAME: [MessageHandler(Filters.text, name, pass_user_data=True)]
        },

        fallbacks=[CommandHandler('cancel', cancel)]
    )

    dp.add_handler(conv_handler)

    # log all errors
    dp.add_error_handler(error)

    # Start the Bot
    updater.start_polling()

    # Run the bot until you press Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()


if __name__ == '__main__':
    load_db('database.xlsx')
    main()
