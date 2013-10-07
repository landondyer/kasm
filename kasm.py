#
#   6502 assembler
#
import tok


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


def fn_org( tokens, tokenValue, tokenIndex ):
    pass

def fn_dc( tokens, tokenValue, tokenIndex ):
    pass

def fn_dw( tokens, tokenValue, tokenIndex ):
    pass

def fn_include( tokens, tokenValue, tokenIndex ):
    pass


gPsuedoOps = {
    'org':      fn_org,
    'db':       fn_dc,
    'dw':       fn_dw,
    'include':  fn_include
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


def isDefined( label ):
    global gSymbol, gScope

    if label.startswith( '.' ):
        return gScope and gScope in gSymbol and label in gSymbol[gScope]
    else:
        return label in gSymbol[label]


def get( label ):
    global gSymbol, gScope

    if label.startswith( '.' ):
        #xxx mark referenced
        return gSymbol[gScope][label]
    else:
        #xxx mark referenced
        return gSymbol[label][label]


#
#   eval ==> errorString, value, valueAttrs, tokenIndex
#
def eval( tokens, tokenValues, tokenIndex ):
    return None, tokenValues[tokenIndex], 0, tokenIndex + 1        #xxx
    pass


#
#   parseAddressingMode ==> errorString, addrMode, value, valueAttrs, tokenIndex
#

def parseAddressingMode( tokens, tokenValues, tokenIndex ):

    if tokenIndex >= len(tokens):
        return None, IMPLIED, None, tokenIndex

    if tokens[tokenIndex] == '#':
        errorString, value, valueAttrs, tokenIndex = eval( tokens, tokenValues, tokenIndex + 1 )
        return errorString, IMMED, value, valueAttrs, tokenIndex

    #
    #   (n)
    #   (nn)
    #   (n,x)
    #   (n),y
    #
    if tokens[tokenIndex] == '(':
        errorString, value, valueAttrs, tokenIndex = eval( tokens, tokenValues, tokenIndex + 1 )
        if errorString:
            return errorString, None, None, None, tokenIndex

        if tokenIndex >= len(tokens):
            return "bad addressing mode (no close-parenthesis)"

        #   (expr,x)
        if tokens[tokenIndex] == ',':
            if tokenIndex + 2 < len(tokens) and tokens[tokenIndex+1] == tok.SYMBOL and tokenValues[tokenIndex+1].lower() == 'x' and tokens[tokenIndex + 2] == ')':
                return None, INDX, value, valueAttrs, tokenIndex + 2
            else:
                return "bad addressing mode (started out looking like indirect-x)", None, None, None, tokenIndex

        elif tokens[tokenIndex] == ')':

            tokenIndex = tokenIndex + 1

            #
            #   (expr),y
            #   (expr)
            #
            if tokenIndex + 2 < len(tokens) and tokens[tokenIndex] == ',' and tokens[tokenIndex+1] == tok.SYMBOL and tokenValues[tokenIndex+1].lower() == 'y':
                return None, INDY, value, valueAttrs, tokenIndex + 2
            else:
                return None, IND, value, valueAttrs, tokenIndex

        else:
            return "bad addressing mode (started out looking indirect, but fizzled)", None, None, None, tokenIndex

    #
    #   nn
    #   n
    #   rel
    #
    #   n,x
    #   n,y
    #

    errorString, value, valueAttrs, tokenIndex = eval( tokens, tokenValues, tokenIndex )
    if errorString:
        return errorString, None, None, None, tokenIndex

    if tokenIndex < len(tokens) and tokens[tokenIndex] == ',':
        tokenIndex = tokenIndex + 1
        if tokens[tokenIndex] == tok.SYMBOL:
            if tokenValues[tokenIndex].lower() == 'x':
                return None, UNDECIDED_X, value, valueAttrs, tokenIndex + 1
            elif tokenValues[tokenIndex].lower() == 'y':
                return None, UNDECIDED_Y, value, valueAttrs, tokenIndex + 1
            else:
                return str.format( "Unxpected symbol {0} following expression", tokenValues[ tokenIndex] ), None, None, None, tokenIndex
        else:
            return "Unxpected gunk following expression", None, None, None, tokenIndex

    return None, UNDECIDED, value, valueAttrs, tokenIndex


def deposit


def depositOp( op, arg, argSize ):
    pass


def rememberOp( op, valueAttrs, size ):
    deposit( op )
    remember( valueAttrs, size )


def assembleInstruction( op, tokens, tokenValues, tokenIndex ):
    errorString, addrMode, value, valueAttrs, tokenIndex = parseAddressingMode( tokens, tokenvalues, tokenIndex )
    if errorString:
        return errorString

    #xxx if value defined, do addr mode conversions for op
    #xxx otherwise do worst case, remember fixup


def assembleLine( line ):
    errorString, leadingWhitespace, tokens, tokenValues = tok.tokenize( line )

    if errorString:
        return errorString

    #
    #   SYMBOL = VALUE
    #
    if len(tokens) >= 3 and tokens[0] == tok.SYMBOL and tokens[1] == '=':
        errorString, value, valueAttrs, tokenIndex = eval( tokens, tokenValues, 2 )
        if errorString:
            return errorString
        if tokenIndex < len(tokens):
            return "Bad expression (extra gunk)"
        set( tokenValues[0], value )
        return
        
    #
    #   handle SYMBOL: at start of line
    #   NOTE: could enforce leadingWhitespace, but we have a ':'
    #   instead of that.
    #
    tokenIndex = 0
    if len(tokens) >= 2 and tokens[0] == tok.SYMBOL and tokens[1] == ':':
        set( tokenValues[tokenIndex], gLoc )
        tokenIndex = tokenIndex + 2

    #
    #   handle ops
    #
    if tokenIndex < len(tokens) and tokens[tokenIndex] == tok.SYMBOL:

        op = tokens[tokenIndex]
        if op in gPsuedoOps:
            errorString = gPsuedoOps[op]( tokens, tokenValues, tokenIndex )
        elif op in gOps:
            assembleInstruction( op, tokens, tokenValues, tokenIndex + 1 )
        else:
            errorString = str.format( 'Unknown op: {0}', op )

    return errorString


def test():
    assert assembleLine( 'label:' ) == None
    assert assembleLine( '.label:' ) == None
    assert assembleLine( 'symbol = 42' ) == None

    # more...

if __name__ == '__main__':
    test()
