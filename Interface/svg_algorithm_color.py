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

# adding open cv to be used for edge detection
import cv2

# parse SVG paths
from svgpathtools import svg2paths
from lxml import etree
import re
from xml.dom import minidom
# REFERENCE-ISH https://github.com/Bhomik04/image-to-svg/blob/main/python%20practice.py

# remove the inner path from svg which is structured as 
# M ... z m ... z
def split_svg_paths(svg_path):
    tree = etree.parse(svg_path)
    root = tree.getroot()
    namespace = {'svg': 'http://www.w3.org/2000/svg'}
    paths = root.findall('.//svg:path', namespaces=namespace)
    
    if len(paths) > 1:
        parent = paths[0].getparent()
        parent.remove(paths[0])
    
    for elements in root.findall('.//svg:path', namespaces=namespace):
        d = elements.get('d')
        if not d:
            continue
        # split at 'M' or 'm' to get subpaths
        subpaths = re.split(r'(?=[Mm])', d)
        subpaths = [s.strip() for s in subpaths if s.strip()]

        if len(subpaths) > 1:
            elements.set('d', subpaths[0])
    
    tree.write(svg_path, pretty_print=True)

# https://stackoverflow.com/questions/3380726/converting-an-rgb-color-tuple-to-a-hexidecimal-string
def rgb2hex(r,g,b):
    return "#{:02x}{:02x}{:02x}".format(r,g,b)

# working on getting colors to the svg
# using same function but making changes
def conversion_svg_color(file_path, output_path = "output.svg", potrace_path = "potrace"):
    # add the path to the image
    # add conversion to greyscale here
    #image = Image.open(file_path)
    image = cv2.imread(file_path)
    # ADD CHECK FOR BACKGROUND BEING TRANSPARENT
################################################################################    
    # WILL BE DONE LATER NOT NEEDED FOR NOW
    # if image.mode in ('RGBA', 'LA'):
    #     # make it white for better processing
    #     background = Image.new('RGB', image.size, (255, 255, 255))
    #     if image.mode == 'RGBA':
    #         background.paste(image, mask = image.split()[3])
    #     else:
    #         background.paste(image, mask=image.split()[1])
    #     image = background
