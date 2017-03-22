#! coding:utf-8
import requests
import sys
from bs4 import BeautifulSoup
import csv
import urllib
import json
import time,datetime
import re
#from adsl import Adsl
import codecs

global writer

def data_Crawling(url):
    s = requests.Session()
    try:
        resp = s.post(url,timeout=60)
        return resp._content
    except requests.exceptions.ReadTimeout:
       print 'requests.exceptions.ReadTimeout'
    except requests.exceptions.ConnectionError:
        print 'requests.exceptions.ConnectionError'

def UDencode(str):
    return eval("u'"+str+"'").encode('utf-8')

#学校信息提取
def schoolinfos(datas):
    flag = False
    for data in datas:
        if flag == False:#第一行不解析
            flag=True
            continue
        #从第二开始数据抽取
        schooldatas = re.findall(r'<td .*?>(.*?)</td>',str(data),re.S|re.M)
        schooolname = re.findall(r'<a .*?>(.*?)</a>',str(schooldatas[0]),re.S|re.M)[0]
        schooolnameurl = "http://yz.chsi.com.cn"+re.findall(r'(?<=href=\").+?(?=\")|(?<=href=\').+?(?=\')',str(schooldatas[0]),re.S|re.M)[0].replace("amp;","")
        address = schooldatas[1]
        schooltype = str(re.findall(r'<span .*?>(.*?)</span>',str(schooldatas[2]),re.S|re.M)).\
            replace("['","").replace("']","").replace("', '",";").replace("[","").replace("]","")

        if schooldatas[3] == "√":
            schooldatas[3] = "是"
        else:
            schooldatas[3] = ""
        if schooldatas[4] == "√":
            schooldatas[4] = "是"
        else:
            schooldatas[4] = ""
        if schooldatas[5] == "√":
            schooldatas[5] = "是"
        else:
            schooldatas[5] = ""
        schoolinfo = UDencode(schooolname)+","+UDencode(address)+","+schooltype+","+UDencode(schooldatas[3])+","+UDencode(schooldatas[4])+","+UDencode(schooldatas[5])
        professes = page(schooolnameurl,2,schoolinfo)

#所属学校专业信息提取
def professes(professes,schoolinfo):
    flag = False
    for data in professes:
        if flag == False:#第一行不解析
            flag = True
            continue
        #从第二开始数据抽取
        professesinfos = re.findall(r'<td.*?>(.*?)</td>',str(data),re.S|re.M)
        Faculty = professesinfos[0]
        professioncode = professesinfos[1]
        research_direction = professesinfos[2]
        mentor = str(re.findall(r'<script .*?>(.*?)</script>',str(professesinfos[3]),re.S|re.M)).split("'")[1].replace(",","")
        enrollednumberT = str(re.findall(r'<script .*?>(.*?)</script>',str(professesinfos[4]),re.S|re.M)).split("'")[1].split(",")
        try:
            if len(enrollednumberT) >=1:
                enrollednumber = enrollednumberT[0].split("\\\\uff1a")[1]
            if len(enrollednumberT) >=2:
                enrollednumberTM = enrollednumberT[1].split("\\\\uff1a")[1]
        except IndexError:
            enrollednumber = 0
            enrollednumberTM = 0
        professesinfoss = schoolinfo+","+UDencode(Faculty)+","+UDencode(professioncode)+","+UDencode(research_direction)+","+str(enrollednumber)+","+str(enrollednumberTM)

        testinfosurl = "http://yz.chsi.com.cn"+re.findall(r'(?<=href=\").+?(?=\")|(?<=href=\').+?(?=\')',str(professesinfos[5]),re.S|re.M)[0].replace("amp;","")
        testinfos = data_Crawling(testinfosurl)
        soup = BeautifulSoup(testinfos,'html.parser')
        testinfolistT = soup.find_all('div',id='result_list')
        testinfolist = re.findall(r'<tr>(.*?)</tr>',str(testinfolistT),re.S|re.M)
        # print testinfolist
        flag1 = False
        for info in testinfolist:
            if flag1 == False:
                flag1 = True
                continue
            classinfo = re.findall(r'<td.*?>(.*?)</td>',str(info),re.S|re.M)
            No = classinfo[0]
            class1 = re.findall(r'<a .*?>(.*?)</a>',str(classinfo[1]),re.S|re.M)[0]
            class2 = re.findall(r'<a .*?>(.*?)</a>',str(classinfo[2]),re.S|re.M)[0]
            class3 = re.findall(r'<a .*?>(.*?)</a>',str(classinfo[3]),re.S|re.M)[0]
            class4 = re.findall(r'<a .*?>(.*?)</a>',str(classinfo[4]),re.S|re.M)[0]
            classinfos = professesinfoss+","+No+","+UDencode(class1)+","+UDencode(class2)+","+UDencode(class3)+","+UDencode(class4)
            # class1 = eval("u'"+classinfos+"'").encode('utf-8')
            global writer
            writer.writerow([classinfos])

