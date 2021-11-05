import numpy as np
from PIL import Image as img
import astropy.io.fits as f
import matplotlib.pyplot as plt
import COCOpy as coco
import os
import pyana

#data = f.open('../CLV_project/nb_3950_2017-10-18T10.15.18_scans=0-24_corrected_im.fits')[0].data[:,0,21] #make cube 3D
#data = f.open('../CLV_project/nb_3950_2017-10-18T09.35.45_scans=0-5_corrected_im.fits')[0].data[0,0]
#data = f.open('../deeppolarimetry/reduced_carlos.fits')[0].data[:,0,2]
#data = f.open('ADP.2019-04-16T18_37_00.929.fits')[1].data
data = f.open('J_crispex.stokes.6302.08.12.10.time_corrected.fits')[0].data[44,4,16]

data = np.swapaxes(np.swapaxes(data,0,-1), 0,1) #Make sure that it is x,y,L
wnan = np.isnan(data) #remove Nan data
data[wnan] = 0
data = data - data.min()

w = np.arange(len(data[0,0,:]))
#w = pyana.getdata('wav.6302.f0')
cfilter = coco.coco_filters(w, 'exp', [[25,20],[50,20],[75,20]]) #create filter
cocoimg, cocodata = coco.coco(data, cfilter, 'test.png') #create coco image
cbar = coco.cbarimg() #create colorbar
coco.coco_img(cocoimg, 'test2.png', cbar) #combine image and colorbar and save

#w = np.array([-0.88 , -0.55 , -0.495, -0.44 , -0.385, -0.33 , -0.275, -0.22 , -0.165, -0.11 , -0.055,  0.   ,  0.055,  0.11 ,  0.165,  0.22 ,  0.275,  0.33 ,  0.385,  0.44 ,  0.495,  0.55 ,  0.88 ])

data = np.swapaxes(np.swapaxes(data,1,-1), 1,2) #Make sure that it is x,y,L
wnan = np.isnan(data) #remove Nan data
data[wnan] = 0
w = np.arange(len(d[0,0,:]))

for i in range(104):
    d = data[i]
    
    cfilter = coco.coco_filters(w, 'exp', [[5,3],[10,3],[15,3]]) #create filter
    cocoimg, cocodata = coco.coco(d, cfilter, 'video/'+str(i)+'.png') #create coco image
    #cbar = coco.cbarimg() #create colorbar
    #coco.coco_img(cocoimg, 'test2.png', cbar) #combine image and colorbar and save

def save(path,fps,name):
    os.system("ffmpeg -r "+fps+" -i "+path+"%01d.png -q:v 1 -vcodec mpeg4 -y "+path+name+".mp4")

import matplotlib.animation as animation

def animate_cube(cube_array, cut=True, mn=0, sd=0, interval=75, cmap='hot'):
    '''
        animates a python cube for quick visualisation. CANNOT BE SAVED.
        
        INPUT:
        cube_array  : name of 3D numpy array that needs to be animated.
        cut         : trims pixels off of the images edge to remove edge detector effects.
        Default = True as 0 returns empty array.
        mn          : mean of the cube | Used for contrast
        sd          : std of the cube  | Used for contrast
        interval    : #of ms between each frame.
        cmap        : colormap. Default='hot'
        
        OUTPUT:
        animated window going through the cube.
        
        '''
    
    fig = plt.figure()
    std = np.std(cube_array[0])
    mean = np.mean(cube_array[0])
    if mn==sd and mn==0:
        img = plt.imshow(cube_array[0][cut:-cut, cut:-cut], animated=True, vmax=mean+3*std, vmin=mean-3*std, cmap=cmap)
    else:
        img = plt.imshow(cube_array[0][cut:-cut, cut:-cut], animated=True, vmax=mn+3*sd, vmin=mn-3*sd, cmap=cmap)

    def updatefig(i):
        img.set_array(cube_array[i][cut:-cut, cut:-cut])
        return img,

    ani = animation.FuncAnimation(fig, updatefig, frames=cube_array.shape[0], interval=interval, blit=True)
    plt.colorbar()
    plt.show()

def save_animated_cube(cube_array, name, fps=15, artist='me', cut=True, mn=0, sd=0, interval=75, cmap='hot'):
    '''
        animates a python cube and saves it
        
        INPUT:
        cube_array  : name of 3D numpy array that needs to be animated.
        name        : filename Should be .mp4
        fps         : frames per second. Default = 15
        artist      : name of creator. Defealt = 'me'
        cut         : trims pixels off of the images edge to remove edge detector effects.
        Default = True as 0 returns empty array.
        mn          : mean of the cube | Used for contrast
        sd          : std of the cube  | Used for contrast
        interval    : #of ms between each frame.
        cmap        : colormap. Default='hot'
        
        OUTPUT:
        animated window going through the cube.
        
        '''
    
    fig = plt.figure()
    std = np.std(cube_array[0])
    mean = np.mean(cube_array[0])
    if mn==sd and mn==0:
        img = plt.imshow(cube_array[0][cut:-cut, cut:-cut], animated=True, vmax=mean+3*std, vmin=mean-3*std, cmap=cmap)
    else:
        img = plt.imshow(cube_array[0][cut:-cut, cut:-cut], animated=True, vmax=mn+3*sd, vmin=mn-3*sd, cmap=cmap)

    def updatefig(i):
        img.set_array(cube_array[i][cut:-cut, cut:-cut])
        return img,

    ani = animation.FuncAnimation(fig, updatefig, frames=cube_array.shape[0], interval=interval, blit=True)
    plt.colorbar()
    Writer = animation.writers['ffmpeg']
    writer = Writer(fps=fps, metadata=dict(artist=artist), bitrate=1800)
    ani.save(name, writer=writer)


