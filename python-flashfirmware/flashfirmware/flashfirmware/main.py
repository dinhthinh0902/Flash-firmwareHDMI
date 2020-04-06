#!/usr/bin/python
import smbus
import time
import sys
import math

m_uChipId = 0x1704
a = int(sys.argv[1])
bus = smbus.SMBus(a)
binfile = str(sys.argv[3])

if sys.argv[2].startswith("0x"):
    addr = int(sys.argv[2][2:], 16)
def CheckChipId():

    bus.write_byte_data(addr, 0xFF, 0x80) #switch to register bank 0x80
    bus.write_byte_data(addr, 0xEE, 0x01)  #enable I2C access
    bus.write_byte_data(addr, 0xFF, 0x81)

    time.sleep(1)
    b = bus.read_byte_data(addr, 0x00)
    c = bus.read_byte_data(addr, 0x01)
    nChipID = (b << 8) | c

    print ("Chip ID in i2c bus "+str(a) +" address "+ sys.argv[2] + " = ", hex(nChipID), "\n")
    return nChipID

def Config():
    bus.write_byte_data(addr, 0xFF, 0x80)
    bus.write_byte_data(addr, 0xEE, 0x01)
    bus.write_byte_data(addr, 0x5A, 0x80)
    bus.write_byte_data(addr, 0x5E, 0xC0 | 0x1F)
    bus.write_byte_data(addr, 0x58, 0x01)
    bus.write_byte_data(addr, 0x59, 0x51)
    bus.write_byte_data(addr, 0x5A, 0x90)
    bus.write_byte_data(addr, 0x5A, 0x80)
    bus.write_byte_data(addr, 0x58, 0x21)

def BlockErase():
    lEraseAddr = 0
    bus.write_byte_data(addr, 0xFF, 0x80)
    bus.write_byte_data(addr, 0xEE, 0x01)
    bus.write_byte_data(addr, 0x5A, 0x80)
    bus.write_byte_data(addr, 0x5A, 0x84)
    bus.write_byte_data(addr, 0x5A, 0x80)
    addra = [0, 0, 0]
    addra[0] = (lEraseAddr & 0xFF0000) >> 16
    addra[1] = (lEraseAddr & 0xFF00) >> 8
    addra[2] = lEraseAddr & 0xFF
    bus.write_byte_data(addr, 0x5B, addra[0])
    bus.write_byte_data(addr, 0x5C, addra[1])
    bus.write_byte_data(addr, 0x5D, addra[2])
    bus.write_byte_data(addr, 0x5A, 0x81)
    bus.write_byte_data(addr, 0x5A, 0x80)
    time.sleep(1)

def ResetFifo():
    bus.write_byte_data(addr, 0xFF, 0x81)
    bRead=bus.read_byte_data(addr, 0x08)
    bRead &= 0xbF
    bus.write_byte_data(addr, 0x08, bRead)
    bRead |= 0x40
    bus.write_byte_data(addr, 0x08, bRead)
    bus.write_byte_data(addr, 0xFF, 0x80)

def Prog(bytes_data):
    ulDataLen = len(bytes_data)
    
    m_ulBlock = 256
    lWriteAddr = 0
    addrb = [0, 0, 0]
    addrb[0] = (lWriteAddr & 0xFF0000) >> 16
    addrb[1] = (lWriteAddr & 0xFF00) >> 8
    addrb[2] = lWriteAddr & 0xFF

    nStartBlock= lWriteAddr / m_ulBlock
    if ulDataLen % m_ulBlock != 0:
        nBlocks = (ulDataLen / m_ulBlock + 1)
    else:
        nBlocks = ulDataLen / m_ulBlock
    lStartAddr = lWriteAddr
    lEndAddr = lWriteAddr
    nSpiDataLen = 32

    bus.write_byte_data(addr, 0xFF, 0x80)
    bus.write_byte_data(addr, 0xEE, 0x01)
    bus.write_byte_data(addr, 0x5A, 0x84)
    bus.write_byte_data(addr, 0x5A, 0x80)

    for i in range(0, nBlocks):
        if (i + nStartBlock + 1) * m_ulBlock > (lWriteAddr + ulDataLen):
            lEndAddr = lWriteAddr + ulDataLen
        else:
            lEndAddr = (i + nStartBlock + 1) * m_ulBlock

        if (lEndAddr - lStartAddr) % nSpiDataLen != 0:
            nPages = (lEndAddr -lStartAddr) / nSpiDataLen + 1
        else:
            nPages = ((lEndAddr - lStartAddr) / nSpiDataLen)

        for j in range(0, nPages):
            bus.write_byte_data(addr, 0x5A, 0x84)
            bus.write_byte_data(addr, 0x5A, 0x80)
            #Set bySpiLen = 31 , write 32bytes one time ;
            bySpiLen = 31
            bus.write_byte_data(addr, 0x5E, 0xC0 | bySpiLen)
            bus.write_byte_data(addr, 0x5A, 0xA0)
            bus.write_byte_data(addr, 0x5A, 0x80)
            bus.write_byte_data(addr, 0x58, 0x21)

            if (lEndAddr - lStartAddr) / nSpiDataLen == 0:
                nCurSpiDataLen = (lEndAddr - lStartAddr) % nSpiDataLen
            else:
                nCurSpiDataLen = nSpiDataLen

            byWriteData = [0]* (bySpiLen + 1)
            for k in range(0,nCurSpiDataLen):
                byWriteData[k] = int(bytes_data[lStartAddr - lWriteAddr + k])

            bus.write_i2c_block_data(addr, 0x59,byWriteData)
            bus.write_byte_data(addr, 0x5B, addrb[0])
            bus.write_byte_data(addr, 0x5C, addrb[1])
            bus.write_byte_data(addr, 0x5D, addrb[2])
            bus.write_byte_data(addr, 0x5E, 0xC0)
            bus.write_byte_data(addr, 0x5A, 0x90)
            bus.write_byte_data(addr, 0x5A, 0x80)

            lStartAddr += (bySpiLen + 1)
            addrb[0] = (lStartAddr & 0xFF0000) >> 16
            addrb[1] = (lStartAddr & 0xFF00) >> 8
            addrb[2] = lStartAddr & 0xFF

        lStartAddr = (i + nStartBlock + 1) * m_ulBlock
        addrb[0] = (lStartAddr & 0xFF0000) >> 16
        addrb[1] = (lStartAddr & 0xFF00) >> 8
        addrb[2] = lStartAddr & 0xFF

    byWriteData = []
    bus.write_byte_data(addr, 0x5A, 0x88)
    bus.write_byte_data(addr, 0x5A, 0x80)

