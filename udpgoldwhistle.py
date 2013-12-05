"""Go all the way to the left side in one command:
python .\udpgoldwhistle.py yy 'mo=1;' 'pa=1039000000;' 'bg;'
or right
python .\udpgoldwhistle.py yy 'mo=1;' 'pa=1075000000;' 'bg;'
"""

import sys
from gevent import socket, Timeout

if sys.argv[1] == 'xx':
    address = ('192.168.1.151', 5001)
elif sys.argv[1] == 'yy':
    address = ('192.168.1.153', 5001)
elif sys.argv[1] == 'zz':
    address = ('192.168.1.49', 5001)

# elif sys.argv[1] == 'xl':
#     address = ('192.168.1.150', 5001)
# elif sys.argv[1] == 'yl':
#     address = ('192.168.1.151', 5001)
# elif sys.argv[1] == 'xr':
#     address = ('192.168.1.152', 5001)
# elif sys.argv[1] == 'yr':
#     address = ('192.168.1.153', 5001)

# elif sys.argv[1] == 'z1':
#     address = ('192.168.1.160', 5001)
# elif sys.argv[1] == 'z2':
#     address = ('192.168.1.161', 5001)
# elif sys.argv[1] == 'z3':
#     address = ('192.168.1.162', 5001)
# elif sys.argv[1] == 'z4':
#     address = ('192.168.1.163', 5001)

else:
    print "Invalid axis"
    exit()

#message = ' '.join(sys.argv[2:])

## sock = socket.socket(type=socket.SOCK_DGRAM)
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, 0)
# allow OS to bind to a free port

for message in sys.argv[2:]:
    print message
    print 'Sending %s bytes to %s:%s' % ((len(message), ) + address)
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
sock.close()
    # while sock.send('mo;') == 'mo;1;':
    #     pass



#print 'Sending %s bytes to %s:%s' % ((len(message), ) + address)
#sock.send(message)
#data, address = sock.recvfrom(8192)
#print '%s:%s: got %r' % (address + (data, ))
