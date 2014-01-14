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

def show(collection):
    """ simply display list/strin and return choosed id. """
    if type(collection) in (dict, tuple, list) :
        print
        for i, each in enumerate(collection):
            print "%d: %s" % (i, each)
        try:
            return raw_input(" : ")
        except EOFError:
            print "script run as non interactive, quitting."
            exit(0)
        except Exception as _e:
            print "Huh, some other unhandled error", _e
    else:
        return raw_input(collection + ":")

def switch(opt, *fun_ptrs, **fun_args):
    """ Use by cli.switch( return val, args as ptrs to functions without() ) """
    try:
        args = fun_args.values()[0][0][int(opt)],
    except: 
        args = None,
    try:
        #print "opt:%s fun_ptrs:%s fun_args:%s" % (opt, fun_ptrs, fun_args)
        fun_ptrs[int(opt)](*args)
    except ValueError: #probably mistakenly pressed enter
        print "Wrong input (only digits are valid)" 
        return
    except Exception as _e:
        print "probably out of range:", opt, " in ", len(fun_ptrs), _e

def menu_factory(*args, **kwargs):
    """ 
    Creates cli menu, launches function from selection. Entry point of this mod.

    """

    ret = show(args[0])
    try:
        switch(ret, *args[1], params = kwargs.values())
    except Exception as e:
        print e
        return