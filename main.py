import time

from src.modules.ai_draw import AIDraw

ai_draw = AIDraw(
    'images/img1.png',
    padding=(140, 125),
    canvas_width=800,
    canvas_height=800,
    number_of_colors=20,
    blur=2
)

ai_draw.generate_coloring_commands()

# ai_draw.commands.add_command({
#     'name': 'pen_color',
#     'color': '#000'
# })

# ai_draw.generate_outline_commands()
print('Waiting 5 seconds')
time.sleep(5)

ai_draw.commands.run()

# from src.modules.gui import Gui
#
# gui = Gui()
#
# gui.run()
