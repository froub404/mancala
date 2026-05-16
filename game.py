"""
mancala final version? maybe? # fixed AI
version: 4-5-2026
author: me :^)
"""

# Imports
import pygame, math, random
import marble
pygame.init()

# Constants #TODO move inside game? if they don't change i dont see a point
SCREEN_WIDTH = 720
SCREEN_HEIGHT = 720
CAPTION = "mancala"
FPS = 60

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
MBLUE = (100, 150, 220)
MGREEN = (120, 190, 150)
MRED = (210, 80, 80)
MCLEAR = (220, 230, 230)
DARK_BROWN = (84, 51, 24)
WOOD = (125, 88, 57)
BEIGE = (164, 131, 97)
MARBLE_COLORS = [MBLUE, MGREEN, MRED, MCLEAR]

FONT_RS = pygame.font.Font(None, 36)
FONT_SM = pygame.font.Font(None, 48)
FONT_MD = pygame.font.Font(None, 64)
FONT_LG = pygame.font.Font(None, 96)

DEBUG = False
DELAY = 0.2
MOUSE = pygame.mouse
START = 1
PLAYING = 2
END = 3
MARBLE_COUNT = 48
P1 = [1, 2, 3, 4, 5, 6]
P2 = [7, 8, 9, 10, 11, 12]

screen = pygame.display.set_mode([SCREEN_WIDTH, SCREEN_HEIGHT])
pygame.display.set_caption(CAPTION)
clock = pygame.time.Clock()

# Game functions # TODO move to functions.py? all methods not rendering? maybe
def darken(color, factor=0.7):
    return tuple(int(c * factor) for c in color)

def find_opposite(pit):
    return (-1 * pit) + 13

