gMyGlobal   =   $40


        org     $200

start:  lda     #123
        stx     gMyGlobal

.loop:  adc     #1
        bcc     .loop
        rts
