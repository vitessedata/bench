import sys,os

if len(sys.argv) != 3:
    sys.exit('Usage: %s file1 file2' % sys.argv[0])

afile = open(sys.argv[1]).readlines()
bfile = open(sys.argv[2]).readlines()

max = 0
atab = {}
for line in afile: 
    x = line.strip().split()
    if len(x) == 2:
	q = int(x[0])
	n = int(float(x[1]))
	if max < q: max = q
	atab[q] = n

btab = {}
for line in bfile:
    x = line.strip().split()
    if len(x) == 2:
	q = int(x[0])
	n = int(float(x[1]))
	if max < q: max = q
	btab[q] = n

atot = 0
btot = 0
for i in xrange(max):
    q = i+1
    a = atab.get(q, -1)
    b = btab.get(q, -1)
    if a < 0 or b < 0:
	r = -1.0
    else:
	atot += a
	btot += b
        if b == 0:
            r = 0.0
        else:
	    r = a / float(b)

    print '%d %d %d %.02f' % (q, a, b, r)

if btot == 0:
    r = 0.0
else:
    r = atot / float(btot)
print
print 'tot: %d %d %0.2f' % (atot, btot, r)
