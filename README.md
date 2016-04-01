# cardcinogen
A deck generator for Tabletop Simulator, allowing users to create expansions for word-card-type games.

## Supported Games
Any game with cards that are identical in style but unique in text.

## Defining a deck
A deck is a collection of unique cards, which will generate one or more large image maps of card faces.
A deck is specified by creating a directory (whose name is the name of the deck) containing a set of text files.

Each line of text in each text file is treated as a possible label for a text field on a card. Each line will only
ever appear on one card in the finished deck.

If a card (see later section) uses text from multiple files, the generator will only generate cards while there are
text lines available in all used text files. For example, if we create `phrases.txt` with 40 lines of text and
`quotes.txt` with 38 lines of text, there will only be 38 cards containing one of each.

## Designing a card
The card layout (which is identical for all cards in the deck) is specified using three images (front, hidden and back) and a JSON
file which defines the dynamic aspects of the card.

The format of the JSON file is as follows:
```json
{
    "back-image": "card-back.jpeg",
    "front-image": "card-front.jpeg",
    "hidden-image": "card-hidden.jpeg",
    "layout": {
        "text-labels": [
            {
                "source": "phrases.txt",
                "x": "10%",
                "y": "15%",
                "width": "80%",
                "height": "5%",
                "font-face": "Sans Serif",
                "font-size": 12,
                "font-weight": "regular"
            },
            
            {
                "source": "quotes.txt",
                "x": "10%",
                "y": "-",
                "width": "80%"
            }
        ]
    }
}
```

The example above defines cards with two pieces of text on each card.
The first text is taken from the file `phrases.txt` and the second is from `quotes.txt`.
Both of these files must be present in the deck directory.

The size of the cards will be equal to the size of the front-image.
The x, y, width and height values for each text label can be specified as a percentage (of the card size) or as an absolute pixel distance. Negative values are counted from the opposite card edge (right or bottom).


## Invocation
When you have a card design (the JSON file and images) and a deck (a named directory with text files in it), you can generate the deck grid for Tabletop Sim by invoking the script.
Let's say I've come up with a set of new white cards with animal themes for CaH, written a JSON file (`cah-white.json`) and created the deck directory (`cah-animals/`) with a text file in it.

```bash
$ cardcinogen.py --template cah-white.json --deck cah-animals --output cah_animal_deck
```

The script will generate one or more jpeg images (there can be a maximum of 69 cards per image) named `cah_animal_deck_01.jpg`, `cah_animal_deck_02.jpg`, and so on.

These images can be imported as decks in Tabletop Sim.
