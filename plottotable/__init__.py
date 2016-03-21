"""Main module of the library."""
from __future__ import print_function, division
from glob import glob
import argparse
import os
import os.path as osp
import subprocess
import cv2
import numpy as np
import Image
from preprocessor import genImages
import guiController
from utils import mergeOutput, clean
from generateTables import getTables, printTables

legend_images_dir = "multicrop-output/"
plot_images_dir = "multicrop-ext-output/"
csv_output_dir = "csv-output/"
pdf_output_dir = "pdf-output/"

pkg_dir = osp.abspath(osp.dirname(__file__))
data_dir = osp.join(pkg_dir, 'data')


def main():
    """The function called by the CLI tool plot2table."""
    argparser = argparse.ArgumentParser(description="Convert plot to table")

    argparser.add_argument("pdf", action="store", help="pdf file",
                           default=None, nargs="*")

    args = argparser.parse_args()

    if len(args.pdf) == 0:
        open_gui()
    else:
        process_pdf(args.pdf[0])

        generate_data()


def process_pdf(pdf):
    """Process the pdf file.

    Parameters
    ----------
    pdf : string
        Name of the pdf file given as input.
    """

    if os.path.exists(legend_images_dir):
        subprocess.call(["rm", "-rf", legend_images_dir])
    os.makedirs(legend_images_dir)

    if os.path.exists(plot_images_dir):
        subprocess.call(["rm", "-rf", plot_images_dir])
    os.makedirs(plot_images_dir)

    if os.path.exists(csv_output_dir):
        subprocess.call(["rm", "-rf", csv_output_dir])
    os.makedirs(csv_output_dir)

    if os.path.exists(pdf_output_dir):
        subprocess.call(["rm", "-rf", pdf_output_dir])
    os.makedirs(pdf_output_dir)

    genImages(pdf)


def open_gui():
    """
    Start the Graphical User Interface of the library.
    """
    guiController.main()


def generate_data():
    """
    Process each plot image to generate table data
    """
    for subdir, dirs, files in os.walk(legend_images_dir):
        for _file in files:
            getTables(_file)

    file_list = []
    for subdir, dirs, files in os.walk(pdf_output_dir):
        for _file in files:
            if _file.endswith('.pdf'):
                file_list.append(_file)

    print ("Writing merged output in Output.pdf...")
    current_dir = os.getcwd()
    mergeOutput(file_list, current_dir + "/Output.pdf")

    clean()

if __name__ == "__main__":
    main()
