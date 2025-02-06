import asyncio
import getpass
import json
import os
import websockets
from typing import Tuple

class Snake:
    def __init__(self):
        self.body = []
        self.snake_head = (None, None)
        self.snake_body = []
        self.snake_sight = {}
        self.snake_score = 0
        self.snake_range = 0
        self.snake_traverse = False
        self.food_positions = {}
        self.map_size = Tuple[int, int]
        self.map_width = 0
        self.map_height = 0
        self.steps = 0
        self.walls_positions = set()

    def update(self, state: dict) -> None:
        """Update the snake's state."""
        try:
            self.body = [tuple(segment) for segment in state["body"]]
            self.snake_head = self.body[0]
            self.snake_body = self.body[1:]
            self.snake_sight = state["sight"]
            self.snake_score = state["score"]
            self.snake_range = state["range"]
            self.snake_traverse = state["traverse"]
            self.steps = state["step"]

            self.food_positions = {}
            body_set = set(self.body)

            for x, sight_row in self.snake_sight.items():
                for y, value in sight_row.items():
                    if value == 1:
                        self.walls_positions.add((int(x), int(y)))
                    if value in {2, 3}:
                        position = (int(x), int(y))
                        if position not in body_set:
                            self.food_positions[position] = value

        except KeyError as e:
            print(f"KeyError: {e}. Stop the game.")

    def update2(self, state: dict) -> None:
        """Update the snake's state."""
        self.map_size = tuple(state["size"])
        self.map_width = self.map_size[0]
        self.map_height = self.map_size[1]

    def check_collision(self, x, y) -> bool:
        """Check if the new position collides with the snake's body.""" 
        return (x, y) in self.body

    def wrap_distance(self, head, target):
        """Calculate the shortest distance considering wrapping around map edges."""
        head_x, head_y = head
        target_x, target_y = target

        x_dist = min(abs(target_x - head_x), self.map_width - abs(target_x - head_x))
        y_dist = min(abs(target_y - head_y), self.map_height - abs(target_y - head_y))

        return x_dist + y_dist # Manhattan distance
    
    def check_nearby_snakes(self) -> set:
        """Check for nearby snakes with value 4 around the head and detect nearby heads."""
        dangerous_positions = set()
        head_x, head_y = self.snake_head

        for dx in range(-2, 3): 
            for dy in range(-2, 3): 
                if dx == 0 and dy == 0:
                    continue  
                x, y = (head_x + dx) % self.map_width, (head_y + dy) % self.map_height
                if self.snake_sight.get(str(x), {}).get(str(y)) == 4:
                    dangerous_positions.add((x, y))
        
        return dangerous_positions


    def decide_direction(self) -> str:
        """Decide the snake's direction, avoiding food 3, value 4 (other snakes), and obstacles."""
        
        if self.snake_head[0] is None or self.snake_head[1] is None:
            return "right"
        
        best_food = None
        best_distance = float("inf")
        directions = {
            "right": ((self.snake_head[0] + 1) % self.map_width, self.snake_head[1]),
            "left": ((self.snake_head[0] - 1) % self.map_width, self.snake_head[1]),
            "down": (self.snake_head[0], (self.snake_head[1] + 1) % self.map_height),
            "up": (self.snake_head[0], (self.snake_head[1] - 1) % self.map_height)
        }
        
        """ Filter food positions based on the snake's score and body positions. """
        if self.snake_score > 70:
            body_set = set(self.body[1:]) 
            food_positions_filtered = {
                pos: value for pos, value in self.food_positions.items()
                if not any(
                    (pos[0] == body_x and abs(pos[1] - body_y) <= 1) or 
                    (pos[1] == body_y and abs(pos[0] - body_x) <= 1)
                    for body_x, body_y in body_set
                )
            }
        else:
            food_positions_filtered = self.food_positions
        
        """ Check for nearby snakes with value 4 around the head. """
        nearby_snakes = self.check_nearby_snakes()
        
        """Calculate the safe and risky directions based on the food positions if the snake is not traversing."""
        if self.snake_traverse == False:
            
            safe_food_directions = []
            safe_directions = []
            risky_directions = []  
            
            for direction, (new_x, new_y) in directions.items():
                if 0 < new_x < self.map_width - 1 and 0 < new_y < self.map_height - 1:
                    if (new_x, new_y) not in self.body and food_positions_filtered.get((new_x, new_y)) != 4:
                        if (new_x, new_y) in self.walls_positions:  
                            risky_directions.append((direction, new_x, new_y))
                        elif food_positions_filtered.get((new_x, new_y)) in {2, 3}:
                            safe_food_directions.append((direction, new_x, new_y))
                        elif food_positions_filtered.get((new_x, new_y)) is None or food_positions_filtered.get((new_x, new_y)) not in {2, 3, 4}:
                            safe_directions.append((direction, new_x, new_y))
                        else:
                            risky_directions.append((direction, new_x, new_y))
                    else:
                        risky_directions.append((direction, new_x, new_y))
                else:
                    risky_directions.append((direction, new_x, new_y))

            if safe_food_directions:
                return safe_food_directions[0][0]  

            if safe_directions:
                return safe_directions[0][0] 
            
            if risky_directions:
                return risky_directions[0][0] 

        """Calculate the distance to the best food position and decide the directio, if no food acessible the code checks for safe and risky directions."""
        if self.steps < 2800:
            for position, value in food_positions_filtered.items():
                if value == 2:
                    distance = self.wrap_distance(self.snake_head, position)
                    if distance < best_distance:
                        best_distance = distance
                        best_food = position
            
            if best_food:
                target_x, target_y = best_food
                head_x, head_y = self.snake_head
                
                for direction, (new_x, new_y) in directions.items():
                    if ((direction == "right" and (target_x > head_x or (target_x < head_x and target_x + self.map_width - head_x < head_x - target_x))) or
                        (direction == "left" and (target_x < head_x or (target_x > head_x and head_x + self.map_width - target_x < target_x - head_x))) or
                        (direction == "down" and (target_y > head_y or (target_y < head_y and target_y + self.map_height - head_y < head_y - target_y))) or
                        (direction == "up" and (target_y < head_y or (target_y > head_y and head_y + self.map_height - target_y < target_y - head_y)))):

                        if not self.check_collision(new_x, new_y) and self.food_positions.get((new_x, new_y)) not in {3, 4}:
                            return direction
            
            safe_directions = []
            risky_directions = []
            for direction, (new_x, new_y) in directions.items():
                if not self.check_collision(new_x, new_y):
                    if (new_x, new_y) in nearby_snakes:
                        risky_directions.append((direction, new_x, new_y))
                    elif food_positions_filtered.get((new_x, new_y)) in {3, 4}:
                        risky_directions.append((direction, new_x, new_y))
                    else:
                        safe_directions.append((direction, new_x, new_y))
            
            for direction, (new_x, new_y) in directions.items():
                if (new_x, new_y) == self.snake_body[-1]:
                    if direction in safe_directions:
                        safe_directions.remove(direction)
            
            if safe_directions:
                return safe_directions[0][0]
            
            if risky_directions:
                return risky_directions[0][0]
            
        else:
            for position, value in food_positions_filtered.items():
                if value in {2,3}:
                    distance = self.wrap_distance(self.snake_head, position)
                    if distance < best_distance:
                        best_distance = distance
                        best_food = position
            
            if best_food:
                target_x, target_y = best_food
                head_x, head_y = self.snake_head
                
                for direction, (new_x, new_y) in directions.items():
                    if ((direction == "right" and (target_x > head_x or (target_x < head_x and target_x + self.map_width - head_x < head_x - target_x))) or
                        (direction == "left" and (target_x < head_x or (target_x > head_x and head_x + self.map_width - target_x < target_x - head_x))) or
                        (direction == "down" and (target_y > head_y or (target_y < head_y and target_y + self.map_height - head_y < head_y - target_y))) or
                        (direction == "up" and (target_y < head_y or (target_y > head_y and head_y + self.map_height - target_y < target_y - head_y)))):

                        if not self.check_collision(new_x, new_y) and food_positions_filtered.get((new_x, new_y)) not in {4}:
                            return direction
            
            safe_directions = []
            risky_directions = []
            
            for direction, (new_x, new_y) in directions.items():
                if not self.check_collision(new_x, new_y):
                    if (new_x, new_y) in nearby_snakes:
                        risky_directions.append((direction, new_x, new_y))
                    elif food_positions_filtered.get((new_x, new_y)) in {3, 4}:
                        risky_directions.append((direction, new_x, new_y))
                    else:
                        safe_directions.append((direction, new_x, new_y))
            
            for direction, (new_x, new_y) in directions.items():
                if (new_x, new_y) == self.snake_body[-1]:
                    if direction in safe_directions:
                        safe_directions.remove(direction)
            
            if safe_directions:
                return safe_directions[0][0]
            
            if risky_directions:
                return risky_directions[0][0]
        
        # fallback
        return "right"
    
