from cv2 import cvtColor, COLOR_BGR2GRAY
from cv2.aruco import (
    getPredefinedDictionary,
    DICT_5X5_100,
    DetectorParameters,
    ArucoDetector
)
from json import load

with open('blocks.json') as f:
    blocks = load(f)

dictionary = getPredefinedDictionary(DICT_5X5_100)

parameters = DetectorParameters()
parameters.adaptiveThreshWinSizeMin = 3
parameters.adaptiveThreshWinSizeMax = 23
parameters.adaptiveThreshWinSizeStep = 10
parameters.adaptiveThreshConstant = 7

detector = ArucoDetector(dictionary, parameters)


def read_arucos(img):
    gray = cvtColor(img, COLOR_BGR2GRAY)
    corners, ids, _ = detector.detectMarkers(gray)
    if ids is None:
        return None

    data = []
    for i, marker_id in enumerate(ids):
        c = corners[i][0]
        x = int(c[:, 0].mean())
        y = int(c[:, 1].mean())
        data.append((x, y, marker_id[0]))

    data.sort(key=lambda t: (t[1], t[0]))

    lines = []
    y_threshold = 40

    for x, y, marker_id in data:
        for line in lines:
            if abs(line['y'] - y) < y_threshold:
                line['items'].append((x, marker_id))
                break
        else:
            lines.append({'y': y, 'items': [(x, marker_id)]})

    lines.sort(key=lambda l: l['y'])

    final_text = []

    for line in lines:
        line['items'].sort(key=lambda t: t[0])
        words = []

        for x, marker_id in line['items']:
            key = str(marker_id)
            if key in blocks:
                words.append(blocks[key])

        final_text.append(' '.join(words))

    return '\n'.join(final_text)