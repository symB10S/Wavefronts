from Wavefront_Generation import get_spatial_voltage_current_at_time
from Wavefront_Storage import *
from Wavefront_Misc import get_array_absolute_maximum, convert_to_image_array, split_outer_inner_default_kwargs
from decimal import Decimal, ROUND_HALF_DOWN
import copy
from warnings import warn

import numpy as np
import matplotlib as mpl
import matplotlib.pyplot as plt
from matplotlib.ticker import (MultipleLocator, EngFormatter)
from matplotlib.animation import FFMpegWriter
from tqdm import tqdm

plt.rcParams['animation.ffmpeg_path'] = 'ffmpeg\\ffmpeg.exe'

import ipywidgets as widgets
from IPython.display import display

def clear_subplot(axs):
    for ax in axs:
        ax.cla()

# Fanout Diagrams

default_fanout_kwargs = {
    'title': "Magnitude Fanout",
    'show_colour_bar': True,
    'contrast' : False,
    'padding' : 0,
    'units' : 'A',
    'origin' : 'lower',
    'transpose' : True,
    'show_ticks' : False,
    'custom_colour_bar_limits': False
}

def plot_fanout_magnitude(input_array : np.ndarray , ax, **input_kwargs):
    """the core function for plotting the fanout diagram of a 2D numpy array.
    Points are coloured using the 'seismic' colour map with red being positive and blue negative.

    :param input_array: The array to be plotted, can also accept lists of numerical data
    :type input_array: np.ndarray or List
    :param ax: a matplotlib Axe object to plot using 'imshow'
    :type ax: matplotlib.Axe
    
    :**input_kwargs**:
        - **title** (*str*) - The title of the fanout (default = "Magnitude Fanout")
        - **show_colour_bar** (*bool*) - if colour bar must be shown (default = True)
        - **contrast** (*bool*) - if the orign node must be ignored for the colour mapping maximum value calculation (default = False)
        - **padding** (*int*) - the amount of padding around the array, thinner arrays are easier to navigate with padding (default = 0)
        - **units** (*str*) - the units of the colour bar (default = 'A')
        - **origin** (*str*) - either 'lower' or 'upper', sets the postion of the origin (default = 'lower')
        - **transpose** (*bool*) - makes x-axis the L-axis if true (default = True)
        - **show_ticks** (*bool*) - if axis ticks are shown (default = False)
        - **custom_colour_bar_limits** (*tuple or bool*) - pass a (max_value, min_value) tuple to customize colouring extent of the fanout(default = False)
        
    .. warning::
        a **wavefront storage array** must be in their magnitude forms, these arrays can be fetched using :py:meth:`Wavefront_Storage.Data_Output_Storage.get_sending_wavefronts_magnitudes` 
        or :py:meth:`Wavefront_Storage.Data_Output_Storage.get_returning_wavefronts_magnitudes`. 
        Alternatively magnitdues from a **wavefront array** can be manually extracted by passing as an input parameter to 
        :py:func:`Wavefront_Misc.get_voltage_array` or :py:func:`Wavefront_Misc.get_current_array`
        
    :return: plots a magnitude fanout on the provided axis
    """
    
    default_kwargs = handle_default_kwargs(input_kwargs,default_fanout_kwargs)
    # convert Lists to image array if necessary 
    input_array = convert_to_image_array(input_array)
    
    if(isinstance(default_kwargs['custom_colour_bar_limits'] ,tuple)):
        max_boundary = default_kwargs['custom_colour_bar_limits'][0]
        min_boundary = default_kwargs['custom_colour_bar_limits'][1]
    elif (default_kwargs['contrast']): 
        Contrast = copy.copy(input_array.astype(float))
        max_index = np.unravel_index(np.argmax(Contrast, axis=None), Contrast.shape)
        Contrast[max_index] = 0
        max_boundary = get_array_absolute_maximum(Contrast)
        min_boundary = -max_boundary
    else:
        max_boundary = get_array_absolute_maximum(input_array.astype(float))
        min_boundary = -max_boundary
    
    if default_kwargs['transpose'] :
        array_plot = np.pad(input_array.astype(float),(default_kwargs['padding'],default_kwargs['padding'])).transpose()
        ax.set_xlabel('L - axis ')
        ax.set_ylabel('C - axis ')
    else:
        array_plot = np.pad(input_array.astype(float),(default_kwargs['padding'],default_kwargs['padding']))
        ax.set_ylabel('L - axis ')
        ax.set_xlabel('C - axis ')
    
    def offset_formatter(x, pos):
        return int(x - default_kwargs['padding'])

    if(default_kwargs['show_ticks']):
        ax.xaxis.set_major_formatter(plt.FuncFormatter(offset_formatter))
        ax.yaxis.set_major_formatter(plt.FuncFormatter(offset_formatter))
    else:
        ax.set_xticks([])
        ax.set_yticks([])
      
    ax.set_title(default_kwargs['title'])
    
    c = ax.imshow(array_plot,cmap= mpl.cm.seismic,vmax =max_boundary, vmin = min_boundary,origin=default_kwargs['origin'])
    
    if(default_kwargs['show_colour_bar']):
        cb = ax.get_figure().colorbar(c,ax=ax)
        cb.ax.yaxis.set_major_formatter(EngFormatter(default_kwargs['units']))
        
def plot_fanout_time(input_array : np.ndarray ,ax , **input_kwargs):
    """Plot a time fanout of a provided input array. 
    Coloured in a rainbow pattern from the minimum array value to the maximum array value.

    :param input_array: The array to be plotted, can also accept lists of numerical data
    :type input_array: np.ndarray or List
    :param ax: a matplotlib Axe object to plot using 'imshow'
    :type ax: matplotlib.Axe
    
    :**input_kwargs**:
        - same input kwargs as :py:func:`plot_fanout_magnitude`
        - **mask_zero** (*bool*) - if zeros values must be masked (default = True)
        
    .. warning::
        a **wavefront storage array** must be in their magnitude forms, these arrays can be fetched using :py:meth:`Wavefront_Storage.Data_Output_Storage.get_sending_wavefronts_magnitudes` 
        or :py:meth:`Wavefront_Storage.Data_Output_Storage.get_returning_wavefronts_magnitudes`. 
        Alternatively magnitdues from a **wavefront array** can be manually extracted by passing as an input parameter to 
        :py:func:`Wavefront_Misc.get_voltage_array` or :py:func:`Wavefront_Misc.get_current_array`
        
    :return: plots a rainbow coloured image on the provided axis
    """
    default_kwargs = default_fanout_kwargs.copy()
    default_kwargs['mask_zero']  = True
    
    default_kwargs = handle_default_kwargs(input_kwargs,default_kwargs)
    # convert Lists to image array if necessary 
    input_array = convert_to_image_array(input_array)
    
    if (default_kwargs['custom_colour_bar_limits']==False):
        max_boundary = np.max(input_array.astype(float))  
        min_boundary = np.min(input_array.astype(float))  
        
    else:
        max_boundary, min_boundary = default_kwargs['custom_colour_bar_limits']
        
    if default_kwargs['transpose'] :
        array_plot = np.pad(input_array.astype(float),(default_kwargs['padding'],default_kwargs['padding'])).transpose()
        ax.set_xlabel('L - axis ')
        ax.set_ylabel('C - axis ')
    else:
        array_plot = np.pad(input_array.astype(float),(default_kwargs['padding'],default_kwargs['padding']))
        ax.set_ylabel('L - axis ')
        ax.set_xlabel('C - axis ')
    
    def offset_formatter(x, pos):
        return int(x - default_kwargs['padding'])

    if(default_kwargs['show_ticks']):
        ax.xaxis.set_major_formatter(plt.FuncFormatter(offset_formatter))
        ax.yaxis.set_major_formatter(plt.FuncFormatter(offset_formatter))
    else:
        ax.set_xticks([])
        ax.set_yticks([])
        
    if(default_kwargs['mask_zero']):
        array_plot = np.ma.masked_where(array_plot == 0, array_plot)
        array_plot[0,0] = 0
      
    ax.set_title(default_kwargs['title'])
    
    c = ax.imshow(array_plot,cmap= mpl.cm.jet,vmax =max_boundary, vmin = min_boundary,origin=default_kwargs['origin'])
    
    if(default_kwargs['show_colour_bar']):
        cb = ax.get_figure().colorbar(c,ax=ax)
        cb.ax.yaxis.set_major_formatter(EngFormatter(default_kwargs['units']))
            
def plot_fanout_interconnect(data_output: Data_Output_Storage,ax, which_string :str, contrast_voltage = True,**kwargs):
    """A wrapper function for :py:func:`plot_fanout_magnitude` for plotting interconnect fanouts.
    Takes in a Data_Output_Storage object and a string to plot and auto format the fanout.
    It will pass provided **kwargs to the underlying plot_fanout_magnitude fucntion.
    
    :param data_output: The data output object that contians the interconnect arrays. Could be commutative or multiplicative data. 
    :type data_output: Data_Output_Storage
    :param ax: the matplotlib axis to plot on
    :type ax: matplotlib Axes object
    :param which_string: determine which interconnect value to plot. Options are "voltage inductor", "current inductor", "voltage capacitor", "current capacitor"
    :type which_string: str
    :param contrast_voltage: determine if voltage arrays must exclude the orign point for better contrast, default is True
    :type contrast_voltage: bool
    :raises ValueError: if incorrect 'which_string' is not provided.
    :raises warning: if 'title=', 'units=' or 'contrast=' keyword are included as they are auto assigned by this function
    
    .. warning::
        When providing the ****kwargs**, you cannot specify 'title=', 'units=' or ''contrast='  as these are auto assinged. Providing these values will result in an error. 
    """
    
    if ('title' in kwargs):
        warn("you cannot specifiy the title of these fanouts as they are automatically assigned. Use plot_fanout_magnitude() instead")
        del kwargs['title']
    elif('units' in kwargs):
        warn("you cannot specifiy the units of these fanouts as they are automatically assigned. Use plot_fanout_magnitude() instead")
        del kwargs['units']
    elif('contrast' in kwargs):
        warn("you cannot specifiy the contrast of these fanouts as they are automatically assigned. Use the third input parameter of this function to control contrast")
        del kwargs['contrast']
    
    allowed_strings = ["voltage inductor", "current inductor", "voltage capacitor", "current capacitor"]
    if(which_string.lower() == allowed_strings[0] ):
        plot_fanout_magnitude( data_output.Voltage_Interconnect_Inductor,ax,title = "Inductor Voltage at Interconnect",units='V',contrast=contrast_voltage,**kwargs)
    elif(which_string.lower() == allowed_strings[1] ):
        plot_fanout_magnitude(data_output.Current_Interconnect_Inductor,ax,title = "Inductor Current at Interconnect",**kwargs)
    elif(which_string.lower() == allowed_strings[2] ):
        plot_fanout_magnitude(data_output.Voltage_Interconnect_Capacitor,ax,title = "Capacitor Voltage at Interconnect",units='V',contrast=contrast_voltage,**kwargs)
    elif(which_string.lower() == allowed_strings[3] ):
        plot_fanout_magnitude(data_output.Current_Interconnect_Capacitor,ax,title = "Capacitor Current at Interconnect",**kwargs)
    else:
            raise ValueError(f"Incorrect plotting choice /, {which_string} is not a valid option. Optiond are: \n {allowed_strings}")
        
def plot_fanout_wavefronts(data_output: Data_Output_Storage,ax, which_string :str, is_sending : bool = True, **kwargs):
    """A wrapper function for :py:func:`plot_fanout_magnitude` for plotting wavefront fanouts.
    Takes in a Data_Output_Storage object, a string and a bool are passed to plot and auto format the fanout.
    It will pass provided **kwargs to the underlying plot_fanout_magnitude fucntion.

    :param data_output: The data output object that contians the interconnect arrays. Could be commutative or multiplicative data. 
    :type data_output: Data_Output_Storage
    :param ax: the matplotlib axis to plot on
    :type ax: matplotlib Axes object
    :param which_string: determine which interconnect value to plot. Options are "voltage inductor", "current inductor", "voltage capacitor", "current capacitor"
    :type which_string: str
    :raises ValueError: if incorrect 'which_string' is not provided.
    :param is_sending: determines if sending or returning wavefronts must be plotted, defaults to True
    :type is_sending: bool, optional
    
    .. warning::
        When providing the ****kwargs**, you cannot specify 'title=' or 'units=' as these are auto assinged. Providing these values will result in an error. 
    """
    if ('title' in kwargs):
        warn("you cannot specifiy the title of these fanouts as they are automatically assigned. Use plot_fanout_magnitude() instead")
        del kwargs['title']
    elif('units' in kwargs):
        warn("you cannot specifiy the units of these fanouts as they are automatically assigned. Use plot_fanout_magnitude() instead")
        del kwargs['units']
    
    allowed_strings = ["voltage inductor", "current inductor", "voltage capacitor", "current capacitor"]
    
    if(is_sending):
        title_prefix = "Sending "
        get_func = data_output.get_sending_wavefronts_magnitudes
    else:
        title_prefix = "Returning "
        get_func = data_output.get_returning_wavefronts_magnitudes
    
    if(which_string.lower() == allowed_strings[0] ):
        plot_fanout_magnitude(get_func(which_string),ax,title = title_prefix + "Voltage Wavefronts\n in Inductor",units='V',**kwargs)
        
    elif(which_string.lower() == allowed_strings[1] ):
        plot_fanout_magnitude(get_func(which_string),ax,title = title_prefix + "Current Wavefronts\n in Inductor",**kwargs)
        
    elif(which_string.lower() == allowed_strings[2] ):
        plot_fanout_magnitude(get_func(which_string),ax,title = title_prefix + "Voltage Wavefronts\n in Capacitor",units='V',**kwargs)
        
    elif(which_string.lower() == allowed_strings[3] ):
        plot_fanout_magnitude(get_func(which_string),ax,title = title_prefix + "Current Wavefronts\n in Capacitor",**kwargs)
    else:
            raise ValueError(f"Incorrect plotting choice /, {which_string} is not a valid option. Optiond are: \n {allowed_strings}")

