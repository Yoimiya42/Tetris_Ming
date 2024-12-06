from board import Direction, Rotation, Action
from random import Random
import time


class Player:
    def choose_action(self, board):
        raise NotImplementedError

class MingPlayer(Player):
    def __init__(self):
        self.best_actions = []

    previous_score = 0
    previous_height = 24
    previous_holes = 0
    # weighted for each heuristic
    weighted_height= - 0.51
    weighted_holes = - 0.95
    weighted_bumpiness = - 0.18
    weighted_lines_cleared = 1.3 #0.760066

    counter_block = 1

#_______________________________________________________________________________#
    #  Heuristic 1 :  Height Increase
    def get_stack_height(self, board):
        topmost_y = 24
        for (x,y) in board.cells:
            if y < topmost_y:
                topmost_y = y

        return 24 - topmost_y

    def _generate_height_lists(self,board):
        height_lists = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]

        for y in reversed(range(board.height)):
            for x in range(10):
                if (x,y) in board.cells:
                    height = 24 - y
                    height_lists[x] = height
        return height_lists
    
    def calculate_height_increase(self, board):
        min_block_row = 24
        for (x, y) in board.cells:
            if y < min_block_row:
                min_block_row = y

        height_increase = (24 - min_block_row) - self.previous_height
        
        if height_increase >0 :
            return height_increase 
        else:
            return 0
        
    # Heuristic 2 :  Holes
    def _generate_holes_lists(self, board):
        holes_list = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        height_list = self._generate_height_lists(board)

        for x in range(10):
            for y in range(24 - height_list[x], 24):
                if (x, y) not in board.cells:
                    holes_list[x] += 1
        return holes_list
    
    def calculate_total_holes(self, board):
        return sum(self._generate_holes_lists(board))
    
    # Heuristic 3 :  Wells
    def calculate_wells(self,board):
        holes = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        height_list = self._generate_height_lists(board)
        for x in range(10):
            for y in range(24 - height_list[x],24):
                if (x,y) not in board.cells:
                    holes[x] += 1
        max_holes = max(holes)
        return max_holes
    
    
    # Heuristic 4 :  Bumpiness
    def calculate_bumpiness(self, board):
        height_list = self._generate_height_lists(board)
        bumpiness = 0
        
        for i in range(len(height_list) - 1):
            bumpiness += abs(height_list[i] - height_list[i+1])
        return bumpiness

    #  Heuristic 5 :  Lines Cleared
    def calculate_lines_cleared(self, board):
  
        current_score = board.score
        diff_score = current_score - self.previous_score

        lines_cleared =0 

        if diff_score >= 1600:
            lines_cleared = 4
            return 100
        
        elif diff_score >= 400:
            lines_cleared = 3
        elif diff_score >= 100:
            lines_cleared = 2
        elif diff_score >= 25:
            lines_cleared = 1

        return lines_cleared * self.weighted_lines_cleared
    
    # Evaluation Function
    def evaluation(self, board):

        height_increase = self.calculate_height_increase(board)
        bumpiness = self.calculate_bumpiness(board)
        holes = self.calculate_total_holes(board)
        wells = self.calculate_wells(board)
        lines_cleared = self.calculate_lines_cleared(board)
        

        evaluation_score = (height_increase * self.weighted_height 
                            + holes * self.weighted_holes
                            + wells * self.weighted_holes * 2.0
                            + bumpiness * self.weighted_bumpiness 
                            + lines_cleared)
        
        
        return evaluation_score

