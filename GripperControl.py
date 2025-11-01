import pygame
import pygame.gfxdraw
import math
import os
import sys
import time
import argparse
from serial_controller import SerialController

def main():
    parser = argparse.ArgumentParser(description="Gripper Control Panel")
    parser.add_argument("--port", type=str, default="COM4",
                        help="Serial port for Arduino connection (e.g. COM3 or /dev/cu.usbmodem101)")
    args = parser.parse_args()

    sc = SerialController(args.port)
    print(f"Connected to serial port: {args.port}")

# ===== Color Theme =====
COLOR_BG         = (15, 15, 15)
COLOR_CARD_BG    = (30, 30, 30)
COLOR_TRACK      = (70, 70, 70)
COLOR_KNOB       = (60, 160, 255)
COLOR_TRACK_HL   = (120, 120, 120)
COLOR_TEXT       = (240, 240, 240)

COLOR_BTN_G      = (0, 168, 84)
COLOR_BTN_R      = (230, 0, 0)
COLOR_BTN_LABEL  = (255, 255, 255)

MODEL_BTN_BG     = (40, 40, 40)
MODEL_BTN_BORDER = (100, 100, 100)
MODEL_BTN_TEXT   = (240, 240, 240)

COLOR_PANEL_BG           = (45, 45, 45)
COLOR_PANEL_ITEM         = (60, 60, 60)
COLOR_PANEL_ITEM_HOVER   = (80, 80, 80)

COLOR_IND_X = (120, 120, 120)   
COLOR_IND_T = (0, 255, 0)     
COLOR_IND_F = (255, 0, 0)     

# ===== UI POSITION =====
WIN_W, WIN_H = 900, 900
SLIDER_X, SLIDER_W = 180, 400
SLIDER_TOP, SLIDER_SPACING, SLIDER_H = 150, 60, 20
ACTPOS = [[100, 630], [330, 450], [550, 630], [330, 800]]

BEND_BTN_RECT = pygame.Rect(780, 80, 100, 40)
bend_pressed = False
logging_bend = False
bend_file = None


KNOB_MARGIN = 8

FLAG_BOX_RECT = pygame.Rect(550, 80, 40, 40)
MODEL_BTN_RECT = pygame.Rect(150, 80, 220, 36)
MODEL_ITEM_H = 30
MODEL_DROPDOWN_X = MODEL_BTN_RECT.x
MODEL_DROPDOWN_Y = MODEL_BTN_RECT.bottom + 4
MODEL_DROPDOWN_W = MODEL_BTN_RECT.width
STOP_BTN_RECT = pygame.Rect(650, 80, 100, 40)

GRIP_CENTER = [[225, 410], [684, 410], [684, 868], [225, 868]]

# ===== Initialize Pygame =====
pygame.init()
screen = pygame.display.set_mode((WIN_W, WIN_H))
pygame.display.set_caption("Arduino Controller")
FONT_NAME = "Calibri"
FONT_SIZE_LARGE = 24
FONT_SIZE_SMALL = 20
font = pygame.font.SysFont(FONT_NAME, FONT_SIZE_LARGE)
bold_font = pygame.font.SysFont(FONT_NAME, FONT_SIZE_LARGE, bold=True)
small_font = pygame.font.SysFont(FONT_NAME, FONT_SIZE_SMALL)

# ===== Initialize Variable =====
curPre = [0, 0, 0, 0]
stopFlag = ['T', 'T', 'T', 'T']
graspFlag = [0, 0, 0, 0]


values = [0.0, 0.0, 0.0, 0.0]
flag = 'R'
dragging_index = None
panel_open = False
current_preset_name = "Customize"
preset_item_rects = {}

flag_pressed = False
stop_pressed = False
model_pressed = False
slider_pressed = [False, False, False, False]
PRESETS = {
    "Square Small":    [0.0, 0.0, 0.0, 0.0],
    "Square Large":    [0.8, 0.8, 0.8, 0.8],
    "Trapezoid Small": [1.0, 0.0, 0.0, 0.0],
    "Trapezoid Large": [1.0, 1.0, 1.0, 0.0],
    "Kite":            [1.0, 1.0, 0.0, 0.0],
    "Rectangle":       [1.0, 0.0, 1.0, 0.0],
    "Advocado":        [0.0, 0.5, 0.0, 0.5],
}


def match_preset(val_list):
    for name, preset in PRESETS.items():
        if all(math.isclose(a, b, abs_tol=1e-3) for a, b in zip(val_list, preset)):
            return name
    return "Customize"

def set_values_and_send(new_vals):
    global values, current_preset_name
    values = [max(0.0, min(1.0, float(v))) for v in new_vals]
    sc.sendActState(values)
    current_preset_name = match_preset(values)


def get_slider_index(mx, my):
    for i in range(4):
        y = SLIDER_TOP + i * SLIDER_SPACING
        if y <= my <= y + SLIDER_H and SLIDER_X <= mx <= SLIDER_X + SLIDER_W:
            return i
    return None

