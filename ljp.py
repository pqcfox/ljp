from math import sqrt, floor, ceil 
from PIL import Image, ImageDraw, ImageFilter

hue = 200 
saturation = 1.0 
value_bounds = (40, 50)
aspect = (8.5, 11)
box_size = 10
input_filename = 'article.txt'
output_filename = 'cover.png' 
blur_radius = 5 

# Read the associated file

with open(input_filename, 'r') as f:
    text = f.read()

# Convert all values into hex, then decimal

encoded = text.encode('hex')
hex_values = [encoded[i:i+2] for i in range(0, len(encoded), 2)]
values = [int(hex_value, 16) for hex_value in hex_values]

# Make the values fit into value_bounds

in_range = max(values) - min(values)
in_min = min(values)
out_range = value_bounds[1] - value_bounds[0]
out_min = value_bounds[0]

# Map the decimal integers into HSL colors

normalize = lambda n: out_range * (n - in_min) / in_range  + out_min
norm_values = [normalize(value) for value in values]
hsl_format = 'hsl({},{}%,{{}}%)'.format(int(hue), int(100 * saturation))
hsl_colors = [hsl_format.format(int(value)) for value in norm_values] 

# Determine, roughly, what the dimensions should be

aspect_area = aspect[0] * aspect[1]
target_area = len(values)
area_ratio = target_area / float(aspect_area)
large_enough = lambda s: s[0] * s[1] >= target_area
rough_size = tuple(value * sqrt(area_ratio) for value in aspect)

# Define different rounding methods to fit all the data

floor_ceil_size = (floor(rough_size[0]), ceil(rough_size[1]))
ceil_floor_size = (ceil(rough_size[0]), floor(rough_size[1]))
ceil_ceil_size = (ceil(rough_size[0]), ceil(rough_size[1]))
size = None

# Select the rounding method that fits best

if rough_size[0] < rough_size[1]:
    if large_enough(floor_ceil_size):
        selected_size = floor_ceil_size
    elif large_enough(ceil_floor_size):
        selected_size = ceil_floor_size
else:
    if large_enough(ceil_floor_size):
        selected_size = ceil_floor_size
    elif large_enough(floor_ceil_size):
        selected_size = floor_ceil_size

if size is None:
    size = ceil_ceil_size

# Map the HSL colors to a grid using rounded dimensions

size = (int(size[0]), int(size[1]))
grid = [[] for _ in range(size[1])]

for i in range(target_area):
    grid[i / size[0]].append(hsl_colors[i])

# Create a new image and draw all of the boxes

dimensions = tuple(value * box_size for value in size)
im = Image.new('RGB', dimensions)  
draw = ImageDraw.Draw(im)

for i in range(size[1]):
    for j in range(size[0]):
        location = (j * box_size, i * box_size)
        corner = tuple(value + box_size for value in location) 
        try:
            color = grid[i][j]
        except IndexError:
            color = hsl_format.format(out_min)
        draw.rectangle((location, corner), outline=color, fill=color)

# Apply optional blur

if blur_radius > 0:
    im = im.filter(ImageFilter.GaussianBlur(blur_radius)) 

# Clean up and save the finalized image

del draw
with open(output_filename, 'w') as f:
    im.save(f, 'PNG')
