import logging
import requests
import bs4
import pymysql 
from bs4 import BeautifulSoup
import sys, getopt

usr_agt = 'User-Agent:Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Ubuntu Chromium/51.0.2704.79 Chrome/51.0.2704.79 Safari/537.36'
hdr = {}
hdr['User-Agent'] = usr_agt

site_nicklst = ['xici', 'kx', 'kuai']

site_httpaddr = {}
site_httpaddr['xici'] = 'http://www.xicidaili.com/nn/1'
site_httpaddr['kx'] = 'http://www.kxdaili.com/dailiip/1/1.html#ip'
site_httpaddr['kuai'] = 'http://www.kuaidaili.com/free/inha/1'

'''
parse_dict = {}
parse_dict['xici'] = parse_xici
parse_dict['kx'] = parse_kx
parse_dict['kuai'] = parse_kuai
'''

pages_dict = {}
pages_dict['xici'] = 1
pages_dict['kx'] = 10
pages_dict['kuai'] = 10

xici_body = 'http://www.xicidaili.com/nn/'
kx_body = 'http://www.kxdaili.com/dailiip/1/'
kx_tail = '.html#ip'
kuai_body = 'http://www.kuaidaili.com/free/inha/'

logging.basicConfig(level=logging.INFO, format=' %(asctime)s - %(levelname)s - %(message)s')

conn = pymysql.connections.Connection
cur = pymysql.cursors.Cursor

'''
    SQL Sentence
'''
proxy_insert = """INSERT IGNORE INTO proxy (ip, port, country, protocal, disconntms) VALUES ('%s', '%s', '%s', '%s', %s)"""
proxy_querry = """SELECT ip, port, country, protocal, disconntms from proxy"""
#proxy_querry = """SELECT * FROM proxy"""
proxy_update = "UPDATE proxy set disconntms=%s WHERE ip='%s'"
proxy_del = """DELETE FROM proxy WHERE ip='%s'"""


'''
    show columns from database:
    +------------+-------------+------+-----+---------+-------+
    | Field      | Type        | Null | Key | Default | Extra |
    +------------+-------------+------+-----+---------+-------+
    | ip         | varchar(15) | NO   | PRI | NULL    |       |
    | port       | varchar(5)  | NO   |     | NULL    |       |
    | country    | varchar(2)  | YES  |     | NULL    |       |
    | protocal   | varchar(5)  | YES  |     | NULL    |       |
    | disconntms | int(1)      | NO   |     | NULL    |       |
    +------------+-------------+------+-----+---------+-------+
'''
def db_conn():
    global conn
    global cur
    conn = pymysql.connect(host='localhost', user='rock', passwd='rock', db='proxydb', charset='utf8')
    cur = conn.cursor()

'''
    Include insert()&update()&delete(), depend on sql sentence
'''
def db_update(sql, args):
    try:
        sta = cur.execute(sql, args)
    except Exception as err:
        logging.critical('db_update failed, reason:%s' %err)
    conn.commit()
    
    print("db_update status:%s" %(sta))
    return sta

'''
    database querry
'''
def db_querry(sql, args):
    if args is None:
        print('in None')
        cur.execute(sql)
    else:
        print('not in None')
        cur.execute(sql, args)

def db_close():
    global conn
    global cur
    cur.close()
    conn.close()

'''
    for www.xicidaili.com
'''
def parse_xici(obj):
    bsobj = obj

    db_conn()
    '''
        find ip_list in html
    '''
    bsobj = bsobj.find('table', {'id':'ip_list'})
    '''
        remove first tag, invalue data in this tag   
    '''
    bsobj.tr.decompose()
 
    for child in bsobj.find_all('tr'):
        '''
            ip
        '''
        ip = child.td.next_sibling.next_sibling.get_text()
        '''
            port
        '''
        port = child.td.next_sibling.next_sibling.next_sibling.next_sibling.get_text()
        '''
            protocal
        '''
        prot = child.td.next_sibling.next_sibling.next_sibling.next_sibling.next_sibling.\
                next_sibling.next_sibling.next_sibling.next_sibling.next_sibling.get_text()
        prot = prot.lower()
        
        '''
            insert sql sentence
        '''
        sql = proxy_insert
        db_update(sql, (ip, port, "NULL", prot, 0))
        print('ip:%s, port:%s, country:NULL, prot:%s, disconntms:0' %(ip, port, prot))
    db_close()

