# Pillow as a tool to import and that handles image processing
from PIL import Image 
import numpy as np
from pathlib import Path
# let's consider using potrace for clearer images
# idk why i can't install this
# import potrace
# use a subprocess that calls potrace (LATER USE)
import subprocess 
import os, shutil, subprocess
import svgwrite
import matplotlib.pyplot as plt
import matplotlib.animation as animation

# adding open cv to be used for edge detection
import cv2

# parse SVG paths
from svgpathtools import svg2paths
from lxml import etree
# REFERENCE-ISH https://github.com/Bhomik04/image-to-svg/blob/main/python%20practice.py


def find_potrace(explicit: str | None = None) -> str:
    if explicit:
        exe = Path(explicit)
        if os.name == "nt" and exe.suffix.lower() != ".exe" and not exe.exists():
            exe = exe.with_suffix(".exe")
        if not exe.exists():
            raise FileNotFoundError(f"potrace not found at: {exe}")
        return str(exe)
    # Try PATH
    exe = shutil.which("potrace") or shutil.which("potrace.exe")
    if not exe:
        raise FileNotFoundError(
            "potrace not found on PATH. Either add it to PATH or pass its full path."
        )
    return exe




# REFERENCE-ISH https://github.com/Bhomik04/image-to-svg/blob/main/python%20practice.py

# function to convert png/jpg to svg
def conversion_svg(file_path, output_path = "output.svg", potrace_path = "potrace"):
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
    # convert to grayscale using open cv
    image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    #image = image.convert('L')
    #width, height = image.size
    # returns the opposite
    height, width = image.shape

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

    # 0 - 255
    #img = image.point(lambda x: 0 if x < 128 else 255, '1')
    
    # using open cv to threshold the image for better results
    # https://docs.opencv.org/4.x/d7/d4d/tutorial_py_thresholding.html 
    _, img = cv2.threshold(image, 128, 255, cv2.THRESH_BINARY)
    # output that potrace expects
    # https://potrace.sourceforge.net/ 
    img_path = "temp.pbm"
    #img.save(img_path)

    # save using open cv
    cv2.imwrite(img_path, img)
    
    # call subprocess since potrace does not work for my computer 
    try:
        cmd = [potrace_path, img_path, "-s", "-o", str(output_path)]
        # Helpful diagnostics:
        print("Running:", cmd)
        print("PATH seen by Python:", os.environ.get("PATH", ""))
        res = subprocess.run(cmd, capture_output=True, text=True)
        if res.returncode != 0:
            raise RuntimeError(
                f"potrace failed (exit {res.returncode}).\nSTDOUT:\n{res.stdout}\nSTDERR:\n{res.stderr}"
            )
        print("SVG created successfully!")
    finally:
        if os.path.exists(img_path):
            try:
                os.remove(img_path)
            except OSError:
                pass
 

    # list of plack pixels and coordinates we need 
    pixels = np.array(img)
    lines = [(x, y) for y in range(height) for x in range(width) if pixels[y, x] == 0]
    
    #### LET'S TRY AND ADD PAPER SIZE ####

    # return the lines and output_path in which is saved
    # also width and height for scaling purposes
    return lines, width, height, width_inch, height_inch, width_cm, height_cm, output_path

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
def extract_coordinates(svg_path, samples=50):
    # FIXED STOKES 
    # using the svg library to extract paths 
    paths, attributes = svg2paths(svg_path)
    all_strokes = []

    for path in paths:
        stroke = []
        prev_end = None
        for segment in path:
            start = segment.point(0)
            end = segment.point(1)
            if prev_end is not None and abs(start - prev_end) > 1e-6:
                if stroke:
                    all_strokes.append(stroke)
                stroke = []
            for t in np.linspace(0, 1, samples):
                point = segment.point(t)
                stroke.append((point.real, point.imag))
            prev_end = end
        if stroke:
            all_strokes.append(stroke)

    num_strokes = len(all_strokes)
    return all_strokes, num_strokes

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
    #input_path = "images/drawinggator.jpeg"
    #input_path = "images/simple.png"
    #input_path = "images/roses.jpg"
    #input_path = "images/testing.png"
    input_path = "images/prototype_design.jpg"
    output_path = "output.svg"
    potrace_executable = "potrace"

    lines, width, height, width_inch, height_inch, width_cm, height_cm, output_path = conversion_svg(input_path, output_path, potrace_executable)
    convert_to_a4(output_path, output_path, width, height)
    # animation lines
    strokes, num_strokes = extract_coordinates(output_path, samples=30)
    animation_simulation(strokes)