from Wavefront_Generation import Full_Cycle
from Wavefront_Plotting import plot_refelction_diagram
import matplotlib.pyplot as plt

# simulate interface
interface = Full_Cycle(L_time = '27',C_time = '32')

# create subplot
fig,ax = plt.subplots(1,2,figsize=(18,8))

# highlight sending wavefronts and make returning gray
c = 'dimgray'
plot_refelction_diagram(interface,ax[0],True, CR_colour=c, CR_style = '--', LR_colour=c, LR_style = '--')
plot_refelction_diagram(interface,ax[1],False, CR_colour=c, CR_style = '--', LR_colour=c, LR_style = '--')

plt.show()