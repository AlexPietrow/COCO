import numpy as np
from PIL import Image as img
import astropy.io.fits as f
import matplotlib.pyplot as plt

def cbarimg(Ticks=['Right Enhanced', 'Central Enhanded', 'Left Enhanced'], size=(0.5,6), show=0):
    '''
    Makes RGBR colorbar whith proper ticks.
    INPUT:
        Ticks   :   List of 3 values to describe what the 3 colors stand for.
        size    :   Size of the bar in inch
        show    :   Shows the colorbar. Default=0
    '''
    Ticks = np.append(Ticks, Ticks[0])
    a = np.array([[0,1]])
    plt.figure(figsize=size)
    plt.imshow(a, cmap="hsv")
    plt.gca().set_visible(False)
    cax = plt.axes([0.1, 0.2, 0.8, 0.6])
    cbar = plt.colorbar(cax=cax, ticks=[0,0.3,0.65,1] )
    cbar.ax.set_yticklabels(Ticks)
    plt.autoscale()
    plt.savefig('cbar.png',bbox_inches='tight')
    if show:
        plt.show()
    cbarimg = img.open('cbar.png')
    return cbarimg

def coco_filters(wavelengths, filtername, pos_rgb, plot=0):
    '''
    Make filters for spec_i
    INPUT:
        wavelengths     : Wavelength points
        filtername      : name of desired filter type. Chose from.

                        'single' :  single wavelength points
                                    uses keyword pos_rgb[r,g,b]
                                    specify which wavength points wanted
                                    with r,g,b
                                    
                        'band'   :  bands of wavelength points
                                    uses keyword pos_rgb[r,g,b]
                                    specify which wavength points are wanted
                                    to start the bands with r,g,b
                                    Give a two number list for each color
                                    to indicate the begining and end wavelength
                                    note that the end wavelength is not included!
                                    e.g. [[2, 3], [3, 4], [6, 7]]
                                    
                        'exp'    :  exponential filters, like the cones of the eye
                                    uses keyword pos_rgb[r,g,b]
                                    specify which wavength points are wanted
                                    to start the bands with r,g,b
                                    Give a two number list for each color
                                    to indicate the mean and std of each Gaussian.
                                    e.g. [[2, 3], [5, 3], [11, 3]]
                                    
        pos_rgb         : input list with desired filter locations.
        plot            : plots filters. Default = 0
    
    OUTPUT:
        filter          : 3 channel cube with length (wavelengths, 3) with applied filter
        
        Based on spec_i.pro:spec_i_filters by M. Druett, Python version by A.G.M. Pietrow
    
    EXAMPLE:
        wavelengths = np.arange(10)
        spec_i_filters(wavelengths, 'band', [[2,4], [4,8], [9,9]])
        
        >>>array([  [ 0.  ,  0.  ,  0.  ],
                    [ 0.  ,  0.  ,  0.  ],
                    [ 0.5 ,  0.  ,  0.  ],
                    [ 0.5 ,  0.  ,  0.  ],
                    [ 0.  ,  0.25,  0.  ],
                    [ 0.  ,  0.25,  0.  ],
                    [ 0.  ,  0.25,  0.  ],
                    [ 0.  ,  0.25,  0.  ],
                    [ 0.  ,  0.  ,  0.  ],
                    [ 0.  ,  0.  ,  1.  ]])
    '''
    
    nL = len(wavelengths)
    filter = np.zeros([nL,3])
    
    if filtername == 'single':
        if len(pos_rgb) <> 3:
            raise ValueError("pos_rgb should have 3 values!")
        filter[pos_rgb[0],0] = 1.
        filter[pos_rgb[1],1] = 1.
        filter[pos_rgb[2],2] = 1.
        
        if plot:
            plt.plot(filter[:,0], color='r')
            plt.plot(filter[:,1], color='g')
            plt.plot(filter[:,2], color='b')
            plt.show()

    elif filtername == 'band':
        if len(pos_rgb) <> 3:
            raise ValueError("pos_rgb should have 3 values!")
        try:
            len(pos_rgb[0]) <> 2
        except TypeError:
            raise TypeError("Check pos_rgb, it should be im the shape of [[a,b],[c,d],[e,f]]")

        if len(pos_rgb[0]) <> 2 or len(pos_rgb[1]) <> 2 or len(pos_rgb[2]) <> 2:
            raise ValueError("pos_rgb should have 2 values for each color band.")

        for i in range(3):
            if (pos_rgb[i][1] - pos_rgb[i][0]) < 0:
                raise ValueError("invalid range.")
            
            if pos_rgb[i][0] == pos_rgb[i][1]: #check if bin is broader than 1
                filt_int = 1./(pos_rgb[i][1] - pos_rgb[i][0] + 1)
                filter[pos_rgb[i][0], i] = filt_int
            else:
                filt_int = 1./(pos_rgb[i][1] - pos_rgb[i][0])
                filter[pos_rgb[i][0]:pos_rgb[i][1], i] = filt_int


        if plot:
            plt.plot(filter[:,0], color='r')
            plt.plot(filter[:,1], color='g')
            plt.plot(filter[:,2], color='b')
            plt.show()

            
    elif filtername == 'exp':
        if len(pos_rgb) <> 3:
            raise ValueError("pos_rgb should have 3 values!")
        try:
            len(pos_rgb[0]) <> 2
        except TypeError:
            raise TypeError("Check pos_rgb, it should be im the shape of [[a,b],[c,d],[e,f]]")

        #mean, sigma
        for i in range(3):
            std = np.float(pos_rgb[i][1])
            mn  = np.float(pos_rgb[i][0])
            c = 1./(std * np.sqrt(2*np.pi))
            
            num = np.arange(len(filter[:,0]))
            num = wavelengths
            
            filter[:,i] =   (c*  np.e**(-0.5 * ( ( num - mn)/std )**2 ) )


        if plot:
            plt.plot(filter[:,0], color='r')
            plt.plot(filter[:,1], color='g')
            plt.plot(filter[:,2], color='b')
            plt.show()

            
    else:
        raise ValueError("filtername not recognised. Check help(filters) for available filter types.")

    return filter


