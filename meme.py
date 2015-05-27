from flask import Flask, request, session, g, redirect, url_for, \
     abort, render_template, flash, jsonify, json
from werkzeug.contrib.fixers import ProxyFix
import sqlite3
import os


app = Flask(__name__)

app.config.update(dict(
    DEBUG=True,
	DATABASE=os.path.join(app.root_path, 'meme.db'),
))

# DB logic for setting up database connection and teardown
def connectDB():
	rv = sqlite3.connect(app.config['DATABASE'])
	rv.row_factory = sqlite3.Row
	return rv

def getDB():
	if not hasattr(g, 'sqlite_db'):
		g.sqlite_db = connectDB()
	return g.sqlite_db

@app.teardown_appcontext
def closeDB(error):
	if hasattr(g, 'sqlite_db'):
		g.sqlite_db.close()


def getPageCount():
    db = getDB()
    cur = db.execute("SELECT count(*) as count FROM images")
    row = cur.fetchone()
    cur.close()

    count = row['count']

    pages = count % 20

    return pages

def getImageThumbs(count=20, offset=0):

    db = getDB()
    cur = db.execute("SELECT title, imgid, path_thumb FROM images ORDER BY title LIMIT ? OFFSET ?", (count,offset))

    rows = cur.fetchall()
    cur.close()

    images = []
    for row in rows:
        images.append(row)

    return images

def getImageByID(imgid):
    db = getDB()
    cur = db.execute("SELECT title, imgid, path, date_added, rating FROM images WHERE imgid=?", (imgid,))

    img = cur.fetchone()
    cur.close()

    return img

def getObfuscate(key):
    db = getDB()
    cur = db.execute("SELECT i.imgid, i.title, i.path FROM images i, meme m WHERE m.imgid=i.imgid AND m.id=?", (key,))

    img = cur.fetchone()
    cur.close()

    return img


@app.route('/')
def hello_world():

    if request.args.get("p"):
        p = int(request.args['p'])
        if p > 1:
            offset = (p -1) * 20
        else:
            offset = 0
            
        thumbs= getImageThumbs(20, offset)
    else:
        p=1
        thumbs = getImageThumbs()

    return render_template('show_main.html', thumbs=thumbs, page_count=getPageCount(), p=p)

@app.route('/<var>')
def parse_ask(var=None):

    if var.isdigit():
        img = getImageByID(var)
        return render_template('show_single.html', image=img)
    else:
        img = getObfuscate(var)
        return render_template('show_ob.html', image=img)


app.wsgi_app = ProxyFix(app.wsgi_app)
if __name__ == '__main__':
    app.run("0.0.0.0")
