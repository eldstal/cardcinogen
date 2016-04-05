#!/bin/env python3

import os
import sys
import json

import argparse

from PIL import Image

from card import CardTemplate
from content import ContentGenerator
from tiler import CardTiler

def main():

  parser = argparse.ArgumentParser(description="Generate decks for Tabletop Simulator")

  parser.add_argument("--template", "-t", required=True, type=argparse.FileType('r'),
                      help="A JSON file defining the layout of each card.")

  parser.add_argument("--deck", "-d", required=True,
                      help="A directory with text files, as named in the JSON template")

  parser.add_argument("--output-prefix", "-o", metavar="output_prefix", default="",
                      help="Name prefix for the generated deck JPEGs. A serial number will be appended. By default, will contain the template name and the deck name.")

  conf = parser.parse_args()

  template_dir = os.path.dirname(conf.template.name)

  if (not os.path.isdir(conf.deck)):
    sys.stderr.write("Supplied --deck is not a directory.")
    return 1

  if (conf.output_prefix == ""):
    # Generate a nice default name for the output images
    template_name = os.path.splitext(os.path.basename(conf.template.name))[0]
    deck_name = os.path.basename(conf.deck)
    conf.output_prefix = template_name + "_" + deck_name + "_"

  # Keeps track of the next piece of text in each opened file.
  textgen = ContentGenerator(conf.deck)

  # Load the JSON template
  try:
    spec = json.load(conf.template)
  except ValueError as e:
    sys.stderr.write("JSON error in %s: %s\n" % (conf.template.name, e))
    return 2

  # Generates card fronts
  tmpl = CardTemplate(spec, template_dir)

  cards = []
  while (True):
    face = tmpl.make_card(textgen)
    if (face is None): break
    cards.append(face)

  print("Generated %d cards." % len(cards))

  tiler = CardTiler()
  tilings = tiler.tile(cards, tmpl.hidden)

  serial = 1
  for img in tilings:
    filename = conf.output_prefix + str(serial).zfill(2) + ".png"
    img.save(filename)
    serial += 1



if __name__ == '__main__':
  sys.exit(main())

