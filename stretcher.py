import sys
from time import sleep
from gevent import socket, Timeout


params = {"X":
              {"LEFT":1586321,
               "RIGHT":32190298},
          "Y":
              {"FRONT":1424258,
               "BACK":32098423},
          "Z":
              {"UP":-5640977,
               "DOWN":-1000,
               "COUNTperMM":200000}
               # "COUNTperMM":171265}
         }

def axisAddress(axis):
    """Return the address of requested axis."""
    if axis == "X": 
        address = ('192.168.1.151', 5001)
    elif axis == "Y": 
        address = ('192.168.1.153', 5001)
    elif axis == "Z": 
        address = ('192.168.1.49', 5001)
    else: 
        raise ValueError("Invalid axis {0}. Expecting X, Y, or Z.".format(axis))
    return address
# end def

def runRecipe(infile):
    file = open(infile,'r')
    for line in file.readlines():
        print line
        exec(line)
    file.close()
    return
# end def

def moveDipDraw(location, dwell_s, draw_speed, dip_speed=500):
    """
    This is the main function.

    Args:
        location (str): Position to move to, "A1" to "C4."
        dwell_s (float): Time to dwell in lowered position (s)
        draw_speed (float): Speed to retract Z axis in (mm/s).
        dip_speed (float): Speed to lower Z axis in (mm/s).

    I. Retract Z axis.
    II. Move to a "location".
    III. Lower Z axis at "dip speed."
    IV. Wait for "dwell_s" seconds.
    V. Retract Z axis at "draw_speed."
    """

    # I.
    retractZ()

    # II.
    moveToPosition(location, dip=False)

    # III.
    retractZ("DOWN", speed=dip_speed)

    # IV.
    dwell(dwell_s)

    # V.
    retractZ("UP", speed=draw_speed)


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
    if position == "UP" or position == "DOWN":
        count_location = params["Z"][position]
    else:
        raise ValueError("Invalid position {0}. Expected 'UP' or 'DOWN'".format(position))

    sp = int(speed*params["Z"]["COUNTperMM"])
    # print "SP = {0}".format(sp)

    messages = ["sp={0};".format(sp), "mo=1;", "pa={0};".format(count_location), "bg;"]

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, 0)

    for message in messages:
        sendCommand(message, address, sock)

    while isMotorMoving(address, sock) == True:
        dwell(.2)

    return
# end def

def moveToPosition(location, dip=True):
    """I. Retract Z axis
    II. Move XY axes to [123][ABC] location.
    III. Lower Z axis."""

    retractZ()


    axes = ["X", "Y"]
    count_location = locationInCounts(location)

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, 0)
    i = 0
    for axis in axes:
        address = axisAddress(axis)

        messages = ["mo=1;", "pa={0};".format(count_location[i]), "bg;"]
        print messages

        for message in messages:
            print sendCommand(message, address, sock)
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

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, 0)

    for message in messages:
        print sendCommand(message, address, sock)

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
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, 0)
        close_socket = True
    else:
        close_socket = False


    # Socket must already be open
    print message
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
    print '%s:%s: got %s' % (address + (data, ))

    if close_socket == True:
        sock.close()

    return data
# end def


def locationInCounts(location):
    # X location
    if location[1] == "1":
        x_pos = 31317211
    elif location[1] == "2":
        x_pos = 21293790
    elif location[1] == "3":
        x_pos = 11489822
    elif location[1] == "4":
        x_pos = 1670066
    else:
        raise ValueError("Invalid target location {0}. Expecting [A B C][1 2 3] e.g. 'A1', 'C3', etc.".format(location))

    # Y location
    if location[0] == "A":
        y_pos = 10884550
    elif location[0] == "B":
        y_pos = 15607662
    elif location[0] == "C":
        y_pos = 20341775
    else:
        raise ValueError("Invalid target location {0}. Expecting [A B C][1 2 3] e.g. 'A1', 'C3', etc.".format(location))
    print x_pos
    print y_pos

    return [x_pos, y_pos]
# end def

def unlock(axes):
    axes = axes.upper()
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, 0)
    for axis in axes:
        message = "mo=0;"
        address = axisAddress(axis)
        sendCommand(message, address, sock)
    sock.close()
    return
# end def

def lock(axes):
    axes = axes.upper()
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, 0)
    for axis in axes:
        message = "mo=1;"
        address = axisAddress(axis)
        sendCommand(message, address, sock)
    sock.close()
    return
# end def
