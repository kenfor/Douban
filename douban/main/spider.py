from bs4 import BeautifulSoup
from collections import OrderedDict
import urllib.request
import urllib.error
import re
import xlwt
import sqlite3


class doubanCatch:
    def __init__(self,baseurl,head,savepath,complileDict,dbpath):
        self.baseurl = baseurl
        self.head = head
        self.savepath = savepath
        self.complileDict = complileDict
        self.datalist = []
        self.conn = sqlite3.connect(dbpath)


    # 1.准备工作
    def preWork(self):
        #TODO 验证传入的参数是否符合规范,初始化数据啼
        return 1

    # 2.爬取网页
    def askURL(self):
        htmls = []
        for i in range(10):  # 调用获取页面信息的函数
            url = self.baseurl + str(i * 25)
            request = urllib.request.Request(url,headers=self.head)
            try:
                response = urllib.request.urlopen(request)
                html = response.read().decode('utf-8')
                htmls.append(html)
            except urllib.error.URLError as e:
                if hasattr(e,'code'):
                    print('askURL: ',e.code)
                if hasattr(e,'reson'):
                    print('askURL: ',e.reason)
        return htmls

    # 3.解析网页
    def getData(self,html):
        soup = BeautifulSoup(html,'html.parser')
        for item in soup.find_all('div',class_='item'):
            data = OrderedDict()
            item = str(item)
            #complileDict = {'findLink': findLink, 'findImg': findImg, 'findTitle': findTitle,
            #                'findRating': findRating, 'findJudge': findJudge, 'findInq': findInq, 'findBd': findBd}
            data['Link'] = re.findall(self.complileDict['findLink'],item)[0]
            data['Img'] = re.findall(self.complileDict['findImg'],item)[0]

            titles = re.findall(self.complileDict['findTitle'],item)
            if len(titles) == 2 :
                data['cTitle'] = titles[0]
                data['oTitle'] = titles[1].replace('/','')
            else:
                data['cTitle'] = titles[0]
                data['oTitle'] = ' '

            data['Rating'] = re.findall(self.complileDict['findRating'],item)[0]
            data['Judge'] = re.findall(self.complileDict['findJudge'], item)[0]

            inqs = re.findall(self.complileDict['findInq'], item)
            if len(inqs) != 0:
                data['Inq'] = inqs[0].replace('.','')
            else:
                data['Inq'] = ' '

            bd = re.findall(self.complileDict['findBd'], item)[0]
            bd = re.sub('<br(\s+)?/>(\s+)?',' ',bd)
            bd = re.sub('/'," ",bd).strip()
            bd = re.sub('"', " ", bd)
            data['Bd'] = bd
            self.datalist.append(data)

    # 4.保存数据
    def saveto_excel(self):
        print('save ...')
        book =  xlwt.Workbook(encoding='utf-8',style_compression=0)
        sheet = book.add_sheet('豆瓣电影TOP250',cell_overwrite_ok=True)
        column = ('电影详情链接','图片链接','影片中文名','影片外国名','评分','评价数','概况','相关信息')

        for i in range(len(column)):
            sheet.write(0,i,column[i])

        for i,d in enumerate(self.datalist,start=1):
            print('第{}条'.format(i))
            print(d)
            for j,v in enumerate(d.values()):
                sheet.write(i,j,v)
        book.save(self.savepath)

    def saveto_sqldb(self):
        self.init_db()
        cur = self.conn.cursor()
        for d in self.datalist:
            data = list(d.values())
            data = [ '"'+i+'"' for i in data ]
            sql = '''
                insert into movie250 (
                info_link,pic_link,cname,oname,score,rated,instroduction,info)
                values({})
            '''.format(','.join(data))
            print(sql)
            cur.execute(sql)
            self.conn.commit()
        else:
            cur.close()


    # 清理工作
    def clear(self):
        self.datalist.clear()
        self.conn.close()

    # 启动
    def run(self):
        flag = self.preWork()  # 1.准备工作
        if flag:
            try:
                htmls = self.askURL()  # 2.爬取网页
                for html in htmls:  # 3.解析网页
                    self.getData(html)
                # self.saveto_excel()  # 4.保存数据
                # self.saveto_sqldb()
            except Exception as e:
                print('run: ',e)
            finally:
                self.clear()  # 5.清理工作

    # 初始化数据库
    def init_db(self):
        sql = '''
            create table movie250
            (
                id integer primary key autoincrement,
                info_link text,
                pic_link text,
                cname varchar,
                oname varchar,
                score numeric,
                rated numeric,
                instroduction text,
                info text
            )
        '''  # 创建数据表单
        cursor = self.conn.cursor()
        try:
            cursor.execute(sql)
            self.conn.commit()
        finally:
            cursor.close()



if __name__ == "__main__":
    baseurl = 'https://movie.douban.com/top250?start=' #TODO 改造从配置文件读取设定
    head = {'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.3239.132 Safari/537.36'}
    savepath = './豆瓣电影TOP250.xls'
    dbpath = 'douban.db'
    complileDict = OrderedDict()

    # 匹配超链接  例如:<a href="">
    findLink = re.compile(r'<a href="(.*?)">')

    #<img alt="肖申克的救赎" class="" src="https://img3.doubanio.com/view/photo/s_ratio_poster/public/p480747492.jpg" width="100"/>
    findImg = re.compile(r'<img.*src="(.*?)"',re.S)

    #<span class="title">肖申克的救赎</span>
    findTitle = re.compile(r'<span class="title">(.*)</span>')

    #<span class="rating_num" property="v:average">9.7</span>
    findRating = re.compile(r'<span class="rating_num" property="v:average">(.*)</span>')

    #<span>2147325人评价</span>
    findJudge = re.compile(r'<span>(\d*)人评价</span>')

    #<span class="inq">希望让人自由。</span>
    findInq = re.compile(r'<span class="inq">(.*?)</span>')

    #<p class="">
    #                       导演: 弗兰克·德拉邦特 Frank Darabont   主演: 蒂姆·罗宾斯 Tim Robbins /...<br/>
    #                       1994 / 美国 / 犯罪 剧情
    #                   </p>
    findBd = re.compile(r'<p class="">(.*?)</p>',re.S)

    #正则匹配字典构造
    complileDict= {'findLink':findLink,'findImg':findImg,'findTitle':findTitle,'findRating':findRating,'findJudge':findJudge,'findInq':findInq,'findBd':findBd}

    try:
        d = doubanCatch(baseurl,head,savepath,complileDict,dbpath)
        d.run()
    except Exception as e:
        print('main: ',e)
    finally:
        pass



