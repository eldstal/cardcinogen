# cardcinogen
A deck generator for Tabletop Simulator, allowing users to create expansions
for card games.

## Requirements
python3, pillow

```
$ pip install -r requirements.txt
```

On linux, requires font-config to locate installed fonts.

The supplied templates use
* Liberation Sans and Liberation Serif TTF fonts (https://fedorahosted.org/liberation-fonts/)
* TexGyreHeros (https://www.fontsquirrel.com/fonts/tex-gyre-heros)

## Supported Games
Any game with cards that are identical in style but unique in text.

The original purpose of the script was to generate expansions for the game
Concept (http://boardgamegeek.com/boardgame/147151/concept), but it also works
for Cards Against Humanity and any other game with the same type of unique-text
cards.

Templates are included for Concept, Fluxx and CaH in the corresponding directories.

## Simple Cards
Games where cards simply have one or more random text strings on them (Concept, CaH, Charades, ...)
are supported using the "simple" layout type.

### Defining a deck
A deck is a collection of unique cards, which will generate one or more large
image maps of card faces.  A deck is specified by creating a directory (whose
name is the name of the deck) containing a set of text files.

Each line of text in each text file is treated as a possible label for a text
field on a card. Each line will only ever appear on one card in the finished
deck. Any occurrence of the characters "\n" in a line will be replaced by an
explicit linebreak

If a card (see later section) uses text from multiple files, the generator will
only generate cards while there are text lines available in all used text
files. For example, if we create `music.txt` with 40 music facts and
`history.txt` with 38 history facts, there will only be 38 cards containing one
of each.

***facts/music.txt***
```
A typical guitar has six strings, but there are varieties with up to 89 strings!
Nobody has ever heard an invisible harpsichord.
```

### Designing a card
The card layout is specified using two images (front, hidden) and a JSON structure
which defines the dynamic aspects of the card.

The format of the JSON file is as follows:

***factoids.json***
```json
{
    "back-image": "back.jpeg",
    "front-image": "front.jpeg",
    "hidden-image": "hidden.jpeg",
    "layouts": [
        {
            "texts": [
                {
                    "source": "music.txt",
                    "x": 20,
                    "y": 35,
                    "width": 180,
                    "height": 300,
                    "color": "#ff0000",
                    "font-face": "Liberty Sans",
                    "font-size": 12,
                    "font-weight": "regular",
                    "justify": "center",
                    "x-align": "center",
                    "y-align": "bottom",
                    "line-spacing": 4
                },
                
                {
                    "source": "history.txt",
                    "x": 20,
                    "y": 50,
                    "rotation": 4
                }
            ]
        }
    ]
}
```

The example above defines cards with two pieces of text on each card.
The first text is taken from the file `music.txt` and the second is from `history.txt`.
Both of these files must be present in the deck directory.

The size of the cards will be equal to the size of the front-image.

The x value of a label determines its horizontal position. If the x-align is
"left" (default), this is the left-hand edge of the text. If the x-align is "center"
 or "right", the x-coordinate determines the center line and the right-hand edge respectively.

The y value works the same way, with the "y-align" property being "top" (top edge of text), "center"
(vertical centering) or "bottom" (the bottom edge of text).

These positions are relative to the top-left corner of the card.

The "justify" property ("left", "center" or "right") determines how lines of text are
rendered. Note that this does NOT affect the placement of the label. Typically, if you
are using "justify":"center", you also want "x-align":"center".

All label properties are optional.

## Complex Cards
Games where each card has multiple text labels, which are related to each other, are supported
using the "complex" deck type.

In these decks, the text for each card is also specified in JSON format, with named labels and
their content text.

The card template defines the layout of these named labels on each card.

For a working example of a complex layout, see ```fluxx/```

### Defining a Deck
For a simple quiz-type game, we might have cards with a Question and an Answer field on them.
We define our cards in pairs of question and answer in a JSON file in the deck directory.

***music/questions.json***
```json
[
  {
    "question": "What singer famously covered Paul Anka's \"Puppy Love\" in 1972?",
    "answer": "Donny Osmond"
  },

  {
    "question": "What was the title of the 1978 musical comedy starring Donny and Marie Osmond?",
    "answer": "Goin' Coconuts"
  }
]

```

This deck would generate two cards, with one question and one answer on each.

### Designing a card

The layout of a card with a JSON source is specified as follows:

**quiz.json**
```json
{
  "front-image": "quiz_front.png",
  "hidden-image": "quiz_hidden.png",
  "layouts": [
    {
      "source": "questions.json",
      "type": "complex",
      "front-image": "question_front.png",
      "texts": [
        {
          "name": "question",
          "x": 32,
          "y": 80,
          "font-size": 36
        },
        {
          "name": "answer",
          "x": 32,
          "y": 80,
          "font-weight": "italic"
        },
      ]
    }

  ]
}
```

Note that the "name" field correlates to the deck file. Each "question" field
on a card will be filled with a question from ```questions.json``` and the
"answer" field on the same card will hold the corresponding answer.

Any options that are valid for the simple text labels are also valid for the
labels in a complex layout.

## Multi-layout card games
Games like Fluxx have multiple types of card, with different designs.
For such games, it is possible to define multiple layouts in the same JSON file.
We note that the "layouts" field is a list - each object in the list is a separate
card layout (either simple or complex). The generator will create as many cards
as possible for each layout (continuing until there isn't content for any more cards)
and put them in the same deck grid.

For an example of how this works, look at ```fluxx/fluxx.json```.

Each of the layouts has its own "front-image" directive, giving each card layout its
own custom background. If a global front-image is also included at the top-level,
this is drawn at the bottom of all cards. PNGs with transparency are supported,
allowing the per-layout image to composite with the global front-image.


## Images on cards
Both the "simple" and "complex" layout supports images loaded from the deck directory
and placed on the card. This is done with the "images" list, which is specified much
like the "texts" list in either layout.

```json
{
  "front-image": "card_front.png",
  "hidden-image": "card_hidden.png",
  "layouts": [
    {
      "source": "famous_people.json",
      "type": "complex",
      "front-image": "people_front.png",
      "texts": [
        {
          "name": "person",
          "x": 32,
          "y": 80,
          "font-size": 36
        }
      ],
      "images": [
        {
          "name": "face",
          "x": 32,
          "y": 80,
          "width": 400,
        },
        {
          "name": "logo",
          "static": "question_mark.png"
          "x": 100,
          "y": 10,
          "x-align": "right",
          "y-align": "top",
          "width": 400,
        }
      ]
    }

  ]
}

```

Image labels support the same placement, alignment and rotation options as text labels.

If either "width" or "height" is specified, the image is scaled proportionally to fit the
specified size. If both are specified, the image is stretched to fit these dimensions.

In the complex layout, the image's "name" property is used in the deck JSON file to
specify the filename of the image used on each individual card:

```deck/famous_people.json```
```json
[
  {
    "person": "Donny Osmond",
    "face": "donny.jpg"
  },
  {
    "person": "Priscilla Presley",
    "face": "priscilla.jpg"
  },
]
```

These image files are located in the deck directory.

If an image is present in the layout but not specified on the card, the image is not included
in the layout. This is not an error in the design - some cards might simply not need an image there.

If the image filename is the same for all cards using the layout, it can be set in the image label's "static" property, as illustrated above. Notice that none of the cards in the deck actually specifies a "logo" field - that image is static.

In the simple layout each image label has a "source" text file just like the text labels. Each line in this file is the filename of an image and these are used sequentially just like the texts.

## Invocation
When you have a card design (the JSON file and images) and a deck (a named
directory with text files and images in it), you can generate the deck grid for Tabletop
Sim by invoking the script.  Let's say I've come up with a set of cards with
animal themes for Fluxx, written a JSON file (`fluxx.json`) and created the
deck directory (`animals/`) with card contents.

```bash
$ Cardcinogen.py --template fluxx/fluxx.json --deck fluxx/cards
```

The script will generate one or more jpeg images (there can be a maximum of 69
cards per image) named `fluxx_cards_01.png`, `fluxx_cards_02.png`, and
so on.

These images can be imported as decks in Tabletop Sim.  Please note that the
generated tiled images only contain the card faces and the "hidden card" face,
and not the card back. Make sure you also have a back image that is the same
size as the front, because you will need it to generate a deck inside the game.



## Future features (probably not going to happen)
* Two-sided cards, such as in Trivial Pursuit



# Acknowledgements
Uses sysfont from python-utils (https://bitbucket.org/marcusva/python-utils)

