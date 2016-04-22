from tkinter import *
from tkinter.filedialog import *

import os

import log

class CardGui:
  """ A simple GUI for users who don't use the command line options """

  def invoke(self):
    try:
      template = open(self.template.get(), 'r')
      self.generator(template=template,
                     deck=self.deck.get(),
                     output_prefix=self.prefix.get())
    except Exception as e:
      log.log.write("Error: %s\n" % e)

  def setTemplate(self):
    # Button was pressed. Select a JSON file.
    directory = os.path.dirname(__file__)

    # Since the deck is usually in the same directory as the template,
    # let's suggest that.
    deck = self.deck.get()
    if (os.path.isdir(deck)):
      directory = os.path.dirname(deck)

    path = askopenfilename(title="Select card layout template",
                           initialdir=directory,
                           filetypes=[("JSON template", ".json")]
                          )
    self.template.set(path)

  def setDeck(self):
    # Button was pressed. Select a Deck directory
    directory = os.path.dirname(__file__)

    # Since the deck is usually in the same directory as the template,
    # let's suggest that.
    template = self.template.get()
    if (os.path.isfile(template)):
      directory = os.path.dirname(template)

    path = askdirectory(title="Select deck data directory", initialdir=directory)
    self.deck.set(path)
    pass

  def write(self, string):
    # Write something to the log window
    self.log.config(state=NORMAL)
    self.log.insert(END, string)
    self.log.config(state=DISABLED)

  def run(self, generator_function):

    self.generator = generator_function

    self.win = Tk()
    self.win.grid_columnconfigure(1, weight=1)

    self.win.wm_title("Cardcinogen")

    self.template = StringVar()
    self.deck = StringVar()
    self.prefix = StringVar()


    Label(self.win, text="Card template:").grid(row=0, column=0, sticky=E)
    self.txtTemplate = Entry(self.win, textvariable=self.template).grid(row=0, column=1, sticky=E+W)
    self.btnTemplate = Button(self.win, text="...", command=self.setTemplate).grid(row=0, column=2)

    Label(self.win, text="Deck data:").grid(row=1, column=0, sticky=E)
    self.txtDeck = Entry(self.win, textvariable=self.deck).grid(row=1, column=1, sticky=E+W)
    self.btnDeck = Button(self.win, text="...", command=self.setDeck).grid(row=1, column=2)

    Label(self.win, text="Output file prefix:").grid(row=2, column=0, sticky=E)
    self.txtDeck = Entry(self.win, textvariable=self.prefix).grid(row=2, column=1, sticky=E+W)

    self.btnGenerate = Button(self.win, text="Generate!", command=self.invoke).grid(row=3, column=0, columnspan=3, sticky=E+W)

    self.log = Text(self.win)
    self.log.grid(row=4, column=0, columnspan=3, sticky=N+S+E+W)
    self.log.config(state=DISABLED)

    log.setlog(self)

    return self.win.mainloop()

