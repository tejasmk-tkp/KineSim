from kivy.app import App
from kivy.uix.gridlayout import GridLayout
from kivy.uix.widget import Widget
from kivy.graphics import Ellipse, Color, Line, Rectangle, Triangle
from kivy.core.window import Window
from kivy.clock import Clock

from math import atan2, cos, sin, sqrt, radians

import socket
import time
import pickle

class Joystick(Widget):
    def __init__(self, client_socket, **kwargs):
        super(Joystick, self).__init__(**kwargs)
        self.client_socket = client_socket  # Store the socket connection
        self.center_x = Window.width / 2
        self.center_y = Window.height / 2
        self.radius = 100  # Joystick boundary

        with self.canvas:
            Color(1, 0, 0, 0.5)  # Red joystick base
            self.base = Ellipse(pos=(self.center_x - self.radius, self.center_y - self.radius),
                                size=(2*self.radius, 2*self.radius))

            Color(0, 0, 1, 1)  # Blue joystick knob
            self.knob = Ellipse(pos=(self.center_x - 30, self.center_y - 30), size=(60, 60))

        self.bind(size=self.update_canvas)

    def update_canvas(self, *args):
        self.base.pos = (self.center_x - self.radius, self.center_y - self.radius)
        self.base.size = (2*self.radius, 2*self.radius)
        self.knob.pos = (self.center_x - 30, self.center_y - 30)

    def on_touch_move(self, touch):
        # Calculate the distance from the center of the joystick base
        dx = touch.x - self.center_x
        dy = touch.y - self.center_y

        # Limit the knob movement to within the base circle
        distance = (dx**2 + dy**2)**0.5
        if distance < self.radius:
            self.knob.pos = (touch.x - 30, touch.y - 30)
        else:
            angle = atan2(dy, dx)
            limited_x = self.center_x + self.radius * cos(angle)
            limited_y = self.center_y + self.radius * sin(angle)
            self.knob.pos = (limited_x - 30, limited_y - 30)

        # Send joystick position (normalized between -1 and 1)
        x_normalized = dx / self.radius
        y_normalized = dy / self.radius
        #print(f'X: {x_normalized}, Y: {y_normalized}')
        # ser.write(f'{x_normalized},{y_normalized}\n'.encode())  # Uncomment for serial output

        # Map normalised joystick output to wheel velocities
        v_max = 10
        v_linear = y_normalized * v_max
        v_angular = x_normalized * v_max
        
        # Individual wheel velocities
        v1 = v_linear + v_angular
        v2 = v_linear - v_angular

        # Send velocities through the existing socket connection
        data = (v1, v2)  # \n to mark the end of a message
        
        try:
            self.client_socket.sendall(pickle.dumps(data))
            #print(f'Sent velocities: {data[0]}, {data[1]}')
        except Exception as e:
            print(f'Error sending data: {e}')

    def on_touch_up(self, touch):
        # Reset joystick to center on touch release
        self.knob.pos = (self.center_x - 30, self.center_y - 30)
        #print('Joystick centered!')
        
        data = (0, 0)

        try:
            self.client_socket.sendall(pickle.dumps(data))
            #print(f'Sent velocities: 0, 0')
        except Exception as e:
            print(f'Error sending data: {e}')

class Interface(App):
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.client_socket = None
    
    def build(self):
        layout = GridLayout(cols=2)
        return layout

    def on_start(self):
        # Connect to server when the app starts
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        
        try:
            self.client_socket.connect(('localhost', 12346))  # Connect to the server
            print("Connected to server")
            
        # Add the joystick widget AFTER the connection is established
            joystick = Joystick(self.client_socket)  # Pass the socket connection to the joystick widget
            self.root.add_widget(joystick)
        
        except ConnectionRefusedError:
            print("Failed to connect to server. Is the server running?")
        
        except Exception as e:
            print(f"Error: {e}")

    def on_stop(self):
        # Close the socket connection when the app stops
        if self.client_socket:
            self.client_socket.close()
            print("Connection closed.")

if __name__ == '__main__':

    Interface().run()
