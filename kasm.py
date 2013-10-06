import tok

#
#   6502 assembler
#

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

gOps = {
    'adc': {  'immed': 0x69, 'abs': 0x6d, 'zp': 0x65, 'indx': 0x61, 'indy': 0x71, 'zpx': 0x75, 'absx': 0x7d, 'absy': 0x79 },
    'and': {  'immed': 0x29, 'abs': 0x2d, 'zp': 0x25, 'indx': 0x21, 'indy': 0x31, 'zpx': 0x35, 'absx': 0x3d, 'absy': 0x39 },
    'asl': {  'abs': 0x0e, 'zp': 0x06, 'impl': 0x0a, 'zpx': 0x16, 'absx': 0x1e },
    'bcc': {  'rel': 0x90 },
    'bcs': {  'rel': 0xb0 },
    'beq': {  'rel': 0xf0 },
    'bne': {  'rel': 0xd0 },
    'bmi': {  'rel': 0x30 },
    'bpl': {  'rel': 0x10 },
    'bvc': {  'rel': 0x50 },
    'bvs': {  'rel': 0x70 },
    'bit': {  'abs': 0x2c, 'zp': 0x24 },
    'brk': {  'impl': 0x00 },
    'clc': {  'impl': 0x18 },
    'cld': {  'impl': 0xd8 },
    'cli': {  'impl': 0x58 },
    'clv': {  'impl': 0xb8 },
    'cmp': {  'immed': 0xc9, 'abs': 0xcd, 'zp': 0xc5, 'indx': 0xc1, 'indy': 0xd1, 'zpx': 0xd5, 'absx': 0xdd, 'absy': 0xd9 },
    'cpx': {  'immed': 0xe0, 'abs': 0xec, 'zp': 0xe4 },
    'cpy': {  'immed': 0xc0, 'abs': 0xcc, 'zp': 0xc4 },
    'dec': {  'abs': 0xce, 'zp': 0xc6, 'zpx': 0xd6, 'absx': 0xde },
    'dex': {  'impl': 0xca },
    'dey': {  'impl': 0x88 },
    'eor': {  'immed': 0x49, 'abs': 0x4d, 'zp': 0x45, 'indx': 0x41, 'indy': 0x51, 'zpx': 0x55, 'absx': 0x5d, 'absy': 0x59 },
    'inc': {  'abs': 0xee, 'zp': 0xe6, 'zpx': 0xf6, 'absx': 0xfe },
    'inx': {  'impl': 0xe8 },
    'iny': {  'impl': 0xc8 },
    'jmp': {  'abs': 0x4c, 'ind': 0x6c },
    'jsr': {  'abs': 0x20 },
    'lda': {  'immed': 0xa9, 'abs': 0xad, 'zp': 0xa5, 'indx': 0xa1, 'indy': 0xb1, 'zpx': 0xb5, 'absx': 0xbd, 'absy': 0xb9 },
    'ldx': {  'immed': 0xa2, 'abs': 0xae, 'zp': 0xa6, 'absy': 0xbe, 'zpy': 0xb6 },
    'ldy': {  'immed': 0xa0, 'abs': 0xac, 'zp': 0xa4, 'zpx': 0xb4, 'absx': 0xbc },
    'lsr': {  'abs': 0x4e, 'zp': 0x46, 'impl': 0x4a, 'zpx': 0x56, 'absx': 0x5e },
    'nop': {  'impl': 0xea },
    'ora': {  'immed': 0x09, 'abs': 0x0d, 'zp': 0x05, 'indx': 0x01, 'indy': 0x11, 'zpx': 0x15, 'absx': 0x1d, 'absy': 0x19 },
    'pha': {  'impl': 0x48 },
    'php': {  'impl': 0x08 },
    'pla': {  'impl': 0x68 },
    'plp': {  'impl': 0x28 },
    'rol': {  'abs': 0x2e, 'zp': 0x26, 'impl': 0x2a, 'zpx': 0x36, 'absx': 0x3e },
    'ror': {  'abs': 0x6e, 'zp': 0x66, 'impl': 0x6a, 'zpx': 0x76, 'absx': 0x7e },
    'rti': {  'impl': 0x40 },
    'rts': {  'impl': 0x60 },
    'sbc': {  'immed': 0xe9, 'abs': 0xed, 'zp': 0xe5, 'indx': 0xe1, 'indy': 0xf1, 'zpx': 0xf5, 'absx': 0xfd, 'absy': 0xf9 },
    'sec': {  'impl': 0x38 },
    'sed': {  'impl': 0xf8 },
    'sei': {  'impl': 0x78 },
    'sta': {  'abs': 0x8d, 'zp': 0x85, 'indx': 0x81, 'indy': 0x91, 'zpx': 0x95, 'absx': 0x9d, 'absy': 0x99 },
    'stx': {  'abs': 0x8e, 'zp': 0x86, 'zpy': 0x96 },
    'sty': {  'abs': 0x8c, 'zp': 0x84, 'zpx': 0x94 },
    'tax': {  'impl': 0xaa },
    'tay': {  'impl': 0xa8 },
    'tsx': {  'impl': 0xba },
    'txa': {  'impl': 0x8a },
    'txs': {  'impl': 0x9a },
    'tya': {  'impl': 0x98 }
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

        
def eval( tokens, tokenValues, tokenIndex ):
    return None, tokenValues[tokenIndex], tokenIndex + 1        #xxx
    pass


def assembleInstruction( op, tokens, tokenvalues, tokenIndex ):
    # parse addressing mode
    pass


def assembleLine( line ):
    errorString, leadingWhitespace, tokens, tokenValues = tok.tokenize( line )

    if errorString:
        return errorString

    #
    #   SYMBOL = VALUE
    #
    if len(tokens) >= 3 and tokens[0] == tok.SYMBOL and tokens[1] == '=':
        errorString, value, tokenIndex = eval( tokens, tokenValues, 2 )
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
    asert assembleLine( '.label:' ) == None
    assert assembleLine( 'symbol = 42' ) == None

    # more...

if __name__ == '__main__':
    test()
