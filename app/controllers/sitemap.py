from slug import slug
from os import getcwd
from os.path import join
import xml.etree.cElementTree as ET
from datetime import datetime

from app.models.mongo import MongoStore


class Sitemap:

    def __init__(self):
        self.db = MongoStore()

    def generate(self):
        domain = 'https://www.condor.com.br/produto'
        dt = datetime.now().strftime("%Y-%m-%d")
        root = ET.Element("urlset")
        root.attrib['xmlns'] = "http://www.sitemaps.org/schemas/sitemap/0.9"
        tree = ET.ElementTree(root)
        products = self.db.get_find('products')
        for item in products:
            url = ''
            if 'lstMercadologicoWeb' in item:
                if item['lstMercadologicoWeb']['setor'] is not None:
                    departament = item['lstMercadologicoWeb']['departamento']['dscMercadologico']
                    sector = item['lstMercadologicoWeb']['setor']['dscMercadologico']
                    url = join(domain, slug(departament), slug(sector),
                               f"{slug(item['nomProduto'])}-{item['codProduto']}")
            doc = ET.SubElement(root, "url")
            ET.SubElement(doc, "loc").text = url
            ET.SubElement(doc, "lastmod").text = dt
            ET.SubElement(doc, "changefreq").text = 'daily'
            ET.SubElement(doc, "priority").text = "0.6"
        tree.write(join(getcwd(), "public", "sitemap", "sitemap.xml"), encoding='utf-8', xml_declaration=True)
