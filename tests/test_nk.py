#!/usr/bin/env python
__author__ = 'Alex'
"""
Tests the cdl related functions of cdl_convert

REQUIREMENTS:

mock
"""

# ==============================================================================
# IMPORTS
# ==============================================================================

# Standard Imports
from decimal import Decimal
try:
    from unittest import mock
except ImportError:
    import mock
import os
import sys
import tempfile
import unittest

# Grab our test's path and append the cdL_convert root directory

# There has to be a better method than:
# 1) Getting our current directory
# 2) Splitting into list
# 3) Splicing out the last 3 entries (filepath, test dir, tools dir)
# 4) Joining
# 5) Appending to our Python path.

sys.path.append('/'.join(os.path.realpath(__file__).split('/')[:-2]))

import cdl_convert

# ==============================================================================
# GLOBALS
# ==============================================================================

NUKE_SINGLE_OCIO_FILE = """set cut_paste_input [stack 0]
version 9.0 v6
push $cut_paste_input
OCIOCDLTransform {
 slope {1.100000024 0.05332994089 0.5167440772}
 offset {0.005376434419 0.05999999866 0}
 power {0.1321808547 0.2599999905 0.1195999905}
 saturation 0.25
 working_space linear
 name OCIOCDLTransform1
 selected true
 xpos -40
 ypos -226
}"""

NUKE_SINGLE_NOTFLOAT3_OCIO_FILE = """set cut_paste_input [stack 0]
version 9.0 v6
push $cut_paste_input
OCIOCDLTransform {
 slope {2 1 4}
 offset {0.5 0 0}
 power 0.8
 saturation 0.25
 working_space linear
 name OCIOCDLTransform7
 selected true
 xpos -480
 ypos -106
}"""

NUKE_SINGLE_DEFAULTVALUES_OCIO_FILE = """set cut_paste_input [stack 0]
version 9.0 v6
push $cut_paste_input
OCIOCDLTransform {
 offset {0.3 0.2 0.2}
 power {1.1 1.4 2}
 saturation 0.7
 working_space linear
 name OCIOCDLTransform8
 selected true
 xpos -480
 ypos -34
}"""

NUKE_MULTI_OCIO_FILE = """set cut_paste_input [stack 0]
version 9.0 v6
push $cut_paste_input
OCIOCDLTransform {
 slope {1.100000024 0.05332994089 0.5167440772}
 offset {0.005376434419 0.05999999866 0}
 power {0.1321808547 0.2599999905 0.1195999905}
 saturation 0.25
 working_space linear
 name OCIOCDLTransform1
 selected true
 xpos -480
 ypos -250
}
OCIOCDLTransform {
 slope {1.1 1.2 1.3}
 offset {0.4 0.5 0.6}
 power {1.7 1.8 1.9}
 saturation 2
 working_space linear
 name OCIOCDLTransform6
 selected true
 xpos -480
 ypos -178
}"""


NUKE_NO_NODES_OCIO_FILE = """set cut_paste_input [stack 0]
version 9.0 v6
push $cut_paste_input
Grade {
 name Grade1
 selected true
 xpos -370
 ypos -586
}
Transform {
 center {1024 778}
 name Transform1
 selected true
 xpos -370
 ypos -490
}"""


# misc ========================================================================

if sys.version_info[0] >= 3:
    enc = lambda x: bytes(x, 'UTF-8')
else:
    enc = lambda x: x

if sys.version_info[0] >= 3:
    builtins = 'builtins'
else:
    builtins = '__builtin__'


# ==============================================================================
# TEST CLASSES
# ==============================================================================

class TestParseNkFull(unittest.TestCase):
    """Tests a full nk parse"""

    # ==========================================================================
    # SETUP & TEARDOWN
    # ==========================================================================

    def setUp(self):

        self.node_names = ["OCIOCDLTransform1"]
        self.slopes = [decimalize(1.100000024, 0.05332994089, 0.5167440772)]
        self.offsets = [decimalize(0.005376434419, 0.05999999866, 0)]
        self.powers = [decimalize(0.1321808547, 0.2599999905, 0.1195999905)]
        self.sats = [Decimal('0.25')]

        # Build our cdl
        with tempfile.NamedTemporaryFile(mode='wb', delete=False) as f:
            f.write(enc(NUKE_SINGLE_OCIO_FILE))
            self.filename = f.name

        self.ccc = cdl_convert.parse_nk(self.filename)
        self.children = self.ccc.all_children

    # ==========================================================================

    def tearDown(self):
        # The system should clean these up automatically,
        # but we'll be neat.
        os.remove(self.filename)
        # We need to clear the ColorCorrection member dictionary so we don't
        # have to worry about non-unique ids.
        cdl_convert.reset_all()

    # ==========================================================================
    # TESTS
    # ==========================================================================

    def testId(self):
        """Tests that id was set to the filename without extension"""
        node_ids = [os.path.basename(self.filename).split('.')[0] + "." + node_name for node_name in self.node_names]
        ids = [x.id for x in self.children]
        self.assertEqual(
            node_ids,
            ids
        )

    # ==========================================================================

    def testSlope(self):
        """Tests that slope was set correctly"""
        slopes = [x.slope for x in self.children]
        self.assertEqual(
            self.slopes,
            slopes
        )

    # ==========================================================================

    def testOffset(self):
        """Tests that offset was set correctly"""
        offsets = [x.offset for x in self.children]
        self.assertEqual(
            self.offsets,
            offsets
        )

    # ==========================================================================

    def testPower(self):
        """Tests that power was set correctly"""
        powers = [x.power for x in self.children]
        self.assertEqual(
            self.powers,
            powers
        )

    # ==========================================================================

    def testSat(self):
        """Tests that sat was set correctly"""
        sats = [x.sat for x in self.children]
        self.assertEqual(
            self.sats,
            sats
        )


