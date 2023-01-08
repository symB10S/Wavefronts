from Wavefront_Generation import Full_Cycle
from Wavefront_Plotting import make_fanout_interconnect_all,plot_trace_on_merged_fanout_axis
import matplotlib.pyplot as plt

# simulate interface
interface = Full_Cycle(L_time='12' , C_time='8')

# make figure internally, plot commutative data
fig1,ax1 = make_fanout_interconnect_all(interface.data_output_commutative)
fig1.suptitle(f"commutative Fanouts") # customize title

# make figure externally, put currents left and voltages right
fig2, ax2 = plt.subplot_mosaic([['IL','VL'],
                                ['IC','VC']])

# pass ax2 to fucniton, also, show multiplicative data this time
make_fanout_interconnect_all(interface.data_output_multiplicative, ax=ax2)
plot_trace_on_merged_fanout_axis(interface,ax2['VL'])

fig2.suptitle(f"multiplicative Fanouts") # customize title

plt.show()