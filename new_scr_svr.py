#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from typing import List, Any, Union

import pygame
import random
import time
import os

SCREEN_DIM = (800, 600)


def isfloat(value):
    try:
        float(value)
        return True
    except ValueError:
        return False


def draw_help():
    """ функция описания горячих клавиш """
    gameDisplay.fill((50, 50, 50))
    font1 = pygame.font.SysFont("courier", 12)
    font2 = pygame.font.SysFont("arial", 12)
    data = []
    data.append(["F1", "Show Help"])
    data.append(["R", "Restart"])
    data.append(["P", "Pause/Play"])
    data.append(["Num+", "More points"])
    data.append(["Num-", "Less points"])
    data.append(["D", "Delete last point"])
    data.append(["S", "Make it slower"])
    data.append(["F", "Make it faster"])
    data.append(["", ""])
    data.append([str(len(control_points.points)), "Active points"])
    data.append([str(steps), "Current points"])
    if pause:
        data.append(["PAUSE", "is active"])

    pygame.draw.lines(gameDisplay, color, True, [
        (0, 0), (SCREEN_DIM[0], 0), (SCREEN_DIM[0], SCREEN_DIM[1]), (0, SCREEN_DIM[1])], 5)
    for i, text in enumerate(data):
        gameDisplay.blit(font1.render(
            text[0], True, (128, 128, 255)), (100, 100 + 30 * i))
        gameDisplay.blit(font2.render(
            text[1], True, (128, 128, 255)), (200, 100 + 30 * i))


class Vec2d:
    """ Класс двумерных векторов, описывает арифметические действия с векторами """

    def __init__(self, x_coord, y_coord):
        """ объект класса вектор содержит координаты, описывающие вектор """
        self.x = x_coord
        self.y = y_coord

    def __add__(self, second):
        """ реализация сложения векторов """
        if not isinstance(second, Vec2d):
            raise ArithmeticError("Правый операнд должен быть объектом типа вектор(Vec2d)")
        """возвращает сумму двух векторов"""
        return Vec2d(self.x + second.x, self.y + second.y)

    def __sub__(self, second):
        """ реализация вычитания векторов """
        if not isinstance(second, Vec2d):
            raise ArithmeticError("Правый операнд должен быть объектом типа вектор(Vec2d)")
        """возвращает сумму двух векторов"""
        return Vec2d(self.x - second.x, self.y - second.y)

    def __mul__(self, rate):
        """ возвращает произведение вектора на число """
        return Vec2d(self.x * rate, self.y * rate)

    def __len__(self):
        """ возвращает длину вектора """
        return (self.x ** 2 + self.y ** 2) ** 0.5

    def int_pair(self):
        """ возвращает координаты вектора кортежем """
        return self.x, self.y

    def vec(self, second):
        """ возвращает пару координат, определяющих вектор (координаты точки конца вектора),
        координаты начальной точки вектора совпадают с началом системы координат (0, 0)
        (метод для удобства и упрощения понимания - по сути же просто не нужен) """
        return second - self


class Polyline(object):
    """ Класс замкнутых ломаных, с методами, отвечающими за
    добавление новых точек, с её скоростями (Vec2d)
    пересчёт координат точек (set_points)
    отрисовку ломанной (draw_points)
    """

    def __init__(self, points=None, speeds=None, screen_size=(800, 600)):
        self.points = points or []
        self.speeds = speeds or []
        self.screen_size_x = screen_size[0]
        self.screen_size_y = screen_size[1]

    def append(self, new_point, new_speed):
        # метод добавления новой контрольной точки в ломаную
        self.points.append(new_point)
        self.speeds.append(new_speed)

    def undo(self):
        # удаление последней контролькой точки
        if len(self.points) != 0:
            self.points.pop()
            self.speeds.pop()

    def slow(self):
        for speed_id in range(len(self.speeds)):
            l = (self.speeds[speed_id].x ** 2 + self.speeds[speed_id].y ** 2) ** 0.5
            if l > 0.2:
                self.speeds[speed_id] = Vec2d(self.speeds[speed_id].x * 0.5, self.speeds[speed_id].y * 0.5)

    def fast(self):
        for speed_id in range(len(self.speeds)):
            l = (self.speeds[speed_id].x ** 2 + self.speeds[speed_id].y ** 2) ** 0.5
            if l < 3:
                self.speeds[speed_id] = Vec2d(self.speeds[speed_id].x * 1.5, self.speeds[speed_id].y * 1.5)

    def draw_curve(self, line_color, width=2):
        # метод рисования ломанной
        for point_id in range(-1, len(self.points) - 1):
            next_id = point_id + 1
            pygame.draw.line(gameDisplay, line_color,
                             (int(self.points[point_id].x), int(self.points[point_id].y)),
                             (int(self.points[next_id].x), int(self.points[next_id].y)),
                             width)

    def draw_points(self, point_color=(255, 255, 255), width=3):
        # метод рисования контрольных точек
        for control_point in self.points:
            pygame.draw.circle(gameDisplay, point_color, (int(control_point.x), int(control_point.y)), width)

    def set_points(self):
        """ метод изменения координат точек в зависимости от их скоростей """
        for point_id in range(len(self.points)):
            self.points[point_id] += self.speeds[point_id]
            if self.points[point_id].x > self.screen_size_x or self.points[point_id].x < 0:
                self.speeds[point_id] = Vec2d(- self.speeds[point_id].x, self.speeds[point_id].y)
            if self.points[point_id].y > self.screen_size_y or self.points[point_id].y < 0:
                self.speeds[point_id] = Vec2d(self.speeds[point_id].x, - self.speeds[point_id].y)


