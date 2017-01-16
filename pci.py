import sqlite3

sqlite_file = 'pcidss32.sqlite'    # name of the sqlite database file
#searchstring = 'password'

# Connecting to the database file
conn = sqlite3.connect(sqlite_file)
c = conn.cursor()

def lookup (searchstring):
    c.execute ('SELECT tblPCIDSS32.req_detail from tblPCIDSS32 WHERE tblPCIDSS32.req_detail LIKE \'%' + searchstring + '%\' ')
    results = c.fetchall()

    return results
    #return results