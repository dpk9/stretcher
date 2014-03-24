import sys
from time import sleep, strftime
from gevent import socket, Timeout


params = {"X":
              {"LEFT": 1521237,
               "RIGHT":32230112},
          "Y":
              {"FRONT":1424258,
               "BACK": 32098423},
          "Z":
              {"UP":   -5640977,
               "DOWN": -4000,
               "CLEARANCE":-3898883,
               "COUNTperMM":200000}
               # "COUNTperMM":171265}
         }

def locationInCounts(location):
    # X location
    if location[1] == "1":
        x_pos = 32230111
    elif location[1] == "2":
        x_pos = 22552672
    elif location[1] == "3":
        x_pos = 12766294
    elif location[1] == "4":
        x_pos = 2828094
    else:
        raise ValueError("Invalid target location {0}. Expecting [A B C][1 2 3 4] e.g. 'A1', 'C3', etc.".format(location))

    # Y location
    if location[0] == "A":
        y_pos = 10721281 #10884550
    elif location[0] == "B":
        y_pos = 15360943 #15607662
    elif location[0] == "C":
        y_pos = 20086789 #20341775
    else:
        raise ValueError("Invalid target location {0}. Expecting [A B C][1 2 3 4] e.g. 'A1', 'C3', etc.".format(location))
    # print x_pos
    # print y_pos

    return [x_pos, y_pos]
# end def


def axisAddress(axis):
    """Return the address of requested axis."""
    if axis == "X": 
        address = ('192.168.1.152', 5001)
    elif axis == "Y": 
        address = ('192.168.1.153', 5001)
    elif axis == "Z": 
        address = ('192.168.1.49', 5001)
    else: 
        raise ValueError("Invalid axis {0}. Expecting X, Y, or Z.".format(axis))
    return address
# end def

def openSocket():
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, 0)
    return sock
# end def

def runRecipe(infile):
    file = open(infile,'r')
    lines = file.readlines()

    # for line in lines:
    #     fnc = line.split('(')[0]
    #     print fnc
    #     if not __dict__:
    #         raise SyntaxError('stretcher.py has no attribute {0}.'.format(line))
    for line in lines:
        if line[0] != "#":
            print strftime('%H:%M:%S ') + line
        exec(line)
    file.close()
    return
# end def

def moveDipDraw(location, dwell_s, draw_speed, dip_speed=500, cycles=1):
    """
    This is the main function.

    Args:
        location (str): Position to move to, "A1" to "C4."
        dwell_s (float): Time to dwell in lowered position (s)
        draw_speed (float): Speed to retract Z axis in (mm/s).
        dip_speed (float): Speed to lower Z axis in (mm/s).

    I. Retract Z axis.
    II. Move to a "location".
    for # of cycles:
        III. Lower Z axis at "dip speed."
        IV. Wait for "dwell_s" seconds.
        V. Retract Z axis at "draw_speed."
    """
    cycles_left = cycles

    # I.
    retractZ("CLEARANCE")

    # II.
    moveToPosition(location, dip=False)

    while cycles_left > 0:
        print strftime('%H:%M:%S ') + "cycle {0} out of {1}.".format(cycles-cycles_left+1, cycles)

        # III.
        retractZ("DOWN", speed=dip_speed)

        # IV.
        dwell(dwell_s)

        # V.
        retractZ("CLEARANCE", speed=draw_speed)

        cycles_left -= 1


    return
# end def

def retractZ(position="UP", speed=500):
    """Retract or lower the Z axis.
    Halts other functions until axis has reached destination.

    position = "UP" or "DOWN"
    speed is in um/s. Regular speed = 500 mm/s
                      Stretch speed = 0.3 mm/s"""
    address = axisAddress("Z")

    position = position.upper()
    if position in ["UP", "DOWN", "CLEARANCE"]:
        count_location = params["Z"][position]
    else:
        raise ValueError("Invalid position {0}. Expected 'UP' 'DOWN' or 'CLEARANCE".format(position))

    sp = int(speed*params["Z"]["COUNTperMM"])
    # print "SP = {0}".format(sp)

    messages = ["sp={0};".format(sp), "mo=1;", "pa={0};".format(count_location), "bg;"]

    sock = openSocket()

    for message in messages:
        sendCommand(message, address, sock)

    while isMotorMoving(address, sock) == True:
        dwell(.2)

    return
