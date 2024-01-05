#Biblioteki
import pygame
import random
import Learner

pygame.init()

#Zmienne
YELLOW = (255, 255, 102)
BLACK = (0, 0, 0)
GREEN = (0, 255, 0)
RED = (255, 0, 0)

BLOCK_SIZE = 10 
DIS_WIDTH = 1280   
DIS_HEIGHT = 720

QVALUES_N = 5     #co ile korków uczy sie
FRAMESPEED = 100    programowa #predkosc

#GRA

def GameLoop():
    global dis
    # wyświetlanie okna, tytułu i licznika
    dis = pygame.display.set_mode((DIS_WIDTH, DIS_HEIGHT))
    pygame.display.set_caption('Snake')
    clock = pygame.time.Clock()

    # Pozycja startowa węża
    x1 = DIS_WIDTH / 2
    y1 = DIS_HEIGHT / 2
    x1_change = 0
    y1_change = 0
    snake_list = [(x1,y1)]
    length_of_snake = 1

    # pozycja pierwszego jabłuszka
    foodx = round(random.randrange(0, DIS_WIDTH - BLOCK_SIZE) / 10.0) * 10.0
    foody = round(random.randrange(0, DIS_HEIGHT - BLOCK_SIZE) / 10.0) * 10.0

    dead = False
    reason = None
    while not dead:
        # Get action from agent
        action = learner.act(snake_list, (foodx,foody))
        if action == "left":
            x1_change = -BLOCK_SIZE
            y1_change = 0
        elif action == "right":
            x1_change = BLOCK_SIZE
            y1_change = 0
        elif action == "up":
            y1_change = -BLOCK_SIZE
            x1_change = 0
        elif action == "down":
            y1_change = BLOCK_SIZE
            x1_change = 0

        # Poruszanie sie weza
        x1 += x1_change
        y1 += y1_change
        snake_head = (x1,y1)
        snake_list.append(snake_head)

        # Sprawdz czy waz wyszedl za granice
        if x1 >= DIS_WIDTH or x1 < 0 or y1 >= DIS_HEIGHT or y1 < 0:
            reason = 'Granica'
            dead = True

        # Sprawdz czy je ogon
        if snake_head in snake_list[:-1]:
            reason = 'Tail'
            dead = True

        # Sprawdz czy je jabluszko
        if x1 == foodx and y1 == foody:
            foodx = x1 + (80 * 10)
            foody = y1 + (7 * 10) 
            length_of_snake += 1
            if foodx >= DIS_WIDTH or foodx < 0 or foody >= DIS_HEIGHT or foody < 0: #sprawdz czy jablko jest za granica jezeli tak to zmien kierunek jabluszka
                foodx = x1 - (80 * 10)
                foody = y1 - (7 * 10) 
                length_of_snake += 1
            
                

        # Delete the last cell since we just added a head for moving, unless we ate a food ???????? 
        if len(snake_list) > length_of_snake:
            del snake_list[0]

        # Wyswietl jablko, weza i wynik
        dis.fill(BLACK)
        DrawFood(foodx, foody)
        DrawSnake(snake_list)
        DrawScore(length_of_snake - 1)
        pygame.display.update()

        # zaktualizuj Q Table
        learner.UpdateQValues(reason)
        
        # Nastepna klatka
        clock.tick(FRAMESPEED)

    return length_of_snake - 1, reason

def DrawFood(foodx, foody):
    pygame.draw.rect(dis, GREEN, [foodx, foody, BLOCK_SIZE, BLOCK_SIZE])   

def DrawScore(score):
    font = pygame.font.SysFont("comicsansms", 35)
    value = font.render(f"Score: {score}", True, YELLOW)
    dis.blit(value, [0, 0])

def DrawSnake(snake_list):
    for x in snake_list:
        pygame.draw.rect(dis, RED, [x[0], x[1], BLOCK_SIZE, BLOCK_SIZE])


game_count = 1

learner = Learner.Learner(DIS_WIDTH, DIS_HEIGHT, BLOCK_SIZE)

while True:
    learner.Reset()
    if game_count > 100:
        learner.epsilon = 0
    else:
        learner.epsilon = .1
    score, reason = GameLoop()
    print(f"Games: {game_count}; Score: {score}; Reason: {reason}") # Output results of each game to console to monitor as agent is training
    game_count += 1
    if game_count % QVALUES_N == 0: # Save qvalues every qvalue_dump_n games
        print("Save Qvals")
        learner.SaveQvalues()