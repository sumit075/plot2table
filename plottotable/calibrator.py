import cv2
import numpy as np
import Image
import subprocess
import lxml.html as lh
from axisDetector import AxesDetection
from legend_detect import getOCRLines


def getHlabel(img, x, y, w, h):
    """
    Crop H axis and label data(below x axis)
    """
    hlabel = img[y:y + h, x:x + w]

    return hlabel


def getVlabel(img, x, y, w, h):
    """
    Crop Y axis and label data(before y axis)
    """
    vlabel = img[y:y + h, x:x + w]

    return vlabel


def getVerticalSplit(vlabel):
    """
    Get local minima and split the y axis data image
    """
    gray = vlabel.copy()
    shape = gray.shape
    rows = shape[0]
    cols = shape[1]

    ret, gray = cv2.threshold(gray, 127, 255, cv2.THRESH_BINARY)

    y = []
    sumr = []

    for i in range(0, cols - 1):
        if i == 0:
            sumr.append(0)
            for j in range(0, rows - 1):
                for k in range(-10, 10):
                    idx = k + i
                    if idx < 0:
                        idx = 0
                    elif idx >= cols:
                        idx = cols - 1
                    sumr[i] += gray[j][idx]
        else:
            sumr.append(sumr[i - 1])

        if i > 10:
            for j in range(0, rows - 1):
                sumr[i] -= gray[j][i - 11]
        else:
            for j in range(0, rows - 1):
                sumr[i] -= gray[j][0]

        if i < cols - 11:
            for j in range(0, rows - 1):
                sumr[i] += gray[j][i + 10]
        else:
            for j in range(0, rows - 1):
                sumr[i] += gray[j][cols - 1]

    begin_check = 0
    for i in range(0, cols - 1):
        percent = (float(sumr[i]) / (20 * 255 * rows)) * 100

        if begin_check == 0 and percent < 99:
            ya = i
            begin_check = 1

        if begin_check == 1 and percent > 99:
            yb = i
            begin_check = 0
            if abs(yb - ya) > 4:  # Neglecting small strips of black and noise
                y.append([max(ya - 10, 0), min(yb + 10, cols)])

    if begin_check == 1:
        yb = i
        begin_check = 0
        if abs(yb - ya) > 4:  # Neglecting small strips of black and noise
            y.append([max(ya - 10, 0), min(yb + 10, cols)])

    end = len(y) - 1
    x1 = y[end - 1]
    x2 = y[end - 2]

    vlabel_val = vlabel[0:rows, x1[0]:x1[1]]
    vlabel_axis = vlabel[0:rows, x2[0]:x2[1]]
    print "Done!"
    return vlabel_val, vlabel_axis


def getHorizontalSplit(hlabel):
    """
    Get local minima and split the x axis data image
    """
    gray = hlabel.copy()
    shape = gray.shape
    rows = shape[0]
    cols = shape[1]

    ret, gray = cv2.threshold(gray, 127, 255, cv2.THRESH_BINARY)

    y = []

    begin_check = 0
    for i in range(0, rows - 1):
        sumr = 0
        for j in range(0, cols - 1):
            sumr += gray[i][j]

        percent = (float(sumr) / (255 * cols)) * 100

        if begin_check == 0 and percent < 99:
            ya = i
            begin_check = 1

        if begin_check == 1 and percent > 99:
            yb = i
            begin_check = 0
            # Neglecting small strips of black and noise
            if abs(yb - ya) > 10:
                y.append([max(ya - 10, 0), min(yb + 10, rows)])

    if begin_check == 1:
            yb = i
            begin_check = 0
            # Neglecting small strips of black and noise
            if abs(yb - ya) > 10:
                y.append([max(ya - 10, 0), min(yb + 10, rows)])

    y1 = y[0]
    y2 = y[1]

    hlabel_val = hlabel[y1[0]:y1[1], 0:cols]
    hlabel_axis = hlabel[y2[0]:y2[1], 0:cols]

    return hlabel_axis, hlabel_val


