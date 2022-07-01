import random
import time
import math

ROW_COUNT = 6
COLUMN_COUNT = 7
IN_A_ROW = 4

def mcts(board, player):
	state = board.copy()
	initial_time = time.time()
	root = Node(state, player)

	while time.time() - initial_time < 0.8:
		root.run()

	children_scores = [child.node_total_visits for child in root.children]
	max_score = max(children_scores)
	best_child = root.children[children_scores.index(max_score)]
	return best_child.action_taken
	
class Node:
	def __init__(self, state, player, parent=None, is_terminal=False, terminal_score=None, action_taken=None):
		self.state = state
		self.player = player
		self.children = []
		self.parent = parent
		self.node_total_score = 0
		self.node_total_visits = 0
		self.available_moves = get_valid_locations(state)
		self.is_terminal = is_terminal
		self.terminal_score = terminal_score
		self.action_taken = action_taken

	def run(self):
		if self.is_terminal:
			self.backpropagate(self.terminal_score)
			return
		if self.is_expandable():
			self.expand_and_simulate_child()
			return
		children_scores = [
			uct_score(
				child.node_total_score, child.node_total_visits, self.node_total_visits
			) for child in self.children
		]
		max_score = max(children_scores)
		best_child = self.children[children_scores.index(max_score)]
		best_child.run()

	def backpropagate(self, score):
		self.node_total_score += score
		self.node_total_visits += 1
		if self.parent is not None:
			self.parent.backpropagate(opponent_score(score))

	def is_expandable(self):
		return (not self.is_terminal) and (len(self.available_moves) > 0)

	def expand_and_simulate_child(self):
		column = random.choice(self.available_moves)
		child_state = self.state.copy()
		drop_piece(child_state, column, self.player)
		is_terminal, terminal_score = check_finish_and_score(child_state, column, self.player)
		self.children.append(
			Node(child_state, opponent_player(self.player), self, is_terminal, terminal_score, column)
		)
		simulation_score = self.children[-1].simulate()
		self.children[-1].backpropagate(simulation_score)
		self.available_moves.remove(column)

	def simulate(self):
		if self.is_terminal:
			return self.terminal_score
		return opponent_score(default_policy_simulation(self.state, self.player))

def is_win(board, column, mark):
	columns = COLUMN_COUNT
	rows = ROW_COUNT
	inarow = IN_A_ROW - 1
	row = min([r for r in range(rows) if board[column + (r * columns)] == mark])

	def count(offset_row, offset_column):
		for i in range(1, inarow + 1):
			r = row + offset_row * i
			c = column + offset_column * i
			if (
				r < 0
				or r >= rows
				or c < 0
				or c >= columns
				or board[c + (r * columns)] != mark
			):
				return i - 1
		return inarow

	return (
		count(1, 0) >= inarow  # vertical.
		or (count(0, 1) + count(0, -1)) >= inarow  # horizontal.
		or (count(-1, -1) + count(1, 1)) >= inarow  # top left diagonal.
		or (count(-1, 1) + count(1, -1)) >= inarow  # top right diagonal.
	)

def get_valid_locations(state):
	return [c for c in range(COLUMN_COUNT) if state[c] == 0]

def is_terminal(state):
	if len(get_valid_locations(state)) == 0:
		return True
	for col in range(COLUMN_COUNT):
		try:
			if is_win(state, col, 1) or is_win(state, col, -1):
				return True
		except Exception:
			pass
	return False

def opponent_score(score):
	return 1 - score

def opponent_player(player):
	# return 3 - player
	return -1*player

def drop_piece(state, column, player):
	row = max([r for r in range(ROW_COUNT) if state[column + (r * COLUMN_COUNT)] == 0])
	state[column + (row * COLUMN_COUNT)] = player

def check_finish_and_score(state, column, player):
	if is_win(state, column, player):
		return (True, 1)
	if len(get_valid_locations(state)) == 0:
		return (True, 0.5)
	return (False, 0)

def default_policy_simulation(state, player):
	initial_player = player
	state = state.copy()
	column = random.choice(get_valid_locations(state))
	drop_piece(state, column, player)
	is_finish, score = check_finish_and_score(state, column, player)
	while not is_finish:
		player = opponent_player(player)
		column = random.choice(get_valid_locations(state))
		drop_piece(state, column, player)
		is_finish, score = check_finish_and_score(state, column, player)
	if player == initial_player:
		return score
	return opponent_score(score)

def uct_score(node_total_score, node_total_visits, parent_total_visits):
	if node_total_visits == 0:
		return float('inf')
	return node_total_score/node_total_visits + math.sqrt(2*math.log(parent_total_visits)/node_total_visits)
