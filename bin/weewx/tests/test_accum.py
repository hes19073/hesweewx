#
#    Copyright (c) 2009-2015 Tom Keffer <tkeffer@gmail.com>
#
#    See the file LICENSE.txt for your full rights.
#
"""Test module weewx.accum"""
import time
import unittest

import weewx.accum
from gen_fake_data import genFakeRecords

# 30 minutes worth of data:
start_ts = int(time.mktime((2009,1,1,0, 0,0,0,0,-1)))
stop_ts  = int(time.mktime((2009,1,1,0,30,0,0,0,-1)))

class AccumTest(unittest.TestCase):
    
    def setUp(self):

        self.dataset = [record for record in genFakeRecords(start_ts=start_ts, stop_ts=stop_ts, interval=5)]

    def test_scalarStats(self):
        
        ss = weewx.accum.ScalarStats()
        
        # Make sure the default values work:
        self.assertEqual(ss.min, None)
        self.assertEqual(ss.last, None)
        
        tmin = tmintime = None
        tsum = tcount = 0
        for record in self.dataset:
            if record['outTemp'] is not None:
                tsum += record['outTemp']
                tcount += 1
                if tmin is None or record['outTemp'] < tmin:
                    tmin = record['outTemp']
                    tmintime = record['dateTime']
                    
            ss.addHiLo(record['outTemp'], record['dateTime'])
            ss.addSum(record['outTemp'])
        
        self.assertEqual(ss.min, tmin)
        self.assertEqual(ss.mintime, tmintime)
        
        # Assumes the last data point is not None:
        self.assertEqual(ss.last,     self.dataset[-1]['outTemp'])
        self.assertEqual(ss.lasttime, self.dataset[-1]['dateTime'])
        
        self.assertEqual(ss.sum, tsum)
        self.assertEqual(ss.count, tcount)
        self.assertEqual(ss.avg, tsum/tcount)
        
        # Merge ss into its self. Should leave highs and lows unchanged, but double counts:
        ss.mergeHiLo(ss)
        ss.mergeSum(ss)
        
        self.assertEqual(ss.min, tmin)
        self.assertEqual(ss.mintime, tmintime)
        
        self.assertEqual(ss.last,     self.dataset[-1]['outTemp'])
        self.assertEqual(ss.lasttime, self.dataset[-1]['dateTime'])
        
        self.assertEqual(ss.sum, 2*tsum)
        self.assertEqual(ss.count, 2*tcount)
        
if __name__ == '__main__':
    unittest.main()
            
