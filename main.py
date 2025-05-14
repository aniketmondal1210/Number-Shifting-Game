import pygame
import time
import text_box
import random
import copy
import time
import stopwatch

pygame.init()


class Button:
    def __init__(self, surface, button_id, coordinates=(0, 0), font=pygame.font.Font("freesansbold.ttf", 16),
                 text="", colour_passive=(50, 50, 150), colour_hover=(100, 100, 200), colour_press=None,
                 text_colour_passive=(0, 0, 0), text_colour_hover=(100, 50, 50), text_colour_press=None
                 , margin=5, action_on_enter=None, catch_continuous_press=False, shadow_width=2, passive_shadow_width=2,
                 shadow_light_colour=(255, 255, 255), shadow_dark_colour=(100, 100, 100), freeze_colour=pygame.Color("lightgrey"), bottom_shadow=True,
                 top_shadow_on_press=True, light_colour_passive_on_press=True, relaxation_time=0,
                 animation_speed=2, action_on_full_press=True):
        self.button_id = button_id
        self.surface = surface
        self.font = font
        self.margin = margin
        self.text = text
        self.colour_passive = colour_passive
        self.colour_hover = colour_hover
        self.colour_press = colour_press if colour_press is not None else self.colour_hover
        self.colour = self.colour_passive
        self.text_colour_passive = text_colour_passive
        self.text_colour_hover = text_colour_hover
        self.text_colour_press = text_colour_press if text_colour_press is not None else self.text_colour_hover
        self.text_colour = self.text_colour_passive
        self.freeze_colour = freeze_colour
        self.text_show = font.render(text, True, self.text_colour)
        self.rect = pygame.Rect((coordinates[0], coordinates[1], self.text_show.get_width() + 2 * self.margin,
                                 self.text_show.get_height() + 2 * self.margin))
        self.enter_key_action = action_on_enter
        self.catch_continuous_press = catch_continuous_press
        self.click_status = False
        self.shadow_width = shadow_width
        self.passive_shadow_width = passive_shadow_width
        self.shadow_dark_colour = shadow_dark_colour
        self.shadow_light_colour = shadow_light_colour
        self.top_shadow_on_press = top_shadow_on_press
        self.bottom_shadow = bottom_shadow
        self.light_colour_passive_on_press = light_colour_passive_on_press
        self.relax_time = relaxation_time
        self.t = -1
        self.action_on_full_press = action_on_full_press

        self.full_press_streak = 0
        self.active = True

        # For animation
        self.pos = 0
        self.pos_change = 0
        self.speed = animation_speed
        self.freeze_status = False

    def update(self):
        if not self.active:
            return
        streak = 0
        just_released = False
        mouse_pos = pygame.mouse.get_pos()
        if self.rect.collidepoint(mouse_pos):
            if pygame.mouse.get_pressed()[0]:
                self.colour = self.colour_press
                self.text_colour = self.text_colour_press
                if self.click_status:
                    streak = 1
                else:
                    streak = 0
                    if (time.time() - self.t) >= self.relax_time:
                        self.click_status = True

            else:
                self.colour = self.colour_hover
                self.text_colour = self.text_colour_hover
                if self.click_status:
                    just_released = True
                self.click_status = False
        else:
            self.colour = self.colour_passive
            self.text_colour = self.text_colour_passive
            if self.click_status:
                just_released = True
            self.click_status = False

        text_rect = pygame.Rect(0, 0, 0, 0)
        text_rect.w = self.text_show.get_width()
        text_rect.h = self.text_show.get_height()
        text_rect.center = self.rect.center
        self.text_show = self.font.render(self.text, True, self.text_colour)
        self.rect = pygame.Rect((self.rect.topleft[0], self.rect.topleft[1], self.text_show.get_width() + 2 * self.margin,
                                 self.text_show.get_height() + 2 * self.margin))

        new_rect = pygame.Rect(self.rect)
        new_rect.center = (new_rect.center[0] + self.shadow_width, new_rect.center[1] + self.shadow_width)

        new_text_rect = pygame.Rect(text_rect)
        new_text_rect.center = (new_text_rect.center[0] + self.shadow_width,
                                new_text_rect.center[1] + self.shadow_width)

        c_rect = pygame.Rect(self.rect)
        c_rect.center = (c_rect.center[0] + self.pos, c_rect.center[1] + self.pos)

        c_text_rect = pygame.Rect(text_rect)
        c_text_rect.center = (c_text_rect.center[0] + self.pos,
                              c_text_rect.center[1] + self.pos)

        # On Freeze
        if self.freeze_status:
            new_text_show = self.font.render(self.text, True, self.text_colour_passive)
            pygame.draw.rect(self.surface, self.freeze_colour, c_rect)
            self.surface.blit(new_text_show, c_text_rect)
            if self.bottom_shadow:
                pygame.draw.polygon(self.surface, self.shadow_dark_colour,
                                    (c_rect.topright,
                                     new_rect.topright,
                                     new_rect.bottomright,
                                     new_rect.bottomleft,
                                     c_rect.bottomleft,
                                     c_rect.bottomright))
            return

        pygame.draw.rect(self.surface, self.colour, c_rect)
        self.surface.blit(self.text_show, c_text_rect)
        if self.pos == 0:
            pygame.draw.line(self.surface, self.shadow_light_colour, self.rect.bottomleft, self.rect.topleft, self.passive_shadow_width)
            pygame.draw.line(self.surface, self.shadow_light_colour, self.rect.topleft, self.rect.topright, self.passive_shadow_width)

        if (self.pos == self.shadow_width) and not self.light_colour_passive_on_press:
            pygame.draw.line(self.surface, self.shadow_light_colour, new_rect.bottomleft, new_rect.bottomright,
                             self.passive_shadow_width)
            pygame.draw.line(self.surface, self.shadow_light_colour, new_rect.bottomright, new_rect.topright,
                             self.passive_shadow_width)

        if self.bottom_shadow:
            pygame.draw.polygon(self.surface, self.shadow_dark_colour,
                                (c_rect.topright,
                                 new_rect.topright,
                                 new_rect.bottomright,
                                 new_rect.bottomleft,
                                 c_rect.bottomleft,
                                 c_rect.bottomright))

        if self.top_shadow_on_press:
            pygame.draw.polygon(self.surface, self.shadow_dark_colour,
                                (c_rect.topleft,
                                 c_rect.topright,
                                 self.rect.topright,
                                 self.rect.topleft,
                                 self.rect.bottomleft,
                                 c_rect.bottomleft))

        if just_released:
            self.t = time.time()
            self.pos_change = -self.speed
            self.full_press_streak = 0
        if self.catch_continuous_press:
            streak = 0

        if self.click_status and self.action_on_full_press:
            if self.pos == self.shadow_width:
                if self.full_press_streak == 0 or self.catch_continuous_press:
                    self.full_press_streak = 1
                    if self.enter_key_action is not None:
                        if len(self.enter_key_action) == 1:
                            self.enter_key_action[0](self)
                        else:
                            self.enter_key_action[0](self, self.enter_key_action[1])
        if self.click_status and (streak == 0):
            if (self.enter_key_action is not None) and not self.action_on_full_press:
                if len(self.enter_key_action) == 1:
                    self.enter_key_action[0](self)
                else:
                    self.enter_key_action[0](self, self.enter_key_action[1])
            self.pos_change = self.speed

        # For animation
        self.pos += self.pos_change
        if self.pos <= 0:
            self.pos = 0
            if self.pos_change == -self.speed:
                self.pos_change = 0
        elif self.pos >= self.shadow_width:
            self.pos = self.shadow_width
            if self.pos_change == self.speed:
                self.pos_change = 0

    def get_text(self):
        return self.text

    def set_text(self, text):
        self.text = text

    def set_coordinates(self, tup):
        self.rect.topleft = tup

    def set_box_colour(self, colour_hover=None, colour_passive=None, colour_press=None):
        if colour_hover is not None:
            self.colour_hover = colour_hover
        if colour_passive is not None:
            self.colour_passive = colour_passive
        if colour_press is not None:
            self.colour_press = colour_press

    def set_inactive(self):
        self.active = False

    def set_active(self):
        self.active = True

    def is_active(self):
        return self.active

    def get_id(self):
        return self.button_id

    def freeze(self):
        self.freeze_status = True

    def unfreeze(self):
        self.freeze_status = False

    def is_freeze(self):
        return self.freeze_status

