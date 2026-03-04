"""
Simple icon generator for Google Maps Scraper
Creates a basic map-pin style icon in ICO format
"""
from PIL import Image, ImageDraw
import os

def create_map_icon():
    """Create a simple map pin icon"""
    print("Creating Google Maps Scraper icon...")
    
    # Create assets folder
    os.makedirs('assets', exist_ok=True)
    
    # Create 256x256 image with transparency
    size = 256
    img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    
    # Color scheme
    pin_color = (220, 53, 69)      # Red (Google Maps style)
    outline_color = (150, 30, 40)   # Dark red
    inner_color = (255, 255, 255)   # White
    
    # Pin dimensions
    center_x = size // 2
    center_y = size // 2 - 20
    radius = 60
    
    # Draw outer circle (main pin body)
    draw.ellipse(
        [center_x - radius, center_y - radius, 
         center_x + radius, center_y + radius],
        fill=pin_color,
        outline=outline_color,
        width=5
    )
    
    # Draw triangle (point of pin)
    point_height = 60
    point_width = 30
    points = [
        (center_x, center_y + radius + point_height),  # Bottom point
        (center_x - point_width, center_y + radius),    # Top left
        (center_x + point_width, center_y + radius)     # Top right
    ]
    draw.polygon(points, fill=pin_color, outline=outline_color)
    
    # Draw inner circle (center dot)
    inner_radius = 25
    draw.ellipse(
        [center_x - inner_radius, center_y - inner_radius,
         center_x + inner_radius, center_y + inner_radius],
        fill=inner_color,
        outline=outline_color,
        width=3
    )
    
    # Draw center dot
    dot_radius = 12
    draw.ellipse(
        [center_x - dot_radius, center_y - dot_radius,
         center_x + dot_radius, center_y + dot_radius],
        fill=pin_color,
        outline=None
    )
    
    # Save as ICO with multiple sizes for Windows
    icon_path = 'assets/icon.ico'
    img.save(
        icon_path, 
        format='ICO',
        sizes=[(256, 256), (128, 128), (64, 64), (48, 48), (32, 32), (16, 16)]
    )
    
    print(f"✅ Icon created successfully: {icon_path}")
    print(f"   - Format: ICO (Windows Icon)")
    print(f"   - Sizes: 256x256, 128x128, 64x64, 48x48, 32x32, 16x16")
    print(f"   - Style: Map pin (Google Maps inspired)")
    print("")
    print("Next steps:")
    print("1. Run: .\\build_exe.ps1")
    print("2. Your executable will have the custom icon!")
    
    return icon_path

if __name__ == "__main__":
    try:
        create_map_icon()
    except ImportError:
        print("❌ Error: Pillow library not found")
        print("")
        print("Please install Pillow:")
        print("   pip install Pillow")
        print("")
        print("Then run this script again:")
        print("   python create_icon.py")
    except Exception as e:
        print(f"❌ Error creating icon: {e}")
        print("")
        print("Alternative options:")
        print("1. Download an icon from https://flaticon.com/")
        print("2. Convert an image at https://convertio.co/png-ico/")
        print("3. Build without icon (modify build_exe.spec)")