class TestParseNkSingleValue(unittest.TestCase):
    """Tests a full nk parse"""

    # ==========================================================================
    # SETUP & TEARDOWN
    # ==========================================================================

    def setUp(self):

        self.node_names = ["OCIOCDLTransform7"]
        self.slopes = [decimalize(2, 1, 4)]
        self.offsets = [decimalize(0.5, 0, 0)]
        self.powers = [decimalize(0.8, 0.8, 0.8)]
        self.sats = [Decimal('0.25')]

        # Build our cdl
        with tempfile.NamedTemporaryFile(mode='wb', delete=False) as f:
            f.write(enc(NUKE_SINGLE_NOTFLOAT3_OCIO_FILE))
            self.filename = f.name

        self.ccc = cdl_convert.parse_nk(self.filename)
        self.children = self.ccc.all_children

    # ==========================================================================

    def tearDown(self):
        # The system should clean these up automatically,
        # but we'll be neat.
        os.remove(self.filename)
        # We need to clear the ColorCorrection member dictionary so we don't
        # have to worry about non-unique ids.
        cdl_convert.reset_all()

    # ==========================================================================
    # TESTS
    # ==========================================================================

    def testId(self):
        """Tests that id was set to the filename without extension"""
        node_ids = [os.path.basename(self.filename).split('.')[0] + "." + node_name for node_name in self.node_names]
        ids = [x.id for x in self.children]
        self.assertEqual(
            node_ids,
            ids
        )

    # ==========================================================================

    def testSlope(self):
        """Tests that slope was set correctly"""
        slopes = [x.slope for x in self.children]
        self.assertEqual(
            self.slopes,
            slopes
        )

    # ==========================================================================

    def testOffset(self):
        """Tests that offset was set correctly"""
        offsets = [x.offset for x in self.children]
        self.assertEqual(
            self.offsets,
            offsets
        )

    # ==========================================================================

    def testPower(self):
        """Tests that power was set correctly"""
        powers = [x.power for x in self.children]
        self.assertEqual(
            self.powers,
            powers
        )

    # ==========================================================================

    def testSat(self):
        """Tests that sat was set correctly"""
        sats = [x.sat for x in self.children]
        self.assertEqual(
            self.sats,
            sats
        )


class TestParseNkDefaultValue(unittest.TestCase):
    """Tests a full nk parse"""

    # ==========================================================================
    # SETUP & TEARDOWN
    # ==========================================================================

    def setUp(self):

        self.node_names = ["OCIOCDLTransform8"]
        self.slopes = [decimalize(1, 1, 1)]
        self.offsets = [decimalize(0.3, 0.2, 0.2)]
        self.powers = [decimalize(1.1, 1.4, 2)]
        self.sats = [Decimal('0.7')]

        # Build our cdl
        with tempfile.NamedTemporaryFile(mode='wb', delete=False) as f:
            f.write(enc(NUKE_SINGLE_DEFAULTVALUES_OCIO_FILE))
            self.filename = f.name

        self.ccc = cdl_convert.parse_nk(self.filename)
        self.children = self.ccc.all_children

    # ==========================================================================

    def tearDown(self):
        # The system should clean these up automatically,
        # but we'll be neat.
        os.remove(self.filename)
        # We need to clear the ColorCorrection member dictionary so we don't
        # have to worry about non-unique ids.
        cdl_convert.reset_all()

    # ==========================================================================
    # TESTS
    # ==========================================================================

    def testId(self):
        """Tests that id was set to the filename without extension"""
        node_ids = [os.path.basename(self.filename).split('.')[0] + "." + node_name for node_name in self.node_names]
        ids = [x.id for x in self.children]
        self.assertEqual(
            node_ids,
            ids
        )

    # ==========================================================================

    def testSlope(self):
        """Tests that slope was set correctly"""
        slopes = [x.slope for x in self.children]
        self.assertEqual(
            self.slopes,
            slopes
        )

    # ==========================================================================

    def testOffset(self):
        """Tests that offset was set correctly"""
        offsets = [x.offset for x in self.children]
        self.assertEqual(
            self.offsets,
            offsets
        )

    # ==========================================================================

    def testPower(self):
        """Tests that power was set correctly"""
        powers = [x.power for x in self.children]
        self.assertEqual(
            self.powers,
            powers
        )

    # ==========================================================================

    def testSat(self):
        """Tests that sat was set correctly"""
        sats = [x.sat for x in self.children]
        self.assertEqual(
            self.sats,
            sats
        )


