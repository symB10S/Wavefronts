import subprocess
import ltspy3
import matplotlib.pyplot as plt

LTSpice_exe_Path = 'C:\Program Files\LTC\LTspiceXVII\XVIIx64.exe'
Spice_File_Template = 'LC_Spice_Input.txt'
Spice_File_Altered = 'LC_Spice_Altered.txt'

# Default Values found in provided .txt file
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

# Alterations to Default Values
new_Spice_values = {
    'L_impedance':'50',
    'Simulation_stop_time':'10 00'}

altered_Spice_parameters = default_Spice_parameters.copy()

with open(Spice_File_Template, 'rb') as file:
    Data_Template = file.read()
    
    for new_key,new_value in new_Spice_values.items():
        if(default_Spice_parameters.get(new_key) is None):
            # new value cannot be found
            raise ValueError(f"No setting found for {new_key}, here are the possible options: \n{default_Spice_parameters}")
        else:
            # assign new value
            altered_Spice_parameters[new_key] = new_value
            # search string -> 'key=value' to match whole case
            Spice_search_string = new_key+'='+default_Spice_parameters[new_key]
            Spice_new_string = new_key+'='+new_value
            
            Data_Template = Data_Template.replace(Spice_search_string.encode('ascii'),Spice_new_string.encode('ascii'))

with open(Spice_File_Altered,'wb') as file:
    file.write(Data_Template)
    
    
subprocess.call(LTSpice_exe_Path + ' -b '+Spice_File_Altered)

data_out = ltspy3.SimData('LC_Spice_Altered.raw')

names = data_out.variables
values = data_out.values

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


plt.figure(1)
plt.plot(time,Capacitor_Current_Tx)
plt.plot(time,Inductor_Current_Circuit)
plt.show()