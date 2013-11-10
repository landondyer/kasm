kasm
====

This is a simple two-pass 6502 assembler that I wrote for fun. No warranty expressed or implied.

It supports standard opcodes and opcode syntax. Binary output is in Kim-1 format.

Command line synopsis:

    python kasm.py inputfile[.asm]

The files 'inputfile.lst' (an assembler listing) and 'inputfile.dat' (the Kim-1 format binary) are produced unconditionally.

General syntax:

Labels are case sensitive, and are followed with a colon. Assembler
mnemonics and psuedo-ops are not case sensitive. The special symbol
'*' is the location counter of the start of the current line of input.

    ; ----------------
    ; comments start with semicolons

            include     "filename.asm"
            org         expression                  ; set location counter
            db          byte, byte, byte...
            dw          word, word, word...
            ds          expression                  ; reserve bytes

Labels have colons:

    label:      op      operand(s)

Equate values with =

    symbol      =       expression

Labels starting with '.' are local between labels that don't start with '.'

    func:       lda     #1
    .loop       adc     #1
                bcc     .loop
    mumble:     ldx     #1
    .loop       inx                             ; distinct from first '.loop'
                bne     .loop

Expressions use C operators, and C operator precedence. Operators are (in order of decreasing precedence):

    ( expression )

    -                   (unary minus)
    !                   (logical not, yields 0 or 1)

    *     /     % 

    +     - 

    <<     >> 

    <     <=     >     >=     ==     != 

    &     ^     |



Development status:

This assembles some moderately size files without fuss, and apparently correctly (I tried it on Microchess, for instance). There are probably bugs in it.

It would be nice if the listing file wasn't unconditionally created, but it's fine for me at the moment.

It would be nice to have macros and conditional assembly.

It would be nice to have (say) Atari output format, but I don't really need it.

More pseudo-ops might be interesting (e.g., EQU in addition to '=').
