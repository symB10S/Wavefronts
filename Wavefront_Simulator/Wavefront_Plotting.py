from Wavefront_Generation import Data_Input_Storage, Data_Output_Storage, Data_Output_Storage_Ordered, Data_Interface_Storage, get_spatial_voltage_current_at_time, handle_default_kwargs
from Wavefront_Storage import *
from decimal import Decimal, ROUND_HALF_DOWN
import numpy as np
import copy
import matplotlib as mpl
import matplotlib.pyplot as plt
from matplotlib.ticker import (MultipleLocator, EngFormatter)
from matplotlib.animation import FFMpegWriter
from tqdm import tqdm

plt.rcParams['animation.ffmpeg_path'] = 'ffmpeg\\ffmpeg.exe'

import ipywidgets as widgets
from IPython.display import display

## Plotting
def clear_subplot(axs):
    for ax in axs:
        ax.cla()

def plot_fanout_seismic(arr : np.ndarray ,ax ,title = "Fanout Plot", show_colour_bar = True ,contrast = False, padwidth = 15):
    
    max_boundary= 0
    if (contrast):
        Contrast = copy.copy(arr.astype(float))
        max_index = np.unravel_index(np.argmax(Contrast, axis=None), Contrast.shape)
        Contrast[max_index] = 0
        
        max_boundary = abs(np.max(Contrast))  
        min_boundary = abs(np.min(Contrast))  
        
        max_boundary = max(max_boundary, min_boundary)
    else:
        max_boundary = abs(np.max(arr.astype(float)))
        min_boundary = abs(np.min(arr.astype(float)))
        
        max_boundary = max(max_boundary, min_boundary)
    
    ax.set_title(title)
    c = ax.imshow(np.pad(arr.astype(float),(padwidth,padwidth)),cmap= mpl.cm.seismic,vmax =max_boundary, vmin = - max_boundary,origin='lower')
    
    if(show_colour_bar):
        cb = ax.get_figure().colorbar(c,ax=ax)
        
def plot_fanout_colour(arr : np.ndarray ,ax ,title = "Fanout Plot", show_colour_bar = True ,contrast = False):
    
    max_boundary = np.max(arr.astype(float))  
    min_boundary = np.min(arr.astype(float))  
    
    ax.set_title(title)
    cb = ax.imshow(arr.astype(float),cmap=mpl.cm.jet,vmax =max_boundary, vmin =min_boundary)
    
    if(show_colour_bar):
        ax.get_figure().colorbar(cb,ax=ax)
        
def plot_fanout_crossection(arr : np.ndarray, ax, row_number : int, title : str, show_colour_bar = True ,contrast : bool = False):
    
    clear_subplot(ax)
    
    plt.gcf().suptitle("Crossection of " + title+" Fanout at index " + str(row_number) )
    
    row_a = arr[row_number,:]
    row_b = arr[:,row_number]
    
    ax[0].plot(row_a)
    ax[1].plot(row_b)
    
    plot_fanout_seismic(arr,ax[2],"Fanout",show_colour_bar,contrast,0)
    ax[2].plot([row_number,row_number],[0,arr.shape[0]],'m--')
    ax[2].plot([0,arr.shape[0]],[row_number,row_number],'c--')

def plot_fanout_interconnect(data_output_merged: Data_Output_Storage,ax, which_string :str, data_str : str = ""):
    
    allowed_strings = ["voltage inductor", "current inductor", "voltage capacitor", "current capacitor"]
    if(which_string.lower() == allowed_strings[0] ):
        plot_fanout_seismic( data_output_merged.Voltage_Interconnect_Inductor,ax,allowed_strings[0]+ data_str,True,True)
    elif(which_string.lower() == allowed_strings[1] ):
        plot_fanout_seismic(data_output_merged.Current_Interconnect_Inductor,ax,allowed_strings[1]+ data_str)
    elif(which_string.lower() == allowed_strings[2] ):
        plot_fanout_seismic(data_output_merged.Voltage_Interconnect_Capacitor,ax,allowed_strings[2]+ data_str,True,True)
    elif(which_string.lower() == allowed_strings[3] ):
        plot_fanout_seismic(data_output_merged.Current_Interconnect_Capacitor,ax,allowed_strings[3]+ data_str)
    else:
            raise ValueError("Incorrect plotting choice")

