import sys 


'''
Recieves integer value of a register
The values are changed by the algorithm in the mask function 
and returned to the backend.py to set new register value

'''
def mask(registerValue):

	val = None
	if registerValue[0:2] == "0x":
		val = int(registerValue,16)
	else:
		val = int(registerValue)

	bValue = val << 1
	return bValue



def bindigits(n, bits):
	#s = bin(n & int("1"*bits, 2))[2:]
    s = bin(n & int('0b' + '1' * 16, 2))
    #return ("{0:0>%s}" % (bits)).format(s)
    return s

