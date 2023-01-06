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