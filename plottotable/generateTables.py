import os
import sys
import cv2
import csv
import math
import subprocess
import numpy as np

from legend_detect import (fetchLegendColors, getLegendsBox,
                           legendLabelCoordinates)
from calibrator import getLabelData
from axisDetector import AxesDetection
from color_kmeans import colorCluster
from preprocessor import (sharpenImage, cluster, resizeImage,
                          otsusBinarization, enhance, histogram, getHue)
from titleExtractor import getTitle

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4, inch, landscape
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph
from reportlab.platypus.flowables import Flowable, Image
from reportlab.lib.styles import getSampleStyleSheet

ZERO = 0
ERROR_CODE = -1

legend_images_dir = "multicrop-output/"
plot_images_dir = "multicrop-ext-output/"
csv_output_dir = "csv-output/"
pdf_output_dir = "pdf-output/"


def colorDistance(pixelBGR, legendRGB):
    '''
    Calculate Color Distance between two pixels
    '''
    rmean = ((int(pixelBGR[2]) + int(legendRGB[0])) / 2)
    r = int(pixelBGR[2]) - int(legendRGB[0])
    g = int(pixelBGR[1]) - int(legendRGB[1])
    b = int(pixelBGR[0]) - int(legendRGB[2])

    return math.sqrt((((512 + rmean) * r * r) >> 8) + 4 * g * g +
                     (((767 - rmean) * b * b) >> 8))


def estimateMissingData(Plot_data, legends):
    '''
    Estimate values which could not be calculated,
    If possible otherwise use default value '-'
    '''

    if Plot_data is None or legends is None:
        print("Either Generate Plot data or Legends is None exiting "
              "estimateMissingData()...")
        return

    for legend in legends:
        last_val_found = {}
        last_val_found["val"] = None
        last_val_found["index"] = None

        for index, val in enumerate(Plot_data[legend["name"]]):
            if not val == "-":
                last_val_found["val"] = val
                last_val_found["index"] = index
            else:
                if not last_val_found["val"] is None:
                    next_value = None
                    next_index = None
                    for next_ind, next_val in \
                            enumerate(Plot_data[legend["name"]][index + 1:]):
                        if not next_val == "-":
                            next_value = next_val
                            next_index = next_ind + index + 1
                            break

                    if not next_value is None:
                        prev_value = last_val_found["val"]
                        prev_index = last_val_found["index"]
                        prev_ratio = index - prev_index
                        next_ratio = next_index - index
                        Plot_data[legend["name"]][index] = float(
                            next_ratio * prev_value + prev_ratio *
                            next_value) / (prev_ratio + next_ratio)

                        last_val_found["val"] = Plot_data[
                            legend["name"]][index]
                        last_val_found["index"] = index
                    else:
                        Plot_data[legend["name"]][index] = "-"
                else:
                    Plot_data[legend["name"]][index] = "-"


