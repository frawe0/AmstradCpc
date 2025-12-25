############################################################################################
#   IMPORT
############################################################################################
import os
import random
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd

import math

############################################################################################
#   PROC
############################################################################################
def f_pix(oct):
    # decompose pixel colors for an octet
    bits = np.unpackbits([oct])
    print(oct,bits)
    return 1

def f_readbin(path_in,path_out,width=21):
    ''' read cpc binary_file
    Purpose: The header tells the CPC’s AMSDOS (disk/tape operating system) what kind of file it is, where to load it in memory, how long it is, and whether it should auto‑execute.
    Size: The header is 128 bytes at the start of the file.
    Contents include:
    Filename (up to 8 characters + 3‑char extension)
    File type (binary, ASCII, BASIC, etc.)
    Load address (where in RAM the file should be loaded)
    Length (number of bytes of data)
    Execution address (where to jump if it’s a program)
    Checksum (for integrity)
    '''

    # Read the binary file: 21x13*8
    data0 = np.fromfile(path_in, dtype=np.uint8)

    # Remove header
    data=data0[128:-112]

    # Image dimensions
    n = data.shape[0]
    sx = 2*width # mode 1: 2 Bytes for a 8 pixels line
    sy = n//sx//8

    # Reshape to 16x16
    print(n,n/16)
    print(f"{data.shape} pixels -> Mode1: 2*{width} x 8*{sy} : {2*width*8*sy}")
    M = data.reshape((sy,sx*8))
    N = np.zeros((sy*8,sx),dtype=np.uint8)
    print("M:",M.shape,"N:",N.shape)

    # rearrange array to de-interlace
    for j in range(sy):
        for i in range(8):
            #print(sy,0,sx,sx*i,sx*(i+1))
            N[j*8+i,0:sx]=M[j,sx*i:sx*(i+1)]
            #print(i,j,j*8+i)

    # Unpack bits
    B = np.unpackbits(N,axis=1)

    # Combine bits for M1
    F = np.zeros((sy*8,sx*4),dtype=np.uint8)
    for i in range(0,sx*4,4):
        for k in range(4):
            F[:,i+k] = 2*B[:,i*2+k]+1*B[:,i*2+4+k] # color given by 2 bits

    #colorL = ['#000000',]
    plt.matshow(F,cmap='viridis')
    plt.show()

    # Transform to other format
    D = data[:]
    nd = D.shape[0]
    R = np.zeros((nd),dtype=np.uint8)
    z=0
    for k in range(8):
        for j in range(sy):
            y = 8*j+k
            R[z:z+sx]= N[y,:]
            z+= sx

    # Save to binary file
    print(path_out)
    data0[128:128+nd]=R
    data0.tofile(path_out)

############################################################################################
#   MAIN
############################################################################################
def main():
    '''Plot '''

    path ="/Volumes/Data_FW/5-Jeux/5.7-Amstrad/asm/MM/All/Face4/"
    #path_in = path+"AUBDRA"+".bin"
    path_in = path + "DRAGON" + ".CHA" #9
    #path_in = path + "EPEE.bin"  # 9

    path_out = path_in.replace("Face","FaceConv")

    # Create the folder
    os.makedirs(os.path.dirname(path_out), exist_ok=True)
    #f_readbin(path_in,path_out,width=21)
    f_readbin(path_in, path_out, width=15)

############################################################################################
############################################################################################
if __name__ == '__main__':
    main()
