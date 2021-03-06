# _*_ coding:utf-8 _*_

import os
import pdb
import sqlite3
from flask import Flask, request, session, g, redirect, url_for, abort, \
render_template, flash

app = Flask(__name__)

app.config.update(dict(
    DATABASE = os.path.join(app.root_path, 'practise.db'),
    DEBUG = True,
    SECRET_KEY = 'development key',
    USERNAME = 'admin',
    PASSWORD = 'default'
))

app.config.from_object(__name__)
#app.config.from_envvar('FLASKR_SETTINGS',silent=True)

def connect_db():
    rv = sqlite3.connect(app.config['DATABASE'])
    rv.row_factory = sqlite3.Row
    return rv

def init_db():
    with app.app_context():
        db = get_db()
    with app.open_resource('schema.sql', mode='r') as f:
        db.cursor().executescript(f.read())
    db.commit()

@app.cli.command('initdb')
def initdb_command():
    init_db()
    print('Initialized the database.')

def get_db():
    if not hasattr(g,'sqlite_db'):
        g.sqlite_db = connect_db()
    return g.sqlite_db

@app.teardown_appcontext
def close_db(error):
    if hasattr(g,'sqlite_db'):
        g.sqlite_db.close()

#视图
@app.route('/')
def index():
    return render_template('index.html')
'''
def show_entries():
    db = get_db()
    cur = db.execute('select title, text from entries order by id desc')
    entries = cur.fetchall()
    return render_template('show_entries.html', entries=entries)
'''
@app.route('/add', methods=['POST'])
def add_entry():
    if not session.get('logged_in'):
        abort(401)
    db = get_db()
    db.execute('insert into entries(title,text) values (?,?)'), [request.form['title'],request.form['text']]
    db.commit()
    flash('New entry was sucdessfully posted')
    return redirect(url_for('show_entries'))

#登录和登出模块
@app.route('/login',methods=['GET','POST'])
def login():
    error = None
    if request.method =='POST':
        if request.form['username'] != app.config['USERNAME']:
            error = 'Invalid username'
        elif request.form['password'] != app.config['PASSWORD']:
            error = 'Invalid password'
        else:
            session['logged_in'] = True
    return render_template('login.html',error=error)

@app.route('/logout')
def logout():
    session.pop('logged_in',None)
    flash('You were logged out')
    return redirect(url_for('show_entries'))


if __name__ == '__main__':
    app.run(host='0.0.0.0')