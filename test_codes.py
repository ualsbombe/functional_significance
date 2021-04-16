#%% test
import serial
from psychopy.clock import getTime

port_address = '/dev/ttyUSB0'

port = serial.Serial(port=port_address, baudrate=38400, timeout=1.0)
pulse = b'?*A,S$C0#'
intensity_1 = b'?I,10$D6#'
intensity_2 = b'?I,20$D7#'
intensity_3 = b'?I,30$D8#'


port.write(intensity_1)

begin_time = getTime()
port.write(intensity_2)
port.write(pulse)
end_time = getTime() - begin_time
print('Without "port.readline')
print(str(end_time) + ' s\n')



port.write(intensity_3)
port.close()


port = serial.Serial(port=port_address, baudrate=38400, timeout=1.0)
pulse = b'?*A,S$C0#'

begin_time = getTime()
port.write(pulse)
port.readline()
print('With "port.readline" and timeout of 1.0 s')
end_time = getTime() - begin_time
print(str(end_time) + ' s\n')
port.close()

port = serial.Serial(port=port_address, baudrate=38400, timeout=0.1)
pulse = b'?*A,S$C0#'

begin_time = getTime()
port.write(pulse)
port.readline()
end_time = getTime() - begin_time
print('With "port.readline" and timeout of 0.1 s')
print(str(end_time) + ' s\n')
port.close()

port = serial.Serial(port=port_address, baudrate=38400, timeout=0.0001)
pulse = b'?*A,S$C0#'

begin_time = getTime()
port.write(pulse)
port.readline()
end_time = getTime() - begin_time
print('With "port.readline" and timeout of 0.0001 s')
print(str(end_time) + ' s\n')
port.close()

