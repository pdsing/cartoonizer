from __future__ import print_function
import cv2 as cv
import numpy as np
import argparse
import random as rng
rng.seed(12345)
def thresh_callback(val):
    threshold = val
    # Detect edges using Canny
    canny_output = cv.Canny(src_gray, threshold, threshold * 2)
    # Find contours
    contours, hierarchy = cv.findContours(canny_output, cv.RETR_TREE, cv.CHAIN_APPROX_SIMPLE)
    # Draw contours
    drawing = np.zeros((canny_output.shape[0], canny_output.shape[1], 3), dtype=np.uint8)
    for i in range(len(contours)):
        color = (rng.randint(0,256), rng.randint(0,256), rng.randint(0,256))
        cv.drawContours(drawing, contours, i, color, 2, cv.LINE_8, hierarchy, 0)
    # Show in a window
    cv.imshow('Contours', drawing)


def find_and_draw_contours(val):
    threshold = val
    # Detect edges using Canny
    canny_output = cv.Canny(src_gray, threshold, threshold * 2)
    # Find contours
    contours, hierarchy = cv.findContours(canny_output, cv.RETR_TREE, cv.CHAIN_APPROX_SIMPLE)
    # Draw contours
    drawing = np.zeros((canny_output.shape[0], canny_output.shape[1], 3), dtype=np.uint8)
    for i in range(len(contours)):
        color = (rng.randint(0,256), rng.randint(0,256), rng.randint(0,256))
        cv.drawContours(drawing, contours, i, color, 2, cv.LINE_8, hierarchy, 0)
    # Show in a window
    cv.imwrite('contour.png', drawing)

    # c = max(contours, key=cv.contourArea) #max contour
    # f = open('path.svg', 'w+')
    # f.write('<svg width="'+str(width)+'" height="'+str(height)+'" xmlns="http://www.w3.org/2000/svg">')
    # f.write('<path d="M')

    # for i in range(len(c)):
    #     #print(c[i][0])
    #     x, y = c[i][0]
    #     print(x)
    #     f.write(str(x)+  ' ' + str(y)+' ')

    # f.write('"/>')
    # f.write('</svg>')
    # f.close()

    with open("path.svg", "w+") as f:
        f.write(f'<svg width="{width}" height="{height}" xmlns="http://www.w3.org/2000/svg">')

        for c in contours:
            f.write('<path d="M')
            for i in range(len(c)):
                x, y = c[i][0]
                f.write(f"{x} {y} ")
            f.write('" style="stroke:pink"/>')
        f.write("</svg>")


# Load source image
parser = argparse.ArgumentParser(description='Code for Finding contours in your image tutorial.')
parser.add_argument('--input', help='Path to input image.', default='HappyFish.jpg')
args = parser.parse_args()
src = cv.imread(cv.samples.findFile(args.input))
if src is None:
    print('Could not open or find the image:', args.input)
    exit(0)
# Convert image to gray and blur it
height, width, channels = src.shape 
cartoon_image = cv.stylization(src, sigma_s=150, sigma_r=0.25)
cartoon_image1, cartoon_image2  = cv.pencilSketch(src, sigma_s=60, sigma_r=0.5, shade_factor=0.02)
cv.imwrite('cartoon.png', cartoon_image)
cv.imwrite('cartoon1.png', cartoon_image1)
cv.imwrite('cartoon2.png', cartoon_image2)

src_gray = cv.cvtColor(src, cv.COLOR_BGR2GRAY)
src_gray = cv.blur(src_gray, (3,3))
# Create Window
# source_window = 'Source'
# cv.namedWindow(source_window)
# cv.imshow(source_window, src)
# max_thresh = 255
# thresh = 100 # initial threshold
# cv.createTrackbar('Canny Thresh:', source_window, thresh, max_thresh, thresh_callback)
# thresh_callback(thresh)
find_and_draw_contours(100)
cv.waitKey()