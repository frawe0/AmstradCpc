;##############################################################
; DOC: 
; https://cheatsheets.one/tech/z80
; https://dn721605.ca.archive.org/0/items/07-le-langage-machine-pour-l-amstrad-cpc-464-664-6128-1987acme/07_Le_langage_machine_pour_l_AMSTRAD_CPC464-664-6128%281987%29%28acme%29.pdf
;

; % cd /Volumes/Data_FW/5-Jeux/5.7-Amstrad/asm
; % ./rasm 5-block.asm
; %### open AceDL.app /Volumes/Data_FW/5-Jeux/5.7-Amstrad/asm/rasmoutput.sna
; Tips:
; bc,de,hl +a accumulator optimized for arithmetic
; assembler directives: DEFB,EQU,ORG
;--------------------------------------------------------------

;--------------------------------------------------------------
; Remove this part to build *.bin instead of *.sna
SNAPINIT 'image6128.sna' ; la mémoire de Rasm est initialisée avec le snapshot
BUILDSNA
SNASET GA_ROMCFG,%1100 ; pour être sûr de démarrer dans la mémoire, on les désactive du snapshot au cas où
BANKSET 0 ; assembler dans les premiers 64K
; MEMORY &A000
; Available for LM: [&A000-&AB7F] below:basic,above System+Screen
; set constant at &AB00+
org #600A ; on veut mettre notre programme au début de la mémoire
run #600A ; et le point de démarrage est ici aussi


;--------------------------------------------------------------
;;;org #A100 : ecran1 incbin 'IM1.BIN'

; ### Init graphic adress:place at x1 ###
ld iy,dest ; goto address
dec iy
ld de,(win_x1_add) ;win_x1>0
add iy,de

; ### Init graphic adress:place at y1 ###
ld de,80
ld a,0
loop_y1:
    inc a
    ld bc,(win_y1_add) #16bit
    cp a,c ; load octet faible
    jr z,end_loop_y1
    add iy,de
    jr nz,loop_y1
end_loop_y1:

; note hl and iy are incremented the same way in parallel
ld hl,source ; source address
ld a,8 ; nb of lines in a block
loop_line;
    push iy;
    push af ; save a for the outer_loop
    ld a,(win_dy_add) ; win_dy stored in (win_dy_add)
    ;ld a,win_dy
    loop_y;
        ; copy block: line: need de,bc,hl
        ;ld   hl,source     ; HL = source address
        ld   de,iy          ; DE = destination address
        ld   bc,(win_dx_add) ; BC = number of bytes to copy
        ;ld   bc,win_dx
        ldir                ; Copy [HL] to [DE], BC times
        ;ld (hl),255
        ; increment hl of 80
        ;pop hl;
        ;ld de,win_dx
        ;add hl,de
        ld de,80
        add iy,de
        dec a
    jr nz,loop_y; run while
    pop af; restore a for the outer_loop
    dec a
    pop iy
    ;pop hl ;get back address of start x
    ld de,#0800 ;offset to next line
    ;inc hl ;jump to next line
    add iy,de
jr nz,loop_line; run while 


;call #BB06 ; wait for keypressed

ret
;--------------------------------------------------------------
; Macro
;--------------------------------------------------------------
win_x1=3
win_dx=4
win_y1=4
win_dy=2
dest=#C000
source=#6200
size = win_dx*win_dy*8
win_x1_add=#6000
win_dx_add=#6002
win_y1_add=#6004
win_dy_add=#6006
;-------------------------------------------
SAVE 'LOADBLCK.BIN',#600A,$-#600A,DSK,'Frawe.dsk'
;SAVE 'IM1.BIN',#A200,size,DSK,'Frawe.dsk'
; en BASIC: load"BLOCK1.BIN",&A000: CALL &A000

;  usage: ./rasm helloword.asm
