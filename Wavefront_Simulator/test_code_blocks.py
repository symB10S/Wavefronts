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