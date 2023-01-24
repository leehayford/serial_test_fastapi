from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse

import serial
import threading
import asyncio


app = FastAPI()

class ToolID:
    def __init__( self, id, sub, mcnt, mtyp, mcap, fwy, fww ):
        self.ID = id
        self.SubID = sub
        self.MemCount = mcnt
        self.MemType = mtyp
        self.MemCpacity = mcap
        self.FWYear = fwy
        self.FWWeek = fww

toolID = ToolID( 0,0,0,0,0,0,0)
toolIDBytes = [ 0, 0, 0, 0, 0, 0, 0 ] 

ser = serial.Serial( )
# ser.port = "/dev/ttyUSB0"
ser.port = "COM3"
ser.baudrate = 230400
ser.bytesize = serial.EIGHTBITS #number of bits per bytes
ser.parity = serial.PARITY_NONE #set parity check: no parity
ser.stopbits = serial.STOPBITS_ONE #number of stop bits
try: 
    ser.open( )
except Exception as e:
    print( "Error opening serial port: " + str( e ) )
    exit( )

def serial_read( ser ):
    global toolID
    while ser.isOpen( ):
        while True:
            data = list( ser.read( 15 ) )
            toolIDBytes = data
            toolID.ID = data[ 7:8 ][ 0 ]
            toolID.SubID = data[ 12:13 ][ 0 ]
            toolID.MemCount = data[ 8:9 ][ 0 ]
            toolID.MemType = data[ 9:10 ][ 0 ]
            toolID.MemCapacity = data[ 13:14 ][ 0 ]
            toolID.FWYear = data[ 10:11 ][ 0 ]
            toolID.FWWeek = data[ 11:12 ][ 0 ]
            print( toolID.__dict__ )

thread = threading.Thread( target=serial_read, args=( ser, ) )
thread.start( )

@app.get("/tool-id")
async def get_tool_id( ):
    global toolID
    if ser.isOpen():

        # ser.flushInput()    #flush input buffer, discarding all its contents
        # ser.flushOutput()   #flush output buffer, aborting current output 
        #                             #and discard all that is in buffer

        #write data
        cmd = bytes.fromhex('aaaaaa55400001eefa')
        # print( cmd )
        ser.write( cmd )
        # print("Serial Write: [ 0xAA, 0xAA, 0xAA, 0x55, 0x40, 0x00, 0x01, 0xEE, 0xFA ]")

        while toolID.ID == 0:
            await asyncio.sleep( 0.1 )
        
    else:
        print( "serial port is not open..." )
    
    return toolID



app.mount("", StaticFiles(directory="web/public", html=True), name="web")
app.mount("/build", StaticFiles(directory="web/public/build"), name="web")

@app.get("/")
async def web(): return RedirectResponse(url="web")