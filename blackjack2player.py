import numpy as np
import random
from collections import defaultdict
import matplotlib.pyplot as plt

total_sum = 340

def gen_initial_deck():
    # Initial Deck
    suite = np.concatenate((np.arange(1,10),np.ones(4)*10))
    deck = np.repeat(suite, 4).astype(int)
    return deck

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

def hit_q_old(your_cards, deck):
	random_draw = random.randint(0,len(deck)-1)
	next_deck = np.delete(deck, random_draw)
	cards = list(your_cards)
	cards[deck[random_draw] - 1] += 1
	your_cards = tuple(cards)
	return your_cards, next_deck, deck[random_draw]

def calc_score(total):
	if total > 21:
		return 0
	return total

def score(s):
	return sum([(i + 1) * s[i] for i in range(10)])

def score_o(s):
	add = 0
	if(s[0] > 0):
		add = 10
	return sum([(i + 1) * s[i] for i in range(10)]) + add

def opp_score(s, deck):
	return total_sum - score(s) - np.sum(deck)

def opp_strat(o, deck, threshold):
	while(score_o(o) < threshold):
		o, deck, _ = hit_q(o, deck)

	sc = score_o(o)
	sc = calc_score(sc)

	return sc, deck

def init(deck, threshold):
	s = (0, 0, 0, 0, 0, 0, 0, 0, 0, 0)
	o = (0, 0, 0, 0, 0, 0, 0, 0, 0, 0)
	for i in range(2):
		s, deck, _ = hit_q(s, deck)
	
	sc, deck = opp_strat(o, deck, threshold)
	return s, deck, sc 

def qlearning(deck, threshold, alpha=0.5, gamma=0.95):
	q = [defaultdict(int) for i in range(2)]
	s, curr_d, opp_sc = init(deck, threshold)
	game_score = []
	for iteration in range(1000000):
		state = (s, tuple(curr_d))
		#epsilon greedy
		if(np.random.rand() < 0.8):
			if(q[0][state] > q[1][state]):
				a = 0
			else:
				a = 1
		else:
			a = np.random.choice(1)

		if(a == 1):
			s_new, next_d, r = hit_q(s, curr_d)
			state_new = (s_new, tuple(next_d))
			sc = sum([(i + 1) * s_new[i] for i in range(10)])
			if(sc <= 21):
				q[a][state] += alpha * (0 + gamma * (max(q[0][state_new], q[1][state_new]) - q[a][state]))
				s = s_new
				curr_d = next_d
			else:
				if(opp_sc != 0):
					q[a][state] += alpha * (-20 + gamma * (max(q[0][state_new], q[1][state_new]) - q[a][state]))
				game_score.append(-opp_sc)

				s, curr_d, opp_sc = init(curr_d, threshold)
		else:
			sc = score(s)
			if(s[0] > 0 and sc + 10 <= 21):
				#q[a][state] += alpha * 10
				sc += 10
			sc = calc_score(sc)
			if(sc > opp_sc):
				q[a][state] += alpha * 20
			elif(sc < opp_sc):
				q[a][state] += alpha * -20

			game_score.append(sc - opp_sc)
			s, curr_d, opp_sc = init(curr_d, threshold)

	policy = defaultdict(int)
	for s in q[0]:
		if(q[0][s] > q[1][s]):
			policy[s] = 0
		else:
			policy[s] = 1

	for s in q[1]:
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
	curr_d = deck
	# Dictionary of cards left
	your_cards = (0, 0, 0, 0, 0, 0, 0, 0, 0, 0)
	game_over = False
	your_score = 0
	sc_against_opp = 0

	#Q-Learning
	wins = []
	for threshold in [15, 16, 17]:
		policy = qlearning(deck, threshold)
		win_rate = 0
		games = 5000
		for i in range(5000):
			s, curr_d, opp_sc = init(curr_d, threshold)
			state = (s, tuple(curr_d))
			while(policy[state] == 1):
				s, curr_d, _ = hit_q(s, curr_d)
				sc = score(s)
				if(sc > 21):
					break
				state = (s, tuple(curr_d))

			sc = score(s)
			if(s[0] > 0 and sc + 10 <= 21):
				sc += 10
			sc = calc_score(sc)
			your_score += sc
			if(sc > opp_sc):
				win_rate += 1
			if(sc == opp_sc):
				games -= 1

		win_rate /= games
		your_score /= games
		print("Your Score:",your_score)
		print("Score against opponent:", win_rate)
		wins.append(win_rate)

	"""
	plt.figure()
	plt.bar([i for i in range(22)], wins)
	plt.xlabel('Threshold Values')
	plt.ylabel('Win Rates')
	plt.title('Win Rates for Q-Learning Per Threshold')
	plt.savefig('win_rates_new.png')
	"""

if __name__ == '__main__':
	main()