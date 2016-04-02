import unittest

from PIL import Image

class CardTiler:
  """ Takes individual card faces and builds the 10x7 tiled image for Tabletop """
  def __init__(self):
    self.backcolor = (0, 255, 0)
    pass


  def empty_tiling(self, hidden):
    w = 10 * hidden.width
    h = 7 * hidden.height

    # A flat image
    ret = Image.new("RGB", (w, h), self.backcolor)

    # The hidden image goes in the bootom-left slot
    ret.paste(hidden, (w - hidden.width, h - hidden.height))

    return ret

  def tile(self, cards, hidden):
    """ List of card face images, a single hidden-card face image of the same size """
    ret = []

    tiling = self.empty_tiling(hidden)

    index = 0
    while (len(cards) > 0):

      face = cards.pop(0)

      # Coordinates of this card in the grid
      yc = index // 10
      xc = index % 10

      # Pixel coordinates of this card's upper-left corner
      x = xc * hidden.width
      y = yc * hidden.height

      # Insert the image into the grid
      tiling.paste(face, (x, y))

      index += 1

      # Starting a new 69-card image
      if (index >= 69):
        ret.append(tiling)
        tiling = self.empty_tiling(hidden)
        index = 0

    # Don't forget the last (unfilled!) tile
    if (index != 0): ret.append(tiling)

    return ret

#
# Unit tests
#
class TestTiler(unittest.TestCase):

  # Unique card colors
  def cc(self, index):
    return (255-(index % 256), 255 ^ (index % 256) , index % 256)

  def test_static(self):
    empt = CardTiler()
    face = Image.new("RGB", (30, 50), (10, 20, 30))
    hidden = Image.new("RGB", face.size, (255, 0, 255))
    tilings = empt.tile([face], hidden)

    self.assertEqual(len(tilings), 1)
    self.assertEqual(tilings[0].size, (30*10, 50*7))
    self.assertEqual(tilings[0].getpixel((299, 349)), (255, 0, 255))

  def test_boundary(self):

    # This one should fill up exactly, 69 cards.
    full = CardTiler()

    faces = []
    for i in range(69):
      faces.append(Image.new("RGB", (30, 50), self.cc(i) ))   # each card is unique!

    hidden = Image.new("RGB", faces[0].size, (255, 0, 255))
    tilings = full.tile(faces, hidden)

    self.assertEqual(len(tilings), 1)
    self.assertEqual(tilings[0].size, (30*10, 50*7))
    self.assertEqual(tilings[0].getpixel((299, 349)), (255, 0, 255))
    self.assertEqual(tilings[0].getpixel((269, 349)), self.cc(i))

  def test_multiple(self):
    # One full and one new tiling with only one card on it
    overfilled = CardTiler()
    faces = []
    for i in range(70):
      faces.append(Image.new("RGB", (30, 50), self.cc(i)))   # each card is unique!

    hidden = Image.new("RGB", faces[0].size, (255, 0, 255))
    tilings = overfilled.tile(faces, hidden)

    self.assertEqual(len(tilings), 2)
    self.assertEqual(tilings[0].size, (30*10, 50*7))
    self.assertEqual(tilings[0].getpixel((299, 349)), (255, 0, 255))    # Hidden card
    self.assertEqual(tilings[0].getpixel((269, 349)), self.cc(68))      # Face of card 69
    self.assertEqual(tilings[1].size, (30*10, 50*7))
    self.assertEqual(tilings[1].getpixel((299, 349)), (255, 0, 255))    # Hidden card
    self.assertEqual(tilings[1].getpixel((269, 349)), (0, 255, 0))      # Face of card 69, there's no card there.
    self.assertEqual(tilings[1].getpixel((1, 1)), self.cc(69))          # There's a card in the first slot

if __name__ == '__main__':
    unittest.main()

