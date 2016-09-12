import os
import requests
import bs4
import logging

def_url = 'http://www.xicidaili.com/nn/1'
head_url = 'http://www.xicidaili.com/nn/'
usr_agt = 'User-Agent:Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Ubuntu Chromium/51.0.2704.79 Chrome/51.0.2704.79 Safari/537.36'

def_dirname = os.path.expanduser('~') + '/proxy'
def_proxyip = def_dirname + '/proxy_ip.txt'
def_proxyhttp = def_dirname + '/proxy_http.txt'
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

    if not os.path.exists(def_proxyip):
        try:
            f = open(def_proxyip, 'w')
        except Exception as err:
            logging.critical('create proxy_list file failed, reason: %s' %(err))
        f.close()

    if not os.path.exists(def_proxyhttp):
        try:
            f = open(def_proxyhttp, 'w')
        except Exception as err:
            logging.critical('create proxy_avail file failed, reason: %s' %(err))
        f.close()

    if os.path.exists(def_log):
        os.remove(def_log)

def getlist_from_file(path):

    try:
        f = open(path, 'r')
        f_list = f.readlines()
    except Exception as err:
        logging.warning('open proxy_list file warning, reason: %s' %(err))
    f.close()

    return f_list

def list_file_diff(list_in, path):

    old_list = []
    old_list = getlist_from_file(path)

    if (list_in == []):
        logging.warning('list_in is None!!!')
        list_out = old_list
        return list_out

    if old_list == []:
        logging.warning('old list is None!!!')
        list_out = list_in
    else:
        list_out = list(set(list_in) - set(old_list))

    logging.info('list diff length: %s' %(str(len(list_out))))
    return list_out

def list_file_intersec(list_in, path):

    old_list = []
    old_list = getlist_from_file(path)

    if (list_in == []):
        logging.warning('list_in is None!!!')
        return list_in

    if old_list == []:
        logging.warning('old list is None!!!')
        return old_list
    else:
        list_out = list(set(list_in) & set(old_list))

    logging.info('list diff length: %s' %(str(len(list_out))))
    return list_out

def list_file_union(list_in, path):

    old_list = []
    old_list = getlist_from_file(path)

    if (list_in == []):
        logging.warning('list_in is None!!!')
        return list_in

    if old_list == []:
        logging.warning('old list is None!!!')
        return old_list
    else:
        list_out = list(set(list_in) | set(old_list))

    logging.info('list diff length: %s' %(str(len(list_out))))
    return list_out

def list_store2file(list_in, path, mode):

    logging.info('list need to store, length: %s' %(str(len(list_in))))

    try:
        f = open(path, mode)
    except Exception as err:
        logging.critical('open %s file failed, reason: %s' %(path, err))

    length = len(list_in)
    for i in range(0, length):
        f.write(list_in[i])
    f.close()

def gethtml_from_url(url):

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
    parse downloaded html page.
    should re-write this handler base on different proxy site.
'''
def getlist_from_html(html):

    elems = html.select('tr > td')
    elems_len = len(elems)

    if html == None:
        logging.warning("input param is None!!!")
        return

    new_list = []
    i = 1
    while (i) < (elems_len):
        ip = elems[i].getText().strip()
        port = elems[i + 1].getText().strip()
        prot = elems[i + 4].getText().strip()
        proxy_info = prot + ' ' + ip + ' ' + port + '\n'
        new_list.append(proxy_info)
        i = i + 10

    return new_list

def iplist_to_dict(ip_list):

    proxy_dict = []

    for i in range(0, len(ip_list)):
        ip = ip_list[i].strip('\n').split(' ')
        proxy_host = str(ip[0]).lower() +'://' + str(ip[1]) + ':'+ str(ip[2])
        proxy_temp = {'http':proxy_host}
        proxy_dict.append(proxy_temp)

    return proxy_dict

def httplist_to_dict(http_list):

    proxy_dict = []

    for i in range(0, len(http_list)):
        ip = http_list[i].strip('\n')
        proxy_host = ip
        proxy_temp = {'http':proxy_host}
        proxy_dict.append(proxy_temp)

    return proxy_dict

def proxy_available(proxys):

    tmp_list = []

    if proxys == []:
        return tmp_list

    tmp_list = []
    for proxy in proxys:
        try:
            res = requests.get(proxy_url_test, proxies=proxy, timeout=0.5)
            res.raise_for_status()
        except Exception as err:
            logging.info("invaluable proxy ip: %s" %err)
            continue
        logging.debug('available proxy ip is: %s' %str(proxy['http']))
        tmp_list.append(str(proxy['http']) + '\n')

    return tmp_list

'''
    generate or update proxy_list.txt file
'''
def proxylist_file_gen():

    html = None
    tmp_list = []

    for i in range(1, def_pages):
        url = str(head_url) + str(i)
        logging.info('scrapy url: %s' %url)
        html = gethtml_from_url(url)
        if html == None:
            logging.critical("can't download url: %s!!!" %(url))
            continue
        tmp_list = tmp_list + getlist_from_html(html)

    ip_list = list_file_diff(tmp_list, def_proxyip)
    http_list = iplist_to_dict(ip_list)
    tmp_list = proxy_available(http_list)

#    http_list = getlist_from_file(def_proxyhttp)
#    http_list = httplist_to_dict(http_list)
#    tmp_list = tmp_list + proxy_available(http_list)

    list_store2file(ip_list, def_proxyip, 'w')
    list_store2file(list(set(tmp_list)), def_proxyhttp, 'w')

if __name__ == '__main__':

    hammer_init()
    logging.info("Hammer Start!")

    proxylist_file_gen()

    logging.info("Hammer End!")
    exit(0)
