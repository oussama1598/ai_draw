import time

import clipboard
import pyautogui

pyautogui.FAILSAFE = False
pyautogui.PAUSE = 0


class CommandsExecuter:
    def __init__(self, logger=print):
        self.logger = logger
        self.commands = []

        self.mouse_pressed = False

    def add_command(self, command: dict):
        self.commands.append(command)

    def pop_last_command(self):
        self.commands.pop()

    def get_last_command(self):
        return self.commands[-1]

    def _mouse(self, command):
        self.mouse_pressed = command.get('pressed')

    def _move(self, command):
        x = command.get('x')
        y = command.get('y')

        if self.mouse_pressed:
            pyautogui.dragTo(x, y, 0)

        pyautogui.moveTo(x, y, 0)

    def _pen_color(self, command):
        color = command.get('color')

        print(f'Changing color to {color}')
        clipboard.copy(color)

        mouse_positions = [
            (164, 1008),
            (310, 663),
            (596, 390),
            (687, 349)
        ]

        time.sleep(1)
        pyautogui.moveTo(*mouse_positions[0])
        time.sleep(1)
        pyautogui.click(clicks=2)
        time.sleep(1)
        pyautogui.moveTo(*mouse_positions[1])
        time.sleep(1)
        pyautogui.click(clicks=1)
        time.sleep(1)
        pyautogui.moveTo(*mouse_positions[2])
        time.sleep(1)
        pyautogui.click(clicks=3)
        time.sleep(1)
        pyautogui.press('backspace')
        time.sleep(1)
        pyautogui.hotkey('ctrl', 'v')
        time.sleep(1)
        pyautogui.moveTo(*mouse_positions[3])
        time.sleep(1)
        pyautogui.click()
        time.sleep(1)

    def run(self):
        for i, command in enumerate(self.commands):
            self.logger(f'Drawing Progress: {round((i + 1) / len(self.commands), 2) * 100}%')

            command_name = command.get('name')

            if command_name == 'move':
                self._move(command)

            if command_name == 'mouse':
                self._mouse(command)

            if command_name == 'pen_color':
                self._pen_color(command)
