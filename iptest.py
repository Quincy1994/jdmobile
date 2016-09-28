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
        print "timeout"



def testUrl(proxies):
    try:
        filehandle = urllib.urlopen('http://www.baidu.com',proxies = proxies)
        filehandle.read()
    except:
        print 'refuse'

def main():
    ip_list,lines = getIP()
    for line in lines:
        group = line.split('@')
        ip = group[0]
        if ipIsInvalid(ip) is True:
            print line


if __name__ == '__main__':
    main()


