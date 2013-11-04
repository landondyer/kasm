        include "test.inc"

gMyGlobal   =   $40


        org     $200

        db      1,2,3

        db      gronk

gronk = 0xfe

        db      'this is a test\n'
        dw      1234, 0, 0xffff, 0x8000, -32768
        dw      'this is unicode?'

        jsr     start
        nop
        nop
start:  lda     #123
        stx     gMyGlobal

.loop:  adc     #1
        bcc     .loop
        rts


kongb   =     $80

pckong:
	tax				; kongb ~= A
	eor	kongb
	sta	kongb
	txa