def imgResize(img, finalDimension):
    """
    Function to resize image(opencv resizing)
    """
    shape = img.shape
    rows = shape[0]
    cols = shape[1]

    if rows > cols:
        scale = finalDimension / rows
    else:
        scale = finalDimension / cols

    img = cv2.resize(img, None, fx=scale,
                     fy=scale, interpolation=cv2.INTER_CUBIC)

    return img


def binarize(img, shape):
    """
    Function to grayscale and threshold binarize image
    """
    dim = max(shape)
    if dim == shape[0]:
        if dim < 350:
            thresh = 197
        else:
            thresh = 177

    if dim == shape[1]:
        if dim < 600:
            thresh = 197
        else:
            thresh = 177

    img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    ret, img = cv2.threshold(img, thresh, 255, cv2.THRESH_TOZERO)

    return img


def preProcessLabel(label, size):
    """
    Process x and y label data before passig it to the tesseract OCR
    """
    shape = label.shape

    label = imgResize(label, size)
    label = binarize(label, shape)
    return label


def rotateYlabel(label):
    """
    Function to rotate y axis label
    """
    label = cv2.transpose(label)
    label = cv2.flip(label, 1)
    return label


def prepareHocr(img):
    """
    Function to call tesseract hocr command on an image file
    """
    subprocess.call("tesseract " + img +
                    ".jpg outtess hocr digits", shell=True)
    subprocess.call("mv outtess.hocr outtess.html", shell=True)
    block = getOCRLines('outtess.html')
    return block


def prepareTesseract(img):
    """
    Function to run tesseract ocr on image file
    """
    subprocess.call("tesseract " + img + ".jpg out -l eng", shell=True)
    fp = open("out.txt")

    return fp.read().strip()


def getVaxisData(block, rows, size):
    """
    Function to process hocr block of y axis and return data
    """
    nums = []
    block = processBlock(block)
    for ele in block:
        ele = ele.split(",")
        num = ele[0]
        x1 = ele[1]
        y1 = ele[2]
        x2 = ele[3]
        y2 = ele[4]

        try:
            nums.append([float(num), (float(y1) + float(y2)) / 2])
            if len(nums) == 2:
                break
        except ValueError:
            print("not a float, checking next y axis number...")

    if len(nums) == 2:
        reference = nums[1]
        scale = size / rows
        gradient = abs(float(nums[1][0] - nums[0][0])) / abs(
            nums[1][1] - nums[0][1])
        gradient = gradient * scale
        reference[1] = reference[1] / scale
        return gradient, reference
    else:
        return False, False


def quantizeAxisEnd(x, step, reference, marker):
    """
    Function to quantize x axis labels into endpoint values
    """
    rangeQ = float(step / 2)
    if marker == 1:
        while True:
            if abs(reference - x) <= rangeQ:
                x = reference
                break
            reference += step
    elif marker == -1:
        while True:
            if abs(reference - x) <= rangeQ:
                x = reference
                break
            reference -= step
    return x


def maxOccurence(steps):
    d = {}
    k = {}
    maxim = 0
    for step in steps:
        try:
            d[str(step)] += 1
            k[str(d[str(step)])] = step
            if d[str(step)] > maxim:
                maxim = d[str(step)]
        except KeyError:
            d = {
                str(step): 1
            }

    step = k[str(maxim)]
    return step


def getXaxisData(block, xo1, xo2, cols, size):
    """
    Function to get x axis data from hocr block
    """
    steps = []
    nums = []
    nums1 = []
    block = processBlock(block)
    dist = 0
    check = -1
    for ele in block:
        ele = ele.split(",")
        num = ele[0]
        x1 = ele[1]
        y1 = ele[2]
        x2 = ele[3]
        y2 = ele[4]

        try:
            if 'prevnum' in locals():
                step = abs(float(num) - prevnum) / (dist + 1)
                steps.append(step)
            nums.append([float(num), (float(x1) + float(x2)) / 2, (dist + 1)])
            prevnum = float(num)
            dist = 0
        except ValueError:
            dist += 1
            print("Not a float, checking next y axis number...")

    if len(nums) >= 2:

        step = maxOccurence(steps)

        for num in nums:
            if 'prevnum1' in locals():
                dist = num[2]
                step_check = abs(num[0] - prevnum1) / dist
                if step_check == step:
                    nums1.append(num)
            prevnum1 = num[0]

        reference = nums1[1]
        gradient = abs(float(nums1[1][0] - nums1[0][0])) / abs(
            nums1[1][1] - nums1[0][1])

        scale = size / cols
        gradient = gradient * scale
        reference[1] = reference[1] / scale

        minVal = quantizeAxisEnd(reference[0] + gradient * (
            float(xo1) - reference[1]), step, reference[0], -1)
        maxVal = quantizeAxisEnd(reference[0] + gradient * (
            float(xo2) - reference[1]), step, reference[0], 1)

        startPixel = reference[1] + float(minVal - reference[0]) / gradient

        return minVal, maxVal, step, gradient, startPixel
    else:
        return False, False, False, False, False