def make_fanout_crossection(input_array : np.ndarray, L_intercept : int, C_intercept : int, **kwargs):
    """Plots a magnitude fanout and corssection at a L and C intercept for a given input data array.
    The kwargs supplied are passed down to :py:func:`plot_fanout_magnitude`. 
    Additonal key-value customiztion is included for the crossection plot below.

    :param input_array: The fanout data to be investigated
    :type input_array: np.ndarray
    :param L_intercept: The value on the L-axis to intercept
    :type L_intercept: int
    :param C_intercept: The value on the C-axis to intercept
    :type C_intercept: int
    :return: the matplotlib Figure and Axes objects created in this fucntion
    :rtype: tuple( fig , ax )
    :**kwargs for crossection**:
        - **ax** (*Dict(Axes)*) - Whether to create a subpot or use exsiting subplot axes.If left blank default is 'False' and subplot is created internally.If axes are provided, the must be of a matplotlib.pyplot.subplot_mosaic() form.The labels for these axes must inculde: 
            - 'C' for C-plot/ L interception
            - 'L' for L-plot/ C interception
            - 'D' for the Diagonal plot
            - 'F' for Fanout magnitude plot
        - **fig_size** (*tuple of ints*) - The size of the figure. Default is (10, 8).
        - **Transpose_C_Plot** (*bool*) - Whether to transpose the C plot. Default is True.
        - **Transpose_L_Plot** (*bool*) - Whether to transpose the L plot. Default is False
        
    .. code-block::
    
        from Wavefront_Generation import Full_Cycle
        from Wavefront_Plotting import make_fanout_crossection
        import matplotlib.pyplot as plt
        
        # simulate interface
        interface = Full_Cycle(L_time='6.5' , C_time='3' , L_impedance='700')
        
        # make axes internally, intercept at L=25, C= 10
        data = interface.data_output_commutative.Voltage_Interconnect_Capacitor
        make_fanout_crossection(data, 25, 10, units='V')
        
        # make axes externally, intercept at L=25, C= 10
        
        fig, ax = plt.subplot_mosaic([['C','F'],
                                      ['D','L']])
                                      
        make_fanout_crossection(data, 25, 10, units='V', ax=ax)
        
        plt.show()
        
        
    .. warning::
        if ax keyword is not provided, fucntion will make new subplot objects each time it is called.
        These plots will not be closed by default, so if multiple calls are needed it is suggested you provide
        the appropriate subplot_mosaic Axes object.
    """
    
    default_crossection_kwargs : dict = {'ax':False,
                                         'fig_size':(10,8),
                                         'Transpose_C_Plot':True,
                                         'Transpose_L_Plot':False}
    
    internal_fanout_kwargs = default_fanout_kwargs.copy()
    internal_fanout_kwargs['show_ticks'] = True
    
    crossection_kwargs, fanout_kwargs = split_outer_inner_default_kwargs(kwargs,default_crossection_kwargs,internal_fanout_kwargs)
    input_array = convert_to_image_array(input_array)# converts list to 2D numpy object
    
    if (crossection_kwargs['ax'] == False):
        # create fig and ax
        fig, ax = plt.subplot_mosaic([['C','F'],
                                      ['D','L']])
    else :
        ax = crossection_kwargs['ax']
        fig = ax['C'].get_figure()

    fig.set_size_inches(crossection_kwargs['fig_size'])
    fig.suptitle(f"Crossection of Fanout at index L = {L_intercept}, C = {C_intercept}")
    
    # handle out of bounds
    input_array_shape = input_array.shape
    if (L_intercept < 0):
        L_intercept = 0
    elif(L_intercept>input_array_shape[0]-1):
        L_intercept = input_array_shape[0]-1
        
    if (C_intercept < 0):
        C_intercept = 0
    elif(C_intercept>input_array_shape[1]-1):
        C_intercept = input_array_shape[1]-1
        
    L_y = input_array[:,C_intercept]
    C_y = input_array[L_intercept,:]
    D_y = np.diag(input_array)
    
    L_x = np.arange(0,len(L_y))
    C_x = np.arange(0,len(C_y))
    
    if (crossection_kwargs['Transpose_L_Plot']):
        ax['L'].set_ylabel('L-axis')
        ax['L'].set_ylim(0,input_array_shape[0])
        ax['L'].xaxis.set_major_formatter(EngFormatter(kwargs['units']))
        ax['L'].plot(L_y,L_x)
        ax['L'].axvline(x=0,color='gray',linestyle= '--')
    else:
        ax['L'].set_xlabel('L-axis')
        ax['L'].set_xlim(0,input_array_shape[0])
        ax['L'].yaxis.set_major_formatter(EngFormatter(kwargs['units']))
        ax['L'].plot(L_x,L_y)
        ax['L'].axhline(y=0,color='gray',linestyle= '--')
    
    if(crossection_kwargs['Transpose_C_Plot']):
        ax['C'].set_ylabel('C-axis')
        ax['C'].set_ylim(0,input_array_shape[1])
        ax['C'].xaxis.set_major_formatter(EngFormatter(kwargs['units']))
        ax['C'].plot(C_y,C_x)
        ax['C'].axvline(x=0,color='gray',linestyle= '--')
    else:
        ax['C'].set_xlabel('L-axis')
        ax['C'].set_xlim(0,input_array_shape[1])
        ax['C'].yaxis.set_major_formatter(EngFormatter(kwargs['units']))
        ax['C'].plot(C_x,C_y)
        ax['C'].axhline(y=0,color='gray',linestyle= '--')
        
    ax['D'].set_xlabel('Diagonal-axis')
    ax['D'].yaxis.set_major_formatter(EngFormatter(kwargs['units']))
    ax['D'].plot(D_y)
    ax['D'].set_xlim(0)
    
    plot_fanout_magnitude(input_array,ax['F'],**fanout_kwargs)
    ax['F'].plot([0,input_array_shape[0]],[C_intercept,C_intercept],'k-')
    ax['F'].plot([L_intercept,L_intercept],[0,input_array_shape[1]],'k-')
    ax['F'].plot([0,input_array_shape[0]],[0,input_array_shape[1]],'k-')
    
    # if figure created internally then return created handles 
    if (crossection_kwargs['ax'] == False):
        return fig,ax

def make_fanout_interconnect_all(data_output: Data_Output_Storage,contrast_voltage = True,**kwargs):
    """plots all the interconnect magnitude fanouts for a particular Data_Output_Storage object. 
    A wrapper fucniton for :py:func:`plot_fanout_interconnect`.
    This is a 'make' type function which means that by default the function will internally create the plotting axes unless specified otherwise. 
    The kwargs supplied are passed down to :py:func:`plot_fanout_interconnect`. 
    Additonal key-value customiztion is included for the crossection plot below.

    :param data_output: The data object to be plotted
    :type data_output: Data_Output_Storage
    :param contrast_voltage: if the voltage arrays must ignore the intial excitation point for better contrast, defaults to True
    :type contrast_voltage: bool, optional
    :return: the matplotlib Figure and Axes objects created in this function (if created)
    :rtype: tuple( fig , ax )
    :**kwargs for figure creation**:
        - **ax** (*Dict(Axes)*) - Whether to create a subpot or use exsiting subplot axes.If left blank default is 'False' and subplot is created internally.If axes are provided, the must be of a matplotlib.pyplot.subplot_mosaic() form.The labels for these axes must inculde: 
            - 'VL' axis for inductor voltage
            - 'VC' axis for capcitor voltage
            - 'IL' axis for inductor current
            - 'IC' axis for capacitor current
        - **fig_size** (*tuple of ints*) - The size of the figure. Default is (10, 8).

    .. code-block::
    
        from Wavefront_Generation import Full_Cycle
        from Wavefront_Plotting import make_fanout_interconnect_all
        import matplotlib.pyplot as plt

        # simulate interface
        interface = Full_Cycle(L_time='12' , C_time='8')

        # make figure internally, plot commutative data
        fig1,ax1 = make_fanout_interconnect_all(interface.data_output_commutative)
        fig1.suptitle(f"commutative Fanouts") # customize title

        # make figure externally, put currents left and voltages right
        fig2, ax2 = plt.subplot_mosaic([['IL','VL'],
                                        ['IC','VC']])

        # pass ax2 to fucniton, also, show multiplicative data this time
        make_fanout_interconnect_all(interface.data_output_multiplicative, ax=ax2)
        fig2.suptitle(f"multiplicative Fanouts") # customize title

        plt.show()
        
    .. warning::
        if ax keyword is not provided, fucntion will make new subplot objects each time it is called.
        These plots will not be closed by default, so if multiple calls are needed it is suggested you provide
        the appropriate subplot_mosaic Axes object.
    """

    default_make_kwargs : dict = {'ax':False,
                                  'fig_size':(10,8)}
    
    make_kwargs, fanout_kwargs = split_outer_inner_default_kwargs(kwargs,default_make_kwargs,default_fanout_kwargs)
    
    del fanout_kwargs['title']
    del fanout_kwargs['units']
    del fanout_kwargs['contrast']
    
    if (make_kwargs['ax'] == False):
        fig, ax = plt.subplot_mosaic([['VL','VC'],
                                    ['IL','IC']])
    else:
        ax = make_kwargs['ax']
        fig = ax['VL'].get_figure()
        
    
    fig.set_size_inches(make_kwargs['fig_size'])
    fig.suptitle(f"Interconnect Fanouts")
    
    plot_fanout_interconnect(data_output,ax['VL'],"Voltage Inductor",contrast_voltage,**fanout_kwargs)
    plot_fanout_interconnect(data_output,ax['IL'],"Current Inductor",**fanout_kwargs)
    plot_fanout_interconnect(data_output,ax['VC'],"Voltage Capacitor",**fanout_kwargs)
    plot_fanout_interconnect(data_output,ax['IC'],"Current Capacitor",**fanout_kwargs)
    
    # figure internally created, return figure and axes
    if (make_kwargs['ax'] == False):
        return fig,ax

def make_fanout_wavefronts_all(data_output: Data_Output_Storage,is_Inductor: bool,**kwargs):
    """plots all the sending and returning magnitude fanouts for a transmission line of a Data_Output_Storage object. 
    A wrapper fucniton for :py:func:`plot_fanout_wavefronts`.
    This is a 'make' type function which means that by default the function will internally create the plotting axes unless specified otherwise. 
    The kwargs supplied are passed down to :py:func:`plot_fanout_wavefronts`. 
    Additonal key-value customiztion is included for the crossection plot below.

    :param data_output: The data object to be plotted
    :type data_output: Data_Output_Storage
    :param is_Inductor: if the wavefronts shown are form the inductor or the capacitor.
    :type is_Inductor: bool
    :return: the matplotlib Figure and Axes objects created in this function (if created)
    :rtype: tuple( fig , ax )
    :**kwargs for figure creation**:
        - **ax** (*Dict(Axes)*) - Whether to create a subpot or use exsiting subplot axes.If left blank default is 'False' and subplot is created internally.If axes are provided, the must be of a matplotlib.pyplot.subplot_mosaic() form.The labels for these axes must inculde: 
            - 'VS' axis for sending voltage
            - 'VR' axis for returning voltage
            - 'IS' axis for sending current
            - 'IR' axis for returning current
        - **fig_size** (*tuple of ints*) - The size of the figure. Default is (10, 8).

    .. code-block::
    
        from Wavefront_Generation import Full_Cycle
        from Wavefront_Plotting import make_fanout_wavefronts_all
        import matplotlib.pyplot as plt

        # simulate interface
        interface = Full_Cycle(L_time='0.34' , C_time='0.12', L_impedance = '700', C_impedance = '7')

        # make figure internally, 
        # plot commutative inductive wavefronts
        fig_ind,ax_ind = make_fanout_wavefronts_all(interface.data_output_commutative,True)

        # plot commutative capacitive wavefronts
        fig_cap,ax_cap = make_fanout_wavefronts_all(interface.data_output_commutative,False)

        # make figure externally,
        # put sending wavefronts left and returning wavefronts right
        # show merged data

        fig2_ind, ax2_ind = plt.subplot_mosaic([['IS','IR'],
                                                ['VS','VR']])
        make_fanout_wavefronts_all(interface.data_output_multiplicative,True, ax=ax2_ind)

        # put voltages in opposite corners (for fun)
        fig2_cap, ax2_cap = plt.subplot_mosaic([['IS','VR'],
                                                ['VS','IR']])
        make_fanout_wavefronts_all(interface.data_output_multiplicative,False, ax=ax2_cap)

        plt.show()
        
    .. warning::
        if ax keyword is not provided, fucntion will make new subplot objects each time it is called.
        These plots will not be closed by default, so if multiple calls are needed it is suggested you provide
        the appropriate subplot_mosaic Axes object.
    """   
    default_make_kwargs : dict = {'ax':False,
                                  'fig_size':(12,10)}
    
    make_kwargs, fanout_kwargs = split_outer_inner_default_kwargs(kwargs,default_make_kwargs,default_fanout_kwargs)
    
    del fanout_kwargs['title']
    del fanout_kwargs['units']
    # del fanout_kwargs['contrast']
    
    if (make_kwargs['ax'] == False):
        fig, ax = plt.subplot_mosaic([['VS','IS' ],
                                      ['VR','IR']])
    else:
        ax = make_kwargs['ax']
        fig = ax['VS'].get_figure()
    
    fig.set_size_inches(make_kwargs['fig_size'])
    
    if (is_Inductor):
    
        fig.suptitle("Inductor Wavefront Fanouts")
        plot_fanout_wavefronts(data_output,ax['VS'],"voltage inductor",True,**fanout_kwargs)
        plot_fanout_wavefronts(data_output,ax['IS'],"current inductor",True,**fanout_kwargs)
        plot_fanout_wavefronts(data_output,ax['VR'],"voltage inductor",False,**fanout_kwargs)
        plot_fanout_wavefronts(data_output,ax['IR'],"current inductor",False,**fanout_kwargs)
    else:
        
        fig.suptitle("Capacitor Wavefront Fanouts")
        plot_fanout_wavefronts(data_output,ax['VS'],"voltage capacitor",True,**fanout_kwargs)
        plot_fanout_wavefronts(data_output,ax['IS'],"current capacitor",True,**fanout_kwargs)
        plot_fanout_wavefronts(data_output,ax['VR'],"voltage capacitor",False,**fanout_kwargs)
        plot_fanout_wavefronts(data_output,ax['IR'],"current capacitor",False,**fanout_kwargs)
    
    if (make_kwargs['ax'] == False):
        return fig, ax

def handle_interface_to_ordered(data) -> Data_Output_Storage_Ordered:
    """ensures data is ordered, extracts it if it can, else raises an error.

    :param data: input data to be checked
    :type data: any
    :raises TypeError: if ordered data cannot be extracted
    :return: ordered data 
    :rtype: Data_Output_Storage_Ordered
    """
    if isinstance(data, Data_Interface_Storage ):
        data = data.data_output_ordered
    elif isinstance(data, Data_Output_Storage_Ordered ):
        pass
    else:
        raise TypeError(f"input data is of wrong type, must be Data_Output_Storage_Ordered. inputted {type(data)} instead.")
    
    return data

