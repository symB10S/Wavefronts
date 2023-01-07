from Wavefront_Generation import Full_Cycle
from Wavefront_Misc import closest_event_to_time
from decimal import Decimal

# simulate random interface
interface = Full_Cycle(L_time='7' , C_time='3.4',show_about = False)

# handle for ordered time list
Time_arr = interface.data_output_ordered.Time
time_enquirey = Decimal('10.3')

# find closest event, can be after enquirey
i_after, t_after = closest_event_to_time(Time_arr,time_enquirey,True)
# find closest event, event must be before enquirey
i_before, t_before = closest_event_to_time(Time_arr,time_enquirey,False)

# the two closest times are 10.4 and 10.2 and time enquirey is 10.3
# 10.2 <--- 10.3 -> 10.4
print(f" time enquirey is {time_enquirey}")
print(f" best time if can be after {t_after} ") # returns 10.4
print(f" best time if must be before {t_before} ") # returns 10.2

# We can get the [ L , C ] coordiante by refernecing the 'Indexes' array

coord_after  = interface.data_output_ordered.Indexes[ i_after ]
coord_before = interface.data_output_ordered.Indexes[ i_before ]

print(f" [L , C] after  {coord_after} ") #  returns [1, 1]
print(f" [L , C] before {coord_before} ") # returns [0, 3]


# # plot accumulation wavefront activity for inductor
# fig,ax = make_time_wavefronts_all(interface,True,True)

# # plot the accumulation wavefront activity for capacitor
# # here we just pass the ax object as a kwarg so that it is plotted on the same axes
# make_time_wavefronts_all(interface,False,True,ax=ax)

# # rename the auto generated suptitle
# fig.suptitle('Comparison between accumulated wavefronts over time in each transmission line')

# # use the key word to set titles of each axis independantly 
# ax['VS'].set_title('Sending Voltage Wavefronts')
# ax['VR'].set_title('Returning Voltage Wavefronts')
# ax['IS'].set_title('Sending Current Wavefronts')
# ax['IR'].set_title('Returning Current Wavefronts')

# # plot a legend for all axes
# for ax_i in ax.values(): 
#     ax_i.legend(['Inductor', 'Capacitor'])

# plt.show()