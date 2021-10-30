class cli_ui:
    def __init__(self):
        pass

    def display(self, env):
        replace_dict = {-1: "///", 0: "   ", 1: " d "}

        final_list=[["___" for _ in range(len(env.map_array[0])+2)]]
        for row in env.map_array:
            final_list.append([" | "]+list(replace_dict[tile] for tile in row)+[" | "])
        final_list.append(["___" for _ in range(len(env.map_array[0])+2)])
        final_list[0][0]=final_list[-1][0]=" __"
        final_list[0][-1]=final_list[-1][-1]="__ "

        for ad in env.agent_list:
            i,j = ad["agent_loc"]
            if final_list[i+1][j+1]==" d ": final_list[i+1][j+1] = "dX "
            else: final_list[i+1][j+1] = " X "

        print('\n'.join([''.join(['{:4}'.format(item) for item in row]) for row in final_list]))

#*********************************************************************************************************************

import os, sys
with open(os.devnull, 'w') as f:
    # disable stdout
    oldstdout = sys.stdout
    sys.stdout = f

    import pygame

    # enable stdout
    sys.stdout = oldstdout

from string import ascii_lowercase as alphabeta
from time import sleep


class Graphics:
    pixelWidth, pixelHeight, page, cubeSize = 0, 0, 0, 0

    def __init__(self, cubeSize, game):
        self.cubeSize = cubeSize
        w=len(game.foodGrid); h=w=len(game.foodGrid[0])
        self.pixelWidth, self.pixelHeight = w * self.cubeSize + w - 1, h * self.cubeSize + h - 1
        self.page = pygame.display.set_mode((self.pixelWidth + 6 * self.cubeSize, self.pixelHeight + 2 * self.cubeSize))
        self.redrawPage(game)

    def redrawPage(self, game):
        sleep(1)
        self.page.fill((0, 0, 0))
        self.drawFood(game)
        self.drawSnake(game)
        pygame.display.update()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()

    def drawFood(self, game):
        for i in range(len(game.foodGrid)):
            for j in range(len(game.foodGrid[i])):
                color = game.foodGrid[i][j] * 255 // 9
                self.colorCube(i, j, (255 - color, 255, 255 - color))

    def drawSnake(self, game):
        for snake in game.agent_list:
            if snake.body==[]: continue
            for part in snake.body:
                self.colorCube(part[0], part[1], (0,100,0))
            self.markHead(snake.body[-1][0], snake.body[-1][1])

    def drawText(self, text, color, delay):
        pygame.draw.rect(self.page, (0, 0, 0),
                         (0, self.pixelHeight, self.pixelWidth + 6 * self.cubeSize, 2 * self.cubeSize))
        pygame.font.init()
        font = pygame.font.SysFont('arial', self.cubeSize)
        text_surface = font.render(text, True, color)
        self.page.blit(text_surface, (self.cubeSize // 3, self.pixelHeight + self.cubeSize // 3))
        pygame.display.update()
        pygame.time.delay(delay)

    def drawScores(self, game):
        for i in range(game.numT):
            pygame.draw.rect(self.page, (0, 0, 0), (0, self.pixelHeight, self.pixelWidth, 2 * self.cubeSize))
            pygame.font.init()
            font = pygame.font.SysFont('arial', self.cubeSize)

            color = game.players[i].color
            text = "Team " + alphabeta[i].upper() + ": " + str(game.getTeamScore(i))
            text_surface = font.render(text, True, color)

            x = len(game.foodGrid) * (self.cubeSize + 1) + self.cubeSize // 3
            y = i * self.cubeSize + i * self.cubeSize // 3
            self.page.blit(text_surface, (x, y))

            pygame.display.update()

    def colorCube(self, i, j, color):
        pygame.draw.rect(self.page, color, (self.pixelPos(i), self.pixelPos(j), self.cubeSize, self.cubeSize))

    def markHead(self, i, j):
        circlePos = (self.pixelPos(i) + 2 * self.cubeSize // 7, self.pixelPos(j) + 2 * self.cubeSize // 5)
        pygame.draw.circle(self.page, (0, 0, 0), circlePos, self.cubeSize // 10)
        circlePos = (self.pixelPos(i) + 5 * self.cubeSize // 7, self.pixelPos(j) + 2 * self.cubeSize // 5)
        pygame.draw.circle(self.page, (0, 0, 0), circlePos, self.cubeSize // 10)

    def pixelPos(self, i):
        return i * self.cubeSize + i

    def getAction(self):
        while True:
            events = pygame.event.get()
            for event in events:
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_LEFT:
                        return 1
                    if event.key == pygame.K_RIGHT:
                        return 3
                    if event.key == pygame.K_DOWN:
                        return 0
                    if event.key == pygame.K_UP:
                        return 2


    def randColor(self, n):
        ret = 0
        r = int(random.random() * 220) + 30
        g = int(random.random() * 150)
        b = int(random.random() * 200) + 30
        step = 256 / n
        for i in range(n):
            r += step
            g += step
            b += step
            r = int(r) % 256
            g = int(g) % 256
            b = int(b) % 256
            ret = (r, g, b)
        return ret
