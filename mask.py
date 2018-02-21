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

	newVal = []
	bnum = bin(val)
	#print bnum ,
	for i in range(bnum.find('b') + 1,len(bnum)):
		if i%2 == 0:
			newVal.append(bnum[i])
			continue

		if bnum[i] == '1':
			newVal.append('0')
		else:
			newVal.append('1')

	flipped = bnum[0:bnum.find('b') + 1] + ''.join(newVal)
	#print flipped
	return int(flipped, 2)



def bindigits(n, bits):
	#s = bin(n & int("1"*bits, 2))[2:]
    s = bin(n & int('0b' + '1' * 16, 2))
    #return ("{0:0>%s}" % (bits)).format(s)
    return s