def plot_time_interconnect(data_output_ordered : Data_Output_Storage_Ordered,ax, which_string :str, is_integrated: bool = True ): 
    """Plots the time waveform of one of the interconncet metrics. 
    It must be noted that interconnect values stored in the :Data_Output_Storage_Ordered: object signify the 'change' in interface values due to wavefronts.
    To see the full time wavefrom, the changes must be accumulated. This function shows both change and accumulated quantities. 

    :param data_output_ordered: The data object containing 1D ordered simulation data
    :type data_output_ordered: Data_Output_Storage_Ordered or (Data_Interface_Storage)
    :param ax: The axis on which the interconncet wavefrom will be plotted.
    :type ax: Matplotlib Axes object
    :param which_string: The interconnect value to be plotted, options are "voltage inductor", "current inductor", "voltage capacitor" and "current capacitor"
    :type which_string: str
    :param is_integrated: If the wavefrom must represent the 'change' or 'accumulation of changes' of the data selected to be plotted, default is True
    :type is_integrated: bool
    :raises ValueError: if an incorrect which_string is provided.
    
    .. code-block::
    
        from Wavefront_Generation import Full_Cycle
        from Wavefront_Plotting import plot_time_interconnect
        import matplotlib.pyplot as plt

        # simulate interface
        interface = Full_Cycle(L_time='0.34' , C_time='0.12', L_impedance = '700', C_impedance = '7')

        # Make axes 
        fig,ax = plt.subplots(2,1)

        # make a handle for ordered data (very optional)
        data = interface.data_output_ordered

        # plot accumulated data on ax[0]
        plot_time_interconnect(data,ax[0],'current capacitor',True)

        # plot change data on ax[1]
        plot_time_interconnect(data,ax[1],'current capacitor',False)

        plt.show()

    .. warning::
    
        This function accepts only :py:class:`Wavefront_Storage.Data_Output_Storage_Ordered` as an input. The data is required to be 1D and ordered.
    
    """
    data_output_ordered = handle_interface_to_ordered(data_output_ordered)
    
    allowed_strings = ["voltage inductor", "current inductor", "voltage capacitor", "current capacitor"]
    
    ax.xaxis.set_major_formatter(EngFormatter('s'))
    
    if(is_integrated):
        if(which_string.lower() == allowed_strings[0] ):
            ax.set_title("Inductor voltage at Interconnect")
            ax.yaxis.set_major_formatter(EngFormatter('V'))
            ax.step(data_output_ordered.Time,np.cumsum(data_output_ordered.Voltage_Interconnect_Inductor),where='post')
        elif(which_string.lower() == allowed_strings[1] ):
            ax.set_title("Inductor current at Interconnect")
            ax.yaxis.set_major_formatter(EngFormatter('A'))
            ax.step(data_output_ordered.Time,np.cumsum(data_output_ordered.Current_Interconnect_Inductor),where='post')
        elif(which_string.lower() == allowed_strings[2] ):
            ax.set_title("Capacitor voltage at Interconnect")
            ax.yaxis.set_major_formatter(EngFormatter('V'))
            ax.step(data_output_ordered.Time,np.cumsum(data_output_ordered.Voltage_Interconnect_Capacitor),where='post')
        elif(which_string.lower() == allowed_strings[3] ):
            ax.set_title("Capacitor current at Interconnect")
            ax.yaxis.set_major_formatter(EngFormatter('A'))
            ax.step(data_output_ordered.Time,np.cumsum(data_output_ordered.Current_Interconnect_Capacitor),where='post')
        else:
            raise ValueError(f"Incorrect plotting choice /, {which_string} is not a valid option. Optiond are: \n {allowed_strings}")
    else:
        if(which_string.lower() == allowed_strings[0] ):
            ax.set_title("Inductor voltage change at Interconnect")
            ax.yaxis.set_major_formatter(EngFormatter('V'))
            ax.step(data_output_ordered.Time,data_output_ordered.Voltage_Interconnect_Inductor,where='post')
        elif(which_string.lower() == allowed_strings[1] ):
            ax.set_title("Inductor current change at Interconnect")
            ax.yaxis.set_major_formatter(EngFormatter('A'))
            ax.step(data_output_ordered.Time,data_output_ordered.Current_Interconnect_Inductor,where='post')
        elif(which_string.lower() == allowed_strings[2] ):
            ax.set_title("Capacitor voltage change at Interconnect")
            ax.yaxis.set_major_formatter(EngFormatter('V'))
            ax.step(data_output_ordered.Time,data_output_ordered.Voltage_Interconnect_Capacitor,where='post')
        elif(which_string.lower() == allowed_strings[3] ):
            ax.set_title("Capacitor current change at Interconnect")
            ax.yaxis.set_major_formatter(EngFormatter('A'))
            ax.step(data_output_ordered.Time,data_output_ordered.Current_Interconnect_Capacitor,where='post')
        else:
            raise ValueError(f"Incorrect plotting choice /, {which_string} is not a valid option. Optiond are: \n {allowed_strings}")

def plot_time_wavefronts(data_output_ordered : Data_Output_Storage_Ordered,ax, which_string :str, is_sending :bool,is_integrated: bool = True ): 
    """Plots the time waveform of one of the wavefront metrics. 
    It must be noted that interconnect values stored in the :Data_Output_Storage_Ordered: object signify the 'change' in interface values due to wavefronts.
    To see the full time wavefrom, the changes must be accumulated. This function shows both change and accumulated quantities. 

    :param data_output_ordered: The data object containing 1D ordered simulation data, also accepts full interface data
    :type data_output_ordered: Data_Output_Storage_Ordered or Data_Interface_Storage
    :param ax: The axis on which the interconncet wavefrom will be plotted.
    :type ax: Matplotlib Axes object
    :param which_string: The wavefront value to be plotted, options are "voltage inductor", "current inductor", "voltage capacitor" and "current capacitor"
    :type which_string: str
    :param is_sending: If the the wavefront data shown must be for sending or returning wavefronts.
    :type is_sending: bool
    :param is_integrated: If the wavefrom must represent the 'change' or 'accumulation of changes' of the data selected to be plotted, default is True
    :type is_integrated: bool
    :raises ValueError: if an incorrect which_string is provided.
    
    .. code-block::
    
        from Wavefront_Generation import Full_Cycle
        from Wavefront_Plotting import plot_time_wavefronts
        import matplotlib.pyplot as plt

        # Example, comparing the sending and returning current wavefronts in the capacitor:
        # =================================================================================

        # simulate interface
        interface = Full_Cycle(L_time='3' , C_time='7', L_impedance = '700', C_impedance = '7')
        data = interface.data_output_ordered

        # Make axes 
        fig,ax = plt.subplots()

        # plot sending wavefronts (not accumulated)
        plot_time_wavefronts(data,ax,'current capacitor',True,False)

        # plot returning wavefronts (not accumulated)
        plot_time_wavefronts(data,ax,'current capacitor',False,False)

plt.show()

    .. warning::
    
        This function accepts only :py:class:`Wavefront_Storage.Data_Output_Storage_Ordered` as an input. The data is required to be 1D and ordered.
    
    """
    data_output_ordered = handle_interface_to_ordered(data_output_ordered)
    
    allowed_strings = ["voltage inductor", "current inductor", "voltage capacitor", "current capacitor"]
    
    if (is_sending):
        title_prefix = "Sending "
        get_func = data_output_ordered.get_sending_wavefronts_magnitudes
    else:
        title_prefix = "Returning "
        get_func = data_output_ordered.get_returning_wavefronts_magnitudes
    
    ax.xaxis.set_major_formatter(EngFormatter('s'))
    
    if(is_integrated):
        if(which_string.lower() == allowed_strings[0] ):
            ax.set_title(title_prefix + "voltage wavefronts\n accumulated in Inductor")
            ax.yaxis.set_major_formatter(EngFormatter('V'))
        elif(which_string.lower() == allowed_strings[1] ):
            ax.set_title(title_prefix + "current wavefronts\n accumulated in Inductor")
            ax.yaxis.set_major_formatter(EngFormatter('A'))
        elif(which_string.lower() == allowed_strings[2] ):
            ax.set_title(title_prefix + "voltage wavefronts\n accumulated in Capacitor")
            ax.yaxis.set_major_formatter(EngFormatter('V'))
        elif(which_string.lower() == allowed_strings[3] ):
            ax.set_title(title_prefix + "current wavefronts\n accumulated in Capacitor")
            ax.yaxis.set_major_formatter(EngFormatter('A'))
        else:
            raise ValueError(f"Incorrect plotting choice /, {which_string} is not a valid option. Optiond are: \n {allowed_strings}")
        
        ax.step(data_output_ordered.Time,np.cumsum(get_func(which_string)),where='post')
    else:
        if(which_string.lower() == allowed_strings[0] ):
            ax.set_title(title_prefix + "voltage wavefronts\n in Inductor")
            ax.yaxis.set_major_formatter(EngFormatter('V'))
        elif(which_string.lower() == allowed_strings[1] ):
            ax.set_title(title_prefix + "current wavefronts\n in Inductor")
            ax.yaxis.set_major_formatter(EngFormatter('A'))
        elif(which_string.lower() == allowed_strings[2] ):
            ax.set_title(title_prefix + "voltage wavefronts\n in Capacitor")
            ax.yaxis.set_major_formatter(EngFormatter('V'))
        elif(which_string.lower() == allowed_strings[3] ):
            ax.set_title(title_prefix + "current wavefronts\n in Capacitor")
            ax.yaxis.set_major_formatter(EngFormatter('A'))
        else:
            raise ValueError(f"Incorrect plotting choice /, {which_string} is not a valid option. Optiond are: \n {allowed_strings}")
        
        ax.step(data_output_ordered.Time,get_func(which_string),where='post')

def make_time_interconnect_all(data_output_ordered: Data_Output_Storage_Ordered,is_integrated :bool = True,**kwargs):
    """Plots all interconnect time waveforms of an interface/ orderd data.

    :param data_output_ordered: data to be plotted. Can be interface or ordered data.
    :type data_output_ordered: Data_Output_Storage_Ordered
    :param is_integrated: If the wavefrom must represent the 'change' or 'accumulation of changes' of the data selected to be plotted, default is True
    :type is_integrated: bool, optional
    :return: the matplotlib Figure and Axes objects created in this function (if created)
    :rtype: tuple( fig , ax )
    :**kwargs for figure creation**:
        - **ax** (*Dict(Axes)*) - Whether to create a subpot or use exsiting subplot axes.If left blank default is 'False' and subplot is created internally.If axes are provided, the must be of a matplotlib.pyplot.subplot_mosaic() form.The labels for these axes must inculde: 
            - 'VL' axis for inductor voltage
            - 'VC' axis for capcitor voltage
            - 'IL' axis for inductor current
            - 'IC' axis for capacitor current
        - **fig_size** (*tuple of ints*) - The size of the figure. Default is (10, 8).
        
    .. code-block::

        from Wavefront_Generation import Full_Cycle
        from Wavefront_Plotting import make_time_interconnect_all
        import matplotlib.pyplot as plt

        # simulate interface
        interface = Full_Cycle(L_time='8' , C_time='7', L_impedance = '500', C_impedance = '2')

        # plot all interconnect time waveforms
        fig,ax = make_time_interconnect_all(interface)

        # plot the 'change' in those waveforms
        fig2,ax2 = make_time_interconnect_all(interface,False)

        plt.show()
        
    """
    
    data_output_ordered = handle_interface_to_ordered(data_output_ordered)
    
    default_make_kwargs : dict = {'ax':False,
                                  'fig_size':(10,8)}
    
    make_kwargs = handle_default_kwargs(kwargs,default_make_kwargs)
    
    if (make_kwargs['ax'] == False):
        fig, ax = plt.subplot_mosaic([['VL','VC'],
                                      ['IL','IC']])
    else:
        ax = make_kwargs['ax']
        fig = ax['VL'].get_figure()
        
    fig.set_size_inches(make_kwargs['fig_size'])
    
    if (is_integrated):
        fig.suptitle(f"Interconnect Time Waveforms")
    else:
        fig.suptitle(f"Interconnect Change Time Waveforms")

    plot_time_interconnect(data_output_ordered,ax['VL'],"Voltage Inductor", is_integrated)
    plot_time_interconnect(data_output_ordered,ax['IL'],"Current Inductor", is_integrated)
    plot_time_interconnect(data_output_ordered,ax['VC'],"Voltage Capacitor", is_integrated)
    plot_time_interconnect(data_output_ordered,ax['IC'],"Current Capacitor", is_integrated)
    
    if (make_kwargs['ax'] == False):
        return fig,ax

def make_time_wavefronts_all(data_output_ordered : Data_Output_Storage_Ordered, is_Inductor :bool,is_integrated: bool = True, **kwargs ):
    """Plots the wavefront time beahviour of a particualr transmission line. 
    Both sending and returning, current and voltage wavefront time behaviour is shown

    :param data_output_ordered:  data to be plotted. Can be interface or ordered data.
    :type data_output_ordered: Data_Output_Storage_Ordered or Data_Interface_Storage
    :param is_Inductor: if the inductor or capacitor wavefronts must be plot.
    :type is_Inductor: bool
    :param is_integrated: if the individual wavefront value or an accumulation of these values msut be shown, defaults to True
    :type is_integrated: bool, optional
    :return: the matplotlib Figure and Axes objects created in this function (if created)
    :rtype: tuple( fig , ax )
    :**kwargs for figure creation**:
        - **ax** (*Dict(Axes)*) - Whether to create a subpot or use exsiting subplot axes.If left blank default is 'False' and subplot is created internally.If axes are provided, the must be of a matplotlib.pyplot.subplot_mosaic() form.The labels for these axes must inculde: 
            - 'VS' axis for sending voltage
            - 'VR' axis for returning voltage
            - 'IS' axis for sending current
            - 'IR' axis for returning current
        - **fig_size** (*tuple of ints*) - The size of the figure. Default is (10, 8).
        
    .. code-block::
    
        from Wavefront_Generation import Full_Cycle
        from Wavefront_Plotting import make_time_wavefronts_all
        import matplotlib.pyplot as plt

        # Example: the accumulated wavefront behaviour over time between the capacitor and inductor
        # ==========================================================================================

        # simulate interface
        interface = Full_Cycle(L_time='7' , C_time='3.4', L_impedance = '654', C_impedance = '2.5')

        # plot accumulation wavefront activity for inductor
        fig,ax = make_time_wavefronts_all(interface,True,True)

        # plot the accumulation wavefront activity for capacitor
        # here we just pass the ax object as a kwarg so that it is plotted on the same axes
        make_time_wavefronts_all(interface,False,True,ax=ax)

        # rename the auto generated suptitle
        fig.suptitle('Comparison between accumulated wavefronts over time in each transmission line')

        # use the key word to set titles of each axis independantly 
        ax['VS'].set_title('Sending Voltage Wavefronts')
        ax['VR'].set_title('Returning Voltage Wavefronts')
        ax['IS'].set_title('Sending Current Wavefronts')
        ax['IR'].set_title('Returning Current Wavefronts')

        # plot a legend for all axes
        for ax_i in ax.values(): 
            ax_i.legend(['Inductor', 'Capacitor'])

        plt.show()
    """
    
    
    data_output_ordered = handle_interface_to_ordered(data_output_ordered)

    default_make_kwargs : dict = {'ax':False,
                                  'fig_size':(12,10)}
    
    make_kwargs = handle_default_kwargs(kwargs, default_make_kwargs)
    
    if (make_kwargs['ax'] == False):
        fig, ax = plt.subplot_mosaic([['VS','IS' ],
                                      ['VR','IR']])
    else:
        ax = make_kwargs['ax']
        fig = ax['VS'].get_figure()
    
    fig.set_size_inches(make_kwargs['fig_size'])
    
    if (is_Inductor):
        title_prefix = 'Inductor'
        plot_time_wavefronts(data_output_ordered,ax['VS'],"voltage inductor",True, is_integrated)
        plot_time_wavefronts(data_output_ordered,ax['IS'],"current inductor",True, is_integrated)
        plot_time_wavefronts(data_output_ordered,ax['VR'],"voltage inductor",False, is_integrated)
        plot_time_wavefronts(data_output_ordered,ax['IR'],"current inductor",False, is_integrated)
    else:
        title_prefix = 'Capacitor'
        plot_time_wavefronts(data_output_ordered,ax['VS'],"voltage capacitor",True, is_integrated)
        plot_time_wavefronts(data_output_ordered,ax['IS'],"current capacitor",True, is_integrated)
        plot_time_wavefronts(data_output_ordered,ax['VR'],"voltage capacitor",False, is_integrated)
        plot_time_wavefronts(data_output_ordered,ax['IR'],"current capacitor",False, is_integrated)
    
    fig.suptitle(title_prefix + " Wavefronts Time Behaviour")
    
    if (make_kwargs['ax'] == False):
        return (fig, ax)
    
    
    
    
    

