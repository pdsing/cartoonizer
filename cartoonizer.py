#!/usr/bin/env python
import argparse
import time
import numpy as np
from collections import defaultdict
import scipy.stats as stats
from PIL import Image


def cartoonize(image):
    """
    convert image into cartoon-like image

    image: input PIL image
    """
    hist = image.histogram()
    hists = []
    hists.append(np.array(hist[0:256]))
    hists.append(np.array(hist[256:256*2]))
    hists.append(np.array(hist[256*2:]))

    C = []
    for h in hists:
        C.append(k_histogram(h))
    print(C)
    output = np.array(image, dtype=np.int)
    x, y, c = output.shape

    output = output.reshape((-1, c))
    for k in xrange(c):
        channel = output[:, k]
        index = np.argmin(np.abs(channel[:, np.newaxis] - C[k]), axis=1)
        output[:, k] = C[k][index]
    output = output.reshape((x, y, c))
    cartoonized = Image.fromarray(output.astype(np.int8), mode='RGB')
    return cartoonized


def update_C(C, hist):
    """
    update centroids until they don't change
    """
    while True:
        groups = defaultdict(list)
        #assign pixel values
        for i in range(len(hist)):
            d = np.abs(C-i)
            index = np.argmin(d)
            groups[index].append(i)

        new_C = np.array(C)
        for i, indice in groups.items():
            new_C[i] = int(np.sum(indice*hist[indice])/np.sum(hist[indice]))
        if np.sum(new_C-C) == 0:
            break
        C = new_C
    return C, groups


def k_histogram(hist):
    """
    choose the best K for k-means and get the centroids
    """
    alpha = 0.0001              # p-value threshold for normaltest
    N = 80                     # minimun group size for normaltest
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
                right = 255 if i == len(C)-1 else C[i+1]
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

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('input', help='input image')
    parser.add_argument('output', help='output cartoonized image')

    args = parser.parse_args()

    image = Image.open(args.input)
    start_time = time.time()
    output = cartoonize(image)
    end_time = time.time()
    t = end_time-start_time
    print('time: {0}s'.format(t))
    output.save(args.output)