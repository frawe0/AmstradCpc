############################################################################################
#   IMPORT
############################################################################################
import sys,os,glob
import random
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap
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

def f_readbin1(path_in,path_out,width=21,off=0):
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
    print(data0[0:4])

    # Remove header
    data=data0[128+off:-112]

    # Image dimensions
    n = data.shape[0]
    sx = 2*width # mode 1: 2 Bytes for a 8 pixels line
    sy = round(n/sx/8)

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
    #a,b = 44,20
    #plt.matshow(data[0:a*b].reshape((a,b)))
    #plt.show()
    #sys.exit()

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
    #data0[128:128+nd] = R
    if 1==1:
        height = sy
        x1,y1 = 3,7
        dataL = [x1,0,y1,0,2*width,0,height,0] # each variable on 2 bytes
        for n,d in enumerate(dataL):
            data0[128+n] = d
        n+=1
        data0[128+n:128++n+nd] = R

    data0.tofile(path_out)

def f_readbin2(path_in,path_out,width=21,off=0,flag_show=True):
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

    ############
    # Image Prep
    #############
    # Read the binary file block and reshape to array: 21x13*8
    data0 = np.fromfile(path_in, dtype=np.uint8)

    # Remove header
    off,off2 = 0,-17
    data=data0[128+off:-112+off2]

    # Image dimensions
    n = data.shape[0]
    sx = int(2*width) # mode 1: 2 Bytes for a 8 pixels line
    sy = n//sx
    off +=round(n-sx*sy)
    print(n,sx*sy,sx,sy,off,n/width)
    data = data0[128+off:-112+off2]

    # Reshape data
    print(f"Ver2: {data.shape} pixels -> Mode1: 2*W{width} x 8*H{sy // 8} : {sx * sy}")
    M = data.reshape((sy, sx))
    print(M.shape)

    # Get dual array: remapping depending on block output type
    M2 = M*0
    for j in range(8):
        for i in range(sy//8):
            n = i+(sy//8)*j # increment
            k = 8 * i + j # 8
            M2[n,:]= M[k,:]
            #print(i,j,k,n)
    #M=M2
    #plt.matshow(M)
    #plt.show()

    # Transform image format: step #50,#800 to #800,#50
    # Option1 for bin block: saving first line of blocs and then 2nd line
    # Option2 for bin block: saving first 1st characters  and then next characters

    ######################
    # Save to binary file
    ######################
    # Header
    height = sy
    x1,y1 = 3,7
    dataL = [x1,0,y1,0,2*width,0,height,0] # each variable on 2 bytes
    for n,d in enumerate(dataL): #header containing the image location and dimension
        data0[128+n] = d
    n+=1
    # Image data
    data0[128+n:128+n+sx*sy] = M.flatten().astype(np.uint8)
    # Output
    print(path_out)
    data0.tofile(path_out)

    ################
    # Showing image
    ################
    # In mode 1, needs to combine 2 bits for 1 pixel (4 colors)
    if flag_show==True:
        B = np.unpackbits(M, axis=1)
        F = np.zeros((sy,sx*4),dtype=np.uint8) #Mode1: 4 pixel per byte
        for i in range(0,sx*4,4):
            for k in range(4*0+4):
                F[:,i+k] = 2*B[:,i*2+k]+1*B[:,i*2+4+k] # color given by 2 bits
        plt.matshow(F,cmap='viridis')
        plt.show()

def f_readbin3(path_in,path_out,width=21,off=0,flag_show=True):
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

    ############
    # Image Prep
    #############
    # Read the binary file block and reshape to array: 21x13*8
    data0 = np.fromfile(path_in, dtype=np.uint8)
    w,h = data0[128].astype(np.uint16),data0[129].astype(np.uint16)
    print("WxH",w,h,w*h)

    # Remove header
    off =0
    #h=10
    data = data0[130+off:130+off+w*h]
    #data = np.roll(data,2,axis=0)
    #data[1:3]=1+2+4+8
    # Image dimensions
    n = data.shape[0]
    if width<0:
        width = data0[128]/2
    sx = int(2*width) # mode 1: 2 Bytes for a 8 pixels line
    sy = n//sx
    off +=round(n-sx*sy)
    print(n,sx*sy,sx,sy,off,n/width)
    # Reshape data
    print(f"{data.shape} pixels -> Mode1: W{sx} x H{sy} : {sx * sy} Off:{off}")
    M = data.reshape((sy, sx))
    print(M.shape)
    #return

    # Get dual array: remapping depending on block output type
    M2 = M*0
    for j in range(8):
        for i in range(sy//8):
            n = i+(sy//8)*j # increment
            k = 8 * i + j # 8
            M2[n,:]= M[k,:]
            #print(i,j,k,n)
    #M=M2
    #plt.matshow(M)
    #plt.show()

    # Transform image format: step #50,#800 to #800,#50
    # Option1 for bin block: saving first line of blocs and then 2nd line
    # Option2 for bin block: saving first 1st characters  and then next characters
    '''
    ######################
    # Save to binary file
    ######################
    # Header
    dataf =data0.copy()
    height = sy
    x1,y1 = 3,7
    dataL = [x1,0,y1,0,2*width,0,height,0] # each variable on 2 bytes
    for n,d in enumerate(dataL): #header containing the image location and dimension
        dataf[128+n] = d
    n+=1
    # Image data
    dataf[128+n:128+n+sx*sy] = M.flatten().astype(np.uint8)
    # Output
    print(path_out)
    dataf.tofile(path_out)
    '''
    ################
    # Showing image
    ################
    # In mode 1, needs to combine 2 bits for 1 pixel (4 colors)
    if flag_show==True:

        colL=['#000000','#FF4422','#FFFFFF','#3333DD']
        cmap = ListedColormap(colL)

        B = np.unpackbits(M, axis=1)
        #B = np.roll(B,2,axis=0)
        F = np.zeros((sy,sx*4),dtype=np.uint8) #Mode1: 4 pixel per byte
        for i in range(0,sx*4,4):
            for k in range(4):
                F[:,i+k] = 2*B[:,i*2+k]+1*B[:,i*2+4+k] # color given by 2 bits
        #F = np.roll(F,-1,axis=1)
        plt.matshow(F,cmap=cmap)
        plt.show()

    return 1






############################################################################################
#   MAIN
############################################################################################
def main():
    '''Plot '''

    # Init paths
    path1 ="/Volumes/Data_FW/5-Jeux/5.7-Amstrad/asm/MM/Bin/Face2/"
    path2 = path1.replace("Face","FaceConv")
    os.makedirs(path2, exist_ok=True)

    # Loop
    imageL = glob.glob(path1+'/*.BIN')
    fileLL = [["Garde.bin",-1,0]]
    #fileLL = [["Disk.bin", -1, 0]]
    fileLL = [["Tete.2", -1, 0]]
    fileLL = [["Corps.2", -1, 0]]
    #fileLL = [["Epee.bin", -1, 0]]
    #fileLL = [["Aubdra1.bin", 21, 0]]
    #fileLL = [["Ombre.bin", -21, 0]]
    #fileLL = [["Chateau.mud", 7.5, 0]]
    #fileLL = [["Auberge.bin", 21,0]]
    #fileLL = [[os.path.basename(ima),21,0] for ima in imageL]
    #path_in,width = path1+"AUBDRA.bin",21
    for ima_in,width,off in fileLL:
        print(f"Process {ima_in}")
        path_in = path1+ima_in
        path_out = path_in.replace("Face","FaceConv")
        if width>0:
            f_readbin2(path_in, path_out, width=width,off=off)
        else:
            f_readbin3(path_in, path_out, width=width, off=off)
    #f_readbin(path_in, path_out, width=width)


    #path_in, width = path + "DRAGON.CHA",15
    #path_in = path + "EPEE.bin"  # 9
    #path_out = path_in.replace("Face","FaceConv")

    # Create the folder
    #os.makedirs(os.path.dirname(path_out), exist_ok=True)
    #f_readbin(path_in,path_out,width=width)

############################################################################################
############################################################################################
if __name__ == '__main__':
    main()
