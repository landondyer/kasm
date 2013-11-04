kasm
====

Simple 6502 assembler

Supports standard opcodes and opcode syntax.

General syntax:

labels are case sensitive. Assembler mnemonics and psuedo-ops are not
case sensitive.

    ; ----------------
    ; comments start with semicolons

    include "filename.asm"
    org     expression                  ; set location counter
    db      byte, byte, byte...
    dw      word, word, word...
    ds      expression                  ; reserve bytes
    ; ----------------

Labels have colons:

    ; ----------------
    label:  op  operand(s)
    ; ----------------

Equate values with =

    ; ----------------
    symbol  =   expression
    ; ----------------

Labels starting with '.' are local between labels that don't start with '.'

    ; ----------------
    func:   lda     #1
    .loop   adc     #1
            bcc     .loop
    mumble: ldx     #1
    .loop   inx                         ; distinct from first '.loop'
            bne     .loop
    ; ----------------

Expressions use C operators, and C operator precedence.

Operators are

    ( expression )
    -                   (unary)
    !                   (unary)

    { '&': self.doAnd, '^': self.doXor, '|': self.doOr },
    { '<': self.doLT, '<=': self.doLE, '>': self.doGT, '>=': self.doGE, '==': self.doEQ, '!=': self.doNE },
    { '<<': self.doSHL, '>>': self.doSHR },
    { '+': self.doAdd, '-': self.doSub },
    { '*': self.doMult, '/': self.doDiv, '%': self.doMod }

