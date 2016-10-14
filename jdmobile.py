# coding=utf-8
import chardet
import re
import urllib

import time
import urllib2
import xlwt

from selenium import webdriver

proxies = {}  ## 加入代理ip的字典


"""商品属性"""
total_parameters = [u'搜索关键词',u'商品坑位排名',u'商品Url',u'商品主标题',u'商品副标题',u'商品价格',u'商品促销信息',u'商品名称',u'商品编号',u'品牌',u'店铺',u'商品毛重',u'商品产地',u'货号',u'适合肤质',u'功效',u'产品产地',u'性别',u'分类',u'类型',u'面贴膜数量']


class JDMobile:

    def __init__(self, keyword):
        self.keyword = keyword


    def get_url(self, page ,type):
        ## 模拟手机滑动,查看列表, 主要参数是sort, sort=0为综合排序, sort=1为销量排序
        url = 'http://so.m.jd.com/ware/searchList.action?_format_=json&stock=1&sort=%s&&page=%s&keyword=%s'% (page, type, self.keyword)
        return url

    def get_wareList(self, type):

        """获取商品排名列表"""

        wareList = list()
        page = 1
        item_num = 2000  ## 要获取的目标数量
        while True:
            url = self.get_url(page, type)
            print proxies
            content = urllib.urlopen(url, proxies=proxies).read()
            content = content.replace('\n', '')
            wareList_content = self.match_wareList(content)
            if wareList_content is None or wareList.__len__() >= item_num:
                break
            ware_ids = self.match_wareId(wareList_content)
            for id in ware_ids:
                wareList.append(id)
            page += 1
            # time.sleep(1)
        print 'len:', wareList.__len__()

        return wareList


    def match_wareList(self,content):

        """匹配商品坑位列表"""
        wareList_pattern = re.compile("\"wareList.*?:\[\{.*\}\]\}")
        wareList_content = wareList_pattern.findall(content)
        return wareList_content[0]

    def match_wareId(self, wareList_content):

        """在商品坑位列表，匹配商品的id"""
        wareId_pattern = re.compile('wareId.*?:.*?(\d+)')
        ware_ids = wareId_pattern.findall(wareList_content)
        print ware_ids
        return ware_ids



class JDitem:

    @staticmethod
    def get_item_url(id):

        """获取商品的详情页"""
        item_url = "http://item.jd.com/%s.html" % (id)
        return item_url



    @staticmethod
    def get_price(id):

        """获取商品的价格"""
        price_url = 'http://item.m.jd.com/product/%s.html' %(id)
        content = urllib.urlopen(price_url).read().replace("\n","")
        price_pattern = re.compile("<input type=\"hidden\" id=\"jdPrice\" name=\"jdPrice\" value=\"(.*?)\"/>")
        price = price_pattern.findall(content)
        if len(price) == 0:     ##出现全球购的情况
            price_url = 'http://mitem.jd.hk/product/1963190765.html'
            browser = webdriver.PhantomJS()
            browser.get(price_url)
            content = browser.page_source
            price_pattern = re.compile("<span class=\"big-price\">(.*?)</span>")
            price = price_pattern.findall(content)

        try:
            return price[0]
        except:
            return ''

    @staticmethod
    def get_static_parameter(id):

        """获取商品的静态属性"""
        title = ''
        parameter_dict = {}
        try:
            item_url = 'http://item.jd.com/%s.html' % (id)
            data = (urllib2.urlopen(item_url)).read()
            charset = chardet.detect(data)
            code = charset['encoding']
            content = str(data).decode(code, 'ignore').encode('utf8')
            content = content.replace('\n', '')
            title_pattern = re.compile('<h1>(.*?)</h1>')
            group = title_pattern.findall(content)
            title = group[0].replace(" ","")


            parameter_pattern = re.compile('<div class=\"p-parameter\".*?</div>')
            group = parameter_pattern.findall(content)
            parameter_dict = {}
            if len(group) == 0 :
                parameter_pattern = re.compile('<div class=\"parameter-content\".*?</div>')
                group = parameter_pattern.findall(content)
                p_parameter = group[0]
            else:
                p_parameter = group[0]
            li_pattern = re.compile("<li title=.*?/li>")
            parameter_list = li_pattern.findall(p_parameter)
            for parameter in parameter_list:

                value_pattern = re.compile("<li title='(.*?)'")
                group = value_pattern.findall(parameter)
                value = group[0].decode('utf8')

                key_pattern = re.compile("'>(.*?)：")
                group = key_pattern.findall(parameter)
                key = group[0].decode('utf8')


                parameter_dict[key] = value

        except:
            print 'bug in p_parameter'
        return title, parameter_dict


    @staticmethod
    def get_subtitle_and_promotion(id):

        """获取副标题和促销信息"""
        url = 'http://cd.jd.com/promotion/v2?callback=jQuery5780193&skuId='+id+'&area=1_2802_2821_0&shopId=1000002836&venderId=1000002836&cat=737%2C1276%2C739&_=1474185064703'
        data = (urllib2.urlopen(url)).read()

        charset = chardet.detect(data)
        code = charset['encoding']
        content = str(data).decode(code, 'ignore').encode('utf8')
        content = content.replace('\n', '')
        subtitle_pattern = re.compile("ad\":\"(.*?)\"}]")
        group = subtitle_pattern.findall(content)

        try:
            subtitle = group[0]
        except:
            subtitle = ''

        promotion_pattern = re.compile("content\":\"(.*?)\"")
        group = promotion_pattern.findall(content)
        try:
            promotion = group[0]
        except:
            promotion = ''
        return subtitle, promotion

    @staticmethod
    def get_itemInfo(id):

        """获取商品的具体属性"""
        title , parameter_dict = JDitem.get_static_parameter(id)
        subtitle, promotion = JDitem.get_subtitle_and_promotion(id)
        price = JDitem.get_price(id)
        url = JDitem.get_item_url(id)
        print '----------------'
        print 'title', title
        print 'subtitle', subtitle
        print 'promotion', promotion
        print 'price', price
        print 'url', url
        print 'parameter_dict'
        for key in parameter_dict:
            print key, ":", parameter_dict[key]
        item_list = []
        item_list.append(url)   # 添加url信息 0
        item_list.append(title)  # 添加主标题 1
        item_list.append(subtitle)  # 添加副标题 2
        item_list.append(price)  # 添加价格 3
        item_list.append(promotion) # 添加促销信息 4
        item_list.append(parameter_dict) # 添加静态属性 5

        return item_list

