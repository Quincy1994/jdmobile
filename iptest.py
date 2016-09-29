# coding=utf-8
import urllib
import time
import signal


def getIP():

    f = open('ip.txt')
    lines = f.readlines()
    ip_list = []
    for line in lines:
        group = line.split('@')
        ip_list.append(group[0])
    return ip_list, lines


def ipIsInvalid(ip):
    def handler(signum, frame):
        raise AssertionError

    proxies = {}
    proxies['http'] = 'http://' + ip
    try:
        signal.signal(signal.SIGALRM, handler)
        signal.alarm(3)
        testUrl(proxies=proxies)
        signal.alarm(0)
        return True
    except AssertionError:
        # print "timeout"
        pass


def testUrl(proxies):
    try:
        filehandle = urllib.urlopen('http://so.m.jd.com/ware/searchList.action?_format_=json&stock=1&sort=&&page=1&keyword=面膜',proxies = proxies)
        filehandle.read()
    except:
        print 'refuse'
        pass

def main():
    ip_list,lines = getIP()
    active_ip = []
    areas = []
    for line in lines:
        group = line.split('@')
        ip = group[0]
        if ipIsInvalid(ip) is True:
            area = group[1]
            if area not in areas:
                areas.append(area)
                active_ip.append(line.strip())
                print line.strip()

if __name__ == '__main__':
    main()


