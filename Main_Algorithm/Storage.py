from Circuit_Solver import Simulation_Stop_Time
from Wavefronts import *
from collections import deque


#Storage Arrays

Storage_Voltage_Active : Wavefront_Source = deque()
Storage_Capacitor_Active : Wavefront_Capacitive = deque()
Storage_Inductor_Active : Wavefront_Inductive = deque()

Storage_Capacitor_New : Wavefront_Capacitive = deque()
Storage_Inductor_New : Wavefront_Inductive = deque()

Storage_Voltage_Completed : Wavefront_Source = deque()
Storage_Capacitor_Completed : Wavefront_Capacitive = deque()
Storage_Inductor_Completed : Wavefront_Inductive = deque()

def Clear_Storage():
    Storage_Voltage_Active.clear()
    Storage_Capacitor_Active.clear()
    Storage_Inductor_Active.clear()

    Storage_Capacitor_New.clear()
    Storage_Inductor_New.clear()

    Storage_Voltage_Completed.clear()
    Storage_Capacitor_Completed.clear()
    Storage_Inductor_Completed.clear()

def Process_Active_Capacitor_Wavefronts():
    while len(Storage_Capacitor_Active) > 0:
        temp_wavefront = Storage_Capacitor_Active.popleft()

        if(temp_wavefront.time_start <= Simulation_Stop_Time):
            temp_wavefront.Generate(Storage_Inductor_Active,Storage_Capacitor_New)
            Storage_Capacitor_Completed.append(temp_wavefront)
        
    while len(Storage_Capacitor_New) > 0:
        temp_wavefront = Storage_Capacitor_New.popleft()

        if temp_wavefront.time_start <= Simulation_Stop_Time:
            Storage_Capacitor_Active.append(temp_wavefront)

    if(len(Storage_Capacitor_Active) > 0):
        Process_Active_Capacitor_Wavefronts()

def Process_Active_Inductor_Wavefronts():
    while len(Storage_Inductor_Active) > 0:
        temp_wavefront = Storage_Inductor_Active.popleft()

        if(temp_wavefront.time_start <= Simulation_Stop_Time):
            temp_wavefront.Generate(Storage_Inductor_New,Storage_Capacitor_Active)
            Storage_Inductor_Completed.append(temp_wavefront)
    
    while len(Storage_Inductor_New) > 0:
        temp_wavefront = Storage_Inductor_New.popleft()

        if temp_wavefront.time_start <= Simulation_Stop_Time:
            Storage_Inductor_Active.append(temp_wavefront)

    if(len(Storage_Inductor_Active) > 0):
        Process_Active_Inductor_Wavefronts()


def Process_Wavefronts():
    while(len(Storage_Inductor_Active) > 0 or  len(Storage_Capacitor_Active) > 0):
        Process_Active_Inductor_Wavefronts()
        Process_Active_Capacitor_Wavefronts()
