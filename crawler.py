import requests
import re
import mysql.connector
from mysql.connector import errorcode
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from time import sleep
import random



class TaobaoData():
    #数据库taobao里表的结构
    DB_NAME='taobao'
    conn = mysql.connector.connect(user='root', password='mysqlpasswd')
    cur = conn.cursor()
    def __init__(self,tbname):
        self.tablename=tbname
        self.tb = '''create table '''+self.tablename+'''(
                nid varchar(50) not null,
                title varchar(80) not null,
                price float not null,
                fee float not null,
                loc varchar(50) not null,
                sales int not null,
                comcnt varchar(50) not null,
                primary key (nid)
                )'''


    #创建数据库函数
    def createDatabase(self,cur):
        try:
            cur.execute("CREATE DATABASE {} DEFAULT CHARACTER SET 'utf8'".format(self.DB_NAME))
            print("Create database successfully")
        except mysql.connector.Error as err:
            print("Failed creating databases: {}".format(err))

    #使用数据库
    def useDatabase(self):
        try:
            self.cur.execute("USE {}".format(self.DB_NAME))
            print("use database ok")
        except mysql.connector.Error as err:
            print("Database {} does not exists.".format(self.DB_NAME))
            if err.errno == errorcode.ER_BAD_DB_ERROR:
                self.createDatabase(self.cur)
                print("Database {} created successfully.")
                self.conn.database=self.DB_NAME
            else:
                print(err)

    #创建表
    def createTable(self):
        try:
            print("Creating table {}: ".format(self.tablename),end='')
            self.cur.execute(self.tb)
        except mysql.connector.Error as err:
            if err.errno == errorcode.ER_TABLE_EXISTS_ERROR:
                print("table already exists.")
            else:
                print(err.msg)
        else:
            print("OK")



class TaobaoLogin:
    # 对象初始化
    def __init__(self):
        url = 'https://login.taobao.com/member/login.jhtml'
        self.url = url

        options = webdriver.ChromeOptions()
        #options.add_argument('headless')#静默启动浏览器
        options.add_experimental_option("prefs", {"profile.managed_default_content_settings.images": 2})  # 不加载图片,加快访问速度
        options.add_experimental_option('excludeSwitches',['enable-automation'])  # 设置为开发者模式，防止被识别出来使用了Selenium
        #options.add_argument("--proxy-server=http://163.125.18.47:8888")
        self.browser = webdriver.Chrome(executable_path="D:/python/chromedriver.exe", options=options)
        self.wait = WebDriverWait(self.browser, 10)  # 超时时长为10s


    # 登录淘宝
    def login(self,user,passwd):
        # 打开网页
        self.browser.get(self.url)

        # 选择密码登录
        password_login = self.wait.until(
            EC.presence_of_element_located((By.CSS_SELECTOR, '.qrcode-login > .login-links > .forget-pwd')))
        password_login.click()
        print("choose password successfully")

        # 选择微博登录
        weibo_login = self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, '.weibo-login')))
        weibo_login.click()
        print("choose weibo-login successfully")

        # 输入微博账号
        weibo_user = self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, '.username > .W_input')))
        weibo_user.send_keys(user)

        # 输入微博密码
        weibo_pwd = self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, '.password > .W_input')))
        weibo_pwd.send_keys(passwd)

        # 点击登录按钮
        submit = self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, '.btn_tip > a > span')))
        submit.click()

        # 直到获取到淘宝会员昵称才能确定是登录成功
        taobao_name = self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR,'.site-nav-bd > ul.site-nav-bd-l > li#J_SiteNavLogin > div.site-nav-menu-hd > div.site-nav-user > a.site-nav-login-info-nick ')))
        # 输出淘宝昵称
        print(taobao_name.text)

        # 获取cookie 
        cookie = [item["name"] + "=" + item["value"] for item in self.browser.get_cookies()]

        # 整合输出cookie  
        cookiestr = ';'.join(item for item in cookie)

        print(cookiestr)

        #返回淘宝名和cookie
        loginresult=[taobao_name.text,cookiestr]
        return loginresult

    #爬虫
def getHTML(var):
    hd = {'cookie': var[1],'user-sgent': 'Mozilla/5.0'}
    try:
        r = requests.get(var[0], headers=hd,timeout=30)
        r.raise_for_status()
        r.encoding = r.apparent_encoding
        print(r.text)
        sleep(random.uniform(1.0,3.5))
        return r.text
    except:
        print("crawler error")
        return "Error!"


#数据预处理存入数据库
def analyzeHTML(ilt, html,tbname):
    try:
        nlt=re.findall(r'\"nid\"\:\".*?\"', html)
        plt = re.findall(r'\"view_price\"\:\"[\d\.]*\"', html)
        ttlt = re.findall(r'\"raw_title\"\:\".*?\"', html)
        itloc = re.findall(r'\"item_loc\"\:\".*?\"', html)
        vfee = re.findall(r'\"view_fee\"\:\"[\d\.]*\"', html)
        itsales = re.findall(r'\"view_sales\"\:\".*?\"', html)
        itcomcnt = re.findall(r'\"comment_count\"\:\"[\d\.]*\"', html)
        for i in range(2,len(nlt)):
            nid=eval(nlt[i].split(':')[1])
            title = eval(ttlt[i].split(':')[1])
            price = eval(plt[i].split(':')[1])
            itlocation_init = eval(itloc[i].split(':')[1])
            itlocation=itlocation_init.split(' ')[0]
            itemfee = eval(vfee[i].split(':')[1])
            itsalecnt_init = eval(itsales[i].split(':')[1])
            itsalecnt = itsalecnt_init.split('人')[0]
            if itsalecnt.endswith('+'):
                itsalecnt=itsalecnt.split('+')[0]
                if itsalecnt.endswith('万'):
                    itsalecnt = int(float(itsalecnt.split('万')[0]) * 10000)
                else:
                    itsalecnt=int(itsalecnt)
            itcommentcnt = eval(itcomcnt[i].split(':')[1])
            if len(itcommentcnt) == 0:
                itcommentcnt = '0'
            ilt.append([nid,title, price, itemfee, itlocation, itsalecnt, itcommentcnt])
            # 往表里插数据的sql语句
            add_info = ("insert into "+tbname+"(nid,title,price,fee,loc,sales,comcnt) values(%s, %s, %s, %s, %s, %s, %s)")
            try:
                data_info = (nid,title, price, itemfee, itlocation, itsalecnt, itcommentcnt)
                TaobaoData.cur.execute(add_info, data_info)
                print("insert ok")
            except mysql.connector.Error as err:
                print(err.msg)
    except:
        print("处理失败")
    TaobaoData.conn.commit()


#打印数据
def showGoodsList(ilt):
    tplt = "{0:4}\t{1:4}\t{2:8}\t{3:8}\t{4:8}\t{5:8}\t{6:8}\t{7:<16}"
    print(tplt.format("序号", "编号","价格","邮费", "地点", "销量", "评论数", "商品名称"))
    count = 0
    for g in ilt:
        count = count + 1
        print(tplt.format(count,g[0],g[2],g[3],g[4], g[5], g[6], g[1]))






















