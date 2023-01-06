from Wavefront_Generation import Full_Cycle
from Wavefront_Plotting import make_fanout_wavefronts_all
import matplotlib.pyplot as plt

# simulate interface
interface = Full_Cycle(L_time='0.34' , C_time='0.12', L_impedance = '700', C_impedance = '7')

# make figure internally, 
# plot commutative inductive wavefronts
fig_ind,ax_ind = make_fanout_wavefronts_all(interface.data_output_commutative,True)

# plot commutative capacitive wavefronts
fig_cap,ax_cap = make_fanout_wavefronts_all(interface.data_output_commutative,False)

# make figure externally,
# put sending wavefronts left and returning wavefronts right
# show merged data

fig2_ind, ax2_ind = plt.subplot_mosaic([['IS','IR'],
                                        ['VS','VR']])
make_fanout_wavefronts_all(interface.data_output_multiplicative,True, ax=ax2_ind)

fig2_cap, ax2_cap = plt.subplot_mosaic([['IS','IR'],
                                        ['VS','VR']])
make_fanout_wavefronts_all(interface.data_output_multiplicative,False, ax=ax2_cap)

plt.show()