def processBlock(block):
    """
    Convert hocr block , convert 2d hocr block array to 1d array
    """
    out = []
    a = ""
    for i in block:
        for j in i:
            if a == "":
                a = j
            else:
                a = a + "|" + j

    out = a.split("|")
    return out


def getLabelData(img_path):
    """
    Takes image(plot) path and returns all x axis and y axis related data
    (along with labels)
    """

    y_error = x_error = False

    try:  # Processing for Y axis data
        img = cv2.imread(img_path)
        imgAxes = AxesDetection(img)

        img_shape = img.shape

        rows = img_shape[0]
        cols = img_shape[1]

        vlabel = getVlabel(img, 0, 0, imgAxes["vaxisX"] - 2, imgAxes["haxisY"])
        vlabel = preProcessLabel(vlabel, 1000.0)
        vlabel_val, vlabel_axis = getVerticalSplit(vlabel)
        vlabel_val = rotateYlabel(vlabel_val)

        cv2.imwrite("vlabel_val.jpg", vlabel_val)
        cv2.imwrite("vlabel_axis.jpg", vlabel_axis)
    except:
        y_error = True

    try:  # Processing for X axis data
        hlabel = getHlabel(
            img, 0, imgAxes["haxisY"] + 2, cols, rows - imgAxes["haxisY"] - 2)
        hlabel = preProcessLabel(hlabel, 1000.0)
        hlabel_val, hlabel_axis = getHorizontalSplit(hlabel)
        cv2.imwrite("hlabel_val.jpg", hlabel_val)
        cv2.imwrite("hlabel_axis.jpg", hlabel_axis)
    except:
        x_error = True

    if not x_error:
        try:
            receipt = Image.open("hlabel_val.jpg")
            receipt.load()

            hlabel_val_text = prepareTesseract("hlabel_val")
            if hlabel_val_text == '':
                hlabel_val_text = 'X-Label'
        except:
            hlabel_val_text = 'X-Label'

        try:
            hocr_block = prepareHocr("hlabel_axis")
            minVal, maxVal, stepX, gradientX, startPixel = getXaxisData(
                hocr_block, imgAxes["vaxisX"], imgAxes["vaxisX2"],
                cols, 1000.0)

            xMin = [minVal, startPixel]
            xMax = maxVal
        except:
            xMin = False
            xMax = False
            stepX = False
            gradientX = False
            x_error = True

    if not y_error:
        try:
            receipt = Image.open("vlabel_val.jpg")
            receipt.load()

            vlabel_val_text = prepareTesseract("vlabel_val")

            if vlabel_val_text == '':
                vlabel_val_text = 'Y-Label'
        except:
            vlabel_val_text = 'Y-Label'

        try:
            hocr_block = prepareHocr("vlabel_axis")
            gradientY, referenceY = getVaxisData(
                hocr_block, imgAxes["haxisY"], 1000.0)
        except:
            gradientY = False
            referenceY = False
            y_error = True

    print "Labels Done!"

    if y_error or not referenceY or not gradientY:
        return False, False, False, False, False, False, False, False
    if x_error or not xMin or not xMax or not stepX or not gradientX:
        return False, False, False, False, referenceY, gradientY, \
            hlabel_val_text, vlabel_val_text
    else:
        return xMin, xMax, stepX, gradientX, referenceY, gradientY, \
            hlabel_val_text, vlabel_val_text
