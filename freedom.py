import sys
import copy
import operator
import math

# board dimensions
dims = [8,8]

# globals
freedom_flag = False

# function to map strings to logical operators
def param_op(x, op, y): 
	op_map = {'<' : operator.lt, '>=' : operator.ge }
	return op_map[op](x, y)

# class FBState is used represent a freedom board state
class FBState:

	def __init__(self, base_stones, num_stones, lsw, lsb):
		if not(base_stones == None):
			self.stones = base_stones
		else:
			self.stones = self.zero_state()
		self.utility = 0
		self.stone_count = num_stones
		self.last_stone_white = lsw
		self.last_stone_black = lsb

	# determines when games has ended, based on stone count
	def game_over(self):
		return (self.stone_count >= (dims[0] * dims[1]))

	# evaluation function = (AI lives - Player lives)
	def evaluate(self):
		wc = 0
		ws = 0
		bc = 0
		bs = 0
		visited = {}
		lw = [{},{},{},{}]
		lb = [{},{},{},{}]
		lc = []
		sign = 0
		for key in self.stones:
			if self.stones[key].color == 'W':
				sign = -1
				lc = lw
			elif self.stones[key].color == 'B':
				sign = 1
				lc = lb
			else:
				continue
			#count along diag down-right
			ws += (sign * FBState.check_diag_dr(self.stones[key], \
			self.stones, visited, self.stones[key].color, lc[0], wc, \
			[-1, -1, 1, 1], ['>=', '>=', '<', '<'], [0, 0, dims[0], dims[1]]))
			visited.clear()
			# count along diag up-right
			ws += (sign * FBState.check_diag_dr(self.stones[key], \
			self.stones, visited, self.stones[key].color, lc[1], wc, \
			[1, -1, 1, -1], ['<', '>=', '<', '>='], [dims[0], 0, dims[0], 0]))
			visited.clear()
			# count along vertical
			ws += (sign * FBState.check_diag_dr(self.stones[key], \
			self.stones, visited, self.stones[key].color, lc[2], wc, \
			[-1, 0, 1, 0], ['>=', '>=', '<', '>='], [0, 0, dims[0], 0]))
			visited.clear()
			# count along horizontal
			ws += (sign * FBState.check_diag_dr(self.stones[key], \
			self.stones, visited, self.stones[key].color, lc[3], wc, \
			[0, -1, 0, 1], ['>=', '>=', '>=', '<'], [0, 0, 0, dims[1]]))
			visited.clear()

		self.utility = ws

	# method used to recursively check a direction to see if a live is present
	# the "visted" dict prevents revisiting nodes during a search and "line_nodes"
	# prevents duplicate counting along a given direction
	@staticmethod
	def check_diag_dr(stone, stones, visited, color, line_nodes, counter, lhsl, oplist, rhsl):
		if not(stone.color == color) or stone.pos in line_nodes or stone.pos in visited:
			return counter
		visited[stone.pos] = stone
		if len(visited) == 4:
			for key in visited:
				line_nodes[key] = visited[key]
			counter += 1
			return counter
		if (param_op(stone.npos[0] + lhsl[0], oplist[0], rhsl[0])) and \
			(param_op(stone.npos[1] + lhsl[1], oplist[1], rhsl[1])):
			cellx = stones[str(stone.npos[0] + lhsl[0]) + str(stone.npos[1] + lhsl[1])] 
			counter = max(FBState.check_diag_dr(cellx, stones, visited, color, line_nodes, \
			counter, lhsl, oplist, rhsl), counter)
		if (param_op(stone.npos[0] + lhsl[2], oplist[2], rhsl[2])) and \
			(param_op(stone.npos[1] + lhsl[3], oplist[3], rhsl[3])):
			celly = stones[str(stone.npos[0] + lhsl[2]) + str(stone.npos[1] + lhsl[3])] 
			counter = max(FBState.check_diag_dr(celly, stones, visited, color, line_nodes, \
			counter, lhsl, oplist, rhsl), counter)
		return counter

	# zeros out board
	def zero_state(self):
		stones = {}
		for i in range(dims[0]):
			for j in range(dims[1]):
				stones[str(i) + str(j)] = FStone(str(i) + " " + str(j), "-")
		return stones

	# checks for equality among two states
	def __eq__(self, other):
		is_equal = True
		for key in self.stones:
			if not(self.stones[key] == other.stones[key]):
				is_equal = False
				break
		return is_equal

	# class to string method
	def __str__(self):
		stones_str = ""
		i = 0;
		for key in self.stones:
			stones_str += str(self.stones[key])
			if i == dims[0] - 1:
				stones_str += "\n"
			i = (i+1) % dims[0]
		return stones_str

	# add a stone to the board state
	def add_stone(self, stone):
		self.stones[stone.pos].color = stone.color
		self.stone_count += 1
		if stone.color == 'W':
			self.last_stone_white = stone
		else:
			self.last_stone_black = stone

