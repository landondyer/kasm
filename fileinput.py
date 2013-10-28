
class FileInput:

    def __init__( self, filename=None ):
        self.m_filenames = []
        self.m_lines = []
        self.m_lineIndices = []

        if filename:
            self.push( filename )

    def push( self, filename ):
        try:
            lines = []
            with open( filename ) as file:
                for line in file:
                    lines.append( line )

            self.m_filenames.append( filename )
            self.m_lines.append( lines )
            self.m_lineIndices.append( 0 )

        except:
            raise Exception( str.format( "Can't open {0}", filename ) )
            

    def nextLine( self ):
        if len( self.m_lineIndices ) == 0:
            return None

        if self.m_lineIndices[-1] >= len( self.m_lines[-1] ):
            self.pop()
            return self.nextLine()

        lineIndex = self.m_lineIndices[-1]
        self.m_lineIndices[-1] = lineIndex + 1

        return self.m_lines[-1][lineIndex]


    def pop( self ):
        if len( self.m_lineIndices ) > 0:
            self.m_filenames.pop()
            self.m_lines.pop()
            self.m_lineIndices.pop()


    def file( self ):
        if len( self.m_filenames ) > 0:
            return self.m_filenames[-1]
        else:
            return "(top level)"


    def line( self ):
        if len( self.m_lineIndices ) > 0:
            return self.m_lineIndices[-1]
        else:
            return 1


def test():
    filer = FileInput()
    filer.push( 'fileinput.py' )
    filer.push( 'kasm.py' )
    while True:
        line = filer.nextLine()
        if line:
            print filer.file(), filer.line(), str.format("{0!r}", line)
        else:
            print "EOF"
            break

if __name__ == '__main__':
    test()
