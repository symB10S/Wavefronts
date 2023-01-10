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