from PIL import Image, ImageDraw, ImageSequence, ImageOps, ImageFont
import io
import tempfile


def add_text(text):
    im = Image.open('images/breakingbad.gif')

    frames = []
    durations = []

    for frame in ImageSequence.Iterator(im):
        durations.append(frame.info['duration'])
        frame = ImageOps.expand(frame.convert('RGB'), (0, 45, 0, 0), 'white')

        d = ImageDraw.Draw(frame)
        font_size = 33
        font = ImageFont.truetype("fonts/arial.ttf", font_size)
        w, h = d.textsize(text, font=font)
        while (w > frame.size[0] * 0.9):
            if font_size > 3:
                font_size -= 3
                font = ImageFont.truetype("fonts/arial.ttf", font_size)
                w, h = d.textsize(text, font=font)
            else:
                break

        d.text(
            ((frame.size[0] - w) / 2, (45 - h) / 2),
            text,
            font=font,
            fill='black')
        del d

        b = io.BytesIO()
        frame.save(b, format="GIF")
        frame = Image.open(b)

        frames.append(frame)

    tmpfile = io.BytesIO()
    frames[0].save(
        tmpfile,
        save_all=True,
        append_images=frames[1:],
        format="GIF",
        duration=durations,
        loop=0)
    tmpfile.seek(0)
    return tmpfile


if __name__ == "__main__":
    tmpfile = add_text("hammed burger :(")
    with open('test.gif', 'wb') as outfile:
        outfile.write(tmpfile.read())
