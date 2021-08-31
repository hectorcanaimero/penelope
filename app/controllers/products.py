from os import closerange, getcwd
from datetime import datetime
from os.path import join
from progressbar import ProgressBar

from app.models.condor import Condor
from app.models.imagem import Imagem
from app.controllers.utils import Utils
from app.models.mongo import MongoStore


class Products:
    def __init__(self):
        self.u = Utils()
        self.img = Imagem()
        self.condor = Condor()
        self.db = MongoStore()

    def initialize(self, line=1):
        self.u.color(f"[ADD][PRODUCT][LINE][{line}]", 'green')
        departments = self.condor.get_departament_line(line)
        for department in departments:
            products = self.condor.get_products_line_department(line, department['codDepto'])
            length = len(products)
            self.u.color(f"[LOADING PRODUCT][{length}][DEPARTMENT][{department['codDscDepto']}]", 'yellow')
            for product in products:
                data = self.u.remove_items_product(product)
                self._create_product(data, line)

    def _create_product(self, product, line):
        product['status'] = 0
        product['line'] = line
        product['created'] = datetime.now()
        slug = f"{product['nomProduto']} {product['codProduto']}"
        product['slug'] = self.u.slugy(slug)
        self.db.insert_collection('temp_products', product)

    def add_product_store(self, line):
        count = 0
        length = self.db.get_count('temp_products', {'line': line})
        products = self.db.get_find('temp_products', {'line': line})
        self.u.color(f"\n[ADD][STORES][PRODUCTS][LINE][{line}]", 'yellow')
        with ProgressBar(max_value=length) as bar:
            for i in range(length):
                for product in products:
                    count = count + 1
                    bar.update(count)
                    if 'lstMercadologicoWeb' in product:
                        if product['lstMercadologicoWeb'] is not None:
                            mw = product['lstMercadologicoWeb']
                            if 'lstPosicaoLojaCargaPdv' in product:
                                if product['lstPosicaoLojaCargaPdv'] is not None:
                                    for store in product['lstPosicaoLojaCargaPdv']:
                                        store['line'] = line
                                        store['product'] = product['_id']
                                        store['host'] = product['codProduto']
                                        store['mercadologicoWeb'] = mw
                                        self.db.insert_collection('temp_stores', store)
                        else:
                            self.reports(product, 'mw')
        remove_field = {'lstPosicaoLojaCargaPdv': "", 'dscComercial': "", 'dscFolheto': "", 'dscDetalheProduto': ""}
        self.db.remove_field_document('temp_products', remove_field)

    def add_product_image(self, line):
        count = 0
        lista = []
        self.u.color(f"\n[REMOVE][PRODUCT][WITHOUT][IMAGE][LINE][{line}]", 'yellow')
        path_public = join(getcwd(), 'public')
        products = self.db.get_find('temp_products', {'line': line})
        for product in products:
            lista.append(str(product['codProduto']))
        delete = self.u.compare(list(lista), line)
        count_del = len(delete)
        if count_del > 0:
            with ProgressBar(max_value=count_del) as bar:
                for i in range(count_del):
                    for res in delete:
                        count = i + 1
                        bar.update(count)
                        self.db.remove_many_collection('temp_products', {'codProduto': int(res)})
                        self.db.remove_many_collection('temp_stores', {'host': int(res)})

    def add_store_shop(self, line):
        count = 0
        self.u.color(f"\n[ADD][SHOP][TO][STORE][LINE][{line}]", 'yellow')
        shops = self.db.get_find('shops')
        length = self.db.get_count('shops')
        with ProgressBar(max_value=length) as bar:
            for i in range(length):
                for shop in shops:
                    count = count + 1
                    bar.update(count)
                    stores = self.db.get_find('temp_stores', {'codLoja': round(shop['code'])})
                    for store in stores:
                        id_store = store['_id']
                        store['shop'] = shop['_id']
                        items = store
                        del items['_id']
                        self.db.update_temp_stores(id_store, items)
        self.db.remove_many_collection('temp_stores', {'shop': {'$exists': False}, 'line': line})

    def reports(self, item, status):
        item['status'] = status
        self.db.insert_collection('reports', item)
        pass

    def add_campanha(self):
        campanhas = self.condor.get_campanhas()
        for campanha in campanhas:
            campanha['slug'] = self.u.time_campanha_slug(campanha['dta_vigencia_inicio'], campanha['dta_vigencia_fim'])
            self.db.insert_collection('temp_campanhas', campanha)

    def add_product_campanhas(self):
        campanhas = self.db.get_find('temp_campanhas')
        for campanha in campanhas:
            products = self.condor.get_campanha_products(str(campanha['cod_campanha']))
            if 'lst_produto' in products:
                for product in products['lst_produto']:
                    del product['lst_ean']
                    del product['lst_mix_lojas']
                    del product['mercadologico']
                    del product['embalagem_venda']
                    del product['lst_grupo_preco']
                    del product['lst_mercadologico_web']
                    product['cod_campanha'] = campanha['cod_campanha']
                    self.db.insert_collection('temp_campanha_product', product)
                    self.u.color(f"[{product['cod_campanha']}][{product['cod_produto']}][{product['nom_produto']}]",
                                 'green')
            # if 'lst_kit' in products:
            #     for kit in products['lst_kit']:
            #         self.db.insert_collection('temp_campanha_kit', kit)
            #         self.u.color(f"[{campanha['cod_campanha']}][{campanha['nom_campanha']}][{kit['cod_produto_kit']}]",
            #                      'cyan')

    def add_campanha_store(self, line):
        campanhas = self.db.get_find('temp_campanha_product')
        for campanha in campanhas:
            host = campanha['cod_produto']
            count_product = self.db.get_count('temp_products', {'codProduto': host})
            if count_product > 1:
                for region in campanha['lst_preco_regiao']:
                    for loja in region['lst_mix_regiao']:
                        store = self.db.get_find_one('temp_stores', {'host': host, 'codLoja': loja})
                        if store is not None:
                            self.evaluate_preco_campanha_store(store, region, campanha['cod_campanha'], campanha['_id'])

    def evaluate_preco_campanha_store(self, store, region, cod_campanha, id_campanha):
        id_store = store['_id']
        if 'vlr_preco_regular' in region and 'vlrPrecoRegular' in store:
            if region['vlr_preco_regular'] < store['vlrPrecoRegular']:
                store['cod_campanha'] = cod_campanha
                store['campanha'] = id_campanha
                store['vlrPrecoRegular'] = region['vlr_preco_regular']
        if 'vlr_preco_clube' in region and 'vlrPrecoClube' in store:
            if region['vlr_preco_clube'] < store['vlrPrecoClube']:
                if region['vlr_preco_clube'] > 0:
                    store['cod_campanha'] = cod_campanha
                    store['campanha'] = id_campanha
                    store['vlrPrecoClube'] = region['vlr_preco_clube']
        if region['vlr_cashback_clube'] is not None:
            store['vlr_cashback_clube'] = region['vlr_cashback_clube']
        del store['_id']
        self.db.update_temp_stores(id_store, store)

    def clean_temp_line(self, line):
        count = self.db.get_count('temp_products', {'line': line})
        if count > 1:
            self.db.remove_many_collection('temp_products', {'line': line})
            self.db.remove_many_collection('temp_stores', {'line': line})

    def table_production(self, line):
        print('#########   PRODUCTION   #######')
        stores = self.db.get_find('temp_stores', {'line': line})
        products = self.db.get_find('temp_products', {'line': line})
        count_temp_stores = self.db.get_count('temp_stores', {'line': line})
        count_temp_products = self.db.get_count('temp_products', {'line': line})
        if count_temp_products > 0:
            self.db.remove_many_collection('products', {'line': line})
            for product in products:
                del product['_id']
                del product['lstPosicaoLojaAtual']
                self.db.insert_collection('products', product)
        if count_temp_stores > 0:
            self.db.remove_many_collection('stores', {'line': line})
            for store in stores:
                self.db.insert_collection('stores', store)
        # self.db.rename('temp_products', 'products')
        # self.db.rename('temp_stores', 'stores')
