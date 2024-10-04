import sys
sys.path.insert(0, '../auto_nav/')

from kinematic_model import robot_model

import pickle
import socket
import matplotlib.pyplot as plt
import numpy as np

myrobot = robot_model(0.4, 1)

def plot_robot(state, x_traj, y_traj):
    x, y, theta = state

    # Create a new figure
    plt.clf()
    
    # Define the rectangle parameters
    rect_width = 4
    rect_height = 2
    rectangle = plt.Rectangle(
        (x - rect_width / 2, y - rect_height / 2), 
        rect_width, 
        rect_height, 
        angle=np.degrees(theta), 
        edgecolor='r', 
        facecolor='r',
        rotation_point='center'
    )
    
    r = rect_width/2
    arrow = plt.Arrow(x, y, 0.5 * np.cos(theta), 0.5 * np.sin(theta), edgecolor='b', facecolor='b')

    #print(np.radians(rectangle.get_angle()), rectangle.get_center())

    line = plt.Line2D(x_traj, y_traj, color='g')

    # Add rectangle to plot
    plt.gca().add_patch(rectangle)
    plt.gca().add_patch(arrow)
    plt.gca().add_line(line)
    
    # Set plot limits
    plt.xlim(-10, 10)
    plt.ylim(-10, 10)
    
    plt.gca().set_aspect('equal', adjustable='box')
    
    plt.pause(0.01)

def start_server():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind(('localhost', 12346))
    server_socket.listen(1)
    print("Waiting for connection...")

    conn, addr = server_socket.accept()
    print(f'Connected by {addr}')
    
    state = (0, 0, 0)
    dt = 0.01
    input = (0, 0)
    x_traj, y_traj = [], []

    plt.ion()
    
    try:
        while True:
            
            data = conn.recv(1024)

            if not data:
                break
            
            input = pickle.loads(data)
            
            state = myrobot.kinematic_model(state, input, dt)
            x_traj.append(state[0])
            y_traj.append(state[1])
            #print("State: ", state)
            plot_robot(state, x_traj, y_traj)
            
    except KeyboardInterrupt:
        print("Server stopped.")
    
    finally:
        conn.close()

if __name__ == '__main__':
    start_server()