# class FStone holds data for a given stone, such as it's
# board position and color
class FStone:

	def __init__(self, strpos, color):
		self.pos = strpos.replace(" ", "")
		self.color = color
		self.npos = [int(self.pos[0]), int(self.pos[1])]

	# checks for equality among two stones. They are equal if
	# their position and color are the same
	def __eq__(self, other):
		return (self.pos == other.pos and self.color == other.color)

	# class to string method
	def __str__(self):
		string = ""
		if self.color == 'W':
			string = '\033[92m' + u'\u25CF' + " "
			#string = '\033[92m' + "* "
		elif self.color == 'B':
			string = '\033[91m' + u'\u25CF' + " "
			#string = '\033[91m' + "* "
		else:
			string = u'\u25CF' + " "
			#string = "* "
		return string + '\033[0m'

# class Tree is used to hold data pertinent to a tree
# such as the root node and the tree's depth
class Tree:

	def __init__(self, root):
		self.root = root
		self.depth = 0

	# function prints the tree recursively starting from root
	def print_tree(self, root):
		print(root)
		for child in root.children:
			self.print_tree(child)

# class Node is the node class in which a tree is built.
# In the context of this program, a tree of states is built
class Node:

	def __init__(self, fbstate, children, depth):
		self.state = fbstate
		self.children = children
		self.depth = depth

	# class to string method
	def __str__(self):
		return "node at depth " + str(self.depth) + '\n' + str(self.state) \
				+ " with utility: " + str(self.state.utility)

	# lt used for sorting, returns true based on self node's
	# utility being less than the other's
	def __lt__(self, other):
		return (self.state.utility < other.state.utility)

