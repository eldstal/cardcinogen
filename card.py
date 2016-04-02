#!/bin/env python3
import unittest

import os
import sys

from util import util
from PIL import Image
from text import TextLabel

# If the loaded image is None, return a default of the specified dimensions
# If accept_dimension is specified, scale non-matching image to that size
def default_image(path, default_dimension, accept_dimension=None):
  try:
    loaded = Image.open(path)
    loaded.load()
  except:
    print(sys.exc_info()[0])
    sys.stderr.write("Unable to load image %s. Falling back to plain.\n" % path)
    return Image.new("RGBA", default_dimension, (230, 230, 255, 255))

  if (accept_dimension != None):
    if (loaded.size != accept_dimension):
      sys.stderr.write("Image sizes not matching. Resizing to %d x %d\n" % accept_dimension)
      return loaded.resize(accept_dimension, Image.BICUBIC)

  # Image is good enough as it is.
  return loaded


class CardTemplate:
  """ Parsed version of a JSON card template """
  def __init__(self, json, rootdir="."):
    self.front_name =   util.get_default(json, "front-image", "front.png")
    self.hidden_name =  util.get_default(json, "hidden-image", "hidden.png")

    self.labels = []
    for j in util.get_default(json, "layout", []):
      self.labels.append(TextLabel(j))

    front_path  = os.path.join(rootdir, self.front_name)
    hidden_path = os.path.join(rootdir, self.hidden_name)

    # Make sure we have valid images and they all have matching sizes
    self.front   = default_image(front_path, (372, 520))
    self.hidden  = default_image(hidden_path, self.front.size, self.front.size)

  def make_card(self, textgen):
    """ Generate a single card """
    face = self.front.copy()
    for l in self.labels:
      text = textgen.gen(l.source)  # A unique string for this label

      if (text is None):
        # End of file
        return None

      overlay = l.render(face.size, text)
      face.paste(im=overlay, mask=overlay)

    return face



#
# Unit tests
#
class TestCardStuff(unittest.TestCase):

  def test_default(self):
    tmpl_default = CardTemplate({})
    self.assertEqual(tmpl_default.front_name, "front.png")
    self.assertEqual(tmpl_default.hidden_name, "hidden.png")
    self.assertEqual(tmpl_default.labels, [])

    # Override all settings
    dic = {
      "front-image": "card-front.jpeg",
      "hidden-image": "card-hidden.jpeg",
      "layout": [
        {
          "x": 10
        },
        {
          "y": 20
        }
      ]
    }

    tmpl = CardTemplate(dic)
    self.assertEqual(tmpl.front_name, dic["front-image"])
    self.assertEqual(tmpl.hidden_name, dic["hidden-image"])
    self.assertEqual(len(tmpl.labels), 2)
    self.assertEqual(tmpl.labels[0].x, dic["layout"][0]["x"])
    self.assertEqual(tmpl.labels[1].y, dic["layout"][1]["y"])

if __name__ == '__main__':
    unittest.main()

