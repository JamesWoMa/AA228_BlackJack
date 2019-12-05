import numpy as np
import random
from collections import defaultdict
import matplotlib.pyplot as plt

total_sum = 340

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

def qlearning(deck, threshold, r, alpha=0.5, gamma=0.95):
	q = [defaultdict(int) for i in range(2)]
	s, curr_d, opp_sc = init(deck, threshold)
	game_score = []
	for iteration in range(500000):
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
				q[a][state] += alpha * (-r + gamma * (max(q[0][state_new], q[1][state_new]) - q[a][state]))
				game_score.append(-opp_sc)
				s, curr_d, opp_sc = init(deck, threshold)
		else:
			sc = score(s)
			if(s[0] > 0 and sc + 10 <= 21):
				#q[a][state] += alpha * 10
				sc += 10
			sc = calc_score(sc)
			if(sc > opp_sc):
				q[a][state] += alpha * r
			else:
				q[a][state] += alpha * -r

			game_score.append(sc - opp_sc)
			s, curr_d, opp_sc = init(deck, threshold)

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

	# Dictionary of cards left
	your_cards = (0, 0, 0, 0, 0, 0, 0, 0, 0, 0)
	game_over = False
	your_score = 0
	sc_against_opp = 0

	#Q-Learning
	wins = []
	for r in [10, 15, 20, 25, 30]:
		policy = qlearning(deck, 14, r)
		win_rate = 0
		games = 5000
		for i in range(5000):
			s, curr_d, opp_sc = init(deck, 14)
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

	plt.figure()
	plt.bar([i for i in range(5)], wins)
	plt.xlabel('Reward Values')
	plt.ylabel('Win Rates')
	plt.title('Win Rates for Q-Learning Per Reward Values')
	plt.savefig('rewards.png')

if __name__ == '__main__':
	main()