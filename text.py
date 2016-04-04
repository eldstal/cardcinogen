import unittest

import sys
import os
import json
import textwrap
import sysfont
import util
from PIL import Image, ImageDraw, ImageFont


def wrap_pixel_width(text, maxwidth, font, linesep='\n'):
  """ Split into a list of text lines, such that none of them exceeds the pixel width """
  ret = []

  # Start by respecting any \n newlines in the text
  paragraphs = text.split(linesep)

  # Each of those sections is wrapped individually
  for paragraph in paragraphs:
    if (paragraph == ""): # respect empty lines...
      ret += [" "]
      continue

    for chars in range(len(paragraph), 1, -1):
      lines = textwrap.wrap(paragraph, chars)
      too_wide = False
      for l in lines:
        lw, _ = font.getsize(l)
        if (lw > maxwidth): too_wide = True

      if (not too_wide):
        ret += lines
        break


  if (len(ret) == 0): ret = None
  return ret

# Generate a label-image of a size that fits the text and render it
def render_lines(lines, font, color="#000000", justify="left", spacing=4):
  width = 0
  height = 0

  # Measure the text to figure out our bounds
  for l in lines:
    w,h = font.getsize(l)
    width = max(w, width)
    height = height + h + spacing

  # Some fonts render outside that calculated size, for some reason.
  # Give them some margins and crop it off later.
  image = Image.new("RGBA", (width*2, height*2), (0,0,0,0))
  draw = ImageDraw.Draw(image)

  # Render the text onto our label
  y = 0
  for l in lines:
    w,h = font.getsize(l)

    # Alignment affects each line of text differently.
    x = 0
    if (justify == "center"): x = (width - w) / 2
    if (justify == "right"): x = width - w

    draw.text((x, y), l, font=font, fill=color)
    y += h + spacing

  # Crop the image down to the exact bounds of the text
  return image.crop(image.getbbox())


class TextLabel:
  """ Parsed version of a single text-label object """

  def __init__(self, json):
    """ Parse out the various settings of a text label and clean them up """
    self.source =     util.get_default(json, "source", "text.txt")
    self.type =       util.get_default(json, "type", "simple")
    self.x =          util.get_default(json, "x", 10, int)
    self.y =          util.get_default(json, "y", 10, int)
    self.width =      util.get_default(json, "width", 40000, int)
    self.height =     util.get_default(json, "height", 40000, int)
    self.color =      util.get_default(json, "color", "#000000")
    self.fontface =   util.get_default(json, "font-face", "sans")
    self.fontsize =   util.get_default(json, "font-size", 12, int)
    self.spacing =    util.get_default(json, "line-spacing", 4, int)
    self.justify =    util.get_default(json, "justify", "left")
    self.x_align =    util.get_default(json, "x-align", "left")
    self.y_align =    util.get_default(json, "y-align", "top")
    self.wordwrap =   util.get_default(json, "wordwrap", True, bool)
    self.rotation =   util.get_default(json, "rotation", 0, int)
    weight =          util.get_default(json, "font-weight", "regular")

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


  def render(self, card_dims, text):
    """ Generate a transparent PIL card layer with the text on it """
    # If the user has set a max width, respect that.
    # If not, we use the edge of the card.

    if (self.rotation == 0):
      maxwidth, maxheight = util.aligned_maxdims((self.x, self.y),
                                                 (self.width, self.height),
                                                 card_dims,
                                                 self.x_align,
                                                 self.y_align)
    else:
      # Due to rotation of the text, we don't fully take the card's edges into account.
      maxdim = max(card_dims)
      maxwidth = min(self.width, maxdim)
      maxheight = min(self.height, maxdim)

    # Split the text into lines, in a way that fits our width
    lines = [text]
    if (self.wordwrap):
      lines = wrap_pixel_width(text, maxwidth, self.font, linesep='\\n')

    if (lines is None):
      sys.stderr.write("Warning: Unable to wrap text label \"%s\"\n" % text)
      return None

    # Render the text, one line at a time
    label = render_lines(lines,
                         font=self.font,
                         color=self.color,
                         justify=self.justify,
                         spacing=self.spacing)

    if (label.width > maxwidth):
      sys.stderr.write("Warning: Text label overflows max width: \"%s\"\n" % text)
      return None

    if (label.height > maxheight):
      sys.stderr.write("Warning: Text label overflows max height: \"%s\"\n" % text)
      return None

    if (self.rotation != 0):
      label = util.rotate_image(label, self.rotation)

    # Figure out where to place the top-left corner of the label
    x,y = util.alignment_to_absolute((self.x, self.y), label.size, self.x_align, self.y_align)

    if (x < 0 or y < 0 or
        x + label.width > card_dims[0] or
        y + label.height > card_dims[1]):
      sys.stderr.write("Warning: Text label overflows card boundary: \"%s\"\n" % text)
      return None

    image = Image.new("RGBA", card_dims, (0,0,0,0))
    image.paste(label, (x,y), mask=label)

    return image

