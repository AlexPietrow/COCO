import numpy as np
from PIL import Image as img
import astropy.io.fits as f
import matplotlib.pyplot as plt
import COCOpy as coco

data = f.open('path/to/fits/file')[0].data[0,0] #make cube 3D
data = np.swapaxes(np.swapaxes(data,0,-1), 0,1) #Make sure that it is x,y,L
wnan = np.isnan(data) #remove Nan data
data[wnan] = 0

cfilter = coco.coco_filters(data[0,0,:], 'single', [3,11,19]) #create filter
cocoimg, cocodata = coco.coco(data, cfilter, 'test.png') #create coco image
cbar = coco.cbarimg() #create colorbar
coco.coco_img(cocoimg, 'test.png', cbar) #combine image and colorbar and save







