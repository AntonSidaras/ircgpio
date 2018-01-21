# -*- coding: utf-8 -*-
configuration = "/usr/lib/python3.5/ircgpio/config.txt"
keywords = ["[global]","[record]","[rc]","[data]"]
subkeywords = ["[buttons]"]

globparameters = ["rcontrols", "rcrec", "double_calibration"]
subparams = ["folder", "codes", "buttons"]

variants = ["on","off"]
on = variants[0]
off = variants[1]

oglobal = keywords[0]
record = keywords[1]
rc = keywords[2]
data = keywords[3]

bu = subkeywords[0]

rcontrols = globparameters[0]
rcrec = globparameters[1]
double_calibration = globparameters[2]

folder = subparams[0]
codes = subparams[1]
button = subparams[2]