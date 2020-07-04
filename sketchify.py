import numpy as np
import imageio
import scipy.ndimage
import matplotlib.pyplot as plt


def grayscale(rgb):
    return np.dot(rgb[...,:3], [0.299, 0.587, 0.114])


def dodge(front,back):
    result=front*255/(255-back) 
    result[result>255]=255
    result[back==255]=255
    return result.astype('uint8')


img ="https://pbs.twimg.com/profile_images/1151010215950553088/I6Jrybf_.png"



s = imageio.imread(img)
g=grayscale(s)
i = 255-g
b = scipy.ndimage.filters.gaussian_filter(i,sigma=10)
r= dodge(b,g)

# plt.imshow(r, cmap="gray")

plt.imsave('img42.png', r, cmap='gray', vmin=0, vmax=255)