def plot_fanout_interconnect_4(data_output_merged: Data_Output_Storage):
    
    fig, ax = plt.subplot_mosaic([['A','B'],['C','D']])
    
    plot_fanout_seismic(data_output_merged.Voltage_Interconnect_Inductor,ax['A'],"Inductor Voltage",True,True)
    plot_fanout_seismic(data_output_merged.Current_Interconnect_Inductor,ax['C'],"Inductor Current")
    plot_fanout_seismic(data_output_merged.Voltage_Interconnect_Inductor,ax['B'],"Capacitor Voltage",True,True)
    plot_fanout_seismic(data_output_merged.Current_Interconnect_Inductor,ax['D'],"Capacitor Current")
    
    return fig,ax

def plot_fanout_wavefronts(data_output: Data_Output_Storage,ax, which_string :str, is_sending : bool = True):
    if(is_sending):
        plot_fanout_seismic(data_output.get_sending_wavefronts_magnitudes(which_string),ax)
    else:
        plot_fanout_seismic(data_output.get_returning_wavefronts_magnitudes(which_string),ax)

def plot_fanout_wavefronts_all(data_output: Data_Output_Storage, is_sending : bool = True, data_str :str = ""):
    fig, ax = plt.subplot_mosaic([['A','B','C','D'],['E','F','G','H']])
    
    fig.suptitle("Wavefront Fanouts " + data_str)
    
    plot_fanout_seismic(data_output.get_sending_wavefronts_magnitudes("voltage inductor"),ax['A'],"sending voltage inductor")
    plot_fanout_seismic(data_output.get_sending_wavefronts_magnitudes("current inductor"),ax['B'],"sending current inductor")
    plot_fanout_seismic(data_output.get_sending_wavefronts_magnitudes("voltage capacitor"),ax['C'],"sending voltage capacitor")
    plot_fanout_seismic(data_output.get_sending_wavefronts_magnitudes("current capacitor"),ax['D'],"sending current capacitor")

    plot_fanout_seismic(data_output.get_returning_wavefronts_magnitudes("voltage inductor"),ax['E'],"returning voltage inductor")
    plot_fanout_seismic(data_output.get_returning_wavefronts_magnitudes("current inductor"),ax['F'],"returning current inductor")
    plot_fanout_seismic(data_output.get_returning_wavefronts_magnitudes("voltage capacitor"),ax['G'],"returning voltage capacitor")
    plot_fanout_seismic(data_output.get_returning_wavefronts_magnitudes("current capacitor"),ax['H'],"returning current capacitor")
        
    return fig, ax
    
def plot_time_interconnect(data_output_ordered : Data_Output_Storage_Ordered,ax, which_string :str, is_integrated: bool = False): 
    allowed_strings = ["voltage inductor", "current inductor", "voltage capacitor", "current capacitor"]
    
    if(is_integrated):
        if(which_string.lower() == allowed_strings[0] ):
            ax.set_title("Inductor voltage at Interconnect")
            ax.step(data_output_ordered.Time,np.cumsum(data_output_ordered.Voltage_Interconnect_Inductor),where='post')
        elif(which_string.lower() == allowed_strings[1] ):
            ax.set_title("Inductor current at Interconnect")
            ax.step(data_output_ordered.Time,np.cumsum(data_output_ordered.Current_Interconnect_Inductor),where='post')
        elif(which_string.lower() == allowed_strings[2] ):
            ax.set_title("Capacitor voltage at Interconnect")
            ax.step(data_output_ordered.Time,np.cumsum(data_output_ordered.Voltage_Interconnect_Capacitor),where='post')
        elif(which_string.lower() == allowed_strings[3] ):
            ax.set_title("Capacitor current at Interconnect")
            ax.step(data_output_ordered.Time,np.cumsum(data_output_ordered.Current_Interconnect_Capacitor),where='post')
        else:
            raise ValueError(f"Incorrect plotting choice /, {which_string} is not a valid option. Optiond are: \n {allowed_strings}")
    else:
        if(which_string.lower() == allowed_strings[0] ):
            ax.set_title("Inductor voltage change at Interconnect")
            ax.step(data_output_ordered.Time,data_output_ordered.Voltage_Interconnect_Inductor,where='post')
        elif(which_string.lower() == allowed_strings[1] ):
            ax.set_title("Inductor current change at Interconnect")
            ax.step(data_output_ordered.Time,data_output_ordered.Current_Interconnect_Inductor,where='post')
        elif(which_string.lower() == allowed_strings[2] ):
            ax.set_title("Capacitor voltage change at Interconnect")
            ax.step(data_output_ordered.Time,data_output_ordered.Voltage_Interconnect_Capacitor,where='post')
        elif(which_string.lower() == allowed_strings[3] ):
            ax.set_title("Capacitor current change at Interconnect")
            ax.step(data_output_ordered.Time,data_output_ordered.Current_Interconnect_Capacitor,where='post')
        else:
            raise ValueError(f"Incorrect plotting choice /, {which_string} is not a valid option. Optiond are: \n {allowed_strings}")
        
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