def coco(datacube, filters, name, threshold=0):
    '''
    Color Convolves a 3D cube with an RGB filter.
    INPUT:
        datacube    : 3D cube of shape [x,y,lambda]
        filters     :
        name        : name of file
        
    OUTPUT:
        image       : collapsed spec_i image
        
    Based on spec_i.pro by M. Druett, Python version by A.G.M. Pietrow
    '''
    #datacbe = 3d, numerical, filters have len n
    if len(datacube.shape) <> 3:
        raise ValueError("Array must be 3D")
    try:
        datacube.astype(float)

    except ValueError:
        raise ValueError("Array must be numerical")
    ##filters correct len

    #apply filter to cube and collapse cube int x,y,RGB
    nx,ny,nl = datacube.shape
    filter_rgb = np.tile(filters, (ny,nx,1,1))
    filter_rgb = np.swapaxes(filter_rgb, 0,2)
    data_rgb = np.tile(datacube,(3,1,1,1))
    data_rgb = np.swapaxes(data_rgb,0,-1)
    #data_rgb = np.swapaxes(f_rgb,1,2)
    data_filtered = data_rgb * filter_rgb
    data_collapsed = np.sum(data_filtered, axis=0)
    #normalize to values between 0 and 255
    if threshold:
        data_collapsed[np.where(data_collapsed > threshold[1])] = threshold[1]
        data_collapsed[np.where(data_collapsed < threshold[0])] = threshold[0]

    data_collapsed_norm = np.uint8(np.round(data_collapsed*255/np.max(data_collapsed)))
    image = img.fromarray(data_collapsed_norm)
    image.save(name)
    #image.show()

    return image, data_collapsed_norm

def coco_img(cocoimg, name, cbarimg):
    '''
    Makes a composite image of COCO and a colorbar.
    INPUT:
        cocoimg :   PIL.Image of COCO data. Made with coco()
        name    :   name under which file should be saved
        cbarimg :   PIL.Image of colorbar. Made with cbarimg()
    '''
    imx, imy = cocoimg.size
    cx, cy = cbarimg.size
    bg = img.new('RGB', (imx+20+cx,imy), (255,255,255))
    bg.paste(cocoimg)
    bg.paste(cbarimg, (imx + 20, (imy-cy)/2))
    bg.show()
    bg.save(name)
    plt.close()



