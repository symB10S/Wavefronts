import subprocess
from copy import copy
from Merge_Cartesian import handle_default_kwargs

LTSpice_exe_Path = 'C:\Program Files\LTC\LTspiceXVII\XVIIx64.exe'
Original_File = 'LC_Spice_Input.txt'


# Default Values found in provided .txt file
default_Spice_strings ={
    'L_impedance': 'ZL=100',
    'L_time': 'TL=1',
    'C_impedance': 'ZC=1',
    'C_time': 'TC=1',
    'number_periods': 'periods=1',
    'L_tot': 'Ltot=ZL*TL/2',
    'C_tot': 'Ctot=TC/(2*ZC)',
    'Stop_time': 'Stop_Time=2*periods*pi*sqrt(Ltot*Ctot)',
    'Step_size': 'Step_Size=0.01',
    'input_voltage': 'Vin=1'
}

# Alterations to Default Values
new_Spice_values = {
    'L_impedance':'50',
    'Stop_time':'100'}

altered_Spice_strings = copy(default_Spice_strings)

for new_key,new_value in new_Spice_values.items():
    if(default_Spice_strings.get(new_key) is None):
        # new value cannot be assinged
        raise ValueError(f"No setting found for {new_key}, here are the possible options: \n{default_Spice_strings}")
    else:
        # get default values and split to keep original name
        default_string = default_Spice_strings[new_key]
        parameter_name, parameter_default_value = default_string.split('=')
        
        new_string = parameter_name + '=' + new_value
        altered_Spice_strings[new_key] = new_string

print(default_Spice_strings)
print('\n')
print(altered_Spice_strings)
# subprocess.call(LTSpice_exe_Path + ' -b LC_Spice_Input.txt')