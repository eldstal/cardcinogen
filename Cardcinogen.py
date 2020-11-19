#!/usr/bin/env python3

import os
import sys
import json

import argparse

from PIL import Image

import log
from card import CardTemplate
from content import ContentGenerator
from tiler import CardTiler

def generate(template, deck, output_prefix):
  template_dir = os.path.dirname(template.name)

  if (not os.path.isdir(deck)):
    log.log.write("Supplied --deck is not a directory.")
    return 1

  if (output_prefix == ""):
    # Generate a nice default name for the output images
    template_name = os.path.splitext(os.path.basename(template.name))[0]
    deck_name = os.path.basename(deck)
    output_prefix = template_name + "_" + deck_name + "_"

  # Keeps track of the next piece of text in each opened file.
  textgen = ContentGenerator(deck)

  # Load the JSON template
  try:
    spec = json.load(template)
  except ValueError as e:
    log.log.write("JSON error in %s: %s\n" % (template.name, e))
    return 2

  # Generates card fronts
  tmpl = CardTemplate(spec, template_dir)

  cards = []
  while (True):
    face = tmpl.make_card(textgen)
    if (face is None): break
    cards.append(face)

  log.log.write("Generated %d cards.\n" % len(cards))

  tiler = CardTiler()
  tilings = tiler.tile(cards, tmpl.hidden)

  serial = 1
  for img in tilings:
    filename = output_prefix + str(serial).zfill(2) + ".png"
    img.save(filename)
    serial += 1


def main():

  parser = argparse.ArgumentParser(description="Generate decks for Tabletop Simulator")

  parser.add_argument("--template", "-t", default=None, type=argparse.FileType('r', encoding="utf-8-sig"),
                      help="A JSON file defining the layout of each card.")

  parser.add_argument("--deck", "-d", default=None,
                      help="A directory with text files, as named in the JSON template")

  parser.add_argument("--output-prefix", "-o", metavar="output_prefix", default="",
                      help="Name prefix for the generated deck JPEGs. A serial number will be appended. By default, will contain the template name and the deck name.")

  conf = parser.parse_args()

  if (conf.template is None and
      conf.deck is None and
      conf.output_prefix == ""):
    # No options specified. It's probably a windows user that just invoked the EXE.
    # Show a GUI rather than a vanishing black box.
    try:
      from gui import CardGui
      gui = CardGui()
      gui.run(generate)
    except Exception as e:
      print(e)
      # If we can't show the gui, we're running in a terminal for sure. Just show usage.
      parser.print_help()
      return 2
  else:
    return generate(conf.template, conf.deck, conf.output_prefix)


if __name__ == '__main__':
  sys.exit(main())

