#!/usr/bin/python
#
# Copyright 2012 Google Inc. All Rights Reserved.
#
# unittest requires method names starting in 'test'
#pylint: disable-msg=C6409

"""Unit tests for tr-181 Device.MoCA.* implementation."""

__author__ = 'dgentry@google.com (Denton Gentry)'

import unittest
import google3
import tr.tr181_v2_2 as tr181
import brcmmoca
import netdev


class MocaTest(unittest.TestCase):
  """Tests for brcmmoca.py."""

  def setUp(self):
    self.old_MOCACTL = brcmmoca.MOCACTL
    self.old_PYNETIFCONF = brcmmoca.PYNETIFCONF
    self.old_PROC_NET_DEV = netdev.PROC_NET_DEV

  def tearDown(self):
    brcmmoca.MOCACTL = self.old_MOCACTL
    brcmmoca.PYNETIFCONF = self.old_PYNETIFCONF
    netdev.PROC_NET_DEV = self.old_PROC_NET_DEV

  def testMocaInterfaceStatsGood(self):
    netdev.PROC_NET_DEV = 'testdata/brcmmoca/proc/net/dev'
    moca = brcmmoca.BrcmMocaInterfaceStatsLinux26('foo0')
    moca.ValidateExports()

    self.assertEqual(moca.BroadcastPacketsReceived, None)
    self.assertEqual(moca.BroadcastPacketsSent, None)
    self.assertEqual(moca.BytesReceived, '1')
    self.assertEqual(moca.BytesSent, '9')
    self.assertEqual(moca.DiscardPacketsReceived, '4')
    self.assertEqual(moca.DiscardPacketsSent, '11')
    self.assertEqual(moca.ErrorsReceived, '9')
    self.assertEqual(moca.ErrorsSent, '12')
    self.assertEqual(moca.MulticastPacketsReceived, '8')
    self.assertEqual(moca.MulticastPacketsSent, None)
    self.assertEqual(moca.PacketsReceived, '100')
    self.assertEqual(moca.PacketsSent, '10')
    self.assertEqual(moca.UnicastPacketsReceived, '92')
    self.assertEqual(moca.UnicastPacketsSent, '10')
    self.assertEqual(moca.UnknownProtoPacketsReceived, None)

  def testMocaInterfaceStatsNonexistent(self):
    netdev.PROC_NET_DEV = 'testdata/brcmmoca/proc/net/dev'
    moca = brcmmoca.BrcmMocaInterfaceStatsLinux26('doesnotexist0')
    exception_raised = False
    try:
      moca.ErrorsReceived
    except AttributeError:
      exception_raised = True
    self.assertTrue(exception_raised)

  def testMocaInterface(self):
    brcmmoca.PYNETIFCONF = MockPynet
    brcmmoca.MOCACTL = 'testdata/brcmmoca/mocactl'
    moca = brcmmoca.BrcmMocaInterface(ifname='foo0', upstream=False)
    self.assertEqual(moca.Name, 'foo0')
    self.assertEqual(moca.LowerLayers, '')
    self.assertFalse(moca.Upstream)
    self.assertEqual(moca.MACAddress, MockPynet.v_mac)
    moca = brcmmoca.BrcmMocaInterface(ifname='foo0', upstream=True)
    self.assertTrue(moca.Upstream)
    MockPynet.v_is_up = True
    MockPynet.v_link_up = True
    self.assertEqual(moca.Status, 'Up')
    MockPynet.v_link_up = False
    self.assertEqual(moca.Status, 'Dormant')
    MockPynet.v_is_up = False
    self.assertEqual(moca.Status, 'Down')
    self.assertEqual(moca.FirmwareVersion, '5.6.789')
    self.assertEqual(moca.NetworkCoordinator, 1)
    self.assertEqual(moca.NodeID, 2)

  def testMocaInterfaceMocaCtlFails(self):
    brcmmoca.PYNETIFCONF = MockPynet
    brcmmoca.MOCACTL = 'testdata/brcmmoca/mocactl_fail'
    moca = brcmmoca.BrcmMocaInterface(ifname='foo0', upstream=False)
    self.assertEqual(moca.FirmwareVersion, '0')


class MockPynet(object):
  v_is_up = True
  v_mac = '00:11:22:33:44:55'
  v_speed = 1000
  v_duplex = True
  v_auto = True
  v_link_up = True

  def __init__(self, ifname):
    self.ifname = ifname

  def is_up(self):
    return self.v_is_up

  def get_mac(self):
    return self.v_mac

  def get_link_info(self):
    return (self.v_speed, self.v_duplex, self.v_auto, self.v_link_up)


if __name__ == '__main__':
  unittest.main()