def plot_time_interconnect_3(data_output_merged : Data_Output_Storage, data_output_ordered : Data_Output_Storage_Ordered, which_string : str):
    
    padwidth = 15
    
    fig, ax = plt.subplot_mosaic([['A','C'],['B','C']])
    
    plot_time_interconnect(data_output_ordered,ax['A'],which_string)
    plot_time_interconnect(data_output_ordered,ax['B'],which_string,True)
    plot_fanout_interconnect(data_output_merged,ax['C'],which_string)

    for i,index in enumerate(data_output_ordered.Indexes):
        if(i  == 0):
            pass
        else:
            x1 = data_output_ordered.Indexes[i-1][0]+ padwidth
            y1 = data_output_ordered.Indexes[i-1][1]+ padwidth
            
            x2 = index[0]+ padwidth
            y2 = index[1]+ padwidth
            ax['C'].plot([y1,y2],[x1,x2],'black',marker='o')
            
    return fig, ax 

    
def plot_time_interconnect_3_both(data_output_merged : Data_Output_Storage
                                  , data_output_ordered : Data_Output_Storage_Ordered
                                  , data_output_merged_2 : Data_Output_Storage
                                  , data_output_ordered_2 : Data_Output_Storage_Ordered
                                  , which_string : str):
    
    padwidth = 15
    
    fig, ax = plt.subplot_mosaic([['A','C','D'],['B','C','D']])
    
    plot_time_interconnect(data_output_ordered,ax['A'],which_string)
    plot_time_interconnect(data_output_ordered_2,ax['A'],which_string)
    
    plot_time_interconnect(data_output_ordered,ax['B'],which_string,True)
    plot_time_interconnect(data_output_ordered_2,ax['B'],which_string,True)
    
    plot_fanout_interconnect(data_output_merged,ax['C'],which_string," self 1")
    plot_fanout_interconnect(data_output_merged_2,ax['D'],which_string," self 2")

    for i,index in enumerate(data_output_ordered.Indexes):
        if(i  == 0):
            pass
        else:
            x1 = data_output_ordered.Indexes[i-1][0]+ padwidth
            y1 = data_output_ordered.Indexes[i-1][1]+ padwidth
            
            x2 = index[0]+ padwidth
            y2 = index[1]+ padwidth
            ax['C'].plot([y1,y2],[x1,x2],'black',marker='.')
            
    for i,index in enumerate(data_output_ordered_2.Indexes):
        if(i  == 0):
            pass
        else:
            x1 = data_output_ordered_2.Indexes[i-1][0]+ padwidth
            y1 = data_output_ordered_2.Indexes[i-1][1]+ padwidth
            
            x2 = index[0]+ padwidth
            y2 = index[1]+ padwidth
            ax['D'].plot([y1,y2],[x1,x2],'black',marker='.')
            
    return fig, ax 

def plot_time_interconnect_4(data_output_ordered: Data_Output_Storage_Ordered):
    
    fig, ax = plt.subplot_mosaic([['A','B'],['C','D']])
    
    ax['A'].set_title("Inductor voltage at Interconnect")
    ax['A'].step(data_output_ordered.Time,np.cumsum(data_output_ordered.Voltage_Interconnect_Inductor),where='post')
    
    ax['C'].set_title("Inductor current at Interconnect")
    ax['C'].step(data_output_ordered.Time,np.cumsum(data_output_ordered.Current_Interconnect_Inductor),where='post')
    
    ax['B'].set_title("Capacitor voltage at Interconnect")
    ax['B'].step(data_output_ordered.Time,np.cumsum(data_output_ordered.Voltage_Interconnect_Capacitor),where='post')
    
    ax['D'].set_title("Capacitor current at Interconnect")
    ax['D'].step(data_output_ordered.Time,np.cumsum(data_output_ordered.Current_Interconnect_Capacitor),where='post')
    
    return fig, ax

def plot_time_interconnect_4_wavefronts(data_output_ordered: Data_Output_Storage_Ordered):
    
    fig, ax = plt.subplot_mosaic([['A','B'],['C','D']])
    
    ax['A'].set_title("Inductor voltage change at Interconnect")
    ax['A'].step(data_output_ordered.Time,data_output_ordered.Voltage_Interconnect_Inductor,where='post')
    
    ax['C'].set_title("Inductor current change at Interconnect")
    ax['C'].step(data_output_ordered.Time,data_output_ordered.Current_Interconnect_Inductor,where='post')
    
    ax['B'].set_title("Capacitor voltage change at Interconnect")
    ax['B'].step(data_output_ordered.Time,data_output_ordered.Voltage_Interconnect_Capacitor,where='post')
    
    ax['D'].set_title("Capacitor current change at Interconnect")
    ax['D'].step(data_output_ordered.Time,data_output_ordered.Current_Interconnect_Capacitor,where='post')
    
    return fig, ax

def plot_time_interconnect_4_both(data_output_ordered: Data_Output_Storage_Ordered,data_output_ordered_2: Data_Output_Storage_Ordered):
    
    fig, ax = plt.subplot_mosaic([['A','B'],['C','D']])
    
    ax['A'].set_title("Inductor voltage at Interconnect")
    ax['A'].step(data_output_ordered.Time,np.cumsum(data_output_ordered.Voltage_Interconnect_Inductor),where='post')
    ax['A'].step(data_output_ordered_2.Time,np.cumsum(data_output_ordered_2.Voltage_Interconnect_Inductor),where='post')
    
    ax['C'].set_title("Inductor current at Interconnect")
    ax['C'].step(data_output_ordered.Time,np.cumsum(data_output_ordered.Current_Interconnect_Inductor),where='post')
    ax['C'].step(data_output_ordered_2.Time,np.cumsum(data_output_ordered_2.Current_Interconnect_Inductor),where='post')
    
    ax['B'].set_title("Capacitor voltage at Interconnect")
    ax['B'].step(data_output_ordered.Time,np.cumsum(data_output_ordered.Voltage_Interconnect_Capacitor),where='post')
    ax['B'].step(data_output_ordered_2.Time,np.cumsum(data_output_ordered_2.Voltage_Interconnect_Capacitor),where='post')
    
    ax['D'].set_title("Capacitor current at Interconnect")
    ax['D'].step(data_output_ordered.Time,np.cumsum(data_output_ordered.Current_Interconnect_Capacitor),where='post')
    ax['D'].step(data_output_ordered_2.Time,np.cumsum(data_output_ordered_2.Current_Interconnect_Capacitor),where='post')
    
    return fig, ax

def plot_time_interconnect_4_wavefronts_both(data_output_ordered: Data_Output_Storage_Ordered, data_output_ordered_2: Data_Output_Storage_Ordered):
    
    fig, ax = plt.subplot_mosaic([['A','B'],['C','D']])
    
    ax['A'].set_title("Inductor voltage change at Interconnect")
    ax['A'].step(data_output_ordered.Time,data_output_ordered.Voltage_Interconnect_Inductor,where='post')
    ax['A'].step(data_output_ordered_2.Time,data_output_ordered_2.Voltage_Interconnect_Inductor,where='post')
    
    ax['C'].set_title("Inductor current change at Interconnect")
    ax['C'].step(data_output_ordered.Time,data_output_ordered.Current_Interconnect_Inductor,where='post')
    ax['C'].step(data_output_ordered_2.Time,data_output_ordered_2.Current_Interconnect_Inductor,where='post')
    
    ax['B'].set_title("Capacitor voltage change at Interconnect")
    ax['B'].step(data_output_ordered.Time,data_output_ordered.Voltage_Interconnect_Capacitor,where='post')
    ax['B'].step(data_output_ordered_2.Time,data_output_ordered_2.Voltage_Interconnect_Capacitor,where='post')
    
    ax['D'].set_title("Capacitor current change at Interconnect")
    ax['D'].step(data_output_ordered.Time,data_output_ordered.Current_Interconnect_Capacitor,where='post')
    ax['D'].step(data_output_ordered_2.Time,data_output_ordered_2.Current_Interconnect_Capacitor,where='post')
    
    return fig, ax

def plot_time_wavefronts_all(data_output : Data_Output_Storage, what_to_plot : str):
    fig_sub, ax_sub = plt.subplots(2,3)

    fig_sub.suptitle("Wavefronts of the "+ what_to_plot)
     
    ax_sub[0,0].set_title("sending voltage")
    ax_sub[0,0].step(np.ma.masked_where(data_output.Time == 0 ,data_output.Time), np.ma.masked_where(data_output.Time == 0 ,data_output.get_sending_wavefronts_magnitudes("voltage "+ what_to_plot)),where='post')
    ax_sub[0,1].set_title("returning voltage")
    ax_sub[0,1].step(np.ma.masked_where(data_output.Time == 0 ,data_output.Time), np.ma.masked_where(data_output.Time == 0 ,data_output.get_returning_wavefronts_magnitudes("voltage "+ what_to_plot)),where='post')
    ax_sub[0,2].set_title("sending + returning voltage")
    ax_sub[0,2].step(np.ma.masked_where(data_output.Time == 0 ,data_output.Time), np.ma.masked_where(data_output.Time == 0 ,data_output.get_returning_wavefronts_magnitudes("voltage "+ what_to_plot)+data_output.get_sending_wavefronts_magnitudes("voltage "+ what_to_plot)),where='post')

    ax_sub[1,0].set_title("sending current")
    ax_sub[1,0].step(np.ma.masked_where(data_output.Time == 0 ,data_output.Time), np.ma.masked_where(data_output.Time == 0 ,data_output.get_sending_wavefronts_magnitudes("current " + what_to_plot)),where='post')
    ax_sub[1,1].set_title("returning current")
    ax_sub[1,1].step(np.ma.masked_where(data_output.Time == 0 ,data_output.Time), np.ma.masked_where(data_output.Time == 0 ,data_output.get_returning_wavefronts_magnitudes("current " + what_to_plot)),where='post')
    ax_sub[1,2].set_title("sending + returning current")
    ax_sub[1,2].step(np.ma.masked_where(data_output.Time == 0 ,data_output.Time), np.ma.masked_where(data_output.Time == 0 ,data_output.get_returning_wavefronts_magnitudes("current " + what_to_plot)+data_output.get_sending_wavefronts_magnitudes("current " + what_to_plot)),where='post')
    
    return fig_sub, ax_sub

def plot_time_wavefronts_all_both(data_output : Data_Output_Storage, data_output_2: Data_Output_Storage, what_to_plot : str):
    fig_sub, ax_sub = plt.subplots(2,3)

    fig_sub.suptitle("Wavefronts of the "+ what_to_plot)
     
    ax_sub[0,0].set_title("sending voltage")
    ax_sub[0,0].step(np.ma.masked_where(data_output.Time == 0 ,data_output.Time), np.ma.masked_where(data_output.Time == 0 ,data_output.get_sending_wavefronts_magnitudes("voltage "+ what_to_plot)),where='post')
    ax_sub[0,0].step(np.ma.masked_where(data_output_2.Time == 0 ,data_output_2.Time), np.ma.masked_where(data_output_2.Time == 0 ,data_output_2.get_sending_wavefronts_magnitudes("voltage "+ what_to_plot)),where='post')
    ax_sub[0,1].set_title("returning voltage")
    ax_sub[0,1].step(np.ma.masked_where(data_output.Time == 0 ,data_output.Time), np.ma.masked_where(data_output.Time == 0 ,data_output.get_returning_wavefronts_magnitudes("voltage "+ what_to_plot)),where='post')
    ax_sub[0,1].step(np.ma.masked_where(data_output_2.Time == 0 ,data_output_2.Time), np.ma.masked_where(data_output_2.Time == 0 ,data_output_2.get_returning_wavefronts_magnitudes("voltage "+ what_to_plot)),where='post')
    ax_sub[0,2].set_title("sending + returning voltage")
    ax_sub[0,2].step(np.ma.masked_where(data_output.Time == 0 ,data_output.Time), np.ma.masked_where(data_output.Time == 0 ,data_output.get_returning_wavefronts_magnitudes("voltage "+ what_to_plot)+data_output.get_sending_wavefronts_magnitudes("voltage "+ what_to_plot)),where='post')
    ax_sub[0,2].step(np.ma.masked_where(data_output_2.Time == 0 ,data_output_2.Time), np.ma.masked_where(data_output_2.Time == 0 ,data_output_2.get_returning_wavefronts_magnitudes("voltage "+ what_to_plot)+data_output_2.get_sending_wavefronts_magnitudes("voltage "+ what_to_plot)),where='post')

    ax_sub[1,0].set_title("sending current")
    ax_sub[1,0].step(np.ma.masked_where(data_output.Time == 0 ,data_output.Time), np.ma.masked_where(data_output.Time == 0 ,data_output.get_sending_wavefronts_magnitudes("current " + what_to_plot)),where='post')
    ax_sub[1,0].step(np.ma.masked_where(data_output_2.Time == 0 ,data_output_2.Time), np.ma.masked_where(data_output_2.Time == 0 ,data_output_2.get_sending_wavefronts_magnitudes("current " + what_to_plot)),where='post')
    ax_sub[1,1].set_title("returning current")
    ax_sub[1,1].step(np.ma.masked_where(data_output.Time == 0 ,data_output.Time), np.ma.masked_where(data_output.Time == 0 ,data_output.get_returning_wavefronts_magnitudes("current " + what_to_plot)),where='post')
    ax_sub[1,1].step(np.ma.masked_where(data_output_2.Time == 0 ,data_output_2.Time), np.ma.masked_where(data_output_2.Time == 0 ,data_output_2.get_returning_wavefronts_magnitudes("current " + what_to_plot)),where='post')
    ax_sub[1,2].set_title("sending + returning current")
    ax_sub[1,2].step(np.ma.masked_where(data_output.Time == 0 ,data_output.Time), np.ma.masked_where(data_output.Time == 0 ,data_output.get_returning_wavefronts_magnitudes("current " + what_to_plot)+data_output.get_sending_wavefronts_magnitudes("current " + what_to_plot)),where='post')
    ax_sub[1,2].step(np.ma.masked_where(data_output_2.Time == 0 ,data_output_2.Time), np.ma.masked_where(data_output_2.Time == 0 ,data_output_2.get_returning_wavefronts_magnitudes("current " + what_to_plot)+data_output_2.get_sending_wavefronts_magnitudes("current " + what_to_plot)),where='post')
    
    return fig_sub, ax_sub

