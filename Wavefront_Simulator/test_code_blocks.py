from Wavefront_Generation import Full_Cycle
from Wavefront_Plotting import make_fanout_crossection
import matplotlib.pyplot as plt

# simulate interface
interface = Full_Cycle(L_time='3' , C_time='3' , L_impedance='700')

# make axes internally, intercept at L=25, C= 10
data = interface.data_output_ordered.Voltage_Interconnect_Capacitor
make_fanout_crossection(data, 25, 10, units='V')

# make axes externally, intercept at L=25, C= 10

fig, ax = plt.subplot_mosaic([['C','F'],
                              ['D','L']])

make_fanout_crossection(data, 25, 10, units='V', ax=ax)

plt.show()