# end def

def moveToPosition(location, dip=True):
    """I. Retract Z axis
    II. Move XY axes to [ABC][1234] location.
    III. Lower Z axis."""

    location = location.capitalize()

    retractZ("CLEARANCE")


    axes = ["X", "Y"]
    count_location = locationInCounts(location)

    sock = openSocket()
    i = 0
    for axis in axes:
        address = axisAddress(axis)

        messages = ["mo=1;", "pa={0};".format(count_location[i]), "bg;"]
        # print messages

        for message in messages:
            data = sendCommand(message, address, sock)
            # print data
            
        i += 1

    while isMotorMoving(axisAddress("X"), sock) == True:
        dwell(.2)
    while isMotorMoving(axisAddress("Y"), sock) == True:
        dwell(.2)

    sock.close()
    if dip == True:
        retractZ("DOWN")
    return
# end def

def moveToLoadPosition():
    retractZ()
    address = axisAddress("Y")
    load_pos = params["Y"]["BACK"]
    messages = ["mo=1;", "pa={0};".format(load_pos), "bg;"]

    sock = openSocket()

    for message in messages:
        data = sendCommand(message, address, sock)
        # print data

    while isMotorMoving(axisAddress("Y"), sock) == True:
        dwell(.2)

    sock.close()
    return
# end def

def dwell(dwell_s):
    sleep(dwell_s)
    return
# end_def

def isMotorMoving(address, sock):
    """Check motion status.
    If motor is moving, return True.
    If motor is stopped, return False."""
    data = sendCommand("ms;", address, sock)
    if data == "ms;0;":
        return False
    # elif data == "ms;1;":
    #     return False
    elif data == "ms;3;":
        raise IOError("Motor failed. Aborting.")
    else:
        return True

def sendCommand(message, address, sock=None):
    """Send a command to an axis."""
    if sock == None:
        sock = openSocket()
        close_socket = True
    else:
        close_socket = False


    # Socket must already be open
    # print message
    #sock.send(message)
    sock.sendto(message, address)
    # data, address = sock.recvfrom(8192)
    # print data
    # print '%s:%s: got %s' % (address + (data, ))
    
    messages = []
    msg_lim = 2
    semi_colon_lim = 2
    semi_col_count = 0
    msg_count = 0
    with Timeout(2, False): # timeout and abort after 2 seconds waiting
        while semi_col_count < semi_colon_lim and msg_count < msg_lim:
            data, address_rx = sock.recvfrom(8192)
            if not data:
                # print "data end reached"
                break
            messages.append(data)
            semi_col_count += data.count(';')
            msg_count += 1
    # print messages, semi_col_count, msg_count
    data = ''.join(messages)
    # print '%s:%s: got %s' % (address + (data, ))

    if close_socket == True:
        sock.close()

    return data
# end def


def unlock(axes):
    axes = axes.upper()
    sock = openSocket()
    for axis in axes:
        message = "mo=0;"
        address = axisAddress(axis)
        sendCommand(message, address, sock)
    sock.close()
    return
# end def

def lock(axes):
    axes = axes.upper()
    sock = openSocket()
    for axis in axes:
        message = "mo=1;"
        address = axisAddress(axis)
        sendCommand(message, address, sock)
    sock.close()
    return
# end def

def uvTimer(time_s):
    try:
        time_s = float(time_s)
    except:
        raise ValueError("time_s should be a number (float or int) in seconds. Received '{}'".format(time_s))
    uvSwitch(True)
    sleep(time_s)
    uvSwitch(False)
# end def

def uvSwitch(on=False):
    """
on (bool) = bool
    True closes circuit (UV light on)
    False opens circuit (UV light off)
    """
    if type(on) == bool:
        lightswitch = 1 if on == False else 0
        sock = openSocket()
        message = "ob[2]={};".format(lightswitch)
        print message
        address = axisAddress("X")
        print address
        sendCommand(message, address, sock)
        sock.close()
    else:
        raise ValueError("Invalid 'on' value recieved: {}. Should be 'True' (on) or 'False' (off)".format(on))
# end def

if __name__ == "__main__":
    import sys
    file = sys.argv[1]
    runRecipe(file)