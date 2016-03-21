# Resize image
import cv2
import subprocess
import glob
import os
import re
import shutil
import numpy as np
from garbageImageDetector import isGarbageImage, isAxisPresent
from pylab import array, plot, show, axis, arange, figure, uint8
from sklearn.cluster import KMeans
from axisDetector import AxesDetection


def resizeImage(img, resizeTo=1000):

    shape = img.shape
    rows = shape[0]
    cols = shape[1]

    if rows > cols:
        scale = float(resizeTo) / rows
    else:
        scale = float(resizeTo) / cols

    img = cv2.resize(img, None, fx=scale,
                     fy=scale, interpolation=cv2.INTER_CUBIC)

    return img


# Morphological operations
def morphological(img):
    kernel = np.ones((1, 1), np.uint8)
    erosion = cv2.erode(img, kernel, iterations=1)
    kernel = np.ones((2, 2), np.uint8)
    dilation = cv2.dilate(erosion, kernel, iterations=1)
    return dilation


# Clustering
def cluster(img, K=10):
    Z = img.reshape((-1, 3))

    # convert to np.float32
    Z = np.float32(Z)

    # define criteria, number of clusters(K) and apply kmeans()
    criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 10, 1.0)

    ret, label, center = cv2.kmeans(
        Z, K, criteria, 10, cv2.KMEANS_RANDOM_CENTERS)

    # Now convert back into uint8, and make original image
    center = np.uint8(center)
    res = center[label.flatten()]
    res2 = res.reshape((img.shape))
    return res2, center

# enhancing


def sharpenImage(img):
    blur = cv2.bilateralFilter(img, 9, 75, 75)
    weighted = cv2.addWeighted(img, 1.5, blur, -0.5, 0)
    return weighted


def enhance(image):
    maxIntensity = 255.0  # depends on dtype of image data
    x = arange(maxIntensity)

    # Parameters for manipulating image data
    phi = 1
    theta = 1

    # Increase intensity such that
    # dark pixels become much brighter,
    # bright pixels become slightly bright
    newImage0 = (maxIntensity / phi) * (image / (maxIntensity / theta)) ** 0.5
    newImage0 = array(newImage0, dtype=uint8)

    y = (maxIntensity / phi) * (x / (maxIntensity / theta)) ** 0.5

    # Decrease intensity such that
    # dark pixels become much darker,
    # bright pixels become slightly dark
    newImage1 = (maxIntensity / phi) * (image / (maxIntensity / theta)) ** 2
    newImage1 = array(newImage1, dtype=uint8)

    return newImage1

# Otsu's binarization


