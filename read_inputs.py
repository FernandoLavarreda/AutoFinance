#!./venv/bin/python3
#Fernando Lavarreda
#Parse data from user inputs 


from typing import Any
from functools import partial
from datetime import datetime
from database import create_record


def read_date(date:str):
    try:
        d = datetime.strptime(date, "%Y-%m-%d")
    except Exception:
        raise ValueError(f"Could not read date: '{date}', must follow format YYYY-mm-dd")
    return d


def read_input(params:dict[str, Any], required:set, default:dict[str, Any]):
    parsed = {}
    for r in required:
        if r not in params:
            raise ValueError(f"Missing required parameter: {r.replace('_', '')}")
        parsed[r] = params[r]
    for d in default:
        if d not in params:
            parsed[d] = default[d]
        else:
            parsed[d] = params[d]
    return parsed


def read_insert(params:dict[str, str], types:dict[str, int]):
    required = {"type_", "description", "amount", "date"}
    default = {}
    parsed = read_input(params, required, default)
    parsed["types"] = types
    return [create_record(**parsed),]


def read_delete(params:dict[str, str]):
    required={"type_", "start"}
    default = {"end":None, "description":""}
    parsed = read_input(params, required, default)
    parsed["start"] = read_date(parsed["start"])
    if parsed["end"]:
        parsed["end"] = read_date(parsed["end"])
    else:
        parsed["end"] = None
    return parsed


def read_custom(params:dict[str, str]):
    required = {}
    default = {"type_":"All", "description":"", "start":None, "end":None}
    parsed = read_input(params, required, default)
    if parsed["type_"] == "All":
        parsed["type_"] = "" 
    if parsed["end"]:
        parsed["end"] = read_date(parsed["end"])
        parsed["force_end_date"] = parsed["end"]
    else:
        parsed["end"] = None
        parsed["force_end_date"] = None
    if parsed["start"]:
        parsed["start"] = read_date(parsed["start"])
    else:
        parsed["start"] = None
    return parsed
