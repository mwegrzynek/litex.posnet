# -*- coding: UTF-8 -*-
from datetime import datetime

from functools import partial
from binascii import hexlify
from construct import Struct, Byte, Bytes, Const, String, CString, \
    Switch, Pointer, Anchor, Sequence, GreedyRange, Computed, this, \
    RawCopy, Checksum, Probe, Container

from PyCRC.CRCCCITT import CRCCCITT

TIME_FORMAT = '%Y-%m-%d;%H:%M'

crc16 = lambda val: '{:04x}'.format(CRCCCITT().calculate(val)).upper()

TabTerminated = CString(terminators=b'\x09')

PosnetParameter = Struct(
    'name' / String(length=2),
    'value' / TabTerminated
)

PosnetToken = Struct(
    'name' / Const('@'),
    'value' / String(length=4)
)

PosnetErrorCode = Struct(
    'name' / Const('?'),
    'value' / TabTerminated
)

PosnetFrame = Struct(
     Const(b'\x02'),
     'summed' / RawCopy(
         Struct(
             'instruction' / TabTerminated,
             'parameters' /
                Switch(this.instruction, dict(
                     ERR=Sequence(PosnetErrorCode)
                ),
                default=GreedyRange(PosnetParameter)
              ),
         )
      ),
      Const('#'),
      'crc' / Checksum(Bytes(4), crc16, 'summed'),
      Const('\x03'),
      'instruction' / Computed(this.summed.value.instruction),
      'parameters' / Computed(this.summed.value.parameters)
)

def build_frame(instruction, *params):
    '''
    Helper for building Posnet protocol frames out of instructions and
    params passed as (name, value) tuples. Can't use **kwargs: Posnet protocol
    uses reserved chars (such as @ and ?)
    '''
    data = Container(
        summed=Container(
            value=Container(
                instruction=instruction,
                parameters=[Container(name=name, value=value) for name, value in params]
            )
        )
    )

    return PosnetFrame.build(data)

def parse_frame(frame):
    '''
    Reverse of build frame -- for parsing printr responses
    '''
    result = PosnetFrame.parse(frame)
    return Container(
        instruction=result.instruction,
        parameters=[(param.name, param.value) for param in result.parameters]
    )


class PosnetProtocol(object):
    '''
    Protocol class for a Posnet Printer.
    '''

    def __init__(self, conn):
        '''
        conn - object with read and write methods for communicationg with printer
        '''
        self.conn = conn

    def write(self, data):
        return self.conn.write(data)

    def read_response(self, timeout=1, read_at_once=10):
        '''
        Reads a whole response frame from the printer
        '''
        frame = ''
        self.conn.timeout = timeout

        data = self.conn.read(read_at_once)

        while data and '\x03' not in data:
            frame += data
            data = self.conn.read(read_at_once)

        frame += data

        return parse_frame(frame)

    def get_time(self):
        '''
        Gets time on the printer
        '''
        self.write(build_frame('rtcget'))
        resp = self.read_response()

        return datetime.strptime(resp.parameters[0][1], TIME_FORMAT)

    def set_time(self, date=None):
        '''
        Sets time on printer
        '''
        if date is None:
            date = datetime.now()

        date_str = date.strftime(TIME_FORMAT)
        frame = build_frame('rtcset', ('da', date_str))

        self.conn.write(frame)
        resp = self.read_response()

        assert resp.instruction == 'rtcset' and not resp.parameters, 'Wrong reply received.'
