import sys, os, re, subprocess, os.path

VERBOSE=0
TABLE = 'customer lineitem nation orders part partsupp region supplier'.split()

def run(cmd):
    if VERBOSE:
        print cmd
    rc = os.system(cmd)
    if rc:
        sys.exit("ERROR: %s" % cmd)

if 1:
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('-v', '--verbose', help="turn on verbose mode", action="store_true")
    parser.add_argument('DB', help='{1,10,100}[mnf]')
    args = parser.parse_args()

    VERBOSE = args.verbose
    DB = 'tpch'+args.DB
    DBGENPATH = 'tpch-dbgen'

    match = re.match(r"([0-9]+)([mnf])", args.DB, re.I)
    if not match:
        parser.print_help()
        sys.exit(1)

    SCALE,TYP = match.groups()
    SCALE = int(SCALE)
    if SCALE not in [1,10,100]:
        parser.print_help()
        sys.exit(1)

    if not os.access(os.path.join(DBGENPATH, 'dbgen'), os.X_OK):
	sys.exit('Cannot run dbgen at %s' % os.path.join(DBGENPATH, 'dbgen'))


def load(db, scale, tab):
    print '   ',tab
    cmd = ['cat %s.tbl' % os.path.join(DBGENPATH, tab), 
           '''psql %s -c "COPY %s from stdin with csv delimiter '|'" ''' % (db, tab)]

    cmd = ' | '.join(cmd)
    run(cmd)


MKTAB = "mktab-%s.sql" % TYP
MKVIEW = "mkview-%s.sql" % (TYP in "nf" and 'n' or 'm')

if 1:  # dbgen
    print "1. dbgen %s" % SCALE
    run("cd %s && rm -f *.tbl" % DBGENPATH)
    proc = []
    for opt in 'cLnOPSrs':
        p = subprocess.Popen(['./dbgen', '-f', '-s', str(SCALE)], cwd=DBGENPATH)
	proc += [p]
    for p in proc:
        rc = p.wait()
        if rc:
            sys.exit('Cannot run dbgen -s %s in dir %s' % (SCALE, DBGENPATH))

    proc = []
    for t in TABLE:
        proc += [(t, subprocess.Popen(['perl', '-pi', '-e', 's/\|$//', '%s.tbl' % t], cwd=DBGENPATH))]
    for (t, p) in proc:
        rc = p.wait()
        if rc: 
	    sys.exit('Cannot process %s', t)
    
print "2. createdb %s" % DB
run("dropdb %s 2>/dev/null || true" % DB)
run("createdb %s" % DB)

print "3. mktab"
run("psql -q %s -f %s" % (DB, MKTAB))

print "4. mkview"
run("psql -q %s -f %s" % (DB, MKVIEW))

print "5. load"
for tab in TABLE:
    load(DB, SCALE, tab)

print "6. analyze"
run("psql -q %s -c 'vacuum analyze'" % DB)

if 0:
    print "7. cleanup"
    run("cd %s && rm -f *.tbl" % DBGENPATH)
