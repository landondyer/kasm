#
#   Quick tokenizer for an assembler
#

import sys
import re

EOF = 0
STRING = 1
SYMBOL = 2
NUMBER = 3

gTokenTypeToString = [
    "End of file",
    "String",
    "Symbol",
    "Number"
    ]


gMultiCharTokenStarts = {
    '>': { '>': True, '=': True },
    '<': { '<': True, '=': True },
    '=': { '=': True },
    '!': { '=': True }
    }

gSingleCharTokens = {
     '!': True,
     '#': True,
     '%': True,
     '&': True,
     '(': True,
     ')': True,
     '*': True,
     '+': True,
     ',': True,
     '-': True,
     '.': True,
     '/': True,
     ':': True,
     ';': True,
     '=': True,
     '>': True,
     '?': True,
     '@': True,
     '[': True,
     ']': True,
     '^': True,
     '_': True,
     '{': True,
     '|': True,
     '}': True,
     '<': True,
     '~': True
    }


def isSpace( s ):
    return s == ' ' or s == '\t'


def isDigit( s, base=10 ):
    if base <= 10:
        return s >= '0' and s < chr( ord('0') + base )
    elif base == 16:
        return (s >= '0' and s <= '9') or (s >= 'a' and s <= 'f') or (s >= 'A' and s <= 'F')
    else:
        return False


def digitValue( s ):
    if s >= '0' and s <= '9':
        return ord(s) - ord('0')
    elif s >= 'a' and s <= 'f':
        return ord(s) - ord('a') + 10
    elif s >= 'A' and s <= 'F':
        return ord(s) - ord('A') + 10
    else:
        return None


def isSymbolStart( s ):
    return (s >= 'a' and s <= 'z') or (s >= 'A' and s <= 'Z') or s == '_' or s == '.'


def isSymbolContinuation ( s ):
    return (s >= 'a' and s <= 'z') or (s >= 'A' and s <= 'Z') or s == '_' or (s >= '0' and s <= '9')


def skipspace( s, i ):
    while i < len(s) and isSpace( s[i] ):
        i = i + 1
    return i


def parseNumber( s, i ):
    value = 0
    base = 10
    gotDigit = False

    if i + 2 < len(s) and s[i] == '0' and (s[i+1] == 'x' or s[i+1] == 'X'):
        base = 16
        i = i + 2
    elif s[i] == '$':
        base = 16
        i = i + 1
    elif s.startswith( '0b' ) or s.startswith( '0B' ):
        base = 2
        i = i + 2

    while i < len(s) and isDigit( s[i], base ):
        dv = digitValue( s[i] )
        value = value * base + dv
        i = i + 1
        gotDigit = True

    if not gotDigit:
        raise Exception( str.format( "Vaucous number, need actual value digits" ) )
    else:
        return value, i


def parseString( s, i, endQuote ):
    value = ''

    while True:
        if i >= len(s):
            raise Exception( "Unterminated string" )

        c = s[i]
        
        if c == endQuote:
            i = i + 1
            break

        if c == '\\':
            i = i + 1
            if i >= len(s):
                raise Exception( "Bad escape at end of string" )
            c = s[i]

            if c == 'n':
                c = '\n'
            elif c == 't':
                c = '\t'
            elif c == 'r':
                c = '\r'

            value += c
            i = i + 1
            continue
        
        value += c
        i = i + 1

    return value, i


#
#   string ==> ( leadingWhitespaceBool, [token...], [tokenValue...] )
#
def tokenize( s ):

    leadingWhitespace = len(s) > 0 and isSpace( s[0] )
    tokens = []
    tokenValues = []
    
    i = 0
    while i < len(s):
        i = skipspace( s, i )
        if i >= len(s):
            break

        c = s[i]
        
        if isDigit( c ) or c == '$':
            value, i = parseNumber( s, i )
            tokens.append( NUMBER )
            tokenValues.append( value )

        elif isSymbolStart( c ):
            symbol = c
            i = i + 1
            while i < len(s) and isSymbolContinuation( s[i] ):
                symbol += s[i]
                i = i + 1
            tokens.append( SYMBOL )
            tokenValues.append( symbol )

        elif c == '\'':
            value, i = parseString( s, i + 1, '\'' )
            tokens.append( STRING )
            tokenValues.append( value )

        elif c == '"':
            value, i = parseString( s, i + 1, '"' )
            tokens.append( STRING )
            tokenValues.append( value )

        elif c == ';':
            #   stop at comment
            break

        elif c in gMultiCharTokenStarts and i + 1 < len(s) and s[i+1] in gMultiCharTokenStarts[c]:
            tokens.append( s[i:i+1] )
            tokenValues.append( None )
            i = i + 2

        elif c in gSingleCharTokens:
            tokens.append( c )
            tokenValues.append( None )
            i = i + 1

        else:
            raise Exception( str.format( 'Unexpected character: {0}', c ) )


    return leadingWhitespace, tokens, tokenValues


