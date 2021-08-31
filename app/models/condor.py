from datetime import date
from json import load, loads
from requests import request
from os import getcwd, path, getenv
from urllib3 import disable_warnings
from dotenv import dotenv_values, load_dotenv
from urllib3.exceptions import InsecureRequestWarning
disable_warnings(InsecureRequestWarning)


class Condor:

    def __init__(self):
        load_dotenv()

    @staticmethod
    def get_connect():
        headers = {'Content-Type': "application/x-www-form-urlencoded"}
        res = request("POST", getenv('CONDOR_URL_TOKEN'),
                      data=getenv('CONDOR_PAYLOAD'), headers=headers, verify=False)
        access = loads(res.text)
        return access['access_token']

    def get_departament_line(self, line):
        url = path.join(getenv('CONDOR_URL_PRODUCTS'), 'mercadologico', 'departamento')
        headers = {
            'Authorization': "Bearer %s" % self.get_connect(),
            'codLinha': "%s" % line,
        }
        res = request("GET", url, headers=headers, verify=False)
        return loads(res.text)

    def get_products(self, line):
        headers = {
            'Authorization': "Bearer %s" % self.get_connect(),
            'indSituacao': 'ATIVO',
            'codLinha': "%s" % line,
            'indTextoLegal': 'true',
            'indPrecoCargaPdv': 'true',
            'indMercadologicoWeb': 'true'
        }
        res = request("GET", getenv('CONDOR_URL_PRODUCTS'), headers=headers, verify=False)
        return loads(res.text)

    def get_products_line_department(self, line, department):
        headers = {
            'Authorization': "Bearer %s" % self.get_connect(),
            'indSituacao': 'ATIVO',
            'codLinha': '%s' % line,
            'codDepartamento': '%s'% department,
            'indTextoLegal': 'true',
            'indPrecoCargaPdv': 'true',
            'indMercadologicoWeb': 'true',
            'dtaReferencia': '%s' % date.today()
        }
        res = request("GET", getenv('CONDOR_URL_PRODUCTS'), headers=headers, verify=False)
        return loads(res.text)

    def get_product_detail(self, host):
        url = path.join(getenv('CONDOR_URL_PRODUCTS'), 'detalhada')
        headers = {
            'Authorization': "Bearer %s" % self.get_connect(),
            'indSituacao': 'ATIVO',
            'codProduto': "%s" % host
        }
        res = request("GET", url, headers=headers, verify=False)
        if res.status_code == 200:
            if len(res.text) > 2:
                return loads(res.text)[0]
            return False

    def get_image(self, code):
        url = path.join(getenv('CONDOR_URL_PRODUCTS'), 'imagem', str(code))
        headers = {'Authorization': "Bearer %s" % self.get_connect()}
        return request("GET", url, headers=headers)

    def get_campanhas(self, start=date.today(), end=date.today()):
        url = path.join(getenv('CONDOR_URL_CAMPANHA'), 'campanhas')
        headers = {
            'dta_vigencia_inicio': "%s" % start,
            'dta_vigencia_fim': "%s" % end,
            'ind_situacao_campanha': "CONVERTIDA",
            'Authorization': "Bearer %s" % self.get_connect()
        }
        res = request("GET", url, headers=headers, verify=False)
        return loads(res.text)

    def get_campanha_products(self, code):
        url = path.join(getenv('CONDOR_URL_CAMPANHA'), 'campanhas', 'detalhar', f"{code}")
        headers = {'Authorization': "Bearer %s" % self.get_connect()}
        res = request("GET", url, headers=headers, verify=False)
        return loads(res.text)
