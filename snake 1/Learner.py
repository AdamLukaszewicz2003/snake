import random
import json

import dataclasses

@dataclasses.dataclass
class GameState:
    distance: tuple
    position: tuple
    surroundings: str
    food: tuple


class Learner(object):
    def __init__(self, display_width, display_height, block_size):
        # Parametry gry
        self.display_width = display_width
        self.display_height = display_height
        self.block_size = block_size

        # Parametry wagi
        self.epsilon = 0.1
        self.lr = 0.7
        self.discount = .5

        # Historia dzialan i wynikow
        self.qvalues = self.LoadQvalues()
        self.history = []

        # Ruch
        self.actions = {
            0:'left',
            1:'right',
            2:'up',
            3:'down'
        }

    def Reset(self):
        self.history = []

    def LoadQvalues(self, path="qvalues.json"):
        with open(path, "r") as f:
            qvalues = json.load(f)
        return qvalues

    def SaveQvalues(self, path="qvalues.json"):
        with open(path, "w") as f:
            json.dump(self.qvalues, f)
            
    def act(self, snake, food):
        state = self._GetState(snake, food)

        # Epsilon greedy
        rand = random.uniform(0,1)
        if rand < self.epsilon:
            action_key = random.choices(list(self.actions.keys()))[0]
        else:
            state_scores = self.qvalues[self._GetStateStr(state)]
            action_key = state_scores.index(max(state_scores))
        action_val = self.actions[action_key]
        
        # Zapamietywanie  dzialan, jakie zostaly podjete w kazdym stanie
        self.history.append({
            'state': state,
            'action': action_key
            })
        return action_val
    
    def UpdateQValues(self, reason):
        history = self.history[::-1]
        for i, h in enumerate(history[:-1]):
            if reason: # Waz umarl, dodanie kary
                sN = history[0]['state']
                aN = history[0]['action']
                state_str = self._GetStateStr(sN)
                reward = -1
                self.qvalues[state_str][aN] = (1-self.lr) * self.qvalues[state_str][aN] + self.lr * reward # Rownanie Bellmana - od zakończenia gry nie ma stanu przyszłego
                reason = None
            else:
                s1 = h['state'] # aktualny stan
                s0 = history[i+1]['state'] # poprzedni stan
                a0 = history[i+1]['action'] # dzialanie podjete w poprzednim kroku
                
                x1 = s0.distance[0] # dystans x w aktualnym stanie
                y1 = s0.distance[1] # dystans y w aktualnym stanie
    
                x2 = s1.distance[0] # dystans x w poprzednim stanie
                y2 = s1.distance[1] # dystans y w poprzednim stanie
                
                if s0.food != s1.food: # Waz zjadl jablko, dodanie nagrody
                    reward = 1
                elif (abs(x1) > abs(x2) or abs(y1) > abs(y2)): # Waz zblizyl sie do jablka, dodanie nagrody
                    reward = 1
                else:
                    reward = -1 # Waz oddalil sie od jablka, dodanie kary
                    
                state_str = self._GetStateStr(s0)
                new_state_str = self._GetStateStr(s1)
                self.qvalues[state_str][a0] = (1-self.lr) * (self.qvalues[state_str][a0]) + self.lr * (reward + self.discount*max(self.qvalues[new_state_str])) # Rownanie Bellmana


    def _GetState(self, snake, food):
        snake_head = snake[-1]
        dist_x = food[0] - snake_head[0]
        dist_y = food[1] - snake_head[1]

        if dist_x > 0:
            pos_x = '1' # Jedzenie jest na prawo od weza
        elif dist_x < 0:
            pos_x = '0' # Jedzenie jest na lewo od weza
        else:
            pos_x = 'NA' # Jedzenie i waz sa w tym samym x

        if dist_y > 0:
            pos_y = '3' # Jedzenie jest pod wezem
        elif dist_y < 0:
            pos_y = '2' # Jedzenie jest nad wezem
        else:
            pos_y = 'NA' # Jedzenie i waz sa w tym samym y

        sqs = [
            (snake_head[0]-self.block_size, snake_head[1]),   
            (snake_head[0]+self.block_size, snake_head[1]),         
            (snake_head[0],                  snake_head[1]-self.block_size),
            (snake_head[0],                  snake_head[1]+self.block_size),
        ]
        
        surrounding_list = []
        for sq in sqs:
            if sq[0] < 0 or sq[1] < 0: # off screen left or top
                surrounding_list.append('1')
            elif sq[0] >= self.display_width or sq[1] >= self.display_height: # off screen right or bottom
                surrounding_list.append('1')
            elif sq in snake[:-1]: # part of tail
                surrounding_list.append('1')
            else:
                surrounding_list.append('0')
        surroundings = ''.join(surrounding_list)

        return GameState((dist_x, dist_y), (pos_x, pos_y), surroundings, food)

    def _GetStateStr(self, state):
        return str((state.position[0],state.position[1],state.surroundings))