#!./venv/bin/python3
#Fernando Lavarreda

import numpy as np
from datetime import datetime
import matplotlib.pyplot as plt


plt.style.use("dark_background")


def mseries(records:list[list[datetime, float]], *, save:str="", labels:list[str]=[], colors:list[str]=[], absolute:bool=False):
    assert len(labels) == len(records), f"Labels should match number of series"
    colors_ = {
        "blue":"#158eb3",
        "red":"#c91224",
        "green":"#109123",
        "golden":"#e3b019",
    }
    cp = []
    for color in colors:
        color = colors_[color] if color in colors_ else color
        cp.append(color)
    if not records:
        return ""
    fig = plt.figure()
    ax = fig.subplots()
    for i, record in enumerate(records):
        if absolute:
            ys = [abs(r[1]) for r in record]
        else:
            ys = [r[1] for r in record]
        xs = np.asarray([r[0] for r in record], dtype="datetime64[s]")
        if i < len(cp):
            ax.plot(xs, ys, label=labels[i], color=cp[i])
        else:
            ax.plot(xs, ys, label=labels[i])
    ax.tick_params(axis="x", labelrotation=75)
    ax.legend(loc="upper left")
    ax.set_xlabel("Date")
    ax.set_ylabel("Money")
    fig.tight_layout()
    fig.savefig(save)
    return save


def series(records:list[datetime, float], save:str, color:str="blue", absolute:bool=False, title:str=None):
    colors = {
        "blue":"#158eb3",
        "red":"#c91224",
        "green":"#109123",
        "golden":"#e3b019",
    }
    color = colors[color] if color in colors else color
    if not records:
        return ""
    fig = plt.figure()
    ax = fig.subplots()
    if len(records) == 1:
        y = abs(records[0][1]) if absolute else records[0][1]
        ax.scatter(records[0][:1], [y,], color=color)
    else:
        if absolute:
            ys = [abs(r[1]) for r in records]
        else:
            ys = [r[1] for r in records]
        xs = np.asarray([r[0] for r in records], dtype="datetime64[s]")
        ax.plot(xs, ys, color=color)
    ax.tick_params(axis="x", labelrotation=75)
    ax.set_title(title)
    ax.set_xlabel("Date")
    ax.set_ylabel("Money")
    fig.tight_layout()
    fig.savefig(save)
    return save


def bar(xs:list[str], ins:list[float], out:list[float], save:str,\
        color_in:str="blue", color_out:str="red"):
    assert len(ins) == len(out), f"Should provide same number of inflows and outflows"
    assert len(xs) == len(out), f"Should provide same number of labels and inflows"
    colors = {
        "blue":"#158eb3",
        "red":"#c91224",
        "green":"#109123",
        "golden":"#e3b019",
    }
    color_in = colors[color_in] if color_in in colors else color_in
    color_out = colors[color_out] if color_out in colors else color_out
    if not xs:
        return ""
    width = 0.14
    label_loc = list(range(len(xs)))
    fig = plt.figure()
    ax = fig.subplots()
    heights = ax.bar(label_loc, ins, width=width, color=color_in, label="Inflow")
    ax.bar_label(heights)
    heights = ax.bar([width+l for l in label_loc], out, width=width, color=color_out, label="Outflow")
    ax.bar_label(heights)
    ax.set_xticks([l+width/2 for l in label_loc], xs)
    ax.set_ylim(0, max(ins+out)*1.05)
    ax.legend(loc="upper right")
    fig.tight_layout()
    fig.savefig(save)
    return save


