import unittest

import sys
import os
from util import sysfont, util
from PIL import Image, ImageDraw, ImageFont


class TextLabel:
  """ Parsed version of a single text-label object """

  def __init__(self, json):
    """ Parse out the various settings of a text label and clean them up """
    self.source =   util.get_default(json, "source", "text.txt")
    self.x =        util.get_default(json, "x", 10, int)
    self.y =        util.get_default(json, "y", 10, int)
    self.color =    util.get_default(json, "color", "#000000")
    self.fontface = util.get_default(json, "font-face", "sans")
    self.fontsize = util.get_default(json, "font-size", 12, int)
    weight =        util.get_default(json, "font-weight", "regular")

    self.fontweight = sysfont.STYLE_NORMAL
    if (weight == "bold"):   self.fontweight = sysfont.STYLE_BOLD
    if (weight == "italic"): self.fontweight = sysfont.STYLE_ITALIC

    # Try to auto-select a font based on the user's string
    candidate_font = sysfont.get_font(self.fontface, self.fontweight)
    if (candidate_font is None):
      # Fallback to arial
      sys.stderr.write("Unable to locate font %s. Falling back to Arial.\n" % self.fontface)
      candidate_font = sysfont.get_font("arial black", self.fontweight)

    self.font = ImageFont.load_default()
    if (candidate_font is not None):
      self.font = ImageFont.truetype(candidate_font, self.fontsize)


  def render(self, dimensions, text):
    """ Generate a transparent PIL card layer with the text on it """
    image = Image.new("RGBA", dimensions, (0,0,0,0))
    draw = ImageDraw.Draw(image)
    # TODO: Wrapping
    draw.text((self.x, self.y), text, font=self.font, fill=self.color)

    return image


class TextGenerator:

  def __init__(self, directory):
    self.directory = directory
    self.loaded = {}


  def gen(self, filename):
    if (filename not in self.loaded):
      path = os.path.join(self.directory, filename)
      handle = open(path, "r")
      if (handle is None):
        sys.stderr.write("Unable to open text file %s\n" % path)
        return None
      sys.stderr.write("Opened file %s\n" % path)
      self.loaded[filename] = handle

    line = self.loaded[filename].readline().rstrip()
    if (line == ""):
      # End of file
      return None
    return line

#
# Unit tests
#
class TestTextStuff(unittest.TestCase):

  def test_text_init(self):
    # This one makes use of all the default values
    lab_default = TextLabel({})
    self.assertEqual(lab_default.x, 10)
    self.assertEqual(lab_default.y, 10)
    self.assertEqual(lab_default.color, "#000000")
    self.assertEqual(lab_default.source, "text.txt")
    self.assertEqual(lab_default.fontface, "sans")
    self.assertEqual(lab_default.fontsize, 12)

    # This one overrides every possible setting
    dic = {
      "source": "phrases.txt",
      "x": 20,
      "y": 30,
      "color": "#DEADBE",
      "font-face": "courier new",
      "font-size": 32,
      "font-weight": "bold"
    }

    lab_override = TextLabel(dic)

    self.assertEqual(lab_override.source, dic["source"])
    self.assertEqual(lab_override.x, dic["x"])
    self.assertEqual(lab_override.y, dic["y"])
    self.assertEqual(lab_override.color, dic["color"])
    self.assertEqual(lab_override.fontface, dic["font-face"])
    self.assertEqual(lab_override.fontsize, dic["font-size"])

  def test_render_text(self):
    lab_default = TextLabel({ "color": "#AABBCC" })
    layer = lab_default.render((100, 30), "Hello")
    self.assertEqual(layer.width, 100)
    self.assertEqual(layer.height, 30)
    # There are some transparent pixels and some of the text color. Good enough.
    self.assertEqual(layer.getextrema(), ((0, 0xAA), (0, 0xBB), (0, 0xCC), (0, 255)))

if __name__ == '__main__':
    unittest.main()