# function to determine all valid states given a current state
# other parameters used to handle edge cases such as when it's the first
# move or when a player has the right to freedom
def reachable_states(fbstate, color, is_first_move, consider_freedom):
	if color == 'W':
		target_color = 'B'
		stone = fbstate.last_stone_black
	else:
		target_color = 'W'
		stone = fbstate.last_stone_white
	states = []
	if not(is_first_move):
		pos = stone.pos
		npos = stone.npos
	# check up
	if  not(is_first_move) and (int(pos[0]) - 1 >= 0) and \
		fbstate.stones[str(npos[0] - 1) + str(npos[1])].color == '-':
		new_state = FBState(copy.deepcopy(fbstate.stones), fbstate.stone_count, \
		fbstate.last_stone_white, fbstate.last_stone_black)
		new_state.add_stone(FStone(str(npos[0] - 1) + str(npos[1]), color))
		states.append(new_state)
	# check down
	if not(is_first_move) and (int(pos[0]) + 1 < dims[0]) and \
		fbstate.stones[str(npos[0] + 1) + str(npos[1])].color == '-':
		new_state = FBState(copy.deepcopy(fbstate.stones), fbstate.stone_count, \
		fbstate.last_stone_white, fbstate.last_stone_black)
		new_state.add_stone(FStone(str(npos[0] + 1) + str(npos[1]), color))
		states.append(new_state)
	# check left
	if not(is_first_move) and (npos[1] - 1 >= 0) and \
		fbstate.stones[str(npos[0]) + str(npos[1] - 1)].color == '-':
		new_state = FBState(copy.deepcopy(fbstate.stones), fbstate.stone_count, \
		fbstate.last_stone_white, fbstate.last_stone_black)
		new_state.add_stone(FStone(str(npos[0]) + str(npos[1] - 1), color))
		states.append(new_state)
	# check right
	if not(is_first_move) and (npos[1] + 1 < dims[1]) and \
		fbstate.stones[str(npos[0]) + str(npos[1] + 1)].color == '-':
		new_state = FBState(copy.deepcopy(fbstate.stones), fbstate.stone_count, \
		fbstate.last_stone_white, fbstate.last_stone_black)
		new_state.add_stone(FStone(str(npos[0]) + str(npos[1] + 1), color))
		states.append(new_state)
	# check up-right
	if not(is_first_move) and (npos[0] - 1 >= 0) and (npos[1] + 1 < dims[1]) and \
		fbstate.stones[str(npos[0] - 1) + str(npos[1] + 1)].color == '-':
		new_state = FBState(copy.deepcopy(fbstate.stones), fbstate.stone_count, \
		fbstate.last_stone_white, fbstate.last_stone_black)
		new_state.add_stone(FStone(str(npos[0] - 1) + str(npos[1] + 1), color))
		states.append(new_state)
	# check up-left
	if not(is_first_move) and (npos[0] - 1 >= 0) and (npos[1] - 1 >= 0) and \
		fbstate.stones[str(npos[0] - 1) + str(npos[1] - 1)].color == '-':
		new_state = FBState(copy.deepcopy(fbstate.stones), fbstate.stone_count, \
		fbstate.last_stone_white, fbstate.last_stone_black)
		new_state.add_stone(FStone(str(npos[0] - 1) + str(npos[1] - 1), color))
		states.append(new_state)
	# check down-right
	if not(is_first_move) and (npos[0] + 1 < dims[0]) and (npos[1] + 1 < dims[1]) and \
		fbstate.stones[str(npos[0] + 1) + str(npos[1] + 1)].color == '-':
		new_state = FBState(copy.deepcopy(fbstate.stones), fbstate.stone_count, \
		fbstate.last_stone_white, fbstate.last_stone_black)
		new_state.add_stone(FStone(str(npos[0] + 1) + str(npos[1] + 1), color))
		states.append(new_state)
	# check down-left
	if not(is_first_move) and (npos[0] + 1 < dims[0]) and (npos[1] - 1 >= 0) and \
		fbstate.stones[str(npos[0] + 1) + str(npos[1] - 1)].color == '-':
		new_state = FBState(copy.deepcopy(fbstate.stones), fbstate.stone_count, \
		fbstate.last_stone_white, fbstate.last_stone_black)
		new_state.add_stone(FStone(str(npos[0] + 1) + str(npos[1] - 1), color))
		states.append(new_state)

	# case freedom
	if len(states) <= 0:
		global freedom_flag
		if not(is_first_move) and consider_freedom:
			freedom_flag = True
		for key in fbstate.stones:
			current = fbstate.stones[key]
			if current.color == '-':
				new_state = FBState(copy.deepcopy(fbstate.stones), fbstate.stone_count, \
				fbstate.last_stone_white, fbstate.last_stone_black)
				new_state.add_stone(FStone(current.pos, color))
				states.append(new_state)

	# return list of valid next states
	return states

# this function generates a tree of nodes (which have states)
# in a BFS manner
def generate_tree(depth, init_state):
	root = Node(init_state, [], 0)

	queue = []
	queue.append(root)

	tree = Tree(root)

	current = root
	while (current.depth < depth and not(len(queue) <= 0)):

		current = queue[0]

		if current.depth >= depth:
			break

		queue = queue[1:]

		# tracking turn so that the appropiate states are generated
		if current.depth % 2 == 0:
			turn = 'B'
		else:
			turn = 'W'

		r_states = reachable_states(current.state, turn, False, False)
		for state in r_states:
			new_node = Node(state, [], current.depth + 1)
			queue.append(new_node)
			current.children.append(new_node)
			tree.depth = current.depth + 1

	while not(len(queue) <= 0):
		deep_node = queue[0]
		queue = queue[1:]
		deep_node.state.evaluate()

	return tree

