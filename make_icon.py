from PIL import Image

img = Image.open("logo.png").convert("RGBA")
sizes = [16, 32, 48, 64, 128, 256]
frames = [img.resize((s, s), Image.NEAREST) for s in sizes]
frames[0].save("logo.ico", format="ICO",
               sizes=[(s, s) for s in sizes],
               append_images=frames[1:])
print("logo.ico erstellt.")