def DataExtraction(datas,type,schoolinfo):
    soup = BeautifulSoup(datas, "html.parser")
    resultdata = soup.find_all("div", id="sch_list")
    datas = re.findall(r'<tr>(.*?)</tr>',str(resultdata),re.S|re.M)
    if type == 1:
        schoolinfos(datas)
    if type == 2:
        professes(datas,schoolinfo)



#多页翻页
def page(checkurl,type,schoolinfo):
    pagecontent = data_Crawling(checkurl)
    pagecount = re.findall(r'<li class="lip" id="page_total">1/(.*?)</li>',pagecontent,re.S|re.M)[0]
    # print pagecount
    for i in range(1,int(pagecount)+1,1):
        url = checkurl+'&pageno='+str(i)
        datas = data_Crawling(url)
        DataExtraction(datas,type,schoolinfo)


def main():
    profinfo = [{"mc":"哲学","dm":"0101"},{"mc":"理论经济学","dm":"0201"},{"mc":"应用经济学","dm":"0202"},{"mc":"金融","dm":"0251"},
                {"mc":"应用统计","dm":"0252"},{"mc":"税务","dm":"0253"},{"mc":"国际商务","dm":"0254"},{"mc":"保险","dm":"0255"},
                {"mc":"资产评估","dm":"0256"},{"mc":"审计","dm":"0257"},{"mc":"统计学","dm":"0270"},{"mc":"法学","dm":"0301"},
                {"mc":"政治学","dm":"0302"},{"mc":"社会学","dm":"0303"},{"mc":"民族学","dm":"0304"},{"mc":"马克思主义理论","dm":"0305"},
                {"mc":"公安学","dm":"0306"},{"mc":"法律","dm":"0351"},{"mc":"社会工作","dm":"0352"},{"mc":"警务","dm":"0353"},
                {"mc":"教育学","dm":"0401"},{"mc":"心理学","dm":"0402"},{"mc":"体育学","dm":"0403"},{"mc":"教育","dm":"0451"},
                {"mc":"体育","dm":"0452"},{"mc":"汉语国际教育","dm":"0453"},{"mc":"应用心理","dm":"0454"},{"mc":"","dm":"0471"},
                {"mc":"中国语言文学","dm":"0501"},{"mc":"外国语言文学","dm":"0502"},{"mc":"新闻传播学","dm":"0503"},{"mc":"翻译","dm":"0551"},
                {"mc":"新闻与传播","dm":"0552"},{"mc":"出版","dm":"0553"},{"mc":"考古学","dm":"0601"},{"mc":"中国史","dm":"0602"},
                {"mc":"世界史","dm":"0603"},{"mc":"文物与博物馆","dm":"0651"},{"mc":"数学","dm":"0701"},{"mc":"物理学","dm":"0702"},
                {"mc":"化学","dm":"0703"},{"mc":"天文学","dm":"0704"},{"mc":"地理学","dm":"0705"},{"mc":"大气科学","dm":"0706"},
                {"mc":"海洋科学","dm":"0707"},{"mc":"地球物理学","dm":"0708"},{"mc":"地质学","dm":"0709"},{"mc":"生物学","dm":"0710"},
                {"mc":"系统科学","dm":"0711"},{"mc":"科学技术史","dm":"0712"},{"mc":"生态学","dm":"0713"},{"mc":"统计学","dm":"0714"},
                {"mc":"心理学","dm":"0771"},{"mc":"力学","dm":"0772"},{"mc":"材料科学与工程","dm":"0773"},{"mc":"电子科学与技术","dm":"0774"},
                {"mc":"计算机科学与技术","dm":"0775"},{"mc":"环境科学与工程","dm":"0776"},{"mc":"生物医学工程","dm":"0777"},{"mc":"基础医学","dm":"0778"},
                {"mc":"公共卫生与预防医学","dm":"0779"},{"mc":"药学","dm":"0780"},{"mc":"中药学","dm":"0781"},{"mc":"医学技术","dm":"0782"},
                {"mc":"护理学","dm":"0783"},{"mc":"","dm":"0784"},{"mc":"","dm":"0785"},{"mc":"","dm":"0786"},{"mc":"力学","dm":"0801"},
                {"mc":"机械工程","dm":"0802"},{"mc":"光学工程","dm":"0803"},{"mc":"仪器科学与技术","dm":"0804"},{"mc":"材料科学与工程","dm":"0805"},
                {"mc":"冶金工程","dm":"0806"},{"mc":"动力工程及工程热物理","dm":"0807"},{"mc":"电气工程","dm":"0808"},{"mc":"电子科学与技术","dm":"0809"},
                {"mc":"信息与通信工程","dm":"0810"},{"mc":"控制科学与工程","dm":"0811"},{"mc":"计算机科学与技术","dm":"0812"},{"mc":"建筑学","dm":"0813"},
                {"mc":"土木工程","dm":"0814"},{"mc":"水利工程","dm":"0815"},{"mc":"测绘科学与技术","dm":"0816"},{"mc":"化学工程与技术","dm":"0817"},
                {"mc":"地质资源与地质工程","dm":"0818"},{"mc":"矿业工程","dm":"0819"},{"mc":"石油与天然气工程","dm":"0820"},{"mc":"纺织科学与工程","dm":"0821"},
                {"mc":"轻工技术与工程","dm":"0822"},{"mc":"交通运输工程","dm":"0823"},{"mc":"船舶与海洋工程","dm":"0824"},{"mc":"航空宇航科学与技术","dm":"0825"},
                {"mc":"兵器科学与技术","dm":"0826"},{"mc":"核科学与技术","dm":"0827"},{"mc":"农业工程","dm":"0828"},{"mc":"林业工程","dm":"0829"},
                {"mc":"环境科学与工程","dm":"0830"},{"mc":"生物医学工程","dm":"0831"},{"mc":"食品科学与工程","dm":"0832"},{"mc":"城乡规划学","dm":"0833"},
                {"mc":"风景园林学","dm":"0834"},{"mc":"软件工程","dm":"0835"},{"mc":"生物工程","dm":"0836"},{"mc":"安全科学与工程","dm":"0837"},
                {"mc":"公安技术","dm":"0838"},{"mc":"网络空间安全","dm":"0839"},{"mc":"建筑学","dm":"0851"},{"mc":"工程","dm":"0852"},
                {"mc":"城市规划","dm":"0853"},{"mc":"科学技术史","dm":"0870"},{"mc":"管理科学与工程","dm":"0871"},{"mc":"设计学","dm":"0872"},
                {"mc":"作物学","dm":"0901"},{"mc":"园艺学","dm":"0902"},{"mc":"农业资源与环境","dm":"0903"},{"mc":"植物保护","dm":"0904"},{"mc":"畜牧学","dm":"0905"},
                {"mc":"兽医学","dm":"0906"},{"mc":"林学","dm":"0907"},{"mc":"水产","dm":"0908"},{"mc":"草学","dm":"0909"},{"mc":"农业","dm":"0951"},{"mc":"兽医","dm":"0952"},{"mc":"风景园林","dm":"0953"},{"mc":"林业","dm":"0954"},{"mc":"科学技术史","dm":"0970"},{"mc":"环境科学与工程","dm":"0971"},{"mc":"食品科学与工程","dm":"0972"},{"mc":"风景园林学","dm":"0973"},{"mc":"基础医学","dm":"1001"},{"mc":"临床医学","dm":"1002"},{"mc":"口腔医学","dm":"1003"},{"mc":"公共卫生与预防医学","dm":"1004"},{"mc":"中医学","dm":"1005"},{"mc":"中西医结合","dm":"1006"},{"mc":"药学","dm":"1007"},{"mc":"中药学","dm":"1008"},{"mc":"特种医学","dm":"1009"},{"mc":"医学技术","dm":"1010"},{"mc":"护理学","dm":"1011"},{"mc":"临床医学","dm":"1051"},{"mc":"口腔医学","dm":"1052"},{"mc":"公共卫生","dm":"1053"},{"mc":"护理","dm":"1054"},{"mc":"药学","dm":"1055"},{"mc":"中药学","dm":"1056"},{"mc":"中医","dm":"1057"},{"mc":"科学技术史","dm":"1071"},{"mc":"生物医学工程","dm":"1072"},{"mc":"","dm":"1073"},{"mc":"","dm":"1074"},{"mc":"军事思想及军事历史","dm":"1101"},{"mc":"战略学","dm":"1102"},{"mc":"战役学","dm":"1103"},{"mc":"战术学","dm":"1104"},{"mc":"军队指挥学","dm":"1105"},{"mc":"军制学","dm":"1106"},{"mc":"军队政治工作学","dm":"1107"},{"mc":"军事后勤学","dm":"1108"},{"mc":"军事装备学","dm":"1109"},{"mc":"军事训练学","dm":"1110"},{"mc":"军事","dm":"1151"},{"mc":"管理科学与工程","dm":"1201"},{"mc":"工商管理","dm":"1202"},{"mc":"农林经济管理","dm":"1203"},{"mc":"公共管理","dm":"1204"},{"mc":"图书情报与档案管理","dm":"1205"},{"mc":"工商管理","dm":"1251"},{"mc":"公共管理","dm":"1252"},{"mc":"会计","dm":"1253"},{"mc":"旅游管理","dm":"1254"},{"mc":"图书情报","dm":"1255"},{"mc":"工程管理","dm":"1256"},{"mc":"艺术学理论","dm":"1301"},{"mc":"音乐与舞蹈学","dm":"1302"},{"mc":"戏剧与影视学","dm":"1303"},{"mc":"美术学","dm":"1304"},{"mc":"设计学","dm":"1305"},{"mc":"艺术","dm":"1351"}]
    profinfocode = '0808'#电气工程
    print "正在数据提取中，请稍等..."
    global writer
    writer = csv.writer(codecs.open("classinfo.csv", "a"), dialect='excel')
    firsturl = 'http://yz.chsi.com.cn/zsml/queryAction.do?ssdm=&mldm=&mlmc=--%E9%80%89%E6%8B%A9%E9%97%A8%E7%B1%BB--&yjxkdm='+profinfocode+'&dwmc=&zymc='
    page(firsturl,1,'')


if __name__ == '__main__':
    main()