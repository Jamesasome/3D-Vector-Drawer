import pyqtgraph as pg 
from pyqtgraph.Qt import QtWidgets 
import pyqtgraph.opengl as gl
import numpy as np 
from vectors import Vector 

####################################################################################
class FunctionRunner(QtWidgets.QWidget):
    def __init__(self, functions: dict):
        super().__init__()
        self.functions = functions  # store dict internally

        self.setWindowTitle("Function Runner")
        self.resize(300, 50)

        self.dropdown = QtWidgets.QComboBox()
        self.dropdown.addItems(functions.keys())

        self.run_button = QtWidgets.QPushButton("Run")
        self.run_button.clicked.connect(self.run_selected_function)

        h_layout = QtWidgets.QHBoxLayout()
        h_layout.addWidget(self.dropdown)
        h_layout.addWidget(self.run_button)

        self.setLayout(h_layout)

    def run_selected_function(self):
        func_name = self.dropdown.currentText()
        func = self.functions.get(func_name)
        if func:
            func()


###########################################################

vector_items = []  # global or persistent list
grid = []
axis_item = None
max2 = 5

###########################################################

# --- App and window --- 
app = QtWidgets.QApplication([]) 
window = QtWidgets.QWidget() 
window.setWindowTitle("Vector Drawer") 
layout = QtWidgets.QVBoxLayout() 
window.setLayout(layout) 

# 3D view
plot = gl.GLViewWidget(parent=window)
plot.setMinimumSize(700, 500)
plot.setCameraPosition(distance=15)
plot.setBackgroundColor('k')

# Axes
axes = gl.GLAxisItem()
axes.setSize(5,5,5)
plot.addItem(axes)

layout.addWidget(plot)

###########################################################

# --- Input fields --- 
input_layout = QtWidgets.QHBoxLayout() 
layout.addLayout(input_layout) 


input_layout.addWidget(QtWidgets.QLabel("Vector (x,y,z):"))
vector_input = QtWidgets.QLineEdit("3,2,1")
input_layout.addWidget(vector_input)

draw_btn = QtWidgets.QPushButton("Draw Vectors")
clear_btn = QtWidgets.QPushButton("Clear Vectors")

input_layout.addWidget(draw_btn)
input_layout.addWidget(clear_btn)

############################################################

# --- Store vectors ---
vectors_to_draw = []  # list of Vector objects

############################################################

# --- Dropdowns for selecting two vectors to sum ---
select_layout = QtWidgets.QHBoxLayout()
layout.addLayout(select_layout)

vec1_dropdown = QtWidgets.QComboBox()
vec2_dropdown = QtWidgets.QComboBox()

select_layout.addWidget(QtWidgets.QLabel("Vector 1:"))
select_layout.addWidget(vec1_dropdown)
select_layout.addWidget(QtWidgets.QLabel("Vector 2:"))
select_layout.addWidget(vec2_dropdown)

############################################################

# --- Helpers ---
def update_dropdowns():
    vec_strings = [f"({v.vector[0]}, {v.vector[1]}, {v.vector[2]})" for v in vectors_to_draw]
    vec1_dropdown.clear()
    vec2_dropdown.clear()
    vec1_dropdown.addItems(vec_strings)
    vec2_dropdown.addItems(vec_strings)

def create_grid_axis(a):
    global axis_item
    if axis_item:
        plot.removeItem(axis_item)
    axis_item = gl.GLAxisItem()
    axis_item.setSize(a,a,a)
    plot.addItem(axis_item)
    
def max_point(points):
    if not points:
        return 5
    elif max(abs(coord) for p in points for coord in p) < 5:
        return 5
    return max(abs(coord) for p in points for coord in p)

def create_grid_plane(plane='XY', size=10, spacing=1, color=(0.5,0.5,0.5,0.3)):
    global grid
    coords = np.arange(-size, size+spacing, spacing)
    for c in coords:
        if plane == 'XY':
            pts1 = np.array([[-size, c, 0], [size, c, 0]])
            pts2 = np.array([[c, -size, 0], [c, size, 0]])
        elif plane == 'XZ':
            pts1 = np.array([[-size, 0, c], [size, 0, c]])
            pts2 = np.array([[c, 0, -size], [c, 0, size]])
        elif plane == 'YZ':
            pts1 = np.array([[0, -size, c], [0, size, c]])
            pts2 = np.array([[0, c, -size], [0, c, size]])
        a = gl.GLLinePlotItem(pos=pts1, color=color, width=1, antialias=True)
        b = gl.GLLinePlotItem(pos=pts2, color=color, width=1, antialias=True)
        plot.addItem(a)
        plot.addItem(b)
        grid.extend([a, b])  # track each line
        
def draw_vector(vec, color=(1,0,0,1), width=2, tip_radius=0.1):
    pts = np.array([[0,0,0], vec])
    line = gl.GLLinePlotItem(pos=pts, color=color, width=width, antialias=True)
    plot.addItem(line)
    
    md = gl.MeshData.sphere(rows=10, cols=10, radius=tip_radius)
    sphere = gl.GLMeshItem(meshdata=md, smooth=True, color=color, shader='shaded', glOptions='opaque')
    sphere.translate(*vec)
    plot.addItem(sphere)

    # Return both items separately
    return line, sphere

