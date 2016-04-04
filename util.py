import unittest
import sys

from PIL import Image

def get_default(dic, k, fallback, cast=None):
  retval = fallback

  if (k in dic): retval = dic[k]
  #else: sys.stderr.write("Warning: Unspecified setting %s, defaulting to %s\n" % (k, fallback))

  if (cast is not None): retval = cast(retval)
  return retval


def rotate_image(image, rotation):
  """ Rotate a PIL image, returning a minimal bounding image """

  if (rotation == 0): return image

  # Give enough space in all directions to properly rotate
  maxdim = max(image.height, image.width)
  rotimg = Image.new("RGBA", (maxdim*2, maxdim*2), (0, 0, 0, 0))
  rotimg.paste(image, (maxdim, maxdim), mask=image)
  rotimg = rotimg.rotate(rotation)

  # Trim off the excess
  return rotimg.crop(rotimg.getbbox())


def alignment_to_absolute(origin, dimensions, alignment_x="left", alignment_y="top"):
  """ Convert a specified location (origin + alignment) to absolute top-left coordinates """
  x,y = origin
  w,h = dimensions

  # Horizontal alignment
  if (alignment_x == "center"): x = int(x - (w/2))
  if (alignment_x == "right"): x = int(x - w)

  # Vertical alignment
  if (alignment_y == "center"): y = int(y - (h/2))
  if (alignment_y == "bottom"): y = int(y - h)

  return (x,y)


def aligned_maxdims(origin, dims, container_dims, alignment_x="left", alignment_y="top"):
  """ Determine the maximum dimensions of an object inside a container of fixed size. """
  x, y = origin
  w, h = dims
  cw, ch = container_dims

  # This needs to take into account the alignment (X)
  maxwidth = min(cw - x, w)
  if (alignment_x == "center"):
    maxwidth = min(2*x, 2*(cw - x))     # Edges of the card
    maxwidth = min(maxwidth, w)                     # Specified width

  elif (alignment_x == "right"):
    maxwidth = min(x, w)

  # Likewise, we need to find the max height including the edges of the card.
  maxheight = min(ch - y, h)
  if (alignment_y == "center"):
    maxheight = min(2*y, 2*(ch - y))   # Edges of the card
    maxheight = min(maxheight, h)                 # Specified height

  elif (alignment_y == "bottom"):
    maxheight = min(y, h)

  return (maxwidth, maxheight)


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

