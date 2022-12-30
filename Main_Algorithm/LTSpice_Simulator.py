"""A Module responsible getting LTSpice simulation data as for verification.
    Ensure that 'LTSpice_exe_Path' in this file points to your LTspice installation.
    Requires the the LC interface spice file template 'LC_Spice_Input.txt' which must be in the root directory.
"""

import subprocess
import ltspy3

# Path to installed LTSpice exe
LTSpice_exe_Path = 'C:\Program Files\LTC\LTspiceXVII\XVIIx64.exe'
# Name of provided parameterised LC interface template
Spice_File_Template = 'LC_Spice_Input.txt'
Spice_File_Altered = 'LC_Spice_Altered.txt'

# Default Parameters and values found in provided LC_Spice_Input.txt spice input file
default_Spice_parameters ={
    'L_impedance': '100',
    'L_time': '1',
    'C_impedance': '1',
    'C_time': '1',
    'number_periods': '1',
    'L_tot': 'L_impedance*L_time/2 ',
    'C_tot': 'C_time/(2*C_impedance)',
    'Simulation_stop_time': '2*number_periods*pi*sqrt(L_tot*C_tot)',
    'Step_size': '0.01',
    'V_source': '1'
}

def get_Spice_Arrays(**new_Spice_values):
    """Runs a LTSpice simulation on a Circuit theory LC interface as well as a distributed LC interface. Returns associated arrays.

    :param new_Spice_values: A set of key-value pairs used to configure the simulaiton.
    default values are as follows and will be overwritten with provided key-values.
    
    Default Parameters:
    
        'L_impedance': '100',
        'L_time': '1',
        'C_impedance': '1',
        'C_time': '1',
        'number_periods': '1',
        'L_tot': 'L_impedance*L_time/2 ',
        'C_tot': 'C_time/(2*C_impedance)',
        'Simulation_stop_time': '2*number_periods*pi*sqrt(L_tot*C_tot)',
        'Step_size': '0.01',
        'V_source': '1'
        
    Returns dictionary of output arrays:
    
        dict{ 
            "time",  
            "Inductor_Voltage_Circuit",  
            "Inductor_Current_Circuit",  
            "Capacitor_Voltage_Circuit",  
            "Capacitor_Current_Circuit",  
            "Inductor_Voltage_Tx",  
            "Inductor_Current_Tx",  
            "Capacitor_Voltage_Tx",  
            "Capacitor_Current_Tx"  
        }
    
    Example:
    =======
        only specify the default parameters you want to alter,
            
        # Change Impedances and simulaiton timestep
        
        LTSpice_Arrays = get_Spice_Arrays(L_impedance = '500',C_impedance = '20', Step_size='0.1'):
        
        # Plot Inductor votlage using Lumped circuit elements
        
        plt.plot(LTSpice_Arrays['time'],LTSpice_Arrays['Inductor_Voltage_Circuit']])
    """

    # read input SPICE file, replace paramters in file with provided values
    with open(Spice_File_Template, 'rb') as file:
        Data_Template = file.read()
        
        for new_key,new_value in new_Spice_values.items():
            if(default_Spice_parameters.get(new_key) is None):
                # new value cannot be found
                raise ValueError(f"No setting found for {new_key}, here are the possible options: \n{default_Spice_parameters}")
            else:
                # search string to find default value in template
                Spice_search_string = new_key+'='+default_Spice_parameters[new_key]
                # new string to replace with matched string
                Spice_new_string = new_key+'='+new_value
                
                Data_Template = Data_Template.replace(Spice_search_string.encode('ascii'),Spice_new_string.encode('ascii'))

    # create new SPICE directive with replaced values
    with open(Spice_File_Altered,'wb') as file:
        file.write(Data_Template)
        
    # run LTSpice on new SPICE directive
    subprocess.call(LTSpice_exe_Path + ' -b '+Spice_File_Altered)

    # Extract data from outputted .raw file from LTSpice execution
    data_out = ltspy3.SimData('LC_Spice_Altered.raw')

    names = data_out.variables
    values = data_out.values

    # get arrays -> "name in SPICE data"
    # "time"
    time = values[names.index(b"time")]

    # "V(l_node_circuit)" - "V(c_node_circuit)"
    Inductor_Voltage_Circuit = values[names.index(b"V(l_node_circuit)")] - values[names.index(b"V(c_node_circuit)")] 
    # "I(Inductor_circuit)"
    Inductor_Current_Circuit = values[names.index(b"I(Inductor_circuit)")]

    # "V(c_node_circuit)"
    Capacitor_Voltage_Circuit = values[names.index(b"V(c_node_circuit)")]
    # "I(Capacitor_circuit)"
    Capacitor_Current_Circuit = values[names.index(b"I(Capacitor_circuit)")]

    # "V(l_node_tx)" - "V(c_node_tx)"
    Inductor_Voltage_Tx = values[names.index(b"V(l_node_tx)")] - values[names.index(b"V(c_node_tx)")] 
    # "Ia(Inductor_tx)"
    Inductor_Current_Tx = values[names.index(b"Ia(Inductor_tx)")]

    # "V(c_node_tx)"
    Capacitor_Voltage_Tx = values[names.index(b"V(c_node_tx)")]
    # "Ia(Capacitor_tx)"
    Capacitor_Current_Tx = values[names.index(b"Ia(Capacitor_tx)")]
    
    return({
        "time":time,
        "Inductor_Voltage_Circuit":Inductor_Voltage_Circuit,
        "Inductor_Current_Circuit":Inductor_Current_Circuit,
        "Capacitor_Voltage_Circuit":Capacitor_Voltage_Circuit,
        "Capacitor_Current_Circuit":Capacitor_Current_Circuit,
        "Inductor_Voltage_Tx":Inductor_Voltage_Tx,
        "Inductor_Current_Tx":Inductor_Current_Tx,
        "Capacitor_Voltage_Tx":Capacitor_Voltage_Tx,
        "Capacitor_Current_Tx":Capacitor_Current_Tx,
    })