from PIL import Image
from datetime import datetime
from inspect import currentframe
from shutil import copyfile, rmtree, move
from pysftp import CnOpts, Connection
from os.path import join, getsize, isfile, isdir, splitext
from os import getcwd, getenv, mkdir, listdir, remove, rename

from app.models.condor import Condor
from app.models.imagem import Imagem
from app.controllers.utils import Utils
from app.models.mongo import MongoStore


class Images:

    def __init__(self):
        self.u = Utils()
        self.img = Imagem()
        self.condor = Condor()
        self.db = MongoStore()
        self.public = join(getcwd(), 'public')

    def initialize(self, line):
        count = 0
        path_line = join(self.public, 'temp', f"temp-{line}")
        self.is_file(path_line)
        departments = self.condor.get_departament_line(line)
        for department in departments:
            products = self.condor.get_products_line_department(line, department['codDepto'])
            self.u.color(f"[LOADING][LINE][{line}][DEPARTMENT][{department['codDscDepto']}][TOTAL][{len(products)}]")
            for item in products:
                count = count + 1
                # self.download_image(item, line, count)

    def download_image(self, item, line, count):
        host = item['codProduto']
        path_image = join(self.public, 'image', f"{line}",f"{host}.png")
        temp_path = join(self.public, 'temp', f"temp-{line}")
        if isfile(path_image) is not True:
            image = self.condor.get_image(host)
            if image is not None:
                with open(path_image, 'wb') as f:
                    f.write(image.content)
                if getsize(path_image) > 0:
                    original = round(getsize(path_image)/1024, 2)
                    img = Image.open(path_image)
                    img = img.convert("RGBA")
                    img_resize = img.resize((500, 500), Image.ANTIALIAS)
                    img_resize.save(path_image, 'PNG', optimize=True, quality=50)
                    optimize = round(getsize(path_image)/1024, 2)
                    copyfile(path_image, join(temp_path, f"{host}.jpg"))
                    self.u.color(f"[{line}][{count}][{host}][Image was created!][{original}kb][{optimize}kb]", 'green')
                else:
                    remove(path_image)
                    item['status'] = 'sem_image'
                    item['created'] = datetime.now()
                    self.db.insert_collection('logs', item)
                    self.db.remove_product(host)
                    self.u.color(f"[{line}][{count}][{host}][Image was not created]", 'red')
        else:
            self.u.color(f"[{line}][{count}][{host}][Image in the database!]", 'green')

    def move_folder(self, item, line, count):
        host = item['codProduto']
        path_old = join(self.public, 'image',f"{host}.png")
        path_new = join(self.public, 'image', f"{line}",f"{host}.png")
        if isfile(path_old) is True:
            move(path_old, path_new)

    def move_image(self, line):
        path_image = join(self.public, 'image', f"{line}")
        path_new_img = join(self.public, 'temp',f"temp-{line}")
        for item in listdir(path_image):
            print(item)
            x, y = splitext(item)
            is_file = isfile(join(path_new_img, f"{x}.jpg"))
            print(is_file)
            if is_file is not True:
                image = join(path_new_img, f"{x}.jpg")
                print(image)
                Image.open(join(path_image, item)).convert('RGB').resize((500, 500), Image.ANTIALIAS).save(image)

    def delete_product(self, line):
        products = self.db.get_find('temp_products', {'line': line})
        for product in products:
            host = product['codProduto']
            image = join(self.public, "image", f"{host}.png")
            if isfile(image) is not True:
                self.db.remove('temp_products', {'codProduto': host})
                self.u.color(f"[{line}][{host}][Product was deleted]", 'red')

    def upload(self, line):
        cnopts = CnOpts()
        cnopts.hostkeys = None
        temp_path = join(self.public, 'temp', f"temp-{line}")
        directory = listdir(temp_path)
        server = Connection(getenv('FTP_HOST'), username=getenv('FTP_USER'), password=getenv('FTP_PASS'),
                            port=int(getenv('FTP_PORT')), cnopts=cnopts)
        server.cwd(getenv('FTP_FOLDER'))
        for item in directory:
            file_image = join(temp_path, item)
            server.put(file_image)
            server.chmod(item, 755)
            self.u.color(f'[Server][{ item }][was uploaded]', 'green')
            remove(join(temp_path, item))
        rmtree(temp_path)
        server.close()

    @staticmethod
    def is_file(path):
        if isdir(path):
            rmtree(path)
        return mkdir(path)
