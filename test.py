import os
# os.environ.update({'DEBUG_SERVER':'1'})
from debug import debug

debug(TEST_debug = "TEST", debug = 1, simple=True)
class Test:
    def testme(self):
        debug(TEST_debug_1 = "TEST", debug = 1, simple=True)

Test().testme()
