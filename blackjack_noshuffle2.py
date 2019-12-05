import numpy as np
import random
from collections import defaultdict
import matplotlib.pyplot as plt

def hit(your_cards, deck):
    random_draw = random.randint(0,len(deck)-1)
    next_deck = np.delete(deck, random_draw)
    your_cards.append(deck[random_draw])
    return your_cards, next_deck

def gen_initial_deck():
    # Initial Deck
    suite = np.concatenate((np.arange(1,10),np.ones(4)*10))
    deck = np.repeat(suite, 4).astype(int)
    return deck

# TODO
def hit_q(your_cards, deck):
    if len(deck) == 0: # run out of cards
        # generate new deck
        deck = gen_initial_deck()
        #print('generated new deck: ', deck)
        # remove your current cards from this deck
        #print('you currently have the cards: ', your_cards)
        i = 0
        for card in your_cards:
            #print('card: ',card)
            for card_occurrence in range(card):
                #print('removed', i)
                deck = np.delete(deck, np.argmax(deck==(i+1)))
            i += 1
            
        #print('new deck after removal: ', deck)

    random_draw = random.randint(0,len(deck)-1) # draw random card from deck
    next_deck = np.delete(deck, random_draw) # delete card from deck
    cards = list(your_cards)
    cards[deck[random_draw] - 1] += 1 # add drawn card to your cards
    your_cards = tuple(cards)

    return your_cards, next_deck, deck[random_draw] # return your cards, modified deck, the randomly drawn card

def calc_score(total):
    if total > 21:
        return 0
    else:
        return total

def init(deck):
    s = (0, 0, 0, 0, 0, 0, 0, 0, 0, 0)
    for i in range(2): # initially, hit twice
        s, deck, _ = hit_q(s, deck)
    return s, deck

def qlearning(deck, alpha=0.5, gamma=0.95):
    q = [defaultdict(int) for i in range(2)]
    s, curr_d = init(deck)
    game_score = []
    for iteration in range(50000):
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
                    q[a][s] += alpha * (-sc + gamma * (max(q[0][s_new], q[1][s_new]) - q[a][s]))
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

    deck = gen_initial_deck()

    # Dictionary of cards left
    your_cards = (0, 0, 0, 0, 0, 0, 0, 0, 0, 0)
    game_over = False
    score = 0

    #Q-Learning
    policy = qlearning(deck)
    """
    for p in policy:
        if(policy[p] == 0):
            if(sum([(i + 1) * p[i] for i in range(10)]) < 12):
                print(p, sum([(i + 1) * p[i] for i in range(10)]))
    """
    persistent_curr_d = []
    for i in range(1000):
        
        if i == 0: # use initial deck on first round
            s, curr_d = init(deck)
        else: # use existing deck
            s, curr_d = init(persistent_curr_d)
        while(policy[s] == 1):
            s, curr_d, _ = hit_q(s, curr_d) # hitq(your_cards, deck)
            sc = sum([(i + 1) * s[i] for i in range(10)])
            if(sc > 21):
                break

        sc = sum([(i + 1) * s[i] for i in range(10)])
        if(s[0] > 0 and sc + 10 <= 21):
            sc += 10
        score += calc_score(sc)
            
        persistent_curr_d = curr_d # store current deck for next round

    score /= 1000
    # Play Game
    """
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
    """

    # Final Payoff
    print("Your Score:",score)

if __name__ == '__main__':
    main()