def plot_diff(Y,X,ax,title_str :str = "Derivative"):
    dy = np.ediff1d(Y[1:])
    dx = np.ediff1d(X[1:])
    
    dydx = dy/dx
    
    ax.set_title(title_str)
    ax.step(X[1:-1],dydx,where="post") 
    
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

        first_y_voltage_inductor = 0
        first_y_voltage_capacitor = 0
        first_y_current = 0
        
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
                        
                        first_y_voltage_inductor = left_voltage
                        first_y_current = left_current
                        
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
                        
                        first_y_voltage_capacitor = left_voltage
                        
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
        
        return first_y_voltage_capacitor, first_y_voltage_inductor, first_y_current

def plot_time_interconnect_and_intercept(time,data_output_ordered,ax_voltage,ax_current,first_y_voltage_capacitor=0, first_y_voltage_inductor=0, first_y_current=0):
    ax_voltage.axvline(time,linestyle='--',c='gray')

    plot_time_interconnect(data_output_ordered,ax_voltage,'voltage inductor',True)
    ax_voltage.axhline(first_y_voltage_inductor,linestyle='--',c='C0')
    plot_time_interconnect(data_output_ordered,ax_voltage,'voltage capacitor',True)
    ax_voltage.axhline(first_y_voltage_capacitor,linestyle='--',c='C1')

    plot_time_interconnect(data_output_ordered,ax_current,'current inductor',True)
    ax_current.get_lines()[0].set_color("black")

    y_limits = ax_current.get_ylim()

    ax_current.axhline(first_y_current,linestyle='--',c='gray')
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
            first_y_voltage_capacitor, first_y_voltage_inductor, first_y_current = plot_spatial_same_axis(time,Interface,ax_save_2d[0,0],ax_save_2d[1,0])
            plot_time_interconnect_and_intercept(time,Interface.data_output_ordered,ax_save_2d[0,1],ax_save_2d[1,1],first_y_voltage_capacitor, first_y_voltage_inductor, first_y_current)
            
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
        first_y_voltage_capacitor, first_y_voltage_inductor, first_y_current = plot_spatial_same_axis(time,Interface,ax_s[0,0],ax_s[1,0])
        plot_time_interconnect_and_intercept(time,Interface.data_output_ordered,ax_s[0,1],ax_s[1,1],first_y_voltage_capacitor, first_y_voltage_inductor, first_y_current)
        
        
    def on_decrement_click(b):
        time_slider.value -= increment_text.value
        time = Decimal(str(time_slider.value))
        clear_axes()
        first_y_voltage_capacitor, first_y_voltage_inductor, first_y_current = plot_spatial_same_axis(time,Interface,ax_s[0,0],ax_s[1,0])
        plot_time_interconnect_and_intercept(time,Interface.data_output_ordered,ax_s[0,1],ax_s[1,1],first_y_voltage_capacitor, first_y_voltage_inductor, first_y_current)
        
    def handle_slider_change(change):
        if(isinstance(change.new,dict)):
            if(len(change.new) > 0):
                time = Decimal(str(change.new['value']))
                clear_axes()
                first_y_voltage_capacitor, first_y_voltage_inductor, first_y_current = plot_spatial_same_axis(time,Interface,ax_s[0,0],ax_s[1,0])
                plot_time_interconnect_and_intercept(time,Interface.data_output_ordered,ax_s[0,1],ax_s[1,1],first_y_voltage_capacitor, first_y_voltage_inductor, first_y_current)
                
    increment_button.on_click(on_increment_click)
    decrement_button.on_click(on_decrement_click)
    time_slider.observe(handle_slider_change)

    increment_grid = widgets.GridspecLayout(1,3)
    increment_grid[0,0] = decrement_button
    increment_grid[0,1] = increment_button
    increment_grid[0,2] = increment_text

    display(increment_grid,time_slider)