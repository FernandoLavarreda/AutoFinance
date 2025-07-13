#!./venv/bin/python3
#App to keep track of personal finances
#Fernando Lavarreda

import os
import sys
import shutil
import render
import read_inputs
import database as db
import sqlite3 as sql
from datetime import datetime
from argon2 import PasswordHasher
from flask import Flask, render_template, request, redirect, url_for, send_file


app = Flask(__name__)
passwd = os.environ["DBPASSWORD"]
passwd2 = os.environ["DBPASSWORD2"]
DATABASE = os.environ["DATABASE"]
DATA_SOURCE = os.environ["DATASOURCE"]
statics = os.path.join(os.path.dirname(os.path.abspath(__file__)), "static")


def cleanup(loc:str):
    assert os.path.isdir(loc), f"'{loc}' is not a directory"
    for f in os.listdir(loc):
        file_loc = os.path.join(statics, f)
        if os.path.isfile(file_loc):
            try:
                os.remove(file_loc)
            except Exception:
                pass
        else:
            shutil.rmtree(file_loc, ignore_errors=True)
    return


def startup():
    if os.path.dirname(DATABASE):
        assert os.access(os.path.dirname(DATABASE), os.W_OK), f"Cannot create database"
    if not os.path.isfile(DATABASE):
        db.init(DATABASE)
        if os.path.isfile(DATA_SOURCE):
            cn = sql.connect(DATABASE)
            cur = cn.cursor()
            types = db.get_types(cursor=cur)
            with open(DATA_SOURCE) as fd:
                entries = fd.readlines()
                records = db.load(entries, types, delimiter='|')
            db.insert(cur, records)
            cn.commit()
            cn.close()
    if not os.path.isdir(statics):
        os.mkdir(statics)
    return


with app.app_context():
    startup()


@app.route("/", methods=["GET", "POST"])
def home():
    customization = {"page_name":"[AutoFinance]", "home":True}
    if request.method != "POST": 
        return render_template("index2.html", **customization)
    pwh = PasswordHasher()
    try:
        assert "password" in request.form, "" 
        pwh.verify(passwd, request.form["password"])
    except Exception:
        return render_template("index2.html", **customization)
    try:
        cn = sql.connect(DATABASE)
    except Exception:
        return render_template("index2.html", **customization)
    cleanup(statics)
    cur = cn.cursor()
    context = render.main_report(cur)
    cn.close()
    return render_template("index.html", **context, **customization)


@app.route("/insert", methods=["GET", "POST"])
def insert():
    customization = {"addcss":True, "page_name":"Insert Records", "insert":True}
    try:
        cn = sql.connect(DATABASE)
    except Exception:
        return render_template("insert.html", **customization)
    cur = cn.cursor()
    options = render.list_types(cur)
    types = db.get_types(cursor=cur)
    cn.close()
    if request.method != "POST": 
        return render_template("insert.html", options=options, **customization)
    pwh = PasswordHasher()
    try:
        assert "password" in request.form, "" 
        pwh.verify(passwd, request.form["password"])
    except Exception:
        return render_template("insert.html", msg=render.err("Incorrect Password"), options=options, **customization)
    if "file" in request.files and request.files["file"].filename.strip():
        cn = sql.connect(DATABASE)
        cur = cn.cursor()
        try:
            file_cn = request.files["file"].read().decode()
            entries = file_cn.split("\n")
            records = db.load(entries, types, delimiter='|')
            db.insert(cursor=cur, records=records)
            cn.commit()
            cn.close()
            return render_template("insert.html", options=options,\
                                msg=render.success(f"Inserted: {len(records)} records"), **customization)
        except Exception as e:
            print(e)
            sys.stdout.flush()
            cn.close()
            return render_template("insert.html", msg=render.err("Could not process file"),\
                                   options=options, **customization)
    try:
        record = read_inputs.read_insert(request.form, types=types)
    except Exception as e:
        return render_template("insert.html", msg=render.err(str(e)), options=options, **customization)
    cn = sql.connect(DATABASE)
    cur = cn.cursor()
    db.insert(cursor=cur, records=record)
    cn.commit()
    cn.close()
    return render_template("insert.html", options=options, msg=render.success("Inserted record"), **customization)


@app.route("/delete", methods=["GET", "POST"])
def delete():
    customization = {"addcss":True, "page_name":"Delete Records", "delete":True}
    try:
        cn = sql.connect(DATABASE)
    except Exception:
        return render_template("delete.html", **customization)
    cur = cn.cursor()
    options = render.list_types(cur)
    cn.close()
    if request.method != "POST": 
        return render_template("delete.html", options=options, **customization)
    pwh = PasswordHasher()
    try:
        assert "password" in request.form, "" 
        pwh.verify(passwd, request.form["password"])
    except Exception:
        return render_template("delete.html", msg=render.err("Incorrect Password"), options=options, **customization)
    try:
        params = read_inputs.read_delete(request.form)
    except Exception as e:
        return render_template("delete.html", msg=render.err(str(e)), options=options, **customization)
    cn = sql.connect(DATABASE)
    cur = cn.cursor()
    db.delete(cursor=cur, **params)
    cn.commit()
    cn.close()
    return render_template("delete.html", msg=render.success(f"Deleted record(s)"), options=options, **customization)


@app.route("/custom", methods=["GET", "POST"])
def custom():
    customization = {"addcss":True, "page_name":"Custom Reports", "custom":True}
    try:
        cn = sql.connect(DATABASE)
    except Exception:
        return render_template("custom2.html", **customization)
    cur = cn.cursor()
    options = render.list_types(cur)
    cn.close()
    if request.method != "POST": 
        return render_template("custom2.html", options=options, **customization)
    pwh = PasswordHasher()
    try:
        assert "password" in request.form, "" 
        pwh.verify(passwd, request.form["password"])
    except Exception:
        return render_template("custom2.html", msg=render.err("Incorrect Password"), options=options, **customization)
    try:
        params = read_inputs.read_custom(request.form)
    except Exception as e:
        return render_template("custom2.html", msg=render.err(str(e)), options=options, **customization)
    cleanup(statics)
    cn = sql.connect(DATABASE)
    cur = cn.cursor()
    context = render.custom_report(cursor=cur, **params)
    cn.close()
    return render_template("custom.html", options=options,  **customization, **context)


@app.route("/all", methods=["GET", "POST"])
def see():
    customization = {"page_name":"See Records", "see":True}
    if request.method != "POST": 
        return render_template("see.html", **customization)
    pwh = PasswordHasher()
    backup = False
    try:
        assert "password" in request.form, "" 
        try:
            pwh.verify(passwd, request.form["password"])
        except Exception:
            pwh.verify(passwd2, request.form["password"])
            backup = True
    except Exception:
        return render_template("see.html", table=render.err("Incorrect Password"), **customization)
    try:
        cn = sql.connect(DATABASE)
    except Exception:
        return render_template("see.html", **customization)
    cur = cn.cursor()
    if backup:
        file = render.backup(cur)
        cn.close()
        return send_file(file, as_attachment=True, download_name=f"backup_{datetime.today().strftime('%F')}.csv")
    context = render.table(cur)
    cn.close()
    return render_template("see.html", table=context, **customization)


@app.route("/<invalid>", methods=["GET"])
def invalid(invalid):
    return redirect(url_for('home'))

