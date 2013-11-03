#   ----------------------------------------------------------------
#   Symbol management
#   ----------------------------------------------------------------

#
#   { '<name>':   { '<name>': value, '.subname': value ... } ... }
#
gSymbol = {}
gSymbolState = {}
gScope = None

gLoc = 0


def clear():
    global gSymbol, gScope
    gSymbol = {}
    gSymbolState = {}
    gScope = None
    gLoc = 0


def set( label, value ):
    global gSymbol, gScope
    scope = None

    if label.startswith( '.' ):
        scope = gScope
    else:
        gScope = label
        scope = label

    if not scope in gSymbol:
        gSymbol[scope] = {}
        gSymbolState[scope] = {}

    gSymbol[scope][label] = value
    gSymbolState[scope][label] = True


def setScope( label ):
    global gScope
    if not label.startswith( '.' ):
        gScope = label


def isDefined( label ):
    global gSymbol, gScope

    if label.startswith( '.' ):
        return gScope and gScope in gSymbol and label in gSymbol[gScope]
    else:
        return label in gSymbol and label in gSymbol[label]


def get( label ):
    global gSymbol, gScope

    if label.startswith( '.' ):
        #xxx mark referenced
        return gSymbol[gScope][label]
    else:
        #xxx mark referenced
        return gSymbol[label][label]


def dumpSymbols():
    for scope in gSymbol:
        print str.format("{0:20} {1}", scope, gSymbol[scope][scope] )
        for localSymbol in gSymbol[scope]:
            if localSymbol != scope:
                print str.format("    {0:20} {1}", localSymbol, gSymbol[scope][localSymbol] )

