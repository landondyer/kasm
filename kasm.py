#
#   Simple 6502 assembler
#   Writen by Landon Dyer
#   ABRMS license
#

import sys

import tok
import eval
import fileinput
import symbols
import traceback
import re


gListingFile = None
gInput = None
gPriorFile = None


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


gLoc = 0


#   ----------------------------------------------------------------
#   Pseudo ops
#   ----------------------------------------------------------------

def fn_org( tokenizer, phaseNumber ):
    global gLoc
    org = eval.Expression( tokenizer ).eval()
    if org == None:
        raise Exception( "Undefined expression" )
    gLoc = org


def fn_db( tokenizer, phaseNumber ):
    while not tokenizer.atEnd():

        if tokenizer.curTok() == tok.STRING:

            s = tokenizer.curValue()
            for c in s:
                depositByte( ord( c ) )

            tokenizer.advance()

        else:

            expr = eval.Expression( tokenizer )

            value = expr.eval()
            if phaseNumber > 0:
                if value > 0xff or value < -128:
                    raise Exception( "value too large for a byte" )
                depositByte( value )

            else:
                depositByte( 0 )

        if tokenizer.curTok() != ',':
            break
        else:
            tokenizer.advance()


def fn_dw( tokenizer, phaseNumber ):

    while not tokenizer.atEnd():

        if tokenizer.curTok() == tok.STRING:

            s = tokenizer.curValue()
            for c in s:
                depositWord( ord( c ) )

            tokenizer.advance()

        else:

            expr = eval.Expression( tokenizer )

            value = expr.eval()
            if phaseNumber > 0:
                depositWord( value )

            else:
                depositWord( 0 )

        if tokenizer.curTok() != ',':
            break
        else:
            tokenizer.advance()


def fn_ds( tokenizer, phaseNumber ):
    global gLoc
    
    value = eval.Expression( tokenizer ).eval()
    if value == None:
        raise Exception( "Undefined expression" )
    gLoc += value


def fn_include( tokenizer, phaseNumber ):

    if tokenizer.curTok() == tok.STRING or tokenizer.curTok() == tok.SYMBOL:
        gInput.push( tokenizer.curValue() )
        tokenizer.advance()
    else:
        raise Exception( "Expected filename" )


