#!./venv/bin/python3
#Fernando Lavarreda

import os
import uuid
import graph
import sqlite3 as sql
import database as db
from io import BytesIO
from datetime import datetime


def err(msg:str):
    return f'<p class="h6 text-danger">{msg}</p>'


def success(msg:str):
    return f'<p class="h6 text-success">{msg}</p>'


def list_types(cursor:sql.Cursor):
    types = db.get_types(cursor)
    html = ""
    for type_ in types:
        html+=f'<option value="{type_}">{type_}</option>'
    return html

def nullify(input_):
    if type(input_) in {int, float} or input_:
        if type(input_) == list:
            input_ = input_[0][0]
        try:
            rnd = round(input_, 2)
        except Exception:
            return input_
        return rnd
    return "-"

def main_report(cursor:sql.Cursor, static_dir:str="./static"):
    context = {}
    context["records"] = db.get_count(cursor)
    context["inflow"] = nullify(db.sum_sign(cursor, select="positive"))
    context["outflow"] = nullify(db.sum_sign(cursor, select="negative"))
    context["netflow"] = nullify(db.sum_sign(cursor))
    context["historic"] = os.path.join(static_dir, str(uuid.uuid4())+".png")
    context["monthly_flow"] = os.path.join(static_dir, str(uuid.uuid4())+".png")
    context["cumulative"] = os.path.join(static_dir, str(uuid.uuid4())+".png")
    historic = db.cumulative(cursor)
    flows = db.monthly_flow(cursor, force_end_date=datetime.today())
    cumulative_pos = db.cumulative(cursor, select="positive")
    cumulative_neg = db.cumulative(cursor, select="negative")
    context["historic"] = os.path.basename(graph.series(historic, color="blue", save=context["historic"]))
    context["monthly_flow"] = os.path.basename(graph.series(flows, color="golden", save=context["monthly_flow"]))
    context["cumulative"] = os.path.basename(graph.mseries([cumulative_pos, cumulative_neg],colors=["green", "red"],\
                            labels=["Inflow", "Outflow"], save=context["cumulative"], absolute=True))

    context["medianinf"] = nullify(db.monthly_flow_median(cursor, force_end_date=datetime.today(), select="positive"))
    context["meaninf"] = nullify(db.monthly_flow_mean(cursor, force_end_date=datetime.today(), select="positive"))
    context["stdinf"] = nullify(db.monthly_flow_sd(cursor, force_end_date=datetime.today(), select="positive"))
    context["maxinf"] = nullify(db.monthly_flow_max(cursor, force_end_date=datetime.today(), select="positive"))

    context["medianou"] = nullify(db.monthly_flow_median(cursor, force_end_date=datetime.today(), select="negative"))
    context["meanou"] = nullify(db.monthly_flow_mean(cursor, force_end_date=datetime.today(), select="negative"))
    context["stdou"] = nullify(db.monthly_flow_sd(cursor, force_end_date=datetime.today(), select="negative"))
    context["maxou"] = nullify(db.monthly_flow_min(cursor, force_end_date=datetime.today(), select="negative"))

    context["mediannet"] = nullify(db.monthly_flow_median(cursor, force_end_date=datetime.today()))
    context["meannet"] = nullify(db.monthly_flow_mean(cursor, force_end_date=datetime.today()))
    context["stdnet"] = nullify(db.monthly_flow_sd(cursor, force_end_date=datetime.today()))
    context["maxnet"] = nullify(db.monthly_flow_max(cursor, force_end_date=datetime.today()))
    context["minnet"] = nullify(db.monthly_flow_min(cursor, force_end_date=datetime.today()))

    context["medianin"] = nullify(db.get_median(cursor, type_="Income"))
    context["meanin"] = nullify(db.get_avg(cursor, type_="Income"))
    context["stdin"] = nullify(db.get_std(cursor, type_="Income"))
    context["maxin"] = nullify(db.get_max(cursor, type_="Income"))

    context["medianne"] = nullify(db.get_median(cursor, type_="Necessity"))
    context["meanne"] = nullify(db.get_avg(cursor, type_="Necessity"))
    context["stdne"] = nullify(db.get_std(cursor, type_="Necessity"))
    context["maxne"] = nullify(db.get_min(cursor, type_="Necessity"))

    context["medianpe"] = nullify(db.get_median(cursor, type_="Pleasure"))
    context["meanpe"] = nullify(db.get_avg(cursor, type_="Pleasure"))
    context["stdpe"] = nullify(db.get_std(cursor, type_="Pleasure"))
    context["maxpe"] = nullify(db.get_min(cursor, type_="Pleasure"))

    context["medianinv"] = nullify(db.get_median(cursor, type_="Investment"))
    context["stdinv"] = nullify(db.get_std(cursor, type_="Investment"))
    context["maxinv"] = nullify(db.get_max(cursor, type_="Investment"))
    context["mininv"] = nullify(db.get_min(cursor, type_="Investment"))

    context["medianem"] = nullify(db.get_median(cursor, type_="Emergency"))
    context["meanem"] = nullify(db.get_avg(cursor, type_="Emergency"))
    context["stdem"] = nullify(db.get_std(cursor, type_="Emergency"))
    context["maxem"] = nullify(db.get_min(cursor, type_="Emergency"))
    return context


