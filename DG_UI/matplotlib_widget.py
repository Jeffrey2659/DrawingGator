from PyQt6.QtWidgets import QWidget, QVBoxLayout
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib.animation as animation

class MatplotlibWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.figure = Figure(figsize=(8, 6))
        self.canvas = FigureCanvas(self.figure)

        layout = QVBoxLayout()
        layout.addWidget(self.canvas)
        self.setLayout(layout)

        self.ax = None
        self.ani = None  

    def clear(self):
        self.figure.clear()
        self.ax = None
        self.canvas.draw()


##############################################################################
############ BELOW THERE ARE TWO FUNCTIONS FOR PLOTTING SVG ##################
############ NR.1 --> OUTPUT OF SVG FILE #####################################
############ NR.2 --> ANIMATION SIMULATION ###################################

    # same function as in svg_algorithm.py 
    def plot_svg(self, strokes, num_strokes = None, image_size = None):
        self.clear()
        self.ax = self.figure.add_subplot(111)
        self.ax.set_aspect('equal')
        self.ax.invert_yaxis()
        self.ax.axis('off')
        
        if not strokes or not any(strokes):
            return
        
        # num strokes
        if num_strokes is None:
            num_strokes = len(strokes)

        def get_points(stroke):
            return stroke['points'] if isinstance(stroke, dict) else stroke

        def get_color(stroke):
            return stroke['color'] if isinstance(stroke, dict) else 'black'

        all_points = [p for stroke in strokes for p in get_points(stroke)]
        if not all_points:
            return

        xs, ys = zip(*all_points)
        
        # Add margin
        x_range = max(xs) - min(xs) if max(xs) != min(xs) else 1
        y_range = max(ys) - min(ys) if max(ys) != min(ys) else 1
        pad_x = x_range * 0.05
        pad_y = y_range * 0.05
        
        self.ax.set_xlim(min(xs) - pad_x, max(xs) + pad_x)
        self.ax.set_ylim(min(ys) - pad_y, max(ys) + pad_y)
        
        # Draw all strokes
        for stroke in strokes:
            pts = get_points(stroke)
            color = get_color(stroke)
            if pts:
                xs_stroke = [p[0] for p in pts]
                ys_stroke = [p[1] for p in pts]
                self.ax.plot(xs_stroke, ys_stroke, color=color, linewidth=2)

        # adding line to display the image size
        if image_size is not None:
            width_inch, height_inch = image_size
            self.figure.text(0.02, 0.98, f'Number of Strokes: {num_strokes} Image Size: {width_inch:.2f} x {height_inch:.2f} inch',
                     ha = 'left', va = 'top',
                     fontsize = 10, fontweight = 'bold')
        
        self.canvas.draw()

    def update_colors(self, color_str: str):
        self.current_color = color_str

        # update the color of the displayed image based on the color selected
        if self.ax:
            for line in self.ax.lines:
                line.set_color(self.current_color)
            self.canvas.draw_idle()



'''        
    def plot_svg(self, strokes, interval=1):
        self.clear()
        self.ax = self.figure.add_subplot(111)
        self.ax.set_aspect('equal')
        self.ax.invert_yaxis()
        self.ax.axis('off')

        if not strokes or not any(strokes):
            return

        all_points = [p for stroke in strokes for p in stroke]
        xs, ys = zip(*all_points)

        # Padding
        pad_x = (max(xs) - min(xs)) * 0.05
        pad_y = (max(ys) - min(ys)) * 0.05
        self.ax.set_xlim(min(xs) - pad_x, max(xs) + pad_x)
        self.ax.set_ylim(min(ys) - pad_y, max(ys) + pad_y)

        # Create a line object for each stroke
        lines = [self.ax.plot([], [], lw=2, color='black')[0] for _ in strokes]

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

        frames = [(i, j) for i, stroke in enumerate(strokes) for j in range(1, len(stroke) + 1)]

        self.ani = animation.FuncAnimation(
            self.figure,
            update,
            frames=frames,
            init_func=init,
            blit=True,
            interval=interval,
            repeat=False
        )

        self.canvas.draw()
'''