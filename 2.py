# -*- coding: utf-8 -*-
"""
Created on Mon Apr 17 21:18:36 2023

@author: EnHeng
"""

import time
from enum import IntEnum
import pygame
import sys
import numpy as np
import random

t = time.localtime()
date = str(t.tm_year) + '-' + str(t.tm_mon) + '-' + str(t.tm_mday) + ' ' + str(t.tm_hour) + ':' + str(t.tm_min) + ':' + str(t.tm_sec)
version = 'FiveChessV'
 
# 基础参数设置
square_size = 40  # 单格的宽度（不是格数！是为了方便绘制棋盘用的变量
chess_size = square_size // 2 - 2  # 棋子大小
web_broad = 15  # 棋盘格数+1（nxn）
map_w = web_broad * square_size  # 棋盘长度
map_h = web_broad * square_size  # 棋盘高度
info_w = 60  # 按钮界面宽度
button_w = 120  # 按钮长宽
button_h = 45
screen_w = map_w  # 总窗口长宽
screen_h = map_h + info_w
 
 
# 地图绘制模块
 
class MAP_ENUM(IntEnum):  # 用数字表示当前格的情况
    be_empty = 0,  # 无人下
    player1 = 1,  # 玩家一，执白
    player2 = 2,  # 玩家二，执黑
    out_of_range = 3,  # 出界
 
 
