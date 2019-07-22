import PIL.Image
import PIL.ImageTk
from tkinter import *
from tkinter.messagebox import *
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg,NavigationToolbar2Tk
import numpy as np
import mysql.connector
import multiprocessing as mp
import jieba
from wordcloud import WordCloud
import time
from crawler import *


plt.rcParams['font.sans-serif']=['SimHei'] #用来正常显示中文标签
plt.rcParams['axes.unicode_minus']=False #用来正常显示负号

#初始
class BaseDesk():
    def __init__(self, master):
        self.root = master
        self.root.config()
        self.root.title('欢迎使用淘宝商品数据爬取系统')
        self.root.geometry('1600x900')
        WelcomePage(self.root)

# #欢迎界面
class WelcomePage(object):
    def __init__(self,master=None):
        self.root=master
        self.root.geometry('1600x900')
        self.createPage()

    def createPage(self):
        self.page = Frame(self.root)  # 创建Frame
        self.page.pack()
        canvas = Canvas(self.page, height=900, width=1600)
        image=canvas.create_image(0,0,anchor='nw',image=image_file)
        canvas.pack(side='top')

        # 欢迎界面按钮
        btn_enter = Button(self.page, bg='silver', text="进入系统", font=("微软雅黑 18"), width=10, height=2,
                           command=self.enterPresent)
        btn_enter.place(x=710, y=280)

        # 退出系统按钮
        btn_exit = Button(self.page, bg='silver', text="退出系统", font=("微软雅黑 18"), width=10, height=2, command=exit)
        btn_exit.place(x=710, y=400)

    def enterPresent(self):
        self.page.destroy()
        LoginPage(self.root)


#登录页面
class LoginPage(object):
    reresult = ["",""]
    def __init__(self,master=None):
        self.root=master
        self.root.geometry('1600x900')
        self.username = StringVar()
        self.password = StringVar()
        self.e1=Entry()
        self.e2=Entry()
        self.createPage()


    def createPage(self):
        self.page = Frame(self.root)
        self.page.pack()
        canvas = Canvas(self.page, height=900, width=1600)
        image = canvas.create_image(0, 0, anchor='nw', image=image_file)
        canvas.pack(side='top')
        info="本系统需使用与淘宝账户相关联的微博账户登录"
        l1=Label(self.page,text=info,font=("微软雅黑 18"))
        l1.place(x=530,y=130)
        l2=Label(self.page, text='账户: ',font=("微软雅黑 12"))
        l2.place(x=650,y=250)
        self.e1=Entry(self.page, textvariable=self.username,font=("微软雅黑 13"))
        self.e1.place(x=698,y=250)
        l3 = Label(self.page, text='密码: ', font=("微软雅黑 12"))
        l3.place(x=650, y=310)
        self.e2 = Entry(self.page, textvariable=self.password, show='*',font=("微软雅黑 13"))
        self.e2.place(x=698, y=310)
        btn_login=Button(self.page, text='登录', font=("微软雅黑 10"),width=4,height=1,command=self.login)
        btn_login.place(x=650,y=370)
        btn_exit=Button(self.page, text='返回', font=("微软雅黑 10"),width=4,height=1, command=self.reWelcome)
        btn_exit.place(x=860,y=370)
        t1=Text(self.page)

    def login(self):
        try:
            tb = TaobaoLogin()
            LoginPage.reresult = tb.login(self.e1.get(),self.e2.get())  # 登录
            print("登录成功")
            showinfo('Tip', '登录成功')
            self.page.destroy()
            Process(self.root)
        except:
            showinfo('Tip', '登录失败')
            print("登录失败")

    def reWelcome(self):
        self.page.destroy()
        WelcomePage(self.root)

#初始时间
t1=time.time()

