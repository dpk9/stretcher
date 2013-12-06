import sys
from time import sleep
from gevent import socket, Timeout
    

def axisAddress(axis):
    """Return the address of requested axis."""
    if axis == "x_axis": 
        address = ('192.168.1.151', 5001)
    elif axis == "y_axis": 
        address = ('192.168.1.153', 5001)
    elif axis == "z_axis": 
        address = ('192.168.1.49', 5001)
    else: 
        raise ValueError("Invalid axis {0}. Expecting x_axis, y_axis, or z_axis.".format(axis))
    return address
# end def

def moveDipRetract(location, dip_speed, draw_speed, dwell_s):
    """Write this function."""
    return
# end def

def retractZ(speed, position="UP"):
    """Retract or lower the Z axis.
    Halts other functions until axis has reached destination."""
    address = axisAddress("z_axis")

    if position == "UP":
        count_location = -5283137
    elif position == "DOWN":
        count_location = -145195
    else:
        raise ValueError("Invalid position {0}. Expected 'UP' or 'DOWN'".format(position))

    messages = ["mo=1;", "pa={0};".format(count_location), "bg;"]

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, 0)

    for message in messages:
        sendCommand(message, address, sock)

    while isMotorMoving(address, sock) == True:
        sleep(.2)

    return
# end def

def moveToLocation(location):
    """I. Retract Z axis
    II. Move XY axes to [123][ABC] location.
    III. Lower Z axis."""

    retractZ(1)


    axes = ["x_axis", "y_axis"]
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

    while isMotorMoving(axisAddress("x_axis"), sock) == True:
        sleep(.2)
    while isMotorMoving(axisAddress("y_axis"), sock) == True:
        sleep(.2)

    sock.close()

    retractZ(1, "DOWN")
    return
# end def

def isMotorMoving(address, sock):
    """Check motion status.
    If motor is moving, return True.
    If motor is stopped, return False."""
    data = sendCommand("ms;", address, sock)
    if data == "ms;0;":
        return False
    elif data == "ms;1;":
        return False
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
    if location[1] == "A":
        x_pos = 31799275
    elif location[1] == "B":
        x_pos = 20307120
    elif location[1] == "C":
        x_pos = 11748197
    else:
        raise ValueError("Invalid target location {0}. Expecting [1 2 3][A B C] e.g. '1A', '3C', etc.".format(location))

    # Y location
    if location[0] == "1":
        y_pos = 10281472
    elif location[0] == "2":
        y_pos = 15849824
    elif location[0] == "3":
        y_pos = 21500258
    else:
        raise ValueError("Invalid target location {0}. Expecting [1 2 3][A B C] e.g. '1A', '3C', etc.".format(location))
    print x_pos
    print y_pos

    return [x_pos, y_pos]
# end def