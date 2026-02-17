import os
import pygame

try:
    pygame.init()
    # Simulate being in src/toy.py
    current_file = os.path.join(os.getcwd(), 'src', 'toy.py')
    print(f"Simulated file: {current_file}")
    
    base_path = os.path.dirname(os.path.dirname(current_file))
    print(f"Base path: {base_path}")
    
    image_path = os.path.join(base_path, "assets", "images", "toy.png")
    print(f"Image path: {image_path}")
    
    if os.path.exists(image_path):
        print("SUCCESS: File exists!")
    else:
        print("FAILURE: File not found!")

except Exception as e:
    print(f"Error: {e}")
