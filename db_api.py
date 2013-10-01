import sqlite3 as sql

CONN=None

def init_db(db_name='congressional_rollcalls.db'):
    global CONN
    CONN = sql.connect(db_name)
    c=CONN.cursor()
    try:
        c.execute('SELECT 1 FROM rollcalls')
    except:
        #'sqlite3 {db} {script}'.format(db=db_name, script='simple_db.sql') ## execute me!
        with open('simple_db.sql') as f:
            c.executescript(f.read())
    c.close()
          
def flush_rollcall(record, rc, year):
    print year, rc
    c = CONN.cursor()
    try:
        date = record['date'][0]
    except:
        date=''
    
    rc_record = (rc, year, record['description'], record['issue'], record['question'], date) # why is date in its own list?
    c.execute('INSERT INTO rollcalls VALUES (?,?,?,?,?,?)', rc_record)
    
    # votes. There's probably a more elegant way to do this with executemany()
    for vote in record['votes']:
        ins_rec = [rc, year]
        ins_rec.extend(vote)
        c.execute('INSERT INTO rollcall_votes VALUES (?,?,?,?,?,?,?)',  ins_rec)
    
    if record.has_key('descr'):
        try:
            descr = record['descr'][0]
        except:
            descr=''
        try:
            sponsor = record['sponsor'][0]
        except:
            sponsor=''

        issue_record = (record['issue'], descr, sponsor)
        c.execute('INSERT INTO issues VALUES (?,?,?)', issue_record)
        
        for sub in record['subjects']:
            c.execute('INSERT INTO issue_subjects VALUES (?,?)', (record['issue'], sub))
    
    CONN.commit()

init_db()
    