#启动爬虫
class Process(object):
    goods=""
    def __init__(self, master=None):
        self.root = master
        self.root.geometry('1600x900')
        self.itementry = Entry()
        self.createPage()

    def createPage(self):
        self.page = Frame(self.root)
        self.page.pack()
        canvas = Canvas(self.page, height=900, width=1600)
        image = canvas.create_image(0, 0, anchor='nw', image=image_file)
        canvas.pack(side='top')
        itemlabel = Label(self.page, text='请输入想爬取商品品类名称', font=("微软雅黑 18"))
        itemlabel.place(x=630, y=150)
        self.itementry = Entry(self.page, textvariable=self.itementry, font=("微软雅黑 18"))
        self.itementry.place(x=638, y=195)
        btn_process = Button(self.page, bg='silver', text="开始爬取", font=("微软雅黑 18"), width=12, height=1,command=self.checkGoods)
        btn_process.place(x=685, y=300)
        btn_backlogin = Button(self.page, bg='silver', text="返回", font=("微软雅黑 18"), width=12, height=1,command=self.backLogin)
        btn_backlogin.place(x=685, y=380)

    def backLogin(self):
        self.page.destroy()
        LoginPage(self.root)

    def beginCrawler(self):
        try:
            # 初始时间
            t1 = time.time()
            #爬取的信息存放列表
            infoList = []
            #url列表
            firsturl=[]
            urls = []
            Process.goods = self.itementry.get()
            start_url = 'https://s.taobao.com/search?q=' + Process.goods
            dt=TaobaoData(Process.goods)
            dt.createDatabase(dt.cur)
            dt.useDatabase()
            dt.createTable()
            tpcookie = LoginPage.reresult[1]
            print("loginpageresult is ",LoginPage.reresult)
            #获取页数
            firsturl.append([start_url,tpcookie])
            firstpage = getHTML(firsturl[0])
            pagematch = re.search(r'\"totalPage\"\:[\d\.]*', firstpage)
            pgmatch = pagematch.group()
            pagenum = eval(pgmatch.split(':')[1])
            print("页数：" + str(pagenum))
            #爬取深度
            depth=pagenum
            for i in range(depth):
                url = start_url + '&s=' + str(44 * i)
                urls.append([url, tpcookie])
            pool = mp.Pool(4)
            htmls = pool.map(getHTML, urls)
            pool.close()
            pool.join()
            for html in htmls:
                analyzeHTML(infoList, html,Process.goods)
            # pool2 = mp.Pool(4)
            # infoListresult=pool2.map(analyzeHTML,htmls)
            # pool2.close()
            # pool2.join()
            showGoodsList(infoList)
            #爬取总用时
            print('Total time: %.1f s' % (time.time() - t1,))
            print("爬取完成")
            showinfo('Tip',"爬取完成")
            self.page.destroy()
            ShowResult(self.root)
        except:
            showinfo('Tip', '爬取失败')
            print("爬取失败")

    def checkGoods(self):
        ask=askyesno(title='提示', message='请勿输入空格及特殊符号！\n输入是否合法？')
        print(ask)
        if ask:
            print(ask)
            self.beginCrawler()
        else:
            pass

#显示数据处理结果
class ShowResult(object):
    def __init__(self, master=None):
        self.root = master
        self.root.geometry('1600x900')
        self.createPage()

    def createPage(self):
        self.page = Frame(self.root)
        self.page.pack()
        canvas = Canvas(self.page, height=900, width=1600)
        image = canvas.create_image(0, 0, anchor='nw', image=image_file)
        canvas.pack(side='top')
        btn_show = Button(self.page, bg='silver', text="显示数据处理结果", font=("微软雅黑 18"), width=13, height=1,command=self.showFigs)
        btn_show.place(x=703, y=300)
        btn_pre = Button(self.page, bg='silver', text="返回上一页", font=("微软雅黑 18"), width=12, height=1, command=self.backProcess)
        btn_pre.place(x=710, y=400)

    def backProcess(self):
            self.page.destroy()
            Process(self.root)

    def showFigs(self):
        self.page.destroy()
        InfoFigure1(self.root)



