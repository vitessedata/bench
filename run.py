from __future__ import print_function
import sys, os, subprocess, re

VERBOSE = 0
SINGLE = 0

if 1:
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('-v', '--verbose', help="turn on verbose mode", action="store_true")
    parser.add_argument('-s', '--single', help='single threaded', action='store_true')
    parser.add_argument('DB', help='{1,10,100}[mnf]')
    args = parser.parse_args()
    
    VERBOSE = args.verbose
    SINGLE = args.single
    DB = 'tpch'+args.DB

    match = re.match(r"([0-9]+)([mnf])", args.DB, re.I)
    if not match:
        parser.print_help()
        sys.exit(1)

    SCALE,TYP = match.groups()
    SCALE = int(SCALE)
    if SCALE not in [1, 10, 100]:
        parser.print_help()
        sys.exit(1)

DIR = './tpch_run'
os.system('mkdir -p ' + DIR)

SQL = '''
-- TPCH1 needs hashjoin only
SET client_min_messages TO WARNING;
set enable_mergejoin=0;
set enable_nestloop=0;
set work_mem='256MB';
set optimizer=0;
set vitesse.enable=%(vdb_jit)s;
set statement_timeout=%(statement_timeout)s;
set vitesse.thread=%(vdb_thread)s;

\\timing on
'''
for i in range(23):
    SQL += '''
\\echo q%d
\\o q%d_out
select * from q%d;
''' % (i,i,i)

VARS = {
    'vdb_thread': SINGLE and '1' or '0',
    'statement_timeout': '100000',
    'vdb_jit': '0',
    'DIR': DIR,
    'DB': DB
}

#
# FIRST RUN : NO JIT
#
VARS['vdb_jit'] = '0'
cmd = '''(mkdir -p %(DIR)s/nojit && cd %(DIR)s/nojit && psql %(DB)s -qAt -F ' ' | awk 'BEGIN { RS="q" } {print $1, $3}' | grep '^[1-9]') > %(DIR)s/result_nojit''' % VARS
p = subprocess.Popen(cmd, shell=True, stdin=subprocess.PIPE)
sql = SQL % (VARS)
p.stdin.write(sql)
p.stdin.close()
p.wait()


#
# SECOND RUN : WITH JIT
#
VARS['vdb_jit'] = '1'
cmd = '''(mkdir -p %(DIR)s/jit && cd %(DIR)s/jit && psql %(DB)s -qAt -F ' ' |  awk 'BEGIN { RS="q" } {print $1, $3}' | grep '^[1-9]') > %(DIR)s/result_jit''' % VARS
p = subprocess.Popen(cmd, shell=True, stdin=subprocess.PIPE)
sql = SQL % (VARS)
p.stdin.write(sql)
p.stdin.close()
p.wait()


#
# MATCH THE OUTPUT
#
diff = ['cd %s' % DIR]
for i in range(1, 23):
    x = 'sort jit/q%d_out > jit/q%d_sorted' % (i,i)
    y = 'sort nojit/q%d_out > nojit/q%d_sorted' % (i,i)
    z = 'diff jit/q%d_sorted nojit/q%d_sorted > /dev/null || echo q%d diff' % (i,i,i)
    diff += [x, y, z]

os.system('\n'.join(diff))


#
# PARSE AND PRINT SPEEDUP TABLE
#
os.system('python parse.py %(DIR)s/result_nojit %(DIR)s/result_jit' % VARS)
