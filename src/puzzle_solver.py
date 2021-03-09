""" Thanks algorithmsinsight.wordpress.com 
    Their insight really help with this program""" 
import numpy as np

class Node(object):
    def __init__(self, state, parent_node, g):
        self.state = state  # The 2d array that is the current state of the puzzle board
        self.parent_node = parent_node
        self.g_score = g
        self.f_score = 0    # Initialize f to 0

    """ Return the position of the blank spot in the board """
    def find_blank(self, state, val):
        rows = np.shape(state)[0]
        cols = np.shape(state)[1]
        for i in range(0,rows):
            for j in range(0,cols):
                if state[i][j] == val:
                    return (i,j)

    """ Return the state of the parent node after one tile move
        Basically, returning a child node """
    def move_tile(self,cur_state,x1,y1,x2,y2):
        """We're checking if x2, y2 is out of the board size"""
        if x2 >= 0 and x2 < np.shape(cur_state)[0] and y2 >= 0 and y2 < np.shape(cur_state)[1]:
            temp_state = np.copy(cur_state)
            temp = temp_state[x2][y2]      
            temp_state[x2][y2] = temp_state[x1][y1]
            temp_state[x1][y1] = temp
            return temp_state
        else:
            return None

    """ This function generate child nodes from the current state by moving the blank space
        in the four directions that is up,down,left,right """
    def generate_child(self):
        x,y = self.find_blank(self.state,0)     # Current location of blank spot

        """ Possible locations of the blank after one move """
        new_blank = [[x+1,y], [x-1,y], [x,y+1], [x,y-1]] 
        children = []
        for i in new_blank:
            child = self.move_tile(self.state,x,y,i[0],i[1]) 
            if child is not None:
                child_node = Node(child,self.state,self.g_score+1) # We pass in the current state as the parent node, the g_score is the level i.e a counter for move taken
                children.append(child_node)
        return children

class Puzzle(object):
    def __init__(self, size):
        self.open_list = []
        self.closed_list = []
        self.board_size = size

    """ f_score = h_score + g_score """
    """ In our case, g_score is the level. and h_score is the manhattan distance """
    def f(self, curr, goal):
        return self.h(curr.state,goal) + curr.g_score

    """ Find the actual location of the puzzle piece on the goal state board """
    def find_loc(self, state, val_to_find):
        for i in range(0,self.board_size):
            for j in range(0, self.board_size):
                if state[i][j] == val_to_find: 
                    return i,j
                    
    """ Currently Manhattan distance """
    """ Planning on adding in linear conflicts """
    def h(self,curr,goal):
        """Calculates the different between the current state and the goal state """
        temp = 0
        for i in range(0,self.board_size):
            for j in range(0,self.board_size):
                if curr[i][j] != goal[i][j] and curr[i][j] != 0:
                    goal_loc = self.find_loc(goal, curr[i][j])   # Finding that mismatched number in the goal state and get its location on the board
                    temp += abs(i - goal_loc[0]) + abs(j - goal_loc[1]) # Adding the distance from the misplaced node to the correct position

        temp += self.linear_conflict(curr,goal) 
        return temp

    """ An attemp at linear conflict """
    def linear_conflict(self,curr,goal):
        linearConflict = 0
        for i in range(0,self.board_size):
            for j in range(0,self.board_size):
                if curr[i][j] == 0: continue    # Just the blank piece
                num = curr[i][j]
                correctPos = self.find_loc(goal,num)
                if (i,j) == correctPos: continue    # The current tile is in the right spot
                if i == correctPos[0]:  # if we're in the correct row
                    for fromCol in range(j+1,self.board_size):
                        """ We checking the conflict on the same row"""
                        if num > curr[i][fromCol] and self.find_loc(goal, curr[i][fromCol])[0] == i:
                            linearConflict += 1
                elif j == correctPos[1]:    # if we're in the correct column                            
                    for fromRow in range(i+1,self.board_size):
                        if num > curr[fromRow][j] and self.find_loc(goal, curr[fromRow][j])[1] == j:
                            linearConflict += 1
        
        return 2 * linearConflict

    """ Check for the existence of a state in the open list """
    def check_exist_in_open(self,board_to_check):
        for i in self.open_list:
            if np.array_equal(board_to_check,i.state):       
                return i
        return None

    """ Check for the existence of a state in the close list 
        by checking the state and its g_score"""
    def check_exist_in_closed(self,node_to_check):
        for i in self.closed_list:
            if i.g_score == node_to_check.g_score and np.array_equal(i.state,node_to_check.state) == True:
                return True
        return False

    """ The main puzzle solver """
    def solve_sliding_puzzle(self,start,goal):
        """ First Node """
        start = Node(start,None,0)
        start.f_score = self.f(start,goal)

        self.open_list.append(start)

        while self.open_list:
            curr = self.open_list[0] # node with the smallest f_score
            print(curr.state)

            if(self.h(curr.state,goal) == 0):
                print(curr.state)   ## Debug
                print("Took " + str(curr.g_score) + " moves")
                break

            self.open_list.pop(0)                
            self.closed_list.append(curr)

            for i in curr.generate_child():
                if self.check_exist_in_closed(i) == True:   # Already in closed list, we skip
                    continue
                else:             
                    # First we see if the state already exist in the open list
                    # If it is not, then we simply append that to the open list
                    check_node = self.check_exist_in_open(i.state)
                    if check_node is None:
                        i.f_score = self.f(i,goal)
                        self.open_list.append(i)
                    else:
                        if(check_node.g_score < i.g_score):         # No need to overwrite the state
                            check_node.g_score = i.g_score
                            check_node.parent_node = i.parent_node
                            check_node.f_score = self.f(i,goal)

            self.open_list.sort(key= lambda x:x.f_score,reverse=False)

# Doing 3x3 puzzle
def main():
    """ Board Generation """
    goal_state = np.array([1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,0]) #0 is the empty space

    print("Please enter your starting puzzle board")
    start_state =  []
    for i in range(0,16):
        temp = int(input())
        start_state.append(temp)

    print('Thanks for the input')
    start_state = np.array(start_state) 

    """ Reshape the array """
    goal_state = np.reshape(goal_state,(4,4))
    start_state = np.reshape(start_state,(4,4))

    """ May have to check if the user input start board is solvable or not """

    """ Initialize the puzzle """
    puzzle =  Puzzle(4)

    """ Solve the solvable puzzle """  
    puzzle.solve_sliding_puzzle(start_state,goal_state)

if __name__ == '__main__':
    main()