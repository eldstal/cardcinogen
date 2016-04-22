import unittest
import sys

from PIL import Image
import log

def get_default(dic, k, fallback, cast=None):
  retval = fallback

  if (k in dic): retval = dic[k]
  #else: log.log.write("Warning: Unspecified setting %s, defaulting to %s\n" % (k, fallback))

  if (cast is not None): retval = cast(retval)
  return retval

# If the image can't be loaded, return a default of the specified dimensions
# If accept_dimension is specified, scale non-matching image to that size
def default_image(path, default_dimension=(300,800), accept_dimension=None):
  try:
    loaded = Image.open(path)
    loaded.load()
  except:
    log.log.write("Unable to load image %s. Falling back to plain.\n" % path)
    return Image.new("RGBA", default_dimension, (230, 230, 255, 255))

  if (accept_dimension != None):
    if (loaded.size != accept_dimension):
      log.log.write("Image sizes not matching. Resizing to %d x %d\n" % accept_dimension)
      return loaded.resize(accept_dimension, Image.BICUBIC)

  # Image is good enough as it is.
  return loaded

def rotate_image(image, rotation):
  """ Rotate a PIL image, returning a minimal bounding image """

  if (rotation == 0): return image

  # Give enough space in all directions to properly rotate
  maxdim = max(image.height, image.width)
  rotimg = Image.new("RGBA", (maxdim*2, maxdim*2), (0, 0, 0, 0))
  rotimg.paste(image,
               (maxdim - int(image.width/2), maxdim - int(image.height/2)),  # Center the image
               mask=image)
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
    maxwidth = min(2*x, 2*(cw - x))                 # Edges of the container
    maxwidth = min(maxwidth, w)                     # Specified width

  elif (alignment_x == "right"):
    maxwidth = min(x, w)

  # Likewise, we need to find the max height including the edges of the card.
  maxheight = min(ch - y, h)
  if (alignment_y == "center"):
    maxheight = min(2*y, 2*(ch - y))              # Edges of the container
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

  def test_alignment_to_absolute(self):
    pos = alignment_to_absolute((20,30), (10, 15), "left", "top")
    self.assertEqual(pos, (20,30))

    pos = alignment_to_absolute((20,30), (10, 15), "center", "top")
    self.assertEqual(pos, (15,30))

    pos = alignment_to_absolute((20,30), (10, 15), "right", "top")
    self.assertEqual(pos, (10,30))

    pos = alignment_to_absolute((20,30), (10, 15), "left", "center")
    self.assertEqual(pos, (20,22))

    pos = alignment_to_absolute((20,30), (10, 15), "left", "bottom")
    self.assertEqual(pos, (20,15))

  def test_align_maxdims(self):

    # Left-aligned
    #
    # No edges
    dims = aligned_maxdims((20, 30), (100, 200), (300, 400), "left", "top")
    self.assertEqual(dims, (100, 200))

    # Right edge
    dims = aligned_maxdims((20, 30), (100, 200), (100, 400), "left", "top")
    self.assertEqual(dims, (80, 200))

    # Horizontal centering
    #
    # No edges
    dims = aligned_maxdims((150, 30), (100, 200), (300, 400), "center", "top")
    self.assertEqual(dims, (100, 200))

    # Right edge
    dims = aligned_maxdims((280, 30), (140, 200), (300, 400), "center", "top")
    self.assertEqual(dims, (40, 200))

    # Left edge
    dims = aligned_maxdims((30, 30), (140, 200), (300, 400), "center", "top")
    self.assertEqual(dims, (60, 200))

    # Right-aligned
    #
    # No edges
    dims = aligned_maxdims((120, 30), (100, 200), (300, 400), "right", "top")
    self.assertEqual(dims, (100, 200))

    # Right edge
    dims = aligned_maxdims((120, 30), (140, 200), (100, 400), "right", "top")
    self.assertEqual(dims, (120, 200))


    # Top-aligned
    #
    # No edges
    dims = aligned_maxdims((20, 30), (10, 200), (300, 400), "left", "top")
    self.assertEqual(dims, (10, 200))

    # Bottom edge
    dims = aligned_maxdims((20, 210), (10, 200), (300, 400), "left", "top")
    self.assertEqual(dims, (10, 190))

    # Vertical centering
    #
    # No edges
    dims = aligned_maxdims((20, 110), (100, 200), (300, 400), "right", "center")
    self.assertEqual(dims, (20, 200))

    # Top edge
    dims = aligned_maxdims((20, 100), (110, 250), (300, 400), "right", "center")
    self.assertEqual(dims, (20, 200))

    # Bottom edge
    dims = aligned_maxdims((20, 300), (110, 250), (300, 400), "right", "center")
    self.assertEqual(dims, (20, 200))

    # Bottom-aligned
    #
    # No edges
    dims = aligned_maxdims((20, 230), (10, 200), (300, 400), "left", "bottom")
    self.assertEqual(dims, (10, 200))

    # Top edge
    dims = aligned_maxdims((20, 40), (10, 200), (300, 400), "left", "bottom")
    self.assertEqual(dims, (10, 40))


  def test_rotate_image(self):
    # A block that's pink on one side and blue on the other
    pink = (255, 50, 200, 255)
    blue = (0, 50, 255, 255)
    left = Image.new("RGBA", (40, 40), pink)
    box = Image.new("RGBA", (80, 40), blue)
    box.paste(left, (0, 0))

    stand = rotate_image(box, 90)
    self.assertEqual(stand.size, (40, 80))
    self.assertEqual(stand.getpixel((0,0)), blue)
    self.assertEqual(stand.getpixel((0,79)), pink)

    fall = rotate_image(box, -90)
    self.assertEqual(fall.size, (40, 80))
    self.assertEqual(fall.getpixel((0,0)), pink)
    self.assertEqual(fall.getpixel((0,79)), blue)


if __name__ == '__main__':
    unittest.main()

