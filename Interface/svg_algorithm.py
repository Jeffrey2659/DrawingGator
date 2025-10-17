# Pillow as a tool to import and that handles image processing
from PIL import Image 
import numpy as np
# let's consider using potrace for clearer images
# idk why i can't install this
# import potrace
# use a subprocess that calls potrace (LATER USE)
import subprocess 
import svgwrite
import matplotlib.pyplot as plt
import matplotlib.animation as animation

from svgdigitizer.svg import SVG
from svgdigitizer.svgplot import SVGPlot
from svgdigitizer.svgfigure import SVGFigure

# REFERENCE-ISH https://github.com/Bhomik04/image-to-svg/blob/main/python%20practice.py

# function to convert png/jpg to svg
def conversion_svg(file_path, output_path = "output.svg"):
    # add the path to the image
    # add conversion to greyscale here
    image = Image.open(file_path).convert('L')
    # get the size of the image
    width, height = image.size

    # working with black and white images only
    array_of_pixels = np.array(image)
    
    vals = array_of_pixels < 128 

    # convert to svg using the svgwrite
    outcome = svgwrite.Drawing(output_path, profile='tiny', size=(width, height))

    lines = []
    for y in range(height):
        for x in range(width):
            if vals[y, x]:
                lines.append((x, y))
                outcome.add(outcome.rect(insert=(x, y), size=(1, 1), fill='black'))

    outcome.save()
    print("SVG created successfully!")
    return lines, width, height

# Adding a simulation to see how the drawing would look like
def animation_simulation(lines, width, height):
    fig, ax = plt.subplots()
    ax.set_xlim(0, width)
    ax.set_ylim(height, 0)

    xdata, ydata = [], []
    scat = ax.scatter([], [], s=1, color='black')

    # init frame
    def init():
        scat.set_offsets(np.empty((0, 2)))
        return scat,

    # update frame
    def update(frame):
        xdata.append(lines[frame][0])
        ydata.append(lines[frame][1])
        scat.set_offsets(np.c_[xdata, ydata])
        return scat,

    # make the animation
    ani = animation.FuncAnimation(fig, update, frames=len(lines), init_func=init, blit=True, interval=3, repeat=False)
    plt.show()

# add main
if __name__ == "__main__":
    lines, width, height = conversion_svg("drawinggator.jpeg", "output.svg")
    animation_simulation(lines, width, height)
            