class TestParseNkMultiNode(unittest.TestCase):
    """Tests a full nk parse"""

    # ==========================================================================
    # SETUP & TEARDOWN
    # ==========================================================================

    def setUp(self):

        self.node_names = ["OCIOCDLTransform1", "OCIOCDLTransform6"]
        self.slopes = [decimalize(1.100000024, 0.05332994089, 0.5167440772),
                       decimalize(1.1, 1.2, 1.3)]
        self.offsets = [decimalize(0.005376434419, 0.05999999866, 0),
                        decimalize(0.4, 0.5, 0.6)]
        self.powers = [decimalize(0.1321808547, 0.2599999905, 0.1195999905),
                       decimalize(1.7, 1.8, 1.9)]
        self.sats = [Decimal('0.25'),
                     Decimal('2')]

        # Build our cdl
        with tempfile.NamedTemporaryFile(mode='wb', delete=False) as f:
            f.write(enc(NUKE_MULTI_OCIO_FILE))
            self.filename = f.name

        self.ccc = cdl_convert.parse_nk(self.filename)
        self.children = self.ccc.all_children

    # ==========================================================================

    def tearDown(self):
        # The system should clean these up automatically,
        # but we'll be neat.
        os.remove(self.filename)
        # We need to clear the ColorCorrection member dictionary so we don't
        # have to worry about non-unique ids.
        cdl_convert.reset_all()

    # ==========================================================================
    # TESTS
    # ==========================================================================

    def testId(self):
        """Tests that id was set to the filename without extension"""
        node_ids = [os.path.basename(self.filename).split('.')[0] + "." + node_name for node_name in self.node_names]
        ids = [x.id for x in self.children]
        self.assertEqual(
            node_ids,
            ids
        )

    # ==========================================================================

    def testSlope(self):
        """Tests that slope was set correctly"""
        slopes = [x.slope for x in self.children]
        self.assertEqual(
            self.slopes,
            slopes
        )

    # ==========================================================================

    def testOffset(self):
        """Tests that offset was set correctly"""
        offsets = [x.offset for x in self.children]
        self.assertEqual(
            self.offsets,
            offsets
        )

    # ==========================================================================

    def testPower(self):
        """Tests that power was set correctly"""
        powers = [x.power for x in self.children]
        self.assertEqual(
            self.powers,
            powers
        )

    # ==========================================================================

    def testSat(self):
        """Tests that sat was set correctly"""
        sats = [x.sat for x in self.children]
        self.assertEqual(
            self.sats,
            sats
        )


class TestParseNkMNoNode(unittest.TestCase):
    """Tests a full nk parse"""

    # ==========================================================================
    # SETUP & TEARDOWN
    # ==========================================================================

    def setUp(self):

        self.exception_str = "The passed file does not appear to have Nuke nodes of type OCIOCDLTransform. Please make" \
                             " sure that you are using the OCIOCDLTransform nodes when exporting the CDL data."

        # Build our cdl
        with tempfile.NamedTemporaryFile(mode='wb', delete=False) as f:
            f.write(enc(NUKE_MULTI_OCIO_FILE))
            self.filename = f.name

        self.ccc = cdl_convert.parse_nk(self.filename)

    # ==========================================================================

    def tearDown(self):
        # The system should clean these up automatically,
        # but we'll be neat.
        os.remove(self.filename)
        # We need to clear the ColorCorrection member dictionary so we don't
        # have to worry about non-unique ids.
        cdl_convert.reset_all()

    # ==========================================================================
    # TESTS
    # ==========================================================================

    def testRaisesException(self):
        """Tests that id was set to the filename without extension"""
        self.assertRaisesRegexp(ValueError, self.exception_str)


# ==============================================================================
# FUNCTIONS
# ==============================================================================
def decimalize(*args):
    """Converts a list of floats/ints to Decimal list"""
    return tuple(Decimal(str(i)) for i in args)

# ==============================================================================
# RUNNER
# ==============================================================================
if __name__ == '__main__':
    unittest.main()
