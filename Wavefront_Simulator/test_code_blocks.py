from Wavefront_Storage import Data_Input_Storage
from Wavefront_Generation import Full_Cycle
from Wavefront_Plotting import make_time_interconnect_all
from copy import copy
from decimal import Decimal 
import builtins
import matplotlib.pyplot as plt

# generate a data input array
data_input_1 = Data_Input_Storage(L_time = '1',C_time='7')
# generate interface data storage object
interface_1 = Full_Cycle(data_input_1)

# create a copy of data_1
data_input_2 = copy(data_input_1)

# setup a new termination function
R = Decimal('10')
ZL = data_input_2.Inductor_Impedance
def new_inductor_termination_func(V_arrive,I_arrive):
    V_out = I_arrive * (1/(1/R + 1/ZL)) - V_arrive*ZL/(R +ZL )
    I_out = -(V_out/ZL)
    
    return V_out, I_out

# replace the old termination funciton
builtins.setattr(data_input_2, 'Termination_Event_Solver_Inductor',new_inductor_termination_func)

# generate interface data storage object unsing the altered data_input
interface_2 = Full_Cycle(data_input_2)

# plot data 
fig_1, axes_1 = make_time_interconnect_all(interface_1)
fig_2, axes_2 = make_time_interconnect_all(interface_2)

fig_1.suptitle("LC - Osscilator")
fig_2.suptitle("RC - Charger")
axes_2['VL'].set_title("Resistor Votlage at Interconnect")
axes_2['IL'].set_title("Resistor Current at Interconnect")

plt.show()