import logging
import requests
import bs4
import pymysql 
from bs4 import BeautifulSoup

usr_agt = 'User-Agent:Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Ubuntu Chromium/51.0.2704.79 Chrome/51.0.2704.79 Safari/537.36'
hdr = {}
hdr['User-Agent'] = usr_agt

site_httpaddr = {}
site_httpaddr['xici'] = 'http://www.xicidaili.com/nn/1'
site_httpaddr['mimvp'] = 'http://proxy.mimvp.com/free.php?proxy=in_hp'
site_httpaddr['kuaidaili'] = 'http://www.kuaidaili.com/free/inha/1'
site_httpaddr['kxdaili'] = 'http://www.kxdaili.com/dailiip/1/1.html#ip'
site_nicklst = ['xici', 'mimvp', 'kuaidaili', 'kxdaili']

xici_body = 'http://www.xicidaili.com/nn/'


logging.basicConfig(level=logging.INFO, format=' %(asctime)s - %(levelname)s - %(message)s')

conn = pymysql.connections.Connection
cur = pymysql.cursors.Cursor

'''
    table columns:
    +----------+-------------+------+-----+---------+-------+
    | Field    | Type        | Null | Key | Default | Extra |
    +----------+-------------+------+-----+---------+-------+
    | ip       | varchar(15) | NO   |     | NULL    |       |
    | port     | varchar(5)  | NO   |     | NULL    |       |
    | country  | varchar(2)  | YES  |     | NULL    |       |
    | protocal | varchar(5)  | YES  |     | NULL    |       |
    +----------+-------------+------+-----+---------+-------+
'''
def db_conn():
    global conn
    global cur
    
    conn = pymysql.connect(host='localhost', user='rock', passwd='rock', db='proxydb', charset='utf8')
    cur = conn.cursor()

    cur.execute('select * from proxy')

'''
    Include update()&delete(), depend on sql sentence
'''
def db_update(sql):
#    sql_s = '\"' + sql + '\"'
    sql_s = sql
    sta = cur.execute(sql_s)
    conn.commit()
    return(sta)

def db_close():
    global conn
    global cur

    cur.close()
    conn.close()

def parse_xici_perpage(obj):
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
        sql = """INSERT INTO proxy (ip, port, country, protocal) VALUES ("%s", "%s", "%s", "%s")"""
        db_update(sql %(ip, port, "NULL", prot))
        print('ip:%s, port:%s, country:NULL, prot:%s' %(ip, port, prot))
   
    db_close()

def gen_xici_nextpage(order): 
    body = xici_body
    next_page_site = body + str(order)

    return next_page_site

def parse_xici_pages(page_num):
    for num in range(1, page_num):
        site = gen_xici_nextpage(num)
        bsobj = get_bsobj(site)
        parse_xici_perpage(bsobj)

'''def parse_kaixin(obj):
    bsobj = obj

    print('hello world')
'''
def parse_handler(site_nick, pages):
    if site_nick == 'xici':
        parse_xici_pages(pages)
'''    if site_nick == 'kxdaili':
        parse_kaixin(obj)
'''
def get_bsobj(site):
    
    try:
        r = requests.get(url = site, headers=hdr)
        r.raise_for_status()
    except Exception as err:
        logging.critical('open %s failed, reason:%s' %(href, err))
        return None
    
    bsobj = BeautifulSoup(r.text, 'lxml')
    return bsobj

if __name__ == '__main__':
   
    pages = 5

    for site in site_nicklst:
        parse_handler(site, pages)

    logging.info('end main')
