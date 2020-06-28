def pair():
	return 'USDGBP'

def spnm(pair):
	if(pair == 'USDGBP'):
		return 10000.0, 1.0
	elif(pair == 'USDJPY'):
		return 100.0, 0.5
	else:
		return 100.0, 0.5
