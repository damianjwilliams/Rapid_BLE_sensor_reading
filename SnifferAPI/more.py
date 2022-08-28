# Copyright (c) Nordic Semiconductor ASA
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without modification,
# are permitted provided that the following conditions are met:
#
# 1. Redistributions of source code must retain the above copyright notice, this
#    list of conditions and the following disclaimer.
#
# 2. Redistributions in binary form, except as embedded into a Nordic
#    Semiconductor ASA integrated circuit in a product or a software update for
#    such product, must reproduce the above copyright notice, this list of
#    conditions and the following disclaimer in the documentation and/or other
#    materials provided with the distribution.
#
# 3. Neither the name of Nordic Semiconductor ASA nor the names of its
#    contributors may be used to endorse or promote products derived from this
#    software without specific prior written permission.
#
# 4. This software, with or without modification, must only be used with a
#    Nordic Semiconductor ASA integrated circuit.
#
# 5. Any software provided in binary form under this license must not be reverse
#    engineered, decompiled, modified and/or disassembled.
#
# THIS SOFTWARE IS PROVIDED BY NORDIC SEMICONDUCTOR ASA "AS IS" AND ANY EXPRESS
# OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES
# OF MERCHANTABILITY, NONINFRINGEMENT, AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL NORDIC SEMICONDUCTOR ASA OR CONTRIBUTORS BE
# LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
# CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE
# GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION)
# HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT
# LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT
# OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

import collections
import logging
import serial
from threading import Thread, Event

import serial.tools.list_ports as list_ports

from SnifferAPI import Exceptions
from SnifferAPI import Packet
#from . import Filelock

import os
if os.name == "posix":
    import termios

SNIFFER_OLD_DEFAULT_BAUDRATE = 460800
# Baudrates that should be tried (add more if required)
SNIFFER_BAUDRATES = [1000000, 460800]


def find_sniffer(write_data=False):
    open_ports = list_ports.comports()
    print(open_ports)

    sniffers = []
    for port in [x.device for x in open_ports]:
        print()
        for rate in SNIFFER_BAUDRATES:
            reader = None
            l_errors = [serial.SerialException, ValueError, Exceptions.LockedException]
            if os.name == 'posix':
                l_errors.append(termios.error)
            try:
                reader = Packet.PacketReader(portnum=port, baudrate=rate)
                try:
                    if write_data:
                        reader.sendPingReq()
                        _ = reader.decodeFromSLIP(0.1, complete_timeout=0.1)
                    else:
                        _ = reader.decodeFromSLIP(0.3, complete_timeout=0.3)

                    # FIXME: Should add the baud rate here, but that will be a breaking change
                    sniffers.append(port)
                    break
                except (Exceptions.SnifferTimeout, Exceptions.UARTPacketError):
                    pass
            except tuple(l_errors):
                continue
            finally:
                if reader is not None:
                    reader.doExit()
    return sniffers

find_sniffer(write_data=False)