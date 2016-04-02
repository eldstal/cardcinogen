# cardcinogen
A deck generator for Tabletop Simulator, allowing users to create expansions
for word-card-type games.

## Requirements
python3, pillow (install with pip)

## Supported Games
Any game with cards that are identical in style but unique in text.

The original purpose of the script was to generate expansions for the game
Concept (http://boardgamegeek.com/boardgame/147151/concept), but it also works
for Cards Against Humanity and any other game with the same type of unique-text
cards.

Templates are included for Concept and CaH in the corresponding directories.

## Defining a deck
A deck is a collection of unique cards, which will generate one or more large
image maps of card faces.  A deck is specified by creating a directory (whose
name is the name of the deck) containing a set of text files.

Each line of text in each text file is treated as a possible label for a text
field on a card. Each line will only ever appear on one card in the finished
deck. Any occurrence of the characters "\n" in a line will be replaced by an
explicit linebreak

If a card (see later section) uses text from multiple files, the generator will
only generate cards while there are text lines available in all used text
files. For example, if we create `phrases.txt` with 40 lines of text and
`quotes.txt` with 38 lines of text, there will only be 38 cards containing one
of each.

## Designing a card
The card layout (which is identical for all cards in the deck) is specified
using three images (front, hidden and back) and a JSON file which defines the
dynamic aspects of the card.

The format of the JSON file is as follows:
```json
{
    "back-image": "back.jpeg",
    "front-image": "front.jpeg",
    "hidden-image": "hidden.jpeg",
    "text-labels": [
        {
            "source": "phrases.txt",
            "x": "20",
            "y": "35",
            "color": "#ff0000",
            "font-face": "Sans Serif",
            "font-size": 12,
            "font-weight": "regular"
        },
        
        {
            "source": "quotes.txt",
            "x": "20",
            "y": "50",
        }
    ]
}
```

The example above defines cards with two pieces of text on each card.
The first text is taken from the file `phrases.txt` and the second is from `quotes.txt`.
Both of these files must be present in the deck directory.

The size of the cards will be equal to the size of the front-image.  The x, y,
for each text label are specified in pixels, defining the top-left corner of
the text label from the top-left corner of the card.


## Invocation
When you have a card design (the JSON file and images) and a deck (a named
directory with text files in it), you can generate the deck grid for Tabletop
Sim by invoking the script.  Let's say I've come up with a set of new white
cards with animal themes for CaH, written a JSON file (`cah-white.json`) and
created the deck directory (`cah-animals/`) with a text file in it.

```bash
$ Cardcinogen.py --template cards-against-humanity/cah-white.json --deck cards-against-humanity/animals --output cah_animal_deck_
```

The script will generate one or more jpeg images (there can be a maximum of 69
cards per image) named `cah_animal_deck_01.jpg`, `cah_animal_deck_02.jpg`, and
so on.

These images can be imported as decks in Tabletop Sim.  Please note that the
generated tiled images only contain the card faces and the "hidden card" face,
and not the card back. Make sure you also have a back image that is the same
size as the front, because you will need it to generate a deck inside the game.



## Future features (probably not going to happen)
* Fancier font stuff, such as centered text
* Two-sided cards, such as in Trivial Pursuit



# Acknowledgements
Uses sysfont from python-utils (https://bitbucket.org/marcusva/python-utils)