def otsusBinarization(img):

    img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    # blur = cv2.bilateralFilter(img,9,75,75)
    ret, img = cv2.threshold(img, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

    return img

# Otsu's binarization


def iterativeThresholding(img):

    gray_img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    threshold = 0
    new_threshold = 100
    i = 0

    while not new_threshold <= threshold + 0.001 and \
            new_threshold >= threshold - 0.001:
        print i, new_threshold
        i += 1

        threshold = new_threshold
        th, th_img = cv2.threshold(gray_img, threshold, 255, cv2.THRESH_BINARY)

        count_back = 0
        avg_back = 0
        count_fore = 0
        avg_fore = 0

        for r, row in enumerate(th_img):
            for p, pixel in enumerate(row):
                if pixel == 255:
                    avg_back += gray_img[r][p]
                    count_back += 1
                else:
                    avg_fore += gray_img[r][p]
                    count_fore += 1

        avg_back = float(avg_back) / count_back
        # print count_back, avg_back
        avg_fore = float(avg_fore) / count_fore
        # print count_fore, avg_fore

        new_threshold = (avg_back + avg_fore) / 2

    return th_img


def makeEnlarged(page, ENLR_THRESH, MC_EXT=150):

    subprocess.call('convert -density 300 -trim output_%02d.pdf -quality 100 '
                    '-sharpen 0x1.0 raw_%02d.jpg' % (page, page), shell=True)

    subprocess.call("bash multicrop -u 3 " + ("raw_%02d.jpg " % page)
                    + ("multicrop-output/new_raw_mc_%02d.ppm " % page),
                    shell=True)
    subprocess.call(("bash multicrop -e %d -u 3 " % MC_EXT) +
                    ("raw_%02d.jpg " % page) +
                    ("multicrop-ext-output/new_raw_mc_%02d.ppm " % page),
                    shell=True)

    new_imgs = glob.glob1(
        'multicrop-ext-output/', "new_raw_mc_%02d*.ppm" % page)

    for i in new_imgs:
        # print i
        img = cv2.imread('multicrop-ext-output/' + i)
        img_2 = cv2.imread('multicrop-output/' + i)
        height, width = img_2.shape[:2]
        if isGarbageImage(img):
            try:
                os.remove("multicrop-output/" + i)
                os.remove("multicrop-ext-output/" + i)
            except Exception, e:
                print str(e)
        elif max(height, width) > 2 * ENLR_THRESH + 50:
            try:
                os.remove("multicrop-output/" + i)
                os.remove("multicrop-ext-output/" + i)
            except Exception, e:
                print str(e)
        else:
            pass

    os.remove('raw_%02d.jpg' % page)


def genImages(inPdf, ENLR_THRESH=600, MC_EXT=150):

    subprocess.call(['pdftk', inPdf, 'burst', 'output', 'output_%02d.pdf'])
    subprocess.call(['pdftoppm', inPdf, 'output'])
    numPages = len(glob.glob1('.', "output_*.pdf"))

    for i in range(1, numPages + 1):
        subprocess.call("bash multicrop -u 3 " + ("output-%d.ppm " % i)
                        + ("multicrop-output/tmp_raw_mc_%02d.ppm " % i),
                        shell=True)
        subprocess.call("bash multicrop " + ("-e %d -u 3 " % MC_EXT) + (
            "output-%d.ppm " % i) +
            ("multicrop-ext-output/tmp_raw_mc_%02d.ppm " % i), shell=True)

        mc_imgs = glob.glob1(
            'multicrop-ext-output/', "tmp_raw_mc_%02d*.ppm" % i)

        fin_files = []

        for currImg in mc_imgs:
            img = cv2.imread('multicrop-ext-output/' + currImg)
            if isGarbageImage(img):
                # print "is garbage! " + currImg
                try:
                    os.remove('multicrop-ext-output/' + currImg)
                    os.remove('multicrop-output/' + currImg)
                except Exception, e:
                    print str(e)
            else:
                fin_files.append(currImg)

        flag = False
        for croppedImg in fin_files:
            img = cv2.imread('multicrop-output/' + croppedImg)
            height, width = img.shape[:2]
            if max(height, width) <= ENLR_THRESH:
                try:
                    os.remove('multicrop-output/' + croppedImg)
                    os.remove('multicrop-ext-output/' + croppedImg)
                    flag = True
                except Exception, e:
                    print str(e)

        if flag:
            makeEnlarged(i, ENLR_THRESH, MC_EXT)

    mc_imgs = glob.glob1('multicrop-output/', "*.ppm")

    for im in mc_imgs:
        img = cv2.imread('multicrop-output/' + im)
        if min(img.shape[0], img.shape[1]) < 50:
            try:
                os.remove('multicrop-output/' + im)
                os.remove('multicrop-ext-output/' + im)
                continue
            except Exception, e:
                print str(e)

        if isAxisPresent(img):
            # print "isAxisPresent____________________", im
            try:
                crp_img = cv2.imread('multicrop-output/' + im)
                ax = AxesDetection(crp_img, False)

                if ax:
                    os.remove('multicrop-ext-output/' + im)
                    shutil.move(
                        'multicrop-output/' + im, 'multicrop-ext-output/' + im)

                    # print "================================", ax
                    crp_img = crp_img[
                        ax['haxisY2']:ax['haxisY'], ax['vaxisX']:ax['vaxisX2']]
                    cv2.imwrite('multicrop-output/' + im, crp_img)

            except Exception, e:
                print str(e)

    for dump in glob.glob1('.', "output_*.pdf"):
        os.remove(dump)

    for dump in glob.glob1('.', "output-*.ppm"):
        os.remove(dump)


def histogram(center, img):

    hue = []
    histo = []
    final_list = []
    for i in range(0, len(center)):
        hue.append(getHue(center[i]))

    for i in range(0, len(center)):
        count_hue = 0
        count_sat = 0
        print img.shape
        for j in range(0, (img.shape)[0]):
            for k in range(0, (img.shape)[1]):
                if img[j, k, 0] == center[i][0] and img[j, k, 1] == \
                        center[i][1] and img[j, k, 2] == center[i][2]:
                    count_hue += 1
        histo.append(count_hue)

    hue_pushed = []
    for i in range(0, len(hue)):
        maximum = histo[i]
        max_pos = i
        for j in range(0, len(hue)):
            if hue[i] == hue[j]:
                if maximum < histo[j]:
                    max_pos = j
        if (hue[max_pos] in hue_pushed) is False:
            final_list.append(center[max_pos])
            hue_pushed.append(hue[max_pos])

    return final_list


def getHue(colorBGR):
    hue1 = None

    R1 = int(colorBGR[2])
    G1 = int(colorBGR[1])
    B1 = int(colorBGR[0])
    M1 = max(R1, B1, G1)
    m1 = min(R1, B1, G1)
    Del1 = M1 - m1

    # Hue calculation
    if Del1 == 0:
        hue1 = 0
    elif M1 == R1:
        hue1 = 60 * ((float(G1 - B1) / Del1))
    elif M1 == G1:
        hue1 = 60 * ((float(B1 - R1) / Del1) + 2)
    elif M1 == B1:
        hue1 = 60 * ((float(R1 - G1) / Del1) + 4)
    else:
        print"out of bounds"

    return hue1