#绘制的第一幅图
class InfoFigure1(object):
    def __init__(self, master=None):
        self.root = master
        self.root.geometry('1600x900')
        self.createPage()

    def createPage(self):
        self.page = Frame(self.root)
        self.page.pack(fill=BOTH,expand=1)
        conn = mysql.connector.connect(user='root', password='mysqlpasswd', database='taobao')
        cur = conn.cursor()

        # 不同价格对应的商品数量分布图
        try:
            fig1 = plt.figure(figsize=(20, 7))
            sql1 = "select price from " + Process.goods + ";"
            cur.execute(sql1)
            result1 = cur.fetchall();
            price1 = [n1[0] for n1 in result1]
            max_price = int(max(price1))
            min_price = int(min(price1))
            gap = int((max_price - min_price) / 10)
            plt.hist(price1, range(0, max_price, gap), color='steelblue', edgecolor='k')
            x_ticks1 = np.arange(0, max_price, gap)
            plt.xticks(x_ticks1)
            plt.xlim(0,max_price)
            plt.xlabel('价格',fontsize=16)
            plt.ylabel('商品数量',fontsize=16)
            plt.title('不同价格对应的商品数量分布',fontsize=18)
            btn_next1=Button(self.page, text='下一张图', font=("微软雅黑 10"),width=8,height=1, command=self.nextPage)
            btn_next1.pack(side=BOTTOM)
            canvas = FigureCanvasTkAgg(fig1, master=self.page)
            canvas.draw()
            canvas.get_tk_widget().pack(side=TOP)
            toolbar = NavigationToolbar2Tk(canvas, self.page)
            toolbar.update()
            canvas._tkcanvas.pack(fill=BOTH, expand=1)
            # 关闭数据库连接
            cur.close()
            conn.close()
        except:
            showinfo('Tip', '数据读取失败')
            Process(self.root)

    #跳转到下一幅图
    def nextPage(self):
        self.page.destroy()
        InfoFigure2(self.root)

#绘制的第二幅图
class InfoFigure2(object):
    def __init__(self, master=None):
        self.root = master
        self.root.geometry('1600x900')
        self.createPage()

    def createPage(self):
        self.page = Frame(self.root)
        self.page.pack(fill=BOTH, expand=1)
        conn = mysql.connector.connect(user='root', password='mysqlpasswd', database='taobao')
        cur = conn.cursor()

        # 不同销量对应的商品数量分布图
        fig2 = plt.figure(figsize=(20, 7))
        sql2 = "select sales from " + Process.goods + ";"
        cur.execute(sql2)
        result2 = cur.fetchall()
        sales1 = [int(n2[0]) for n2 in result2]
        min_sales = int(min(sales1))
        max_sales = int(max(sales1))
        gap = int((max_sales - min_sales) / 10)
        plt.hist(sales1, range(0, max_sales, gap), color='steelblue', edgecolor='k')
        x_ticks2 = np.arange(0, max_sales + 1, gap)
        plt.xticks(x_ticks2)
        plt.xlim(0,max_sales)
        plt.xlabel('销量',fontsize=16)
        plt.ylabel('商品数量',fontsize=16)
        plt.title('不同销量对应的商品数量分布',fontsize=18)
        btn_last1 = Button(self.page, text='上一张图', font=("微软雅黑 10"), width=8, height=1, command=self.lastPage)
        btn_next2 = Button(self.page, text='下一张图', font=("微软雅黑 10"), width=8, height=1, command=self.nextPage)
        btn_next2.pack(side=BOTTOM)
        btn_last1.pack(side=BOTTOM)
        canvas = FigureCanvasTkAgg(fig2, master=self.page)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=BOTH, expand=1)
        toolbar = NavigationToolbar2Tk(canvas, self.page)
        toolbar.update()
        canvas._tkcanvas.pack(fill=BOTH, expand=1)
        # 关闭数据库连接
        cur.close()
        conn.close()

    #跳转到前一幅图
    def lastPage(self):
        self.page.destroy()
        InfoFigure1(self.root)

    #跳转到后一幅图
    def nextPage(self):
        self.page.destroy()
        InfoFigure3(self.root)

