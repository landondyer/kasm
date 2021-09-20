#
#   Expression evaluator
#
#   Constructor: Expression( tokenizer ), parses next expression
#
#   Subsequent calls to 'eval' cough up an integer value, or None
#

import symbols
import tok


class Expression:

    def __init__( self, tokenizer ):
        self.initOperators()
        self.parse( tokenizer )
        
    def doPushConst( self ):
        self.m_stack.append( self.m_postfix[ self.m_index] )
        self.m_index = self.m_index + 1

    def doPushSym( self ):
        symbol = self.m_postfix[ self.m_index]
        self.m_index = self.m_index + 1

        if symbols.isDefined( symbol ):
            self.m_stack.append( symbols.get( symbol ) )
        else:
            self.m_undefined = True
            self.m_stack.append( 1 )

    def doAdd( self ):
        v1 = self.m_stack.pop()
        v2 = self.m_stack.pop()
        self.m_stack.append( v2 + v1 )

    def doAnd( self ):
        v1 = self.m_stack.pop()
        v2 = self.m_stack.pop()
        self.m_stack.append( v2 & v1 )

    def doDiv( self ):
        if self.m_undefined:
            self.m_stack.pop()
        else:
            v1 = self.m_stack.pop()
            v2 = self.m_stack.pop()
            if v1 == 0:
                raise Exception( "Division by zero" )
            self.m_stack.append( v2 / v1 )

    def doEQ( self ):
        v1 = self.m_stack.pop()
        v2 = self.m_stack.pop()
        if v1 == v2:
            self.m_stack.append( 1 )
        else:
            self.m_stack.append( 0 )

    def doGE( self ):
        v1 = self.m_stack.pop()
        v2 = self.m_stack.pop()
        if v1 >= v2:
            self.m_stack.append( 1 )
        else:
            self.m_stack.append( 0 )

    def doGT( self ):
        v1 = self.m_stack.pop()
        v2 = self.m_stack.pop()
        if v1 > v2:
            self.m_stack.append( 1 )
        else:
            self.m_stack.append( 0 )

    def doLE( self ):
        v1 = self.m_stack.pop()
        v2 = self.m_stack.pop()
        if v1 <= v2:
            self.m_stack.append( 1 )
        else:
            self.m_stack.append( 0 )

    def doLT( self ):
        v1 = self.m_stack.pop()
        v2 = self.m_stack.pop()
        if v1 < v2:
            self.m_stack.append( 1 )
        else:
            self.m_stack.append( 0 )

    def doMod( self ):
        if self.m_undefined:
            self.m_stack.pop()
        else:
            v1 = self.m_stack.pop()
            v2 = self.m_stack.pop()
            if v1 == 0:
                raise Exception( "Modulo by zero" )
            self.m_stack.append( v2 % v1 )

    def doMult( self ):
        v1 = self.m_stack.pop()
        v2 = self.m_stack.pop()
        if v1 == 0:
            v1 = 1
        self.m_stack.append( v2 * v1 )

    def doNE( self ):
        v1 = self.m_stack.pop()
        v2 = self.m_stack.pop()
        if v1 != v2:
            self.m_stack.append( 1 )
        else:
            self.m_stack.append( 0 )

    def doOr( self ):
        v1 = self.m_stack.pop()
        v2 = self.m_stack.pop()
        self.m_stack.append( v2 | v1 )

    def doSHL( self ):
        v1 = self.m_stack.pop()
        v2 = self.m_stack.pop()
        self.m_stack.append( v2 << v1 )

    def doSHR( self ):
        v1 = self.m_stack.pop()
        v2 = self.m_stack.pop()
        self.m_stack.append( v2 >> v1 )

    def doSub( self ):
        v1 = self.m_stack.pop()
        v2 = self.m_stack.pop()
        self.m_stack.append( v2 - v1 )

    def doXor( self ):
        v1 = self.m_stack.pop()
        v2 = self.m_stack.pop()
        self.m_stack.append( v2 ^ v1 )

    def doNeg( self ):
        self.m_stack[-1] = - self.m_stack[-1]

    def doNot( self ):
        v = self.m_stack[-1]
        if v:
            self.m_stack[-1] = 0
        else:
            self.m_stack[-1] = 1

    def eval( self ):
        self.m_undefined = []
        self.m_stack = []
        self.m_index = 0

        while self.m_index < len(self.m_postfix):
            fn = self.m_postfix[self.m_index]
            self.m_index += 1
            fn()

        assert len(self.m_stack) == 1

        if self.m_undefined:
            return None
        else:
            return self.m_stack[0]

    def isUndefined( self ):
        return len(self.m_undefined) == 0


    #
    #   operators, in increasing precedence
    #   unary operators, terms and parenthesis are handled "by hand"
    #
    def initOperators( self ):
        self.m_operators = [
                { '&': self.doAnd, '^': self.doXor, '|': self.doOr },
                { '<': self.doLT, '<=': self.doLE, '>': self.doGT, '>=': self.doGE, '==': self.doEQ, '!=': self.doNE },
                { '<<': self.doSHL, '>>': self.doSHR },
                { '+': self.doAdd, '-': self.doSub },
                { '*': self.doMult, '/': self.doDiv, '%': self.doMod }
            ]


    def parse( self, tokenizer ):

        def parseTerm():
            if tokenizer.curTok() == tok.SYMBOL:
                self.m_postfix.append( self.doPushSym )
                self.m_postfix.append( tokenizer.curValue() )
                tokenizer.nextTok()
            elif tokenizer.curTok() == tok.NUMBER:
                self.m_postfix.append( self.doPushConst)
                self.m_postfix.append( tokenizer.curValue() )
                tokenizer.nextTok()
            elif tokenizer.curTok() == tok.STRING:
                if len(tokenizer.curValue()) != 1:
                    raise Exception( 'String constants must be one character' )
                self.m_postfix.append( self.doPushConst)
                self.m_postfix.append( ord(tokenizer.curValue()[0]) )
                tokenizer.nextTok()
            elif tokenizer.curTok() == '(':
                tokenizer.advance()
                parseHelper( len(self.m_operators) - 1)
                tokenizer.expect( ')' )
            elif tokenizer.curTok() == '*':
                self.m_postfix.append( self.doPushSym )
                self.m_postfix.append( '*' )
                tokenizer.nextTok()
            else:
                raise Exception( str.format( "unexpected token {0}", tokenizer.curTok() ) )

        def parseUnary():
            if tokenizer.curTok() == '-':
                tokenizer.advance()
                parseTerm()
                self.m_postfix.append( self.doNeg )
            elif tokenizer.curTok() == '!':
                tokenizer.advance()
                parseTerm()
                self.m_postfix.append( self.doNot )
            else:
                parseTerm()

        def parseHelper( level ):
            if level < 0:
                parseUnary()
            else:
                parseHelper( level - 1 )
                while tokenizer.curTok() in self.m_operators[level]:
                    op = tokenizer.curTok()
                    tokenizer.advance()
                    parseHelper( level - 1 )
                    self.m_postfix.append( self.m_operators[level][op] )

        self.m_postfix = []
        parseHelper( len(self.m_operators) - 1)


def test():
    def testExpr( expr ):
        t = tok.Tokenizer( expr )
        e = Expression( t )
        print(expr, " ==> ", e.eval())

    testExpr( "42" )
    testExpr( "3 + 4" )
    testExpr( "9 - 5" )
    testExpr( "8 / 4" )
    testExpr( "10 % 3" )
    testExpr( "15 & 3" )
    testExpr( "1 | 6" )
    testExpr( "1 << 8" )
    testExpr( "1024 >> 2" )
    testExpr( "(1 + 2) * 3" )
    testExpr( "4 * (1 + 2)" )
    testExpr( "4 * (1 + 2) * 100" )
    testExpr( "-100" )
    testExpr( "! 1" )
    testExpr( "! 0" )

    symbols.set( "foo", 42 )
    testExpr( "foo" )
    testExpr( "foo + foo * 100 * foo" )

    symbols.set( "bar", 0x10000 )
    testExpr( "bar - 1" )

    testExpr( "notYetDefined" )


if __name__ == '__main__':
    test()
