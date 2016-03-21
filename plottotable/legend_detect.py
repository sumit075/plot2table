import cv2
import numpy as np
import subprocess
from color_kmeans import colorCluster
import lxml.html as lh
import re
import os
from preprocessor import (otsusBinarization, resizeImage, sharpenImage,
                          cluster, enhance, morphological)


def getOCRLines(input_):
    """
    Parse ocr_line from the hocr file and
    return a list of ocr_lines, each containing 1/more ocr_words
    """

    tree = lh.parse(input_)

    print "Parsing the OCR files... ",
    # xpath for ocr line
    blurb = tree.xpath("//span[@class='ocr_line']")

    blocks = []

    for ocrline in blurb:
        # ocrx_word within the current line
        elems = ocrline.xpath("./span[@class='ocrx_word']")
        outl = []
        for ocrword in elems:
            content = ocrword.text_content().encode('utf8')

            if len(content.strip()) > 0:
                # extract the bounding boxes
                s = ocrword.attrib['title'].split(';', 2)[0]
                y = ','.join(s.split(' ')[1:])
                outl.append(content.replace(',', '.') + ',' + y)

        if len(outl) > 0:
            blocks.append(outl)

    # DEBUGGING
    # print blocks
    # print "<########################################################>"
    print "Done!"
    return blocks

"""
Parse ocr_par from the hocr file and
return a list of top left and bottom right
coordinates of all legends bounding box
"""


def getLegendsBox(html_path):

    tree = lh.parse(html_path)
    # xpath for ocr par
    paras = tree.xpath("//p[@class='ocr_par']")

    str_box = []
    for par in paras:
        if not par.text_content().strip().replace("\n", "").replace(" ", "") \
                == "":
            str_box.append(par.xpath("./@title"))

    # print str_box
    box = None
    for i, par in enumerate(str_box):
        tmp = par[0].split(" ")[1:]
        para_box = []
        for p in tmp:
            para_box.append(int(p))

        if i == 0:
            box = para_box
        else:
            if para_box[0] < box[0]:
                box[0] = para_box[0]
            if para_box[1] < box[1]:
                box[1] = para_box[1]
            if para_box[2] > box[2]:
                box[2] = para_box[2]
            if para_box[3] > box[3]:
                box[3] = para_box[3]

    return box


"""
Utility function to check if a string is a word
def word: alphanumeric permutation
"""


def isWord(word):
    # regex for a word ie 1 or more alphanumeric characters
    pattern = re.compile("[a-zA-Z0-9]+")
    if pattern.search(word) is not None:
        return True
    else:
        return False


"""
Function to determine the orientation of legend box
Left :: [ color code | text ]
Right :: [ text | color code]
Param - blocks returned by getOCRLines()
"""


def getLegendOrientation(blocks):
    # counts to keep track of majority
    left_c = 0
    right_c = 0
    print "Trying to extract orientation... ",
    for line in blocks:
        # try to determine only if multi-worded line
        if len(line) > 1:
            i = 0
            # split the ocrword
            val = line[i].split(',')
            # first ocrword in line is word
            if isWord(val[0]):
                i = 1
                val = line[i].split(',')
                # keep going till non-word is found
                while(isWord(val[0]) and i < len(line)):
                    val = line[i].split(',')
                    i += 1

                # count as right if within bounds
                if i < len(line):
                    right_c += 1

                # else:
                # DEBUGGING -TODO section
                #   print "All are words."

            else:
                i = 1
                val = line[i].split(',')
                # keep going till word is found
                while((not isWord(val[0])) and i < len(line)):
                    val = line[i].split(',')
                    i += 1

                if i < len(line):
                    left_c += 1

                # else:
                # DEBUGGING -TODO section
                #   print "All are non-words."

    # decide by majority
    print "Done!"
    if right_c > left_c:
        return 0
    elif left_c > right_c:
        return 1
    else:
        # incase of tie
        return None


"""
Function to parse the boundaries
of the legends detected,
returns the legend text and its boundary
"""


