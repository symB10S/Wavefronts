from Circuit_Solver import Simulation_Stop_Time
from Wavefronts import *
from collections import deque

#Storage Arrays

Storage_Voltage_Active : Wavefront_Source = deque()

Storage_Voltage_Completed : Wavefront_Source = deque()
Storage_Capacitor_Completed : Wavefront_Capacitive = deque()
Storage_Inductor_Completed : Wavefront_Inductive = deque()

Storage_Away : Wavefront = deque()
Storage_Return : Wavefront = deque()


def Process_Wavefronts():

    is_Simulation_Completed = False

    while not is_Simulation_Completed:

        # Manage away waves, generate return waves

        is_Inductive = True

        while len(Storage_Away)> 0:
            temp_wavefront = Storage_Away.popleft()
            temp_wavefront.Generate(Storage_Return,Storage_Return)

            if(is_Inductive):
                Storage_Inductor_Completed.append(temp_wavefront)
            else:
                Storage_Capacitor_Completed.append(temp_wavefront)

            is_Inductive = not is_Inductive

        # Manage return waves, check simulation end criteria, generate and merge away waves

        ## Do this always for the first wave. It can *never merge.
        temp_wavefront = Storage_Return.popleft()

        if Inductor_Time <= Capacitor_Time:
            if temp_wavefront.time_start >= Simulation_Stop_Time:
                is_Simulation_Completed = True

        temp_wavefront.Generate(Storage_Away,Storage_Away)

        Storage_Inductor_Completed.append(temp_wavefront)

        while len(Storage_Return) > 0:

            temp_wavefront = Storage_Return.popleft()

            if len(Storage_Return) == 0 : # It is the last wave
                if(Capacitor_Time <= Inductor_Time and temp_wavefront.time_start >= Simulation_Stop_Time):
                    is_Simulation_Completed = True

                temp_wavefront.Generate(Storage_Away,Storage_Away)
                Storage_Capacitor_Completed.append(temp_wavefront)

            else: # It is not the last wave
                temp_next_wavefront = Storage_Return.popleft()

                temp_wavefront_inductive, temp_wavefront_capacitve = temp_wavefront.Generate_Return()
                temp_next_wavefront_inductive, temp_next_wavefront_capacitve = temp_next_wavefront.Generate_Return()

                temp_wavefront_inductive.Merge(temp_next_wavefront_inductive)
                temp_wavefront_capacitve.Merge(temp_next_wavefront_capacitve)

                Storage_Away.append(temp_wavefront_inductive)
                Storage_Away.append(temp_wavefront_capacitve)

                Storage_Capacitor_Completed.append(temp_wavefront)
                Storage_Inductor_Completed.append(temp_next_wavefront)