def input_vectors():
    vec = None
    try:
        x, y, z = vector_input.text().split(',')
        vec = Vector(vector=[float(x), float(y), float(z)])
    except Exception:
        QtWidgets.QMessageBox.warning(window, "Input Error", "Enter numbers as x,y,z")
        return

    # Store vector
    vectors_to_draw.append(vec)
    vector_input.clear()

    # Assign colors (cycle through)
    colors = [(1,0,0,1), (0,1,0,1), (0,0,1,1), (1,1,0,1)]
    items = [(v, colors[i % len(colors)]) for i, v in enumerate(vectors_to_draw)]

    # Extract points
    points = [tuple(v.vector) for v in vectors_to_draw]

    # Compute scale
    maxa = max_point(points)

    # Draw everything
    draw_vec(items, maxa)

    # Update dropdowns
    update_dropdowns()
    
    
def input_vecs(vector3):
    vec = None
    x, y, z = vector3.vector
    vec = Vector(vector=[float(x), float(y), float(z)])

    # Store vector
    vectors_to_draw.append(vec)

    # Assign colors (cycle through)
    colors = [(1,0,0,1), (0,1,0,1), (0,0,1,1), (1,1,0,1),(0,1,1,1),(1,1,1,1)]
    items = [(v, colors[i % len(colors)]) for i, v in enumerate(vectors_to_draw)]

    # Extract points
    points = [tuple(v.vector) for v in vectors_to_draw]

    # Compute scale
    maxa = max_point(points)

    # Draw everything
    draw_vec(items, maxa)

    # Update dropdowns
    update_dropdowns()
    
    
     
def clear_vectors():
    global vector_items, grid
    

    for item in vector_items:
        plot.removeItem(item)
    vector_items = []

    for item in grid:
        plot.removeItem(item)
    grid = []

    vectors_to_draw.clear()

    create_grid_axis(max2+2)
    create_grid_plane('XY', size=max2+2)
    create_grid_plane('XZ', size=max2+2)
    create_grid_plane('YZ', size=max2+2)

    plot.setCameraPosition(distance=max2*2)
    update_dropdowns()
    
# Draw all vectors and grids
def draw_vec(items, maxa):
    global vector_items, grid, max2

    max2 = maxa
    # Remove old grids
    for item in grid:
        plot.removeItem(item)
    grid = []

    # Adjust camera
    plot.setCameraPosition(distance=maxa*2)
    create_grid_axis(maxa+2)

    # Draw new vectors
    for vec, color in items:
        line, sphere = draw_vector(vec.vector, color)
        vector_items.extend([line, sphere])

    # Draw new grids
    create_grid_plane('XY', size=maxa+2, spacing=1)
    create_grid_plane('XZ', size=maxa+2, spacing=1)
    create_grid_plane('YZ', size=maxa+2, spacing=1)
    
#####################################################################################
def add_vectors():
    """Add two selected vectors from dropdown, store their sum in the list."""
    if len(vectors_to_draw) < 2:
        QtWidgets.QMessageBox.warning(window, "Need vectors", "Choose at least two vectors first")
        return

    idx1 = vec1_dropdown.currentIndex()
    idx2 = vec2_dropdown.currentIndex()

    if idx1 < 0 or idx2 < 0:
        QtWidgets.QMessageBox.warning(window, "Select vectors", "Select two vectors to add")
        return

    v1 = vectors_to_draw[idx1]
    v2 = vectors_to_draw[idx2]

    result = v1 + v2 # + in vec class defined
    input_vecs(result)
    
def subtract_vectors():
    """Subtracts two selected vectors from dropdown, store their difference in the list."""
    if len(vectors_to_draw) < 2:
        QtWidgets.QMessageBox.warning(window, "Need vectors", "Choose at least two vectors first")
        return

    idx1 = vec1_dropdown.currentIndex()
    idx2 = vec2_dropdown.currentIndex()

    if idx1 < 0 or idx2 < 0:
        QtWidgets.QMessageBox.warning(window, "Select vectors", "Select two vectors to subtract")
        return

    v1 = vectors_to_draw[idx1]
    v2 = vectors_to_draw[idx2]

    result = v1 - v2 # - in vec class defined
    input_vecs(result)   
    
def crossproduct_vectors():
    """Cross product two selected vectors from dropdown, store their crossproduct in the list."""
    if len(vectors_to_draw) < 2:
        QtWidgets.QMessageBox.warning(window, "Need vectors", "Choose at least two vectors first")
        return

    idx1 = vec1_dropdown.currentIndex()
    idx2 = vec2_dropdown.currentIndex()

    if idx1 < 0 or idx2 < 0:
        QtWidgets.QMessageBox.warning(window, "Select vectors", "Select two vectors to find the Cross Product Of")
        return

    v1 = vectors_to_draw[idx1]
    v2 = vectors_to_draw[idx2]

    result = v1.crossproduct(v2) # - in vec class defined
    input_vecs(result)  
 
#############################################################

# Add grids
create_grid_plane('XY', size=5, spacing=1)
create_grid_plane('XZ', size=5, spacing=1)
create_grid_plane('YZ', size=5, spacing=1)

#############################################################

items = []
points = []
    
#############################################################

# --- Connect button --- 
draw_btn.clicked.connect(input_vectors)
clear_btn.clicked.connect(clear_vectors)

functions = {"Add Vectors" : add_vectors, "Subtract Vectors" : subtract_vectors,
             "Cross Product of Vectors" : crossproduct_vectors }

func_runner = FunctionRunner(functions)
layout.addWidget(func_runner)


# --- Show window --- 
window.show() 
app.exec()