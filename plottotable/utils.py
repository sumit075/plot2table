import numpy as np
import cv2
import os
import subprocess
from glob import glob
import matplotlib as mpl
import matplotlib.pyplot as plt
import matplotlib.cbook as cbook

legend_images_dir = "multicrop-output/"
plot_images_dir = "multicrop-ext-output/"
csv_output_dir = "csv-output/"
pdf_output_dir = "pdf-output/"


def centroid_histogram(clt):
    # grab the number of different clusters and create a histogram
    # based on the number of pixels assigned to each cluster
    numLabels = np.arange(0, len(np.unique(clt.labels_)) + 1)
    (hist, _) = np.histogram(clt.labels_, bins=numLabels)

    # normalize the histogram, such that it sums to one
    hist = hist.astype("float")
    hist /= hist.sum()

    # return the histogram
    return hist


def plot_colors(hist, centroids):
    # initialize the bar chart representing the relative frequency
    # of each of the colors
    bar = np.zeros((50, 300, 3), dtype="uint8")
    startX = 0

    # loop over the percentage of each cluster and the color of
    # each cluster
    for (percent, color) in zip(hist, centroids):
        # plot the relative percentage of each cluster
        endX = startX + (percent * 300)
        cv2.rectangle(bar, (int(startX), 0), (int(endX), 50),
                      color.astype("uint8").tolist(), -1)
        startX = endX

    # return the bar chart
    return bar


def mergeOutput(Images, out_path):

    input_str = []
    for i, image_name in enumerate(Images):
        input_str.append(
            pdf_output_dir + os.path.splitext(image_name)[0] + ".pdf")

    if not len(input_str) == 0:
        subprocess.call(['pdftk'] + input_str + ['cat', 'output', out_path])
    else:
        print "Please select at least one image"


def clean():
    print "Deleting temp files... "

    for dump in glob("*.html"):
        os.remove(dump)

    for dump in glob("*.jpg"):
        os.remove(dump)

    for dump in glob("*.tiff"):
        os.remove(dump)

    for dump in glob("*.txt"):
        os.remove(dump)

    if os.path.exists(legend_images_dir):
        subprocess.call(["rm", "-rf", legend_images_dir])
    if os.path.exists(plot_images_dir):
        subprocess.call(["rm", "-rf", plot_images_dir])
    if os.path.exists(csv_output_dir):
        subprocess.call(["rm", "-rf", csv_output_dir])
    if os.path.exists(pdf_output_dir):
        subprocess.call(["rm", "-rf", pdf_output_dir])


def plotCSV(img_name):
    base_name = os.path.splitext(img_name)[0]
    data = np.genfromtxt(csv_output_dir + base_name + ".csv",
                         delimiter=',', skip_header=2, names=True,
                         missing_values='-')

    names = data.dtype.names
    vals = [data[names[i]] for i in range(0, len(names))]

    # print names
    fin = []
    count = 1
    for n in names:
        temp = unicode(n, errors='ignore').replace('_', ' ').strip()
        if len(temp) > 0:
            fin.append(temp)
        else:
            fin.append('Label %d' % count)
        count += 1

    # print fin

    for i in range(1, len(fin)):
        plt.plot(vals[0], vals[i], label=fin[i])

    y_label = 'Y Label'
    title = "Title"

    with open(csv_output_dir + base_name + ".csv", 'r') as f:
        title = f.readline().replace(',', '')
        y_label = f.readline().replace(',', '')

    title = unicode(title, errors='ignore')
    y_label = unicode(y_label, errors='ignore')
    plt.title(title)
    plt.xlabel(fin[0])
    plt.ylabel(y_label)
    plt.legend()
    plt.show()