# Starts


class ScreenHandler:

    def __init__(self, screen_type):
        self.screen = screen_type
        test_width = pygame.font.Font("freesansbold.ttf", 20).render("Start!", True, (0, 0, 0)).get_width()

        self.pause_status = False
        self.time_pause = -1
        self.start_game_button = Button(screen, coordinates=(int(WIDTH / 2)-int(test_width/2), 3*int(HEIGHT/4)), button_id="001", text="Start!", font=pygame.font.Font("freesansbold.ttf", 20), action_on_enter=(self.change_screen_button_action, ("choose_dimensions",)), animation_speed=1)
        self.d_box = text_box.TextBox(screen, coordinates=(int(WIDTH/2)-25, int(HEIGHT/4)), max_characters=1, restricted_list=list(range(0, 10)), default_width=50)

        test_width = pygame.font.Font("freesansbold.ttf", 20).render("Next>", True, (0, 0, 0)).get_width()
        self.dimensions_next = Button(screen, coordinates=(int(WIDTH / 2)-int(test_width/2), 4*int(HEIGHT/5)), button_id="002", text="Next>", font=pygame.font.Font("freesansbold.ttf", 20), action_on_enter=(self.change_screen_button_action, ("choose_mode",)))

        test_width = pygame.font.Font("freesansbold.ttf", 20).render("Manual", True, (0, 0, 0)).get_width()
        self.manual_mode = Button(screen, coordinates=(int(WIDTH / 2)-int(test_width/2), int(HEIGHT/2)), button_id="003", text="Manual", font=pygame.font.Font("freesansbold.ttf", 20), action_on_enter=(self.change_screen_button_action, ("main_game",)))

        test_width = pygame.font.Font("freesansbold.ttf", 20).render("Challenger", True, (0, 0, 0)).get_width()
        self.challenger_mode = Button(screen, coordinates=(int(WIDTH / 2)-int(test_width/2), self.manual_mode.rect.bottom + 20), button_id="004", text="Challenger", font=pygame.font.Font("freesansbold.ttf", 20), action_on_enter=(self.change_screen_button_action, ("main_game",)))

        self.back_choose_mode = Button(screen, coordinates=(20, HEIGHT - 40), button_id="005", text="Back", font=pygame.font.Font("freesansbold.ttf", 20), action_on_enter=(self.change_screen_button_action, ("choose_dimensions",)))

        test_width = pygame.font.Font("freesansbold.ttf", 20).render("Back", True, (0, 0, 0)).get_width()
        self.back_main_game = Button(screen, coordinates=(WIDTH - test_width - 20, HEIGHT - 40), button_id="006", text="Back", font=pygame.font.Font("freesansbold.ttf", 20), action_on_enter=(self.change_screen_button_action, ("choose_mode",)))

        test_width = pygame.font.Font("freesansbold.ttf", 20).render("Play Again", True, (0, 0, 0)).get_width()
        self.back_end_screen = Button(screen, coordinates=(int(WIDTH/2) - int(test_width/2), 3*int(HEIGHT/4)), button_id="007", text="Play Again!", font=pygame.font.Font("freesansbold.ttf", 20), action_on_enter=(self.change_screen_button_action, ("choose_dimensions",)))

        self.sw = stopwatch.Stopwatch(screen, font=pygame.font.Font("freesansbold.ttf", 50), text_spacing=5,
                                      bg_colour=pygame.Color("lightgreen"))
        self.sw.set_center((int(WIDTH/2), 50))
        self.first_move = False

    def change_screen_button_action(self, button, tup):
        if (button.button_id == self.start_game_button.button_id) and (tup[0] == "choose_dimensions"):
            self.change_screen(tup[0])
        if button.button_id == self.dimensions_next.button_id:
            self.change_screen(tup[0])
        if (button.button_id == self.manual_mode.button_id) and (tup[0] == "main_game"):
            global game
            game = Game(int(self.d_box.get_text()), 100, 500, 200, 600, bg=pygame.Color("brown"), mode="manual", box_colour=pygame.Color("yellow"))
            self.change_screen(tup[0])
        if (button.button_id == self.challenger_mode.button_id) and (tup[0] == "main_game"):
            game = Game(int(self.d_box.get_text()), 100, 500, 200, 600, bg=pygame.Color("brown"), mode="challenger", box_colour=pygame.Color("yellow"))
            game.randomise()
            self.sw = stopwatch.Stopwatch(screen, font=pygame.font.Font("freesansbold.ttf", 50), text_spacing=5,
                                          bg_colour=pygame.Color("lightgreen"))
            self.sw.set_center((int(WIDTH / 2), 50))
            self.first_move = False
            game.first_move_played = False
            self.change_screen(tup[0])
        if (button.button_id == self.back_choose_mode.button_id) and (tup[0] == "choose_dimensions"):
            self.change_screen(tup[0])
        if (button.button_id == self.back_main_game.button_id) and (tup[0] == "choose_mode"):
            self.change_screen(tup[0])
        if button.button_id == self.back_end_screen.button_id:
            self.d_box.set_text("")
            self.change_screen(tup[0])

    def change_screen(self, screen_type):
        self.screen = screen_type

    @staticmethod
    def draw_highlighter():
        span = 1
        initial_counter = 255 - min(bg_colour)
        count = 0
        position = pygame.mouse.get_pos()
        curr_col = list(bg_colour)
        for i in range(initial_counter, 0, -1):
            radius = span * i
            pygame.draw.circle(screen, curr_col, position, radius)
            for j in range(3):
                curr_col[j] += 1
                if curr_col[j] > 255:
                    curr_col[j] = 255

    def handler(self):
        screen.fill(bg_colour)
        self.draw_highlighter()
        for events in pygame.event.get():
            if events.type == pygame.QUIT:
                pygame.quit()
                quit()
            if (self.screen == "main_game") and not self.pause_status:
                game.send_keys(events)
            if self.screen == "choose_dimensions":
                self.d_box.send_keys(events)
        if self.screen == "main_game":
            game.draw()
            self.back_main_game.update()
            if game.get_mode() == "challenger":
                self.sw.update()

                if not self.first_move:
                    if game.first_move_played:
                        self.first_move = True
                        self.sw.resume()

                if game.check_challenge_completed():
                    act_time = 0.2

                    if not self.pause_status:
                        self.time_pause = time.time()
                        self.pause_status = True

                        self.sw.pause()

                    if self.pause_status:
                        if (time.time() - self.time_pause) >= act_time:
                            self.pause_status = False
                            self.time_pause = -1
                            self.screen = "end_screen"
                    return

        if self.screen == "end_screen":
            gap = 20
            text_colour = (184, 134, 11)
            timer_colour = (255, 0, 0)

            new_font = pygame.font.Font("freesansbold.ttf", 64)
            text1 = new_font.render("Congratulations!", True, text_colour)
            text_rect1 = text1.get_rect()
            text_rect1.center = (int(WIDTH/2), int(HEIGHT/4))

            font = pygame.font.Font("freesansbold.ttf", 32)
            text2 = font.render("You completed the challenge!", True, text_colour)
            text_rect2 = text2.get_rect()
            text_rect2.center = (int(WIDTH/2), text_rect1.bottom + gap + int(text_rect2.h/2))

            font = pygame.font.Font("freesansbold.ttf", 32)

            text3 = font.render("TIME:", True, text_colour)
            text_rect3 = text3.get_rect()
            text_rect3.center = (int(WIDTH/2), text_rect2.bottom + (2*gap) + int(text_rect3.h/2))

            text4 = font.render(self.sw.get_time_in_hhmmss(), True, timer_colour)
            text_rect4 = text4.get_rect()
            text_rect4.center = (int(WIDTH/2), text_rect3.bottom + gap + int(text_rect4.h/2))

            self.back_end_screen.update()
            screen.blit(text1, text_rect1)
            screen.blit(text2, text_rect2)
            screen.blit(text3, text_rect3)
            screen.blit(text4, text_rect4)

        if self.screen == "choose_dimensions":
            text_colour = (0, 0, 0)
            gap = 10

            self.d_box.update()
            self.dimensions_next.update()
            font = pygame.font.Font("freesansbold.ttf", 20)
            text1 = font.render("Enter the dimensions:", True, text_colour)
            text_rect1 = text1.get_rect()

            text2 = font.render("(Ranges from 2 to 9)", True, text_colour)
            text_rect2 = text2.get_rect()

            text_rect2.center = (int(WIDTH/2), int(HEIGHT/4) - gap - int(text_rect2.h/2))
            text_rect1.center = (int(WIDTH/2), text_rect2.top - gap - int(text_rect2.h/2))

            screen.blit(text1, text_rect1)
            screen.blit(text2, text_rect2)
            if self.d_box.get_text() in ("", "0", "1"):
                self.dimensions_next.freeze()
            else:
                self.dimensions_next.unfreeze()
                # Add ints
                s_len = self.dimensions_next.rect.top - 50 - (HEIGHT/3)
                sample = Game(int(self.d_box.get_text()), (HEIGHT/3), self.dimensions_next.rect.top - 50, (WIDTH/2) - (s_len/2), (WIDTH/2) + (s_len/2), bg=pygame.Color("brown"), box_colour=pygame.Color("yellow"))
                sample.draw()

        if self.screen == "choose_mode":
            gap = 20
            text_colour = (0, 0, 0)
            font = pygame.font.Font("freesansbold.ttf", 20)

            text = font.render("Choose the mode:", True, text_colour)
            text_rect = text.get_rect()
            text_rect.center = (int(WIDTH/2), self.manual_mode.rect.top - gap - int(text_rect.h/2))
            screen.blit(text, text_rect)

            self.manual_mode.update()
            self.challenger_mode.update()
            self.back_choose_mode.update()

        if self.screen == "welcome_page":
            welcome_y_center = int(HEIGHT/4)
            text_colour = (184, 134, 11)
            gap = 50
            font1 = pygame.font.Font("freesansbold.ttf", 64)
            text1 = font1.render("WELCOME", True, text_colour)
            text_rect1 = text1.get_rect()
            text_rect1.center = (int(WIDTH/2), welcome_y_center)

            font2 = pygame.font.Font("freesansbold.ttf", 32)
            text2 = font2.render("TO THE", True, text_colour)
            text_rect2 = text2.get_rect()
            text_rect2.center = (int(WIDTH / 2), welcome_y_center+int(text_rect1.h/2)+gap)

            font3 = pygame.font.Font("freesansbold.ttf", 60)
            text3 = font3.render("NUMBER SHIFTING GAME", True, text_colour)
            text_rect3 = text3.get_rect()
            text_rect3.center = (int(WIDTH / 2), welcome_y_center + int(text_rect1.h/2)+gap+int(text_rect2.h)+gap)

            screen.blit(text1, text_rect1)
            screen.blit(text2, text_rect2)
            screen.blit(text3, text_rect3)

            self.start_game_button.update()


