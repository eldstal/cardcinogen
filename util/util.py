import unittest
import sys

def get_default(dic, k, fallback, cast=None):
  retval = fallback

  if (k in dic): retval = dic[k]
  else: sys.stderr.write("Warning: Unspecified setting %s, defaulting to %s\n" % (k, fallback))

  if (cast is not None): retval = cast(retval)
  return retval

#
# Unit tests
#
class TestUtils(unittest.TestCase):

  def test_default(self):
    dic = { "text" : "abcd", "number" : 3.14, "numeric" : "34" }
    self.assertEqual(get_default(dic, "text", "xyz"), "abcd")
    self.assertEqual(get_default(dic, "notext", "xyz"), "xyz")
    self.assertEqual(get_default(dic, "number", 8), 3.14)
    self.assertEqual(get_default(dic, "number", 16, int), 3)
    self.assertEqual(get_default(dic, "numeric", 12, int), 34)
    self.assertEqual(get_default(dic, "not-a-number", 8), 8)

if __name__ == '__main__':
    unittest.main()

