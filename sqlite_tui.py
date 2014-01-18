#!/usr/bin/python
"""
    utils.sqlite_tui
    ---------------------
    Used to give user wery basic interface to sqlite db. Tested only in Linux.
    Utilizes commandlinemenu from same package, in future maybe i'll make gui.
    Usage:
        Just run python this_module (ie python sqlite_tui).
        Rest should be pretty well described, tell me so, if isn't :)
    Well, it is poorly written, i must admit, but it done its job many times :)

    :copyright: Krzysztof Krolczyk 2013
    :licence:   MIT
"""

import sqlite3
import commandlinemenu as cli
import os
from translation_sqlite_tui import t


def sep(*a):
    """ adds space between things """
    return "".join([a[x] + " " for x in xrange(0, len(a)) ])[:-1]

def tablegenrator(tablename = None, fields = None, \
                  fieldstypes = None, options = None):
    """ creates sql to create table, or if table exists, read its variables """

    if tablename:
        tab['tbname'] = tablename
    else:    
        tab['tbname'] = cli.show(sep(t['provide'], t["tbname"]))

    do_create = True
    #if table exists just read its data, inform user and return
    try:
        x = tab["cur"].execute("SELECT * FROM sqlite_master \
                                WHERE name='%s'" %tab['tbname'])
        data = [r for r in x]
        if data:
            do_create = False
        #for r in data: print "tb items", r
            # since string is "create table = 14 + tablename + id autoinc = 47"
            scheme = data[0][4][14 + len(tab['tbname']) + 47:-1] 
            tab['tbheaders'] = ",".join( [ x[0:x.index(" ")] \
                               for x in scheme.split(",") ] )
            tab['tbheaders'] = "(" + tab['tbheaders'] + ")"

    except Exception as e: # should raise?
        print e   # Exception might mean that incorrectly parse table

    if do_create:
        # cant actually assume that if tbheaders are set, we wont 
        # want to reset them...unless they'd be passed as fields, hmm 
        if fields:
            tab['tbheaders'] = fields
            fields = tab['tbheaders'].split(";")
        else:
            tab['tbheaders'] = cli.show(sep(t['provide'], 
                                            t["fields"], 
                                            t['separated_by']))
            fields = tab['tbheaders'].split(";")
            try:
                tab['tbheaders'] = ",".join(tab['tbheaders'].split(";"))               
                tab['tbheaders'] = "(" + tab['tbheaders'] + ")"
            except Exception as e:
                print t['notallowed']
                return
        variable = []
        for f in fields:
            variable.append((f, cli.show(sep(t['provide'], "sql typ dla", f, \
               "\nDATATIME, TEXT, INT, INTEGER, CHAR(39), VAR(3), REAL etc"))))
            #  TODO : +options if any
        
        sql =  "CREATE TABLE" + " " + tab['tbname'] + " "
        sql += "(ID INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,"   
        for v in variable:
            sql += sep(v[0], v[1]) + ","
        sql = sql[:-1] #strip last ","
        sql += ");"
        return sql


def select():
    """ user selects db and table. Perhaps should split those two """
    print t['sel_db'] 
    _dbs = [ x for x in os.listdir(".") if x.endswith(".db") ]
    if _dbs:
        print t["select_file_or_input"]
    ret = cli.show(_dbs)
    # :/ not proud. Since using cli with digits to control flow,"\0" is needed
    skipthis = False
    if ret[0] == "/":
        skipthis = True
        ret = ret[1:]
    if ret.isdigit() and not skipthis:
        try:
            ret = _dbs[int(ret)]
        except IndexError:
            print sep(t['failed'], t['will_try_fix'])
            ret = "tmp" + ".db"
    elif len(ret) < 3:
        ret += ".db"
    elif len(ret) >= 3 and ret[-3:0] != ".db":
        ret += ".db"
    else:
        print t['sel_no'] % ret
        ret = "_" + ret + ".db"
    tab["dbname"] = ret
    createdb()
    tabs = tab["cur"].execute("SELECT * FROM sqlite_master WHERE type='table'")
    _tbs = [ x[2] for x in tabs ]
    print t["sel_tb"]
    if _tbs:
        print t["select_file_or_input"]
    ret = cli.show(_tbs)
    skipthis = False
    if ret[0] == "/":
        skipthis = True
        ret = ret[1:]    
    if ret.isdigit() and not skipthis:
        try:
            ret = _tbs[int(ret)]
        except IndexError:
            print sep(t['failed'], t['will_try_fix'])
            ret = "tmp"
    tab["tbname"] = ret
    createtab()
    return 0

