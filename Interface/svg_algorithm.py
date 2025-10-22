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

from svgdigitizer.svg import SVG
from svgdigitizer.svgplot import SVGPlot
from svgdigitizer.svgfigure import SVGFigure

# REFERENCE-ISH https://github.com/Bhomik04/image-to-svg/blob/main/python%20practice.py

# function to convert png/jpg to svg
def conversion_svg(file_path, output_path = "output.svg", potrace_path = "potrace"):
    # add the path to the image
    # add conversion to greyscale here
    image = Image.open(file_path).convert('L')
    width, height = image.size
    # 0 - 255
    img = image.point(lambda x: 0 if x < 128 else 255, '1')
    img_path = "temp.pbm"
    img.save(img_path)

    # call subprocess since potrace does not work 
    try:
        subprocess.run([potrace_path, img_path, "-s", "-o", output_path], check=True)
        print("SVG created successfully!")
    finally:
        if os.path.exists(img_path):    
            os.remove(img_path)

    pixels = np.array(img)
    lines = [(x, y) for y in range(height) for x in range(width) if pixels[y, x] == 0]
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

# extract the coordinates
def extract_coordinates(svg_path, samples = 50):
    paths, _ = svg2paths(svg_path)
    strokes = []

    for path in paths:
        for segment in path:
            for t in np.linspace(0, 1, samples):
                point = segment.point(t)
                strokes.append((point.real, point.imag))
    return strokes

# add main
if __name__ == "__main__":
    input_path = "drawinggator.jpeg"
    output_path = "output.svg"
    potrace_executable = "potrace"  

    conversion_svg(input_path, output_path, potrace_executable)
    coords = extract_coordinates(output_path, samples=100)

            