# minimax function also has alpha beta pruning added
# and finds the optimal path for max, which in this case
# is the AI
def minimax(root, max_move, depth, a, b):
	if depth == 0:
		return root.state.utility

	if max_move:
		max_eval = -math.inf
		for child in root.children:
			evaluation = minimax(child, False, depth - 1, a, b)
			max_eval = max(max_eval, evaluation)
			root.state.utility = max_eval
			a = max(a, evaluation)
			if b <= a:
				break
		return max_eval
	else:
		min_eval = math.inf
		for child in root.children:
			evaluation = minimax(child, True, depth - 1, a, b)
			min_eval = min(min_eval, evaluation)
			root.state.utility = min_eval
			b = min(b, evaluation)
			if b <= a:
				break
		return min_eval

# function ai_move is the function that links all functionality
# the ai needs to decide the next move. This function returns the
# next best move based on the tree, or the passed state in the case
# the ai is the last turn and the current state is optimal or equal
# to the final state
def ai_move(init_state, depth):

	r_states = reachable_states(init_state, 'B', False, True)

	global freedom_flag
	if freedom_flag:
		print("AI given right to freedom")
		freedom_flag = False

	tree = generate_tree(depth, init_state)
	e = minimax(tree.root, True, tree.depth, -math.inf, math.inf)

	tree.root.children.sort(reverse = True)

	# AI right to skip turn on last if reduces score
	if init_state.stone_count >= ((dims[0] * dims[1]) - 1) and \
		init_state.utility > tree.root.children[0].state.utility:
		init_state.stone_count += 1
		print("AI choose not to place last stone")
		return init_state

	if not(len(tree.root.children) <= 0):
		return tree.root.children[0].state

# player_move encapsulates all logic regarding the player entering
# a valid move. This method returns a state that is the state after the
# player has made their move
def player_move(fbstate):

	global freedom_flag
	move_valid = False
	while (not(move_valid)):

		r_states = reachable_states(fbstate, 'W', (fbstate.stone_count <= 0), True)

		if (fbstate.stone_count <= 0):
			input_str = "First move goes to the human... thats you!\nEnter move in format 'row col', Ex: 1 2\nTop-Left hand corner of the board is position 0 0\nEnter move: "
		elif fbstate.stone_count >= ((dims[0] * dims[1]) - 1):
			input_str = "Type 'skip' to skip this turn if you would like: "
		elif freedom_flag:
			input_str = "You currently have the right to freedom!\nChoose any open spot: "
			freedom_flag = False
		else:
			input_str = "Enter your move: "
		player_move = input(input_str)

		if (player_move == 'q' or player_move.lower() == "quit" \
			or player_move.lower() == "exit"):
			exit(0)

		if fbstate.stone_count >= ((dims[0] * dims[1]) - 1) and \
			player_move.lower() == "pass" or player_move.lower() == "skip":
			fbstate.stone_count += 1
			return fbstate

		stone = FStone(player_move, 'W')
		new_state = FBState(copy.deepcopy(fbstate.stones), fbstate.stone_count, \
		fbstate.last_stone_white, fbstate.last_stone_black)
		new_state.add_stone(stone)

		if new_state.stone_count == 1:
			move_valid = True
			break

		for state in r_states:
			if state == new_state:
				move_valid = True
				break

	fbstate.add_stone(stone)

# playgame is the function that has both players, the human and
# AI respectively play until the board is full
def playgame(depth):

	# create empty board
	fbstate = FBState(None, 0, None, None)
	print(fbstate)

	while not(fbstate.game_over()):

		player_move(fbstate)

		if (fbstate.game_over()):
			break

		fbstate = ai_move(fbstate, depth)

		print("choosing state with utility: " + str(fbstate.utility))
		fbstate.evaluate()
		print("chosen state has AI score: " + str(fbstate.utility))
		print(fbstate)

	return fbstate
