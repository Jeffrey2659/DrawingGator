# Pillow as a tool to import and that handles image processing
from PIL import Image 
import numpy as np
# let's consider using potrace for clearer images
# idk why i can't install this
# import potrace
# use a subprocess that calls potrace (LATER USE)
import subprocess 
import os
import svgwrite
import matplotlib.pyplot as plt
import matplotlib.animation as animation
# parse SVG paths
from svgpathtools import svg2paths

# REFERENCE-ISH https://github.com/Bhomik04/image-to-svg/blob/main/python%20practice.py

# function to convert png/jpg to svg
def conversion_svg(file_path, output_path = "output.svg", potrace_path = "potrace"):
    # add the path to the image
    # add conversion to greyscale here
    image = Image.open(file_path).convert('L')
    width, height = image.size
    # 0 - 255
    img = image.point(lambda x: 0 if x < 128 else 255, '1')
    # output that potrace expects
    # https://potrace.sourceforge.net/ 
    img_path = "temp.pbm"
    img.save(img_path)

    # call subprocess since potrace does not work for my computer 
    try:
        subprocess.run([potrace_path, img_path, "-s", "-o", output_path], check=True)
        print("SVG created successfully!")
    finally:
        if os.path.exists(img_path):    
            os.remove(img_path)

    # list of plack pixels and coordinates we need 
    pixels = np.array(img)
    lines = [(x, y) for y in range(height) for x in range(width) if pixels[y, x] == 0]
    # return the lines and output_path in which is saved
    # also width and height for scaling purposes
    return lines, width, height, output_path

    # get the size of the image
    # width, height = image.size

    # # working with black and white images only
    # array_of_pixels = np.array(image)
    
    # vals = array_of_pixels < 128 

    # # convert to svg using the svgwrite
    # outcome = svgwrite.Drawing(output_path, profile='tiny', size=(width, height))

    # lines = []
    # for y in range(height):
    #     for x in range(width):
    #         if vals[y, x]:
    #             lines.append((x, y))
    #             outcome.add(outcome.rect(insert=(x, y), size=(1, 1), fill='black'))

    # outcome.save()
    # print("SVG created successfully!")
    # return lines, width, 


##############################################################################################
                    ### NOT NEEDED BUT USED FOR TESTING PURPOSES ###
# extract the coordinates
def extract_coordinates(svg_path, samples=50):
    # using the svg library to extract paths 
    paths, _ = svg2paths(svg_path)
    all_strokes = []

    for path in paths:
        stroke = []
        for segment in path:
            for t in np.linspace(0, 1, samples):
                point = segment.point(t)
                stroke.append((point.real, point.imag))
        all_strokes.append(stroke)
    return all_strokes


# Adding a simulation to see how the drawing would look like
def animation_simulation(strokes):
    # a4 size in inches to visualize the simulation
    a4_width_in = 8.27   
    a4_height_in = 11.69 

    fig, ax = plt.subplots(figsize=(a4_width_in, a4_height_in))
    ax.set_aspect('equal')

    ax.invert_yaxis()

    all_points = [p for stroke in strokes for p in stroke]
    # unpack the x, y list from the extract_coordinates function
    xs, ys = zip(*all_points)

    # add a little margin around the drawing
    pad_x = (max(xs) - min(xs)) * 0.05
    pad_y = (max(ys) - min(ys)) * 0.05

    # set the axis limits
    ax.set_xlim(min(xs) - pad_x, max(xs) + pad_x)
    ax.set_ylim(min(ys) - pad_y, max(ys) + pad_y)
    
    # turn the axis off for better visualization
    ax.axis('off')

    # get the lines and with update call the lines
    lines = [ax.plot([], [], lw=2, color='black')[0] for _ in strokes]

    def init():
        for ln in lines:
            ln.set_data([], [])
        return lines
    
    def update(frame):
        stroke_idx, point_idx = frame
        stroke = strokes[stroke_idx]
        xdata = [p[0] for p in stroke[:point_idx]]
        ydata = [p[1] for p in stroke[:point_idx]]
        lines[stroke_idx].set_data(xdata, ydata)
        return lines

    # Animation frames
    frames = []
    for i, stroke in enumerate(strokes):
        for j in range(1, len(stroke) + 1):
            frames.append((i, j))

    ani = animation.FuncAnimation(
        fig, update, frames=frames,
        init_func=init, blit=True, interval=0.5, repeat=False
    )

    plt.show() 

# display the svg drawing, because animation is not working when called in the UI  
def display_svg(strokes):
    # a4 size in inches
    a4_width_in = 8.27   
    a4_height_in = 11.69 

    fig, ax = plt.subplots(figsize=(a4_width_in, a4_height_in))
    ax.set_aspect('equal')
    ax.invert_yaxis()
    
    all_points = [p for stroke in strokes for p in stroke]
    xs, ys = zip(*all_points)

    x_range = max(xs) - min(xs) if max(xs) != min(xs) else 1
    y_range = max(ys) - min(ys) if max(ys) != min(ys) else 1
    pad_x = x_range * 0.05
    pad_y = y_range * 0.05
    
    ax.set_xlim(min(xs) - pad_x, max(xs) + pad_x)
    ax.set_ylim(min(ys) - pad_y, max(ys) + pad_y)
    ax.axis('off')
    
    # Draw all strokes
    for stroke in strokes:
        if stroke:
            xs_stroke = [p[0] for p in stroke]
            ys_stroke = [p[1] for p in stroke]
            ax.plot(xs_stroke, ys_stroke, 'k-', linewidth=2)

    plt.show()
##############################################################################################

# add main
if __name__ == "__main__":
    #input_path = "images/shapes.png"
    #input_path = "drawinggator.jpeg"
    #input_path = "images/simple.png"
    #input_path = "images/roses.jpg"
    input_path = "images/testing.png"
    output_path = "output.svg"
    potrace_executable = "potrace"

    conversion_svg(input_path, output_path, potrace_executable)
    # animation lines
    strokes = extract_coordinates(output_path, samples=30)
    animation_simulation(strokes)
