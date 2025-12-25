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
org #6000 ; on veut mettre notre programme au début de la mémoire
run #6000 ; et le point de démarrage est ici aussi

;--------------------------------------------------------------
init_variable ; label -> should be replaced by poke

;ld hl,#AB01
;ld (hl),#04
;ld hl,#AB02
;ld (hl),#00

;ld hl,#AB03
;ld (hl),10
;ld hl,#AB04
;ld (hl),#00

; formatting 
;ld a,2
;call #BC0E ; set  mode 2
;ld h,5    ; row (Y coordinate)
;ld l,10    ; column (X coordinate)
;call #BB75 ; locate x,y

;save_binary:
    ;ld de, #C000    ; start of memory to save
    ;ld bc, #FF        ; number of bytes to save
    ;ld hl, filename   ; address of zero-terminated filename string
    ;call &BD19              ; AMSDOS SAVE call

;ld hl,#a501
;ld (hl),255

start_saveblock;
; ### Init graphic adress:place at x1 ###
ld hl,#BFFF
ld de,win_x1 ;win_x1>0
add hl,de

; ### Init graphic adress:place at y1 ###
ld de,80
ld a,0
loop_y1:
    inc a
    cp a,win_y1
    jr z,end_loop_y1
    add hl,de
    jr nz,loop_y1
end_loop_y1:

; note hl is incremented to scan the window
; whereas iy is incremented one by one
ld iy,dest ; goto address
ld a,8 ; nb of lines in a block

loop_line;
    push hl;
    ;push iy;
    push af ; save a for the outer_loop
    ld a,win_dy
    loop_y;
        push hl; because used by cmd ldir
        ;ld (hl),127; to debug
        ; copy block: line: need de,bc,hl
        ;ld   hl,source     ; HL = source address
        ld   de,iy          ; DE = destination address
        ld   bc,win_dx      ; BC = number of bytes to copy
        ldir                ; Copy [HL] to [DE], BC times
        ; increment hl of 80
        pop hl;
        ld (hl),255; to debug
        ld de,80
        add hl,de
        ld de,win_dx
        add iy,de
        dec a
    jr nz,loop_y; run while
    pop af; restore a for the outer_loop
    dec a
    ;pop iy
    pop hl ;get back address of start x
    ld de,#0800 ;offset to next line
    add hl,de ;jump to next line
    ;ld (hl),127; debug2
    ;add iy,de ; when copy on screen
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
;dest=#C030
dest=#6200
size = win_dx*win_dy*8
;-------------------------------------------
SAVE 'SAVEBLCK.BIN',#6000,$-#6000,DSK,'Frawe.dsk'
;SAVE 'IM1.BIN',dest,size,DSK,'Frawe.dsk'
; en BASIC: load"BLOCK1.BIN",&A000: CALL &A000

;  usage: ./rasm helloword.asm