def parseBlock(block):

    outstr = ''
    left_bbox = ''
    right_bbox = ''

    for ocr_word in block:
        val = ocr_word.split(',')
        if isWord(val[0]):
            if outstr == '':
                outstr = val[0]
                left_bbox = val[1] + ',' + val[2]
                right_bbox = val[3] + ',' + val[4]
            else:
                outstr = outstr + ' ' + val[0]
                right_bbox = val[3] + ',' + val[4]

    outstr = '"' + outstr + '"' + ',' + left_bbox + ',' + right_bbox

    return outstr


"""
Function which maps colors and legends.
Param - Input plot (axes cropped out)
Return - dict of list(text to color) and orientation
"""


def fetchLegendColors(imgFile):
    img = cv2.imread(imgFile)

    #
    # pre-process stuff
    print "Preprocessing for OCR... ",
    img_rs = resizeImage(img)
    img1 = sharpenImage(img)
    img2 = cluster(img1)[0]
    out = otsusBinarization(img2)
    out1 = enhance(out)
    # out2 = morphological(out1)
    cv2.imwrite("temp_image.tiff", out1)
    print "Done!"
    #

    # using binarisation for better ocr

    # binarised = otsusBinarization(img)
    # cv2.imwrite('temp_image.ppm', binarised)

    # subprocess.call("tesseract %s outtess hocr -l eng" % imgFile, shell=True)
    print "Running OCR... ",
    subprocess.call(
        "tesseract temp_image.tiff outtess hocr -l eng", shell=True)
    subprocess.call("mv outtess.hocr outtess.html", shell=True)
    print "Done!"

    os.remove('temp_image.tiff')
    # cv2.imshow("win",sharpenImage(img))
    # cv2.waitKey(0)

    height, width, depth = img.shape

    blocks = getOCRLines('outtess.html')

    orient = getLegendOrientation(blocks)

    # DEBUGGING
    # if orient is not None:
    #   print " ==============> Orientation is %d <===============" %  orient
    # else:
    #   print " ==============> Orientation is None <==============="

    output_map = []

    print "Extracting colors... ",
    for block in blocks:
        # handle single words separately
        if len(block) == 1:
            # DEBUGGING
            # print "-------------------START----------------------"
            # print block
            # print "-------------------END----------------------"
            if orient is None:
                # consider both sides of word if orient is None
                try:
                    box = block[0]
                    val = box.split(',')
                    x1, y1, x2, y2 = int(val[1]), int(
                        val[2]), int(val[3]), int(val[4])
                    crop_img = img[y1:y2, x1 - 100:x2 + 100]

                    # crop_img = cluster(sharpenImage(crop_img), 3)
                    leg_color = colorCluster(crop_img, 3, 20)

                    output_map.append([parseBlock(block), leg_color])
                    # if leg_color is not None:
                    #   print leg_color
                    # else:
                    #   print "None found - 0"
                except Exception, e:
                    print str(e)

            # Use the identified orient if available
            elif orient == 1:
                try:
                    box = block[0]
                    val = box.split(',')

                    x1, y1, x2, y2 = int(val[1]), int(
                        val[2]), int(val[3]), int(val[4])
                    crop_img = img[y1:y2, x1 - 100:x1]

                    # crop_img = cluster(sharpenImage(crop_img), 3)
                    leg_color = colorCluster(crop_img, 3, 20)
                    output_map.append([parseBlock(block), leg_color])
                    # if leg_color is not None:
                    #   print leg_color
                    # else:
                    #   print "None found - 1"
                except Exception, e:
                    print str(e)

            else:
                try:
                    box = block[0]
                    val = box.split(',')
                    x1, y1, x2, y2 = int(val[1]), int(
                        val[2]), int(val[3]), int(val[4])
                    crop_img = img[y1:y2, x2:x2 + 100]

                    # crop_img = cluster(sharpenImage(crop_img), 3)
                    leg_color = colorCluster(crop_img, 3, 20)
                    output_map.append([parseBlock(block), leg_color])
                    # if leg_color is not None:
                    #   print leg_color
                    # else:
                    #   print "None found - 2"
                except Exception, e:
                    print str(e)

        # for multi-worded ocrline
        else:
            i = 0
            box = block[i]
            # DEBUGGING
            # print "-------------------START----------------------"
            # print block
            # print "-------------------END----------------------"
            val = box.split(',')
            if isWord(val[0]):
                # try to identify the boundary of word and color code
                # i = 1
                nisW_flag = False
                for i in range(1, len(block)):
                    box = block[i]
                    val = box.split(',')
                    if not isWord(val[0]):
                        print "not word ", i
                        nisW_flag = True
                        i -= 1
                        break

                # while(isWord(val[0]) and i<len(block)):
                #   print "sdfsdf------",val[0],isWord(val[0])
                #   box = block[i]
                #   val = box.split(',')
                #   i+=1
                #   print i

                # if i<len(block):
                if nisW_flag:
                    # use orientation if identified
                    if orient == 1:
                        try:
                            val = block[0].split(',')
                            x1, y1, x2, y2 = int(val[1]), int(
                                val[2]), int(val[3]), int(val[4])

                            crop_img = img[y1:y2, x2 - 100:x2]

                            # crop_img = cluster(sharpenImage(crop_img), 3)
                            leg_color = colorCluster(crop_img, 3, 20)

                            output_map.append([parseBlock(block), leg_color])
                            # if leg_color is not None:
                            #   print leg_color
                            # else:
                            #   print "None found 3"
                        except Exception, e:
                            print str(e)

                    # use the individual orient if None
                    else:
                        try:
                            val = block[i].split(',')
                            x1, y1, x2, y2 = int(val[1]), int(
                                val[2]), int(val[3]), int(val[4])

                            crop_img = img[y1:y2, x2:x2 + 100]

                            # crop_img = cluster(sharpenImage(crop_img), 3)
                            leg_color = colorCluster(crop_img, 3, 20)

                            output_map.append([parseBlock(block), leg_color])
                            # if leg_color is not None:
                            #   print leg_color
                            # else:
                            #   print "None found 4"
                        except Exception, e:
                            print str(e)

                # when all ocrwords are words
                else:
                    # print "All are words.!"
                    try:
                        w_f = block[0].split(',')
                        w_l = block[-1].split(',')

                        # consider the first words and its left

                        y1, y2 = sorted(
                            [int(w_f[2]), int(w_f[4]), int(w_l[2]),
                             int(w_l[4])])[1:3]

                        x1, x2 = int(w_f[1]), int(w_f[3])
                        crop_img1 = img[y1:y2, x2 - 100:x2]

                        # and the last word and its right
                        x1, x2 = int(w_l[1]),  int(w_l[3])
                        crop_img2 = img[y1:y2, x1:x1 + 100]

                        # concatenate and test for color
                        final_crop = np.concatenate(
                            (crop_img1, crop_img2), axis=1)

                        # final_crop = cluster(sharpenImage(final_crop), 3)
                        leg_color = colorCluster(final_crop, 3, 20)

                        output_map.append([parseBlock(block), leg_color])
                        # if leg_color is not None:
                        #   print leg_color
                        # else:
                        #   print "None found 5"
                    except Exception, e:
                        print str(e)

            else:
                # try to find boundary
                isW_flag = False
                for i in range(1, len(block)):
                    box = block[i]
                    val = box.split(',')
                    if isWord(val[0]):
                        isW_flag = True
                        # i -= 1
                        break

                # i = 1
                # box = block[i]
                # val = box.split(',')
                # while((not isWord(val[0])) and i<len(block)):
                #   box = block[i]
                #   val = box.split(',')
                #   i+=1

                # if i<len(block):
                if isW_flag:
                    # use orientation if available
                    # else go with the current orientation
                    if orient == 0:
                        try:
                            val = block[-1].split(',')
                            x1, y1, x2, y2 = int(val[1]), int(
                                val[2]), int(val[3]), int(val[4])
                            crop_img = img[y1:y2, x1:x1 + 100]

                            # crop_img = cluster(sharpenImage(crop_img), 3)
                            leg_color = colorCluster(crop_img, 3, 20)
                            output_map.append([parseBlock(block), leg_color])
                            # if leg_color is not None:
                            #   print leg_color
                            # else:
                            #   print "None found - 6"
                        except Exception, e:
                            print str(e)

                    else:
                        try:
                            val = block[i].split(',')
                            x1, y1, x2, y2 = int(val[1]), int(
                                val[2]), int(val[3]), int(val[4])

                            crop_img = img[y1:y2, x1 - 100:x1]

                            # crop_img = cluster(sharpenImage(crop_img), 3)
                            leg_color = colorCluster(crop_img, 3, 20)
                            output_map.append([parseBlock(block), leg_color])
                            # if leg_color is not None:
                            #   print leg_color
                            # else:
                            #   print "None found - 7"
                        except Exception, e:
                            print str(e)

                else:
                    # if all are non-words, consider the current
                    # ocrline for color clustering
                    try:
                        # print "All are non-words."
                        w_f = block[0].split(',')
                        w_l = block[-1].split(',')

                        x1, y1, x2, y2 = int(w_f[1]), int(
                            w_f[2]), int(w_f[3]), int(w_f[4])

                        a1, b1, a2, b2 = int(w_l[1]), int(
                            w_l[2]), int(w_l[3]), int(w_l[4])

                        # using the maximum y window
                        fy1 = min(y1, y2, b1, b2)
                        fy2 = max(y1, y2, b1, b2)

                        # go from the first word to the last word
                        crop_img2 = img[fy1:fy2, x1:a2]

                        # crop_img = cluster(sharpenImage(crop_img), 3)
                        leg_color = colorCluster(crop_img, 3, 20)
                        output_map.append([parseBlock(block), leg_color])

                        # if leg_color is not None:
                        #   print leg_color
                        # else:
                        #   print "None found - 8"
                    except Exception, e:
                        print str(e)

    print "Done!"

    filtered_ = []
    for l in output_map:
        word = l[0].split(',')[0]
        # print word
        if len(word.strip('"')) > 1:
            filtered_.append(l)

    final_map = {'legend': filtered_, 'orient': orient}
    print "Finished fetchLegendColors!"
    return final_map