def custom_report(cursor:sql.Cursor, static_dir:str="./static", force_end_date:datetime=None, **kwargs):
    context = {}
    context["records"] = db.get_count(cursor, **kwargs)
    context["sum"] = nullify(db.sum_sign(cursor, **kwargs))
    context["median"] = nullify(db.get_median(cursor, **kwargs))
    context["mean"] = nullify(db.get_avg(cursor, **kwargs))
    context["std"] = nullify(db.get_std(cursor, **kwargs))
    context["monthly_flow"] = os.path.join(static_dir, str(uuid.uuid4())+".png")
    context["daily_flow"] = os.path.join(static_dir, str(uuid.uuid4())+".png")
    context["cumulative"] = os.path.join(static_dir, str(uuid.uuid4())+".png")
    mflows = db.monthly_flow(cursor, force_end_date=force_end_date, **kwargs)
    dflows = db.daily_flow(cursor, **kwargs)
    cumulative = db.cumulative(cursor, **kwargs)
    context["monthly_flow"] = os.path.basename(graph.series(mflows, color="golden", save=context["monthly_flow"]))
    context["daily_flow"] = os.path.basename(graph.series(dflows, color="#6432a8", scatter=True, save=context["daily_flow"]))
    context["cumulative"] = os.path.basename(graph.series(cumulative, color="blue", save=context["cumulative"]))
    min_ = db.get_min(cursor, limit=5, **kwargs)
    max_ = db.get_max(cursor, limit=5, **kwargs)
    title = """<table class="table table-dark table-striped">
            <thead><tr><th>Amount</th><th>Description</th><th>Type</th><th>Date</th></tr></thead><tbody>"""
    if min_:
        tbmin = title
        for mn in min_:
            tbmin += f'<tr><td>{mn[0]}</td><td>{mn[2]}</td><td>{mn[1]}</td><td>{mn[3]}</td></tr>'
        min_ = tbmin+'</tbody></table>'
    else:
        min_ = f'<div class="row"><div class="col"></div><div class="col">-</div></div>'
    if max_:
        tbmax = title
        for mx in max_:
            tbmax += f'<tr><td>{mx[0]}</td><td>{mx[2]}</td><td>{mx[1]}</td><td>{mx[3]}</td></tr>'
        max_ = tbmax+'</tbody></table>'
    else:
        max_ = f'<div class="row"><div class="col"></div><div class="col">-</div></div>'
    context["min"] = min_
    context["max"] = max_

    context["medianmo"] = nullify(db.monthly_flow_median(cursor, force_end_date=force_end_date, **kwargs))
    context["meanmo"] = nullify(db.monthly_flow_mean(cursor, force_end_date=force_end_date, **kwargs))
    context["stdmo"] = nullify(db.monthly_flow_sd(cursor, force_end_date=force_end_date, **kwargs))
    context["maxmo"] = nullify(db.monthly_flow_max(cursor, force_end_date=force_end_date, **kwargs))
    context["minmo"] = nullify(db.monthly_flow_min(cursor, force_end_date=force_end_date, **kwargs))
    return context


def backup(cursor:sql.Cursor)->BytesIO:
    data = db.peek(cursor, limit=-1)
    header = "|".join(["type", "description", "amount", "date"])
    body = "\n"
    for record in data:
        body+="|".join([str(rd) for rd in record])+"\n"
    return BytesIO((header+body).encode())


def table(cursor:sql.Cursor)->str:
    data = db.peek(cursor)
    if data:
        html = """<table class="table table-dark table-striped">
                <thead><tr><th>Type</th><th>Description</th><th>Amount</th><th>Date</th></tr></thead>"""
    else:
        html = 	'<div class="col"><p class="h4">No Data Available</p></div>'
    for d in data:
        row = f'<tr><td>{d[0]}</td><td>{d[1]}</td><td>{d[2]}</td><td>{d[3]}</td></tr>' 
        html+=row
    if data:
        html+="</table>"
    return html
