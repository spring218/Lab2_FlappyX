from PIL import Image, ImageDraw

# Create a new image with a white background
img = Image.new('RGB', (34, 24), color='yellow')
draw = ImageDraw.Draw(img)

# Draw a simple bird shape
draw.ellipse([2, 2, 32, 22], fill='red')  # Body
draw.ellipse([20, 5, 30, 15], fill='white')  # Eye
draw.ellipse([25, 8, 28, 11], fill='black')  # Pupil
draw.polygon([(15, 12), (25, 8), (25, 16)], fill='orange')  # Beak

# Save the image
img.save('profile_picture.jpg') 