import ASUS.GPIO as GPIO
import time
import importlib

defaults = importlib.import_module('ircgpio.ircauxiliary.defaults')
parser = importlib.import_module('ircgpio.ircauxiliary.parser')

ir_sensor_th = 36

GPIO.setwarnings(False)
GPIO.setmode(GPIO.BOARD)

def clearlst(lst, str):
	for l in lst:
		if l == "":
			lst.remove(str)

def getrcsubparam(configfile, rcname, subparam):
	rcontrols = parser.getvalfromconfigbykeyword(defaults.rc, defaults.keywords, configfile, [""])
	clearlst(rcontrols, "")

	data = parser.getvalfromconfigbykeyword(defaults.data, defaults.keywords, configfile, [""])
	clearlst(data, "")		

	rc = parser.getvalfromlistbykeyword(rcname, rcontrols, data, [""])

	pairs = parser.getparametersandvals(rc, defaults.subparams, "=", [" ", "	"], ",")
	
	return parser.extractvaluebyparam(subparam, pairs)
	
pairs = parser.getparametersandvals(parser.getvalfromconfigbykeyword(defaults.oglobal,defaults.keywords,defaults.configuration,[""]), defaults.globparameters, "=", [" ", "	"], ",")
rc = parser.extractvaluebyparam(defaults.rcontrols, pairs)
rcontrols = rc[0]

codesfile = getrcsubparam(defaults.configuration, rcontrols, defaults.codes)
folder = getrcsubparam(defaults.configuration, rcontrols, defaults.folder)

sortfolder = folder[0].replace("/usr/lib/python3.5/", "")

dst = sortfolder.replace("/", ".") + "." + codesfile[0].strip('.py')

code = importlib.import_module(dst)

def getcode(pin):
	GPIO.setup(pin, GPIO.IN)
	buffer = []
	sqr = []
	buttons = list(code.btn_codes.keys())
	while True:
		tic = time.time()
		GPIO.wait_for_edge(pin, GPIO.FALLING)
		toc = time.time()
		if (toc - tic < 1):
			if ((toc - tic)*1000 < ir_sensor_th):
				buffer.append(float("{0:.3f}".format((toc - tic)*1000)))
			else:
				if (len(buffer) == code.code_len):
					i = 0
					for b in buttons:
						for digit in range(0,code.code_len):
							sqr.append(float("{0:.3f}".format((code.btn_codes.get(b)[digit] - buffer[digit])**2)))
						same = True
						for d in sqr:
							if d > 1:
								same = False
						if same == True:
							sqr.clear()
							buffer.clear()
							#print(b)
							return [b,code.btn_codes.get(b)]
							#continue
						i = i + 1
						sqr.clear()
				buffer.clear()
	
	return ["",[0]]