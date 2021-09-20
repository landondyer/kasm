
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

gBranchOps = {
    'bcc': {  REL: 0x90 },
    'bcs': {  REL: 0xb0 },
    'beq': {  REL: 0xf0 },
    'bne': {  REL: 0xd0 },
    'bmi': {  REL: 0x30 },
    'bpl': {  REL: 0x10 },
    'bvc': {  REL: 0x50 },
    'bvs': {  REL: 0x70 },
    }

gOps = {
    'adc': {  IMMED: 0x69, ABS: 0x6d, ZP: 0x65, INDX: 0x61, INDY: 0x71, ZPX: 0x75, ABSX: 0x7d, ABSY: 0x79 },
    'and': {  IMMED: 0x29, ABS: 0x2d, ZP: 0x25, INDX: 0x21, INDY: 0x31, ZPX: 0x35, ABSX: 0x3d, ABSY: 0x39 },
    'asl': {  ABS: 0x0e, ZP: 0x06, IMPLIED: 0x0a, ZPX: 0x16, ABSX: 0x1e },
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
UNDECIDED_X = 12
UNDECIDED_Y = 13
UNDECIDED = 14



def PrintTestVector():

    def emit( *args ):
        print('\t' + ' '.join( args ))

    def emitTestImplied( op ):
        emit( op )

    def emitTestImmed( op ):
        emit( op, '#123' )

    def emitTestAbs( op ):
        emit( op, 'abs' )

    def emitTestZp( op ):
        emit( op, 'zp' )

    def emitTestAbsx( op ):
        emit( op, 'abs,x' )

    def emitTestAbsy( op ):
        emit( op, 'abs,y' )

    def emitTestInd( op ):
        emit( op, '(abs)' )
        emit( op, '(zp)' )

    def emitTestRel( op ):
        emit( op, 'rel' )

    def emitTestZpx( op ):
        emit( op, 'zp,x' )

    def emitTestZpy( op ):
        emit( op, 'zp,y' )

    def emitTestIndx( op ):
        emit( op, '(zp,x)' )

    def emitTestIndy( op ):
        emit( op, '(zp),y' )

    def emitTestUndecided_X( op ):
        emit( op, '(abs),x' )
        emit( op, '(zp),x' )

    def emitTestUndecided_Y( op ):
        emit( op, '(abs),y' )
        emit( op, '(zp),y' )

    def emitTestUndecided( op ):
        emit( op, 'abs' )
        emit( op, 'zp' )


    testVectorEmitters = {
        IMPLIED: emitTestImplied,
        IMMED: emitTestImmed,
        ABS: emitTestAbs,
        ZP: emitTestZp,
        ABSX: emitTestAbsx,
        ABSY: emitTestAbsy,
        IND: emitTestInd,
        REL: emitTestRel,
        ZPX: emitTestZpx,
        ZPY: emitTestZpy,
        INDX: emitTestIndx,
        INDY: emitTestIndy,
        UNDECIDED_X: emitTestUndecided_X,
        UNDECIDED_Y: emitTestUndecided_Y,
        UNDECIDED: emitTestUndecided
        }

    def emitBoilerplate():
        print("abs = 0x1234")
        print("zp = 0x56")
        print("rel: nop")

    emitBoilerplate()

    for op in gBranchOps:
        for mode in gBranchOps[op]:
            testVectorEmitters[mode]( op )

    for op in gOps:
        for mode in gOps[op]:
            testVectorEmitters[mode]( op )


PrintTestVector()