def plot_refelction_diagram(Data_Input: Data_Input_Storage, Data_Output_Ordered : Data_Output_Storage_Ordered, stop_time, ax, mutiple_ticks : bool = True,**input_kwargs):
    
    kwargs = dict([('saving_folder','plots/'),('is_saving',False),('face_colour','xkcd:grey'),
                   ('cap_sending_style','r'),('cap_returning_style','r'),
                   ('ind_sending_style','b'),('ind_returning_style','b')])
    
    for key, item in input_kwargs.items():
        if(kwargs.get(key) is None):
            raise Exception(f"No setting found for {key}, here are the possible options: \n{kwargs}")
        else:
            kwargs[key] = item
    
    ax.set_facecolor(kwargs['face_colour'])
    ax.set_xlim([-1,1])
    ax.set_xticks([-1,-0.5,0,0.5,1])
    ax.set_xticklabels(["$\mathregular{\ell_C}$","Capacitor","Interface","Inductor","$\mathregular{\ell_L}$"],fontsize='large')
    
    C_Time = str(2*Data_Input.Capacitor_Time)
    C_impedance = str(Data_Input.Capacitor_Impedance)
    
    L_Time = str(2*Data_Input.Inductor_Time)
    L_impedance = str(Data_Input.Inductor_Impedance)

    ax.axhline(linewidth=1, color='k')
    ax.axvline(linewidth=1, color='k')
    
    ax.plot([-1,-1],[0,stop_time],'k')
    ax.plot([1,1],[0,stop_time],'k')
    #ax.plot([-1,1],[stop_time,stop_time],'k')
    
    #ax.get_xaxis().set_visible(False)
    ax2 = ax.secondary_yaxis('right')
    ax.set_xticks = ([])
    ax2.set_xticks = ([])
    ax.set_xticklabels = ('')
    ax2.set_xticklabels = ('')
    
    ax.set_ylabel('Capacitor Time Delay = '+ C_Time, fontsize = 'large')
    ax2.set_ylabel('Inductor Time Delay = '+ L_Time, fontsize = 'large')
    #ax.yaxis.set_ticks(np.arange(0, stop_time, 1))
    #ax2.yaxis.set_ticks(np.arange(0, stop_time, 1))
    
    ax.set_title(f'Reflection Diagram for \n Capacitor Transit Time = {C_Time}s, Inductor Transit Time = {L_Time}s  ', fontsize = 'large')
    # ax.set_xlabel('Relative distance down Transmission Line')
    
    if(mutiple_ticks):
        ax.yaxis.set_major_locator(MultipleLocator(float(C_Time)))
        ax2.yaxis.set_major_locator(MultipleLocator(float(L_Time)))
        #ax.yaxis.set_major_formatter(FormatStrFormatter('%d'))

        # For the minor ticks, use no labels; default NullFormatter.
        ax.yaxis.set_minor_locator(MultipleLocator(float(C_Time)/2))
        ax2.yaxis.set_minor_locator(MultipleLocator(float(L_Time)/2))
    
    ax.set_ylim(0,stop_time)


    for wave in Data_Output_Ordered.Wavefronts_Sending_Capacitor:

        x1 = -wave.position_start
        x2 = -wave.position_end

        y1 = wave.time_start
        y2 = wave.time_end

        if(wave.time_start <=stop_time):
            ax.plot([x1,x2],[y1,y2],kwargs['cap_sending_style'])
            
    for wave in Data_Output_Ordered.Wavefronts_Returning_Capacitor:

        x1 = -wave.position_start
        x2 = -wave.position_end

        y1 = wave.time_start
        y2 = wave.time_end

        if(wave.time_start <=stop_time):
            ax.plot([x1,x2],[y1,y2],kwargs['cap_returning_style'])


    for wave in Data_Output_Ordered.Wavefronts_Sending_Inductor:

        x1 = wave.position_start
        x2 = wave.position_end

        y1 = wave.time_start
        y2 = wave.time_end

        if(wave.time_start <=stop_time):
            ax.plot([x1,x2],[y1,y2],kwargs['ind_sending_style'])
            
    for wave in Data_Output_Ordered.Wavefronts_Returning_Inductor:

        x1 = wave.position_start
        x2 = wave.position_end

        y1 = wave.time_start
        y2 = wave.time_end

        if(wave.time_start <=stop_time):
            ax.plot([x1,x2],[y1,y2],kwargs['ind_returning_style'])
            
    plt.tight_layout()
    file_name = kwargs['saving_folder']+f'Refelction_TL_{2*Data_Input.Inductor_Time}_TC_{2*Data_Input.Capacitor_Time}_stop_time_{stop_time}.png'
    if kwargs['is_saving']:
        plt.savefig(file_name)
            
def plot_refelction_diagram_specific(Data_Input: Data_Input_Storage, Data_Output_Ordered : Data_Output_Storage_Ordered, is_current, stop_time, ax, mutiple_ticks : bool = True):
    
    C_Time = str(2*Data_Input.Capacitor_Time)
    C_impedance = str(Data_Input.Capacitor_Impedance)
    
    L_Time = str(2*Data_Input.Inductor_Time)
    L_impedance = str(Data_Input.Inductor_Impedance)
    
    ax.axhline(linewidth=1, color='k')
    ax.axvline(linewidth=1, color='k')
    
    ax.plot([-1,-1],[0,stop_time],'k')
    ax.plot([1,1],[0,stop_time],'k')
    #ax.plot([-1,1],[stop_time,stop_time],'k')
    
    #ax.get_xaxis().set_visible(False)
    ax2 = ax.secondary_yaxis('right')
    ax.set_xticks = ([])
    ax2.set_xticks = ([])
    ax.set_xticklabels = ('')
    ax2.set_xticklabels = ('')
    
    ax.set_ylabel('Capacitor Time Delay = '+ C_Time, fontsize = 'large')
    ax2.set_ylabel('Inductor Time Delay = '+ L_Time, fontsize = 'large')
    #ax.yaxis.set_ticks(np.arange(0, stop_time, 1))
    #ax2.yaxis.set_ticks(np.arange(0, stop_time, 1))
    
    if(is_current):
        ax.set_title('Current Reflection Diagarm \n Capacitor Impedance = '+ C_impedance +'Ω, Inductor Impedance = ' + L_impedance+ 'Ω', fontsize = 'large')
    else:
        ax.set_title('Votlage Reflection Diagarm \n Capacitor Impedance = '+ C_impedance +'Ω, Inductor Impedance = ' + L_impedance+ 'Ω', fontsize = 'large')
        
    # ax.set_xlabel('Relative distance down Transmission Line')
    
    if(mutiple_ticks):
        ax.yaxis.set_major_locator(MultipleLocator(float(C_Time)))
        ax2.yaxis.set_major_locator(MultipleLocator(float(L_Time)))
        #ax.yaxis.set_major_formatter(FormatStrFormatter('%d'))

        # For the minor ticks, use no labels; default NullFormatter.
        ax.yaxis.set_minor_locator(MultipleLocator(float(C_Time)/2))
        ax2.yaxis.set_minor_locator(MultipleLocator(float(L_Time)/2))
    
    ax.set_ylim(0,stop_time)
    
    # Setup Colour Map
    max_cap_s = 0
    min_cap_s = 0
    max_ind_s = 0
    min_ind_s = 0
    
    max_cap_r = 0
    min_cap_r = 0
    max_ind_r = 0
    min_ind_r = 0
    
    boundary = 0 
    
    if(is_current):
        max_cap_s = abs(np.max(Data_Output_Ordered.get_sending_wavefronts_magnitudes("current capacitor")))
        min_cap_s = abs(np.min(Data_Output_Ordered.get_sending_wavefronts_magnitudes("current capacitor")))
        max_ind_s = abs(np.max(Data_Output_Ordered.get_sending_wavefronts_magnitudes("current inductor")))
        min_ind_s = abs(np.min(Data_Output_Ordered.get_sending_wavefronts_magnitudes("current inductor")))

        max_cap_r = abs(np.max(Data_Output_Ordered.get_returning_wavefronts_magnitudes("current capacitor")))
        min_cap_r = abs(np.min(Data_Output_Ordered.get_returning_wavefronts_magnitudes("current capacitor")))
        max_ind_r = abs(np.max(Data_Output_Ordered.get_returning_wavefronts_magnitudes("current inductor")))
        min_ind_r = abs(np.min(Data_Output_Ordered.get_returning_wavefronts_magnitudes("current inductor")))
    else:
        max_cap_s = abs(np.max(Data_Output_Ordered.get_sending_wavefronts_magnitudes("voltage capacitor")))
        min_cap_s = abs(np.min(Data_Output_Ordered.get_sending_wavefronts_magnitudes("voltage capacitor")))
        max_ind_s = abs(np.max(Data_Output_Ordered.get_sending_wavefronts_magnitudes("voltage inductor")))
        min_ind_s = abs(np.min(Data_Output_Ordered.get_sending_wavefronts_magnitudes("voltage inductor")))

        max_cap_r = abs(np.max(Data_Output_Ordered.get_returning_wavefronts_magnitudes("voltage capacitor")))
        min_cap_r = abs(np.min(Data_Output_Ordered.get_returning_wavefronts_magnitudes("voltage capacitor")))
        max_ind_r = abs(np.max(Data_Output_Ordered.get_returning_wavefronts_magnitudes("voltage inductor")))
        min_ind_r = abs(np.min(Data_Output_Ordered.get_returning_wavefronts_magnitudes("voltage inductor")))
        
    boundary = max(max_cap_s,min_cap_s,max_ind_s,min_ind_s,max_cap_r,min_cap_r,max_ind_r,min_ind_r)
    
    colour_map = mpl.cm.seismic
    norm = mpl.colors.Normalize(vmin=-boundary, vmax=boundary)
    
    for wave in Data_Output_Ordered.Wavefronts_Sending_Capacitor:

        x1 = -wave.position_start
        x2 = -wave.position_end

        y1 = wave.time_start
        y2 = wave.time_end
        
        mag = 0
        
        if(is_current):
            mag = float(wave.magnitude_current)
        else:
            mag = float(wave.magnitude_voltage)

        if(wave.time_start <=stop_time):
            ax.plot([x1,x2],[y1,y2],c=colour_map(norm(mag)))
            # ax.plot([(x2-x1)/2],[y1 + (y2-y1)/2], marker ='o',c=colour_map(norm(mag)),markersize=15)
            
    for wave in Data_Output_Ordered.Wavefronts_Returning_Capacitor:

        x1 = -wave.position_start
        x2 = -wave.position_end

        y1 = wave.time_start
        y2 = wave.time_end
        
        mag = 0
        
        if(is_current):
            mag = float(wave.magnitude_current)
        else:
            mag = float(wave.magnitude_voltage)

        if(wave.time_start <=stop_time):
            ax.plot([x1,x2],[y1,y2],c=colour_map(norm(mag)))
            # ax.plot([-(x2-x1)/2],[y1 + (y2-y1)/2], marker ='o',c=colour_map(norm(mag)),markersize=15)

    # Inductor Wavefronts
    for wave in Data_Output_Ordered.Wavefronts_Sending_Inductor:

        x1 = wave.position_start
        x2 = wave.position_end

        y1 = wave.time_start
        y2 = wave.time_end

        mag = 0
        
        if(is_current):
            mag = float(wave.magnitude_current)
        else:
            mag = float(wave.magnitude_voltage)

        if(wave.time_start <=stop_time):
            ax.plot([x1,x2],[y1,y2],c=colour_map(norm(mag)))
            # ax.plot([(x2-x1)/2],[y1 + (y2-y1)/2], marker ='o',c=colour_map(norm(mag)),markersize=15)
            
    for wave in Data_Output_Ordered.Wavefronts_Returning_Inductor:

        x1 = wave.position_start
        x2 = wave.position_end

        y1 = wave.time_start
        y2 = wave.time_end

        mag = 0
        
        if(is_current):
            mag = float(wave.magnitude_current)
        else:
            mag = float(wave.magnitude_voltage)

        if(wave.time_start <=stop_time):
            ax.plot([x1,x2],[y1,y2],c=colour_map(norm(mag)))
            # ax.plot([-(x2-x1)/2],[y1 + (y2-y1)/2], marker ='o',c=colour_map(norm(mag)),markersize=15)      
            
