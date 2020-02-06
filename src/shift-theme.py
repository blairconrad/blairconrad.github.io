import colorsys
import sys

with open(sys.argv[1]) as f:
    lines = [line.rstrip() for line in f]

shift = sys.argv[2]
if shift != "monochrome":
    shift = int(sys.argv[2])

for l in lines:
    output = l
    if (
        "-color:" in l
        and "#" in l
        and "success" not in l
        and "warning" not in l
        and "danger" not in l
        and "info" not in l
    ):

        color = l.split("#")[1][0:6]
        # if color[0:2] == color[2:4] == color[4:6]:
        #    continue

        r = int(color[0:2], 16) / 255
        g = int(color[2:4], 16) / 255
        b = int(color[4:6], 16) / 255
        # print(r, g, b)
        hls = colorsys.rgb_to_hls(r, g, b)

        if shift == "monochrome":
            hsl = [
                (int(hls[0] * 360)) % 360,
                0,
                int(hls[1] * 100),
            ]
        else:
            hsl = [
                shift,
                # (int(hls[0] * 360) + shift) % 360,
                int(hls[2] * 100),
                int(hls[1] * 100),
            ]
        # print(hls, "\t", color)
        output = l.replace("#" + color, f"hsl({hsl[0]}, {hsl[1]}%, {hsl[2]}%)")
    print(output)