gPsuedoOps = {
    'org':      fn_org,
    'db':       fn_db,
    'dw':       fn_dw,
    'ds':       fn_ds,
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
            elif tokenizer.curValue().lower() == 'y':
                return UNDECIDED_Y, expr
            else:
                raise Exception( str.format( "Unxpected symbol {0} following expression", tokenizer.curValue() ) )
        else:
            raise Exception( "Unxpected gunk following expression" )

    return UNDECIDED, expr


#   ----------------------------------------------------------------
#   Image construction
#   ----------------------------------------------------------------


gMemory = [None] * 65536
gThisLine = []


def clearLineBytes():
    global gThisLine
    gThisLine = []


def depositByte( byte ):
    global gLoc, gThisLine

    if byte == None:
        byte = 0

    #xxx print("DEP ", gLoc, byte)
    gMemory[gLoc] = byte & 0xff
    gThisLine.append( byte & 0xff )
    gLoc += 1
    if gLoc >= 0x10000:
        gLoc = 0


def depositWord( word ):

    if word == None:
        word = 0

    depositByte( word )
    depositByte( word >> 8 )


#   ----------------------------------------------------------------
#   Assembly
#   ----------------------------------------------------------------

def depositImpliedArg( expr, value ):
    pass

def depositByteArg( expr, value ):
    depositByte( value )

def depositAbsArg( expr, value ):
    depositWord( value )

def depositRelArg( expr, value ):
    global gLoc

    if value != None:
        fromLoc = gLoc + 1
        delta = value - fromLoc

        if delta < -128 or delta > 127:
            raise Exception( str.format( "relative reference out of range ({0} bytes)", delta ) )
        depositByte( delta )

    else:

        depositByte( 0 )
    

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
        
    if phaseNumber > 0 and value == None and addrMode != IMPLIED:
        raise Exception( "Undefined expression" )

    #
    #   Translate UNDECIDED into various forms of REL / ZP / ABS
    #
    if not addrMode in gOps[op]:

        if addrMode == UNDECIDED:

            if REL in gOps[op]:
                addrMode = REL
            elif ZP in gOps[op] and value != None and value < 0x100:
                addrMode = ZP
            else:
                addrMode = ABS

        elif addrMode == UNDECIDED_X:

            if ZPX in gOps[op] and value != None and value < 0x100:
                addrMode = ZPX
            else:
                addrMode = ABSX

        elif addrMode == UNDECIDED_Y:

            if ZPY in gOps[op] and value != None and value < 0x100:
                addrMode = ZPY
            else:
                addrMode = ABSY

    if addrMode in gOps[op]:

        depositByte( gOps[op][addrMode] )
        gDepositDispatch[addrMode]( expr, value )

    else:

        raise Exception( "Bad addressing mode for instruction" )


def generateListingLine( line ):
    global gListingFile, gPriorFile

    if gInput.file() != gPriorFile:
        gListingFile.write( str.format( "File {0}\n", gInput.file() ) )
        gPriorFile = gInput.file()

    prefix = str.format( "{0:5}: ", gInput.line() )
    baseAddr = gLoc - len( gThisLine )

    if len( gThisLine ) > 0:
        i = 0
        while i < len( gThisLine ):
            n = len( gThisLine ) - i
            if n > 8:
                n = 8

            s, ascii = dump( gThisLine, i, i + n )

            if i == 0:
                gListingFile.write( str.format( "{0} {1:04X}  {2:30} {3}", prefix, baseAddr + i, s, line ) )
            else:
                gListingFile.write( str.format( "{0} {1:04X}  {2:10}\n", prefix, baseAddr + i, s ) )

            i += n

    else:

        gListingFile.write( str.format( "{0} {1:30} {2}", prefix, "", line ) )


#
#   Handle a line of assembly input
#
#   Phase 0:    just intern stuff
#   Phase 1:    emit stuff (expressions required to be defined)
#
def assembleLine( line, phaseNumber=0 ):
    global gLoc
    
    clearLineBytes()
    tokenizer = tok.Tokenizer( line )

    #
    #   Set '*' psuedo-symbol at the start of each line
    #
    symbols.set( '*', gLoc )

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
        
        symbols.set( sym, expr.eval() )

        if gListingFile != None and phaseNumber > 0:
            generateListingLine( line )

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
            symbols.set( sym, gLoc )
            
        else:
            #
            #   check that the symbol has the same value in
            #   subsequent phases
            #
            symbols.setScope( sym )
            if symbols.get( sym ) != gLoc:
                raise Exception( str.format( "Symbol phase error (expected {0}, have {1})", symbols.get(sym), gLoc ) )

    #
    #   handle ops
    #
    if tokenizer.curTok() == tok.SYMBOL:

        op = tokenizer.curValue().lower()
        tokenizer.advance()
        
        if op in gPsuedoOps:
            gPsuedoOps[op]( tokenizer, phaseNumber )
        elif op in gOps:
            assembleInstruction( op, tokenizer, phaseNumber )
        else:
            raise Exception( str.format( 'Unknown op: {0}', op ) )

    if gListingFile != None and phaseNumber > 0:
        generateListingLine( line )


def assembleFile( filename ):
    global gInput, gPriorFile, gLoc
    
    symbols.clear()
    gPriorFile = None
    gotError = False
    
    for phase in range(0,2):

        if gotError:
            break
            
        try:
            gInput = fileinput.FileInput( filename )
        except:
            print("Error: {0}", sys.exc_info()[1])
            return

        gLoc = 0

        try:
            while True:
                line = gInput.nextLine()
                if not line:
                    break
                assembleLine( line, phase )
        except:
            err = str.format("Error: {0}({1}): {2}",
                gInput.file(),
                gInput.line(),
                sys.exc_info()[1] )
            print(err)
            gotError = True
            # traceback.print_exc()

    return not gotError


def dump(ar, start, end ):
    s = ''
    ascii = ''
    j = 0

    for i in range( start, end ):
        v = 0
        if ar[i] != None:
            v = ar[i]

        if j > 0:
            s += ' '

        if j == 8:
            s += ' '

        s += str.format('{0:02X}', v)

        if v >= ord(' ') and v <= 0x7f:
            ascii += chr( v )
        else:
            ascii += '.'

        j = j + 1

    return s, ascii

def dumpMem():
    global gMemory

    def probe( start, end ):
        for i in range(start, end):
            if gMemory[i] != None:
                return True
        return False

    i = 0
    while i < 0x10000:
        if probe(i, i + 16):
            s, ascii = dump(gMemory, i, i+16)
            print(str.format('{0:04X}  {1}  {2}', i, s, ascii ))
        i += 0x10


def makeKim1Record( ar, start, end ):
    record = str.format( ';{0:02X}{1:02X}{2:02X}',
        end - start,
        (start >> 8) & 0xff,
        start & 0xff )
    sum = 0

    for i in range( start, end ):
        v = 0
        if ar[i] != None:
            v = ar[i]
        record += str.format( '{0:02X}', v )
        sum += v

    record += str.format( '{0:02X}{1:02X}\r\n', (sum >> 8) & 0xff, sum & 0xff )
    return record


def dumpKim1Records( filename, startAddress=0 ):
    global gMemory

    def probe( start, end ):
        if end > 0x10000:
            end = 0x10000
            
        for i in range(start, end):
            if gMemory[i] != None:
                return True
        return False

    outputFile = open( filename, 'w' )

    recordCount = 0
    i = 0
    while i < 0x10000:
        if probe( i, i + 16 ):
            outputFile.write( makeKim1Record( gMemory, i, i + 16 ) )
            recordCount += 1
        i += 16

    outputFile.write( str.format( ';00{0:02X}{1:02X}{0:02X}{1:02X}\r\n',
        (recordCount >> 8) & 0xff,
        recordCount & 0xff )
        )

    outputFile.close()


gCommands = {
    # 'foo': { 'handler': function, 'count': numberOfArguments }
    }


def main( argv ):
    global gCommands
    global gListingFile
    
    argno = 1
    while argno < len( argv ):

        arg = argv[argno].lower()

        if arg in gCommands:
            count = 0
            if 'count' in gCommands[arg]:
                count = gCommands[arg]['count']
                if argno + count >= len( argv ):
                    raise Exception( str.format( "Not enough arguments for {0}", arg ) )

                args = argv[argno + 1 : argno + count + 1]
                argno += count + 1
                gCommands[arg]['handler'](*args)
            else:
                argno += 1
                gCommands[arg]['handler']()
                
        elif arg.startswith( '-' ):
            
            raise Exception( str.format( "Unknown option {0}", arg ) )

        else:
            
            argno += 1

            match = re.match( ".*\.(.*)", arg )
            if not match:
                arg += ".asm"

            match = re.match( "(.*\.).*", arg )
            if not match:
                raise Exception( "internal error flogging filenames" )

            baseFile = match.group(1)
            listingFile = baseFile + "lst"
            outputFile = baseFile + "dat"

            gListingFile = open( listingFile, "w" )

            if assembleFile( arg ):
                dumpKim1Records( outputFile )


if __name__ == '__main__':
    try:
        main( sys.argv )
    except:
        err = str.format( "Error: {0}", sys.exc_info()[1] )
        print(err)
