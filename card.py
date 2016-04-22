#!/bin/env python3
import unittest

import os
import sys

import util
import log

from PIL import Image
from layout import SimpleLayout, ComplexLayout



class CardTemplate:
  """ Parsed version of a JSON card template """
  def __init__(self, json, rootdir="."):
    self.front_name =   util.get_default(json, "front-image", "front.png")
    self.hidden_name =  util.get_default(json, "hidden-image", "hidden.png")

    self.layouts = []
    for j in util.get_default(json, "layouts", []):
      self.type = util.get_default(j, "type", "simple")
      if (self.type == "complex"):
        self.layouts.append(ComplexLayout(j, rootdir))
      else:
        self.layouts.append(SimpleLayout(j, rootdir))

    front_path  = os.path.join(rootdir, self.front_name)
    hidden_path = os.path.join(rootdir, self.hidden_name)

    # Make sure we have valid images and they all have matching sizes
    self.front   = util.default_image(front_path, (372, 520))
    self.hidden  = util.default_image(hidden_path, self.front.size, self.front.size)

  def make_card(self, textgen):
    """ Generate a single card """

    if (len(self.layouts) == 0):
      log.log.write("Warning: No layouts specified.")
      return None

    face = self.front.copy()
    for l in self.layouts:

      overlay = l.render(face.size, textgen)
      if (overlay is None):
        # This layout is done generating cards.
        # This happens when, eventually, textgen runs out of card texts for a given layout.
        continue

      # We have a card! Return it and that's that.
      face.paste(overlay, mask=overlay)
      return face

    # None of the layouts can generate any cards. We're done.
    return None



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

