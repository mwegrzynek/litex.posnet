# -*- coding: UTF-8 -*-
from datetime import datetime

from functools import partial
from binascii import hexlify
from construct import Struct, Byte, Bytes, Const, String, CString, \
    Switch, Pointer, Anchor, Sequence, GreedyRange, Computed, this, \
    RawCopy, Checksum, Probe, Container, Array, Range, Select

from PyCRC.CRCCCITT import CRCCCITT

TIME_FORMAT = '%Y-%m-%d;%H:%M'

crc16 = lambda val: '{:04x}'.format(CRCCCITT().calculate(val)).upper()

TabTerminated = CString(terminators=b'\x09', encoding='cp1250')

PosnetParameter = Struct(
    'name' / Select(Const('@'), Const('?'), String(length=2)),
    'value' / TabTerminated
)

PosnetFrame = Struct(
     Const(b'\x02'),
     'summed' / RawCopy(
         Struct(
             'instruction' / TabTerminated,
             'parameters' / GreedyRange(PosnetParameter)
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
    frame = PosnetFrame.build(data)
    return frame

def parse_frame(frame):
    '''
    Reverse of build frame -- for parsing printer responses
    '''
    result = PosnetFrame.parse(frame)
    return Container(
        instruction=result.instruction,
        parameters=[(param.name, param.value) for param in result.parameters]
    )


class PosnetProtocolError(RuntimeError):

    def __init__(self, err_no, instruction_id=None, field_name=None, token=None):
        self.err_no = err_no
        self.instruction_id = instruction_id
        self.field_name = field_name
        self.token = token

    def __str__(self):
        return 'Code: {0.err_no}; instruction: {0.instruction_id}; field name: {0.field_name}; token: {0.token}'.format(self)


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

    def read_response(self, instruction, standard=False, timeout=1, read_at_once=10):
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

        resp = parse_frame(frame)

        if resp.instruction != instruction:
            '''
            Incorrect reply. Maybe it's an error?
            '''
            if resp.instruction == 'ERR':
                token, err_no, instruction_id, field_name = \
                    None, None, None, None

                for name, value in resp.parameters:
                    if name == '@':
                        token = value
                    elif name == '?':
                        err_no = value
                    elif name == 'cm':
                        instruction_id = value
                    elif name == 'fd':
                        field_name = value

                raise PosnetProtocolError(
                    err_no, instruction_id, field_name, token
                )
            else:
                raise AssertionError('Unknown response received: {}'.format(resp))
        else:
            if standard:
                assert resp.instruction == instruction and not resp.parameters, \
                    'Unknown response received: {}'.format(resp)
            return resp

    def get_time(self):
        '''
        Gets time on the printer
        '''
        self.write(build_frame('rtcget'))
        resp = self.read_response('rtcget')

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
        self.read_response('rtcset', standard=True)

    def get_vat_rates(self):
        '''
        Gets list of tuples in (<code>, <percentage>) format
        '''
        self.write(build_frame('vatget'))
        resp = self.read_response('vatget')

        return [
            (code[1].upper(), float(perc.replace(',', '.'))) \
            for code, perc in resp.parameters
        ]

    def show_on_display(self, display, line_no, text):
        '''
        display = 0 - client display
        display = 1 - operator display
        '''
        self.write(build_frame('dsptxtline', ('id', str(display)), ('no', str(line_no)), ('ln', text)))
        resp = self.read_response('dsptxtline', standard=True)

    def prepare_qr_code(self, text):
        '''
        Prepare a QR code for printing
        '''
        self.write(build_frame('qrcode', ('tx', text)))
        self.read_response('qrcode', standard=True)