class Knot(Polyline):
    def __init__(self, control_points=[], count=0):
        super().__init__(points=control_points)
        #self.points = control_points or []
        self.count = count

    def __get_point(self, base_points, alpha, deg=None):
        if deg is None:
            deg = len(base_points) - 1
        if deg == 0:
            return base_points[0]
        return (base_points[deg] * alpha + self.__get_point(base_points, alpha, deg - 1) * (1 - alpha))

    def __get_points(self, base_points):
        alpha = 1 / self.count
        result_list = []
        for i in range(self.count):
            result_list.append(self.__get_point(base_points, i * alpha))
        return result_list

    def get_knot(self):
        if len(self.points) < 3:
            return []
        res = list()
        for point_id in range(-2, len(self.points) - 2):
            ptn = list()
            ptn.append((self.points[point_id] + self.points[point_id + 1]) * 0.5)
            ptn.append(self.points[point_id + 1])
            ptn.append((self.points[point_id + 1] + self.points[point_id + 2]) * 0.5)

            res.extend(self.__get_points(ptn))
        return res


# ----------------------
#   Основная программа
# ----------------------
if __name__ == "__main__":
    # инициализируем окно программы
    pygame.init()
    gameDisplay = pygame.display.set_mode(SCREEN_DIM)

    ''' # ставим свою картинку/иконку на окно
    i_icon = os.getcwd() + '\\scr_svr.jpg'
    icon = pygame.image.load(i_icon)
    pygame.display.set_icon(icon)
    '''
    pygame.display.set_caption("My color curve screen saver 2.0")

    # блок переменных, управляющих состоянием программы
    start_program_time = time.time()
    steps = 20
    working = True
    show_help = False
    pause = True
    control_points = Polyline(screen_size=SCREEN_DIM)

    curves = [Knot(control_points=control_points.points, count=steps)]
    # оттенок и цвет
    hue = 0
    color = pygame.Color(0)

    # блок работы программы
    while working:

        for event in pygame.event.get():
            # не вышли из программы?
            if event.type == pygame.QUIT:
                working = False
            # "слушаем" нажатия клавиш
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    working = False
                if event.key == pygame.K_r:
                    curves = [Knot(control_points=control_points.points, count=steps)]
                    control_points = Polyline(screen_size=SCREEN_DIM)
                if event.key == pygame.K_p:
                    pause = not pause
                if event.key == pygame.K_KP_PLUS:
                    steps += 3 if steps < 50 else 50
                if event.key == pygame.K_F1:
                    show_help = not show_help
                if event.key == pygame.K_KP_MINUS:
                    steps -= 3 if steps > 1 else 0
                if event.key == pygame.K_d:
                    control_points.undo()
                if event.key == pygame.K_f:
                    control_points.fast()
                if event.key == pygame.K_s:
                    control_points.slow()
                if event.key == pygame.K_n:
                    control_points = Polyline(screen_size=SCREEN_DIM)
                    curves.append(Knot(control_points=control_points.points, count=steps))

            if event.type == pygame.MOUSEBUTTONDOWN:
                control_points.append(Vec2d(event.pos[0], event.pos[1]),
                                      Vec2d(random.random() * 4 - 2, random.random() * 4 - 2))

        gameDisplay.fill((0, 0, 0))
        time_delta = time.time() - start_program_time
        hue = int(time_delta * 20 % 360)
        color.hsla = (hue, 100, 50, 100)

        for spline in curves:
            control_points.draw_points()
            spline.get_knot()
            spline.draw_curve(color)
            print("draw curve")
            if not pause:
                spline.set_points()

        if not pause:
            control_points.set_points()
        if show_help:
            draw_help()

        pygame.display.flip()

    pygame.display.quit()
    pygame.quit()
    exit(0)
