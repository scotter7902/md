import os

# check is created data folder in the current path yet
datafol = 'data'
legifol = '/'.join([datafol, 'legi'])
malifol = '/'.join([datafol, 'mali'])
fols = [datafol, legifol, malifol]
def fols_():
	global fols
	for fol in fols:
		if not os.path.isdir(fol):
			print('create folder: '+fol, end=' ')
			try:
				os.mkdir(fol)
				print('[done]')
			except:
				print('[error]')
	print('- done')

# counting files in folder tree
def len_(dir):
	count = 0
	temp = os.listdir(dir)
	for file in temp:
		filepath = os.path.join(dir, file)
		if os.path.isdir(filepath):
			count = count+len_(filepath)-1
	return count+len(temp)