################################################################################
    # need color mapping here
    # using LAB gets more colors but not accurte
    image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

    #image = image.convert('L')
    #width, height = image.size
    # returns the opposite
    height, width, _ = image.shape

    # keep the same
    # convert from pixel to cm/inch to display
    # using 96 DPI as that is a default
    #dpi = image.info.get('dpi', (96, 96))[0]
    # hard code the number for dpi
    dpi = 96
    # inches
    width_inch = width / dpi
    height_inch = height / dpi
    # cm
    width_cm = width_inch * 2.54
    height_cm = height_inch * 2.54

    ## REFERENCE: https://blog.finxter.com/5-best-ways-to-perform-color-quantization-in-an-image-using-k-means-in-opencv-python/
    ## https://stackoverflow.com/questions/73666119/open-cv-python-quantize-to-a-given-color-palette 
    
    # blurring image?
    blurred = cv2.GaussianBlur(image, (3, 3), 0)

    # using color quantanization
    color_img = blurred.reshape(-1, 3).astype(np.float32)
    # define criteria
    criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 100, 0.01)
    # increase for better results
    k = 6
    _, labels, centers = cv2.kmeans(color_img, k, None, criteria, 10, cv2.KMEANS_PP_CENTERS)

    # back to 8 bits
    centers = np.uint8(centers)
    quantized_img = centers[labels.flatten()].reshape(blurred.shape)

    # need to somehow save the file to edit it
    # https://coderivers.org/blog/python-svg/
    dwg = svgwrite.Drawing(output_path, profile='tiny', size=(width, height))

    # covert to grayscale
    # img_gray = cv2.cvtColor(quantized_img, cv2.COLOR_RGB2GRAY)
    # pixels = np.array(img_gray)
    # lines = [(x, y) for y in range(height) for x in range(width) if pixels[y, x] == 255]
    
    for i, color in enumerate(centers):
        # skip near white colors
        if np.all(color > 250):
            continue
        # https://blog.finxter.com/5-best-ways-to-color-identification-in-images-using-python-and-opencv/
        img = cv2.inRange(
            quantized_img,
            color,
            color
        )

        img = cv2.bitwise_not(img)

        # output that potrace expects
        # https://potrace.sourceforge.net/ 
        img_path = f"temp_{i}.pbm"
        img_svg = f"temp_{i}.svg"
        #img.save(img_path)

        # save using open cv
        cv2.imwrite(img_path, img)
        
        # call subprocess since potrace does not work for my computer 
        # REFERENCE: https://potrace.sourceforge.net/potrace.1.html
        try:
            subprocess.run([
                potrace_path, 
                img_path, 
                "-s", 
                "-a", "0", # alphamax for cornerns (helps with the square image)
                "-t", "70", # turdside mostly for noise
                "-k", "0.3",
                "-o", 
                img_svg], check=True)
            paths, _ = svg2paths(img_svg)
            hex_color = rgb2hex(color[0], color[1], color[2])
            for path in paths:
                dwg.add(dwg.path(d=path.d(), fill=hex_color, stroke='none'))
                #dwg.add(dwg.path(d=path.d(), stroke='none'))
            #split_svg_paths(img_svg)
            #print("SVG created successfully!")
        finally:
            if os.path.exists(img_path):    
                os.remove(img_path)
            if os.path.exists(img_svg):
                os.remove(img_svg)

    # list of plack pixels and coordinates we need 
    
    
    #### LET'S TRY AND ADD PAPER SIZE ####

    # return the lines and output_path in which is saved
    # also width and height for scaling purposes
    dwg.save()
    split_svg_paths(output_path)
    return width, height, width_inch, height_inch, width_cm, height_cm, output_path

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


# function to convert png/jpg to svg
# def conversion_svg_color(file_path, output_path = "output.svg", potrace_path = "potrace"):
#     # add the path to the image
#     # add conversion to greyscale here
#     #image = Image.open(file_path)
#     image = cv2.imread(file_path)
#     # ADD CHECK FOR BACKGROUND BEING TRANSPARENT
# ################################################################################    
#     # WILL BE DONE LATER NOT NEEDED FOR NOW
#     # if image.mode in ('RGBA', 'LA'):
#     #     # make it white for better processing
#     #     background = Image.new('RGB', image.size, (255, 255, 255))
#     #     if image.mode == 'RGBA':
#     #         background.paste(image, mask = image.split()[3])
#     #     else:
#     #         background.paste(image, mask=image.split()[1])
#     #     image = background
# ################################################################################
#     # convert to grayscale using open cv
#     image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

#     #image = image.convert('L')
#     #width, height = image.size
#     # returns the opposite
#     height, width = image.shape

#     # convert from pixel to cm/inch to display
#     # using 96 DPI as that is a default
#     #dpi = image.info.get('dpi', (96, 96))[0]
#     # hard code the number for dpi
#     dpi = 96
#     # inches
#     width_inch = width / dpi
#     height_inch = height / dpi
#     # cm
#     width_cm = width_inch * 2.54
#     height_cm = height_inch * 2.54

#     # 0 - 255
#     #img = image.point(lambda x: 0 if x < 128 else 255, '1')
    
#     # using open cv to threshold the image for better results
#     # https://docs.opencv.org/4.x/d7/d4d/tutorial_py_thresholding.html 
#     # Smooth noise but preserve edges

#     ## This section extracts 73 strokes (includes a canvas border) ==> FOR GATOR IMAGE
#     ## Includes a border with every image processed
#     img = cv2.adaptiveThreshold(
#         image,
#         255,
#         cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
#         \
#         cv2.THRESH_BINARY,
#         11,
#         2
#     )
#     img = cv2.bitwise_not(img)

