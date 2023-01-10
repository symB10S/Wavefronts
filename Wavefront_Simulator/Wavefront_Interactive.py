from Wavefront_Storage import *
from Wavefront_Plotting import *

import ipywidgets as widgets
from IPython.display import display


def spatial_interconnect_investigator_ui(Interface : Data_Interface_Storage, slider_step_size:float = 0.1):
    """Creates an interactive spatial plot using ipywidgets. 

    :param Interface: interface data storage object
    :type Interface: Data_Interface_Storage
    :param slider_step_size: the step size of the slider, make larger for smoother sliding, defaults to 0.1
    :type slider_step_size: float, optional
    """
    # define widgets
    increment_button = widgets.Button(description = "step forward", layout=widgets.Layout(width='auto'))
    decrement_button = widgets.Button(description = "step backward", layout=widgets.Layout(width='auto'))
    increment_text = widgets.FloatText(description = 'increment', value=0.1)
    auto_zoom_toggle = widgets.Checkbox(value=False,description='Auto-Zoom',disabled=False,tooltip='if spatial plots axes must zoom to features or be constant')
    time_slider = widgets.FloatSlider(value=0, min =0, max = Interface.data_input.Simulation_Stop_Time-1, step = slider_step_size, layout=widgets.Layout(width='auto'))
    # output = widgets.Output()
    
    fig_s,ax_s = plt.subplot_mosaic([['V','inter-V'],
                                     ['I','inter-I']],figsize=(14, 8))
    
    def handle_input(t:Decimal):
        clear_subplot(ax_s.values())
        make_spatial_voltage_and_current(t,Interface,ax=ax_s,fig_size=(14, 8))
        plot_time_interconnect_and_intercepts_at_time(t,Interface.data_output_ordered,ax_voltage=ax_s['inter-V'],ax_current=ax_s['inter-I'])
        if(auto_zoom_toggle.value == False):
            ax_s['V'].set_ylim(ax_s['inter-V'].get_ylim())
            ax_s['I'].set_ylim(ax_s['inter-I'].get_ylim())
    
    handle_input(Decimal('0'))


    def on_increment_click(b):
        time_slider.value += increment_text.value
        time = Decimal(str(time_slider.value))
        handle_input(time)
        
    def on_decrement_click(b):
        time_slider.value -= increment_text.value
        time = Decimal(str(time_slider.value))
        handle_input(time)
        
    def handle_slider_change(change):
        if(isinstance(change.new,dict)):
            if(len(change.new) > 0):
                time = Decimal(str(change.new['value']))
                handle_input(time)
                
    def update(b):
        time = Decimal(str(time_slider.value))
        handle_input(time)
                
                
    increment_button.on_click(on_increment_click)
    decrement_button.on_click(on_decrement_click)
    time_slider.observe(handle_slider_change)
    auto_zoom_toggle.observe(update)

    increment_grid = widgets.GridspecLayout(1,4)
    increment_grid[0,0] = decrement_button
    increment_grid[0,1] = increment_button
    increment_grid[0,2] = increment_text
    increment_grid[0,3] = auto_zoom_toggle

    display(increment_grid,time_slider)
    
    
