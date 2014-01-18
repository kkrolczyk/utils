#!/usr/bin/env python
"""
    utils.commandlinemenu
    ---------------------
    Used to generate commandline menu. Tested only in Linux.
    Usage:
        #  hdr = (t['some_menu_PL'], t["other menu_GB"], "a_string", exit)
        #  [thismodule].menu_factory( hdr, (ptrToFun1, fun2, _at_exit) )
        ####  or to pass also args to functions:
    >>> import commandlinemenu as cli
    >>> def funA(a):
    ...    print "funA:", a
    >>> funB = funC = funD = funA
    >>> menuheaders = (" A ", " B ", " C ", " D ")
    >>> functions = (funA, funB, funC, funD)
    >>> par = (2, ["g",1], (3, {"dictH":1}))
    >>> cli.menu_factory(menuheaders, functions, params = par)
    0:  A 
    1:  B 
    2:  C 
    3:  D 
     : 2
    funA: (3, {'dictH': 1})

        #  every function gets ordinal parameters so be careful.
        #  This means, in above example 
        #  2 belongs to funA, ["g", 1] to f, tuple of 3 and dict to funC
        - undefined functions throws Exception.
        - wrong len() of parameters passed to function throws Exception.

    :copyright: Krzysztof Krolczyk 2013
    :licence:   MIT
"""

class MyExceptions(Exception):
    """ handles EOT, SIGINT """
    def __init__(self, arg):
        arg = type(arg)
        if arg == EOFError:
            print " > Got EOF signal, quitting..."
            exit(0)
        elif arg == KeyboardInterrupt:
            print " > Got sigint signal, quitting..."
            exit(0)
        else:
            print "Huh, some other unhandled error", arg
            print "will try to continue, but caveat lector, might fail anywhere"

def multiline():
    """ multiline asssumes that none wil just input plain empty space 
        or rather no input followed by enter. Previously I assumed
        it should be handled as an error but now i think I could actually
        use that to indicate that user wants to have multiline input. 
        It shall end when signal is recieved, EOF or interrupt. 
        This should be able to handle copy pasted data as well. """

    buf = []
    try:
        while True:
            buf += raw_input(" : (ctrl-c = END):") + "\n"
    except (EOFError, KeyboardInterrupt):
        return "".join(buf)
    except Exception as _e:
        print "a bug! ", _e

def show(collection, allow_multilines = True):
    """ simply display list/string and return choosed id. """
    if type(collection) in (dict, tuple, list) :
        print
        for i, each in enumerate(collection):
            print "%d: %s" % (i, each)
        try:
            ret = raw_input(" : ")
            if allow_multilines and ret == "":
                print "entering multiline mode..."
                return multiline()
            else:
                return ret
        # this way we dont need to import sys
        except (EOFError, KeyboardInterrupt, Exception) as _e:
            MyExceptions(_e)
    else:
        try:
            ret = raw_input(collection + " : ")
            if allow_multilines and ret == "":
                print "entering multiline mode..."
                return multiline()
            else:
                return ret
        except (EOFError, KeyboardInterrupt, Exception) as _e:
            MyExceptions(_e)


def switch(opt, *fun_ptrs, **fun_args):
    """ Use this function by issuing ie. 
        cli.switch( choosed_ptr, args_as_ptrs to functions, **optional ) """
    try:
        args = fun_args.values()[0][0][int(opt)]
    except: 
        args = None
    try:
        #print "opt:%s fun_ptrs:%s fun_args:%s" % (opt, fun_ptrs, fun_args)
        fun_ptrs[int(opt)](args) if args else fun_ptrs[int(opt)]() 
    except ValueError: #probably mistakenly pressed enter
        print "Wrong input (only digits are valid)" 
        return
    except Exception as _e:
        print " Error occured : ", opt, " in ", len(fun_ptrs), _e, type(_e)

def menu_factory(*args, **kwargs):
    """ Creates cli menu, launches function from selection. 
        Entry point of this module. """

    ret = show(args[0])
    try:
        switch(ret, *args[1], params = kwargs.values())
    except Exception as e:
        print e
        return