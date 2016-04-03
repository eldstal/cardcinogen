# cardcinogen
A deck generator for Tabletop Simulator, allowing users to create expansions
for card games.

## Requirements
python3, pillow

```
$ pip install -r requirements.txt
```

On linux, requires font-config to locate installed fonts.

The supplied templates use the Liberation Sans TTF font (https://fedorahosted.org/liberation-fonts/) and TexGyreHeros (https://www.fontsquirrel.com/fonts/tex-gyre-heros)

## Supported Games
Any game with cards that are identical in style but unique in text.

The original purpose of the script was to generate expansions for the game
Concept (http://boardgamegeek.com/boardgame/147151/concept), but it also works
for Cards Against Humanity and any other game with the same type of unique-text
cards.

Templates are included for Concept, Fluxx and CaH in the corresponding directories.

## Simple Cards
Games where cards simply have one or more random text strings on them (Concept, CaH, Charades, ...)
are supported using the "simple" deck type.

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
The card layout (which is identical for all cards in the deck) is specified
using three images (front, hidden and back) and a JSON file which defines the
dynamic aspects of the card.

The format of the JSON file is as follows:

***factoids.json***
```json
{
    "back-image": "back.jpeg",
    "front-image": "front.jpeg",
    "hidden-image": "hidden.jpeg",
    "text-labels": [
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
            "alignment": "right",
            "baseline": "center",
            "line-spacing": 4
        },
        
        {
            "source": "history.txt",
            "x": 20,
            "y": 50,
        }
    ]
}
```

The example above defines cards with two pieces of text on each card.
The first text is taken from the file `music.txt` and the second is from `history.txt`.
Both of these files must be present in the deck directory.

The size of the cards will be equal to the size of the front-image.

The x value of a label determines its horizontal position. If the alignment is
"left" (default), this is the left-hand edge of the text. If the alignment is "center"
 or "right", the x-coordinate determines the center line and the right-hand edge respectively.

The y value works the same way, with the baseline being "top" (top edge of text), "center"
(vertical centering) or "bottom" (the bottom edge of text).

These positions are relative to the top-left corner of the card.

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
  "front-image": "quiz_front.jpg",
  "hidden-image": "quiz_hidden.jpg",
  "layout": [
    {
      "source": "questions.json",
      "type": "complex",
      "front": "quiz_front.jpg",
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
labels in a complex layut.


## Invocation
When you have a card design (the JSON file and images) and a deck (a named
directory with text files in it), you can generate the deck grid for Tabletop
Sim by invoking the script.  Let's say I've come up with a set of new white
cards with animal themes for CaH, written a JSON file (`cah-white.json`) and
created the deck directory (`cah-animals/`) with a text file in it.

```bash
$ Cardcinogen.py --template cards-against-humanity/cah-white.json --deck cards-against-humanity/animals --output-prefix cah_animal_deck_
```

The script will generate one or more jpeg images (there can be a maximum of 69
cards per image) named `cah_animal_deck_01.jpeg`, `cah_animal_deck_02.jpeg`, and
so on.

These images can be imported as decks in Tabletop Sim.  Please note that the
generated tiled images only contain the card faces and the "hidden card" face,
and not the card back. Make sure you also have a back image that is the same
size as the front, because you will need it to generate a deck inside the game.



## Future features (probably not going to happen)
* Two-sided cards, such as in Trivial Pursuit



# Acknowledgements
Uses sysfont from python-utils (https://bitbucket.org/marcusva/python-utils)

