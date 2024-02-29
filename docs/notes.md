

# Crop to center

	width, height = im.size   # Get dimensions

	new_width = 2000
	new_height = 2000

	left = round((width - new_width)/2)
	top = round((height - new_height)/2)
	x_right = round(width - new_width) - left
	x_bottom = round(height - new_height) - top
	right = width - x_right
	bottom = height - x_bottom

	# Crop the center of the image
	im = im.crop((left, top, right, bottom))


## Add copyright

	# textwidth, textheight = drawing.textbbox((0,0), text, font=font, fill="black", ) # fill="black"
	draw = drawing
	position = (0, 0)

	left, top, right, bottom = draw.textbbox(position, text, font=font)
	print(left, top, right, bottom)
	padding_y = 2
	padding_x = 3

	text_height = bottom - top
	text_width = right - left

	new_x1 = w-text_width - padding_x
	new_x2 = w-text_width + right + padding_x
	new_y1 = h-text_height - padding_y
	new_y2 = h-text_height + bottom + padding_y

	new_pos = (new_x1, new_y1)
	print(new_pos)

	draw.rectangle((new_x1, new_y1, new_x2, new_y2), fill="black")
	draw.text(new_pos, text, font=font, fill="white")

