import ASUS.GPIO as GPIO
import time
import importlib

defaults = importlib.import_module('ircgpio.ircauxiliary.defaults')
parser = importlib.import_module('ircgpio.ircauxiliary.parser')

amendment = []
GPIO.setwarnings(False)
GPIO.setmode(GPIO.BOARD)
pin=7
ir_sensor_th = 36
GPIO.setup(pin, GPIO.IN)

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
	
def makecodespyfile(filename, dict, _len, buttons):
	f = open(filename,"w")
	f.write("code_len = ")
	f.write(str(_len))
	f.write("\n")
	f.write("btn_codes = {\n")
	i = 0
	for b in buttons:
		f.write("\'")
		f.write(b)
		f.write("\' ")
		f.write(": [")
		j = 0
		for c in dict.get(b):
			f.write(str(c))
			if(j != len(dict.get(b)) - 1):
				f.write(", ")
			else:
				f.write("]")
			j = j + 1
		if(i != len(buttons) - 1):
			f.write(",\n")
		else:
			f.write("\n}")
		i = i + 1
		
	f.close()

def count(lst):
	map = []
	for l in lst:
		fq = 0
		for r in lst:
			if l == r:
				fq = fq + 1
		map.append([l,fq])
		
	res = []
	
	for i in range (0,len(map)):
		if i == 0:
			res.append(map[i])
		else:
			if map[i] not in res:
				res.append(map[i])
	
	return res
	
def findcalibrparam(lst, th):
	max = [[0,0]]
	for l in lst:
		if l[1] > max[0][1]:
			max[0] = l
			
	if max[0][1] < th:
		return -1
		
	if max[0][1] >= th:	
		return max[0][0]
		
def getmax(lst):
	max = 0
	for l in lst:
		if l > max:
			max = l
	
	return max
	
def dispersion(lst):
	max = getmax(lst)
	_disp = []
	
	for l in lst:
		if l >= 0.8 * max:
			_disp.append(max - l)
			
	disp = 0
	sum = 0
	for d in _disp:
		sum = sum + d
	
	disp = sum / len(_disp)
	_disp.clear()
	
	return disp
	
def calibration():
	buffer = []
	calibr = []
	print("Startting calibration")
	ic = 0
	while True:
		tic = time.time()
		GPIO.wait_for_edge(pin, GPIO.FALLING)
		toc = time.time()
		if (toc - tic < 1):
			if ((toc - tic)*1000 < ir_sensor_th):
				buffer.append(float("{0:.3f}".format((toc - tic)*1000)))
			else:
				print("Calibration step ", ic)
				calibr.append(len(buffer.copy()))
				buffer.clear()
				ic = ic + 1
				if ic == 11:
					ic = 0
					cparams = count(calibr.copy())
					print(cparams)
					calibr.clear()
					print("Start calibration again? (Y/any key)")
					inp = input()
					if inp == "Y":
						print("New calibration")
					else:
						cp = findcalibrparam(cparams, 5)
						if (cp == -1):
							print("Calibration parameter has hot been defined, starting calibration again")
						else:
							return cp
							
def dcalibration(p_calib):
	buffer = []
	avg = []
	ic2 = 0
	print("Startting double calibration")
	while True:
		tic = time.time()
		GPIO.wait_for_edge(pin, GPIO.FALLING)
		toc = time.time()
		if (toc - tic < 1):
			if ((toc - tic)*1000 < ir_sensor_th):
				buffer.append(float("{0:.3f}".format((toc - tic)*1000)))
			else:
				if (len(buffer) == p_calib):
					print("Double calibration step ", ic2)
					print (buffer)
					avg.append(buffer.copy()[0])
					ic2 = ic2 + 1
					if ic2 == 11:
						max = getmax(avg)
						disp = float("{0:.3f}".format(dispersion(avg)))
						avg.clear()
						res = [max, disp]
						return res
						
				buffer.clear()

def frecord(p_calib, irsteps, corr = [0,0]):
	buffer = []
	record = []
	if len(record) != 0:
		record.clear()
	print("Recording...")
	ir = 1
	while True:
		tic = time.time()
		GPIO.wait_for_edge(pin, GPIO.FALLING)
		toc = time.time()
		if (toc - tic < 1):
			if ((toc - tic)*1000 < ir_sensor_th):
				buffer.append(float("{0:.3f}".format((toc - tic)*1000)))
			else:
				max = getmax(buffer)
				if (len(buffer) == p_calib):
					if corr != [0,0]:
						print(corr)
						if max < corr[0] - corr[1]:
							continue
					print("Record step ", ir)
					print (buffer)
					record.append(buffer.copy())
					ir = ir + 1
					if ir == irsteps + 1:
						ir = 1
						tmp = []
						for i in range(0,p_calib):
							sum = 0
							for j in range (0, irsteps):
								sum = record[j][i] + sum
							tmp.append(float("{0:.3f}".format((sum)/irsteps)))
						print("Average")
						print(tmp)
						print("Save record? (Y/any key)")
						inp = input()
						if inp != "Y":
							print("New record")
							tmp.clear()
							record.clear()
						else:
							return tmp.copy()
				buffer.clear()
				
def savebutton(p_calib, buttons, corr = [0,0]):
	dict = {}
	for b in buttons:
		print("Record started for button ", b)
		code = frecord(p_calib, 3, corr)
		dict[b] = code
		print("Saved!")

	return dict


p_calib = calibration()
print("Calibration parameter = ", p_calib)


pairs = parser.getparametersandvals(parser.getvalfromconfigbykeyword(defaults.record,defaults.keywords,defaults.configuration,[""]), defaults.globparameters, "=", [" ", "	"], ",")
rec = parser.extractvaluebyparam(defaults.rcrec, pairs)

pairs = parser.getparametersandvals(parser.getvalfromconfigbykeyword(defaults.oglobal,defaults.keywords,defaults.configuration,[""]), defaults.globparameters, "=", [" ", "	"], ",")
_dc = parser.extractvaluebyparam(defaults.double_calibration, pairs)

irtorec = rec[0]
dc = _dc[0]


if dc == defaults.on:
	amendment = dcalibration(p_calib)
	print("Amendmebt parameter = ", amendment)


_buttonfile = getrcsubparam(defaults.configuration, irtorec, defaults.button)
_codesfile = getrcsubparam(defaults.configuration, irtorec, defaults.codes)
_folder = getrcsubparam(defaults.configuration, irtorec, defaults.folder)

buttonfile = _folder[0] + "/" + _buttonfile[0]
codesfile = _folder[0] + "/" + _codesfile[0]

buttons = parser.getvalfromconfigbykeyword(defaults.bu, defaults.subkeywords, buttonfile, [""])


if dc == defaults.on:
	dict = savebutton(p_calib, buttons, amendment)
else:
	dict = savebutton(p_calib, buttons)


makecodespyfile(codesfile, dict, p_calib, buttons)