class Tokenizer:

    def __init__( self, string ):
        self.m_leadingWhitespace, self.m_tokens, self.m_tokenValues = tokenize( string )
        self.m_tokenIndex = 0

    def leadingWhitespace( self ):
        return self.m_leadingWhitespace

    def atEnd( self ):
        return self.m_tokenIndex >= len( self.m_tokens )

    def advance( self ):
        if self.m_tokenIndex < len( self.m_tokens ):
            self.m_tokenIndex = self.m_tokenIndex + 1
        else:
            raise Exception( "unexpected end of line" )

    def nextTok( self ):
        if self.atEnd():
            raise Exception( "Unexpected end" )

        self.m_tokenIndex = self.m_tokenIndex + 1
        return self.curTok()

    def curTok( self ):
        if self.m_tokenIndex < len( self.m_tokens ):
            return self.m_tokens[self.m_tokenIndex]
        else:
            return EOF

    def curValue( self ):
        if self.m_tokenIndex < len( self.m_tokens ):
            return self.m_tokenValues[self.m_tokenIndex]
        else:
            raise Exception( "Ran off end of tokens" )

    # expect a token, an optional value, and advance past it
    def expect( self, expectedTok, expectedValue=None ):
        if self.curTok() != expectedTok:
            raise Exception( str.format( "Expected token type {0}", gTokenTypeToString( expectedTok) ) )

        if expectedValue != None and expectedValue != self.curValue():
            raise Exception( str.format( "Expected value {0}", expectedValue ) )

        if not self.atEnd():
            self.m_tokenIndex = self.m_tokenIndex + 1


def test():
    assert not isSpace( 'x' )
    assert isSpace( ' ' )
    assert isSpace( '\t' )
    
    assert not isDigit( 'a' )
    assert isDigit( '0' )
    assert isDigit( '8' )
    assert isDigit( '9' )
    assert isDigit( '0', 16 )
    assert isDigit( '9', 16 )
    assert isDigit( 'a', 16 )
    assert isDigit( 'f', 16 )
    assert isDigit( 'A', 16 )
    assert isDigit( 'F', 16 )
    assert not isDigit( 'G', 16 )
    assert not isDigit( 'g', 16 )
    
    assert not isSymbolStart( '=' )
    assert isSymbolStart( 'a' )
    assert isSymbolStart( 'z' )
    assert isSymbolStart( 'Z' )
    assert not isSymbolStart( '0' )
    
    assert not isSymbolContinuation( '=' )
    assert isSymbolContinuation( 'a' )
    assert isSymbolContinuation( 'z' )
    assert isSymbolContinuation( 'Z' )
    assert isSymbolContinuation( '0' )

    def testNumber( s, wantedValue ):
        v, i = parseNumber( s, 0 )
        assert v == wantedValue

    testNumber( '0', 0 )
    testNumber( '1', 1 )
    testNumber( '9', 9 )
    testNumber( '42', 42 )
    testNumber( '0xdeadbeef', 0xdeadbeef )
    testNumber( '0XDEADBEEF', 0xdeadbeef )
    testNumber( '0b111', 7 )
    testNumber( '0B111', 7 )
    testNumber( '0xffffffff', 0xffffffff )
    testNumber( '0xffffffff', 0xffffffff )

    def brokenNumber( s ):
        try:
            v, i = parseNumber( s, 0 )
            assert False # should have taken an exception
        except:
            pass

    brokenNumber( '0x' )
    brokenNumber( '0b' )

    def testString( s, wantedValue ):
        v, i = parseString( s, 1, s[0] )
        assert v == wantedValue

    testString( '\'\'', '' )
    testString( '\'test\'', 'test' )
    testString( '\'code=\\n\'', 'code=\n' )
    testString( '\'code=\\r\'', 'code=\r' )
    testString( '\'code=\\t\'', 'code=\t' )
    testString( '\'code=\\\\\'', 'code=\\' )
    testString( '\'code=\\\'\'', 'code=\'' )

    def brokenString( s ):
        try:
            v, i = parseString( s, 1, s[0] )
            assert False        # should have taken an exception
        except:
            pass

    brokenString( '\'foo' )
    brokenString( '\'foo\\' )

    print tokenize( 'this is a test' )
    print tokenize( 'label: adc a, #42' )
    print tokenize( 'label: db "a string"' )
    print tokenize( '\ttya' )
    print tokenize( ' foo ; comment ' )


def testTokenizer():
    def printTokens( tokenizer ):
        while not tokenizer.atEnd():
            print tokenizer.curTok(), tokenizer.curValue()
            tokenizer.nextTok()

    printTokens( Tokenizer( "label: lda #0x42  ; get froggles" ) )
    printTokens( Tokenizer( "label: lda #$42  ; get froggles" ) )
    

if __name__ == '__main__':
    test()
    testTokenizer()
