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
#        sql = INSERT INTO 'proxy' VALUES ('+'\''+ip+'\''+', '+'\''+port+'\''+', '+'\''+'NULL'+'\''+', '+'\''+prot+'\''+')
        sql = 'INSERT INTO proxy VALUES (' + ip + ', ' + port + ', ' + 'NULL' + ', ' + prot + ')'
        db_update(sql)
   
    db_close()

def parse_kaixin(obj):
    bsobj = obj

    print('hello world')

def parse_site(obj, site_nick):
    if site_nick == 'xici':
        parse_xici(obj)
    if site_nick == 'kxdaili':
        parse_kaixin(obj)

def get_bsobj(site_nick):
    
    try:
        r = requests.get(url = site_httpaddr[site_nick], headers=hdr)
        r.raise_for_status()
    except Exception as err:
        logging.critical('open %s failed, reason:%s' %(href, err))
        return None
    
    bsobj = BeautifulSoup(r.text, 'lxml')
    return bsobj

if __name__ == '__main__':
    
    for site in site_nicklst:
        obj = get_bsobj(site)
        parse_site(obj, site)

    if obj == None:
        logging.info('bad obj')

    #logging.info('in main:%s' %obj)