# print fetchLegendColors('input.ppm')


def legendLabelCoordinates(img, points):
    img = cv2.imread(img)

    shape = img.shape
    rows = shape[0]
    cols = shape[1]

    x1 = points[0][0]
    if x1 > cols:
        x1 = cols
    elif x1 < 0:
        x1 = 0

    y1 = points[0][1]
    if y1 > rows:
        y1 = rows
    elif y1 < 0:
        y1 = 0

    x2 = points[1][0]
    if x2 > cols:
        x2 = cols
    elif x2 < 0:
        x2 = 0

    y2 = points[1][1]
    if y2 > rows:
        y2 = rows
    elif y2 < 0:
        y2 = 0

    legend = img[y1:y2, x1:x2]

    height = y2 - y1
    width = x2 - x1

    legend = cv2.cvtColor(legend, cv2.COLOR_BGR2GRAY)
    ret, legend = cv2.threshold(legend, 127, 255, cv2.THRESH_BINARY)

    y = []

    begin_check = 0
    for i in range(0, height - 1):

        sumr = 0

        for j in range(0, width - 1):
            sumr += legend[i][j]

        percent = (float(sumr) / (255 * width)) * 100

        if begin_check == 0 and percent < 96:
            ya = y1 + i
            begin_check = 1

        if begin_check == 1 and percent > 96:
            yb = y1 + i
            begin_check = 0
            if abs(yb - ya) > 8:  # neglecting small strips of black and noise
                y.append([ya - 1, yb + 1])

    if begin_check == 1:
        yb = y1 + i
        begin_check = 0
        if abs(yb - ya) > 8:  # neglecting small strips of black and noise
            y.append([ya - 1, yb + 1])

    return y