#绘制的第三幅图
class InfoFigure3(object):
    def __init__(self, master=None):
        self.root = master
        self.root.geometry('1600x900')
        self.createPage()

    def createPage(self):
        self.page = Frame(self.root)
        self.page.pack(fill=BOTH, expand=1)
        conn = mysql.connector.connect(user='root', password='mysqlpasswd', database='taobao')
        cur = conn.cursor()
        fig3 = plt.figure(figsize=(20, 7))
        sql3 = "select sales,price from " + Process.goods + ";"
        cur.execute(sql3)
        result3 = cur.fetchall();
        price_row = [p[1] for p in result3]
        min_price = min(price_row)
        max_price = max(price_row) + 5
        part = 10
        gap = int((max_price - min_price) / part)
        price_group=[]
        sales_group=[]
        for n in range(part):
            cnt=0
            sum_sales=0
            begin_price = int(min_price + n * gap)
            end_price = int(begin_price + gap)
            # begin_price=float("%.1f"%begin_price)
            # end_price=float("%.1f"%end_price)
            price_group.append([begin_price,end_price])
            for i in result3:
                if i[1] > begin_price and i[1] <= end_price:
                    cnt = cnt + 1
                    sum_sales = sum_sales + int(i[0])
            if cnt == 0:
                ave_sales=0
            else:
                ave_sales=(int)(sum_sales/cnt)
            sales_group.append(ave_sales)
        index=np.arange(len(price_group))
        plt.bar(index,sales_group,color='steelblue')
        plt.xticks(index,(n for n in price_group))
        plt.xlabel('价格',fontsize=16)
        plt.ylabel('平均销量',fontsize=16)
        plt.title('不同价格对应的商品平均销量分布',fontsize=18)
        btn_last2 = Button(self.page, text='上一张图', font=("微软雅黑 10"), width=8, height=1, command=self.lastPage)
        btn_next3 = Button(self.page, text='下一张图', font=("微软雅黑 10"), width=8, height=1, command=self.nextPage)
        btn_next3.pack(side=BOTTOM)
        btn_last2.pack(side=BOTTOM)
        canvas = FigureCanvasTkAgg(fig3, master=self.page)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=BOTH, expand=1)
        toolbar = NavigationToolbar2Tk(canvas, self.page)
        toolbar.update()
        canvas._tkcanvas.pack(fill=BOTH, expand=1)
        # 关闭数据库连接
        cur.close()
        conn.close()

    # 跳转到前一幅图
    def lastPage(self):
        self.page.destroy()
        InfoFigure2(self.root)

    # 跳转到后一幅图
    def nextPage(self):
        self.page.destroy()
        InfoFigure4(self.root)

#绘制的第四幅图
class InfoFigure4(object):
    def __init__(self, master=None):
        self.root = master
        self.root.geometry('1600x900')
        self.createPage()

    def createPage(self):
        self.page = Frame(self.root)
        self.page.pack(fill=BOTH, expand=1)
        conn = mysql.connector.connect(user='root', password='mysqlpasswd', database='taobao')
        cur = conn.cursor()
        fig4 = plt.figure(figsize=(20, 7))
        #商品价格对销量的影响
        sql4="select price,sales from "+Process.goods+" where sales<=10000;"
        cur.execute(sql4)
        result4=cur.fetchall()
        price4 = [n4[0] for n4 in result4]
        sales4 = [n4[1] for n4 in result4]
        plt.scatter(price4,sales4,color='steelblue')
        plt.xlabel('价格',fontsize=16)
        plt.ylabel('销量',fontsize=16)
        plt.title('价格对商品销量的影响',fontsize=18)
        btn_last3 = Button(self.page, text='上一张图', font=("微软雅黑 10"), width=8, height=1, command=self.lastPage)
        btn_next4 = Button(self.page, text='下一张图', font=("微软雅黑 10"), width=8, height=1, command=self.nextPage)
        btn_next4.pack(side=BOTTOM)
        btn_last3.pack(side=BOTTOM)
        canvas = FigureCanvasTkAgg(fig4, master=self.page)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=BOTH, expand=1)
        toolbar = NavigationToolbar2Tk(canvas, self.page)
        toolbar.update()
        canvas._tkcanvas.pack(fill=BOTH, expand=1)
        # 关闭数据库连接
        cur.close()
        conn.close()

    # 跳转到前一幅图
    def lastPage(self):
        self.page.destroy()
        InfoFigure3(self.root)

    # 跳转到后一幅图
    def nextPage(self):
        self.page.destroy()
        InfoFigure5(self.root)

