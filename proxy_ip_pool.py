import logging
import requests
from bs4 import BeautifulSoup

usr_agt = 'User-Agent:Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Ubuntu Chromium/51.0.2704.79 Chrome/51.0.2704.79 Safari/537.36'
hdr = {}
hdr['User-Agent'] = usr_agt

xici = 'http://www.xicidaili.com/nn/1'

logging.basicConfig(level=logging.INFO, format=' %(asctime)s - %(levelname)s - %(message)s')

def get_bsobj(href):
    
    try:
        r = requests.get(url = href, headers=hdr)
        r.raise_for_status()
    except Exception as err:
        logging.critical('open %s failed, reason:%s' %(href, err))
        return None
    
    bsobj = BeautifulSoup(r.text, 'lxml')
    return bsobj

def parse_ip(obj):
    ip_list = []

    bsobj = obj

    for child in bsobj.find('table', {'id':'ip_list'}).children:
        if child == None:
            print('None child')
            continue
        else:
            print(child)
            print('child end..........................')
    #child.find()
    
    
    return ip_list


if __name__ == '__main__':

    obj = parse_ip(get_bsobj(xici))
    if obj == None:
        logging.info('bad obj')

    #logging.info('in main:%s' %obj)
