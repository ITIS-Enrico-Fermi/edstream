from PIL import Image

img = Image.open("lib/edstream/tools/image.bmp")
img_bytes = img.tobytes()

print("Ok")