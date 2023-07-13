import os
import pyglet
from pyglet import shapes
import sys
from model import Model

gestures = ['arrow', 'caret', 'check']

# pyglet application
window = pyglet.window.Window(fullscreen=True)

# later: drawn points are saved here
line = []

# init of lstm
recognizer = Model()

result_text = pyglet.text.Label("Gesture:   ", x=window.width-150, y=window.height-20, anchor_x='center', anchor_y='center', font_size=20)


# can quit window with q / esc(?)
@window.event
def on_key_press(symbol, modifiers):
    if symbol == pyglet.window.key.Q:
        sys.exit(0)
    elif symbol == pyglet.window.key.Q:
        line.clear()

@window.event
def on_draw():
    window.clear()
    for point in line:
        pointShape = shapes.Circle(point[0], point[1], radius=5, color=(255, 225, 255))
        pointShape.draw()


# if mouse is released predict gesture and start an application
@window.event
def on_mouse_release(x, y, button, modifiers):
    window.clear()
    if pyglet.window.mouse.LEFT:
        prediction = recognizer.predict_gesture(line)
        # if gesture is recognized as one of the 3 defined, start the corresponding application
        for gesture in gestures:
            if prediction == gesture:
                print("RESULT", prediction)
                line.clear()
                result_text.text = "Gesture:   " + prediction[0]
                result_text.draw()
                result_text.text = "Gesture:   "

        line.clear()


# if gesture is drawn by mouse draw the current point
@window.event
def on_mouse_drag(x, y, dx, dy, buttons, modifiers):
    if buttons & pyglet.window.mouse.LEFT:
        line.append([int(x), int(y)])



pyglet.app.run()