def parse_kx(obj):
    bsobj = obj
    
    db_conn()
    bsobj = bsobj.find('tbody')
    for child in bsobj.find_all('tr'):
        ip = child.td.get_text()
        port = child.td.next_sibling.next_sibling.get_text()
#        prot = child.td.next_sibling.next_sibling.next_sibling.next_sibling.next_sibling.next_sibling.get_text()
        '''
            set 'prot' to http manually 
        '''
        prot = 'http'
        sql = proxy_insert
        db_update(sql, (ip, port, "NULL", prot, 0))
        print('ip:%s, port:%s, country:NULL, prot:%s, disconntms:0' %(ip, port, prot))
    db_close()

def parse_kuai(obj):
    bsobj = obj
    
    db_conn()
    bsobj = bsobj.find('tbody')
    for child in bsobj.find_all('tr'):
        ip = child.td.get_text()
        port = child.td.next_sibling.next_sibling.get_text()
        '''
            set 'prot' to http manually 
        '''
        prot = 'http'
        sql = proxy_insert 
        db_update(sql, (ip, port, "NULL", prot, 0))
        print('ip:%s, port:%s, country:NULL, prot:%s, disconntms:0' %(ip, port, prot))
    db_close()

'''
    placed here to avoid warning. 
    i am python fresh man, is there a better way to deal with this problem? 
'''
parse_dict = {}
parse_dict['xici'] = parse_xici
parse_dict['kx'] = parse_kx
parse_dict['kuai'] = parse_kuai


def gen_newpage(order, site_n):
    if site_n == 'xici':
        body = xici_body
        tail = str(order)
    elif site_n == 'kx':
        body = kx_body
        tail = str(order) + kx_tail
    elif site_n == 'kuai':    
        body = kuai_body
        tail = str(order)
    
    page_site = body + tail
    print(page_site)
    return page_site

def parse_pages(page_num, site_n):
    for num in range(1, page_num+1):
        site = gen_newpage(num, site_n)
        bsobj = get_bsobj(site, None, None)
        parse_dict[site_n](bsobj)

def get_bsobj(site, proxies, timeout):
    
    try:
        r = requests.get(url=site, headers=hdr, proxies=proxies, timeout=timeout )
        r.raise_for_status()
    except Exception as err:
        logging.critical('open %s failed, reason:%s' %(site, err))
        return None
    
    bsobj = BeautifulSoup(r.text, 'lxml')
    return bsobj

def start_scrapy():
    for site in site_nicklst:
        parse_pages(pages_dict[site], site)
    
def start_check():
    proxies = {}
    sql = proxy_querry 
    db_conn()
    db_querry(sql, None)
    for each in cur:
        ip = each[0]
        port = each[1]
        disconntms = each[4]
        if disconntms > 3:
            db_update("UPDATE proxy set disconntms=%s", 1)
            print('unavailable ip:%s, delete it!' %(ip))
            continue

        site = 'http://' + ip + ':' + port
        proxies['http'] = site
        obj = get_bsobj('http://www.baidu.com', proxies, 3.05)
        if obj is None:
            sql = proxy_update
            tms = disconntms + 1
            #args = (tms, ip)
            #db_update("UPDATE proxy set disconntms=%s WHERE ip=%s", args)
            db_update("UPDATE proxy set disconntms=%s", 1)
    print("out check")
    db_close()

def test_api():
    bsobj = get_bsobj('http://www.kuaidaili.com/proxylist/1/')
    parse_kuai(bsobj)
    
config = {
            "db":"",        
        }

if __name__ == '__main__':
    opts, args = getopt.getopt(sys.argv[1:], 'hgctd:', ['help', 'get', 'check', 'test', 'db='])

    for op,va in opts:
        if op in ['-h', '--help']:
            print('help')
        elif op in ['-g', '--get']:
            start_scrapy()
        elif op in ['-c', '--check']:
            start_check()
        elif op in ['-t', '--test']:
            print('test api')

    #test_api()

    logging.info('end main')