#_______________________________________________________________________________#
    def choose_action(self, board):

        self.counter_block += 1
        print(self.counter_block)

        best_actions = []

        final_score = 0
        best_score = -999999
        self.previous_score = board.score

        self.previous_holes = self.calculate_total_holes(board)
        bestHoles = 0

        max_height = max(self._generate_height_lists(board))
        min_height = min(self._generate_height_lists(board))
        diff_height = max_height - min_height
        self.prevHeight = self.get_stack_height(board)

        ###### 1st block ######
        if max_height < 6 and diff_height != 4:
            for trans1 in range(1,10):
                for rot1 in range(0, 4):
                    demo1_board = board.clone()
                    actions_list1 = []
                    has_landed1 = False

                    if rot1 > 0:
                        for _ in range(0, rot1):
                            if demo1_board.falling is not None:
                                demo1_board.rotate(Rotation.Anticlockwise)
                                actions_list1.append(Rotation.Anticlockwise)

                    if demo1_board.falling is not None:
                        start_x = demo1_board.falling.left

                        while start_x > trans1 and has_landed1 is False:
                            demo1_board.move(Direction.Left)
                            actions_list1.append(Direction.Left)
                            if demo1_board.falling is not None:
                                start_x = demo1_board.falling.left
                            else:
                                has_landed1 = True
                                break

                        while start_x < trans1 and has_landed1 is False:
                            demo1_board.move(Direction.Right)
                            actions_list1.append(Direction.Right)

                            if demo1_board.falling is not None:
                                start_x = demo1_board.falling.left
                            else:
                                has_landed1 = True
                                break


                        if has_landed1 is False:
                            demo1_board.move(Direction.Drop)
                            actions_list1.append(Direction.Drop)
                            has_landed1 = True

                        score1 = self.evaluation(demo1_board)

                ###### 2nd block ######
                    if has_landed1 is True:

                        for trans2 in range(10):
                            for rot2 in range(4):
                                demo2_board = demo1_board.clone()
                                actions_list2 = []
                                has_landed2 = False
                                if rot2 > 0:
                                    for _ in range(0, rot2):
                                        if demo2_board.falling is not None:
                                            demo2_board.rotate(Rotation.Anticlockwise)
                                            actions_list2.append(Rotation.Anticlockwise)

                                if demo2_board.falling is not None:
                                    start_x2 = demo2_board.falling.left

                                    while start_x2 > trans2 and has_landed2 is False:
                                        demo2_board.move(Direction.Left)
                                        actions_list2.append(Direction.Left)

                                        if demo2_board.falling is not None:
                                            start_x2 = demo2_board.falling.left
                                        else:
                                            has_landed2 = True
                                            break

                                    while start_x2 < trans2 and has_landed2 is False:
                                        demo2_board.move(Direction.Right)
                                        actions_list2.append(Direction.Right)

                                        if demo2_board.falling is not None:
                                            start_x2 = demo2_board.falling.left
                                        else:
                                            has_landed2 = True
                                            break

                                    if has_landed2 is False:
                                        demo2_board.move(Direction.Drop)
                                        actions_list2.append(Direction.Drop)

                                    score2 = self.evaluation(demo2_board)
                                    final_score = score2

                                if final_score > best_score:
                                    best_score = final_score
                                    best_actions = actions_list1
                                   
        else:
            for x in range(10):
                for rotations in range(0, 4):
                    demo1_board = board.clone()
                    actions_list1 = []
                    has_landed1 = False

                    if rotations > 0:
                        for i in range(0, rotations):
                            if demo1_board.falling is not None:
                                demo1_board.rotate(Rotation.Anticlockwise)
                                actions_list1.append(Rotation.Anticlockwise)

                    if demo1_board.falling is not None:
                        start_x = demo1_board.falling.left

                        while start_x > x and has_landed1 is False:
                            demo1_board.move(Direction.Left)
                            actions_list1.append(Direction.Left)
                            if demo1_board.falling is not None:
                                start_x = demo1_board.falling.left
                            else:
                                has_landed1 = True
                                break

                        while start_x < x and has_landed1 is False:
                            demo1_board.move(Direction.Right)
                            actions_list1.append(Direction.Right)

                            if demo1_board.falling is not None:
                                start_x = demo1_board.falling.left
                            else:
                                has_landed1 = True
                                break


                        if has_landed1 is False:
                            demo1_board.move(Direction.Drop)
                            actions_list1.append(Direction.Drop)
                            has_landed1 = True

                        score = self.evaluation(demo1_board)

                    if has_landed1 is True:
                        for trans2 in range(10):
                            for rot2 in range(4):
                                demo2_board = demo1_board.clone()
                                actions_list2 = []
                                has_landed2 = False

                                if rot2 > 0:
                                    for j in range(0, rot2):
                                        if demo2_board.falling is not None:
                                            demo2_board.rotate(Rotation.Anticlockwise)
                                            actions_list2.append(Rotation.Anticlockwise)

                                if demo2_board.falling is not None:
                                    start_x2 = demo2_board.falling.left

                                    while start_x2 > trans2 and has_landed2 is False:
                                        demo2_board.move(Direction.Left)
                                        actions_list2.append(Direction.Left)

                                        if demo2_board.falling is not None:
                                            start_x2 = demo2_board.falling.left
                                        else:
                                            has_landed2 = True
                                            break

                                    while start_x2 < trans2 and has_landed2 is False:
                                        demo2_board.move(Direction.Right)
                                        actions_list2.append(Direction.Right)

                                        if demo2_board.falling is not None:
                                            start_x2 = demo2_board.falling.left
                                        else:
                                            has_landed2 = True
                                            break

                                    if has_landed2 is False:
                                        demo2_board.move(Direction.Drop)
                                        actions_list2.append(Direction.Drop)

                                    score2 = self.evaluation(demo2_board)
                                    
                                    final_score = score2

                                if final_score > best_score:
                                    best_score = final_score
                                    best_actions = actions_list1
                                    bestHoles = self.calculate_total_holes(demo2_board)

        if bestHoles > (self.previous_holes) and board.discards_remaining > 0 and self.counter_block > 180:

            return Action.Discard

        
        return best_actions

SelectedPlayer = MingPlayer


