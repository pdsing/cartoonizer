#!/usr/bin/env python
import argparse
import time
import numpy as np
from collections import defaultdict
from scipy import stats
import cv2
import glob
from os import listdir
from os.path import isfile, join
import os
# for sketchify
import matplotlib.pyplot as plt
import scipy.ndimage


# The main cartoon function running on BizNewz
def cartoonize(image):
    """
    convert image into cartoon-like image
    image: input PIL image
    """

    output = np.array(image)
    x, y, c = output.shape
    for i in range(c):
        output[:, :, i] = cv2.bilateralFilter(output[:, :, i], 5, 50, 50)
    edge = cv2.Canny(output, 100, 200)

    output = cv2.cvtColor(output, cv2.COLOR_RGB2HSV)

    hists = []
    #H
    hist, _ = np.histogram(output[:, :, 0], bins=np.arange(180+1))
    hists.append(hist)
    #S
    hist, _ = np.histogram(output[:, :, 1], bins=np.arange(256+1))
    hists.append(hist)
    #V
    hist, _ = np.histogram(output[:, :, 2], bins=np.arange(256+1))
    hists.append(hist)

    C = []
    for h in hists:
        C.append(k_histogram(h))
    print("centroids: {0}".format(C))

    output = output.reshape((-1, c))
    for i in range(c):
        channel = output[:, i]
        index = np.argmin(np.abs(channel[:, np.newaxis] - C[i]), axis=1)
        output[:, i] = C[i][index]
    output = output.reshape((x, y, c))
    output = cv2.cvtColor(output, cv2.COLOR_HSV2RGB)

    contours, _ = cv2.findContours(edge,
                                   cv2.RETR_EXTERNAL,
                                   cv2.CHAIN_APPROX_NONE)
    cv2.drawContours(output, contours, -1, 0, thickness=1)
    return output

# Helper functions for Cartoonize
def update_C(C, hist):
    """
    update centroids until they don't change
    """
    while True:
        groups = defaultdict(list)
        #assign pixel values
        for i in range(len(hist)):
            if hist[i] == 0:
                continue
            d = np.abs(C-i)
            index = np.argmin(d)
            groups[index].append(i)

        new_C = np.array(C)
        for i, indice in groups.items():
            if np.sum(hist[indice]) == 0:
                continue
            new_C[i] = int(np.sum(indice*hist[indice])/np.sum(hist[indice]))
        if np.sum(new_C-C) == 0:
            break
        C = new_C
    return C, groups


def k_histogram(hist):
    """
    choose the best K for k-means and get the centroids
    """
    alpha = 0.001              # p-value threshold for normaltest
    N = 80                      # minimun group size for normaltest
    C = np.array([128])

    while True:
        C, groups = update_C(C, hist)

        #start increase K if possible
        new_C = set()     # use set to avoid same value when seperating centroid
        for i, indice in groups.items():
            #if there are not enough values in the group, do not seperate
            if len(indice) < N:
                new_C.add(C[i])
                continue

            # judge whether we should seperate the centroid
            # by testing if the values of the group is under a
            # normal distribution
            z, pval = stats.normaltest(hist[indice])
            if pval < alpha:
                #not a normal dist, seperate
                left = 0 if i == 0 else C[i-1]
                right = len(hist)-1 if i == len(C)-1 else C[i+1]
                delta = right-left
                if delta >= 3:
                    c1 = (C[i]+left)/2
                    c2 = (C[i]+right)/2
                    new_C.add(c1)
                    new_C.add(c2)
                else:
                    # though it is not a normal dist, we have no
                    # extra space to seperate
                    new_C.add(C[i])
            else:
                # normal dist, no need to seperate
                new_C.add(C[i])
        if len(new_C) == len(C):
            break
        else:
            C = np.array(sorted(new_C))
    return C


# Helper functions for creating the basic black and white sketch
def grayscale(rgb):
    return np.dot(rgb[...,:3], [0.299, 0.587, 0.114])


def dodge(front,back):
    result=front*255/(255-back) 
    result[result>255]=255
    result[back==255]=255
    return result.astype('uint8')

# The simple sketchify
def sketchify(image):
    g=grayscale(image)
    i = 255-g
    b = scipy.ndimage.filters.gaussian_filter(i,sigma=10)
    r= dodge(b,g)
    return r



# The main function
if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-t', "--type", help="file to process single file, folder to process a full folder")
    parser.add_argument('input', help='source image/ folder that needs to be fully converted')
    parser.add_argument('output', help='destinaton image/ folder with cartoonized images')

    args = parser.parse_args()

    if args.type == "file":
        input_image = args.input
        output_image = args.output
        output_filename, output_file_extension = os.path.splitext(output_image)
        print(f"The files are {input_image} and {output_image}")
        image = cv2.imread(args.input)
        start_time = time.time()
        # Calling the main cartoonizer
        output = cartoonize(image)
        end_time = time.time()
        t = end_time-start_time
        print('time: {0}s'.format(t))
        cv2.imwrite(output_filename + "-1" + output_file_extension, output)

        # Calling the simple black and white sketchify
        r = sketchify(image)
        plt.imsave(output_filename + "-2" + output_file_extension, r, cmap='gray', vmin=0, vmax=255)

    if args.type == "folder":
        input_image_folder = args.input
        output_image_folder = args.output
        print(f"The folders are {input_image_folder} and {output_image_folder}")
        input_images = [join(input_image_folder, f) for f in listdir(input_image_folder) if isfile(join(input_image_folder, f))]
        input_images_names = [f for f in listdir(input_image_folder) if isfile(join(input_image_folder, f))]
        for (input_image, image_name) in zip(input_images, input_images_names):
            image = cv2.imread(input_image)
            start_time = time.time()
            output = cartoonize(image)
            end_time = time.time()
            t = end_time-start_time
            print('time: {0}s'.format(t))
            output_image_name = join(output_image_folder, image_name)
            cv2.imwrite(output_image_name, output)