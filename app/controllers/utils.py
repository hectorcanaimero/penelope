from re import sub
from PIL import Image
from datetime import date
from colorama import init
from termcolor import colored
from inspect import currentframe

from os import getcwd, walk, remove, listdir
from os.path import join, splitext, getsize, isfile


class Utils:

    @staticmethod
    def color(text, color=None, bg=None):
        init()
        print(colored(f" {text}  ", color, bg))

    @staticmethod
    def remove_items_product(item):
        if 'lstGrupoPreco' in item:
            del item['lstGrupoPreco']
        if 'lstPosicaoLoja' in item:
            del item['lstPosicaoLoja']
        if 'codReferenciaWikimee' in item:
            del item['codReferenciaWikimee']
        return item

    @staticmethod
    def covert_name_product(product):
        if 'nomProduto' in product:
            product['nomProduto'] = product['nomProduto']
        else:
            product['nomProduto'] = product['dscProduto']
        return product

    @staticmethod
    def slug_campanha(code):
        value = 'geral'
        if code.find('WHATSAPP') != -1:
            value = 'dia'
        elif code.find('RÁDIO E TV') != -1:
            value = 'dia'
        elif code.find('BOM DIA') != -1:
            value = 'dia'
        elif code.find('FIM') != -1:
            value = 'dia'
        elif code.find('R$ 0,99') != -1:
            value = 'dia'
        elif code.find('SEMANA MALUCA') != -1:
            value = 'semana'
        elif code.find('PAGUE MENOS COMPRANDO MAIS') != -1:
            value = 'semana'
        elif code.find('GOURMET') != -1:
            value = 'gourmet'
        return value

    @staticmethod
    def slug_data_expirada(item):
        delta = Utils.clean_data(item[4]) - Utils.clean_data(item[3])
        if item[2] == 'geral':
            if 2 >= delta.days:
                return item[0], item[1], 'dia', item[3], item[4]
            elif 2 < delta.days <= 7:
                return item[0], item[1], 'semana', item[3], item[4]
            else:
                return item
        else:
            return item

    @staticmethod
    def clean_data(data):
        data = data.split(' ')
        data = data[0]
        y, m, d = data.split('-')
        return date(int(y), int(m), int(d))

    @staticmethod
    def evaluate_price_product(one, two, campanha):
        two['campanha'] = campanha['_id']
        two['codeCampanha'] = campanha['cod_campanha']
        two['slug'] = campanha['slug']
        two['vlrCashbackClube'] = one['vlr_cashback_clube']
        if one['vlr_preco_regular'] < two['vlrPrecoRegular']:
            two['vlrPrecoRegular'] = one['vlr_preco_regular']
            two['vlrParcelaRegular'] = one['vlr_parcela_regular']
            two['qtdParcelaRegular'] = one['qtd_parcela_regular']
        if one['vlr_preco_clube'] > 0:
            if two['vlrPrecoClube'] is None:
                two['vlrPrecoClube'] = one['vlr_preco_clube']
                two['campanha'] = campanha['_id']
                two['codeCampanha'] = campanha['cod_campanha']
                two['slug'] = campanha['slug']
            if one['vlr_preco_clube'] < two['vlrPrecoClube']:
                two['vlrPrecoClube'] = one['vlr_preco_clube']
                two['campanha'] = campanha['_id']
                two['codeCampanha'] = campanha['cod_campanha']
                two['slug'] = campanha['slug']
            two['vlrParcelaClube'] = one['vlr_parcela_clube']
            two['qtdParcelaClube'] = one['qtd_parcela_clube']
        return two

    @staticmethod
    def remove_background(source, dist):
        img = Image.open(source)
        img = img.convert("RGBA")
        datas = img.getdata()
        print(datas)
        new_data = []
        for item in datas:
            if item[0] == 255 and item[1] == 255 and item[2] == 255:
                new_data.append((255, 255, 255, 0))
            else:
                new_data.append(item)

        img.putdata(new_data)
        img.save(dist, "PNG")
        print("Successful")

    @staticmethod
    def split_list(a_list, number):
        half = len(a_list) // number
        return a_list[:half], a_list[half:]

    @staticmethod
    def slugy(text):
        text = text.lower().strip()
        text = sub(r'[^\w\s-]', '', text)
        text = sub(r'[\s_-]+', '-', text)
        text = sub(r'^-+|-+$', '', text)
        return text

    @staticmethod
    def get_line_number():
        cf = currentframe()
        return cf.f_back.f_lineno

    @staticmethod
    def clean_date(data):
        data = data.split(' ')
        data = data[0]
        y, m, d = data.split('-')
        return date(int(y), int(m), int(d))

    @staticmethod
    def time_campanha_slug(start, end):
        delta = Utils.clean_date(end) - Utils.clean_date(start)
        if 2 >= delta.days:
            return 'dia'
        elif 2 < delta.days <= 7:
            return 'semana'
        else:
            return 'geral'

    @staticmethod
    def set_package(item):
        text = item['dscUnidadeVenda']
        if text is not None:
            if text == "Quilo":
                return "kg"
            elif text == "Cada":
                return "Cada"
        return text

    @staticmethod
    def evaluate_preco_campanha_store(store, region, code):
        if 'vlr_preco_regular' in region and 'vlrPrecoRegular' in store:
            if region['vlr_preco_regular'] < store['vlrPrecoRegular']:
                Utils.color(f"[REGULAR][{code}][{store['host']}][{store['codLoja']}][{store['vlrPrecoRegular']}]"
                            f"[{region['vlr_preco_regular']}]", "cyan")
                store['campanha'] = code
                store['vlrPrecoRegular'] = region['vlr_preco_regular']
        if 'vlr_preco_clube' in region and 'vlrPrecoClube' in store:
            if region['vlr_preco_clube'] < store['vlrPrecoClube']:
                Utils.color(f"[CLUBE][{code}][{store['host']}][{store['codLoja']}][{store['vlrPrecoClube']}]"
                            f"[{region['vlr_preco_clube']}]", "yellow")
                store['campanha'] = code
                store['vlrPrecoClube'] = region['vlr_preco_clube']
        return store

    @staticmethod
    def compare(products, line):
        image = []
        path_image = join(getcwd(), 'public', 'image', f"{line}")
        files = [f for f in listdir(path_image) if isfile(join(path_image, f))]
        for file in files:
            x, y = splitext(file)
            image.append(x)
        image = list(image)
        diff = [item for item in products if item not in image]
        return diff