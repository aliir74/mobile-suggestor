import pandas as pd
db = 0

user_data = {}

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

START, BRAND, PRICE, COLOR, SIZE, STORAGE, NAME, END = range(8)
#brands = [['سامسونگ', 'اپل', 'ال جی', 'گوگل'],['هواوی', 'اچ تی سی', 'نوکیا', 'شیائومی']]

def start():
    print('سلام. من ربات تلگرام پیشنهاد دهنده‌ی موبایلم!\n'+
          'چه برند موبایلی مد نظرتونه؟')

    return BRAND

def brand():
    global user_data
    user_data = {}
    user_data['brand'] = input()
    print('حالا محدوده‌ی قیمتی که مد نظرته رو بهم بگو!')

    return PRICE


def price():
    global user_data
    message = input()
    milion = message.split()[0]

    if (message == 'زیر یک میلیون'):
        user_data['price'] = 0
    else:
        user_data['price'] = map_word_to_number(milion)*1000000

    res = find_mobiles(data=user_data)
    if len(res) == 0:
        print('موبایل مورد نظر شما پیدا نشد. یه محدوده‌ی قیمت جدید بهم بگو',
                                  )
        return PRICE
    elif len(res) == 1:
        colors = res.iloc[0]['color']
        colors = [colors.replace(' ', '').split(',')]
        user_data['valid_colors'] = colors[0]
        print('موبایل مورد نظر شما پیدا شد:\n'+
                                  res.iloc[0]['name']+'\n'+
                                  'چه رنگی مد نظر شماست؟'
                                  )
        return COLOR
    else:
        print('چه سایزی مد نظر شماست؟')
        return SIZE

def color():
    user_data['color'] = input()
    if user_data['color'] not in user_data['valid_colors']:
        print('موبایل مورد نظر شما پیدا نشد. یه رنگ جدید بهم بگو',
                                  )
        return COLOR

    res = find_mobiles(data=user_data)
    res = (res.to_dict('records')[0])
    ans = ''
    for key in res:
        if key not in ['Unnamed: 9', 'Conversion rate']:
            ans += key + ": " + str(res[key]) + '\n'
    print('موبایل مورد نظر شما:\n'+
                              ans,
                              )
    return END

def size():
    inch = input()

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
        print('موبایل مورد نظر شما پیدا نشد. یه سایز جدید بهم بگو')
        return SIZE
    elif len(res) == 1:
        colors = res.iloc[0]['color']
        colors = [colors.replace(' ', '').split(',')]
        user_data['valid_colors'] = colors[0]
        print('موبایل مورد نظر شما پیدا شد:\n'+
                                  res.iloc[0]['name']+'\n'+
                                  'چه رنگی مد نظر شماست؟'
                                  )
        return COLOR
    else:
        storages = set(list(res['storage']))
        storages = [(str(i) for i in storages)]
        print('چه مقدار حافظه داخلی مد نظر شماست؟')
        return STORAGE

def storage():
    user_data['storage'] = int(input())

    res = find_mobiles(data=user_data)
    if len(res) == 0:
        print('موبایل مورد نظر شما پیدا نشد. یک حافظه‌ی مورد نظر جدید بهم بگو.')
        return STORAGE
    elif len(res) == 1:
        colors = res.iloc[0]['color']
        colors = [colors.replace(' ', '').split(',')]
        user_data['valid_colors'] = colors[0]
        print('موبایل مورد نظر شما پیدا شد:\n'+
                                  res.iloc[0]['name']+'\n'+
                                  'چه رنگی مد نظر شماست؟'
                                  )
        return COLOR
    else:
        names = [list(res['name'])]
        print('گوشی مورد نظر خود را انتخاب کنید.')
        return NAME

def name():
    user_data['name'] = input()

    res = find_mobiles(data=user_data)
    if (len(res) == 0):
        print('موبایل مورد نظر شما پیدا نشد. یک اسم جدید از اونایی که بهت پیشنهاد دادم بهم بگو.')
        return NAME
    colors = res.iloc[0]['color']
    colors = [colors.replace(' ', '').split(',')]
    user_data['valid_colors'] = colors[0]
    print('موبایل مورد نظر شما پیدا شد:\n'+
                              res.iloc[0]['name']+'\n'+
                              'چه رنگی مد نظر شماست؟'
                              )
    return COLOR


def main():

    state = START
    while state < END:
        if state == START:
            state = start()
        elif state == BRAND:
            state = brand()
        elif state == PRICE:
            state = price()
        elif state == COLOR:
            state = color()
        elif state == SIZE:
            state = size()
        elif state == STORAGE:
            state = storage()
        elif state == NAME:
            state = name()
        elif state == END:
            break

if __name__ == '__main__':
    load_db('database.xlsx')
    main()
    print('BYE')
