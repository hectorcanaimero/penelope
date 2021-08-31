from time import sleep
from threading import Thread
from datetime import datetime
from app.models.condor import Condor
from app.models.mongo import MongoStore
from app.controllers.utils import Utils
from app.controllers.images import Images
from app.controllers.products import Products

ut = Utils()
im = Images()
condor = Condor()
db = MongoStore()
product = Products()

store_thread = []
images_thread = []
number_threads = 4


def create_store(*args):
    line = int(args[0])
    page = int(args[1]) - 1
    per_page = int(args[2])
    acc = per_page * page
    acc2 = per_page * (page + 1)
    init = acc + 1
    if page == 0:
        acc2 = per_page
        init = 0
    items = db.get_find('temp_products', {'line': line})[init:acc2]
    count = 0
    for item in items:
        count = count + 1
        product.create_store_product(items, line, page)


def create_images(*args):
    count = 0
    for item in args[2]:
        count = count + 1
        im.download_image(item, args[0], args[1], count)


def store(line):
    ut.color(datetime.now(), 'red', 'on_cyan')
    total = db.get_count('temp_products', {'line': line})
    rest = total % number_threads
    count = (total // number_threads) + rest
    ut.color(f"[LINE][{line}][TOTAL][{total}][COUNT][{count}][REST][{rest}]", "red", "on_yellow")
    for i in range(number_threads):
        if i > 0:
            pass
            sleep(5)
        store_thread.append(Thread(target=create_store, args=(line, i + 1, count)))
        store_thread[-1].start()

    for i in range(number_threads):
        store_thread[i].join()
    ut.color(datetime.now(), 'red', 'on_yellow')


def images(line):
    products = condor.get_products(line)
    total = len(products)
    rest = total % number_threads
    count = total // number_threads
    ut.color(f"[IMAGES][LINE][{line}][TOTAL][{total}][COUNT][{count}][REST][{rest}]", 'cyan')
    for i in range(number_threads):
        ac = (count * i) + 1
        acc = count * (i + 1)
        if i == 0:
            ac = 0
        if i == 9:
            acc = acc + rest
        data = products[ac:acc]
        sleep(5)
        images_thread.append(Thread(target=create_images, args=(line, i+1, data)))
        images_thread[-1].start()
    for i in range(number_threads):
        images_thread[i].join()
    ut.color(datetime.now(), 'red', 'on_yellow')


def create_items(data):
    item = []
    x = number_threads
    for d in data:
        item.append(d)
    items = list(item)
    output = [items[i:i + x] for i in range(0, len(items), x)]
    return output