class Game:
    def __init__(self):
        self.marbles = []
        self.group = []
        self.current_player = 1
        self.robot = True #TODO maybe let the player choose
        self.moving = False
        self.t = 0
        self.stage = START
        self.winner = None
        self.wins1 = 0
        self.wins2 = 0
        self.running = True
        self.buttons = {}
        self.wins1 = 0
        self.wins2 = 0
        self.current_pit = 1 #for debugging
        self.total_games = 0

    def generate_positions(self):
        positions = []
        for _ in range(500):
            angle = random.uniform(0, 2 * math.pi)
            radius = (random.uniform(0, 1) ** 0.3) * 20
            dcx = int(radius * math.cos(angle))
            dcy = int(radius * math.sin(angle))
            if (any((dcx + i, dcy) in positions for i in range(-10, 10))
                    or any((dcx, dcy + i) in positions for i in range(-10, 10))): #todo im not even sure if this does anything!
                continue
            else:
                positions.append((dcx, dcy))
        return positions

    def generate_marbles(self):
        marbles_per_pit = MARBLE_COUNT // 12
        for pit in range(1, 13):
            positions = iter(self.generate_positions())
            for _ in range(marbles_per_pit):
                dcx, dcy = next(positions)
                rw, rh = random.randint(15, 20), random.randint(15, 20)
                color = random.choice(MARBLE_COLORS)

                m = marble.Marble(color, 0, 0, (dcx, dcy), (rw, rh))
                m.pit = pit
                m.owner = 1 if pit <= 6 else 2

                self.marbles.append(m)

    def new_game(self):
        self.marbles.clear()
        self.winner = None
        self.generate_positions()
        self.generate_marbles()
        self.current_player = 1
        self.stage = PLAYING

    def return_marbles(self, pits=None, owner=None):
        mrbs = []
        if owner:
            mrbs += [m for m in self.marbles if m.owner == owner]
        if pits:
            pits = [pits] if type(pits) != list else pits
            mrbs += [m for m in self.marbles if m.pit in pits]
        return mrbs

    def capture_marbles(self, capturer, pit1, pit2):
        for m in self.marbles:
            if m.pit in [pit1, pit2]:
                m.pit = f'b{capturer}'
                m.owner = capturer

    def check_win(self):
        p1_side = self.return_marbles(P1)
        p2_side = self.return_marbles(P2)

        if self.stage == PLAYING and (not p1_side or not p2_side):
            for m in p1_side: m.pit = "b1"
            for m in p2_side: m.pit = "b2"
            b1_count = len(self.return_marbles('b1'))
            b2_count = len(self.return_marbles('b2'))
            if b1_count > b2_count:
                self.winner = 1
                self.wins1 += 1
            elif b2_count > b1_count:
                self.winner = 2
                self.wins2 += 1
            else:
                self.winner = 'tie'
            self.total_games += 1
            return True
        return False

    def draw_start_screen(self):
        start_txt = FONT_MD.render("Mancala :^)", True, BLACK)
        screen.blit(start_txt, start_txt.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2)))
        play_txt = FONT_SM.render("Press any key to play (not alt f4)", True, BLACK)
        screen.blit(play_txt, play_txt.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 + 50)))

    def draw_end_screen(self):
        if self.winner != 'tie':
            w_txt = f"PLAYER {self.winner} WINS!"
        else:
            w_txt = "IT WAS A TIE :0"
        win_txt = FONT_MD.render(w_txt, True, BLACK)
        screen.blit(win_txt, win_txt.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2)))
        again_txt = FONT_SM.render("Press any key to play again (not alt f4)", True, BLACK)
        screen.blit(again_txt, again_txt.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 + 50)))

    def fill_pit(self, pit, center):
        for m in self.return_marbles(pit):
            mw, mh = m.size[0], m.size[1]
            x = center[0] + m.location[0] - mw // 2
            y = center[1] + m.location[1] - mh // 2
            pygame.draw.ellipse(screen, m.color, [x, y, mw, mh])
            pygame.draw.ellipse(screen, darken(m.color), [x, y, mw, mh], 2)
            pygame.draw.ellipse(screen, WHITE, [x+5, y+3, 0.3*mw, 0.3*mw]) #shine? test

    def draw_board(self):
        # dimensions = 5x17
        width, height = 250, 600
        x, y = SCREEN_WIDTH//2 - width//2, SCREEN_HEIGHT//2 - height//2
        pygame.draw.rect(screen, WOOD, [x, y, width, height])
        pygame.draw.rect(screen, DARK_BROWN, [x, y, width, height], 5)

        bw, bh = width-30, height*0.12
        pygame.draw.rect(screen, BEIGE, [x + 15, y + 20, bw, bh], 0, 20)
        pygame.draw.rect(screen, BEIGE, [x + 15, y + height - 20 - bh, bw, bh], 0, 20)
        b2_center = (x + width // 2, y + 20 + bh // 2)
        self.fill_pit("b2", b2_center)
        b1_center = (x + width // 2, y + height - 20 - bh // 2)
        self.fill_pit("b1", b1_center)

        pw, ph = bw * 0.3, bw * 0.25
        px = (SCREEN_WIDTH // 2) - 20 - pw
        py = y + 35 + bh
        for i in range(2):
            for j in range(6):
                pit = j + 1 if i == 0 else 12 - j
                rect = pygame.Rect(px, py + (j * (ph + 10)), pw, ph)
                if f"pit{pit}" not in self.buttons.keys(): self.buttons[f"pit{pit}"] = rect
                pygame.draw.ellipse(screen, BEIGE, rect)
                self.fill_pit(pit, rect.center)
            px = (SCREEN_WIDTH // 2) + 20

    def draw_stats(self):
        # wins, games, current player, total marbles
        padding = 10
        start_y = 0
        txt = FONT_RS.render(f"Current Player: {self.current_player}", True, BLACK)
        screen.blit(txt, txt.get_rect(center=(SCREEN_WIDTH//2, start_y + padding)))
        start_y += txt.get_rect().h
        txt = FONT_RS.render(f"Total Games: {self.total_games}", True, BLACK)
        screen.blit(txt, txt.get_rect(center=(SCREEN_WIDTH//2, start_y + padding)))

        start_y2 = 0
        txt = FONT_RS.render(f"Wins: {self.wins2}", True, BLACK)
        screen.blit(txt, txt.get_rect(topleft=(0, start_y2)))
        start_y2 += txt.get_rect().h + padding

        start_y1 = SCREEN_HEIGHT
        txt = FONT_RS.render(f"Wins: {self.wins1}", True, BLACK)
        screen.blit(txt, txt.get_rect(bottomleft=(0, start_y1)))
        start_y1 -= txt.get_rect().h + padding

        txt = FONT_RS.render(f"Total marbles: {len(self.return_marbles(None, 2))}", True, BLACK)
        screen.blit(txt, txt.get_rect(topleft=(0, start_y2)))
        start_y2 += txt.get_rect().h + padding

        txt = FONT_RS.render(f"Total marbles: {len(self.return_marbles(None, 1))}", True, BLACK)
        screen.blit(txt, txt.get_rect(bottomleft=(0, start_y1)))

    def draw_debug(self):
        # draw current pit and marbles left in move
        padding = 10
        topx, topy = (7 * SCREEN_WIDTH) // 10, SCREEN_HEIGHT // 10
        txt = FONT_RS.render(f"Current Pit: {self.current_pit}", True, BLACK)
        screen.blit(txt, txt.get_rect(topleft=(topx, topy)))
        topy += txt.get_rect().h + padding

        txt = FONT_RS.render(f"Marbles left: {len(self.group)}", True, BLACK)
        screen.blit(txt, txt.get_rect(topleft=(topx, topy)))
        topy += txt.get_rect().h + padding

        txt = FONT_RS.render(f"Total marbles: {len(self.return_marbles(None, 2))}", True, BLACK)
        screen.blit(txt, txt.get_rect(topleft=(topx, topy)))
        topy += txt.get_rect().h + padding

        txt = FONT_RS.render(f"Total marbles: {len(self.return_marbles(None, 1))}", True, BLACK)
        screen.blit(txt, txt.get_rect(topleft=(topx, topy)))

    def process_input(self):
        """user input"""
        pos = MOUSE.get_pos()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN:
                if self.stage in [START, END]:
                    self.new_game()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if self.stage == PLAYING:
                    for p, rect in self.buttons.items():
                        if "pit" in p and rect.collidepoint(pos) and not self.moving:
                            num = int(p.split("pit")[1])
                            if len(self.return_marbles(num)) > 0:
                                if (self.current_player == 1 and num in P1) or (self.current_player == 2 and num in P2):
                                    self.move_marbles(num)

    #TODO simulation?
    def find_smartest_move(self):
        available_numbers = list(set([m.pit for m in self.return_marbles(P2)]))
        best_choice = available_numbers[0]
        highest_yield = len(self.return_marbles(find_opposite(best_choice)))
        for pit in available_numbers:
            moves = len(self.return_marbles(pit))
            if moves == (13 - pit): return pit

            destination_pit = pit + moves
            capture_pit = find_opposite(destination_pit)
            if destination_pit in P2 and len(self.return_marbles(destination_pit)) == 0:
                m_yield =  len(self.return_marbles(capture_pit))
                if m_yield > highest_yield:
                    highest_yield = m_yield
                    best_choice = pit

        return best_choice

    def stop_move(self, last_pit):
        self.moving = False
        if 'b' not in str(last_pit):
            second_pit = find_opposite(last_pit)
            if len(self.return_marbles(last_pit)) == 1 and len(self.return_marbles(second_pit)) > 0:
                if (self.current_player == 1 and last_pit in P1) or (self.current_player == 2 and last_pit in P2):
                    self.capture_marbles(self.current_player, last_pit, second_pit)
            self.current_player = 1 if self.current_player == 2 else 2
        if self.check_win() and self.stage == PLAYING:
            self.stage = END
        else:
            if self.robot and self.current_player == 2:
                self.move_marbles(self.find_smartest_move())

    def move_marbles(self, pit):
        self.group = self.return_marbles(pit)
        self.moving = True
        self.t = 0

    def update(self):
        """:/"""
        if self.moving:
            dt = clock.tick(FPS) / 1000
            self.t += dt
            if self.t >= DELAY:
                for m in self.group:
                    m.move()
                leave = self.group.pop()
                leave.update_owner()
                last_pit = leave.pit
                self.current_pit = leave.pit#debug
                if not self.group:
                    self.stop_move(last_pit)
                self.t = 0

    def render(self):
        """think this one is quite obvious"""
        screen.fill(WHITE)
        if self.stage == START:
            self.draw_start_screen()
        elif self.stage == PLAYING:
            self.draw_board()
            self.draw_stats()
        elif self.stage == END:
            self.draw_end_screen()
        if DEBUG: self.draw_debug()


    def run(self):
        """main loop"""
        while self.running:
            self.process_input()
            self.update()
            self.render()

            pygame.display.flip()
            clock.tick(FPS)

        pygame.quit()