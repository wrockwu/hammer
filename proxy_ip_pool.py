import logging
import requests
import bs4
import pymysql 
from bs4 import BeautifulSoup

usr_agt = 'User-Agent:Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Ubuntu Chromium/51.0.2704.79 Chrome/51.0.2704.79 Safari/537.36'
hdr = {}
hdr['User-Agent'] = usr_agt

site_set = {}
site_set['xici'] = 'http://www.xicidaili.com/nn/1'

logging.basicConfig(level=logging.INFO, format=' %(asctime)s - %(levelname)s - %(message)s')

def parse_xici(url):

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
   
    '''
        find ip_list in html
    '''
    bsobj = bsobj.find('table', {'id':'ip_list'})
    '''
        remove first tag, invalue data in this tag   
    '''
    bsobj.tr.decompose()

    conn = pymysql.connect(host='localhost', user='rock', passwd='rock', db='proxydb', charset='utf8')
    cur = conn.cursor()
    cur.execute('select * from proxy')
    print('print data from database now..............')
    for each in cur:
        print(each[0].decode('utf-8'))
    cur.close()
    conn.close()

    for child in bsobj.find_all('tr'):
        '''
            ip
        '''
        print(child.td.next_sibling.next_sibling.get_text())
        '''
            port
        '''
        print(child.td.next_sibling.next_sibling.next_sibling.next_sibling.get_text())

    return ip_list


if __name__ == '__main__':

    obj = parse_ip(get_bsobj(site_set['xici']))
    if obj == None:
        logging.info('bad obj')

    #logging.info('in main:%s' %obj)