def Read(lReadLen, byReadData):
    lReadAddr = 0
    addrc = [0, 0, 0]
    addrc[0] = (lReadAddr & 0xFF0000) >> 16
    addrc[1] = (lReadAddr & 0xFF00) >> 8
    addrc[2] = lReadAddr & 0xFF
    nPage = int(math.ceil(lReadLen / 32.))

    if (lReadLen % 32 != 0):
        ++nPage
    
    bus.write_byte_data(addr, 0xFF, 0x80)
    bus.write_byte_data(addr, 0xEE, 0x01)
    bus.write_byte_data(addr, 0x5A, 0x84)
    bus.write_byte_data(addr, 0x5A, 0x80)

    byCurReadData = [0]*32
    
    for i in range(0, nPage):
        bus.write_byte_data(addr, 0x5E, 0x40 | 0x1F)
        bus.write_byte_data(addr, 0x5A, 0xA0)
        bus.write_byte_data(addr, 0x5A, 0x80)
        bus.write_byte_data(addr, 0x5B, addrc[0])
        bus.write_byte_data(addr, 0x5C, addrc[1])
        bus.write_byte_data(addr, 0x5D, addrc[2])
        bus.write_byte_data(addr, 0x5A, 0x90)
        bus.write_byte_data(addr, 0x5A, 0x80)
        bus.write_byte_data(addr, 0x58, 0x21)
       
        if (lReadLen - i * 32) < 32:
            nCurReadLen = lReadLen - i * 32
        else:
            nCurReadLen = 32
    
        byCurReadData = bus.read_i2c_block_data(addr,0x5F,nCurReadLen)
        for j in range(0, nCurReadLen):
            byReadData[i * 32 + j] = byCurReadData[j]
        
        lReadAddr += nCurReadLen
        addrc[0] = (lReadAddr & 0xFF0000) >> 16
        addrc[1] = (lReadAddr & 0xFF00) >> 8
        addrc[2] = lReadAddr & 0xFF

    byCurReadData = []

def main():
    a=CheckChipId()
    print(m_uChipId)
    if a == m_uChipId:
        print("Start config")
        Config()
        print("Start Block Erase")
        BlockErase()
        print("Start reset fifo")
        ResetFifo()
        print("Start progress")
        f = open(binfile, "rb")
        file_data = bytearray()
        try:
            byte = f.read(1)
            while byte != "":
                # Do stuff with byte.
                file_data.append(byte)
                byte = f.read(1)
        fina	lly:
            f.close()
        byProgData = id(file_data)

        ulDataLen = len(file_data)
    
        Prog(file_data)
        print("Start reset fifo")
        ResetFifo()
        byReadData = bytearray(ulDataLen)
        print("Start read")
        Read(ulDataLen, byReadData)

        if bytes(file_data) == bytes(byReadData):
            print ("Flash success")
        else:
            print ("Flash failed", 'debugging...')
            print (len(file_data), len(byReadData))
            for i in range(ulDataLen):
                if file_data[i] != byReadData[i]:
                    print('i=', i, 'file=', file_data[i], 'read=', byReadData[i])
            
        byReadData = []

if __name__== "__main__":
    main()