def plot_refelction_diagram_sending(Data_Input: Data_Input_Storage, Data_Output_Ordered : Data_Output_Storage_Ordered, is_current, stop_time, ax, mutiple_ticks : bool = True):
    
        
    non_active_wavefront_colour = 'xkcd:dark grey'
    
    C_Time = str(2*Data_Input.Capacitor_Time)
    C_impedance = str(Data_Input.Capacitor_Impedance)
    
    L_Time = str(2*Data_Input.Inductor_Time)
    L_impedance = str(Data_Input.Inductor_Impedance)
    
    ax.axhline(linewidth=1, color='k')
    ax.axvline(linewidth=1, color='k')
    
    ax.plot([-1,-1],[0,stop_time],'k')
    ax.plot([1,1],[0,stop_time],'k')
    #ax.plot([-1,1],[stop_time,stop_time],'k')
    
    #ax.get_xaxis().set_visible(False)
    ax2 = ax.secondary_yaxis('right')
    ax.set_xticks = ([])
    ax2.set_xticks = ([])
    ax.set_xticklabels = ('')
    ax2.set_xticklabels = ('')
    
    ax.set_ylabel('Capacitor Time Delay = '+ C_Time, fontsize = 'large')
    ax2.set_ylabel('Inductor Time Delay = '+ L_Time, fontsize = 'large')
    #ax.yaxis.set_ticks(np.arange(0, stop_time, 1))
    #ax2.yaxis.set_ticks(np.arange(0, stop_time, 1))
    
    if(is_current):
        ax.set_title('Sending Current Reflection Diagarm \n Capacitor Impedance = '+ C_impedance +'Ω, Inductor Impedance = ' + L_impedance+ 'Ω', fontsize = 'large')
    else:
        ax.set_title('Sending Votlage Reflection Diagarm \n Capacitor Impedance = '+ C_impedance +'Ω, Inductor Impedance = ' + L_impedance+ 'Ω', fontsize = 'large')
        
    # ax.set_xlabel('Relative distance down Transmission Line')
    
    if(mutiple_ticks):
        ax.yaxis.set_major_locator(MultipleLocator(float(C_Time)))
        ax2.yaxis.set_major_locator(MultipleLocator(float(L_Time)))
        #ax.yaxis.set_major_formatter(FormatStrFormatter('%d'))

        # For the minor ticks, use no labels; default NullFormatter.
        ax.yaxis.set_minor_locator(MultipleLocator(float(C_Time)/2))
        ax2.yaxis.set_minor_locator(MultipleLocator(float(L_Time)/2))
    
    ax.set_ylim(0,stop_time)
    
    # Setup Colour Map
    max_cap_s = 0
    min_cap_s = 0
    max_ind_s = 0
    min_ind_s = 0
    
    max_cap_r = 0
    min_cap_r = 0
    max_ind_r = 0
    min_ind_r = 0
    
    boundary = 0 
    
    if(is_current):
        max_cap_s = abs(np.max(Data_Output_Ordered.get_sending_wavefronts_magnitudes("current capacitor")))
        min_cap_s = abs(np.min(Data_Output_Ordered.get_sending_wavefronts_magnitudes("current capacitor")))
        max_ind_s = abs(np.max(Data_Output_Ordered.get_sending_wavefronts_magnitudes("current inductor")))
        min_ind_s = abs(np.min(Data_Output_Ordered.get_sending_wavefronts_magnitudes("current inductor")))

        max_cap_r = abs(np.max(Data_Output_Ordered.get_returning_wavefronts_magnitudes("current capacitor")))
        min_cap_r = abs(np.min(Data_Output_Ordered.get_returning_wavefronts_magnitudes("current capacitor")))
        max_ind_r = abs(np.max(Data_Output_Ordered.get_returning_wavefronts_magnitudes("current inductor")))
        min_ind_r = abs(np.min(Data_Output_Ordered.get_returning_wavefronts_magnitudes("current inductor")))
    else:
        max_cap_s = abs(np.max(Data_Output_Ordered.get_sending_wavefronts_magnitudes("voltage capacitor")))
        min_cap_s = abs(np.min(Data_Output_Ordered.get_sending_wavefronts_magnitudes("voltage capacitor")))
        max_ind_s = abs(np.max(Data_Output_Ordered.get_sending_wavefronts_magnitudes("voltage inductor")))
        min_ind_s = abs(np.min(Data_Output_Ordered.get_sending_wavefronts_magnitudes("voltage inductor")))

        max_cap_r = abs(np.max(Data_Output_Ordered.get_returning_wavefronts_magnitudes("voltage capacitor")))
        min_cap_r = abs(np.min(Data_Output_Ordered.get_returning_wavefronts_magnitudes("voltage capacitor")))
        max_ind_r = abs(np.max(Data_Output_Ordered.get_returning_wavefronts_magnitudes("voltage inductor")))
        min_ind_r = abs(np.min(Data_Output_Ordered.get_returning_wavefronts_magnitudes("voltage inductor")))
        
    boundary = max(max_cap_s,min_cap_s,max_ind_s,min_ind_s,max_cap_r,min_cap_r,max_ind_r,min_ind_r)
    
    colour_map = mpl.cm.seismic
    norm = mpl.colors.Normalize(vmin=-boundary, vmax=boundary)
    
    for wave in Data_Output_Ordered.Wavefronts_Sending_Capacitor:

        x1 = -wave.position_start
        x2 = -wave.position_end

        y1 = wave.time_start
        y2 = wave.time_end
        
        mag = 0
        
        if(is_current):
            mag = float(wave.magnitude_current)
        else:
            mag = float(wave.magnitude_voltage)

        if(wave.time_start <=stop_time):
            ax.plot([x1,x2],[y1,y2],c=colour_map(norm(mag)),zorder=2)
            # ax.plot([(x2-x1)/2],[y1 + (y2-y1)/2], marker ='o',c=colour_map(norm(mag)),markersize=15)
            
    for wave in Data_Output_Ordered.Wavefronts_Returning_Capacitor:

        x1 = -wave.position_start
        x2 = -wave.position_end

        y1 = wave.time_start
        y2 = wave.time_end
        
        mag = 0
        
        if(is_current):
            mag = float(wave.magnitude_current)
        else:
            mag = float(wave.magnitude_voltage)

        if(wave.time_start <=stop_time):
            ax.plot([x1,x2],[y1,y2],c=non_active_wavefront_colour,linestyle='dashed',zorder=1)
            # ax.plot([-(x2-x1)/2],[y1 + (y2-y1)/2], marker ='o',c=colour_map(norm(mag)),markersize=15)

    # Inductor Wavefronts
    for wave in Data_Output_Ordered.Wavefronts_Sending_Inductor:

        x1 = wave.position_start
        x2 = wave.position_end

        y1 = wave.time_start
        y2 = wave.time_end

        mag = 0
        
        if(is_current):
            mag = float(wave.magnitude_current)
        else:
            mag = float(wave.magnitude_voltage)

        if(wave.time_start <=stop_time):
            ax.plot([x1,x2],[y1,y2],c=colour_map(norm(mag)),zorder=2)
            # ax.plot([(x2-x1)/2],[y1 + (y2-y1)/2], marker ='o',c=colour_map(norm(mag)),markersize=15)
            
    for wave in Data_Output_Ordered.Wavefronts_Returning_Inductor:

        x1 = wave.position_start
        x2 = wave.position_end

        y1 = wave.time_start
        y2 = wave.time_end

        mag = 0
        
        if(is_current):
            mag = float(wave.magnitude_current)
        else:
            mag = float(wave.magnitude_voltage)

        if(wave.time_start <=stop_time):
            ax.plot([x1,x2],[y1,y2],c=non_active_wavefront_colour,linestyle='dashed',zorder=1)
            # ax.plot([-(x2-x1)/2],[y1 + (y2-y1)/2], marker ='o',c=colour_map(norm(mag)),markersize=15)      

def plot_refelction_diagram_returning(Data_Input: Data_Input_Storage, Data_Output_Ordered : Data_Output_Storage_Ordered, is_current, stop_time, ax, mutiple_ticks : bool = True):
    
        
    non_active_wavefront_colour = 'xkcd:dark grey'
    
    C_Time = str(2*Data_Input.Capacitor_Time)
    C_impedance = str(Data_Input.Capacitor_Impedance)
    
    L_Time = str(2*Data_Input.Inductor_Time)
    L_impedance = str(Data_Input.Inductor_Impedance)
    
    ax.axhline(linewidth=1, color='k')
    ax.axvline(linewidth=1, color='k')
    
    ax.plot([-1,-1],[0,stop_time],'k')
    ax.plot([1,1],[0,stop_time],'k')
    #ax.plot([-1,1],[stop_time,stop_time],'k')
    
    #ax.get_xaxis().set_visible(False)
    ax2 = ax.secondary_yaxis('right')
    ax.set_xticks = ([])
    ax2.set_xticks = ([])
    ax.set_xticklabels = ('')
    ax2.set_xticklabels = ('')
    
    ax.set_ylabel('Capacitor Time Delay = '+ C_Time, fontsize = 'large')
    ax2.set_ylabel('Inductor Time Delay = '+ L_Time, fontsize = 'large')
    #ax.yaxis.set_ticks(np.arange(0, stop_time, 1))
    #ax2.yaxis.set_ticks(np.arange(0, stop_time, 1))
    
    if(is_current):
        ax.set_title('Returning Current Reflection Diagarm \n Capacitor Impedance = '+ C_impedance +'Ω, Inductor Impedance = ' + L_impedance+ 'Ω', fontsize = 'large')
    else:
        ax.set_title('Returning Votlage Reflection Diagarm \n Capacitor Impedance = '+ C_impedance +'Ω, Inductor Impedance = ' + L_impedance+ 'Ω', fontsize = 'large')
        
    # ax.set_xlabel('Relative distance down Transmission Line')
    
    if(mutiple_ticks):
        ax.yaxis.set_major_locator(MultipleLocator(float(C_Time)))
        ax2.yaxis.set_major_locator(MultipleLocator(float(L_Time)))
        #ax.yaxis.set_major_formatter(FormatStrFormatter('%d'))

        # For the minor ticks, use no labels; default NullFormatter.
        ax.yaxis.set_minor_locator(MultipleLocator(float(C_Time)/2))
        ax2.yaxis.set_minor_locator(MultipleLocator(float(L_Time)/2))
    
    ax.set_ylim(0,stop_time)
    
    # Setup Colour Map
    max_cap_s = 0
    min_cap_s = 0
    max_ind_s = 0
    min_ind_s = 0
    
    max_cap_r = 0
    min_cap_r = 0
    max_ind_r = 0
    min_ind_r = 0
    
    boundary = 0 
    
    if(is_current):
        max_cap_s = abs(np.max(Data_Output_Ordered.get_sending_wavefronts_magnitudes("current capacitor")))
        min_cap_s = abs(np.min(Data_Output_Ordered.get_sending_wavefronts_magnitudes("current capacitor")))
        max_ind_s = abs(np.max(Data_Output_Ordered.get_sending_wavefronts_magnitudes("current inductor")))
        min_ind_s = abs(np.min(Data_Output_Ordered.get_sending_wavefronts_magnitudes("current inductor")))

        max_cap_r = abs(np.max(Data_Output_Ordered.get_returning_wavefronts_magnitudes("current capacitor")))
        min_cap_r = abs(np.min(Data_Output_Ordered.get_returning_wavefronts_magnitudes("current capacitor")))
        max_ind_r = abs(np.max(Data_Output_Ordered.get_returning_wavefronts_magnitudes("current inductor")))
        min_ind_r = abs(np.min(Data_Output_Ordered.get_returning_wavefronts_magnitudes("current inductor")))
    else:
        max_cap_s = abs(np.max(Data_Output_Ordered.get_sending_wavefronts_magnitudes("voltage capacitor")))
        min_cap_s = abs(np.min(Data_Output_Ordered.get_sending_wavefronts_magnitudes("voltage capacitor")))
        max_ind_s = abs(np.max(Data_Output_Ordered.get_sending_wavefronts_magnitudes("voltage inductor")))
        min_ind_s = abs(np.min(Data_Output_Ordered.get_sending_wavefronts_magnitudes("voltage inductor")))

        max_cap_r = abs(np.max(Data_Output_Ordered.get_returning_wavefronts_magnitudes("voltage capacitor")))
        min_cap_r = abs(np.min(Data_Output_Ordered.get_returning_wavefronts_magnitudes("voltage capacitor")))
        max_ind_r = abs(np.max(Data_Output_Ordered.get_returning_wavefronts_magnitudes("voltage inductor")))
        min_ind_r = abs(np.min(Data_Output_Ordered.get_returning_wavefronts_magnitudes("voltage inductor")))
        
    boundary = max(max_cap_s,min_cap_s,max_ind_s,min_ind_s,max_cap_r,min_cap_r,max_ind_r,min_ind_r)
    
    colour_map = mpl.cm.seismic
    norm = mpl.colors.Normalize(vmin=-boundary, vmax=boundary)
    
    for wave in Data_Output_Ordered.Wavefronts_Returning_Capacitor:

        x1 = -wave.position_start
        x2 = -wave.position_end

        y1 = wave.time_start
        y2 = wave.time_end
        
        mag = 0
        
        if(is_current):
            mag = float(wave.magnitude_current)
        else:
            mag = float(wave.magnitude_voltage)

        if(wave.time_start <=stop_time):
            ax.plot([x1,x2],[y1,y2],c=colour_map(norm(mag)),zorder=2)
            # ax.plot([(x2-x1)/2],[y1 + (y2-y1)/2], marker ='o',c=colour_map(norm(mag)),markersize=15)
            
    for wave in Data_Output_Ordered.Wavefronts_Sending_Capacitor:

        x1 = -wave.position_start
        x2 = -wave.position_end

        y1 = wave.time_start
        y2 = wave.time_end
        
        mag = 0
        
        if(is_current):
            mag = float(wave.magnitude_current)
        else:
            mag = float(wave.magnitude_voltage)

        if(wave.time_start <=stop_time):
            ax.plot([x1,x2],[y1,y2],c=non_active_wavefront_colour,linestyle='dashed',zorder=1)
            # ax.plot([-(x2-x1)/2],[y1 + (y2-y1)/2], marker ='o',c=colour_map(norm(mag)),markersize=15)

    # Inductor Wavefronts
    for wave in Data_Output_Ordered.Wavefronts_Returning_Inductor:

        x1 = wave.position_start
        x2 = wave.position_end

        y1 = wave.time_start
        y2 = wave.time_end

        mag = 0
        
        if(is_current):
            mag = float(wave.magnitude_current)
        else:
            mag = float(wave.magnitude_voltage)

        if(wave.time_start <=stop_time):
            ax.plot([x1,x2],[y1,y2],c=colour_map(norm(mag)),zorder=2)
            # ax.plot([(x2-x1)/2],[y1 + (y2-y1)/2], marker ='o',c=colour_map(norm(mag)),markersize=15)
            
    for wave in Data_Output_Ordered.Wavefronts_Sending_Inductor:

        x1 = wave.position_start
        x2 = wave.position_end

        y1 = wave.time_start
        y2 = wave.time_end

        mag = 0
        
        if(is_current):
            mag = float(wave.magnitude_current)
        else:
            mag = float(wave.magnitude_voltage)

        if(wave.time_start <=stop_time):
            ax.plot([x1,x2],[y1,y2],c=non_active_wavefront_colour,linestyle='dashed',zorder=1)
            # ax.plot([-(x2-x1)/2],[y1 + (y2-y1)/2], marker ='o',c=colour_map(norm(mag)),markersize=15)    

