from flask import Flask,render_template
import sqlite3
import jieba
from matplotlib import pyplot as plt
from wordcloud import WordCloud
import numpy as np
from PIL import Image
import threading


app = Flask(__name__)

@app.route('/')
def root():
    return render_template('temp.html')

@app.route('/index')
def index():
    return render_template('index.html')

@app.route('/movie')
def movie():
    datalist = []
    con = sqlite3.connect('douban.db')
    cur = con.cursor()
    sql = "select * from movie250"
    data = cur.execute(sql)
    for item in data:
        datalist.append(item)
    cur.close()
    con.close()
    return render_template('movie.html',movies=datalist)

@app.route('/word')

def word():
    def wordcloud():
        con = sqlite3.connect('douban.db')
        cur = con.cursor()
        sql = "select instroduction from movie250"
        data = cur.execute(sql)
        text = ''
        for item in data:
            text += item[0]
        cur.close()
        con.close()
        cut = jieba.cut(text)
        string = ' '.join(cut)
        img = Image.open(r'./static/assets/img/tree.jpg')
        img_array = np.array(img)
        wc = WordCloud(
            background_color='white',
            mask = img_array,
            font_path='/home/yzx/PycharmProjects/douban_flask/templates/MSYH.TTF'
        )
        wc.generate_from_text(string)

        #绘制图片
        fig = plt.figure(1)
        plt.imshow(wc)
        plt.axis('off')
        plt.show()
        # plt.savefig('./static/assets/img/word.jpg',dpi=500)
    t = threading.Thread(target=wordcloud,name='wordcloud',daemon=True)
    t.start()

    return render_template('word.html')

@app.route('/team')
def team():
    return render_template('team.html')

@app.route('/score')
def score():
    score = []
    count = []
    con = sqlite3.connect('douban.db')
    cur = con.cursor()
    sql = "select score,count(score) from movie250 group by score"
    data = cur.execute(sql)
    for item in data:
        score.append(item[0])
        count.append(item[1])
    cur.close()
    con.close()
    return render_template('score.html',score=score,count=count)


if __name__ == '__main__' :
    app.run()
