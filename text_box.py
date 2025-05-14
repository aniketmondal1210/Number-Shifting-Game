import pygame
import threading

pygame.init()


class TextBox:
    def __init__(self, surface, text_colour=pygame.Color("black"),
                 coordinates=(0, 0), default_width=100,
                 text_font=pygame.font.Font(pygame.font.get_default_font(), 16),
                 default_text="", text_spacing=5, text_border=2, bg_colour_active=pygame.Color("white"),
                 bg_colour_passive=pygame.Color((175, 175, 175)),
                 colour_active=pygame.Color("lightskyblue3"),
                 colour_passive=pygame.Color("gray15"), extend_boundaries=False, max_characters=50,
                 cursor_visible=True, cursor_blinking_frequency=2,
                 cursor_blinking_permission=True, action_on_enter_key_press=None,
                 restricted_list=None):

        if len(default_text) > max_characters:
            default_text = default_text[:max_characters]
        self.surface = surface
        self.default_text_box_width = default_width
        self.text_rect = pygame.Rect(coordinates[0], coordinates[1], default_width, text_font.get_height() + 2 * text_spacing)
        self.text = default_text
        self.bg_colour_active = bg_colour_active
        self.bg_colour_passive = bg_colour_passive
        self.colour_active = colour_active
        self.colour_passive = colour_passive
        self.colour = colour_passive
        self.text_border = text_border
        self.text_spacing = text_spacing
        self.font = text_font
        self.text_show = None
        self.text_colour = text_colour
        self.active_state = False
        self.extend_boundaries = extend_boundaries
        self.max_characters = max_characters
        self.cursor_visible = cursor_visible
        self.cursor_blinking_frequency = cursor_blinking_frequency
        self.enter_key_action = action_on_enter_key_press

        self.current_interval = [0, 0]

        if len(self.text) != 0:
            count = 0
            st = self.text[0]
            while (self.font.render(st, True, self.text_colour).get_width()
                   + 2 * self.text_spacing) <= self.default_text_box_width:
                count += 1
                if count == len(self.text):
                    break
                st += self.text[count]
            self.current_interval[1] = count

        self.cursor_blink_status = True
        self.cursor_blinking_permission = cursor_blinking_permission

        self.is_active = True
        if self.cursor_visible and self.cursor_blinking_permission:
            t = threading.Thread(target=self.blinker)
            t.daemon = True
            t.start()

        self.cursor_pos = 0
        self.restricted_list = restricted_list
        if self.restricted_list is not None:
            self.restricted_list = list(map(str, self.restricted_list))

    def update(self):
        if not self.is_active:
            return

        if self.active_state:
            self.colour = self.colour_active
        else:
            self.colour = self.colour_passive

        self.text_show = self.font.render(self.text, True, self.text_colour)

        if self.extend_boundaries:
            self.text_rect.w = max(self.default_text_box_width, self.text_show.get_width() + 2 * self.text_spacing)
        else:
            st = self.text[self.current_interval[0]: self.current_interval[1]]
            self.text_show = self.font.render(st, True, self.text_colour)

        bg_colour = None
        if self.active_state:
            bg_colour = self.bg_colour_active
        else:
            bg_colour = self.bg_colour_passive

        pygame.draw.rect(self.surface, bg_colour, self.text_rect)
        pygame.draw.rect(self.surface, self.colour, self.text_rect, self.text_border)
        self.surface.blit(self.text_show, (self.text_rect.x + self.text_spacing,
                                           self.text_rect.y + self.text_spacing))
        self.display_cursor()

    def send_keys(self, events):
        if not self.is_active:
            return

        if events.type == pygame.KEYDOWN:
            if self.active_state:
                if events.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
                    if self.enter_key_action is not None:
                        self.enter_key_action[0](self, self.enter_key_action[1])
                if events.key == pygame.K_LEFT:
                    if self.cursor_pos != 0:
                        if not self.extend_boundaries:
                            if self.cursor_pos == self.current_interval[0]:
                                self.current_interval[0] = self.cursor_pos - 1
                                self.cursor_pos -= 1
                                count = self.current_interval[0]
                                st = self.text[self.current_interval[0]]
                                while (self.font.render(st, True, self.text_colour).get_width()
                                       + 2 * self.text_spacing) <= self.default_text_box_width:
                                    count += 1
                                    if count == len(self.text):
                                        break
                                    st += self.text[count]
                                self.current_interval[1] = count
                            else:
                                self.cursor_pos -= 1
                        else:
                            self.cursor_pos -= 1
                elif events.key == pygame.K_RIGHT:
                    if self.cursor_pos != len(self.text):
                        if not self.extend_boundaries:
                            if self.cursor_pos == self.current_interval[1]:
                                self.current_interval[1] = self.cursor_pos + 1
                                self.cursor_pos += 1
                                count = self.current_interval[1] - 1
                                st = self.text[count]
                                while (self.font.render(st, True, self.text_colour).get_width()
                                       + 2 * self.text_spacing) <= self.default_text_box_width:
                                    count -= 1
                                    if count == -1:
                                        break
                                    st += self.text[count]
                                self.current_interval[0] = count + 1
                            else:
                                self.cursor_pos += 1
                        else:
                            self.cursor_pos += 1
                elif events.key == pygame.K_UP:
                    self.cursor_pos = len(self.text)
                    if (not self.extend_boundaries) and (len(self.text) != 0):
                        self.current_interval[1] = self.cursor_pos
                        count = self.current_interval[1] - 1
                        st = self.text[count]
                        while (self.font.render(st, True, self.text_colour).get_width()
                               + 2 * self.text_spacing) <= self.default_text_box_width:
                            count -= 1
                            if count == -1:
                                break
                            st += self.text[count]
                        self.current_interval[0] = count + 1
                elif events.key == pygame.K_DOWN:
                    self.cursor_pos = 0
                    if (not self.extend_boundaries) and (len(self.text) != 0):
                        self.current_interval[0] = 0
                        count = self.current_interval[0]
                        st = self.text[self.current_interval[0]]
                        while (self.font.render(st, True, self.text_colour).get_width()
                               + 2 * self.text_spacing) <= self.default_text_box_width:
                            count += 1
                            if count == len(self.text):
                                break
                            st += self.text[count]
                        self.current_interval[1] = count

                elif events.key == pygame.K_BACKSPACE:
                    if self.cursor_pos != 0:
                        self.text = self.text[:self.cursor_pos-1] + self.text[self.cursor_pos:]
                        if not self.extend_boundaries:
                            if self.cursor_pos <= self.current_interval[0]:
                                self.current_interval[0] = self.cursor_pos - 1
                                if len(self.text) == 0:
                                    self.current_interval = [0, 0]
                                    self.cursor_pos = 0
                                else:
                                    self.cursor_pos -= 1
                                    count = self.current_interval[0]
                                    st = self.text[count]
                                    while (self.font.render(st, True, self.text_colour).get_width()
                                           + 2 * self.text_spacing) <= self.default_text_box_width:
                                        count += 1
                                        if count == len(self.text):
                                            break
                                        st += self.text[count]
                                    self.current_interval[1] = count
                            else:
                                self.cursor_pos -= 1
                                if len(self.text) == 0:
                                    self.current_interval = [0, 0]
                                    self.cursor_pos = 0
                                elif self.current_interval[1] > len(self.text):
                                    self.current_interval[1] = len(self.text)
                                    count = self.current_interval[1] - 1
                                    st = self.text[count]
                                    while (self.font.render(st, True, self.text_colour).get_width()
                                           + 2 * self.text_spacing) <= self.default_text_box_width:
                                        count -= 1
                                        if count == -1:
                                            break
                                        st += self.text[count]
                                    self.current_interval[0] = count + 1
                        else:
                            self.cursor_pos -= 1
                elif len(self.text) < self.max_characters:
                    st = events.unicode
                    check = True
                    if self.restricted_list is not None:
                        if st not in self.restricted_list:
                            check = False

                    if (st != "") and (str.isprintable(st)) and check:
                        self.text = self.text[0:self.cursor_pos] + st + self.text[self.cursor_pos:]
                        if not self.extend_boundaries:
                            if self.cursor_pos >= self.current_interval[1]:
                                self.current_interval[1] = self.cursor_pos + 1
                                self.cursor_pos += 1
                                count = self.current_interval[1] - 1
                                st = self.text[count]
                                while (self.font.render(st, True, self.text_colour).get_width()
                                       + 2 * self.text_spacing) <= self.default_text_box_width:
                                    count -= 1
                                    if count == -1:
                                        break
                                    st += self.text[count]
                                self.current_interval[0] = count + 1
                            else:
                                self.cursor_pos += 1
                                count = self.current_interval[0]
                                st = self.text[self.current_interval[0]]
                                while (self.font.render(st, True, self.text_colour).get_width()
                                       + 2 * self.text_spacing) <= self.default_text_box_width:
                                    count += 1
                                    if count == len(self.text):
                                        break
                                    st += self.text[count]
                                self.current_interval[1] = count
                        else:
                            self.cursor_pos += 1
        if events.type == pygame.MOUSEBUTTONDOWN:
            if self.text_rect.collidepoint(events.pos):
                self.active_state = True
            else:
                self.active_state = False

    def display_cursor(self):
        if not self.is_active:
            return
        dist = self.font.render(self.text[self.current_interval[0]: self.cursor_pos], True, self.text_colour).get_width()
        if self.active_state and self.cursor_visible and self.cursor_blink_status:
            pygame.draw.rect(self.surface, self.text_colour, (self.text_rect.topleft[0] + dist + self.text_spacing,
                                                              self.text_rect.topleft[1] + self.text_spacing,
                                                              2, self.font.get_height()))

    def blinker(self):
        clock = pygame.time.Clock()
        while True:
            if not self.is_active:
                return
            self.cursor_blink_status = not self.cursor_blink_status
            clock.tick(self.cursor_blinking_frequency)

    def set_inactive(self):
        self.is_active = False

    def set_active(self):
        self.is_active = True
        self.active_state = False
        if self.cursor_visible and self.cursor_blinking_permission:
            t = threading.Thread(target=self.blinker)
            t.daemon = True
            t.start()

    def get_active_status(self):
        return self.is_active

    def get_text(self):
        return self.text

    def set_text(self, text):
        if len(text) > self.max_characters:
            text = text[:self.max_characters]
        self.text = text
        self.cursor_pos = 0
        self.current_interval = [0, 0]

        if len(self.text) != 0:
            count = 0
            st = self.text[0]
            while (self.font.render(st, True, self.text_colour).get_width()
                   + 2 * self.text_spacing) <= self.default_text_box_width:
                count += 1
                if count == len(self.text):
                    break
                st += self.text[count]
            self.current_interval[1] = count
