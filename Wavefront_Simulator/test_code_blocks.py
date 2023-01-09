from Wavefront_Generation import Full_Cycle
from Wavefront_Plotting import plot_trace_on_merged_fanout_axis, plot_fanout_interconnect
import matplotlib.pyplot as plt

# simulate an interface
interface_data = Full_Cycle(L_time = '3.6',C_time = '3.2')

fig, ax = plt.subplots()
plot_fanout_interconnect(interface_data.data_output_multiplicative,ax,'voltage capacitor')
plot_trace_on_merged_fanout_axis(interface_data,ax)
plt.show()