#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from typing import List, Any, Union

import pygame
import random
import time

SCREEN_DIM = (800, 600)


def draw_help(max_limit):
    """ функция описания горячих клавиш """
    gameDisplay.fill((50, 50, 50))
    font1 = pygame.font.SysFont("arial", 16)
    font2 = pygame.font.SysFont("serif", 16)
    data = []
    data.append(["F1", "Show/Hide Help"])
    data.append(["F2", f"Show/Hide control points (mode = {show_control_point})"])
    data.append(["R", "Restart"])
    data.append(["P", "Pause/Play"])
    data.append(["Num +", "More smoothing point"])
    data.append(["Num -", "Less smoothing point"])
    data.append(["Left MB", "Add new control point"])
    data.append(["Del", "Delete last point"])
    data.append(["Right MB", "Delete select point"])
    data.append(["S", "Make it slower"])
    data.append(["F", "Make it faster"])
    data.append(["N", "Create a new curve"])
    data.append(["F8", "Delete active curve"])
    data.append(["Page Up", "Activate the previous curve"])
    data.append(["Page Down", "Activate the next curve"])
    data.append(["", ""])
    data.append([f"{active_curve + 1}", "Active curve id"])
    if len(new_curves) == max_limit:
        data.append([f"{max_limit}", "MAXIMUM number of curves created"])
    else:
        data.append([f"{len(new_curves)}", "number of curves created"])

    if len(new_curves[active_curve].points) == max_limit * 10:
        data.append([f"{max_limit * 10}", "MAXIMUM number of points created"])
    else:
        data.append([str(len(new_curves[active_curve].points)), "Active points"])

    data.append([str(new_curves[active_curve].steps), "Current points"])
    if pause:
        data.append(["PAUSE", "is active"])

    pygame.draw.lines(gameDisplay, color, True, [
        (0, 0), (SCREEN_DIM[0], 0), (SCREEN_DIM[0], SCREEN_DIM[1]), (0, SCREEN_DIM[1])], 5)
    for i, text in enumerate(data):
        gameDisplay.blit(font1.render(
            text[0], True, (128, 128, 255)), (100, 50 + 24 * i))
        gameDisplay.blit(font2.render(
            text[1], True, (128, 128, 255)), (220, 50 + 24 * i))


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

    def __init__(self, points=None, speeds=None, screen_size=(800, 600), steps=15):
        self.points = points or []
        self.speeds = speeds or []
        self.screen_size_x = screen_size[0]
        self.screen_size_y = screen_size[1]
        self.steps = steps


    def append(self, new_point, new_speed):
        # метод добавления новой контрольной точки в ломаную
        self.points.append(new_point)
        self.speeds.append(new_speed)

    def del_point(self, del_point=None):
        if del_point is None:
            if len(self.points) != 0:
                self.points.pop()
                self.speeds.pop()
        else:
            for p_id in range(len(self.points)):
                if ((del_point.x - 15) < self.points[p_id].x < (del_point.x + 15)) and \
                        ((del_point.y - 15) < self.points[p_id].y < (del_point.y + 15)):
                    self.points.pop(p_id)
                    self.speeds.pop(p_id)
                    break

    def change_speed(self, multiplier):
        for speed_id in range(len(self.speeds)):
            l = (self.speeds[speed_id].x ** 2 + self.speeds[speed_id].y ** 2) ** 0.5
            if (multiplier < 1 and l > 0.05) or (multiplier > 1 and l < 4):
                self.speeds[speed_id] = self.speeds[speed_id] * multiplier

    @staticmethod
    def draw_curve(points_to_draw, line_color, width=2):
        # метод рисования ломанной
        for point_id in range(-1, len(points_to_draw) - 1):
            next_id = point_id + 1
            pygame.draw.line(gameDisplay, line_color,
                             (int(points_to_draw[point_id].x), int(points_to_draw[point_id].y)),
                             (int(points_to_draw[next_id].x), int(points_to_draw[next_id].y)),
                             width)

    @staticmethod
    def draw_points(points_to_draw, point_color=(255, 255, 255), width=3):
        # метод рисования контрольных точек
        for control_point in points_to_draw:
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

    def __init__(self, points=None, screen_size=(800, 600), steps=30):
        self.points = points or []
        self.screen_size_x = screen_size[0]
        self.screen_size_y = screen_size[1]
        self.steps = steps

    def __get_point(self, base_points, alpha, deg=None):
        if deg is None:
            deg = len(base_points) - 1
        if deg == 0:
            return base_points[0]
        return (base_points[deg] * alpha + self.__get_point(base_points, alpha, deg - 1) * (1 - alpha))

    def __get_points(self, base_points):
        result_list = []
        if self.steps != 0:
            alpha = 1 / self.steps
            for i in range(self.steps):
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

    pygame.display.set_caption("My screen saver 2.0")

    # блок переменных, управляющих состоянием программы
    start_program_time = time.time()

    working = True
    show_help = True
    pause = True
    new_curves = [Polyline(screen_size=SCREEN_DIM)]
    active_curve = 0
    show_control_point = "Show"
    max_limit = 15

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
                    if show_help:
                        show_help = not show_help
                    else:
                        working = False
                if event.key == pygame.K_r:
                    new_curves = [Polyline(screen_size=SCREEN_DIM)]
                    active_curve = 0

                if event.key == pygame.K_SPACE or event.key == pygame.K_p:
                    pause = not pause
                if event.key == pygame.K_UP or event.key == pygame.K_KP_PLUS:
                    if new_curves[active_curve].steps < 10:
                        mera = 1
                    elif new_curves[active_curve].steps < 20:
                        mera = 3
                    else:
                        mera = 5
                    new_curves[active_curve].steps += mera if new_curves[active_curve].steps < 37 else 0
                if event.key == pygame.K_F1:
                    show_help = not show_help
                if event.key == pygame.K_F2:
                    if show_control_point == "Show":
                        show_control_point = "Hide"
                    else:
                        show_control_point = "Show"
                if event.key == pygame.K_DOWN or event.key == pygame.K_KP_MINUS:
                    if new_curves[active_curve].steps < 10:
                        mera = 1
                    elif new_curves[active_curve].steps < 20:
                        mera = 3
                    else:
                        mera = 5
                    new_curves[active_curve].steps -= mera if new_curves[active_curve].steps > 1 else 0
                if event.key == pygame.K_BACKSPACE:
                    new_curves[active_curve].del_point()
                if event.key == pygame.K_f:
                    new_curves[active_curve].change_speed(1.3)
                if event.key == pygame.K_s:
                    new_curves[active_curve].change_speed(0.8)
                if event.key == pygame.K_n:
                    if len(new_curves) < max_limit:
                        new_curves.append(Polyline(screen_size=SCREEN_DIM))
                        active_curve = len(new_curves) - 1
                    else:
                        show_help = not show_help
                if event.key == pygame.K_F8:
                    if len(new_curves) > 1:
                        new_curves.pop(active_curve)
                        if active_curve == 0:
                            active_curve = 0
                        else:
                            active_curve -= 1
                    else:
                        new_curves = [Polyline(screen_size=SCREEN_DIM)]
                        active_curve = 0
                if event.key == pygame.K_PAGEUP:
                    if active_curve != 0:
                        active_curve -= 1
                    else:
                        active_curve = len(new_curves) - 1

                if event.key == pygame.K_PAGEDOWN:
                    if active_curve != len(new_curves) - 1:
                        active_curve += 1
                    else:
                        active_curve = 0

            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    if len(new_curves[active_curve].points) < max_limit * 10:
                        new_curves[active_curve].append(Vec2d(event.pos[0], event.pos[1]),
                                                        Vec2d(random.random() * 4 - 2, random.random() * 4 - 2))
                    else:
                        show_help = not show_help

                elif event.button == 3:
                    new_curves[active_curve].del_point(Vec2d(event.pos[0], event.pos[1]))

        gameDisplay.fill((0, 0, 0))
        time_delta = time.time() - start_program_time
        hue = int(time_delta * 20 % 360)

        smooth_curve = []
        for spline_id in range(len(new_curves)):
            if active_curve == spline_id and show_control_point == "Show":
                new_curves[active_curve].draw_points(new_curves[active_curve].points)
            smooth_curve = Knot(points=new_curves[spline_id].points, steps=new_curves[spline_id].steps)

            color.hsla = ((hue + 50 * spline_id) % 360, 100, 50, 100)
            Polyline.draw_curve(smooth_curve.get_knot(), color)
            if not pause:
                new_curves[spline_id].set_points()

        if show_help:
            draw_help(max_limit)

        pygame.display.flip()

    pygame.display.quit()
    pygame.quit()
    exit(0)
