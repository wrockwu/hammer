import os
import requests
import bs4
import logging

def_url = 'http://www.xicidaili.com/nn/1'
head_url = 'http://www.xicidaili.com/nn/'
usr_agt = 'User-Agent:Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Ubuntu Chromium/51.0.2704.79 Chrome/51.0.2704.79 Safari/537.36'

def_dirname = os.path.expanduser('~') + '/proxy'
def_proxyinfo = def_dirname + '/proxy_list.txt'
def_proxyavail = def_dirname + '/proxy_avail.txt'
def_log = def_dirname + '/proxy_log.txt'
proxy_url_test = 'http://www.baidu.com'
def_pages = 5

#must define hdr as a dictionary!!!
hdr = {}
hdr['User-Agent'] = usr_agt

logging.basicConfig(level=logging.INFO, format=' %(asctime)s - %(levelname)s - %(message)s')

def hammer_init():

    if not os.path.exists(def_dirname):
        try:
            os.mkdir(def_dirname)
        except Exception as err:
            logging.critical('create proxy dir failed, reason:%s' %(err))

    if not os.path.exists(def_proxyinfo):
        try:
            f = open(def_proxyinfo, 'w')
        except Exception as err:
            logging.critical('create proxy_list file failed, reason: %s' %(err))
        f.close()

    if not os.path.exists(def_proxyavail):
        try:
            f = open(def_proxyavail, 'w')
        except Exception as err:
            logging.critical('create proxy_avail file failed, reason: %s' %(err))
        f.close()

    if os.path.exists(def_log):
        os.remove(def_log)

def html_perpage_download(url):

    soup = None

    if url == None:
        url = def_url

    try:
        res = requests.get(url, headers=hdr)
        res.raise_for_status()
    except Exception as err:
        logging.warning('open url with a problem: %s' %(err))

    soup = bs4.BeautifulSoup(res.text, 'lxml')

    return soup

'''
    generate or update proxy_list.txt file
'''
def proxy_list_gen(def_pages):

    html = None

    for i in range(1, def_pages):
        url = str(head_url) + str(i)
        logging.info('scrapy url: %s' %url)
        html = html_perpage_download(url)
        if html == None:
            logging.critical("Can't download url: %s!!!" %(url))
            continue
        html_parse(html)

def list_merge(old_list, new_list):

    logging.info('old list length: %s, new list length: %s' %(str(len(old_list)), str(len(new_list))))
    tmp_list = None

    if new_list == None:
        logging.critical('new list is None!!!')
        return

    if old_list == None:
        tmp_list = new_list
    else:
        tmp_list = list(set(old_list + new_list))

    return tmp_list

def list_store(s_list, path):

    logging.info('list length: %s' %(str(len(s_list))))

    try:
        f = open(path, 'w')
    except Exception as err:
        logging.critical('Open %s file failed, reason: %s' %(path, err))

    length = len(s_list)
    for i in range(0, length):
        f.write(s_list[i])
    f.close()

'''
    parse downloaded html page.
    should re-write this handler base on different proxy site.
'''
def html_parse(html):

    new_list = None
    old_list = None

    elems = html.select('tr > td')
    elems_len = len(elems)

    if html == None:
        logging.warning("Input param is None!!!")
        return

    try:
        f = open(def_proxyinfo, 'r')
        old_list = f.readlines()
    except Exception as err:
        logging.warning('Open proxy_list file warning, reason: %s' %(err))
    f.close()

    new_list = []
    i = 1
    while (i) < (elems_len):
        ip = elems[i].getText().strip()
        port = elems[i + 1].getText().strip()
        prot = elems[i + 4].getText().strip()
        proxy_info = prot + ' ' + ip + ' ' + port + '\n'
        new_list.append(proxy_info)
        i = i + 10

    s_list = list_merge(old_list, new_list)
    list_store(s_list, def_proxyinfo)

def proxy_assemble():
    proxys = []

    try:
        f = open(def_proxyinfo, 'r')
        lines = f.readlines()
    except Exception as err:
        logging.warning('Open proxy_list warning, reason: %s' %(err))
    f.close()

    for i in range(0, len(lines)):
        ip = lines[i].strip('\n').split(' ')
        proxy_host = str(ip[0]).lower() +'://' + str(ip[1]) + ':'+ str(ip[2])
        proxy_temp = {'http':proxy_host}
        proxys.append(proxy_temp)

    return proxys

def proxy_available(proxys):

    new_list = None
    old_list = None

    if proxys == None:
        return

    try:
        f = open(def_proxyavail, 'r')
        old_list = f.readlines()
    except Exception as err:
        logging.warning('proxy_avail file warning, reason: %s' %(err))
    f.close()

    new_list = []
    for proxy in proxys:
        try:
            res = requests.get(proxy_url_test, proxies=proxy, timeout=1)
            res.raise_for_status()
        except Exception as err:
            logging.debug("Invaluable proxy ip: %s" %err)
            continue
        logging.debug('Available proxy ip is: %s' %str(proxy['http']))
        new_list.append(str(proxy['http']) + '\n')

    s_list = list_merge(old_list, new_list)
    list_store(s_list, def_proxyavail)

'''
    update proxy_avail.txt file
'''
def proxy_avail_gen():

    proxy_list = None

    proxy_list = proxy_assemble()
    logging.info('proxy_list number: %s' %str(len(proxy_list)))
    if (proxy_list == None) or (proxy_list == []):
        logging.critical("Can't get proxys info")
        return None
    proxy_available(proxy_list)

if __name__ == '__main__':

    hammer_init()
    logging.info("Hammer Start!")

    proxy_list_gen(def_pages)
    proxy_avail_gen()

    logging.info("Hammer End!")
    exit(0)
