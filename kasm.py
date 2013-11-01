#
#   6502 assembler
#   Copyright 2013 Landon Dyer
#   BSD License
#

import tok
import eval
import fileinput
import sys


#
#   Opcodes and addressing modes
#
#       (empty)     impl
#       #n          immed
#       nn          abs
#       n           zp
#       nn,x        absx
#       nn,y        absy
#       a           implied
#       (nn)        ind
#       expr        rel
#       n,x         zpx
#       n,y         zpy
#       (n,x)       indx
#       (n),y       indy
#
#   optimize, whenever possible
#       ABS to ZP
#       ABSX to ZPX
#       ABSY to ZPY
#

IMPLIED = 0
IMMED = 1
ABS = 2
ZP = 3
ABSX = 4
ABSY = 5
IND = 6
REL = 7
ZPX = 8
ZPY = 9
INDX = 10
INDY = 11

#   without actual values, these are ambiguous
UNDECIDED_X = 12        # ABSX / ZPX
UNDECIDED_Y = 13        # ABSY / ZPY
UNDECIDED = 14          # ABS / ZP / REL

gAddrModeToByteCount = {
    IMPLIED: 0,
    IMMED: 1,
    ABS: 2,
    ZP: 1,
    ABSX: 2,
    ABSY: 2,
    IND: 2,
    REL: 1,
    ZPX: 1,
    ZPY: 1,
    INDX: 1,
    INDY: 1
    }

gOps = {
    'adc': {  IMMED: 0x69, ABS: 0x6d, ZP: 0x65, INDX: 0x61, INDY: 0x71, ZPX: 0x75, ABSX: 0x7d, ABSY: 0x79 },
    'and': {  IMMED: 0x29, ABS: 0x2d, ZP: 0x25, INDX: 0x21, INDY: 0x31, ZPX: 0x35, ABSX: 0x3d, ABSY: 0x39 },
    'asl': {  ABS: 0x0e, ZP: 0x06, IMPLIED: 0x0a, ZPX: 0x16, ABSX: 0x1e },
    'bcc': {  REL: 0x90 },
    'bcs': {  REL: 0xb0 },
    'beq': {  REL: 0xf0 },
    'bne': {  REL: 0xd0 },
    'bmi': {  REL: 0x30 },
    'bpl': {  REL: 0x10 },
    'bvc': {  REL: 0x50 },
    'bvs': {  REL: 0x70 },
    'bit': {  ABS: 0x2c, ZP: 0x24 },
    'brk': {  IMPLIED: 0x00 },
    'clc': {  IMPLIED: 0x18 },
    'cld': {  IMPLIED: 0xd8 },
    'cli': {  IMPLIED: 0x58 },
    'clv': {  IMPLIED: 0xb8 },
    'cmp': {  IMMED: 0xc9, ABS: 0xcd, ZP: 0xc5, INDX: 0xc1, INDY: 0xd1, ZPX: 0xd5, ABSX: 0xdd, ABSY: 0xd9 },
    'cpx': {  IMMED: 0xe0, ABS: 0xec, ZP: 0xe4 },
    'cpy': {  IMMED: 0xc0, ABS: 0xcc, ZP: 0xc4 },
    'dec': {  ABS: 0xce, ZP: 0xc6, ZPX: 0xd6, ABSX: 0xde },
    'dex': {  IMPLIED: 0xca },
    'dey': {  IMPLIED: 0x88 },
    'eor': {  IMMED: 0x49, ABS: 0x4d, ZP: 0x45, INDX: 0x41, INDY: 0x51, ZPX: 0x55, ABSX: 0x5d, ABSY: 0x59 },
    'inc': {  ABS: 0xee, ZP: 0xe6, ZPX: 0xf6, ABSX: 0xfe },
    'inx': {  IMPLIED: 0xe8 },
    'iny': {  IMPLIED: 0xc8 },
    'jmp': {  ABS: 0x4c, IND: 0x6c },
    'jsr': {  ABS: 0x20 },
    'lda': {  IMMED: 0xa9, ABS: 0xad, ZP: 0xa5, INDX: 0xa1, INDY: 0xb1, ZPX: 0xb5, ABSX: 0xbd, ABSY: 0xb9 },
    'ldx': {  IMMED: 0xa2, ABS: 0xae, ZP: 0xa6, ABSY: 0xbe, ZPY: 0xb6 },
    'ldy': {  IMMED: 0xa0, ABS: 0xac, ZP: 0xa4, ZPX: 0xb4, ABSX: 0xbc },
    'lsr': {  ABS: 0x4e, ZP: 0x46, IMPLIED: 0x4a, ZPX: 0x56, ABSX: 0x5e },
    'nop': {  IMPLIED: 0xea },
    'ora': {  IMMED: 0x09, ABS: 0x0d, ZP: 0x05, INDX: 0x01, INDY: 0x11, ZPX: 0x15, ABSX: 0x1d, ABSY: 0x19 },
    'pha': {  IMPLIED: 0x48 },
    'php': {  IMPLIED: 0x08 },
    'pla': {  IMPLIED: 0x68 },
    'plp': {  IMPLIED: 0x28 },
    'rol': {  ABS: 0x2e, ZP: 0x26, IMPLIED: 0x2a, ZPX: 0x36, ABSX: 0x3e },
    'ror': {  ABS: 0x6e, ZP: 0x66, IMPLIED: 0x6a, ZPX: 0x76, ABSX: 0x7e },
    'rti': {  IMPLIED: 0x40 },
    'rts': {  IMPLIED: 0x60 },
    'sbc': {  IMMED: 0xe9, ABS: 0xed, ZP: 0xe5, INDX: 0xe1, INDY: 0xf1, ZPX: 0xf5, ABSX: 0xfd, ABSY: 0xf9 },
    'sec': {  IMPLIED: 0x38 },
    'sed': {  IMPLIED: 0xf8 },
    'sei': {  IMPLIED: 0x78 },
    'sta': {  ABS: 0x8d, ZP: 0x85, INDX: 0x81, INDY: 0x91, ZPX: 0x95, ABSX: 0x9d, ABSY: 0x99 },
    'stx': {  ABS: 0x8e, ZP: 0x86, ZPY: 0x96 },
    'sty': {  ABS: 0x8c, ZP: 0x84, ZPX: 0x94 },
    'tax': {  IMPLIED: 0xaa },
    'tay': {  IMPLIED: 0xa8 },
    'tsx': {  IMPLIED: 0xba },
    'txa': {  IMPLIED: 0x8a },
    'txs': {  IMPLIED: 0x9a },
    'tya': {  IMPLIED: 0x98 }
}


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


