from PIL import Image, ImageDraw
import math

# Create a 256x256 icon
size = 256
image = Image.new('RGBA', (size, size), (0, 0, 0, 0))  # Start with transparent
draw = ImageDraw.Draw(image)

# Create dark gradient background: top black (#000000) to bottom dark purple (#800080)
for y in range(size):
    # Interpolate color from black to dark purple
    ratio = y / size
    r = int(0 + ratio * 128)  # 0 to 128 (but #800080 is 128,0,128)
    g = int(0 + ratio * 0)
    b = int(0 + ratio * 128)
    color = (r, g, b, 255)  # Opaque
    draw.line([(0, y), (size, y)], fill=color)

# Draw stylized blue "C" with 3D shadow effect
c_color = (0, 102, 204, 255)  # Blue #0066CC
shadow_color = (0, 0, 0, 128)  # Semi-transparent black shadow

# Shadow first (offset down-right by 4px)
shadow_center_x, shadow_center_y = size // 2 + 4, size // 2 + 4
shadow_radius = 75
shadow_thickness = 8
draw.arc(
    (shadow_center_x - shadow_radius, shadow_center_y - shadow_radius * 1.2,
     shadow_center_x + shadow_radius, shadow_center_y + shadow_radius * 1.2),
    start=20, end=200,  # Arc for "C" shape (open to right)
    fill=shadow_color, width=shadow_thickness
)

# Main "C" on top
center_x, center_y = size // 2, size // 2
radius = 75
thickness = 8
draw.arc(
    (center_x - radius, center_y - radius * 1.2,
     center_x + radius, center_y + radius * 1.2),
    start=20, end=200,  # Stylized "C" arc
    fill=c_color, width=thickness
)

# Add subtle glow/outline for 3D effect (thinner white-ish arc outside)
glow_color = (173, 216, 230, 128)  # Light blue glow, semi-transparent
draw.arc(
    (center_x - radius - 2, center_y - radius * 1.2 - 2,
     center_x + radius + 2, center_y + radius * 1.2 + 2),
    start=20, end=200,
    fill=glow_color, width=2
)

# Save as ICO with multiple sizes
image.save('icon.ico', format='ICO', sizes=[(256, 256), (128, 128), (64, 64), (32, 32), (16, 16)])
