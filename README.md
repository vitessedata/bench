Introduction
============

These scripts create and run a TPCH benchmark and compare the results
between Deepgreen DB and Greenplum DB.

Step 1
------

Make sure your database is running. For postgres, you should run the 
next steps on the database machine. For Deepgreen DB or Greenplum DB,
run the next steps on the master machine.

Step 2
------

Clone this repo like this:
```
git clone git@github.com:cktan/bench.git
```

Step 3
------

Initialize the submodule like this:
```
(cd bench; git submodule init; git submodule update)
```

Step 4
------

Create the dbgen command:
```
(cd bench/tpch-dbgen; make clean; rm *.tbl; make)
```

Step 5
------
Optionally, set the necessary env vars so psql can connect
to the DB. The pertinent env vars are: ```PGUSER, PGHOST, PGPORT, 
and PGPASSWORD```.

Step 6
------
Create and load the tpch database by invoking the create.py script. 
The create.py script takes one parameter that could be one of 
the followings:

- 1f: scale 1 with float8 type
- 1n: scale 1 with numeric type
- 1m: scale 1 with money type
- 10f: scale 10 with float8 type
- 10n: scale 10 with numeric type
- 10m: scale 10 with money type

For example:
```
(cd bench; python create.py 1f)
```

Step 7
------
Run the benchmark:
```
(cd bench; python run.py)
```

A successful run will print out a tabulated result of 4 columns: 
1. Query#
2. Greenplum DB elapsed time
3. Deepgreen DB elapsed time
4. Speedup factor, i.e. how many times faster.