def getTables(file_name):
    '''
    Generate Plot Data for an Image and
    Save data as .csv file
    '''
    print("Generating table for " + file_name)

    legend_path = legend_images_dir + file_name
    plot_path = plot_images_dir + file_name
    csv_path = csv_output_dir + file_name.replace(".ppm", "") + ".csv"
    data = []

    try:
        original_img = cv2.imread(legend_path)
    except Exception, e:
        print(str(e))
        print("Image" + file_name + "not found in multicrop-output, "
              "exiting getTables()...")
        return ERROR_CODE

    img_height = original_img.shape[0]
    img_width = original_img.shape[1]
    img = sharpenImage(original_img)
    img, cluster_centers = cluster(img)

    # Get legends
    try:
        tmp_data = fetchLegendColors(legend_path)
    except Exception, e:
        print(str(e))
        print("Legends Not found, creating default...")
        tmp_data = {"legend": [], "orient": None}

    raw_legends = tmp_data["legend"]
    legend_orientation = tmp_data["orient"]

    legends = []

    if len(raw_legends) == 0:
        print("Legends not found, creating using histogram...")

        new_clust = []
        for clt in cluster_centers:
            # Using luma values to find white and black
            luma = 0.2126 * clt[2] + 0.7152 * clt[1] + 0.0722 * clt[0]

            # If color is not black or white
            if luma <= 240 and luma >= 20:
                # Check for Gray color using variance
                Gray_flag = False
                pix_color_variance = np.var(clt)
                if pix_color_variance < 1000:
                    Gray_flag = True

                # If pixel color is not Gray and pixel is not in legend
                # bounded area
                if (not Gray_flag):
                    new_clust.append(clt)

        try:
            legend_hist_clr = histogram(new_clust, img)
        except Exception, e:
            print(str(e))
            print("Could not create Legends, exiting getTables()...")
            return ERROR_CODE

        if len(legend_hist_clr) == 0:
            print("Could not create Legends, exiting getTables()...")
            return ERROR_CODE

        for i, color in enumerate(legend_hist_clr):
            legend_obj = {}
            legend_obj["name"] = "Legend " + str(i + 1)
            legend_obj["top_left_x"] = None
            legend_obj["top_left_y"] = None
            legend_obj["bottom_right_x"] = None
            legend_obj["bottom_right_y"] = None
            legend_obj["color"] = [color[2], color[1], color[0]]
            legend_obj["y_pixel_set"] = []
            legend_obj["min_pixel_dist"] = colorDistance(
                [255, 255, 255], [0, 0, 0])
            legends.append(legend_obj)

    else:
        # Parsing legends
        for legend in raw_legends:
            if not legend[1] is None:
                legend_obj = {}
                tmp_info = legend[0].split(',')
                legend_obj["name"] = tmp_info[0]
                legend_obj["top_left_x"] = int(tmp_info[1])
                legend_obj["top_left_y"] = int(tmp_info[2])
                legend_obj["bottom_right_x"] = int(tmp_info[3])
                legend_obj["bottom_right_y"] = int(tmp_info[4])
                legend_obj["color"] = legend[1]
                legend_obj["y_pixel_set"] = []
                legend_obj["min_pixel_dist"] = colorDistance(
                    [255, 255, 255], [0, 0, 0])

                # Using luma values to find white and black
                luma = 0.2126 * legend_obj["color"][0] + 0.7152 * legend_obj[
                    "color"][1] + 0.0722 * legend_obj["color"][2]

                if luma <= 240 and luma >= 20:
                    # Check for Gray color using variance
                    Gray_flag = False
                    pix_color_variance = np.var(legend_obj["color"])
                    if pix_color_variance < 1000:
                        Gray_flag = True

                    # If pixel color is not Gray and pixel is not in legend
                    # bounded area
                    if (not Gray_flag):
                        legends.append(legend_obj)

        if len(legends) == 0:
            print("All legends are garbage, exiting getTables()...")
            return ERROR_CODE

    # Extract title
    try:
        plot_title = getTitle(plot_path)
    except Exception, e:
        print(str(e))
        print("Title not found")
        plot_title = None

    try:
        ext_img = cv2.imread(plot_path)
    except Exception, e:
        print(str(e))
        print("Image" + file_name + "not found in multicrop-ext-output, "
              "exiting getTables()...")
        return ERROR_CODE

    try:
        axis_box = AxesDetection(ext_img)
    except Exception, e:
        print(str(e))
        print("Error in Axis detection, exiting getTables()...")
        return ERROR_CODE

    if axis_box is None:
        print("Axis not found in Image, exiting getTables()...")
        return ERROR_CODE

    LEFT_EXTENDED_PIXELS = axis_box["vaxisX"]
    BOTTOM_EXTENDED_PIXELS = img_height - axis_box["haxisY"]
    TOP_EXTENDED_PIXELS = axis_box["haxisY2"]

    # Get X, Y values and Labels
    try:
        statrtingPoint, xMAx, xUnit, xGrad, yRef, yGrad, xLabel, \
            yLabel = getLabelData(plot_path)
    except Exception, e:
        print(str(e))
        print("Error in fonding x and y axis data, assigning default...")
        yGrad = False

    # If no data found on x and y axis
    if yGrad is False:
        print("No data found on x and y axis, creating data...")
        yRef = [img_height, TOP_EXTENDED_PIXELS]
        yGrad = 1
        yLabel = "y-label"
        statrtingPoint = [ZERO, ZERO]
        xMAx = img_width
        xUnit = float(img_width) / 10
        xGrad = 1
        xLabel = "x-label"
    # If no data found on x and y axis
    if xGrad is False and (not yGrad is False):
        print("No data found on x axis, creating data...")
        statrtingPoint = [ZERO, ZERO]
        xMAx = img_width
        xUnit = float(img_width) / 10
        xGrad = 1
        xLabel = "x-label"

    # If title not found
    if plot_title == "" or plot_title is None:
        plot_title = xLabel + " vs. " + yLabel

    try:
        f = open(csv_path, "w")
        writer = csv.writer(f)
    except Exception, e:
        print(str(e))
        print("Error in opening csv file to write,exiting getTables()...")
        return ERROR_CODE

    # Writing headers
    try:
        writer.writerow(tuple([plot_title.replace("\n", "")]))
    except:
        try:
            writer.writerow(
                tuple([xLabel.replace("\n", "") + " vs. " +
                      yLabel.replace("\n", "")]))
        except:
            writer.writerow(tuple(["x-Label vs. y-Label"]))
    try:
        writer.writerow(tuple(["", yLabel.replace("\n", "")]))
    except:
        writer.writerow(tuple(["", "y-Label"]))
    try:
        tmp = [xLabel.replace("\n", "")]
    except:
        tmp = ["x-Label"]

    for legend in legends:
        try:
            tmp.append(legend["name"].decode('utf-8').encode(
                'utf-8').replace("\"", "").replace("#", "").replace("\n", ""))
        except:
            tmp.append("Legend " + str(len(tmp)))

    writer.writerow(tuple(tmp))

    # Data structure to store all values for legends
    Plot_data = {}
    Plot_data["x"] = []
    for legend in legends:
        Plot_data[legend["name"]] = []

    try:
        out = otsusBinarization(img)
        out1 = enhance(out)
        cv2.imwrite("temp_image.tiff", out1)

        # Run tesseract to find Legend bounding box coordinates
        subprocess.call("tesseract temp_image.tiff outtess hocr", shell=True)
        subprocess.call("mv outtess.hocr tmp_outtess.html", shell=True)
    except Exception, e:
        print(str(e))
        print("Error in tesseract while reading legends to find legends "
              "bounding box")

    if not legends[0]["top_left_x"] is None:
        # Get Legend bounding box coordinates
        legend_bounding_box = getLegendsBox("tmp_outtess.html")
        subprocess.call("rm tmp_outtess.html", shell=True)

        if legend_bounding_box is None:
            print("Legend bounding box not found, creating same as first "
                  "legend's box...")
            lbb_tl_x = legends[0]["top_left_x"]
            lbb_tl_y = legends[0]["top_left_y"]
            lbb_br_x = legends[0]["bottom_right_x"]
            lbb_br_y = legends[0]["bottom_right_y"]
        else:
            lbb_tl_x = legend_bounding_box[0]
            lbb_tl_y = legend_bounding_box[1]
            lbb_br_x = legend_bounding_box[2]
            lbb_br_y = legend_bounding_box[3]

        # Change Legend bounding box coordinates according to orientation
        for legend in legends:
            if legend_orientation == 1:
                if lbb_tl_x > legend["top_left_x"] - 100:
                    lbb_tl_x = legend["top_left_x"] - 100
            elif legend_orientation == 0:
                if lbb_br_x < legend["top_left_x"] + 100:
                    lbb_br_x = legend["bottom_right_x"] + 100
            else:
                lbb_tl_x = legend["top_left_x"] - 100
                lbb_br_x = legend["bottom_right_x"] + 100

        # Get Legends y-range for checking y values in white gaps between
        # legends
        legend_y_coordinates = legendLabelCoordinates(
            legend_path, [[lbb_tl_x, lbb_tl_y], [lbb_br_x, lbb_br_y]])
        # print lbb_tl_x, lbb_tl_y, lbb_br_x, lbb_br_y
        # print legend_y_coordinates

        if legend_y_coordinates is None:
            print("Legends y-range is not found, creating same as legend "
                  "bounding box...")
            legend_bounding_box = [lbb_tl_y, lbb_br_y]
        elif len(legend_y_coordinates) == 0:
            print("Legends y-range is not found, creating same as legend "
                  "bounding box...")
            legend_bounding_box = [lbb_tl_y, lbb_br_y]

    xMin = statrtingPoint[0]
    startingPointX = ZERO
    yRefPoint = yRef[0]
    yRefPixel = yRef[1] - \
        TOP_EXTENDED_PIXELS  # Taking y ref point for non-extended image

    xCurrent = xMin
    xCurrentPixel = ZERO
    itr = 1

    # Start iterating on one-tenth of a unit x pixel point
    while xCurrentPixel < img_width:
        for legend in legends:
            legend["y_pixel_set"] = []

        # Iterate on y pixels
        yCurrentPixel = ZERO
        while yCurrentPixel < img_height:

            pixel_color = original_img[yCurrentPixel][xCurrentPixel]

            min_dist = colorDistance([255, 255, 255], [0, 0, 0])

            min_legend_index = 0
            for l, legend in enumerate(legends):
                dist = colorDistance(pixel_color, legend["color"])

                if dist is None:
                    print("Color Distance is not found, pixel colors are "
                          "None, skipping legend " + legend["name"] + "...")
                    continue

                if dist < min_dist:
                    min_dist = dist
                    min_legend_index = l

            # Flag = True indicates this pixel is not in legend bounded area
            # hence will be added to any of the set otherwise not
            Flag = True

            if not legends[0]["top_left_x"] is None:
                # Removing background color pixel and black pixels if legend
                # color is not black
                if (xCurrentPixel >= lbb_tl_x and xCurrentPixel <= lbb_br_x):
                    for yCoord in legend_y_coordinates:
                        y_min = yCoord[0]
                        y_max = yCoord[1]
                        if (yCurrentPixel >= y_min and yCurrentPixel <= y_max):
                            # Don't add this pixel to any of the legend
                            # y_pixel_set because it is in legend bounded area
                            Flag = False

            # Using luma values to find white and black
            luma = 0.2126 * \
                pixel_color[2] + 0.7152 * pixel_color[
                    1] + 0.0722 * pixel_color[0]

            # If pixel is not black or white
            if luma <= 240 and luma >= 20:
                # Check for Gray color using variance
                Gray_flag = False
                pix_color_variance = np.var(pixel_color)
                if pix_color_variance < 1000:
                    Gray_flag = True

                # If pixel color is not Gray and pixel is not in legend bounded
                # area
                if (not Gray_flag) and Flag:
                    if len(legends[min_legend_index]["y_pixel_set"]) == 0:
                        legend_c = legends[min_legend_index]["color"]
                        dist = colorDistance(pixel_color, legend_c)

                        try:
                            hue1 = getHue(pixel_color)
                            hue2 = getHue(
                                [legend_c[2], legend_c[1], legend_c[0]])
                        except Exception, e:
                            print(str(e))
                            print("Error in getting Hue values, assigning "
                                  "to exclude this pixel...")
                            hue1 = 0
                            hue2 = 30

                        if abs(hue2 - hue1) <= 20:
                            legends[min_legend_index][
                                "y_pixel_set"].append(yCurrentPixel)
                            legends[min_legend_index]["min_pixel_dist"] = dist
                    else:
                        dist = colorDistance(
                            pixel_color, legends[min_legend_index]["color"])
                        if dist < legends[min_legend_index]["min_pixel_dist"]:
                            legends[min_legend_index]["y_pixel_set"] = []
                            legends[min_legend_index][
                                "y_pixel_set"].append(yCurrentPixel)
                            legends[min_legend_index]["min_pixel_dist"] = dist
                        elif dist == \
                                legends[min_legend_index]["min_pixel_dist"]:
                            legends[min_legend_index][
                                "y_pixel_set"].append(yCurrentPixel)
            # Next iteration
            yCurrentPixel += 1

        # Generate Plot_data using y pixels sets
        Plot_data["x"].append(xCurrent)
        for legend in legends:
            avg_y = ZERO

            if len(legend["y_pixel_set"]) > 0:
                for yPix in legend["y_pixel_set"]:
                    y_val = yRefPoint - (yPix - yRefPixel) * yGrad
                    avg_y += y_val
                avg_y = float(avg_y) / len(legend["y_pixel_set"])
                Plot_data[legend["name"]].append(avg_y)
            else:
                Plot_data[legend["name"]].append("-")

        # Prepare for next iteration
        xCurrent += float(xUnit) / 10
        xCurrentPixel = startingPointX + \
            int(round(itr * (float(xUnit) / 10) * (float(1 / xGrad))))
        itr += 1

    # Estimating missing data after finding Plot_data
    try:
        estimateMissingData(Plot_data, legends)
    except Exception, e:
        print("Error in estimating values")

    # Write estimated Plot data in .csv file
    for row_no, x in enumerate(Plot_data["x"]):
        tmp = [round(x, 5)]
        for legend in legends:
            if Plot_data[legend["name"]][row_no] == "-":
                tmp.append(Plot_data[legend["name"]][row_no])
            else:
                tmp.append(round(Plot_data[legend["name"]][row_no], 5))
        writer.writerow(tuple(tmp))

    f.close()

    printTables(file_name)