#     ## This section extracts 322 strokes ==> FOR GATOR IMAGE
#     # img = cv2.adaptiveThreshold(
#     #     image,
#     #     255,
#     #     cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
#     #     \
#     #     cv2.THRESH_BINARY,
#     #     11,
#     #     2
#     # )
#     # kernel = np.ones((2,2), np.uint8)
#     # img = cv2.dilate(img, kernel, iterations=1)
#     # img = cv2.morphologyEx(img, cv2.MORPH_CLOSE, kernel, iterations=1)


#     # output that potrace expects
#     # https://potrace.sourceforge.net/ 
#     img_path = "temp.pbm"
#     #img.save(img_path)

#     # save using open cv
#     cv2.imwrite(img_path, img)
    
#     # call subprocess since potrace does not work for my computer 
#     try:
#         subprocess.run([potrace_path, img_path, "-s", "-o", output_path], check=True)
#         split_svg_paths(output_path)
#         print("SVG created successfully!")
#     finally:
#         if os.path.exists(img_path):    
#             os.remove(img_path)

#     # list of plack pixels and coordinates we need 
#     pixels = np.array(img)
#     lines = [(x, y) for y in range(height) for x in range(width) if pixels[y, x] == 0]
    
#     #### LET'S TRY AND ADD PAPER SIZE ####

#     # return the lines and output_path in which is saved
#     # also width and height for scaling purposes
#     return lines, width, height, width_inch, height_inch, width_cm, height_cm, output_path

#     # get the size of the image
#     # width, height = image.size

#     # # working with black and white images only
#     # array_of_pixels = np.array(image)
    
#     # vals = array_of_pixels < 128 

#     # # convert to svg using the svgwrite
#     # outcome = svgwrite.Drawing(output_path, profile='tiny', size=(width, height))

#     # lines = []
#     # for y in range(height):
#     #     for x in range(width):
#     #         if vals[y, x]:
#     #             lines.append((x, y))
#     #             outcome.add(outcome.rect(insert=(x, y), size=(1, 1), fill='black'))

#     # outcome.save()
#     # print("SVG created successfully!")
#     # return lines, width, 


def convert_to_a4(svg_in, svg_out, original_width, original_height): 
    tree = etree.parse(svg_in) 
    root = tree.getroot() 
    
    # Define A4 page size in millimeters 
    a4_width, a4_height = 210, 297 
    
    # Update SVG root attributes 
    root.attrib['width'] = f'{a4_width}mm' 
    root.attrib['height'] = f'{a4_height}mm' 
    root.attrib['viewBox'] = f'0 0 {a4_width} {a4_height}' 
    root.attrib['preserveAspectRatio'] = 'xMidYMid meet' 
    
    scale_x = a4_width / original_width
    scale_y = a4_height / original_height
    
    scale = min(scale_x, scale_y)
    
    offset_x = (a4_width - original_width * scale) / 2
    offset_y = (a4_height - original_height * scale) / 2
    
    for g in root.findall(".//{http://www.w3.org/2000/svg}g"): 
        g.attrib['transform'] = f"translate({offset_x},{offset_y + original_height * scale}) scale({scale},{-scale})" 
        
    tree.write(svg_out, pretty_print=True) 

##############################################################################################
                    ### NOT NEEDED BUT USED FOR TESTING PURPOSES ###
# extract the coordinates
# looking at the svg there are 2 paths created inner and outer
# consider removing the inner lines 

