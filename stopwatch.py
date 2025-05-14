import pygame
import time

pygame.init()


class Stopwatch:
    def __init__(self, surface, coordinates=(0, 0), font=pygame.font.Font("freesansbold.ttf", 16),
                 text_colour=(0, 0, 0), text_spacing=2, bg_colour=(255, 255, 255), border_width=2,
                 border_colour=pygame.Color("lightskyblue3")):
        self.surface = surface
        self.font = font
        self.text = "00:00:00.00"
        self.text_colour = text_colour
        self.text_spacing = text_spacing
        self.text_show = self.font.render(self.text, True, self.text_colour)
        self.rect = pygame.Rect(coordinates[0], coordinates[1], self.text_show.get_width() + (2 * self.text_spacing),
                                self.text_show.get_height() + (2 * self.text_spacing))
        self.bg_colour = bg_colour
        self.border_width = border_width
        self.border_colour = border_colour
        self.center = self.rect.center
        self.init_width = self.rect.w

        self.init_time = 0.0
        self.count_time = -1
        self.pause_status = True

    def update(self):
        if self.pause_status:
            self.text = self.convert(self.init_time)
        else:
            tim = (time.time() - self.count_time) + self.init_time
            self.text = self.convert(tim)

        self.text_show = self.font.render(self.text, True, self.text_colour)
        self.rect.w = max(self.rect.w, self.text_show.get_width() + (2 * self.text_spacing))
        self.rect.h = max(self.rect.h, self.text_show.get_height() + (2 * self.text_spacing))
        self.rect.center = self.center

        pygame.draw.rect(self.surface, self.bg_colour, self.rect)
        pygame.draw.rect(self.surface, self.border_colour, self.rect, self.border_width)
        text_rect = self.text_show.get_rect()
        text_rect.center = self.rect.center
        self.surface.blit(self.text_show, text_rect)

    def resume(self):
        if not self.pause_status:
            return
        self.pause_status = False
        self.count_time = time.time()

    def pause(self):
        if self.pause_status:
            return
        self.pause_status = True
        self.init_time += time.time() - self.count_time
        self.count_time = -1

    def is_paused(self):
        return self.pause_status

    def reset(self):
        self.pause()
        self.init_time = 0.0
        self.count_time = -1

    def get_time_in_sec(self):
        if self.pause_status:
            return self.init_time
        else:
            tim = (time.time() - self.count_time) + self.init_time
            return tim

    def get_time_in_hhmmss(self):
        if self.pause_status:
            time_st = self.convert(self.init_time)
        else:
            tim = (time.time() - self.count_time) + self.init_time
            time_st = self.convert(tim)
        return time_st

    def set_center(self, tup):
        self.center = tup

    def get_center(self):
        return self.center

    def convert(self, t):
        dec = t - int(t)
        t = int(t)
        hours = t // 3600
        t = t % 3600
        mint = t // 60
        t = t % 60
        sec = t
        shours = str(hours)
        if len(shours) == 1:
            shours = "0" + shours
        smint = str(mint)
        if len(smint) == 1:
            smint = "0" + smint
        ssec = str(sec)
        if len(ssec) == 1:
            ssec = "0" + ssec
        sdec = str(dec)[2:]
        if len(sdec) == 1:
            sdec = sdec + "0"
        else:
            sdec = sdec[:2]

        return shours + ":" + smint + ":" + ssec + "." + sdec
