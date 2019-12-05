import numpy as np
import random
from collections import defaultdict
import matplotlib.pyplot as plt

def hit(your_cards, deck):
  random_draw = random.randint(0,len(deck)-1)
  next_deck = np.delete(deck, random_draw)
  your_cards.append(deck[random_draw])
  return your_cards, next_deck

def hit_q(your_cards, deck):
  random_draw = random.randint(0,len(deck)-1)
  next_deck = np.delete(deck, random_draw)
  cards = list(your_cards)
  cards[deck[random_draw] - 1] += 1
  your_cards = tuple(cards)
  return your_cards, next_deck, deck[random_draw]

def calc_score(total):
  if total > 21:
    return 0
  else:
    return total

def init(deck):
  s = (0, 0, 0, 0, 0, 0, 0, 0, 0, 0)
  for i in range(2):
    s, deck, _ = hit_q(s, deck)
  return s, deck

def qlearning(deck, reward, alpha=0.5, gamma=0.95):
  q = [defaultdict(int) for i in range(2)]
  s, curr_d = init(deck)
  game_score = []
  for iteration in range(5000):
      if(np.random.rand() < 0.8):
        if(q[0][s] > q[1][s]):
          a = 0
        else:
          a = 1
      else:
        a = np.random.choice(1)

      if(a == 1):
        s_new, curr_d, r = hit_q(s, curr_d)
        sc = sum([(i + 1) * s_new[i] for i in range(10)])
        #q[a][s] += alpha * (0 + gamma * (max(q[0][s_new], q[1][s_new]) - q[a][s]))
        if(sc <= 21):
          q[a][s] += alpha * (r + gamma * (max(q[0][s_new], q[1][s_new]) - q[a][s]))
          s = s_new
        else:
          q[a][s] += alpha * (-reward + gamma * (max(q[0][s_new], q[1][s_new]) - q[a][s]))
          game_score.append(0)
          s, curr_d = init(deck)
      else:
        sc = sum([(i + 1) * s[i] for i in range(10)])
        if(s[0] > 0 and sc + 10 <= 21):
          q[a][s] += alpha * 10
          sc += 10
        game_score.append(sc)
        s, curr_d = init(deck)

  policy = defaultdict(int)
  for s in q[0]:
    if(q[0][s] > q[1][s]):
      policy[s] = 0
    else:
      policy[s] = 1

  game_avg = []
  for i in range(len(game_score) // 10):
    avg = 0
    for j in range(10):
      avg += game_score[i * 10 + j]
    avg /= 10
    game_avg.append(avg)

  plt.scatter([i for i in range(len(game_score) // 10)], game_avg)
  plt.xlabel('Game Numbers (per 10)')
  plt.ylabel('Score')
  plt.title('Q-Learning Scores while Learning')
  plt.savefig('game_scores.png')

  return policy

def main():

  # Initial Deck
  suite = np.concatenate((np.arange(1,10),np.ones(4)*10))
  deck = np.repeat(suite, 4).astype(int)

  # Dictionary of cards left
  your_cards = (0, 0, 0, 0, 0, 0, 0, 0, 0, 0)
  game_over = False
  score = 0

  #Q-Learning
  rewards = [i for i in range(6)]
  scores = []
  for reward in rewards:
    policy = qlearning(deck, reward)
    for i in range(1000):
      s, curr_d = init(deck)
      while(policy[s] == 1):
        s, curr_d, _ = hit_q(s, curr_d)
        sc = sum([(i + 1) * s[i] for i in range(10)])
        if(sc > 21):
          break

      sc = sum([(i + 1) * s[i] for i in range(10)])
      if(s[0] > 0 and sc + 10 <= 21):
        sc += 10
      score += calc_score(sc)

    score /= 1000
    # Final Payoff
    print("Your Score:",score)
    scores.append(score)

  plt.figure()
  plt.bar(rewards, scores)
  plt.xlabel('Reward Values')
  plt.ylabel('Scores')
  plt.title('Expected Scores for Q-Learning Per Reward Values')
  plt.savefig('rewards.png')

if __name__ == '__main__':
  main()
