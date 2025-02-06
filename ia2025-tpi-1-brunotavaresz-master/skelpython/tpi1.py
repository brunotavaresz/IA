#STUDENT NAME: Bruno Tavares
#STUDENT NUMBER: 113372

#DISCUSSED TPI-1 WITH: (names and numbers): Andre Alves 113962, Diogo Costa 112714, Francisco Pinto 113763


from tree_search import *
from strips import *
from blocksworld import *

class MyNode(SearchNode):

    def __init__(self, state, parent, depth=0, cost=0, heuristic=0, action=None):
        super().__init__(state,parent)
        #ADD HERE ANY CODE YOU NEED
        self.depth = depth
        self.cost = cost
        self.heuristic = heuristic
        self.action = action

class MyTree(SearchTree):

    def __init__(self,problem, strategy='breadth',improve=False):
        super().__init__(problem,strategy)
        #ADD HERE ANY CODE YOU NEED
        root = MyNode(problem.initial, None, 0, 0, problem.domain.heuristic(problem.initial,problem.goal), None)
        self.num_open = 0
        self.num_solution = 0
        self.num_skipped = 0
        self.num_closed = 0
        self.improve = improve
        self.open_nodes = [root]

    def astar_add_to_open(self,lnewnodes):
        self.open_nodes.extend(lnewnodes)

        self.open_nodes.sort(key=lambda node: (node.cost + node.heuristic, node.depth, node.state))
        pass

    def informeddepth_add_to_open(self,lnewnodes):
        lnewnodes.sort(key=lambda node: (node.cost + node.heuristic, node.state))
        self.open_nodes = lnewnodes + self.open_nodes
        pass

    def search2(self):
        while self.open_nodes != []:
            node = self.open_nodes.pop(0)
            if not self.improve:
                if self.problem.goal_test(node.state):
                    self.solution = node
                    self.num_solution += 1
                    return self.get_path(node)
            else:
                if self.problem.goal_test(node.state):
                    self.num_solution += 1
                    if self.solution is not None:
                        self.num_open -=1
                    else:
                        0
                    if self.solution is None or node.cost <= self.solution.cost:
                        self.solution = node
                    continue

            if self.solution is not None:
                heuristic_hc = node.cost + node.heuristic 
                if (heuristic_hc >= self.solution.cost): 
                    self.num_skipped += 1 
                    self.num_open -= 1 
                    continue

    
            self.num_closed += 1  
            self.num_open -= 1  
            newnodes = []
            for i in self.problem.domain.actions(node.state):
                newstate = self.problem.domain.result(node.state,i)
                if newstate not in self.get_path(node):
                    depth = node.depth + 1
                    new_cost = node.cost + self.problem.domain.cost(node.state,i)
                    heuristic = self.problem.domain.heuristic(newstate,self.problem.goal)

                    newnode = MyNode(newstate,node,depth,new_cost,heuristic,i)
                    newnodes.append(newnode)

            self.add_to_open(newnodes)
            self.num_open += len(newnodes)

        return self.get_path(self.solution)
        
    def check_admissible(self,node):
        #Assume that the given "node" is a solution node
        #IMPLEMENT HERE
        actual_cost = 0
        actual_node = node

        while actual_node is not None:
            
            if actual_node.heuristic > actual_cost:
                return False
             
            if actual_node.parent is not None:
                action_cost = self.problem.domain.cost(actual_node.parent.state, actual_node.action)  
                actual_cost += action_cost   

            actual_node = actual_node.parent    

        return True

    def get_plan(self,node):
        get_plan = []
    
        while node.parent is not None:
            get_plan.append(node.action)
            node = node.parent
            
        get_plan.reverse() #raiz to nó
        
        return get_plan


class MyBlocksWorld(STRIPS):

    def heuristic(self, state, goal):
        misplaced = 0
        total_distance = 0

        goal_positions = {}
        for i in goal:
            if isinstance(i, On):
                goal_positions[i.args[0]] = i.args[1]  # cima de outro
            elif isinstance(i, Floor):
                goal_positions[i.args[0]] = 'Floor'  # livre

        for i in state:
            if isinstance(i, On):  # em cima de outros
                block_on = i.args[0]
                block_under = i.args[1]
                if block_on in goal_positions:
                    if goal_positions[block_on] != block_under:
                        misplaced += 1  # não está na posição correta
                        total_distance += 1
            elif isinstance(i, Floor):  # livres
                block = i.args[0]
                if block in goal_positions:
                    if goal_positions[block] != 'Floor':
                        misplaced += 1  # bloco não está no chão (devia)
                        total_distance += 1

        # blocos fora + distancia
        return misplaced + total_distance