async def agent_loop(server_address="localhost:8000", agent_name="student"):
    """Example client loop with consecutive left step tracking."""
    async with websockets.connect(f"ws://{server_address}/player") as websocket:
        await websocket.send(json.dumps({"cmd": "join", "name": agent_name}))

        snake = Snake()
        first_state = True
        default_move_count = 0
        moves_made = 0
        consecutive_left_steps = 0

        while True:
            try:
                state = json.loads(await websocket.recv())
                print(f"Received state: {state}")

                # Update the snake's state
                if not first_state:
                    snake.update(state)
                else:
                # Update the map size
                    snake.update2(state)
                    

                first_state = False

                direction = snake.decide_direction()

                print(f"Decided direction: {direction}")

                if direction == 'right':
                    default_move_count += 1
                    consecutive_left_steps = 0
                    await websocket.send(json.dumps({"cmd": "key", "key": "d"}))
                elif direction == 'up':
                    default_move_count = 10
                    consecutive_left_steps = 0
                    await websocket.send(json.dumps({"cmd": "key", "key": "w"}))
                elif direction == 'down':
                    default_move_count = 10
                    consecutive_left_steps = 0
                    await websocket.send(json.dumps({"cmd": "key", "key": "s"}))
                    moves_made += 1
                elif direction == 'left':
                    default_move_count = 0
                    consecutive_left_steps += 1


                    
                    if snake.snake_traverse:
                        if consecutive_left_steps >= 2:
                            head_x, head_y = snake.snake_head

                            path_is_safe = True
                            for i in range(1, 4):
                                check_position = (head_x, (head_y + i) % snake.map_height)
                                if (snake.snake_sight.get(str(check_position[0]), {}).get(str(check_position[1])) == 4 or
                                    snake.check_collision(*check_position)) or snake.food_positions.get(check_position) == 3:
                                    path_is_safe = False
                                    break

                            if path_is_safe:
                                await websocket.send(json.dumps({"cmd": "key", "key": "s"}))
                                consecutive_left_steps = 0
                            else:
                                head_x, head_y = snake.snake_head
                                next_position_left = ((head_x - 1) % snake.map_width, head_y)
                                
                                if snake.check_collision(*next_position_left) or snake.food_positions.get(next_position_left) == 4:
                                    next_position_up = (head_x, (head_y - 1) % snake.map_height)
                                    if snake.check_collision(*next_position_up) or snake.food_positions.get(next_position_up) == 4:
                                        next_position_down = (head_x, (head_y + 1) % snake.map_height)
                                        if snake.check_collision(*next_position_down) or snake.food_positions.get(next_position_down) == 4:
                                            print("All directions are blocked. Taking defensive action.")
                                            await websocket.send(json.dumps({"cmd": "key", "key": "s"}))  
                                            default_move_count = 23
                                        else:
                                            await websocket.send(json.dumps({"cmd": "key", "key": "s"}))  
                                    else:
                                        await websocket.send(json.dumps({"cmd": "key", "key": "w"}))  
                                else:
                                    await websocket.send(json.dumps({"cmd": "key", "key": "a"}))  

                        else:
                            await websocket.send(json.dumps({"cmd": "key", "key": "a"}))  

                    else:
                        if consecutive_left_steps >= 48:
                            head_x, head_y = snake.snake_head
                            next_position = (head_x, (head_y + 1) % snake.map_height)
                            
                            if not snake.check_collision(*next_position) and snake.food_positions.get(next_position) not in {4}:
                                await websocket.send(json.dumps({"cmd": "key", "key": "s"}))
                                consecutive_left_steps = 0
                            else:
                                await websocket.send(json.dumps({"cmd": "key", "key": "a"}))
                        else:
                            await websocket.send(json.dumps({"cmd": "key", "key": "a"}))

                """ if snake is traversing it will move down after 24 right moves, if snake score is less than 50 it will move down after 24 right moves and 3 down moves, if snake score is greater than 50 it will move down after 20 right moves and 3 down moves."""
                if snake.snake_traverse == True:
                    if snake.snake_score < 50:
                        if default_move_count >= 24:
                            if moves_made < 3:
                                head_x, head_y = snake.snake_head
                                
                                path_is_safe = True
                                for i in range(1, 4):
                                    check_position = (head_x, (head_y + i) % snake.map_height)
                                    if (snake.snake_sight.get(str(check_position[0]), {}).get(str(check_position[1])) == 4 or
                                        snake.check_collision(*check_position)):
                                        path_is_safe = False
                                        break

                                next_position = (head_x, (head_y + 1) % snake.map_height)
                                
                                if path_is_safe and not snake.check_collision(*next_position) and snake.food_positions.get(next_position) != 3:
                                    await websocket.send(json.dumps({"cmd": "key", "key": "s"}))
                                    moves_made += 1
                                else:
                                    head_x, head_y = snake.snake_head
                                    next_position = (head_x + 1) % snake.map_width, head_y 
                                    
                                    if snake.check_collision(*next_position) or snake.food_positions.get(next_position) == 4:
                                        next_position_left = (head_x - 1) % snake.map_width, head_y
                                        if snake.check_collision(*next_position_left) or snake.food_positions.get(next_position_left) == 4:
                                            next_position_down = head_x, (head_y + 1) % snake.map_height
                                            if snake.check_collision(*next_position_down) or snake.food_positions.get(next_position_down) == 4:
                                                next_position_up = head_x, (head_y - 1) % snake.map_height
                                                if snake.check_collision(*next_position_up) or snake.food_positions.get(next_position_up) == 4:
                                                    print("All directions are blocked. Taking defensive action.")
                                                    await websocket.send(json.dumps({"cmd": "key", "key": "s"}))
                                                else:
                                                    await websocket.send(json.dumps({"cmd": "key", "key": "w"}))
                                            else:
                                                await websocket.send(json.dumps({"cmd": "key", "key": "s"}))
                                        else:
                                            await websocket.send(json.dumps({"cmd": "key", "key": "a"}))
                                    else:
                                        await websocket.send(json.dumps({"cmd": "key", "key": "d"}))
                                        default_move_count += 1


                            if moves_made >= 3:
                                default_move_count = 0
                                moves_made = 0

                    else:
                        if default_move_count >= 20:
                            if moves_made < 3:
                                head_x, head_y = snake.snake_head
                                
                                path_is_safe = True
                                for i in range(1, 4):
                                    check_position = (head_x, (head_y + i) % snake.map_height)
                                    if (snake.snake_sight.get(str(check_position[0]), {}).get(str(check_position[1])) == 4 or
                                        snake.check_collision(*check_position)):
                                        path_is_safe = False
                                        break

                                next_position = (head_x, (head_y + 1) % snake.map_height)
                                
                                if path_is_safe and not snake.check_collision(*next_position) and snake.food_positions.get(next_position) != 3:
                                    await websocket.send(json.dumps({"cmd": "key", "key": "s"}))
                                    moves_made += 1
                                else:
                                    head_x, head_y = snake.snake_head
                                    next_position = (head_x + 1) % snake.map_width, head_y
                                    
                                    if snake.check_collision(*next_position) or snake.food_positions.get(next_position) == 4:
                                        next_position_left = (head_x - 1) % snake.map_width, head_y
                                        if snake.check_collision(*next_position_left) or snake.food_positions.get(next_position_left) == 4:
                                            next_position_down = head_x, (head_y + 1) % snake.map_height
                                            if snake.check_collision(*next_position_down) or snake.food_positions.get(next_position_down) == 4:
                                                next_position_up = head_x, (head_y - 1) % snake.map_height
                                                if snake.check_collision(*next_position_up) or snake.food_positions.get(next_position_up) == 4:
                                                    print("All directions are blocked. Taking defensive action.")
                                                    await websocket.send(json.dumps({"cmd": "key", "key": "s"}))
                                                else:
                                                    await websocket.send(json.dumps({"cmd": "key", "key": "w"}))
                                            else:
                                                await websocket.send(json.dumps({"cmd": "key", "key": "s"}))
                                        else:
                                            await websocket.send(json.dumps({"cmd": "key", "key": "a"}))
                                    else:
                                        await websocket.send(json.dumps({"cmd": "key", "key": "d"}))
                                        default_move_count += 1


                            if moves_made >= 3:
                                default_move_count = 0
                                moves_made = 0

                # if snake is not traversing default move
                else:
                    default_move_count = 0
                    moves_made = 0

            except websockets.exceptions.ConnectionClosedOK:
                print("The server has disconnected")
                return

# DO NOT CHANGE THE LINES BELOW
loop = asyncio.get_event_loop()
SERVER = os.environ.get("SERVER", "localhost")
PORT = os.environ.get("PORT", "8000")
NAME = os.environ.get("NAME", getpass.getuser())
NAME = "student1"
loop.run_until_complete(agent_loop(f"{SERVER}:{PORT}", NAME))
