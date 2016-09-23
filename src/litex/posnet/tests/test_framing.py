# -*- coding: UTF-8 -*-
from nose.tools import eq_
from nose.plugins.attrib import attr

def test_crc():
    from ..protocol import crc16
    eq_(crc16('ERR\t?5\t'), '7F84')

def test_single_parameter():
    from ..protocol import PosnetParameter

    frame = PosnetParameter.build(dict(name='da', value='20160101'))
    eq_(frame, 'da20160101\t')

def test_multiple_parameters():
    from construct import GreedyRange
    from ..protocol import PosnetParameter

    frame = GreedyRange(PosnetParameter).build([
        dict(name='da', value='20160101'),
        dict(name='vat', value='23')
    ])
    eq_(frame, 'da20160101\tva23\t')

def test_rtcget():
    from construct import Container
    from ..protocol import PosnetFrame

    get_clock_instr = Container(
        summed=dict(value=dict(
            instruction='rtcset',
            parameters=[
                Container(name='da', value='2016-09-22,12:05')
            ]
        ))
    )

    frame = PosnetFrame.build(get_clock_instr)
    eq_(frame, '\x02rtcset\tda2016-09-22,12:05\t#8534\x03')

def test_parse_err():
    from ..protocol import PosnetFrame
    res = PosnetFrame.parse('\x02ERR\t?5\t#7F84\x03')
    eq_(res.parameters[0].value, '5')

def test_build_frame():
    from ..protocol import build_frame
    frame = build_frame('rtcset', ('da', '2016-09-22,12:05'))
    eq_(frame, '\x02rtcset\tda2016-09-22,12:05\t#8534\x03')

def test_parse_frame():
    from ..protocol import parse_frame
    data = parse_frame('\x02rtcset\tda2016-09-22,12:05\t#8534\x03')
    eq_(data.instruction, 'rtcset')
    eq_(data.parameters, [('da', '2016-09-22,12:05')])
