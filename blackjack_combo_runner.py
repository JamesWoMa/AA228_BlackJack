import numpy as np
import random
from collections import defaultdict
import matplotlib.pyplot as plt
import os

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
    for iteration in range(100000):
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
    n_games_avg_over = 5000
    for i in range(len(game_score) // n_games_avg_over):
        avg = 0
        for j in range(n_games_avg_over):
            avg += game_score[i * n_games_avg_over + j]
        avg /= n_games_avg_over
        game_avg.append(avg)

    plt.scatter([i for i in range(len(game_score) // n_games_avg_over)], game_avg)
    plt.xlabel('Game Numbers (per ' + str(n_games_avg_over) + ')')
    plt.ylabel('Score')
    plt.title('Q-Learning Scores while Learning')
    plt.savefig('game_scores_noshuffle_q100000_navg5000.png')

    with open('blackjack_orig_game_avg.txt', 'w') as filehandle:
        for listitem in game_avg:
            filehandle.write('%s\n' % listitem)

    return policy

def main():
    #os.system('python blackjack_higheravg.py')
    #os.system('python blackjack_noshuffle2.py')

    # read in as a list
    noshuffle_gameavg = []
    with open('blackjack_noshuffle_game_avg.txt', 'r') as filehandle:
        for line in filehandle:
            # remove linebreak which is the last character of the string
            currentPlace = line[:-1]
            
            # add item to the list
            noshuffle_gameavg.append(float(currentPlace))
    orig_gameavg = []
    with open('blackjack_orig_game_avg.txt', 'r') as filehandle:
        for line in filehandle:
            # remove linebreak which is the last character of the string
            currentPlace = line[:-1]

            # add item to the list
            orig_gameavg.append(float(currentPlace))

    print(noshuffle_gameavg)
    print(orig_gameavg)
    x = [i*1000 for i in range(23)]
    y = np.asarray([noshuffle_gameavg,orig_gameavg])


    plt.plot(x, noshuffle_gameavg, label='No reshuffle')
    plt.plot(x, orig_gameavg, label='With reshuffle')
    plt.ylabel('Score')
    plt.xlabel('Game Numbers (per 1000)')
    plt.title('Q-Learning Evaluation Scores While Learning')
    plt.legend()

    plt.savefig('twolines.png')





if __name__ == '__main__':
    main()
