import numpy as np
import random

def hit(your_cards, deck):
  random_draw = random.randint(0,len(deck)-1)
  next_deck = np.delete(deck, random_draw)
  your_cards.append(deck[random_draw])
  return your_cards, next_deck

def calc_score(total):
  if total > 21:
    return 0
  else:
    return total

def main():

  # Initial Deck
  suite = np.concatenate((np.arange(1,10),np.ones(4)*10))
  deck = np.repeat(suite, 4).astype(int)

  # Dictionary of cards left
  your_cards = []
  game_over = False
  score = 0

  # Play Game
  while (not game_over):
    print("\nYour cards:")
    print(your_cards)
    action = input("Hit or Stick? (1) for Hit, (2) for Stick: ")
    if action == "1" or action == "2":
      action = int(action)
      if action == 1:
        your_cards, deck = hit(your_cards, deck)
        if sum(your_cards) > 21:
          print("\nYour cards:")
          print(your_cards)
          score = 0
          game_over = True
      if action == 2:
        if 1 in your_cards:
          score = np.maximum(calc_score(sum(your_cards) + 10), calc_score(sum(your_cards)))
        else:
          score = calc_score(sum(your_cards))
        game_over = True
    else:
      print("Action Not Recognized!")

  # Final Payoff
  print("Your Score:",score)

if __name__ == '__main__':
  main()
