# -*- coding: UTF-8 -*-
import os
from datetime import datetime

from nose.tools import eq_, ok_
from nose.plugins.attrib import attr
from serial import serial_for_url

conn = None

def setUp():
    printer_url = os.environ.get('POSNET_URL', 'hwgrep://1424:100b')
    global conn
    conn = serial_for_url(printer_url, timeout=1)

@attr('real')
def test_get_time():
    from ..protocol import PosnetProtocol
    pr = PosnetProtocol(conn)

    ok_(pr.get_time().year > 2015)

@attr('real')
def test_set_time():
    from ..protocol import PosnetProtocol
    pr = PosnetProtocol(conn)

    now = datetime.now()
    pr.set_time(now)
    now_on_printer = pr.get_time()

    diff = now_on_printer - now

    ok_(diff.seconds > 1000)

@attr('real')
def test_get_vat_rates():
    from ..protocol import PosnetProtocol
    pr = PosnetProtocol(conn)

    rates = pr.get_vat_rates()
    eq_(rates[0], ('A', 23.0))


@attr('real')
def test_show_on_display():
    from ..protocol import PosnetProtocol
    pr = PosnetProtocol(conn)

    pr.show_on_display(0, 0, u'Zażółć gęśla jaźń')


@attr('real')
def test_prepare_qr_code():
    from ..protocol import PosnetProtocol
    pr = PosnetProtocol(conn)

    pr.prepare_qr_code('http://www.litexservice.pl')
