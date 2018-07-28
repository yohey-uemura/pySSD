filepath='/Users/uemura/XAFS_DATA/UU/26_01_1149_Ghiasi/ascii'
filename='57228_Co_exafs_1.dat'

f = open(filepath+'/'+filename)
line = f.readline()
print line
i = 0
print "######After readline######"
for term in f:
    print term
    i+=1
    if i < 5:
        pass
    else:
        break