class TextLabelComplex:
  """ Parsed version of a complex text-label object """

  def __init__(self, json, rootdir):
    self.source =       util.get_default(json, "source", "text.json")
    self.type =         util.get_default(json, "type", "simple")
    self.frontSource =  util.get_default(json, "front", "")
    self.subLabelSpecs =    util.get_default(json, "texts", [])
    self.directory =    rootdir

    self.subLabels = {}
    for spec in self.subLabelSpecs:
      name = util.get_default(spec, "name", "")
      self.subLabels[name] = TextLabel(spec)



  def render(self, dimensions, texts):
    """ Generate a transparent PIL card layer with the text on it """

    image = Image.new("RGBA", dimensions, (0,0,0,0))
    if (self.frontSource != ""):
      path = os.path.join(self.directory, self.frontSource)
      front = Image.open(path, 'r')
      image.paste(front, (0,0))

    for name,label in self.subLabels.items():

      text = util.get_default(texts, name, "")

      rendered_text = label.render(dimensions, text)
      if (rendered_text is None):
        sys.stderr.write("Failed to render sub-label %s.\n" % name)
        return None

      image.paste(rendered_text, (0, 0), mask=rendered_text)

    return image


class TextGenerator:

  def __init__(self, directory):
    self.directory = directory
    self.loaded = {}


  def gen(self, filename):
    """ Fetch one line from a given text file in the deck directory """
    if (filename not in self.loaded):
      path = os.path.join(self.directory, filename)
      handle = open(path, "r")
      if (handle is None):
        sys.stderr.write("Unable to open text file %s\n" % path)
        return None
      self.loaded[filename] = handle

    line = self.loaded[filename].readline().rstrip()
    if (line == ""):
      # End of file
      return None
    return line

  def gen_complex(self, filename):
    """ Fetch an entire card (named fields) from a JSON file in the deck directory """
    if (filename not in self.loaded):
      path = os.path.join(self.directory, filename)
      handle = open(path, "r")
      if (handle is None):
        sys.stderr.write("Unable to open json file %s\n" % path)
        return None
      self.loaded[filename] = json.load(handle)

    if (len(self.loaded[filename]) == 0):
      #End of file
      return None
    texts = self.loaded[filename].pop()
    return texts

#
# Unit tests
#
class TestTextStuff(unittest.TestCase):

  def test_text_init(self):
    # This one makes use of all the default values
    lab_default = TextLabel({})
    self.assertEqual(lab_default.x, 10)
    self.assertEqual(lab_default.y, 10)
    self.assertEqual(lab_default.width, 40000)
    self.assertEqual(lab_default.height, 40000)
    self.assertEqual(lab_default.color, "#000000")
    self.assertEqual(lab_default.source, "text.txt")
    self.assertEqual(lab_default.fontface, "sans")
    self.assertEqual(lab_default.fontsize, 12)
    self.assertEqual(lab_default.fontweight, sysfont.STYLE_NORMAL)
    self.assertEqual(lab_default.spacing, 4)
    self.assertEqual(lab_default.justify, "left")
    self.assertEqual(lab_default.rotation, 0)
    self.assertEqual(lab_default.wordwrap, True)
    self.assertEqual(lab_default.y_align, "top")

    # This one overrides every possible setting
    dic = {
      "source": "phrases.txt",
      "x": 20,
      "y": 30,
      "width": 300,
      "height": 200,
      "color": "#DEADBE",
      "font-face": "courier new",
      "font-size": 32,
      "font-weight": "bold",
      "line-spacing": 12,
      "justify": "center",
      "rotation": 90,
      "wordwrap": False,
      "x-align": "right",
      "y-align": "bottom"
    }

    lab_override = TextLabel(dic)

    self.assertEqual(lab_override.source, dic["source"])
    self.assertEqual(lab_override.x, dic["x"])
    self.assertEqual(lab_override.y, dic["y"])
    self.assertEqual(lab_override.width, dic["width"])
    self.assertEqual(lab_override.height, dic["height"])
    self.assertEqual(lab_override.color, dic["color"])
    self.assertEqual(lab_override.fontface, dic["font-face"])
    self.assertEqual(lab_override.fontsize, dic["font-size"])
    self.assertEqual(lab_override.fontweight, sysfont.STYLE_BOLD)
    self.assertEqual(lab_override.spacing, dic["line-spacing"])
    self.assertEqual(lab_override.justify, dic["justify"])
    self.assertEqual(lab_override.rotation, dic["rotation"])
    self.assertEqual(lab_override.wordwrap, dic["wordwrap"])
    self.assertEqual(lab_override.x_align, dic["x-align"])
    self.assertEqual(lab_override.y_align, dic["y-align"])

  def test_render_text(self):
    lab_default = TextLabel({ "color": "#AABBCC" })
    layer = lab_default.render((100, 30), "Hello")
    self.assertEqual(layer.width, 100)
    self.assertEqual(layer.height, 30)
    # There are some transparent pixels and some of the text color. Good enough.
    self.assertEqual(layer.getextrema(), ((0, 0xAA), (0, 0xBB), (0, 0xCC), (0, 255)))

  # TODO: Test text wrapping

if __name__ == '__main__':
    unittest.main()