class Map:  # 地图类
    def __init__(self, width, height):  # 构造函数
        self.width = width
        self.height = height
        self.map = [[0 for x in range(self.width)] for y in range(self.height)]  # 存储棋盘的二维数组
        self.steps = []  # 记录步骤先后
 
    def get_init(self):  # 重置棋盘
        for y in range(self.height):
            for x in range(self.width):
                self.map[y][x] = 0
        self.steps = []
 
    def intoNextTurn(self, turn):  # 进入下一回合，交换下棋人
        if turn == MAP_ENUM.player1:
            return MAP_ENUM.player2
        else:
            return MAP_ENUM.player1
 
    def getLocate(self, x, y):  # 输入下标，返回具体位置
        map_x = x * square_size
        map_y = y * square_size
        return (map_x, map_y, square_size, square_size)  # 返回位置信息
 
    def getIndex(self, map_x, map_y):  # 输入具体位置，返回下标
        x = map_x // square_size
        y = map_y // square_size
        return (x, y)
 
    def isInside(self, map_x, map_y):  # 是否在有效范围内
        if (map_x <= 0 or map_x >= map_w or
                map_y <= 0 or map_y >= map_h):
            return False
        return True
 
    def isEmpty(self, x, y):  # 当前格子是否已经有棋子
        return (self.map[y][x] == 0)
 
    def click(self, x, y, type):  # 点击的下棋动作
        self.map[y][x] = type.value  # 下棋
        self.steps.append((x, y))  # 记录步骤信息
 
    def printChessPiece(self, screen):  # 绘制棋子
        player_one = (255, 245, 238)  # 象牙白
        player_two = (41, 36, 33)  # 烟灰
        player_color = [player_one, player_two]
        for i in range(len(self.steps)):
            x, y = self.steps[i]
            map_x, map_y, width, height = self.getLocate(x, y)
            pos, radius = (map_x + width // 2, map_y + height // 2), chess_size
            turn = self.map[y][x]
            pygame.draw.circle(screen, player_color[turn - 1], pos, radius)  # 画棋子
 
    def drawBoard(self, screen):  # 画棋盘
        color = (0, 0, 0)  # 线色
        for y in range(self.height):
            # 画横着的棋盘线
            start_pos, end_pos = (square_size // 2, square_size // 2 + square_size * y), (
                map_w - square_size // 2, square_size // 2 + square_size * y)
            pygame.draw.line(screen, color, start_pos, end_pos, 1)
        for x in range(self.width):
            # 画竖着的棋盘线
            start_pos, end_pos = (square_size // 2 + square_size * x, square_size // 2), (
                square_size // 2 + square_size * x, map_h - square_size // 2)
            pygame.draw.line(screen, color, start_pos, end_pos, 1)
 
 
# 高级AI模块

#可删
class SITUATION(IntEnum):  # 棋型
    NONE = 0,  # 无
    SLEEP_TWO = 1,  # 眠二
    LIVE_TWO = 2,  # 活二
    SLEEP_THREE = 3,  # 眠三
    LIVE_THREE = 4,  # 活三
    CHONG_FOUR = 5,  # 冲四
    LIVE_FOUR = 6,  # 活四
    LIVE_FIVE = 7,  # 活五
 
 
SITUATION_NUM = 8  # 长度
 
# 方便后续调用枚举内容
FIVE = SITUATION.LIVE_FIVE.value
L4, L3, L2 = SITUATION.LIVE_FOUR.value, SITUATION.LIVE_THREE.value, SITUATION.LIVE_TWO.value
S4, S3, S2 = SITUATION.CHONG_FOUR.value, SITUATION.SLEEP_THREE.value, SITUATION.SLEEP_TWO.value
#可删 
 
class MyChessAI():
    def __init__(self):  # 构造函数
        self.board = np.zeros((web_broad, web_broad), dtype=int)
        self.current_player = MAP_ENUM.player1
 
    def reset(self):
        self.board = np.zeros((web_broad, web_broad), dtype=int)
        self.current_player = MAP_ENUM.player1
    
    def get_state(self):
        return tuple(map(tuple, self.board))

    def make_action(self, action):
        row = action // web_broad
        col = action % web_broad
        self.board[row, col] = self.current_player
        self.current_player = MAP_ENUM.player1 if self.current_player == MAP_ENUM.player2 else MAP_ENUM.player2

    def is_legal_action(self, action):
        row = action // web_broad
        col = action % web_broad
        return self.board[row, col] == MAP_ENUM.be_empty
    
    def is_terminal(self):
        for i in range(web_broad):
            for j in range(web_broad):
                if self.board[i, j] == MAP_ENUM.be_empty:
                    continue
                if self.check_win(i, j):
                    return True
        if np.count_nonzero(self.board) == web_broad ** 2:
            return True
        return False

    def get_reward(self):
        if self.is_terminal():
            if self.current_player == MAP_ENUM.player1:
                return -1
            elif self.current_player == MAP_ENUM.player2:
                return 1
        return 0

    def check_win(self, row, col):
        color = self.board[row, col]
        for i in range(-4, 5):
            if i == 0:
                continue
            if self.check_five_in_a_row(row, col, i // 2, i % 2, color):
                return True
        return False

    def check_five_in_a_row(self, row, col, dr, dc, color):
        for i in range(-4, 5):
            if i == 0:
                continue
            r = row + i * dr
            c = col + i * dc
            if r < 0 or r >= web_broad or c < 0 or c >= web_broad:
                return False
            if self.board[r, c] != color:
                return False
        return True
    
class QLearningAgent:
    def __init__(self, alpha=0.1, gamma=0.9, epsilon=0.1):
        self.q_table = {}
        self.alpha = alpha
        self.gamma = gamma
        self.epsilon = epsilon
        self.go = MyChessAI()

    def reset(self):
        self.state = None
        self.action = None

    def get_q_value(self, state, action):
        if state not in self.q_table:
            self.q_table[state] = np.zeros((web_broad * web_broad,), dtype=np.float32)
        return self.q_table[state][action]
        
    def get_action(self, state): #参数为get_state函数的结果
        if np.random.uniform(0, 1) < self.epsilon:
            legal_actions = [i for i in range(web_broad * web_broad) if self.go.is_legal_action(i)]
            action = np.random.choice(legal_actions)
        else:
            q_values = [self.get_q_value(state, i) for i in range(web_broad * web_broad)]
            max_q_value = np.max(q_values)
            action_candidates = [i for i in range(web_broad * web_broad) if q_values[i] == max_q_value and self.go.is_legal_action(i)]
            action = np.random.choice(action_candidates)
        return action

 
 
# 主程序实现部分
 
# 控制进程按钮类（父类）
class Button:
    def __init__(self, screen, text, x, y, color, enable):  # 构造函数
        self.screen = screen
        self.width = button_w
        self.height = button_h
        self.button_color = color
        self.text_color = (255, 255, 255)  # 纯白
        self.enable = enable
        self.font = pygame.font.SysFont(None, button_h * 2 // 3)
        self.rect = pygame.Rect(0, 0, self.width, self.height)
        self.rect.topleft = (x, y)
        self.text = text
        self.init_msg()
 
    # 重写pygame内置函数，初始化我们的按钮
    def init_msg(self):
        if self.enable:
            self.msg_image = self.font.render(self.text, True, self.text_color, self.button_color[0])
        else:
            self.msg_image = self.font.render(self.text, True, self.text_color, self.button_color[1])
        self.msg_image_rect = self.msg_image.get_rect()
        self.msg_image_rect.center = self.rect.center
 
    # 根据按钮enable状态填色，具体颜色在后续子类控制
    def draw(self):
        if self.enable:
            self.screen.fill(self.button_color[0], self.rect)
        else:
            self.screen.fill(self.button_color[1], self.rect)
        self.screen.blit(self.msg_image, self.msg_image_rect)
 
 
class WhiteStartButton(Button):  # 开始按钮（选白棋）
    def __init__(self, screen, text, x, y):  # 构造函数
        super().__init__(screen, text, x, y, [(26, 173, 25), (158, 217, 157)], True)
 
    def click(self, game):  # 点击，pygame内置方法
        if self.enable:  # 启动游戏并初始化，变换按钮颜色
            game.start()
            game.winner = None
            game.multiple = False
            self.msg_image = self.font.render(self.text, True, self.text_color, self.button_color[1])
            self.enable = False
            return True
        return False
 
    def unclick(self):  # 取消点击
        if not self.enable:
            self.msg_image = self.font.render(self.text, True, self.text_color, self.button_color[0])
            self.enable = True
 
 
class BlackStartButton(Button):  # 开始按钮（选黑棋）
    def __init__(self, screen, text, x, y):  # 构造函数
        super().__init__(screen, text, x, y, [(26, 173, 25), (158, 217, 157)], True)
 
    def click(self, game):  # 点击，pygame内置方法
        if self.enable:  # 启动游戏并初始化，变换按钮颜色，安排AI先手
            game.start()
            game.winner = None
            game.multiple = False
            game.useAI = True
            self.msg_image = self.font.render(self.text, True, self.text_color, self.button_color[1])
            self.enable = False
            return True
        return False
 
    def unclick(self):  # 取消点击
        if not self.enable:
            self.msg_image = self.font.render(self.text, True, self.text_color, self.button_color[0])
            self.enable = True
 
 
class GiveupButton(Button):  # 投降按钮（任何模式都能用
    def __init__(self, screen, text, x, y):
        super().__init__(screen, text, x, y, [(230, 67, 64), (236, 139, 137)], False)
 
    def click(self, game):  # 结束游戏，判断赢家
        if self.enable:
            game.is_play = False
            if game.winner is None:
                game.winner = game.map.intoNextTurn(game.player)
            self.msg_image = self.font.render(self.text, True, self.text_color, self.button_color[1])
            self.enable = False
            return True
        return False
 
    def unclick(self):  # 保持不变，填充颜色
        if not self.enable:
            self.msg_image = self.font.render(self.text, True, self.text_color, self.button_color[0])
            self.enable = True
 
 
class MultiStartButton(Button):  # 开始按钮（多人游戏）
    def __init__(self, screen, text, x, y):  # 构造函数
        super().__init__(screen, text, x, y, [(153, 51, 250), (221, 160, 221)], True)  # 紫色
 
    def click(self, game):  # 点击，pygame内置方法
        if self.enable:  # 启动游戏并初始化，变换按钮颜色
            game.start()
            game.winner = None
            game.multiple=True
            self.msg_image = self.font.render(self.text, True, self.text_color, self.button_color[1])
            self.enable = False
            return True
        return False
 
    def unclick(self):  # 取消点击
        if not self.enable:
            self.msg_image = self.font.render(self.text, True, self.text_color, self.button_color[0])
            self.enable = True
 
 
class Game:  # pygame类,以下所有功能都是根据需要重写
    def __init__(self, caption):
        # 使用pygame之前必须初始化
        pygame.init()
        self.screen = pygame.display.set_mode([screen_w, screen_h])        # 设置主屏窗口
        pygame.display.set_caption(caption)       #设置窗口标题，即游戏名称
        self.clock = pygame.time.Clock()
        self.buttons = []
        self.buttons.append(WhiteStartButton(self.screen, 'Pick White', 10, map_h))
        self.buttons.append(BlackStartButton(self.screen, 'Pick Black', 170, map_h))
        self.buttons.append(GiveupButton(self.screen, 'Surrender', 330, map_h))
        self.buttons.append(MultiStartButton(self.screen, 'Multiple', 490, map_h))
        self.is_play = False
        self.map = Map(web_broad, web_broad)
        self.player = MAP_ENUM.player1
        self.action = None
        self.gomoku = MyChessAI() #webbroad为全局变量
        self.AI = QLearningAgent()
        self.useAI = False
        self.winner = None
        self.multiple = False
 
    def start(self):
        self.is_play = True
        self.player = MAP_ENUM.player1  # 白棋先手
        self.map.get_init()
 
    def play(self):
        # 画底板
        self.clock.tick(60)
        wood_color = (210, 180, 140)
        pygame.draw.rect(self.screen, wood_color, pygame.Rect(0, 0, map_w, screen_h))
        pygame.draw.rect(self.screen, (255, 255, 255), pygame.Rect(map_w, 0, info_w, screen_h))
        # 画按钮
        for button in self.buttons:
            button.draw()
        if self.is_play and not self.isOver():
            if self.useAI and not self.multiple:
                action = self.AI.get_action(self.gomoku.get_state())
                print("action",action)
                x,y = (action+1)%web_broad,(action+1)//web_broad
                print("x",x,"y",y)
                self.checkClick(x, y, True)
                self.useAI = False
            if self.action is not None:
                self.checkClick(self.action[0], self.action[1])
                self.action = None
            if not self.isOver():
                self.changeMouseShow()
        if self.isOver():
            self.showWinner()
            # self.buttons[0].enable = True
            # self.buttons[1].enable = True
            # self.buttons[2].enable = False
        self.map.drawBoard(self.screen)
        self.map.printChessPiece(self.screen)
 
    def changeMouseShow(self):  # 开始游戏的时候把鼠标预览切换成预览棋子的样子
        map_x, map_y = pygame.mouse.get_pos()
        x, y = self.map.getIndex(map_x, map_y)
        if self.map.isInside(map_x, map_y) and self.map.isEmpty(x, y):  # 在棋盘内且当前无棋子
            pygame.mouse.set_visible(False)
            smoke_blue = (176, 224, 230)
            pos, radius = (map_x, map_y), chess_size
            pygame.draw.circle(self.screen, smoke_blue, pos, radius)
        else:
            pygame.mouse.set_visible(True)
 
    def checkClick(self, x, y, isAI=False):  # 后续处理
        self.map.click(x, y, self.player)
        if self.gomoku.check_win(y, x):
            self.winner = self.player
            self.click_button(self.buttons[2])
        else:
            self.player = self.map.intoNextTurn(self.player)
            if not isAI:
                self.useAI = True
 
    def mouseClick(self, map_x, map_y):  # 处理下棋动作
        if self.is_play and self.map.isInside(map_x, map_y) and not self.isOver():
            x, y = self.map.getIndex(map_x, map_y)
            if self.map.isEmpty(x, y):
                self.action = (x, y)
 
    def isOver(self):  # 中断条件
        return self.winner is not None
 
    def showWinner(self):  # 输出胜者
        def showFont(screen, text, location_x, locaiton_y, height):
            font = pygame.font.SysFont(None, height)
            font_image = font.render(text, True, (255, 215, 0), (255, 255, 255))  # 金黄色
            font_image_rect = font_image.get_rect()
            font_image_rect.x = location_x
            font_image_rect.y = locaiton_y
            screen.blit(font_image, font_image_rect)
 
        if self.winner == MAP_ENUM.player1:
            str = 'White Wins!'
        else:
            str = 'Black Wins!'
        showFont(self.screen, str, map_w / 5, screen_h / 8, 100)  # 居上中，字号100
        pygame.mouse.set_visible(True)
 
    def click_button(self, button):
        if button.click(self):
            for tmp in self.buttons:
                if tmp != button:
                    tmp.unclick()
 
    def check_buttons(self, mouse_x, mouse_y):
        for button in self.buttons:
            if button.rect.collidepoint(mouse_x, mouse_y):
                self.click_button(button)
                break
 
 
# 以下为pygame1.9帮助文档的示例代码
if __name__ == '__main__':
    game = Game(version)
    while True:
        game.play()
        # 更新屏幕内容
        pygame.display.update()
        # 循环获取事件，监听事件状态
        for event in pygame.event.get():
            # 判断用户是否点了"X"关闭按钮,并执行if代码段
            if event.type == pygame.QUIT:
                # 卸载所有模块
                pygame.quit()
                # 终止程序，确保退出程序
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                mouse_x, mouse_y = pygame.mouse.get_pos()
                game.mouseClick(mouse_x, mouse_y)
                game.check_buttons(mouse_x, mouse_y)
