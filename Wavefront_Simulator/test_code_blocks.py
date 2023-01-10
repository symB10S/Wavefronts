# from Wavefront_Storage import Data_Input_Storage
# from Wavefront_Generation import Full_Cycle
# from Wavefront_Plotting import make_time_interconnect_all, make_fanout_interconnect_all
# from copy import copy
# from decimal import Decimal 
# import builtins
# import matplotlib.pyplot as plt

# # generate a data input array
# data_input_1 = Data_Input_Storage(L_time = '13',C_time='7')
# # generate interface data storage object
# interface_1 = Full_Cycle(data_input_1)

# # create a copy of data_1
# data_input_2 = copy(data_input_1)

# # setup a new termination function
# R = Decimal('10')
# ZL = data_input_2.Inductor_Impedance
# def new_inductor_termination_func(V_arrive,I_arrive):
#     V_out = I_arrive * (1/(1/R + 1/ZL)) - V_arrive*ZL/(R +ZL )
#     I_out = -(V_out/ZL)
    
#     return V_out, I_out
# ZC = data_input_2.Capacitor_Impedance
# def new_capacitor_termination_func(V_arrive,I_arrive):
#     V_out = I_arrive * (1/(1/R + 1/ZC)) - V_arrive*ZC/(R +ZC )
#     I_out = -(V_out/ZC)
    
#     return V_out, I_out

# # replace the old termination funciton
# builtins.setattr(data_input_2, 'Termination_Event_Solver_Inductor',new_inductor_termination_func)
# builtins.setattr(data_input_2, 'Termination_Event_Solver_Capacitor',new_capacitor_termination_func)

# # generate interface data storage object unsing the altered data_input
# interface_2 = Full_Cycle(data_input_2)

# # plot data 
# fig_1, axes_1 = make_time_interconnect_all(interface_1)
# fig_2, axes_2 = make_time_interconnect_all(interface_2)

# fig_1.suptitle("LC - Osscilator")
# fig_2.suptitle("RC - Charger")
# axes_2['VL'].set_title("Resistor Votlage at Interconnect")
# axes_2['IL'].set_title("Resistor Current at Interconnect")

# make_fanout_interconnect_all(interface_1.data_output_multiplicative)
# make_fanout_interconnect_all(interface_2.data_output_multiplicative)

# plt.show()

from LTSpice_Simulator import get_Spice_Arrays
import matplotlib.pyplot as plt

# Do manual simulation
            
# Change Impedances and simulaiton timestep
LTSpice_Arrays = get_Spice_Arrays(L_impedance = '500',C_impedance = '20', Step_size='0.1')

# Plot Inductor votlage using Lumped circuit elements
plt.plot(LTSpice_Arrays['Time'],LTSpice_Arrays['Inductor_Voltage_Circuit'])
plt.title('Lumped Element analysis of Inductor Voltage')
plt.xlabel('time (s)')
plt.ylabel('Voltage (V)')
plt.show()
