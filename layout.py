import os
import sys

from PIL import Image

from content import TextLabel, ImageLabel
import util


class CardLayout:

  def __init__(self, json, rootdir):
    self.type =          util.get_default(json, "type", "simple")
    self.directory = rootdir

    # Load a front image which is specific to this card layout
    front_name =  util.get_default(json, "front-image", None)
    self.front = None
    if (front_name is not None):
      front_path = os.path.join(rootdir, front_name)
      self.front = util.default_image(front_path)


  def render(self, dimensions, content_gen):
    """ Render a PIL image of the specified dimensions, requesting text and images from content_gen """

    image = Image.new("RGBA", dimensions, (0,0,0,0))
    if (self.front is not None):
      image.paste(self.front, (0,0))

    return image

class SimpleLayout(CardLayout):
  """ Parsed version of a simple layout (uses text lines as deck input) """

  def __init__(self, json, rootdir):
    super().__init__(json, rootdir)
    textspecs = util.get_default(json, "texts", [])
    imagespecs = util.get_default(json, "images", [])

    # Initialize plain text labels, to be rendered when we have text
    self.textlabels = []
    for spec in textspecs:
      self.textlabels.append(TextLabel(spec))

    # Initialize image labels, to be rendered when we have text
    self.imagelabels = []
    for spec in imagespecs:
      self.imagelabels.append(ImageLabel(spec))


  def render(self, dimensions, content_gen):
    """ Generate a transparent PIL card layer with the text on it """

    # The static card face
    image = super().render(dimensions, content_gen)

    if (len(self.textlabels) + len(self.imagelabels) == 0):
      sys.stderr.write("Warning: No text or image labels in layout.")
      return None

    for label in self.imagelabels:

      if (label.static is not None):
        # Some images have static contents.
        contents = content_gen.load_image(label.static)
      else:
        # Others load their filenames from a text file, just like text labels do
        contents = content_gen.gen_image_simple(label.source)

      # Some image failed to load or the generator is out of images.
      if (contents is None):
        return None

      rendered_image = label.render(dimensions, contents)
      image.paste(rendered_image, (0, 0), mask=rendered_image)


    for label in self.textlabels:
      rendered_text = None

      # Some text strings may fail to render (not fit within the label boundary).
      # Those will be rendered as None, so we draw a new text string and try again.
      while (rendered_text is None):

        text = content_gen.gen_text_simple(label.source)
        if (text is None):
          # End of file
          return None
        rendered_text = label.render(dimensions, text)

      image.paste(rendered_text, (0, 0), mask=rendered_text)

    return image



class ComplexLayout(CardLayout):
  """ Parsed version of a complex layout (uses JSON objects as deck input) """

  def __init__(self, json, rootdir):
    super().__init__(json, rootdir)
    self.source =        util.get_default(json, "source", "text.json")
    self.textspecs =     util.get_default(json, "texts", [])
    self.imagespecs =    util.get_default(json, "images", [])

    # Initialize plain text labels, to be rendered when we have text
    self.textlabels = {}
    for spec in self.textspecs:
      name = util.get_default(spec, "name", "")
      self.textlabels[name] = TextLabel(spec)

    self.imagelabels = {}
    for spec in self.imagespecs:
      name = util.get_default(spec, "name", "")
      self.imagelabels[name] = ImageLabel(spec)

  def try_render_labels(self, dimensions, texts, content_gen):
    image = Image.new("RGBA", dimensions, (0,0,0,0))

    for name,label in self.imagelabels.items():

      # Some layouts have a static image - doesn't depend on the card contents.
      filename = label.static
      if (filename is None):
        # This image has its source in the JSON file
        filename  = util.get_default(texts, name, None)

      if (filename is None):
        # This card doesn't specify an image - Don't render and don't complain.
        # This allows the layout to support cards with and without an optional image
        continue

      contents = content_gen.load_image(filename)

      # Some image failed to load
      if (contents is None):
        return None

      rendered_image = label.render(dimensions, contents)

      # Rendering failed for some reason
      if (rendered_image is None):
        return None

      image.paste(rendered_image, (0, 0), mask=rendered_image)

    for name,label in self.textlabels.items():

      # Some layouts have a static text for text labels,
      # use that if the card text doesn't contain
      static = ""
      if (label.static is not None):
        static = label.static

      text  = util.get_default(texts, name, static)

      rendered_text = label.render(dimensions, text)
      if (rendered_text is None):
        sys.stderr.write("Failed to render sub-label %s.\n" % name)
        rendered_labels = None
        return None

      image.paste(rendered_text, (0, 0), mask=rendered_text)

    return image

  def render(self, dimensions, content_gen):
    """ Generate a transparent PIL card layer with the text on it """

    if (len(self.textlabels) == 0):
      sys.stderr.write("Warning: No labels in layout.")
      return None

    # The static card face
    image = super().render(dimensions, content_gen)

    # Some text strings may fail to render (not fit within the label boundary).
    # Those will be rendered as None, so we draw a new set of text strings and try again.
    rendered_labels = None
    while (rendered_labels is None):
      texts = content_gen.gen_text_complex(self.source)
      if (texts is None):
        # End of file
        return None
      rendered_labels = self.try_render_labels(dimensions, texts, content_gen)

    image.paste(rendered_labels, (0,0), mask=rendered_labels)

    return image