def write_record(keyword, total_item_list, total_parameter_list):

    """将每一项数据记录到一个列表中"""
    record_list = []
    count = 1
    for item in total_item_list:
        item_record = []
        para_length = total_parameter_list.__len__()
        item_record.append(keyword)  # 关键词
        item_record.append(str(count))  # 排名
        item_record.append(item[0])  # url
        item_record.append(item[1])  # 主标题
        item_record.append(item[2])  # 副标题
        item_record.append(item[3])  # 商品价格
        item_record.append(item[4])  # 商品促销信息
        parameters = item[5]  # 添加属性
        print parameters
        for i in range(7, len(total_parameters), 1):
            if total_parameters[i] in parameters:
                key = total_parameters[i]
                item_record.append(parameters.get(key))
            else:
                item_record.append(' ')
        record_list.append(item_record)
        count += 1
    return record_list

def writeXls(area, record_list, total_parameter_list):

    print "正在写入excel表格中>>>"
    wbk = xlwt.Workbook(encoding='utf-8', style_compression=0)
    sheet = wbk.add_sheet('sheet 1', cell_overwrite_ok=True)
    for i in range(0, len(total_parameters), 1):
        sheet.write(0, i, total_parameters[i])

    j = 1
    for record in record_list:
        for k in range(0, record.__len__(), 1):
            elememt = record[k]
            sheet.write(j, k, elememt)
        j += 1
    wbk.save(area + 'jd.xls')
    print "xls数据写入完毕"

def main(area, type):

    keyword = '面膜'  # 搜索关键词
    jd = JDMobile(keyword=keyword)  # 获取搜索坑位排序
    wareList = jd.get_wareList(type)
    total_parameter_list = list()
    total_item_list = list()
    for id in wareList:
        item_list = JDitem.get_itemInfo(id)
        total_item_list.append(item_list)
        item_parameters = item_list[5]
        # time.sleep(1)
        for para in item_parameters:
            if para not in total_parameter_list:
                total_parameter_list.append(para)

    ## 将结果添加到记录当中
    record_list = write_record(keyword, total_item_list, total_parameter_list)
    writeXls(area,record_list=record_list, total_parameter_list=total_parameter_list)

def readIP():

    """读取ip列表"""
    ip_list = []
    filename = 'activeip.txt'
    lines = open(filename).readlines()
    for line in lines:
        ip_list.append(line.strip())
    return ip_list

if __name__ == '__main__':
    while(True):
        if 'tm_hour=15' in str(time.localtime()):
            start_time = time.time()
            ip_list = readIP()  ## 读取ip任务列表

            for info in ip_list:
                print info
                group = info.split('@')
                ip = group[0]   # 代理ip或ip
                area = group[1] # 地区
                type = group[2] # 类型，类型0为综合,1为销量
                if ip == 'None':
                    proxies = None
                else:
                    proxies['http'] = 'http://' + ip
                ISOTIMEFORMAT = "%Y%m%d"  # 写入获取的时间
                nowdate = time.strftime(ISOTIMEFORMAT, time.localtime())
                main(area+nowdate,type)

            end_time = time.time()
            print end_time - start_time
        else:
            print 'sleeping'
            time.sleep(3)
