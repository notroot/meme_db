from flask import Flask, request, session, g, redirect, url_for, \
     abort, render_template, flash, jsonify, json
from werkzeug.contrib.fixers import ProxyFix
import sqlite3
import os
from string import join
from random import choice
from datetime import datetime

app = Flask(__name__)

app.config.update(dict(
    DEBUG=True,
	DATABASE=os.path.join(app.root_path, 'meme.db'),
	SECRET_KEY='testkey',
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

# gets list of images to use for thuumbnail view on main pages
# returns list with title, img_id and path to thumbnail
# takes offset and count as optional values
def getImageThumbs(count=20, offset=0):

    db = getDB()
    cur = db.execute("SELECT title, imgid, path_thumb FROM images ORDER BY title LIMIT ? OFFSET ?", (count,offset))

    rows = cur.fetchall()
    cur.close()

    images = []
    for row in rows:
        images.append(row)

    return images

# returns info for image from id number
def getImageByID(imgid):
    db = getDB()
    cur = db.execute("SELECT title, imgid, path, date_added, rating FROM images WHERE imgid=?", (imgid,))

    img = cur.fetchone()
    cur.close()

    return img

# returns image info from obfuscated string
def getObfuscate(key):
    db = getDB()
    cur = db.execute("SELECT i.imgid, i.title, i.path FROM images i, meme m WHERE m.imgid=i.imgid AND m.id=?", (key,))

    img = cur.fetchone()
    cur.close()

    return img

# generate a six character string to use in obfuscated url_for
# doesn't yet check to make sure the key isn't already in use
def genObString():
    length = 6
    characters = "abcdefghijklmnoprstuvwyzABCDEFGHIJKLMNOPRSTUVWYZ"
    string = ''.join(choice(characters) for i in range(length))

    return string

# generates a new URL for an obfuscation of an existing image
def generatetObURL(img_id):
    db = getDB()

    cur = db.execute("SELECT imgid FROM images WHERE imgid=?", (img_id,))

    img = cur.fetchone()
    if img:
        string = genObString()
        db.execute("INSERT INTO meme (id, imgid, created) VALUES (?,?,?)", (string, img_id, datetime.now() ))
        db.commit()
    else:
        string = None

    cur.close()
    return string

###############################################################################
# Route handing logic
###############################################################################
@app.route('/')
def hello_world():

    if request.args.get("i"):
        return redirect("/%s" % request.args["i"])

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
def parse_ask(var):

    back=request.referrer

    if var.isdigit():
        img = getImageByID(var)
        if img:
            return render_template('show_single.html', image=img, back=back)
        else:
            flash('Image not found, dumping you back home')
            return redirect(request.url_root)
    else:
        img = getObfuscate(var)
        if img:
            return render_template('show_ob.html', image=img)
        else:
            return render_template('show_error.html', error_message="Obfuscation not found")

@app.route('/gen/<img_id>')
def parseGen(img_id):

    img = getImageByID(img_id)
    if img:
        string = generatetObURL(img_id)
        new_ob_url = "%s%s" % (request.url_root, string)
        return redirect(new_ob_url)
    else:
        return render_template('show_error.html', error_message="Can't do that sir")

app.wsgi_app = ProxyFix(app.wsgi_app)
if __name__ == '__main__':
    app.run("0.0.0.0")
