import os
import sys

from PIL import Image

from text import TextLabel
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


  def render(self, dimensions, textgen):
    """ Render a PIL image of the specified dimensions, requesting texts from the textgen """

    image = Image.new("RGBA", dimensions, (0,0,0,0))
    if (self.front is not None):
      image.paste(self.front, (0,0))

    return image

class SimpleLayout(CardLayout):
  """ Parsed version of a simple layout (uses text lines as deck input) """

  def __init__(self, json, rootdir):
    super().__init__(json, rootdir)
    self.textspecs = util.get_default(json, "texts", [])

    # Initialize plain text labels, to be rendered when we have text
    self.textlabels = []
    for spec in self.textspecs:
      self.textlabels.append(TextLabel(spec))


  def render(self, dimensions, textgen):
    """ Generate a transparent PIL card layer with the text on it """

    # The static card face
    image = super().render(dimensions, textgen)

    if (len(self.textlabels) == 0):
      sys.stderr.write("Warning: No labels in layout.")
      return None

    for label in self.textlabels:
      rendered_text = None

      # Some text strings may fail to render (not fit within the label boundary).
      # Those will be rendered as None, so we draw a new text string and try again.
      while (rendered_text is None):
        text = textgen.gen_simple(label.source)
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

    # Initialize plain text labels, to be rendered when we have text
    self.textlabels = {}
    for spec in self.textspecs:
      name = util.get_default(spec, "name", "")
      self.textlabels[name] = TextLabel(spec)

  def try_render_labels(self, dimensions, texts):
    image = Image.new("RGBA", dimensions, (0,0,0,0))

    for name,label in self.textlabels.items():

      text  = util.get_default(texts, name, "")

      rendered_text = label.render(dimensions, text)
      if (rendered_text is None):
        sys.stderr.write("Failed to render sub-label %s.\n" % name)
        rendered_labels = None
        return None

      image.paste(rendered_text, (0, 0), mask=rendered_text)
    return image

  def render(self, dimensions, textgen):
    """ Generate a transparent PIL card layer with the text on it """

    if (len(self.textlabels) == 0):
      sys.stderr.write("Warning: No labels in layout.")
      return None

    # The static card face
    image = super().render(dimensions, textgen)

    # Some text strings may fail to render (not fit within the label boundary).
    # Those will be rendered as None, so we draw a new set of text strings and try again.
    rendered_labels = None
    while (rendered_labels is None):
      texts = textgen.gen_complex(self.source)
      if (texts is None):
        # End of file
        return None
      rendered_labels = self.try_render_labels(dimensions, texts)

    image.paste(rendered_labels, (0,0), mask=rendered_labels)

    return image

