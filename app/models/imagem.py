from PIL import Image
from json import load
from shutil import rmtree
from datetime import datetime
from time import perf_counter, sleep
from os import path, getcwd, remove, listdir, mkdir

from .condor import Condor
from .mongo import MongoStore


class Imagem:
    path_public = path.join(getcwd(), 'public')

    def __init__(self):
        self.condor = Condor()
        self.db = MongoStore()

    def image(self, product):
        host = product['codProduto']
        path_image = path.join(self.path_public, 'image', f"{ str(host) }.jpg")
        imagem = self.condor.get_image(host)
        if imagem is not None:
            with open(path_image, 'wb') as f:
                f.write(imagem.content)
                sleep(1)
            if path.getsize(path_image) > 0:
                img = Image.open(path_image)
                if img.mode == "JPEG":
                    img_resize = img.resize((500, 500), Image.ANTIALIAS)
                    img_resize.save(path_image, 'JPEG', quality=60)
                elif img.mode in ["RGBA", "P"]:
                    img = img.convert("RGB")
                    img_resize = img.resize((500, 500), Image.ANTIALIAS)
                    img_resize.save(path_image, 'JPEG', quality=60)
                print(f"Imagem criada - HOST {host}")
                return True
            else:
                remove(path_image)
                product['status'] = 'sem_image'
                product['created'] = datetime.now()
                self.db.insert_collection('logs', product)
                self.db.delete_product(host)
                print(f"HOST: {host} - {product['nomProduto']}| Sem Imagem ")
                return False