class Game:
    def __init__(self, num_rows, up_bound, low_bound, left_bound, right_bound, text_colour=(0, 0, 0),
                 box_colour=(255, 255, 255), bg=(0, 0, 0), edge_width=2, border_colour=(255, 255, 255), mode="Manual"):
        self.num = num_rows
        self.up_bound = up_bound
        self.low_bound = low_bound
        self.left_bound = left_bound
        self.right_bound = right_bound
        self.text_colour = text_colour
        self.edge_width = edge_width
        self.mode = mode
        # Add int
        self.width = ((right_bound - left_bound) / self.num) - (2*edge_width)
        self.box_colour = box_colour
        self.border_colour = border_colour
        self.bg = bg
        # Font
        self.font = pygame.font.Font("freesansbold.ttf", int(self.width/2))
        self.lst = []
        self.rect_lst = []
        self.empty_index = [self.num-1, self.num-1]
        self.first_move_played = False

        k = 1
        for i in range(self.num):
            rect_lst2 = []
            lst2 = []
            for j in range(self.num):
                rect = pygame.Rect((self.left_bound+(j*(self.width+ 2*self.edge_width))+self.edge_width, self.up_bound+(i*(self.width+ 2*self.edge_width))+self.edge_width, self.width, self.width))
                rect_lst2.append(rect)
                if (self.num * self.num) != k:
                    lst2.append(k)
                else:
                    lst2.append(0)
                k += 1
            self.lst.append(lst2)
            self.rect_lst.append(rect_lst2)

    def send_keys(self, events):
        if events.type == pygame.MOUSEBUTTONDOWN:
            point = pygame.mouse.get_pos()
            self.change_value("click", point=point)

        if events.type == pygame.KEYDOWN:
            if events.key == pygame.K_UP:
                self.change_value("key", key="U")
            elif events.key == pygame.K_DOWN:
                self.change_value("key", key="D")
            elif events.key == pygame.K_LEFT:
                self.change_value("key", key="L")
            elif events.key == pygame.K_RIGHT:
                self.change_value("key", key="R")

    def change_value(self, change_type, point=None, key=None):
        if change_type == "click":
            for i in range(self.num):
                for j in range(self.num):
                    if self.rect_lst[i][j].collidepoint(point):
                        if ((i == self.empty_index[0]) and (j == self.empty_index[1] - 1)) or ((i == self.empty_index[0]) and (j == self.empty_index[1] + 1)) or ((i == self.empty_index[0] - 1) and (j == self.empty_index[1])) or ((i == self.empty_index[0] + 1) and (j == self.empty_index[1])):
                            self.lst[self.empty_index[0]][self.empty_index[1]] = self.lst[i][j]
                            self.lst[i][j] = 0
                            self.empty_index = [i, j]
                            if not self.first_move_played:
                                self.first_move_played = True

        elif change_type == "key":
            if not self.first_move_played:
                self.first_move_played = True
            if key == "D":
                if self.empty_index[0] != 0:
                    self.lst[self.empty_index[0]][self.empty_index[1]] = self.lst[self.empty_index[0]-1][self.empty_index[1]]
                    self.lst[self.empty_index[0] - 1][self.empty_index[1]] = 0
                    self.empty_index[0] -= 1

            elif key == "R":
                if self.empty_index[1] != 0:
                    self.lst[self.empty_index[0]][self.empty_index[1]] = self.lst[self.empty_index[0]][self.empty_index[1]-1]
                    self.lst[self.empty_index[0]][self.empty_index[1] - 1] = 0
                    self.empty_index[1] -= 1

            elif key == "U":
                if self.empty_index[0] != (self.num - 1):
                    self.lst[self.empty_index[0]][self.empty_index[1]] = self.lst[self.empty_index[0]+1][self.empty_index[1]]
                    self.lst[self.empty_index[0] + 1][self.empty_index[1]] = 0
                    self.empty_index[0] += 1

            elif key == "L":
                if self.empty_index[1] != (self.num - 1):
                    self.lst[self.empty_index[0]][self.empty_index[1]] = self.lst[self.empty_index[0]][self.empty_index[1]+1]
                    self.lst[self.empty_index[0]][self.empty_index[1] + 1] = 0
                    self.empty_index[1] += 1

    def draw(self):
        pygame.draw.rect(screen, self.bg, (self.left_bound, self.up_bound,
                                                      (self.right_bound - self.left_bound),
                                                      (self.low_bound - self.up_bound)))
        pygame.draw.rect(screen, self.border_colour, (self.left_bound, self.up_bound,
                                                      (self.right_bound - self.left_bound),
                                                      (self.low_bound - self.up_bound)), 1)
        for i in range(self.num):
            for j in range(self.num):
                value = self.lst[i][j]
                sur = pygame.Surface((self.width, self.width))
                rect = self.rect_lst[i][j]
                if value == 0:
                    sur.fill(self.bg)
                    screen.blit(sur, rect)
                else:
                    sur.fill(self.box_colour)
                    text = self.font.render(str(value), True, self.text_colour)
                    text_rect = text.get_rect()
                    text_rect.center = sur.get_rect().center
                    sur.blit(text, text_rect)
                    screen.blit(sur, rect)

    def set_mode(self, mode):
        self.mode = mode

    def get_mode(self):
        return self.mode

    def randomise(self):
        max_turns = self.num * self.num
        orig = copy.deepcopy(self.lst)
        while self.lst == orig:
            self.recur(max_turns, copy.deepcopy(self.lst))
            self.set_empty()

    def recur(self, max_turns, prev):
        if max_turns == 0:
            return

        original = copy.deepcopy(self.lst)
        emp_in = copy.deepcopy(self.empty_index)

        pos = []
        self.change_value("key", key="U")

        pos.append(copy.deepcopy(self.lst))

        self.lst = copy.deepcopy(original)
        self.empty_index = copy.deepcopy(emp_in)

        self.change_value("key", key="L")
        pos.append(copy.deepcopy(self.lst))

        self.lst = copy.deepcopy(original)
        self.empty_index = copy.deepcopy(emp_in)

        self.change_value("key", key="R")
        pos.append(copy.deepcopy(self.lst))

        self.lst = copy.deepcopy(original)
        self.empty_index = copy.deepcopy(emp_in)

        self.change_value("key", key="D")
        pos.append(copy.deepcopy(self.lst))

        self.lst = copy.deepcopy(original)
        self.empty_index = copy.deepcopy(emp_in)

        comb = 0
        sel = []
        for i in range(4):
            if (pos[i] != original) and (pos[i] != prev):
                comb += 1
                sel.append(pos[i])

        ran = random.randint(0, len(sel)-1)
        self.lst = copy.deepcopy(sel[ran])
        self.set_empty()

        prev = copy.deepcopy(original)

        self.recur(max_turns - 1, prev)

    def set_empty(self):
        for i in range(self.num):
            for j in range(self.num):
                if self.lst[i][j] == 0:
                    self.empty_index = [i, j]

    def check_challenge_completed(self):
        k = 1
        for i in range(self.num):
            for j in range(self.num):
                if (i == self.num - 1) and (j == self.num - 1):
                    if self.lst[i][j] != 0:
                        return False
                    continue

                if self.lst[i][j] != k:
                    return False
                k += 1
        return True


WIDTH = 800
HEIGHT = 600
num_row = 4
bg_colour = (150, 150, 255)

screen = pygame.display.set_mode((WIDTH, HEIGHT))
sc = ScreenHandler("welcome_page")

clock = pygame.time.Clock()

while True:

    sc.handler()

    pygame.display.flip()
    clock.tick(60)
