# -*- coding: utf-8 -*-
"""
Created on Fri Apr  4 17:54:58 2025

@author: Gene Felix
"""

import usb.core
import usb.util
import libusb_package
import sys

#%%

def conv_len(a, l):
    # Credit to DLPC3500 package
    """
    Function that converts a number into a bit string of given length.

    :param int a: Number to convert.
    :param int l: Length of bit string.

    :return: Padded bit string.
    """
    b = bin(a)[2:]
    padding = l - len(b)
    b = '0' * padding + b
    return b

#%%

def bits_to_bytes(a, reverse=True):
    # Credit to DLPC3500 package
    """
    Function that converts bit string into a given number of bytes.

    :param str a: Bytes to convert.
    :param bool reverse: Whether or not to reverse the byte list.

    :return: List of bytes.
    """
    bytelist = []

    # check if needs padding
    if len(a) % 8 != 0:
        padding = 8 - len(a) % 8
        a = '0' * padding + a

    # convert to bytes
    for i in range(len(a) // 8):
        bytelist.append(int(a[8 * i:8 * (i + 1)], 2))

    if reverse:
        bytelist.reverse()
    return bytelist

#%%

def write(device, cmd2, cmd3, data):
    try:
        # USB Write Transaction Sequence [2]
        flags = 0x00  # Bit 7 is 0 for write, Bit 6 is 0 as we don't typically need a reply for a write
        sequence = 0x00
        
        buffer = []

        data_len = conv_len(len(data) + 2, 16)
        data_len = bits_to_bytes(data_len)

        buffer.append(flags)
        buffer.append(sequence)
        buffer.extend(data_len)
        buffer.append(cmd3)
        buffer.append(cmd2)
        
        for i in range(len(data)):
            buffer.append(data[i])

            # append empty data to fill buffer
        for i in range(64 - len(buffer)):
            buffer.append(0x00)

        device.write(1, buffer)

    except usb.core.USBError as e:
        print(f"Error setting green LED: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        
#%%

def enable_only_green(dev):
    # Enable only green pin
    cmd2 = 0x1A
    cmd3 = 0x07
    data = [0b00000010]

    write(dev, cmd2, cmd3, data)
    
def enable_all_leds(dev):
    # Enable only green pin
    cmd2 = 0x1A
    cmd3 = 0x07
    data = [0b00001000]

    write(dev, cmd2, cmd3, data)
    
def set_current(dev, red, green, blue):
    # Setting current
    cmd2 = 0x0B  # LED Driver Current Control [3]
    cmd3 = 0x01  # LED Driver Current Control [3]
    data = [255 - red, 255 - green, 255 - blue]
    
    write(dev, cmd2, cmd3, data)

#%%
# Show all VID and PID

# # Find all connected USB devices
dev = libusb_package.find(find_all=True)

for device in dev:
    print(f"  Vendor ID: {hex(device.idVendor)}")
    print(f"  Product ID: {hex(device.idProduct)}")
    print(2*'\n')
    
#%%
VID = 0x0451
PID = 0x6401

dev = usb.core.find(idVendor=VID, idProduct=PID)

if dev is None:
    raise ValueError(f"Device with VID 0x{VID:04X} and PID 0x{PID:04X} not found")
    
#%% 

enable_only_green(dev)

set_current(dev, 0, 240, 0)

#%%
        
enable_all_leds(dev)

set_current(dev, 0, 0, 0)
    
#%%
dev.reset()
del dev