def set( label, value ):
    global gSymbol, gScope
    scope = None

    print "set", label, value

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


#   ----------------------------------------------------------------
#   Pseudo ops
#   ----------------------------------------------------------------

def fn_org( tokenizer ):
    global gLoc
    org = eval.Expression( tokenizer ).eval()
    if org == None:
        raise Exception( "Undefined expression" )
    gLoc = org
    print "gLoc=", gLoc

def fn_dc( tokenizer ):
    pass


def fn_dw( tokenizer ):
    pass


def fn_include( tokenizer ):
    pass


gPsuedoOps = {
    'org':      fn_org,
    'db':       fn_dc,
    'dw':       fn_dw,
    'include':  fn_include
}



#
#   parseAddressingMode ==> addrMode, expressionObject
#

def parseAddressingMode( tokenizer ):

    if tokenizer.atEnd():
        return IMPLIED, None

    if tokenizer.curTok() == '#':
        tokenizer.advance()
        expr = eval.Expression( tokenizer )
        return IMMED, expr

    #
    #   (n)
    #   (nn)
    #   (n,x)
    #   (n),y
    #
    if tokenizer.curTok() == '(':
        tokenizer.advance()
        expr = eval.Expression( tokenizer )

        #   (expr,x)
        if tokenizer.curTok() == ',':
            if  tokenizer.peek( 1 ) == tok.SYMBOL and tokenizer.peekValue(1).lower() == 'x' and tokenizer.peek( 2 ) == ')':
                tokenizer.advance( 3 )
                return INDX, expr
            else:
                raise Exception( "bad addressing mode (started out looking like indirect-x)" )

        elif tokenizer.curTok() == ')':

            tokenizer.advance()

            #
            #   (expr),y
            #   (expr)
            #
            if tokenizer.curTok() == ',' and tokenizer.peek( 1 ) == tok.SYMBOL and tokenizer.peekValue( 1 ).lower() == 'y':
                tokenizer.advance( 2 )
                return INDY, expr
            else:
                return IND, expr

        else:
            raise Exception( "bad addressing mode (started out looking indirect, but fizzled)" )

    #
    #   nn
    #   n
    #   rel
    #
    #   n,x
    #   n,y
    #

    expr = eval.Expression( tokenizer )

    if tokenizer.curTok() == ',':
        tokenizer.advance()

        if tokenizer.curTok() == tok.SYMBOL:
            if tokenizer.curValue().lower() == 'x':
                return UNDECIDED_X, expr
            elif tokenValues.curValue().lower() == 'y':
                return UNDECIDED_Y, expr
            else:
                raise Exception( str.format( "Unxpected symbol {0} following expression", tokenValues[ tokenIndex] ) )
        else:
            raise Exception( "Unxpected gunk following expression" )

    return UNDECIDED, expr


#   ----------------------------------------------------------------
#   Image construction
#   ----------------------------------------------------------------


gMemory = [None] * 65536


