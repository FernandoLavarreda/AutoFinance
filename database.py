#!./venv/bin/python3
#Fernando Lavarreda

import os
import sqlite3 as sql
from datetime import datetime
from dataclasses import dataclass
from typing import Iterable, ClassVar


@dataclass
class Record:
    CLIMIT:ClassVar = 150 
    type_:int
    description:str
    amount:float
    date:str


def create_record(type_:str, description:str, amount:str, date:str, types:dict[str, int])->Record:
    if description.strip() == "":
        raise ValueError("Cannot enter empty description")
    try:
        amount = float(amount)
    except Exception:
        raise ValueError("Amount must be a real number")
    try:
        date = datetime.strptime(date, "%Y-%m-%d")
    except Exception:
        raise ValueError("Date must be formatted as YYYY-MM-DD")
    if type_.title() not in types:
        raise ValueError(f"Type must be: {','.join(list(types.keys()))}")
    description = description[:Record.CLIMIT].strip()
    typ = types[type_.title()]
    date = date.strftime("%Y-%m-%d")
    return Record(typ, description, amount, date)


def init(location:str):
    assert not os.path.isfile(location), f"File: '{location}' already exists"
    cn = sql.connect(location)
    cursor = cn.cursor()
    cursor.execute("CREATE TABLE types(id INTEGER PRIMARY KEY AUTOINCREMENT, type TEXT);")
    cursor.execute("CREATE TABLE records(\
                                         id INTEGER PRIMARY KEY AUTOINCREMENT,\
                                         type INTEGER,\
                                         description TEXT,\
                                         amount REAL,\
                                         date TEXT);")
    cursor.execute("INSERT INTO types(type) VALUES('Income'),('Necessity'),('Pleasure'),('Investment'),('Emergency');")
    cn.commit()
    cn.close()
    return


def insert(cursor:sql.Cursor, records:list[Record]):
    cursor.executemany("INSERT INTO records(type, description, amount, date) VALUES(?,?,?,?);", [(r.type_, r.description, r.amount, r.date) for r in records])
    return


def delete(cursor:sql.Cursor, date:str, type_:str, description:str=""):
    types = get_types(cursor)
    if type_ not in types:
        return False
    cursor.execute("DELETE FROM records WHERE records.date=? AND type=? AND description LIKE '%' ||?|| '%';", (date, types[type_], description))
    return True


def load(data:Iterable[str], types:dict[str, int], delimiter:str=",")->list[Record]:
    records = []
    for line in data:
        args = line.strip().split(delimiter)
        try:
            record = create_record(*args, types=types)
        except Exception as e:
            print(f"{e} for record: {line}")
        else:
            records.append(record)
    return records


def peek(cursor:sql.Cursor, limit:int=30)->list[list[str]]:
    records = []
    if limit == -1:
        records = cursor.execute("SELECT types.type, records.description, records.amount, records.date FROM records\
                                  LEFT JOIN types ON records.type=types.id ORDER BY records.date DESC;")
    elif limit > 0:
        records = cursor.execute("SELECT types.type, records.description, records.amount, records.date FROM records\
                                  LEFT JOIN types ON records.type=types.id ORDER BY records.date DESC LIMIT ?;", (limit,))
    return list(records)
    

def get_types(cursor:sql.Cursor)->dict[str, int]:
    rs = cursor.execute("SELECT id,type FROM types")
    types = {}
    for r in rs:
        id_ = r[0]
        type_ = r[1]
        types[type_] = id_
    return types


def date_predicate(start:datetime=None, end:datetime=None):
    params = []
    predicate = ""
    if type(start) != type(None) and type(end) != type(None):
        assert start<=end, f"Start must be before or equal to end date"
        predicate = "date(records.date)>=? AND date(records.date)<=?"
        params = [start, end]
    elif type(start) == type(end):
        predicate = ""
        params = []
    elif type(start) != type(None):
        predicate = "date(records.date)>=?"
        params = [start,]
    else:
        predicate = "date(records.date)<=?"
        params = [end,]
    return predicate, params


def select_predicate(select:str=""):
    selects = {
            "positive":"amount > 0",
            "negative":"amount < 0",
            "all":""
    }
    params = []
    if select:
        assert select in selects, f"Selection must be of kind: {','.join(list(selects.keys()))}"
        return selects[select], params
    return "", params


def type_predicate(types:dict, type_:str=""):
    params = []
    if type_:
        if type_ not in types:
            raise ValueError(f"Unrecognized type: {type_}")
        predicate = f"records.type=?"
        params.append(types[type_])
        return predicate, params
    return "", params


def apply_filters(*, cursor:sql.Cursor=None, select:str="", type_:str="", start:datetime=None, end:datetime=None):
    if cursor:
        types = get_types(cursor)
    else:
        types = {"No cursor provided":-1}
    se_pred, _ = select_predicate(select)
    date_pred, date_params = date_predicate(start, end)
    typ_pred, typ_params  = type_predicate(types, type_)
    predicate = [pred for pred in (se_pred, date_pred, typ_pred) if pred]
    params = date_params+typ_params
    if predicate:
        predicate = "WHERE "+" AND ".join(predicate)
    else:
        predicate = ""
    return predicate, params


def cumulative(cursor, **kwargs):
    pred, params = apply_filters(cursor=cursor, **kwargs)
    total = cursor.execute(f"SELECT date(records.date),SUM(amount) FROM records {pred} GROUP BY records.date ORDER BY date(records.date);", params)
    return list(total)


def sum_sign(cursor, **kwargs):
    pred, params = apply_filters(cursor=cursor, **kwargs)
    total = cursor.execute(f"SELECT SUM(amount) FROM records {pred};", params)
    return list(total)
    
    
