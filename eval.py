import kasm
import tok


class Expression:

    def __init__( self, postfix ):
        self.m_postfix = postfix
        self.m_index = 0
        self.m_stack = []
        self.initOperators()
        
    def doPushConst( self ):
        self.m_stack.append( self.m_postfix[ self.m_index] )
        self.m_index = self.m_index + 1

    def doPushSym( self ):
        pass

    def doAdd( self ):
        pass

    def doAnd( self ):
        pass

    def doDiv( self ):
        pass

    def doEQ( self ):
        pass

    def doGE( self ):
        pass

    def doGT( self ):
        pass

    def doLE( self ):
        pass

    def doLT( self ):
        pass

    def doMod( self ):
        pass

    def doMult( self ):
        pass

    def doNE( self ):
        pass

    def doOr( self ):
        pass

    def doSHL( self ):
        pass

    def doSHR( self ):
        pass

    def doSub( self ):
        pass

    def doXor( self ):
        pass

    def eval( self ):
        while self.m_index < len(self.m_postfix):
            fn = self.m_postfix[self.m_index]
            self.m_index += 1
            fn()

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


    def parse( self, tok ):

        def parseHelper():

            def parseTerm():
                if tok.curTok() == tok.SYMBOL:
                    self.m_postfix.append( [ doPushSym, tok.curValue] )
                    tok.nextTok()
                elif tok.curTok() == tok.NUMBER:
                    self.m_postfix.append( [ doPushConst, tok.curValue] )
                    tok.nextTok()
                elif tok.curTok() == '(':
                    tok.advance()
                    parseHelper()
                    tok.expect( ')' )
                else:
                    raise Exception( "unexpected token" )

            def parseUnary():
                if tok.curTok() == '-':
                    parseTerm()
                    self.m_postfix.append( doNeg )
                elif tok.curTok() == '!':
                    parseTerm()
                    self.m_postfix.append( doNot )
                else:
                    parseTerm()

            def parse( level ):
                if level == 0:
                    parseUnary()
                else:
                    parse( level - 1 )
                    while tok.curTok() in self.m_operators[level]:
                        op = tok.curTok()
                        parse( level - 1 )
                        self.m_postfix.append( op )

        parse( len(self.m_operators) - 1)



def test():
    e = Expression( tok.Tokenizer("42") )
    # e.eval()

if __name__ == '__main__':
    test()