def depositByte( byte ):
    global gLoc
    print "DEP ", gLoc, byte
    gMemory[gLoc] = byte & 0xff
    gLoc += 1
    if gLoc >= 0x10000:
        gLoc = 0

def depositWord( word ):
    depositByte( word )
    depositByte( word >> 8 )
    

#   ----------------------------------------------------------------
#   Assembly
#   ----------------------------------------------------------------

def depositImpliedArg( expr, value ):
    pass

def depositByteArg( expr, value ):
    pass

def depositAbsArg( expr, value ):
    pass

def depositRelArg( expr, value ):
    pass

gDepositDispatch = {
    IMPLIED: depositImpliedArg,
    IMMED: depositByteArg,
    ABS: depositAbsArg,
    ZP: depositByteArg,
    ABSX: depositAbsArg,
    ABSY: depositAbsArg,
    IND: depositAbsArg,
    REL: depositRelArg,
    ZPX: depositByteArg,
    ZPY: depositByteArg,
    INDX: depositByteArg,
    INDY: depositByteArg
    }


def assembleInstruction( op, tokenizer, phaseNumber ):
    addrMode, expr = parseAddressingMode( tokenizer )

    value = None
    if expr != None:
        value = expr.eval()
        
    print op, phaseNumber, value
    if expr:
        print expr.m_postfix
    dumpSymbols()
    if phaseNumber > 0 and value == None:
        raise Exception( "Undefined expression" )
    
    #   if there's an exact match for (op, addrMode) then assemble it

    if addrMode in gOps[op]:
        depositByte( gOps[op][addrMode] )
        gDepositDispatch[addrMode]( expr, value )

    else:
        pass

        # various cases of UNDECIDED stuff
        # remember which are which, by address?


#
#   Handle a line of assembly input
#
#   Phase 0:    just intern stuff
#   Phase 1:    emit stuff (expressions required to be defined)
#
def assembleLine( line, phaseNumber=0 ):
    global gLoc
    
    tokenizer = tok.Tokenizer( line )

    #
    #   SYMBOL = VALUE
    #
    if tokenizer.curTok() == tok.SYMBOL and tokenizer.peek(1) == '=':
        sym = tokenizer.curValue()
        tokenizer.advance( 2 )
        expr = eval.Expression( tokenizer )
        if not tokenizer.atEnd():
            raise Exception( "Bad expression (extra gunk)" )

        value = expr.eval()

        if phaseNumber > 0 and value == None:
            raise Exception( str.format( "Undefined expression" ) )
        
        set( sym, expr.eval() )
        return
        
    #
    #   handle SYMBOL: at start of line
    #   NOTE: could enforce leadingWhitespace, but we have a ':'
    #   instead of that.
    #
    if tokenizer.curTok() == tok.SYMBOL and tokenizer.peek(1) == ':':
        sym = tokenizer.curValue()
        tokenizer.advance( 2 )

        if phaseNumber == 0:
            set( sym, gLoc )
            
        else:
            #
            #   check that the symbol has the same value in
            #   subsequent phases
            #
            setScope( sym )
            if get( sym ) != gLoc:
                raise Exception( str.format( "Symbol phase error (expected {0}, have {1})", get(sym), gLoc ) )

    #
    #   handle ops
    #
    if tokenizer.curTok() == tok.SYMBOL:

        op = tokenizer.curValue()
        tokenizer.advance()
        
        if op in gPsuedoOps:
            gPsuedoOps[op]( tokenizer )
        elif op in gOps:
            assembleInstruction( op, tokenizer, phaseNumber )
        else:
            raise Exception( str.format( 'Unknown op: {0}', op ) )


def assembleFile( filename ):
    for phase in range(0,2):
        input = None

        try:
            input = fileinput.FileInput( filename )
        except:
            print "Error: {0}", sys.exc_value
            return

        try:
            while True:
                line = input.nextLine()
                if not line:
                    break
                assembleLine( line, phase )
        except:
            err = str.format("Error: {0}({1}): {2}",
                input.file(),
                input.line(),
                sys.exc_value )
            print err
            raise #xxx


def dumpSymbols():
    for scope in gSymbol:
        print str.format("{0:20} {1}", scope, gSymbol[scope][scope] )
        for localSymbol in gSymbol[scope]:
            if localSymbol != scope:
                print str.format("    {0:20} {1}", localSymbol, gSymbol[scope][localSymbol] )

def test():
    assembleLine( 'label:', 0 )
    assembleLine( 'label:', 1 )
    assembleLine( '.label:', 0)
    assembleLine( '.label:', 1)
    assembleLine( 'symbol = 42', 0 )

    assembleLine( ' org $1000', 0 )
    assembleLine( ' org $1000 + 100', 0 )

    assembleFile( 'test.asm' )
    
    print "----------------"
    print "Symbols:"
    dumpSymbols()

    # more...

if __name__ == '__main__':
    test()