#绘制的第五幅图
class InfoFigure5(object):
    def __init__(self, master=None):
        self.root = master
        self.root.geometry('1600x900')
        self.createPage()

    def createPage(self):
        self.page = Frame(self.root)
        self.page.pack(fill=BOTH, expand=1)
        conn = mysql.connector.connect(user='root', password='mysqlpasswd', database='taobao')
        cur = conn.cursor()
        fig5 = plt.figure(figsize=(20, 7))
        # 不同省份的商品数量分布
        sql5=" select loc,count(*) as num from ((select * from "+Process.goods+" where loc <> '美国' and loc <> '日本') as a) group by loc order by num desc limit 15;"
        cur.execute(sql5)
        result5=cur.fetchall()
        loc4 = [n4[0] for n4 in result5]
        num4 = [n4[1] for n4 in result5]
        plt.bar(loc4,num4,color='steelblue')
        plt.xlabel('商家所在地',fontsize=16)
        plt.ylabel('商品数量',fontsize=16)
        plt.title('不同地区对应的商品数量分布',fontsize=18)
        btn_last4 = Button(self.page, text='上一张图', font=("微软雅黑 10"), width=8, height=1, command=self.lastPage)
        btn_next5 = Button(self.page, text='下一张图', font=("微软雅黑 10"), width=8, height=1, command=self.nextPage)
        btn_next5.pack(side=BOTTOM)
        btn_last4.pack(side=BOTTOM)
        canvas = FigureCanvasTkAgg(fig5, master=self.page)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=BOTH, expand=1)
        toolbar = NavigationToolbar2Tk(canvas, self.page)
        toolbar.update()
        canvas._tkcanvas.pack(fill=BOTH, expand=1)
        # 关闭数据库连接
        cur.close()
        conn.close()

    # 跳转到前一幅图
    def lastPage(self):
        self.page.destroy()
        InfoFigure4(self.root)

    # 跳转到下一幅图
    def nextPage(self):
        self.page.destroy()
        InfoFigure6(self.root)


# 绘制的第六幅图
class InfoFigure6(object):
    def __init__(self, master=None):
        self.root = master
        self.root.geometry('1600x900')
        self.createPage()

    def createPage(self):
        self.page = Frame(self.root)
        self.page.pack(fill=BOTH, expand=1)
        conn = mysql.connector.connect(user='root', password='mysqlpasswd', database='taobao')
        cur = conn.cursor()
        fig6 = plt.figure(figsize=(30, 12))
        sql1 = "select title from "+Process.goods+";"
        cur.execute(sql1)
        result = cur.fetchall()
        titles = []
        for (tt,) in result:
            tt_cut = jieba.lcut(tt)
            titles.append(tt_cut)

        # 去重，每个标题分割后词唯一
        titles_clean = []
        for i in titles:
            i_clean = []
            for word in i:
                if word not in i_clean:
                    i_clean.append(word)
            titles_clean.append(i_clean)

        # 将所有词放入一个list中
        allwords = []
        for i in titles_clean:
            for word in i:
                allwords.append(word)

        wl_space_split = " ".join(allwords)
        font = r'C:\Windows\Fonts\simhei.ttf'
        my_wordcloud = WordCloud(font_path=font, background_color='white',collocations=FALSE, scale=3,width=800, height=400).generate(
            wl_space_split)
        plt.imshow(my_wordcloud)
        plt.axis("off")
        plt.title('商品名称词云', fontsize=40)
        btn_last5 = Button(self.page, text='上一张图', font=("微软雅黑 10"), width=8, height=1, command=self.lastPage)
        btn_backprocess = Button(self.page, text='返回选择品类页面', font=("微软雅黑 10"), width=15, height=1,command=self.backProcess)
        btn_exit2 = Button(self.page, text='退出', font=("微软雅黑 10"), width=8, height=1, command=exit)

        btn_backprocess.pack(side=BOTTOM)
        btn_exit2.pack(side=BOTTOM)
        btn_last5.pack(side=BOTTOM)
        canvas = FigureCanvasTkAgg(fig6, master=self.page)
        canvas.draw()
        canvas.get_tk_widget().pack(side=TOP)
        toolbar = NavigationToolbar2Tk(canvas, self.page)
        toolbar.update()
        canvas._tkcanvas.pack(fill=BOTH, expand=1)
        # 关闭数据库连接
        cur.close()
        conn.close()

    # 跳转到前一幅图
    def lastPage(self):
        self.page.destroy()
        InfoFigure5(self.root)

    #返回商品品类输入页面
    def backProcess(self):
        self.page.destroy()
        Process(self.root)


if __name__ == '__main__':
    window=Tk()
    img=PIL.Image.open('D:/Softwares/pycharm/pycmProjects/taobaocrawler/beijing.png')
    image_file=PIL.ImageTk.PhotoImage(img)
    #window.title("欢迎使用淘宝商品数据爬取系统")
    BaseDesk(window)
    window.mainloop()