def plot_refelction_diagram_one_tx_s_and_r(Data_Input: Data_Input_Storage, Data_Output_Ordered : Data_Output_Storage_Ordered, is_capacitor,is_current, stop_time, ax, mutiple_ticks : bool = True):
    
        
    non_active_wavefront_colour = 'xkcd:dark grey'
    
    C_Time = str(2*Data_Input.Capacitor_Time)
    C_impedance = str(Data_Input.Capacitor_Impedance)
    
    L_Time = str(2*Data_Input.Inductor_Time)
    L_impedance = str(Data_Input.Inductor_Impedance)
    
    ax.axhline(linewidth=1, color='k')
    ax.axvline(linewidth=1, color='k')
    
    ax.plot([-1,-1],[0,stop_time],'k')
    ax.plot([1,1],[0,stop_time],'k')
    #ax.plot([-1,1],[stop_time,stop_time],'k')
    
    #ax.get_xaxis().set_visible(False)
    ax2 = ax.secondary_yaxis('right')
    ax.set_xticks = ([])
    ax2.set_xticks = ([])
    ax.set_xticklabels = ('')
    ax2.set_xticklabels = ('')
    
    ax.set_ylabel('Capacitor Time Delay = '+ C_Time, fontsize = 'large')
    ax2.set_ylabel('Inductor Time Delay = '+ L_Time, fontsize = 'large')
    #ax.yaxis.set_ticks(np.arange(0, stop_time, 1))
    #ax2.yaxis.set_ticks(np.arange(0, stop_time, 1))
    
    title_str =""
    
    if(is_capacitor):
        title_str += "Capacitor "
    else:
        title_str += "Inductor "
        
    if(is_current):
        title_str += "Current "
    else:
        title_str += "Voltage "
    
    
    ax.set_title(title_str+'Reflection Diagarm \n Capacitor Impedance = '+ C_impedance +'Ω, Inductor Impedance = ' + L_impedance+ 'Ω', fontsize = 'large')
        
    # ax.set_xlabel('Relative distance down Transmission Line')
    
    if(mutiple_ticks):
        ax.yaxis.set_major_locator(MultipleLocator(float(C_Time)))
        ax2.yaxis.set_major_locator(MultipleLocator(float(L_Time)))
        #ax.yaxis.set_major_formatter(FormatStrFormatter('%d'))

        # For the minor ticks, use no labels; default NullFormatter.
        ax.yaxis.set_minor_locator(MultipleLocator(float(C_Time)/2))
        ax2.yaxis.set_minor_locator(MultipleLocator(float(L_Time)/2))
    
    ax.set_ylim(0,stop_time)
    
    # Setup Colour Map
    max_cap_s = 0
    min_cap_s = 0
    max_ind_s = 0
    min_ind_s = 0
    
    max_cap_r = 0
    min_cap_r = 0
    max_ind_r = 0
    min_ind_r = 0
    
    boundary = 0 
    
    if(is_current):
        max_cap_s = abs(np.max(Data_Output_Ordered.get_sending_wavefronts_magnitudes("current capacitor")))
        min_cap_s = abs(np.min(Data_Output_Ordered.get_sending_wavefronts_magnitudes("current capacitor")))
        max_ind_s = abs(np.max(Data_Output_Ordered.get_sending_wavefronts_magnitudes("current inductor")))
        min_ind_s = abs(np.min(Data_Output_Ordered.get_sending_wavefronts_magnitudes("current inductor")))

        max_cap_r = abs(np.max(Data_Output_Ordered.get_returning_wavefronts_magnitudes("current capacitor")))
        min_cap_r = abs(np.min(Data_Output_Ordered.get_returning_wavefronts_magnitudes("current capacitor")))
        max_ind_r = abs(np.max(Data_Output_Ordered.get_returning_wavefronts_magnitudes("current inductor")))
        min_ind_r = abs(np.min(Data_Output_Ordered.get_returning_wavefronts_magnitudes("current inductor")))
    else:
        max_cap_s = abs(np.max(Data_Output_Ordered.get_sending_wavefronts_magnitudes("voltage capacitor")))
        min_cap_s = abs(np.min(Data_Output_Ordered.get_sending_wavefronts_magnitudes("voltage capacitor")))
        max_ind_s = abs(np.max(Data_Output_Ordered.get_sending_wavefronts_magnitudes("voltage inductor")))
        min_ind_s = abs(np.min(Data_Output_Ordered.get_sending_wavefronts_magnitudes("voltage inductor")))

        max_cap_r = abs(np.max(Data_Output_Ordered.get_returning_wavefronts_magnitudes("voltage capacitor")))
        min_cap_r = abs(np.min(Data_Output_Ordered.get_returning_wavefronts_magnitudes("voltage capacitor")))
        max_ind_r = abs(np.max(Data_Output_Ordered.get_returning_wavefronts_magnitudes("voltage inductor")))
        min_ind_r = abs(np.min(Data_Output_Ordered.get_returning_wavefronts_magnitudes("voltage inductor")))
        
    boundary = max(max_cap_s,min_cap_s,max_ind_s,min_ind_s,max_cap_r,min_cap_r,max_ind_r,min_ind_r)
    
    colour_map = mpl.cm.seismic
    norm = mpl.colors.Normalize(vmin=-boundary, vmax=boundary)
    
    for wave in Data_Output_Ordered.Wavefronts_Returning_Capacitor:

        x1 = -wave.position_start
        x2 = -wave.position_end

        y1 = wave.time_start
        y2 = wave.time_end
        
        mag = 0
        
        if(is_current):
            mag = float(wave.magnitude_current)
        else:
            mag = float(wave.magnitude_voltage)

        if(wave.time_start <=stop_time):
            if(is_capacitor):
                ax.plot([x1,x2],[y1,y2],c=colour_map(norm(mag)),zorder=2)
            else:
                ax.plot([x1,x2],[y1,y2],c=non_active_wavefront_colour,linestyle='dashed',zorder=1)
            
    for wave in Data_Output_Ordered.Wavefronts_Sending_Capacitor:

        x1 = -wave.position_start
        x2 = -wave.position_end

        y1 = wave.time_start
        y2 = wave.time_end
        
        mag = 0
        
        if(is_current):
            mag = float(wave.magnitude_current)
        else:
            mag = float(wave.magnitude_voltage)

        if(wave.time_start <=stop_time):
            if(is_capacitor):
                ax.plot([x1,x2],[y1,y2],c=colour_map(norm(mag)),zorder=2)
            else:
                ax.plot([x1,x2],[y1,y2],c=non_active_wavefront_colour,linestyle='dashed',zorder=1)

    # Inductor Wavefronts
    for wave in Data_Output_Ordered.Wavefronts_Returning_Inductor:

        x1 = wave.position_start
        x2 = wave.position_end

        y1 = wave.time_start
        y2 = wave.time_end

        mag = 0
        
        if(is_current):
            mag = float(wave.magnitude_current)
        else:
            mag = float(wave.magnitude_voltage)

        if(wave.time_start <=stop_time):
            if(not is_capacitor):
                ax.plot([x1,x2],[y1,y2],c=colour_map(norm(mag)),zorder=2)
            else:
                ax.plot([x1,x2],[y1,y2],c=non_active_wavefront_colour,linestyle='dashed',zorder=1)
            # ax.plot([(x2-x1)/2],[y1 + (y2-y1)/2], marker ='o',c=colour_map(norm(mag)),markersize=15)
            
    for wave in Data_Output_Ordered.Wavefronts_Sending_Inductor:

        x1 = wave.position_start
        x2 = wave.position_end

        y1 = wave.time_start
        y2 = wave.time_end

        mag = 0
        
        if(is_current):
            mag = float(wave.magnitude_current)
        else:
            mag = float(wave.magnitude_voltage)

        if(wave.time_start <=stop_time):
            if(not is_capacitor):
                ax.plot([x1,x2],[y1,y2],c=colour_map(norm(mag)),zorder=2)  
            else:
                ax.plot([x1,x2],[y1,y2],c=non_active_wavefront_colour,linestyle='dashed',zorder=1)
            
def plot_refelction_diagram_one_tx_s_or_r(Data_Input: Data_Input_Storage, Data_Output_Ordered : Data_Output_Storage_Ordered, is_capacitor,is_sending,is_current, stop_time, ax, mutiple_ticks : bool = True):
    
        
    non_active_wavefront_colour = 'xkcd:dark grey'
    
    C_Time = str(2*Data_Input.Capacitor_Time)
    C_impedance = str(Data_Input.Capacitor_Impedance)
    
    L_Time = str(2*Data_Input.Inductor_Time)
    L_impedance = str(Data_Input.Inductor_Impedance)
    
    ax.axhline(linewidth=1, color='k')
    ax.axvline(linewidth=1, color='k')
    
    ax.plot([-1,-1],[0,stop_time],'k')
    ax.plot([1,1],[0,stop_time],'k')
    #ax.plot([-1,1],[stop_time,stop_time],'k')
    
    #ax.get_xaxis().set_visible(False)
    ax2 = ax.secondary_yaxis('right')
    ax.set_xticks = ([])
    ax2.set_xticks = ([])
    ax.set_xticklabels = ('')
    ax2.set_xticklabels = ('')
    
    ax.set_ylabel('Capacitor Time Delay = '+ C_Time, fontsize = 'large')
    ax2.set_ylabel('Inductor Time Delay = '+ L_Time, fontsize = 'large')
    #ax.yaxis.set_ticks(np.arange(0, stop_time, 1))
    #ax2.yaxis.set_ticks(np.arange(0, stop_time, 1))
    
    title_str =""
    
    if(is_capacitor):
        title_str += "Capacitor "
    else:
        title_str += "Inductor "
        
    if(is_sending):
        title_str += "Sending "
    else:
        title_str += "Returning "
        
    if(is_current):
        title_str += "Current "
    else:
        title_str += "Voltage "
    
    
    ax.set_title(title_str+'Reflection Diagarm \n Capacitor Impedance = '+ C_impedance +'Ω, Inductor Impedance = ' + L_impedance+ 'Ω', fontsize = 'large')
        
    # ax.set_xlabel('Relative distance down Transmission Line')
    
    if(mutiple_ticks):
        ax.yaxis.set_major_locator(MultipleLocator(float(C_Time)))
        ax2.yaxis.set_major_locator(MultipleLocator(float(L_Time)))
        #ax.yaxis.set_major_formatter(FormatStrFormatter('%d'))

        # For the minor ticks, use no labels; default NullFormatter.
        ax.yaxis.set_minor_locator(MultipleLocator(float(C_Time)/2))
        ax2.yaxis.set_minor_locator(MultipleLocator(float(L_Time)/2))
    
    ax.set_ylim(0,stop_time)
    
    # Setup Colour Map
    max_cap_s = 0
    min_cap_s = 0
    max_ind_s = 0
    min_ind_s = 0
    
    max_cap_r = 0
    min_cap_r = 0
    max_ind_r = 0
    min_ind_r = 0
    
    boundary = 0 
    
    if(is_current):
        max_cap_s = abs(np.max(Data_Output_Ordered.get_sending_wavefronts_magnitudes("current capacitor")))
        min_cap_s = abs(np.min(Data_Output_Ordered.get_sending_wavefronts_magnitudes("current capacitor")))
        max_ind_s = abs(np.max(Data_Output_Ordered.get_sending_wavefronts_magnitudes("current inductor")))
        min_ind_s = abs(np.min(Data_Output_Ordered.get_sending_wavefronts_magnitudes("current inductor")))

        max_cap_r = abs(np.max(Data_Output_Ordered.get_returning_wavefronts_magnitudes("current capacitor")))
        min_cap_r = abs(np.min(Data_Output_Ordered.get_returning_wavefronts_magnitudes("current capacitor")))
        max_ind_r = abs(np.max(Data_Output_Ordered.get_returning_wavefronts_magnitudes("current inductor")))
        min_ind_r = abs(np.min(Data_Output_Ordered.get_returning_wavefronts_magnitudes("current inductor")))
    else:
        max_cap_s = abs(np.max(Data_Output_Ordered.get_sending_wavefronts_magnitudes("voltage capacitor")))
        min_cap_s = abs(np.min(Data_Output_Ordered.get_sending_wavefronts_magnitudes("voltage capacitor")))
        max_ind_s = abs(np.max(Data_Output_Ordered.get_sending_wavefronts_magnitudes("voltage inductor")))
        min_ind_s = abs(np.min(Data_Output_Ordered.get_sending_wavefronts_magnitudes("voltage inductor")))

        max_cap_r = abs(np.max(Data_Output_Ordered.get_returning_wavefronts_magnitudes("voltage capacitor")))
        min_cap_r = abs(np.min(Data_Output_Ordered.get_returning_wavefronts_magnitudes("voltage capacitor")))
        max_ind_r = abs(np.max(Data_Output_Ordered.get_returning_wavefronts_magnitudes("voltage inductor")))
        min_ind_r = abs(np.min(Data_Output_Ordered.get_returning_wavefronts_magnitudes("voltage inductor")))
        
    boundary = max(max_cap_s,min_cap_s,max_ind_s,min_ind_s,max_cap_r,min_cap_r,max_ind_r,min_ind_r)
    
    colour_map = mpl.cm.seismic
    norm = mpl.colors.Normalize(vmin=-boundary, vmax=boundary)
    
    for wave in Data_Output_Ordered.Wavefronts_Returning_Capacitor:

        x1 = -wave.position_start
        x2 = -wave.position_end

        y1 = wave.time_start
        y2 = wave.time_end
        
        mag = 0
        
        if(is_current):
            mag = float(wave.magnitude_current)
        else:
            mag = float(wave.magnitude_voltage)

        if(wave.time_start <=stop_time):
            if(is_capacitor and not is_sending):
                ax.plot([x1,x2],[y1,y2],c=colour_map(norm(mag)),zorder=2)
            else:
                ax.plot([x1,x2],[y1,y2],c=non_active_wavefront_colour,linestyle='dashed',zorder=1)
            
    for wave in Data_Output_Ordered.Wavefronts_Sending_Capacitor:

        x1 = -wave.position_start
        x2 = -wave.position_end

        y1 = wave.time_start
        y2 = wave.time_end
        
        mag = 0
        
        if(is_current):
            mag = float(wave.magnitude_current)
        else:
            mag = float(wave.magnitude_voltage)

        if(wave.time_start <=stop_time):
            if(is_capacitor and is_sending):
                ax.plot([x1,x2],[y1,y2],c=colour_map(norm(mag)),zorder=2)
            else:
                ax.plot([x1,x2],[y1,y2],c=non_active_wavefront_colour,linestyle='dashed',zorder=1)

    # Inductor Wavefronts
    for wave in Data_Output_Ordered.Wavefronts_Returning_Inductor:

        x1 = wave.position_start
        x2 = wave.position_end

        y1 = wave.time_start
        y2 = wave.time_end

        mag = 0
        
        if(is_current):
            mag = float(wave.magnitude_current)
        else:
            mag = float(wave.magnitude_voltage)

        if(wave.time_start <=stop_time):
            if(not is_capacitor and not is_sending):
                ax.plot([x1,x2],[y1,y2],c=colour_map(norm(mag)),zorder=2)
            else:
                ax.plot([x1,x2],[y1,y2],c=non_active_wavefront_colour,linestyle='dashed',zorder=1)
            # ax.plot([(x2-x1)/2],[y1 + (y2-y1)/2], marker ='o',c=colour_map(norm(mag)),markersize=15)
            
    for wave in Data_Output_Ordered.Wavefronts_Sending_Inductor:

        x1 = wave.position_start
        x2 = wave.position_end

        y1 = wave.time_start
        y2 = wave.time_end

        mag = 0
        
        if(is_current):
            mag = float(wave.magnitude_current)
        else:
            mag = float(wave.magnitude_voltage)

        if(wave.time_start <=stop_time):
            if(not is_capacitor and is_sending):
                ax.plot([x1,x2],[y1,y2],c=colour_map(norm(mag)),zorder=2)  
            else:
                ax.plot([x1,x2],[y1,y2],c=non_active_wavefront_colour,linestyle='dashed',zorder=1)