def printTables(_file):
    '''
    Create pdf output file for each image
    '''
    style_param = [('ALIGN', (1, 1), (-2, -2), 'RIGHT'),
                   ('TEXTCOLOR', (1, 1), (-2, -2), colors.red),
                   ('VALIGN', (0, 0), (0, -1), 'TOP'),
                   ('TEXTCOLOR', (0, 0), (0, -1), colors.blue),
                   ('ALIGN', (0, -1), (-1, -1), 'CENTER'),
                   ('VALIGN', (0, -1), (-1, -1), 'MIDDLE'),
                   ('TEXTCOLOR', (0, -1), (-1, -1), colors.green),
                   ('INNERGRID', (0, 0), (-1, -1), 0.25, colors.black),
                   ('BOX', (0, 0), (-1, -1), 0.25, colors.black),
                   ]

    # Configure style and word wrap for table and title
    title_style = getSampleStyleSheet()
    title_style = title_style["Title"]
    title_style.wordWrap = 'CJK'

    table_style = getSampleStyleSheet()
    table_style = table_style["BodyText"]
    table_style.wordWrap = 'CJK'

    base_name = os.path.splitext(_file)[0]
    print("Printing output tables to" + base_name + ".pdf...")

    doc = SimpleDocTemplate(pdf_output_dir + base_name + ".pdf", pagesize=A4,
                            rightMargin=30, leftMargin=30, topMargin=30,
                            bottomMargin=18)
    elements = []

    csv_path = csv_output_dir + base_name + ".csv"

    # Constructing table and Title
    f = open(csv_path, "r")
    reader = csv.reader(f)
    title = reader.next()[0]
    second_line = reader.next()
    header = reader.next()
    data = [[Paragraph(cell, table_style) for cell in second_line]]
    data += [[Paragraph(cell, table_style) for cell in header]]
    no_of_columns = len(header)
    data += [[Paragraph(cell, table_style) for cell in row] for row in reader]
    t = Table(data)
    style = TableStyle(
        style_param + [('SPAN', (1, 0), (no_of_columns - 1, 0))])
    t.setStyle(style)

    f.close()

    # Constructing Image
    image_name = plot_images_dir + base_name
    img = cv2.imread(image_name + ".ppm")
    img = resizeImage(img, 523)
    cv2.imwrite(pdf_output_dir + base_name + ".jpeg", img)

    # Adding elements to pdf _file
    elements.append(Image(open(pdf_output_dir + base_name + ".jpeg", "rb")))
    elements.append(Paragraph(title, title_style))
    elements.append(t)

    doc.build(elements)
