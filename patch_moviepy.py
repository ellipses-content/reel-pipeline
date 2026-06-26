import numpy as np
import moviepy.video.tools.drawing as d

patch = '''import numpy as np

def blit(im1, im2, pos=None, mask=None, ismask=False):
    if pos is None:
        pos = [0, 0]
    pos = list(pos)
    xp, yp = int(pos[0]), int(pos[1])
    x1, y1 = max(0, xp), max(0, yp)
    x2 = min(xp + im1.shape[1], im2.shape[1])
    y2 = min(yp + im1.shape[0], im2.shape[0])
    xl, yl = x1 - xp, y1 - yp
    xr = xl + (x2 - x1)
    yr = yl + (y2 - y1)
    if (x1 >= x2) or (y1 >= y2):
        return im2
    blitted = im1[yl:yr, xl:xr]
    new_im2 = im2.copy()
    if mask is None:
        if new_im2.ndim == 2 and blitted.ndim == 3:
            blitted = blitted.mean(axis=2).astype(new_im2.dtype)
        elif new_im2.ndim == 3 and blitted.ndim == 2:
            blitted = np.stack([blitted, blitted, blitted], axis=2)
        new_im2[y1:y2, x1:x2] = blitted
    else:
        mask_region = mask[yl:yr, xl:xr]
        if mask_region.ndim == 2:
            mask_region = mask_region[:, :, np.newaxis]
        if ismask:
            if new_im2.ndim == 2 and blitted.ndim == 3:
                blitted = blitted.mean(axis=2).astype(new_im2.dtype)
            elif new_im2.ndim == 3 and blitted.ndim == 2:
                blitted = np.stack([blitted, blitted, blitted], axis=2)
            new_im2[y1:y2, x1:x2] = blitted
        else:
            if blitted.ndim == 2:
                blitted = np.stack([blitted, blitted, blitted], axis=2)
            new_im2[y1:y2, x1:x2] = (mask_region * blitted + (1 - mask_region) * new_im2[y1:y2, x1:x2])
    return new_im2
'''

with open(d.__file__, 'w') as f:
    f.write(patch)
print('drawing.py patched successfully')


# --- resize.py: Pillow >= 10 removed Image.ANTIALIAS ---------------------
# moviepy 1.0.3 still calls Image.ANTIALIAS, which was deprecated in Pillow 9
# and removed in Pillow 10. Image.LANCZOS is the identical filter under the
# new name and is still available in current Pillow, so swap it in.
import moviepy.video.fx.resize as r

with open(r.__file__, 'r') as f:
    resize_src = f.read()

if 'Image.ANTIALIAS' in resize_src:
    resize_src = resize_src.replace('Image.ANTIALIAS', 'Image.LANCZOS')
    with open(r.__file__, 'w') as f:
        f.write(resize_src)
    print('resize.py patched successfully')
else:
    print('resize.py already patched (no Image.ANTIALIAS found)')