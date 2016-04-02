#!/bin/env python3

import os
import json

from PIL import Image

from text import TextLabel, TextGenerator
from card import CardTemplate

def main():

  template_file = os.path.join("cards-against-humanity", "cah-white.json")
  deck_path = os.path.join("cards-against-humanity", "animals")

  # Keeps track of the next piece of text in each opened file.
  textgen = TextGenerator(deck_path)

  template_dir = os.path.dirname(template_file)

  fp = open(template_file, "r")
  if (template_file is None):
    sys.stderr.write("Unable to open card template %s\n" % template_file)

  spec = json.load(fp)

  print(spec)

  tmpl = CardTemplate(spec, template_dir)

  img = tmpl.make_card(textgen)

  img.save("debug.png")


if __name__ == '__main__':
  main()

