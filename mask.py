import sys 


'''
Recieves integer value of a register
The values are changed by the algorithm in the mask function 
and returned to the backend.py to set new register value

'''
def mask(operation, registerValue, opValue = None):

	flag = False
	val = None
	if registerValue[0:2] == "0x":
		val = int(registerValue,16)
		flag = True
	else:
		val = int(registerValue)




	if operation == "flipAlt": 
		newVal = flipAlternateBit(registerValue)
	elif operation == "add": 
		newVal = addVal(registerValue,opValue)
	elif operation == "sub": 
		newVal = subVal(registerValue,opValue)


	if flag:
		return hex(newVal)

	return newVal





def addVal(registerValue, opValue):
	return registerValue + opValue


def subVal(registerValue, opValue):
	return registerValue - opValue



def flipAlternateBit(registerValue):

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