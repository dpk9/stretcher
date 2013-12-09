"""Go all the way to the left side in one command:
python .\udpgoldwhistle.py y 'mo=1;' 'pa=1039000000;' 'bg;'
or right
python .\udpgoldwhistle.py y 'mo=1;' 'pa=1075000000;' 'bg;'
"""

import sys
from gevent import socket, Timeout

if sys.argv[1] == 'x':
    address = ('192.168.1.151', 5001)
elif sys.argv[1] == 'y':
    address = ('192.168.1.153', 5001)
elif sys.argv[1] == 'z':
    address = ('192.168.1.49', 5001)
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