# SPATIAL PLOTS NEW
def plot_3d_spatial(Time_Enquriey,data_output_merged,data_output_ordered,ax):
        
        ax.xaxis.set_major_formatter(EngFormatter('m'))
        ax.yaxis.set_major_formatter(EngFormatter('A'))
        ax.zaxis.set_major_formatter(EngFormatter('V'))
                
        ax.set_xlabel('position')
        ax.set_ylabel('current')
        ax.set_zlabel('voltage')
        
        is_Inductive =True

        # INDUCTOR
        pos_all, value_lv, value_rv, value_lc, value_rc = get_spatial_voltage_current_at_time(Time_Enquriey, data_output_merged,data_output_ordered,is_Inductive)
        zip_out = zip(pos_all, value_lv, value_rv, value_lc, value_rc)

        #arrays
        x_position =[]
        y_current =[]
        z_voltage =[]

        dx_position =[]
        dy_current =[]
        dz_voltage =[]

        #initiate variables
        x_old = 0
        y_voltage_old = 0
        y_current_old = 0

        is_first = True

        for (position, left_voltage, right_voltage, left_current, right_current) in zip_out:
                
                x = position
                
                y1_voltage = left_voltage
                y2_voltage = right_voltage
                
                y1_current = left_current
                y2_current = right_current
                
                x_position.append(x)
                y_current.append(0)
                z_voltage.append(0)
                
                if(is_first):
                        x_old = position
                        y_voltage_old = left_voltage
                        y_current_old = left_current
                        is_first = False
                else:
                        dx_position.append(x - x_old)
                        dy_current.append(y_current_old)
                        dz_voltage.append(y_voltage_old)
                        
                x_old = x
                
                y_voltage_old = y2_voltage
                y_current_old = y2_current
                

        x_position.pop()
        y_current.pop()
        z_voltage.pop()
        
        ax.bar3d(x_position, y_current, z_voltage, dx_position, dy_current, dz_voltage )
        
        x_position =[]
        y_current =[]
        z_voltage =[]

        dx_position =[]
        dy_current =[]
        dz_voltage =[]

        is_first = True

        pos_all, value_lv, value_rv, value_lc, value_rc = get_spatial_voltage_current_at_time(Time_Enquriey, data_output_merged,data_output_ordered,not is_Inductive)
        zip_out = zip(pos_all, value_lv, value_rv, value_lc, value_rc)

        for (position, left_voltage, right_voltage, left_current, right_current) in zip_out:
                
                x = -position
                
                y1_voltage = left_voltage
                y2_voltage = right_voltage
                
                y1_current = left_current
                y2_current = right_current
                
                x_position.append(x)
                y_current.append(0)
                z_voltage.append(0)
                
                if(is_first):
                        x_old = position
                        y_voltage_old = left_voltage
                        y_current_old = left_current
                        is_first = False
                else:
                        dx_position.append(x - x_old)
                        dy_current.append(y_current_old)
                        dz_voltage.append(y_voltage_old)
                
                x_old = x
                
                y_voltage_old = y2_voltage
                y_current_old = y2_current

        x_position.pop()
        y_current.pop()
        z_voltage.pop()

        ax.bar3d(x_position, y_current, z_voltage, dx_position, dy_current, dz_voltage )

def plot_spatial_same_axis(Time_Enquriey,Interface : Data_Interface_Storage,ax_voltage,ax_current):
        ax_voltage.get_figure().suptitle("Spatial Waveforms at " + str(Time_Enquriey.quantize(Decimal('.0001'), rounding=ROUND_HALF_DOWN)) + "s")
        
        ax_voltage.set_title('Spatial Voltage')
        # ax_voltage.xaxis.set_major_formatter(matplotlib.ticker.EngFormatter('m'))
        ax_voltage.yaxis.set_major_formatter(EngFormatter('V'))
        ax_voltage.set_xlabel('Capacitor    ←    interconncect    →    Inductor ')
        ax_voltage.set_ylabel('voltage')
        
        
        ax_current.set_title('Spatial Current')
        # ax_current.xaxis.set_major_formatter(matplotlib.ticker.EngFormatter('m'))
        ax_current.yaxis.set_major_formatter(EngFormatter('A'))
        ax_current.set_xlabel('Capacitor    ←    interconncect    →    Inductor ')
        ax_current.set_ylabel('current')


        # INDUCTOR
        pos_all, value_lv, value_rv, value_lc, value_rc = get_spatial_voltage_current_at_time(Time_Enquriey, Interface, True)
        zip_out = zip(pos_all, value_lv, value_rv, value_lc, value_rc)

        interconncet_voltage_inductor = 0
        interconncet_voltage_capacitor = 0
        interconnect_current = 0
        
        #arrays
        x_position =[]
        y_current =[]
        z_voltage =[]
        
        dx_position =[]
        dy_current =[]
        dz_voltage =[]

        #initiate variables
        x_old = 0
        y_voltage_old = 0
        y_current_old = 0

        is_first = True

        for (position, left_voltage, right_voltage, left_current, right_current) in zip_out:
                
                x = float(position)
                
                y1_voltage = left_voltage
                y2_voltage = right_voltage
                
                y1_current = left_current
                y2_current = right_current
                
                x_position.append(x)
                y_current.append(0)
                z_voltage.append(0)
                
                if(is_first):
                        x_old = position
                        y_voltage_old = left_voltage
                        y_current_old = left_current
                        
                        interconncet_voltage_inductor = left_voltage
                        interconnect_current = left_current
                        
                        is_first = False
                else:
                        dx_position.append(x - x_old)
                        dy_current.append(y_current_old)
                        dz_voltage.append(y_voltage_old)
                        
                x_old = x
                
                y_voltage_old = y2_voltage
                y_current_old = y2_current
                

        x_position.pop()
        y_current.pop()
        z_voltage.pop()
        
        # ( x , width , height)
        ax_voltage.bar(x_position, dz_voltage, dx_position, align = 'edge',edgecolor = 'k')
        ax_current.bar(x_position, dy_current, dx_position, align = 'edge',edgecolor = 'k')
        
        x_position =[]
        y_current =[]
        z_voltage =[]

        dx_position =[]
        dy_current =[]
        dz_voltage =[]

        is_first = True

        pos_all, value_lv, value_rv, value_lc, value_rc = get_spatial_voltage_current_at_time(Time_Enquriey, Interface , False)
        zip_out = zip(pos_all, value_lv, value_rv, value_lc, value_rc)

        for (position, left_voltage, right_voltage, left_current, right_current) in zip_out:
                
                x = -float(position)
                
                y1_voltage = left_voltage
                y2_voltage = right_voltage
                
                y1_current = left_current
                y2_current = right_current
                
                x_position.append(x)
                y_current.append(0)
                z_voltage.append(0)
                
                if(is_first):
                        x_old = position
                        y_voltage_old = left_voltage
                        y_current_old = left_current
                        
                        interconncet_voltage_capacitor = left_voltage
                        
                        is_first = False
                else:
                        dx_position.append(x - x_old)
                        dy_current.append(y_current_old)
                        dz_voltage.append(y_voltage_old)
                
                x_old = x
                
                y_voltage_old = y2_voltage
                y_current_old = y2_current

        x_position.pop()
        y_current.pop()
        z_voltage.pop()
        
        ax_voltage.bar(x_position, dz_voltage, dx_position, align = 'edge',edgecolor = 'k')
        ax_current.bar(x_position, dy_current, dx_position, align = 'edge',edgecolor = 'k')
        
        return interconncet_voltage_capacitor, interconncet_voltage_inductor, interconnect_current

def plot_time_interconnect_and_intercept(time,data_output_ordered,ax_voltage,ax_current,interconncet_voltage_capacitor=0, interconncet_voltage_inductor=0, interconnect_current=0):
    ax_voltage.axvline(time,linestyle='--',c='gray')

    plot_time_interconnect(data_output_ordered,ax_voltage,'voltage inductor',True)
    ax_voltage.axhline(interconncet_voltage_inductor,linestyle='--',c='C0')
    plot_time_interconnect(data_output_ordered,ax_voltage,'voltage capacitor',True)
    ax_voltage.axhline(interconncet_voltage_capacitor,linestyle='--',c='C1')

    plot_time_interconnect(data_output_ordered,ax_current,'current inductor',True)
    ax_current.get_lines()[0].set_color("black")

    y_limits = ax_current.get_ylim()

    ax_current.axhline(interconnect_current,linestyle='--',c='gray')
    ax_current.axvline(time,linestyle='--',c='gray')
    ax_current.set_ylim(y_limits)
    
    ax_voltage.set_title('Voltage at Interconnect')
    ax_voltage.xaxis.set_major_formatter(EngFormatter('s'))
    ax_voltage.yaxis.set_major_formatter(EngFormatter('V'))
    ax_voltage.set_xlabel('time')
    ax_voltage.set_ylabel('voltage')
    
    
    ax_current.set_title('Current at Interconnect')
    ax_current.xaxis.set_major_formatter(EngFormatter('s'))
    ax_current.yaxis.set_major_formatter(EngFormatter('A'))
    ax_current.set_xlabel('time')
    ax_current.set_ylabel('current')

def save_spatial_interconnect(Interface : Data_Interface_Storage,**kwargs):

    #Default Values
    kwarg_options = dict([
        ('start_time','0'), ('end_time',Interface.data_input.Simulation_Stop_Time), 
        ('fps','30'),('video_runtime','60'),('dpi','300'),
        ('fig_size',(14, 8)),
        ('meta_data',dict(title='Distributed Modelling', artist='Jonathan Meerholz')),
        ('save_name',f'spatial_and_time_{Interface.data_input.Inductor_Impedance}_{Interface.data_input.Capacitor_Impedance}ohm_{Interface.data_input.Inductor_Time*2}_{Interface.data_input.Capacitor_Time*2}s')
        ])
         
    kwarg_options = handle_default_kwargs(kwargs,kwarg_options)
    
    fig_save_2d, ax_save_2d = plt.subplots(2,2,figsize=kwarg_options['fig_size'],constrained_layout = True)

    save_name = kwarg_options['save_name']
    save_name = save_name.replace('.',',')

    start_time = Decimal(kwarg_options['start_time'])
    end_time = Decimal(kwarg_options['end_time'])

    fps = Decimal(kwarg_options['fps'])
    video_runtime = Decimal(kwarg_options['video_runtime'])
    dpi = kwarg_options['dpi']

    number_frames =  video_runtime*fps
    time_increment = (end_time - start_time)/number_frames

    metadata = kwarg_options['meta_data']
    writer = FFMpegWriter(fps=float(fps), metadata=metadata)

    time = start_time
    frame_counter = 0
    with writer.saving(fig_save_2d, (save_name+".mp4"), float(dpi)):

        for i in tqdm(range(0,int(number_frames))):
            interconncet_voltage_capacitor, interconncet_voltage_inductor, interconnect_current = plot_spatial_same_axis(time,Interface,ax_save_2d[0,0],ax_save_2d[1,0])
            plot_time_interconnect_and_intercept(time,Interface.data_output_ordered,ax_save_2d[0,1],ax_save_2d[1,1],interconncet_voltage_capacitor, interconncet_voltage_inductor, interconnect_current)
            
            writer.grab_frame()
            
            time += time_increment
            frame_counter +=1
            
            ax_save_2d[0,0].clear()
            ax_save_2d[0,1].clear()
            ax_save_2d[1,0].clear()
            ax_save_2d[1,1].clear()
            
    plt.close(fig_save_2d)
    print(f"Spatial video generation completed, video saved as {save_name}.mp4")
  
def spatial_interconnect_investigator_ui(Interface : Data_Interface_Storage):
    fig_s,ax_s = plt.subplots(2,2,figsize=(14, 8))
    def clear_axes():
        ax_s[0,0].clear()
        ax_s[0,1].clear()
        ax_s[1,0].clear()
        ax_s[1,1].clear()

    increment_button = widgets.Button(description = "step forward", layout=widgets.Layout(width='auto'))
    decrement_button = widgets.Button(description = "step backward", layout=widgets.Layout(width='auto'))
    increment_text = widgets.FloatText(description = 'val', value=0.1)


    time_slider = widgets.FloatSlider(value=0, min =0, max = Interface.data_input.Simulation_Stop_Time-1, layout=widgets.Layout(width='auto'))
    output = widgets.Output()

    def on_increment_click(b):
        time_slider.value += increment_text.value
        time = Decimal(str(time_slider.value))
        clear_axes()
        interconncet_voltage_capacitor, interconncet_voltage_inductor, interconnect_current = plot_spatial_same_axis(time,Interface,ax_s[0,0],ax_s[1,0])
        plot_time_interconnect_and_intercept(time,Interface.data_output_ordered,ax_s[0,1],ax_s[1,1],interconncet_voltage_capacitor, interconncet_voltage_inductor, interconnect_current)
        
        
    def on_decrement_click(b):
        time_slider.value -= increment_text.value
        time = Decimal(str(time_slider.value))
        clear_axes()
        interconncet_voltage_capacitor, interconncet_voltage_inductor, interconnect_current = plot_spatial_same_axis(time,Interface,ax_s[0,0],ax_s[1,0])
        plot_time_interconnect_and_intercept(time,Interface.data_output_ordered,ax_s[0,1],ax_s[1,1],interconncet_voltage_capacitor, interconncet_voltage_inductor, interconnect_current)
        
    def handle_slider_change(change):
        if(isinstance(change.new,dict)):
            if(len(change.new) > 0):
                time = Decimal(str(change.new['value']))
                clear_axes()
                interconncet_voltage_capacitor, interconncet_voltage_inductor, interconnect_current = plot_spatial_same_axis(time,Interface,ax_s[0,0],ax_s[1,0])
                plot_time_interconnect_and_intercept(time,Interface.data_output_ordered,ax_s[0,1],ax_s[1,1],interconncet_voltage_capacitor, interconncet_voltage_inductor, interconnect_current)
                
    increment_button.on_click(on_increment_click)
    decrement_button.on_click(on_decrement_click)
    time_slider.observe(handle_slider_change)

    increment_grid = widgets.GridspecLayout(1,3)
    increment_grid[0,0] = decrement_button
    increment_grid[0,1] = increment_button
    increment_grid[0,2] = increment_text

    display(increment_grid,time_slider)