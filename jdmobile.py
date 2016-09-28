# coding=utf-8
import chardet
import re
import urllib

import time
import urllib2
import xlwt


class JDMobile:

    def __init__(self, keyword):
        self.keyword = keyword

    def get_url(self, page):
        url = 'http://so.m.jd.com/ware/searchList.action?_format_=json&stock=1&sort=&&page=%s&keyword=%s'% (page, self.keyword)
        return url

    def get_wareList(self):
        wareList = list()
        page = 1
        while True:
            url = self.get_url(page)
            content = urllib.urlopen(url).read()
            content = content.replace('\n', '')
            wareList_content = self.match_wareList(content)
            if wareList_content is None or wareList.__len__() >= 2:
                break
            ware_ids = self.match_wareId(wareList_content)
            for id in ware_ids:
                wareList.append(id)
            page += 1
            time.sleep(3)

        return wareList

    def match_wareList(self,content):
        wareList_pattern = re.compile("\"wareList.*?:\[\{.*\}\]\}")
        wareList_content = wareList_pattern.findall(content)
        return wareList_content[0]

    def match_wareId(self, wareList_content):
        wareId_pattern = re.compile('wareId.*?:.*?(\d+)')
        ware_ids = wareId_pattern.findall(wareList_content)
        print ware_ids
        return ware_ids



class JDitem:

    @staticmethod
    def get_item_url(id):
        item_url = "http://item.jd.com/%s.html" % (id)
        return item_url

    @staticmethod
    def get_price(id):
        price_url = 'http://p.3.cn/prices/get?type=1&area=1_2802_2821&pdtk=&pduid=911197429&pdpin=PgMediacomBraun&pdbp=0&skuid=J_%s&callback=cnp' % (id)
        content = urllib.urlopen(price_url).read()
        price_pattern = re.compile("p\":\"(.*?)\"")
        price = price_pattern.findall(content)
        try:
            return price[0]
        except:
            return ''

    @staticmethod
    def get_static_parameter(id):
        item_url = 'http://item.jd.com/%s.html' % (id)
        data = (urllib2.urlopen(item_url)).read()
        charset = chardet.detect(data)
        code = charset['encoding']
        content = str(data).decode(code, 'ignore').encode('utf8')
        content = content.replace('\n', '')
        title_pattern = re.compile('<h1>(.*?)</h1>')
        group = title_pattern.findall(content)
        title = group[0]


        parameter_pattern = re.compile('<div class=\"p-parameter\".*?</div>')
        group = parameter_pattern.findall(content)
        p_parameter = group[0]
        li_pattern = re.compile("<li title=.*?/li>")
        parameter_list = li_pattern.findall(p_parameter)
        parameter_dict = {}
        for parameter in parameter_list:

            value_pattern = re.compile("<li title='(.*?)'")
            group = value_pattern.findall(parameter)
            value = group[0]

            key_pattern = re.compile("'>(.*?)：")
            group = key_pattern.findall(parameter)
            key = group[0]

            parameter_dict[key] = value

        return title, parameter_dict


    @staticmethod
    def get_subtitle_and_promotion(id):
        url = 'http://cd.jd.com/promotion/v2?callback=jQuery5780193&skuId='+id+'&area=1_2802_2821_0&shopId=1000002836&venderId=1000002836&cat=737%2C1276%2C739&_=1474185064703'
        data = (urllib2.urlopen(url)).read()
        charset = chardet.detect(data)
        code = charset['encoding']
        content = str(data).decode(code, 'ignore').encode('utf8')
        content = content.replace('\n', '')
        subtitle_pattern = re.compile("ad\":\"(.*?)\"")
        group = subtitle_pattern.findall(content)
        try:
            subtitle = group[0].replaceAll('<a>.*?</a>','')
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
        item_record.append(item[3])  # 价格
        item_record.append(item[4])  # 促销信息
        parameters = item[5]  # 添加属性
        for i in range(0, para_length, 1):
            if total_parameter_list[i] in parameters:
                key = total_parameter_list[i]
                item_record.append(parameters[key])
            else:
                item_record.append(' ')
        record_list.append(item_record)
        count += 1
    return record_list

def writeXls(record_list, total_parameter_list):
    print "正在写入excel表格中>>>"
    wbk = xlwt.Workbook(encoding='utf-8', style_compression=0)
    sheet = wbk.add_sheet('sheet 1', cell_overwrite_ok=True)
    sheet.write(0, 0, u'关键词')
    sheet.write(0, 1, u'排名')
    sheet.write(0, 2, u'商品url')
    sheet.write(0, 3, u'主标题')
    sheet.write(0, 4, u'副标题')
    sheet.write(0, 5, u'价格')
    sheet.write(0, 6, u'促销信息')
    for i in range(0, total_parameter_list.__len__(), 1):
        sheet.write(0, i+7, total_parameter_list[i])

    j = 1
    for record in record_list:
        for k in range(0, record.__len__(), 1):
            elememt = record[k]
            sheet.write(j, k, elememt)
        j += 1
    wbk.save('JDSearch.xls')
    print "xls数据写入完毕"

def main():
    keyword = '洗发水'
    jd = JDMobile(keyword=keyword)
    wareList = jd.get_wareList()
    total_parameter_list = list()
    total_item_list = list()
    for id in wareList:
        item_list = JDitem.get_itemInfo(id)
        total_item_list.append(item_list)
        item_parameters = item_list[5]
        time.sleep(3)
        for para in item_parameters:
            if para not in total_parameter_list:
                total_parameter_list.append(para)

    ## 将结果添加到记录当中
    record_list = write_record(keyword, total_item_list, total_parameter_list)
    writeXls(record_list=record_list, total_parameter_list=total_parameter_list)



if __name__ == '__main__':
    main()