def interact_interconnect_time_and_fanout_path(Interface : Data_Interface_Storage, is_Voltage:bool =True,padding:int =0):

    fig_path, ax_path = plt.subplot_mosaic([['INTER','INTER'],
                                            ['LF','CF']])
    
    if(is_Voltage):
        which_str_prefix = 'voltage '
        ax_voltage = ax_path['INTER']
        ax_current =False
    else:
        which_str_prefix = 'current '
        ax_voltage =False
        ax_current = ax_path['INTER']
        

    plot_time_interconnect_and_intercepts_at_time(0,Interface,ax_voltage=ax_voltage,ax_current=ax_current)
    plot_fanout_interconnect(Interface.data_output_multiplicative,ax_path['LF'],which_str_prefix+'inductor',padding=padding)
    plot_fanout_interconnect(Interface.data_output_multiplicative,ax_path['CF'],which_str_prefix+'capacitor',padding=padding)
    
    def remember_lims(axes):
        lims = []
        for ax in axes:
            lims.append((ax.get_xlim(),ax.get_ylim()))
            
        return lims
    
    def set_lims(axes,lims):
        for ax, lim in zip(axes,lims):
            ax.set_xlim(lim[0])
            ax.set_ylim(lim[1])

    def plot_path(t):
        
        lims = remember_lims(ax_path.values())
        clear_subplot(ax_path.values())
        set_lims(ax_path.values(),lims)
        
        plot_time_interconnect_and_intercepts_at_time(t,Interface,ax_voltage=ax_voltage,ax_current=ax_current)
        plot_fanout_interconnect(Interface.data_output_multiplicative,ax_path['LF'],which_str_prefix+'inductor',show_colour_bar=False,padding=padding)
        plot_fanout_interconnect(Interface.data_output_multiplicative,ax_path['CF'],which_str_prefix+'capacitor',show_colour_bar=False,padding=padding)
        plot_trace_on_merged_fanout_axis(Interface,ax_path['LF'],t,show_cross=True,padding=padding)
        plot_trace_on_merged_fanout_axis(Interface,ax_path['CF'],t,show_cross=True,padding=padding)
        
    inter = widgets.interact(plot_path,t=widgets.FloatSlider(min=0, max=float(Interface.data_input.Simulation_Stop_Time), step=0.1, value=0, layout=widgets.Layout(width='auto')))
    
    
def interact_3D_spatial(Interface : Data_Interface_Storage,**kwargs):
    
    default_kwargs ={
        'z_lim': False,
        'y_lim': False
    }
    
    kwargs = handle_default_kwargs(kwargs,default_kwargs)
    
    fig_3d = plt.figure()

    ax_3d = fig_3d.add_subplot(111,projection='3d')

    x_pos_lim_0 = -float(Interface.data_input.Capacitor_Length)
    x_pos_lim_1 = float(Interface.data_input.Inductor_Length)

    if(isinstance(kwargs['y_lim'],bool)):
        
        y_current_lim_0 = float(min([min(np.cumsum(Interface.data_output_ordered.Current_Interconnect_Inductor)),min(np.cumsum(Interface.data_output_ordered.Current_Interconnect_Capacitor))]))
        y_current_lim_1 = float(max([max(np.cumsum(Interface.data_output_ordered.Current_Interconnect_Inductor)),max(np.cumsum(Interface.data_output_ordered.Current_Interconnect_Capacitor))]))
    else:
        y_current_lim_0 = kwargs['y_lim'][0]
        y_current_lim_1 = kwargs['y_lim'][1]
        
    if(isinstance(kwargs['z_lim'],bool)):
        z_voltage_lim_0 = float(min([min(np.cumsum(Interface.data_output_ordered.Voltage_Interconnect_Inductor)),min(np.cumsum(Interface.data_output_ordered.Voltage_Interconnect_Capacitor))]))
        z_voltage_lim_1 = float(max([max(np.cumsum(Interface.data_output_ordered.Voltage_Interconnect_Inductor)),max(np.cumsum(Interface.data_output_ordered.Voltage_Interconnect_Capacitor))]))
    else:
        z_voltage_lim_0 = kwargs['z_lim'][0]
        z_voltage_lim_1 = kwargs['z_lim'][1]

    def interact_3D_func(t):
        ax_3d.clear()
        ax_3d.set_xlim(x_pos_lim_0,x_pos_lim_1)
        ax_3d.set_ylim(y_current_lim_1,y_current_lim_0)
        ax_3d.set_zlim(z_voltage_lim_0,z_voltage_lim_1)
        make_3d_spatial(str(t),Interface,ax_3d)
        
    inter = widgets.interact(interact_3D_func,t=widgets.FloatSlider(min=0, max=float(Interface.data_input.Simulation_Stop_Time), step=0.1, value=0, layout=widgets.Layout(width='auto')))