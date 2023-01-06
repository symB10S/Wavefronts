from Wavefront_Generation import Full_Cycle
from Wavefront_Plotting import make_time_wavefronts_all
import matplotlib.pyplot as plt

# Example: Compare the accumulated wavefront behaviour over time between the capacitor and inductor
# =================================================================================================

# simulate interface
interface = Full_Cycle(L_time='7' , C_time='3.4', L_impedance = '654', C_impedance = '2.5')

# plot accumulation wavefront activity for inductor
fig,ax = make_time_wavefronts_all(interface,True,True)

# plot the accumulation wavefront activity for capacitor
# here we just pass the ax object as a kwarg so that it is plotted on the same axes
make_time_wavefronts_all(interface,False,True,ax=ax)

# rename the auto generated suptitle
fig.suptitle('Comparison between accumulated wavefronts over time in each transmission line')

# use the key word to set titles of each axis independantly 
ax['VS'].set_title('Sending Voltage Wavefronts')
ax['VR'].set_title('Returning Voltage Wavefronts')
ax['IS'].set_title('Sending Current Wavefronts')
ax['IR'].set_title('Returning Current Wavefronts')

# plot a legend for all axes
for ax_i in ax.values(): 
    ax_i.legend(['Inductor', 'Capacitor'])

plt.show()