def createdb(db = None):
    """ wowzers, executes create db if checks are positive """
    if db:
        tab["dbname"] = db
    if not tab["dbname"] or ((tab["conn"] or tab["cur"]) and db):
        print t['db_empty']
    elif (tab["conn"] or tab["cur"]) and db:
        print t['db_was_set']
        return createdb(db)
    else:
        try:
            tab["conn"] = sqlite3.connect(tab['dbname'])
            tab["cur"] = tab["conn"].cursor()
            print t['success']
        except sqlite3.ProgrammingError:
            print t['notallowed']
    return 0

def createtab(tb = None):
    """ generates table for db """
    if tb:
        tab["dbname"] = tb
    elif not tab["dbname"]:
        print t['db_empty']
        return 0
    generated = tablegenrator(tab["tbname"])
    if generated:
        try:
            tab["conn"].execute(generated)
        except sqlite3.ProgrammingError:
            print t['notallowed']
            return 0
    print t['success']            
    return 0

def insert():    
    """handles inserts in funny way, generating placeholder from tableheader"""
    try:
        if tab["tbheaders"] == None:
            raise Exception("tbheaders not set")
    except Exception:
        print t['sel_st']
        return
                # TODO, optimize for many inserts
                # rows = [ ('itm', itm, 'itm'),
                #          ('itm', itm, 'itm'),
                #          ('itm', itm, 'itm') ]
                #   c.executemany('insert into table values (?,?,?,?,?)', rows )
                #   connection.commit()

    # ouch the pain. Why did i do that like that.
    ret = [ tuple( cli.show(sep(    t['provide'], 
                                    "format: (X; Y; 3; Z),", 
                                    tab["tbheaders"])).split(";") 
                                ) 
            ]
    prep = lambda: "".join( [ "?," for x in tab["tbheaders"].split(",") ] )[:-1]
    for item in ret:
        sql = "INSERT INTO %s %s VALUES(%s)" \
               % ( tab["tbname"], tab['tbheaders'], prep() )
        try:
            tab["cur"].execute(sql, item)
            tab["conn"].commit()
        except sqlite3.ProgrammingError:
            print t['notallowed']

def delete():
    """ deletes rows in a loop """
    while 1:
        ret = cli.show(t['del_extended'])
        if ret == "0":
            pokaz()
            continue
        elif ret == "*":
            tab["cur"].execute("DELETE FROM %s" % (tab["tbname"]) )
        elif ret == "-" or ret[0] == "-":
            return
        elif len(ret) > 2:
            # hah, this should totally fail 
            try:
                r1 = ",".join([ x for x in ret.split(",") if not "-" in x  ])
                # this particulary should explode...but hey it was fun
                # this - was even funnier,but would not handle multi digits like 34-55. 
                # r1 += ",".join( ("".join(str(range(int(x[0]),int(x[2:])+1)))) for x in ret.split(",") if "-" in x )
                # But hey, this beauty below? Can do multidigits. Although range "eats", last one like 1-3 = 1,2...sadface. 
                r1 += ",".join( (",".join(map(str, range(*map(int, x.split("-"))))) for x in ret.split(",") if "-" in x ))
                ret = r1
                print ret, " ok ? "
            except Exception:
                print t['failed']
        else:
            tab["cur"].execute("DELETE FROM %s WHERE ID = %s" 
                                % (tab["tbname"], ret) )
        break
    tab["conn"].commit()

def pokaz():
    """ show all data """
    # todo, filter, where ID = xxx, like etc
    try:
        x = tab["cur"].execute("SELECT * FROM %s" %tab["tbname"])
    except sqlite3.ProgrammingError:
        print t['sel_st']
        return 0
    data = [r for r in x]
    if not data:
        print t['has_no_data']
    for r in data:
        print r

def rawsql(sql = None):
    """ just dont play around and execute raw sql on this db """
    if not sql:
        sql = cli.show(t['provide'])
    try:
        tab["cur"].execute(sql)
    except:
        try:
            tab["cur"].execute(sql)
        except sqlite3.ProgrammingError as _e:
            print "prawdopodobnie niepoprawny sql / probably malformed sql"
            raise _e

if __name__ == "__main__":

    tab = { "tbname" : None, "dbname" : None, "conn" : None, "cur" : None, "tbheaders":None }
    functions = (select, createdb, createtab, 
                 insert, delete, pokaz, rawsql, 
                 exit)
    while 1:
        cli.menu_factory(t['mainmenu'], functions)
        # functions = (  lambda x:print(x) for x in range(0,3)  )

    tab['conn'].close()


# funny Python's gotha's
# >>> str(range(1,5))
# '[1, 2, 3, 4]'
# >>> str(xrange(1,5))
# 'xrange(1, 5)'
# >>> str(list({"Yees, strange":"isn't it?"}))
# "['Yees, strange']"
# 'str(list(xrange(1, 5)))'
# '[1, 2, 3, 4]'