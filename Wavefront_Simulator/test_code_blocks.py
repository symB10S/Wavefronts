from Wavefront_Generation import Full_Cycle
from Wavefront_Plotting import save_spatial_interconnect
import matplotlib.pyplot as plt

# simulate interface
interface = Full_Cycle(L_time='0.34' , C_time='0.12', L_impedance = '700', C_impedance = '7')

# Make axes 
fig,ax = plt.subplots(2,1,figsize=(8,8))

# # make a handle for ordered data (very optional)
# data = interface.data_output_ordered

# # plot accumulated data on ax[0]
# plot_time_interconnect(data,ax[0],'current capacitor',True)

# # plot change data on ax[1], use 'interface' instead of 'data' (for fun)
# plot_time_interconnect(interface,ax[1],'current capacitor',False)

# plt.show()

save_spatial_interconnect(interface,video_runtime='1')