## made changes to extract colors to test
def extract_coordinates_color(svg_path, samples=50):
    # adding a new function for area of path
    def path_area(line):
        # using shoelace formula
        # https://www.101computing.net/the-shoelace-algorithm/
        area = 0.0
        for i in range(len(line)):
            x1, y1 = line[i]
            # wrap around the points
            x2, y2 = line[(i + 1) % len(line)]
            area += x1 * y2 - x2 * y1
        return abs(area) / 2.0
    # FIXED STOKES 
    # using the svg library to extract paths 
    paths, attributes = svg2paths(svg_path)
    #paths, _ = svg2paths(svg_path)
    all_strokes = []
    # start by processing each path 
    for path, attr in zip(paths, attributes):
        color = attr.get('fill', '#000000') 
        # split into continuous subpaths
        subpath = path.continuous_subpaths()
        stroke = [] # area and points
        for segment in subpath:
            point = []
            for seg in segment:
                for t in np.linspace(0, 1, samples):
                    p = seg.point(t)
                    point.append((p.real, p.imag))
            # less than 3 points cannot form a closed shape so skip
            if len(point) < 3:
                continue
            area = abs(path_area(point))
            stroke.append((area, point))
        if not stroke:
            continue
        outer = max(stroke, key=lambda x: x[0])
        all_strokes.append({'points': outer[1], 'color': color})
    return all_strokes, len(all_strokes)

    # for path in paths:
    #     stroke = []
    #     prev_end = None
    #     for segment in path:
    #         start = segment.point(0)
    #         end = segment.point(1)
    #         if prev_end is not None and abs(start - prev_end) > 1e-6:
    #             if stroke:
    #                 all_strokes.append(stroke)
    #             stroke = []
    #         for t in np.linspace(0, 1, samples):
    #             point = segment.point(t)
    #             stroke.append((point.real, point.imag))
    #         prev_end = end
    #     if stroke:
    #         all_strokes.append(stroke)

    # num_strokes = len(all_strokes)
    # return all_strokes, num_strokes

# Adding a simulation to see how the drawing would look like
def animation_simulation(strokes):
    # a4 size in inches to visualize the simulation
    a4_width_in = 8.27   
    a4_height_in = 11.69 

    fig, ax = plt.subplots(figsize=(a4_width_in, a4_height_in))
    ax.set_aspect('equal')

    ax.invert_yaxis()

    all_points = [p for stroke in strokes for p in stroke]
    # unpack the x, y list from the extract_coordinates_color function
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
# making changes to view colors 
def display_svg(strokes):
    a4_width_in = 8.27   
    a4_height_in = 11.69 

    fig, ax = plt.subplots(figsize=(a4_width_in, a4_height_in))
    ax.set_aspect('equal')
    ax.invert_yaxis()
    
    # Extract all points to set limits
    all_pts = [p for s in strokes for p in s['points']]
    xs, ys = zip(*all_pts)
    
    ax.set_xlim(min(xs), max(xs))
    ax.set_ylim(min(ys), max(ys))
    ax.axis('off')
    
    for stroke in strokes:
        pts = stroke['points']
        color = stroke['color']
        if pts:
            xs_s = [p[0] for p in pts]
            ys_s = [p[1] for p in pts]
            # Use the color found in the SVG
            ax.plot(xs_s, ys_s, color=color, linewidth=2)

    plt.show()
##############################################################################################

# add main
if __name__ == "__main__":
    #input_path = "images/shapes.png"
    #input_path = "images/drawinggator.jpeg"
    #input_path = "images/simple.png"
    #input_path = "images/logo.jpg"
    #input_path = "images/testing.png"
    #input_path = "images/prototype_design.jpg"
    #input_path = "images/gator.jpg"
    input_path = "images/menu.jpg"
    output_path = "output.svg"
    potrace_executable = "potrace"

    width, height, width_inch, height_inch, width_cm, height_cm, output_path = conversion_svg_color(input_path, output_path, potrace_executable)
    convert_to_a4(output_path, output_path, width, height)
    # animation lines
    strokes, num_strokes = extract_coordinates_color(output_path, samples=30)
    #animation_simulation(strokes)
    display_svg(strokes)