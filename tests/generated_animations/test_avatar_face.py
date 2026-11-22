import numpy as np
from PIL import Image

from generated_animations.avatar import face


def test_frames_differ_by_mouth_and_blink():
    f = face.get()
    closed, open_, blink = f.frame(0, 0), f.frame(1.0, 0), f.frame(0, 1.0)
    assert closed.shape == open_.shape == blink.shape and closed.shape[2] == 4
    assert not np.array_equal(closed, open_)
    assert not np.array_equal(closed, blink)


def test_base_picture_has_transparent_backdrop():
    a = np.asarray(Image.open(face.BASE))
    assert a[0, 0, 3] == 0 and a[a.shape[0] // 2, a.shape[1] // 2, 3] == 255
