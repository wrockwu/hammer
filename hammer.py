import os
import requests
import bs4
import logging

def_url = 'http://www.xicidaili.com/nn/1'
usr_agt = 'User-Agent:Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Ubuntu Chromium/51.0.2704.79 Chrome/51.0.2704.79 Safari/537.36'

def_dirname = os.path.expanduser('~') + '/proxy'
def_proxyinfo = def_dirname + '/proxy_list.txt'
def_proxyavail = def_dirname + '/proxy_avail.txt'
def_log = def_dirname + '/proxy_log.txt'
proxy_url_test = 'http://www.baidu.com'

#must define hdr as a dictionary!!!
hdr = {}
hdr['User-Agent'] = usr_agt

logging.basicConfig(filename=def_log, level=logging.INFO, format=' %(asctime)s - %(levelname)s - %(message)s')

def html_download():

    soup = None

    try:
        res = requests.get(def_url, headers=hdr)
        res.raise_for_status()
    except Exception as err:
        logging.info('open url with a problem: %s' %(err))

    soup = bs4.BeautifulSoup(res.text, 'lxml')

    return soup

'''
    parse downloaded html page.
    should re-write this handler base on different proxy site.
'''
def html_parse(htm):
    elems = htm.select('tr > td')
    elems_len = len(elems)
    i = 1

    f = open(def_proxyinfo, 'w')

    if htm == None:
        logging.warning("Input param is None!!!")
        return

    while (i) < (elems_len):
        ip = elems[i].getText().strip()
        port = elems[i + 1].getText().strip()
        prot = elems[i + 4].getText().strip()

        proxy_info = prot + ' ' + ip + ' ' + port + '\n'
        f.write(proxy_info)
        i = i + 10

    f.close()

def proxy_assemble():
    proxys = []

    f = open(def_proxyinfo)
    lines = f.readlines()

    for i in range(0, len(lines)):
        ip = lines[i].strip('\n').split(' ')
        proxy_host = str(ip[0]).lower() +'://' + str(ip[1]) + ':'+ str(ip[2])
        proxy_temp = {'http':proxy_host}
        proxys.append(proxy_temp)

    return proxys

def proxy_available(proxys):

    if proxys == None:
        return

    #open this file with 'a' mode
    #so, if file exists we should delete it first
    if os.path.exists(def_proxyavail):
        os.remove(def_proxyavail)
    f = open(def_proxyavail, 'a')

    for proxy in proxys:
        try:
            res = requests.get(proxy_url_test, proxies=proxy, timeout=2)
            res.raise_for_status()
        except Exception as err:
            logging.info("Invaluable proxy ip: %s" %err)
            continue

        logging.info('Available proxy ip is: %s' %str(proxy['http']))
        f.write(str(proxy['http']) + '\n')
    f.close()

if __name__ == '__main__':

    logging.info("Hammer Start!")
    html = None
    proxys = []

    html = html_download()
    if html == None:
        logging.critical("Can't download html file!!!")
    html_parse(html)

    proxys = proxy_assemble()
    if proxys == None:
        logging.critical("Can't get proxys info")
    proxy_available(proxys)

    logging.info("Hammer End!")
    exit(0)
