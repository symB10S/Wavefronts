from Wavefront_Generation import Full_Cycle
from Wavefront_Plotting import plot_time_wavefronts
import matplotlib.pyplot as plt

# Example, comparing the sending and returning current wavefronts in the capacitor:
# =================================================================================

# simulate interface
interface = Full_Cycle(L_time='3' , C_time='7', L_impedance = '700', C_impedance = '7')
data = interface.data_output_ordered

# Make axes 
fig,ax = plt.subplots()

# plot sending wavefronts (not accumulated)
plot_time_wavefronts(data,ax,'current capacitor',True,False)

# plot returning wavefronts (not accumulated)
plot_time_wavefronts(data,ax,'current capacitor',False,False)

plt.show()