def draw_bend_button():
    global bend_pressed, logging_bend
    mouse_pos = pygame.mouse.get_pos()
    is_hovered = BEND_BTN_RECT.collidepoint(mouse_pos)
    base_color = (0, 120, 200)
    hover_color = (0, 150, 240) if is_hovered else base_color

    rect = BEND_BTN_RECT.inflate(4, 4) if bend_pressed else BEND_BTN_RECT
    pygame.draw.rect(screen, hover_color, rect, border_radius=10)
    label_text = "Stop Log" if logging_bend else "Log BS"
    label = bold_font.render(label_text, True, (255, 255, 255))
    text_rect = label.get_rect(center=rect.center)
    screen.blit(label, text_rect)


def draw_title_bar():
    title = bold_font.render("Gripper Control Panel", True, COLOR_TEXT)
    screen.blit(title, (WIN_W // 2 - title.get_width() // 2, 20))

def draw_slider(index, value):
    x = SLIDER_X
    y = SLIDER_TOP + index * SLIDER_SPACING

    knob_min_x = x + KNOB_MARGIN
    knob_max_x = x + SLIDER_W - KNOB_MARGIN
    knob_x = int(knob_min_x + value * (knob_max_x - knob_min_x))
    knob_y = y + SLIDER_H // 2

    pygame.draw.rect(screen, COLOR_TRACK, (x, y, SLIDER_W, SLIDER_H), border_radius=8)

    filled_width = knob_x - x
    if filled_width > 0:
        pygame.draw.rect(screen, COLOR_TRACK_HL, (x, y, filled_width, SLIDER_H), border_radius=8)

    knob_radius = 12 if slider_pressed[index] else 10
    pygame.gfxdraw.filled_circle(screen, knob_x, knob_y, knob_radius, COLOR_KNOB)
    pygame.gfxdraw.aacircle(screen, knob_x, knob_y, knob_radius, COLOR_KNOB)

    label = bold_font.render(f"Actuator {index + 1}: {value:.2f}", True, COLOR_TEXT)
    screen.blit(label, (x + SLIDER_W + 20, y - 2))

def draw_flag_button(flag_state):
    global flag_pressed
    label = bold_font.render("Finger State:", True, COLOR_TEXT)
    screen.blit(label, (FLAG_BOX_RECT.x - 140, FLAG_BOX_RECT.y + 8))

    mouse_pos = pygame.mouse.get_pos()
    is_hovered = FLAG_BOX_RECT.collidepoint(mouse_pos)
    color = COLOR_BTN_G if flag_state == 'G' else COLOR_BTN_R
    if is_hovered:
        color = tuple(min(255, c + 30) for c in color)

    rect = FLAG_BOX_RECT.inflate(4, 4) if flag_pressed else FLAG_BOX_RECT
    pygame.draw.rect(screen, color, rect, border_radius=10)
    text = bold_font.render(flag_state, True, COLOR_BTN_LABEL)
    text_rect = text.get_rect(center=rect.center)
    screen.blit(text, text_rect)

def draw_stop_button():
    global stop_pressed
    mouse_pos = pygame.mouse.get_pos()
    is_hovered = STOP_BTN_RECT.collidepoint(mouse_pos)
    base_color = (200, 0, 0)
    hover_color = (230, 50, 50) if is_hovered else base_color

    rect = STOP_BTN_RECT.inflate(4, 4) if stop_pressed else STOP_BTN_RECT
    pygame.draw.rect(screen, hover_color, rect, border_radius=10)
    label = bold_font.render("RESTART", True, (255, 255, 255))
    text_rect = label.get_rect(center=rect.center)
    screen.blit(label, text_rect)

def draw_model_selector(open_panel: bool):
    global model_pressed
    mouse_pos = pygame.mouse.get_pos()
    is_hovered = MODEL_BTN_RECT.collidepoint(mouse_pos)
    bg_color = tuple(min(255, c + 20) for c in MODEL_BTN_BG) if is_hovered else MODEL_BTN_BG

    rect = MODEL_BTN_RECT

    pygame.draw.rect(screen, bg_color, rect, border_radius=10)
    pygame.draw.rect(screen, MODEL_BTN_BORDER, rect, width=1, border_radius=10)

    cx = rect.left + 12
    cy = rect.centery
    pygame.draw.polygon(screen, MODEL_BTN_TEXT, [
        (cx - 5, cy - 3),
        (cx + 5, cy - 3),
        (cx,     cy + 5)
    ])

    label = small_font.render(current_preset_name, True, MODEL_BTN_TEXT)
    screen.blit(label, (cx + 16, rect.y + 9))

    if not open_panel:
        return

    dropdown_h = len(PRESETS) * MODEL_ITEM_H
    dropdown_rect = pygame.Rect(MODEL_DROPDOWN_X, MODEL_DROPDOWN_Y, MODEL_DROPDOWN_W, dropdown_h)
    pygame.draw.rect(screen, COLOR_PANEL_BG, dropdown_rect, border_radius=8)

    y = MODEL_DROPDOWN_Y
    for name, vals in PRESETS.items():
        item_rect = pygame.Rect(MODEL_DROPDOWN_X, y, MODEL_DROPDOWN_W, MODEL_ITEM_H)
        is_item_hovered = item_rect.collidepoint(mouse_pos)
        item_color = COLOR_PANEL_ITEM_HOVER if is_item_hovered else COLOR_PANEL_ITEM

        pygame.draw.rect(screen, item_color, item_rect)
        label = small_font.render(name, True, COLOR_TEXT)
        screen.blit(label, (item_rect.x + 10, item_rect.y + 6))
        preset_item_rects[name] = (item_rect, vals)
        y += MODEL_ITEM_H

def draw_sensor_output(curPre):
    for i in range(4):
        val_text = bold_font.render(f"Actuator {i+1}: {curPre[i]} hPa", True, COLOR_TEXT)
        screen.blit(val_text, (ACTPOS[i][0] + 20, ACTPOS[i][1]))

def draw_lights(stopFlag):
    for i in range(4):
        y = SLIDER_TOP + i * SLIDER_SPACING
        cx = SLIDER_X - 30
        cy = y + SLIDER_H // 2
        color = (0, 255, 0) if stopFlag[i] == 'T' else (255, 0, 0)
        pygame.gfxdraw.filled_circle(screen, cx, cy, 8, color)
        pygame.gfxdraw.aacircle(screen, cx, cy, 8, color)

def draw_grasp_result(graspFlag):
    for i in range(4):
        y = SLIDER_TOP + i * SLIDER_SPACING
        g = graspFlag[i]
        if g == "1":
            col = COLOR_IND_T
        elif g == "-1":
            col = COLOR_IND_F
        else:
            col = COLOR_IND_X
        pygame.gfxdraw.filled_circle(screen, GRIP_CENTER[i][0], GRIP_CENTER[i][1], 8, col)
        pygame.gfxdraw.aacircle(screen, GRIP_CENTER[i][0], GRIP_CENTER[i][1], 8, col)






def handle_model_selector_click(mx, my):
    global panel_open
    if MODEL_BTN_RECT.collidepoint(mx, my):
        panel_open = not panel_open
        return True
    if panel_open:
        for name, (rect, vals) in preset_item_rects.items():
            if rect.collidepoint(mx, my):
                set_values_and_send(vals)
                panel_open = False
                return True
    return False

running = True
while running:
    outPre, outFlag, outGrasp, bendVals = sc.readOutput()
    if outPre and outFlag and outGrasp:
        curPre = outPre
        stopFlag = outFlag
        graspFlag = outGrasp

    if bendVals and logging_bend and bend_file:
        bend_file.write(" ".join(map(str, bendVals)) + "\n")

    screen.fill(COLOR_BG)
    bg_overlay = pygame.image.load("uipic.png").convert_alpha()
    bg_overlay = pygame.transform.scale(bg_overlay, (600, 600))
    screen.blit(bg_overlay, (150, 350))
    preset_item_rects.clear()

    draw_title_bar()

    for i in range(4):
        draw_slider(i, values[i])

    draw_sensor_output(curPre)
    draw_lights(stopFlag)
    draw_grasp_result(graspFlag)
    draw_flag_button(flag)
    draw_stop_button()
    draw_model_selector(panel_open)
    draw_bend_button()

    pygame.display.flip()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        elif event.type == pygame.MOUSEBUTTONDOWN:
            mx, my = event.pos
            stop_pressed = STOP_BTN_RECT.collidepoint(mx, my)
            flag_pressed = FLAG_BOX_RECT.collidepoint(mx, my)
            model_pressed = MODEL_BTN_RECT.collidepoint(mx, my)
            for i in range(4):
                if get_slider_index(mx, my) == i:
                    slider_pressed[i] = True

            if stop_pressed:
                sc.ser.write(b"S\n")
                print("Emergency STOP triggered")
                pygame.quit()
                time.sleep(2)
                os.execv(sys.executable, [sys.executable] + sys.argv)
            if handle_model_selector_click(mx, my):
                continue
            idx = get_slider_index(mx, my)
            if idx is not None:
                dragging_index = idx
                values[idx] = min(max((mx - SLIDER_X) / SLIDER_W, 0.0), 1.0)
                set_values_and_send(values)
            if flag_pressed:
                flag = 'G' if flag == 'R' else 'R'
                sc.sendFinState(flag)

            bend_pressed = BEND_BTN_RECT.collidepoint(mx, my)
            if bend_pressed:
                logging_bend = not logging_bend
                if logging_bend:
                    bend_file = open("bend_log.txt", "w")
                    print("Started logging bend sensor data")
                else:
                    if bend_file:
                        bend_file.close()
                        bend_file = None
                    print("Stopped logging bend sensor data")


        elif event.type == pygame.MOUSEBUTTONUP:
            bend_pressed = False

            dragging_index = None
            stop_pressed = False
            flag_pressed = False
            model_pressed = False
            slider_pressed = [False, False, False, False]

        elif event.type == pygame.MOUSEMOTION:
            if dragging_index is not None:
                mx, _ = event.pos
                values[dragging_index] = min(max((mx - SLIDER_X) / SLIDER_W, 0.0), 1.0)
                set_values_and_send(values)

sc.close()
pygame.quit()

if __name__ == "__main__":
    main()

