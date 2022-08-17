from decimal import *
from collections import deque
import numpy as np
import math
from dataclasses import dataclass, fields
import matplotlib.cm as cm
import matplotlib.pyplot as plt
import copy

getcontext().traps[FloatOperation] = True

# Data Storage Classes
@dataclass
class Data_Input_Storage :
    Number_Periods  : Decimal
    Simulation_Stop_Time  : Decimal
    Is_Buck : bool

    Voltage_Souce_Magnitude  : Decimal
    Load_Resistance  : Decimal

    Inductor_Inductance_Per_Length  : Decimal
    Inductor_Capacitance_Per_Length  : Decimal
    Inductor_Length  : Decimal

    Capacitor_Inductance_Per_Length  : Decimal
    Capacitor_Capacitance_Per_Length  : Decimal
    Capacitor_Length  : Decimal

    Inductor_Total_Inductance  : Decimal
    Inductor_Total_Capacitance  : Decimal
    Inductor_Velocity  : Decimal
    Inductor_Time  : Decimal
    Inductor_Impedance  : Decimal

    Capacitor_Total_Inductance  : Decimal
    Capacitor_Total_Capacitance  : Decimal
    Capacitor_Velocity  : Decimal
    Capacitor_Time  : Decimal
    Capacitor_Impedance  : Decimal

    Load_Parallel_Inductor  : Decimal
    Load_Parallel_Capacitor  : Decimal

    Inductor_Solver_Term_VL   : Decimal
    Inductor_Solver_Term_VC   : Decimal
    Inductor_Solver_Term_IL   : Decimal
    Inductor_Solver_Term_IC   : Decimal
    Inductor_Solver_Term_VS   : Decimal

    Inductor_Solver_Term_VL_I   : Decimal
    Inductor_Solver_Term_VC_I   : Decimal
    Inductor_Solver_Term_IL_I   : Decimal
    Inductor_Solver_Term_IC_I   : Decimal
    Inductor_Solver_Term_VS_I   : Decimal

    Capacitor_Solver_Term_VC   : Decimal
    Capacitor_Solver_Term_VL   : Decimal
    Capacitor_Solver_Term_IC   : Decimal
    Capacitor_Solver_Term_IL   : Decimal
    Capacitor_Solver_Term_VS   : Decimal

    Capacitor_Solver_Term_VC_I   : Decimal
    Capacitor_Solver_Term_VL_I   : Decimal
    Capacitor_Solver_Term_IC_I   : Decimal
    Capacitor_Solver_Term_IL_I   : Decimal
    Capacitor_Solver_Term_VS_I   : Decimal

    Initial_Inductor_Voltage : Decimal
    Initial_Inductor_Current : Decimal
    Initial_Capacitor_Voltage : Decimal
    Initial_Capacitor_Current : Decimal

    GCD : Decimal
    LCM : Decimal
    Capacitor_LCM_Factor : int
    Inductor_LCM_Factor : int
    is_Higher_Merging : bool
    a : int
    b : int

    Number_of_Wavefronts : int
    Number_of_Layers : int
    
@dataclass
class Data_Output_Storage:
    Time : np.ndarray

    Voltage_Interconnect_Inductor : np.ndarray
    Current_Interconnect_Inductor : np.ndarray

    Voltage_Interconnect_Capacitor : np.ndarray
    Current_Interconnect_Capacitor : np.ndarray

    Wavefronts_Sending_Inductor : np.ndarray
    Wavefronts_Sending_Capacitor : np.ndarray

    Wavefronts_Returning_Inductor : np.ndarray
    Wavefronts_Returning_Capacitor : np.ndarray
    
@dataclass
class Data_Output_Storage_Ordered(Data_Output_Storage):
    Indexes : np.ndarray
    
    
def lcm_gcd(x:Decimal, y:Decimal):

    x_num,x_den = x.as_integer_ratio()
    y_num,y_den = y.as_integer_ratio()

    common_den = Decimal(str(x_den * y_den))

    x_big = x_num * y_den   
    y_big = y_num * x_den   
    
    GCD_big = Decimal(str(math.gcd(x_big,y_big)))

    GCD = GCD_big/common_den

    LCM = x*y/(GCD)
    
    return LCM, GCD

get_lcm_gcd = np.vectorize(lcm_gcd)

def delete_alternating(arr):
    
    x_len,ylen = arr.shape
    
    x_delete = np.arange(1,x_len,2)
    y_delete = np.arange(1,ylen,2)

    arr_deleted = np.delete(arr,x_delete, axis=0)
    arr_deleted = np.delete(arr_deleted,y_delete, axis=1)
    
    return arr_deleted

def Calculate_Variables(Inductor_List, Capacitor_List, Circuit_List):
    
    # INDUCTOR
    Inductor_Impedance = Decimal(Inductor_List[0])
    Inductor_Time = Decimal(Inductor_List[1])/2
    Inductor_Length = Decimal(Inductor_List[2])
    
    Inductor_Velocity = Inductor_Length/Inductor_Time
    Inductor_Inductance_Per_Length =  Inductor_Time*Inductor_Impedance
    Inductor_Capacitance_Per_Length =  Inductor_Time/Inductor_Impedance
    Inductor_Total_Inductance = Inductor_Inductance_Per_Length * Inductor_Length
    Inductor_Total_Capacitance = Inductor_Capacitance_Per_Length * Inductor_Length

    # CAPACITOR
    Capacitor_Impedance = Decimal(Capacitor_List[0])
    Capacitor_Time = Decimal(Capacitor_List[1])/2
    Capacitor_Length = Decimal(Capacitor_List[2])
    
    Capacitor_Velocity = Capacitor_Length/Capacitor_Time
    Capacitor_Inductance_Per_Length =  Capacitor_Time*Capacitor_Impedance
    Capacitor_Capacitance_Per_Length =  Capacitor_Time/Capacitor_Impedance
    Capacitor_Total_Inductance = Capacitor_Inductance_Per_Length * Capacitor_Length
    Capacitor_Total_Capacitance = Capacitor_Capacitance_Per_Length * Capacitor_Length

    # CIRCUIT
    Voltage_Souce_Magnitude = Decimal(Circuit_List[0])
    Number_Periods = Decimal(Circuit_List[1])
    Is_Buck = Circuit_List[2]
    Load_Resistance = Decimal(Circuit_List[3])

    Simulation_Stop_Time = Number_Periods*Decimal('6.28318530718')*(Decimal.sqrt(Capacitor_Total_Capacitance*Inductor_Total_Inductance))
    
    if (Capacitor_Time < Inductor_Time):
        Number_of_Layers = math.ceil(Simulation_Stop_Time/(Capacitor_Time*2))+1
    else:
        Number_of_Layers = math.ceil(Simulation_Stop_Time/(Inductor_Time*2))+1
    
    Number_of_Wavefronts = 0
    for i in range(0,Number_of_Layers+1):
        Number_of_Wavefronts = Number_of_Wavefronts + 4*i
    
    LCM, GCD = lcm_gcd(Inductor_Time*2,Capacitor_Time*2)
    
    Inductor_LCM_Factor = int((Capacitor_Time*2)/(GCD))
    Capacitor_LCM_Factor = int((Inductor_Time*2)/(GCD))
    
    a = Inductor_LCM_Factor
    b = Capacitor_LCM_Factor
    
    if(LCM > Simulation_Stop_Time):
        is_Higher_Merging = False
    else:
        is_Higher_Merging = True
    

    if(Is_Buck):
        Load_Parallel_Inductor = 1/(1/Load_Resistance + 1/Inductor_Impedance)
        Load_Parallel_Capacitor = 1/(1/Load_Resistance + 1/Capacitor_Impedance)

        Inductor_Solver_Term_VL  = Inductor_Impedance/( Inductor_Impedance + Load_Parallel_Capacitor )
        Inductor_Solver_Term_VC  = Load_Parallel_Inductor/( Capacitor_Impedance + Load_Parallel_Inductor )
        Inductor_Solver_Term_IL  = Capacitor_Impedance * Inductor_Impedance * Load_Resistance /(Load_Resistance*Inductor_Impedance + Load_Resistance*Capacitor_Impedance + Inductor_Impedance * Capacitor_Impedance)
        Inductor_Solver_Term_IC  = Inductor_Solver_Term_IL
        Inductor_Solver_Term_VS  = Inductor_Impedance / ( Inductor_Impedance + Load_Parallel_Capacitor )

        Inductor_Solver_Term_VL_I  = Inductor_Solver_Term_VL / Inductor_Impedance
        Inductor_Solver_Term_VC_I  = Inductor_Solver_Term_VC / Inductor_Impedance
        Inductor_Solver_Term_IL_I  = Inductor_Solver_Term_IL / Inductor_Impedance
        Inductor_Solver_Term_IC_I  = Inductor_Solver_Term_IC / Inductor_Impedance
        Inductor_Solver_Term_VS_I  = Inductor_Solver_Term_VS / Inductor_Impedance

        Capacitor_Solver_Term_VC  = Capacitor_Impedance/( Capacitor_Impedance + Load_Parallel_Inductor )
        Capacitor_Solver_Term_VL  = Load_Parallel_Capacitor/( Inductor_Impedance + Load_Parallel_Capacitor )
        Capacitor_Solver_Term_IC  = Capacitor_Impedance * Inductor_Impedance * Load_Resistance /(Load_Resistance*Inductor_Impedance + Load_Resistance*Capacitor_Impedance + Inductor_Impedance * Capacitor_Impedance)
        Capacitor_Solver_Term_IL  = Capacitor_Solver_Term_IC
        Capacitor_Solver_Term_VS  = Load_Parallel_Capacitor / ( Inductor_Impedance + Load_Parallel_Capacitor )

        Capacitor_Solver_Term_VC_I  = Capacitor_Solver_Term_VC / Capacitor_Impedance
        Capacitor_Solver_Term_VL_I  = Capacitor_Solver_Term_VL / Capacitor_Impedance
        Capacitor_Solver_Term_IC_I  = Capacitor_Solver_Term_IC / Capacitor_Impedance
        Capacitor_Solver_Term_IL_I  = Capacitor_Solver_Term_IL / Capacitor_Impedance
        Capacitor_Solver_Term_VS_I  = Capacitor_Solver_Term_VS / Capacitor_Impedance
        
        Initial_Inductor_Current = Voltage_Souce_Magnitude/(Inductor_Impedance + Load_Parallel_Capacitor)
        Initial_Inductor_Voltage = Initial_Inductor_Current * Inductor_Impedance
        
        Initial_Capacitor_Voltage = Initial_Inductor_Current * Load_Parallel_Capacitor
        Initial_Capacitor_Current = Initial_Capacitor_Voltage/Capacitor_Impedance
        
    else:
        Load_Parallel_Inductor = Inductor_Impedance
        Load_Parallel_Capacitor = Capacitor_Impedance

        Inductor_Solver_Term_VL  = Inductor_Impedance/( Inductor_Impedance + Capacitor_Impedance )
        Inductor_Solver_Term_VC  = Inductor_Impedance/( Inductor_Impedance + Capacitor_Impedance )
        Inductor_Solver_Term_IL  = Capacitor_Impedance * Inductor_Impedance /(Inductor_Impedance + Capacitor_Impedance )
        Inductor_Solver_Term_IC  = Inductor_Solver_Term_IL
        Inductor_Solver_Term_VS  = Inductor_Impedance / ( Inductor_Impedance + Capacitor_Impedance )

        Inductor_Solver_Term_VL_I  = Inductor_Solver_Term_VL / Inductor_Impedance
        Inductor_Solver_Term_VC_I  = Inductor_Solver_Term_VC / Inductor_Impedance
        Inductor_Solver_Term_IL_I  = Inductor_Solver_Term_IL / Inductor_Impedance
        Inductor_Solver_Term_IC_I  = Inductor_Solver_Term_IC / Inductor_Impedance
        Inductor_Solver_Term_VS_I  = Inductor_Solver_Term_VS / Inductor_Impedance

        Capacitor_Solver_Term_VC  = Capacitor_Impedance/( Capacitor_Impedance + Inductor_Impedance )
        Capacitor_Solver_Term_VL  = Capacitor_Impedance/( Inductor_Impedance + Capacitor_Impedance )
        Capacitor_Solver_Term_IC  = Capacitor_Impedance * Inductor_Impedance  /(Inductor_Impedance + Capacitor_Impedance )
        Capacitor_Solver_Term_IL  = Capacitor_Solver_Term_IC
        Capacitor_Solver_Term_VS  = Capacitor_Impedance / ( Inductor_Impedance + Capacitor_Impedance )

        Capacitor_Solver_Term_VC_I  = Capacitor_Solver_Term_VC / Capacitor_Impedance
        Capacitor_Solver_Term_VL_I  = Capacitor_Solver_Term_VL / Capacitor_Impedance
        Capacitor_Solver_Term_IC_I  = Capacitor_Solver_Term_IC / Capacitor_Impedance
        Capacitor_Solver_Term_IL_I  = Capacitor_Solver_Term_IL / Capacitor_Impedance
        Capacitor_Solver_Term_VS_I  = Capacitor_Solver_Term_VS / Capacitor_Impedance

        Initial_Inductor_Current = Voltage_Souce_Magnitude/(Inductor_Impedance + Capacitor_Impedance)
        Initial_Inductor_Voltage = Initial_Inductor_Current * Inductor_Impedance
        
        Initial_Capacitor_Current = Initial_Inductor_Current
        Initial_Capacitor_Voltage = Initial_Capacitor_Current* Capacitor_Impedance
               
    return Data_Input_Storage(Number_Periods
                                ,Simulation_Stop_Time 
                                ,Is_Buck
                                ,Voltage_Souce_Magnitude 
                                ,Load_Resistance 
                                ,Inductor_Inductance_Per_Length 
                                ,Inductor_Capacitance_Per_Length 
                                ,Inductor_Length 
                                ,Capacitor_Inductance_Per_Length 
                                ,Capacitor_Capacitance_Per_Length 
                                ,Capacitor_Length 
                                ,Inductor_Total_Inductance 
                                ,Inductor_Total_Capacitance 
                                ,Inductor_Velocity 
                                ,Inductor_Time 
                                ,Inductor_Impedance 
                                ,Capacitor_Total_Inductance 
                                ,Capacitor_Total_Capacitance 
                                ,Capacitor_Velocity 
                                ,Capacitor_Time 
                                ,Capacitor_Impedance 
                                ,Load_Parallel_Inductor 
                                ,Load_Parallel_Capacitor 
                                ,Inductor_Solver_Term_VL  
                                ,Inductor_Solver_Term_VC  
                                ,Inductor_Solver_Term_IL  
                                ,Inductor_Solver_Term_IC  
                                ,Inductor_Solver_Term_VS  
                                ,Inductor_Solver_Term_VL_I  
                                ,Inductor_Solver_Term_VC_I  
                                ,Inductor_Solver_Term_IL_I  
                                ,Inductor_Solver_Term_IC_I  
                                ,Inductor_Solver_Term_VS_I  
                                ,Capacitor_Solver_Term_VC  
                                ,Capacitor_Solver_Term_VL  
                                ,Capacitor_Solver_Term_IC  
                                ,Capacitor_Solver_Term_IL  
                                ,Capacitor_Solver_Term_VS  
                                ,Capacitor_Solver_Term_VC_I  
                                ,Capacitor_Solver_Term_VL_I  
                                ,Capacitor_Solver_Term_IC_I  
                                ,Capacitor_Solver_Term_IL_I  
                                ,Capacitor_Solver_Term_VS_I  
                                ,Initial_Inductor_Voltage
                                ,Initial_Inductor_Current
                                ,Initial_Capacitor_Voltage
                                ,Initial_Capacitor_Current
                                ,GCD
                                ,LCM
                                ,Capacitor_LCM_Factor
                                ,Inductor_LCM_Factor
                                ,is_Higher_Merging
                                ,a 
                                ,b
                                ,Number_of_Wavefronts
                                ,Number_of_Layers)
        
def multiplicative_merge_cycle(arr,a_factor,b_factor):
    
    def make_upper_and_lower(arr,b_factor):
        upper = arr[:,0:b_factor]
        lower = arr[:,b_factor:]
        
        padding_for_upper = np.full(lower.shape,0,dtype=lower.dtype)
        padding_for_lower = np.full(upper.shape,0,dtype=upper.dtype)
        
        upper= np.append(upper,padding_for_upper,axis=1)
        lower= np.append(lower,padding_for_lower,axis=1)
        
        return upper,lower
    
    def shif_and_pad_array_x(arr,number_lines):
    
        rolled_arr = np.roll(arr, number_lines, axis=0)
        
        left_arr = rolled_arr[0:number_lines,:]
        left_arr = np.full(left_arr.shape,0,dtype=left_arr.dtype)
        
        
        rolled_arr= np.delete(rolled_arr,np.arange(0,number_lines,1),axis=0)
        rolled_arr = np.append(left_arr,rolled_arr,axis=0)
        
        return rolled_arr
    
    upper_arr,lower_arr = make_upper_and_lower(arr,b_factor)
    arr_merge_ready = shif_and_pad_array_x(lower_arr,a_factor)
    
    arr_merged = upper_arr + arr_merge_ready
    
    return arr_merged

def multiplicative_merging(arr,a ,b ,number_of_layers):
    
    number_merge_cycles = math.ceil(number_of_layers/b) + 1
    
    for _ in range (0,number_merge_cycles):
        arr = multiplicative_merge_cycle(arr,a,b)

    return arr[:,0:b]

def About_Network(Data: Data_Input_Storage):
    print(f"\nInformation about this network : \n")


    print(f"\n- The Inductor -")
    print(f"{'Inductor Inductance Per Length :':<40}{Data.Inductor_Inductance_Per_Length}")
    print(f"{'Inductor Capacitance Per Length :':<40}{Data.Inductor_Capacitance_Per_Length}")
    print(f"{'Inductor Length :':<40}{Data.Inductor_Length}")
    print(f"{'Inductor Total Inductance :':<40}{Data.Inductor_Total_Inductance}")
    print(f"{'Inductor Total Capacitance :':<40}{Data.Inductor_Total_Capacitance}")
    print(f"{'Inductor Velocity :':<40}{Data.Inductor_Velocity}")
    print(f"{'Inductor Time Delay :':<40}{Data.Inductor_Time}")
    print(f"{'Inductor Impedance :':<40}{Data.Inductor_Impedance}")
    

    print(f"\n- The Capacitor -")
    print(f"{'Capacitor Inductance Per Length :':<40}{Data.Capacitor_Inductance_Per_Length}")
    print(f"{'Capacitor Capacitance Per Length :':<40}{Data.Capacitor_Capacitance_Per_Length}")
    print(f"{'Capacitor Length :':<40}{Data.Capacitor_Length}")
    print(f"{'Capacitor Total Inductance :':<40}{Data.Capacitor_Total_Inductance}")
    print(f"{'Capacitor Total Capacitance :':<40}{Data.Capacitor_Total_Capacitance}")
    print(f"{'Capacitor Velocity :':<40}{Data.Capacitor_Velocity}")
    print(f"{'Capacitor Time Delay :':<40}{Data.Capacitor_Time}")
    print(f"{'Capacitor Impedance :':<40}{Data.Capacitor_Impedance}")
    
    print(f"\n- The Time -")
    print(f"{'Number Periods :':<40}{Data.Number_Periods}")
    print(f"{'Simulation Stop Time :':<40}{Data.Simulation_Stop_Time}")
    print(f"{'Number of Wavefronts :':<40}{Data.Number_of_Wavefronts}")
    print(f"{'Number of Layers :':<40}{Data.Number_of_Layers}")
    print(f"{'A :':<40}{Data.Inductor_Time}")
    print(f"{'B :':<40}{Data.Capacitor_Time}")
    print(f"{'a :':<40}{Data.Inductor_LCM_Factor}")
    print(f"{'b :':<40}{Data.Capacitor_LCM_Factor}")
    print(f"{'LCM :':<40}{Data.LCM}")
    print(f"{'GCD :':<40}{Data.GCD}")
    print(f"{'Higher Merging? :':<40}{Data.is_Higher_Merging}")
    

    print(f"\n- The Circuit -")
    print(f"{'Votage Source Magnitude :':<40}{Data.Voltage_Souce_Magnitude}")
    print(f"{'Buck Converter :':<40}{Data.Is_Buck}")
    print(f"{'Load Resistance :':<40}{Data.Load_Resistance}")

def Higher_Order_Merging(Data_Inputs : Data_Input_Storage,Data_Outputs : Data_Output_Storage):
    if(Data_Inputs.is_Higher_Merging):
        Voltage_Interconnect_Inductor_merged = multiplicative_merging(Data_Outputs.Voltage_Interconnect_Inductor,Data_Inputs.a,Data_Inputs.b,Data_Inputs.Number_of_Layers)
        Current_Interconnect_Inductor_merged = multiplicative_merging(Data_Outputs.Current_Interconnect_Inductor,Data_Inputs.a,Data_Inputs.b,Data_Inputs.Number_of_Layers)
        
        Voltage_Interconnect_Capacitor_merged = multiplicative_merging(Data_Outputs.Voltage_Interconnect_Capacitor,Data_Inputs.a,Data_Inputs.b,Data_Inputs.Number_of_Layers)
        Current_Interconnect_Capacitor_merged = multiplicative_merging(Data_Outputs.Current_Interconnect_Capacitor,Data_Inputs.a,Data_Inputs.b,Data_Inputs.Number_of_Layers)
        
        Wavefronts_Sending_Inductor_merged = multiplicative_merging(Data_Outputs.Wavefronts_Sending_Inductor,Data_Inputs.a,Data_Inputs.b,Data_Inputs.Number_of_Layers)
        Wavefronts_Sending_Capacitor_merged = multiplicative_merging(Data_Outputs.Wavefronts_Sending_Capacitor,Data_Inputs.a,Data_Inputs.b,Data_Inputs.Number_of_Layers)

        Wavefronts_Returning_Inductor_merged = multiplicative_merging(Data_Outputs.Wavefronts_Returning_Inductor,Data_Inputs.a,Data_Inputs.b,Data_Inputs.Number_of_Layers)
        Wavefronts_Returning_Capacitor_merged = multiplicative_merging(Data_Outputs.Wavefronts_Returning_Capacitor,Data_Inputs.a,Data_Inputs.b,Data_Inputs.Number_of_Layers)
    else:
        Voltage_Interconnect_Inductor_merged = Data_Outputs.Voltage_Interconnect_Inductor
        Current_Interconnect_Inductor_merged = Data_Outputs.Current_Interconnect_Inductor
        
        Voltage_Interconnect_Capacitor_merged = Data_Outputs.Voltage_Interconnect_Capacitor
        Current_Interconnect_Capacitor_merged = Data_Outputs.Current_Interconnect_Capacitor
        
        Wavefronts_Sending_Inductor_merged = Data_Outputs.Wavefronts_Sending_Inductor
        Wavefronts_Sending_Capacitor_merged = Data_Outputs.Wavefronts_Sending_Capacitor

        Wavefronts_Returning_Inductor_merged = Data_Outputs.Wavefronts_Returning_Inductor
        Wavefronts_Returning_Capacitor_merged = Data_Outputs.Wavefronts_Returning_Capacitor
    
    Time_cut = Data_Outputs.Time[:,0:Data_Inputs.b]
    
    return Data_Output_Storage(
        Time_cut,
        Voltage_Interconnect_Inductor_merged ,
        Current_Interconnect_Inductor_merged ,
        Voltage_Interconnect_Capacitor_merged ,
        Current_Interconnect_Capacitor_merged ,
        Wavefronts_Sending_Inductor_merged ,
        Wavefronts_Sending_Capacitor_merged ,
        Wavefronts_Returning_Inductor_merged ,
        Wavefronts_Returning_Capacitor_merged 
    )

def Order_Data_Output_Merged(Data_Input : Data_Input_Storage , Data_Output_Merged : Data_Output_Storage):
    
    def store_options(input_arr,x,y,magnitude,indexes):
        x_size,y_size = input_arr.shape
        
        
        if(x+1 < x_size and Marked[x+1,y] == 0):
            
            option_a = input_arr[x+1,y]
            magnitude.append(option_a)
            indexes.append([x+1,y])
            Marked[x+1,y] = 1
        
        if(y+1 < y_size and Marked[x,y+1] == 0):
            
            option_b = input_arr[x,y+1]
            magnitude.append(option_b)
            indexes.append([x,y+1])
            Marked[x,y+1] = 1
        
    def get_best_option_value_index(opt_arr,opt_indexes):
        opt_index_min = np.argmin(opt_arr)
        
        value = opt_arr[opt_index_min]
        del opt_arr[opt_index_min]
        
        index = opt_indexes[opt_index_min]
        del opt_indexes[opt_index_min]
        
        return value, index
    
    # Orderded Data Structure
    out_time = []

    out_voltage_inductor = []
    out_current_inductor = []
    out_voltage_capacitor = []
    out_current_capacitor = []

    out_wavefront_sending_inductor = []
    out_wavefront_sending_capacitor = []
    
    out_wavefront_returning_inductor = []
    out_wavefront_returning_capacitor = []

    out_indexes = []

    # Ordering Utilities
    latest_time = 0

    x_index = 0
    y_index = 0

    option_time = []
    option_indexes =[]
    Marked = np.zeros(Data_Output_Merged.Time.shape, dtype=Data_Output_Merged.Time.dtype)

    # Store Initial Point
    out_time.append(Data_Output_Merged.Time[0,0])
    out_indexes.append([0,0])

    out_voltage_inductor.append(Data_Output_Merged.Voltage_Interconnect_Inductor[0,0])
    out_current_inductor.append(Data_Output_Merged.Current_Interconnect_Inductor[0,0])

    out_voltage_capacitor.append(Data_Output_Merged.Voltage_Interconnect_Capacitor[0,0])
    out_current_capacitor.append(Data_Output_Merged.Current_Interconnect_Capacitor[0,0])
    
    out_wavefront_sending_inductor.append(Data_Output_Merged.Wavefronts_Sending_Inductor[0,0])
    out_wavefront_sending_capacitor.append(Data_Output_Merged.Wavefronts_Sending_Capacitor[0,0])
    
    out_wavefront_returning_inductor.append(Data_Output_Merged.Wavefronts_Returning_Inductor[0,0])
    out_wavefront_returning_capacitor.append(Data_Output_Merged.Wavefronts_Returning_Capacitor[0,0])

    Marked[0,0] = 1

    while latest_time <= Data_Input.Simulation_Stop_Time:
        
        # store options at location
        store_options(Data_Output_Merged.Time,x_index,y_index,option_time,option_indexes)
        
        
        if(len(option_time) > 0):
            # get best option
            best_time, best_time_index = get_best_option_value_index(option_time,option_indexes)
            
            out_time.append(best_time)
            out_indexes.append(best_time_index)
            
            out_voltage_inductor.append(Data_Output_Merged.Voltage_Interconnect_Inductor[best_time_index[0],best_time_index[1]])
            out_current_inductor.append(Data_Output_Merged.Current_Interconnect_Inductor[best_time_index[0],best_time_index[1]])
            
            out_voltage_capacitor.append(Data_Output_Merged.Voltage_Interconnect_Capacitor[best_time_index[0],best_time_index[1]] )
            out_current_capacitor.append(Data_Output_Merged.Current_Interconnect_Capacitor[best_time_index[0],best_time_index[1]] )
            
            Marked[best_time_index[0],best_time_index[1]]  = 2
        
        latest_time = best_time
        x_index, y_index = best_time_index
    
    if(Data_Input.is_Higher_Merging):
        
        max_index = np.max([x[0] for x in out_indexes])
        max_index += 1
        
        Data_Output_Merged.Time = Data_Output_Merged.Time[0:max_index,:]

        Data_Output_Merged.Voltage_Interconnect_Inductor =  Data_Output_Merged.Voltage_Interconnect_Inductor[0:max_index,:]
        Data_Output_Merged.Current_Interconnect_Inductor = Data_Output_Merged.Current_Interconnect_Inductor[0:max_index,:]

        Data_Output_Merged.Voltage_Interconnect_Capacitor = Data_Output_Merged.Voltage_Interconnect_Capacitor[0:max_index,:]
        Data_Output_Merged.Current_Interconnect_Capacitor = Data_Output_Merged.Current_Interconnect_Capacitor[0:max_index,:]

        Data_Output_Merged.Wavefronts_Sending_Inductor = Data_Output_Merged.Wavefronts_Sending_Inductor[0:max_index,:]
        Data_Output_Merged.Wavefronts_Sending_Capacitor = Data_Output_Merged.Wavefronts_Sending_Capacitor[0:max_index,:]

        Data_Output_Merged.Wavefronts_Returning_Inductor = Data_Output_Merged.Wavefronts_Returning_Inductor[0:max_index,:]
        Data_Output_Merged.Wavefronts_Returning_Capacitor = Data_Output_Merged.Wavefronts_Returning_Capacitor[0:max_index,:]
            
        
    return Data_Output_Storage_Ordered(
        out_time ,
        out_voltage_inductor ,
        out_current_inductor ,
        out_voltage_capacitor ,
        out_current_capacitor ,
        out_wavefront_sending_inductor ,
        out_wavefront_sending_capacitor ,
        out_wavefront_returning_inductor ,
        out_wavefront_returning_capacitor ,
        out_indexes
    )        

def Process_Wavefronts(Inductor_List, Capacitor_List, Circuit_List):

    data_input_storage = Calculate_Variables(Inductor_List, Capacitor_List, Circuit_List)
    About_Network(data_input_storage)
    
    def Circuit_Solver_Inductor_Voltage(VL,IL,VC,IC):
        return -VL * data_input_storage.Inductor_Solver_Term_VL - VC * data_input_storage.Inductor_Solver_Term_VC - IL * data_input_storage.Inductor_Solver_Term_IL + IC * data_input_storage.Inductor_Solver_Term_IC 

    def Circuit_Solver_Inductor_Current(VL,IL,VC,IC):
        return -VL * data_input_storage.Inductor_Solver_Term_VL_I - VC * data_input_storage.Inductor_Solver_Term_VC_I - IL * data_input_storage.Inductor_Solver_Term_IL_I + IC * data_input_storage.Inductor_Solver_Term_IC_I 

    def Circuit_Solver_Inductor_Source_Voltage(VS):
        return VS * data_input_storage.Inductor_Solver_Term_VS

    def Circuit_Solver_Inductor_Source_Current(VS):
        return VS * data_input_storage.Inductor_Solver_Term_VS_I

    def Circuit_Solver_Capacitor_Voltage(VL,IL,VC,IC):
        return -VC * data_input_storage.Capacitor_Solver_Term_VC - VL * data_input_storage.Capacitor_Solver_Term_VL - IC * data_input_storage.Capacitor_Solver_Term_IC + IL * data_input_storage.Capacitor_Solver_Term_IL 

    def Circuit_Solver_Capacitor_Current(VL,IL,VC,IC):
        return -VC * data_input_storage.Capacitor_Solver_Term_VC_I - VL * data_input_storage.Capacitor_Solver_Term_VL_I - IC * data_input_storage.Capacitor_Solver_Term_IC_I + IL * data_input_storage.Capacitor_Solver_Term_IL_I 

    def Circuit_Solver_Capacitor_Source_Voltage(VS):
        return VS * data_input_storage.Capacitor_Solver_Term_VS

    def Circuit_Solver_Capacitor_Source_Current(VS):
        return VS * data_input_storage.Capacitor_Solver_Term_VS_I
    
    class Wavefront:
        velocity = Decimal()
        length = Decimal()
        
        position_start = Decimal()
        position_end = Decimal()

        time_start = Decimal()
        time_end = Decimal()

        magnitude_voltage = Decimal()
        magnitude_current = Decimal()

        excitation_event_type = Decimal()
        excitation_event_number = Decimal()
        
        def __add__(self, Wavefront_add ):
            
            if(Wavefront_add == 0):
                pass
            elif(self.time_start == 0 and self.time_end == 0 ):
                pass
            elif(Wavefront_add.time_start == 0 and Wavefront_add.time_end == 0 ):
                pass
            elif(Wavefront_add.time_start == self.time_start and Wavefront_add.time_end == self.time_end ):
                self.magnitude_voltage += Wavefront_add.magnitude_voltage
                self.magnitude_current += Wavefront_add.magnitude_current
            else:
                raise Exception("Wavefronts cannot be added")
            
            return self
            
        def __radd__(self, Wavefront_add ):
            return self.__add__(Wavefront_add)
            
        def about(self) :
            print("\nSome Information about a wavefront")
            print(f"{'Type :':<35}{type(self)}")
            print(f"{'Poisiton Start :':<35}{self.position_start}")
            print(f"{'Poisiton End :':<35}{self.position_end}")
            print(f"{'Time Start :':<35}{self.time_start}")
            print(f"{'Time End :':<35}{self.time_end}")
            print(f"{'Voltage Magnitude :':<35}{self.magnitude_voltage}")
            print(f"{'Current Magnitude :':<35}{self.magnitude_current}")
            print(f"{'Excitation Type :':<35}{'HIGH' if self.excitation_event_type else 'LOW' }")
            print(f"{'Excitation Number :':<35}{self.excitation_event_number}")
        
        def Time_at_position(self,position):
            x = Decimal(position)

            if self.position_start == 0 :
                return (self.time_start + x/self.velocity)
            else:
                return (self.time_start + (self.length -x)/self.velocity)

        def Position_at_time(self,time):
            t = Decimal(time)

            if self.time_start <= t <= self.time_end:
                if self.position_start == 0 :
                    return (t-self.time_start)*self.velocity
                else:
                    return self.length - (t-self.time_start)*self.velocity
            else:
                return -1

    class Wavefront_Source( Wavefront ):

        def __init__(self,magnitude,time_start,time_end,excitation_number):
            
            self.length = Decimal(0)

            self.position_start = Decimal(0)
            self.position_end = Decimal(0)

            self.time_start = Decimal(time_start)
            self.time_end = Decimal(time_end)

            self.magnitude_voltage = Decimal(magnitude)
            self.magnitude_current = Decimal(0)

            if magnitude > 0:
                self.excitation_event_type = True
            else :
                self.excitation_event_type = False

            self.excitation_event_number = excitation_number

        def Generate(self, Wavefront_Storage : list):
            Wavefront_Storage.append(Wavefront_Inductive(self,False))
            Wavefront_Storage.append(Wavefront_Capacitive(self,False))
            
    class Wavefront_Capacitive( Wavefront ):

        def __init__(self, Wavefront_Parent : Wavefront, is_reflection : bool):
            
            self.velocity = data_input_storage.Capacitor_Velocity
            self.length = data_input_storage.Capacitor_Length

            self.position_start = Wavefront_Parent.position_end

            self.time_start = Wavefront_Parent.time_end
            self.time_end = self.time_start + data_input_storage.Capacitor_Time

            if self.position_start == 0:

                self.position_end = data_input_storage.Capacitor_Length

                if is_reflection: # A reflected wave at source side   |<--

                    self.magnitude_voltage = Circuit_Solver_Capacitor_Voltage(0, 0, Wavefront_Parent.magnitude_voltage, Wavefront_Parent.magnitude_current)
                    self.magnitude_current = Circuit_Solver_Capacitor_Current(0, 0, Wavefront_Parent.magnitude_voltage, Wavefront_Parent.magnitude_current)

                elif isinstance(Wavefront_Parent, Wavefront_Source) : # A generate source wave (Vs)-|->

                    self.time_start = Wavefront_Parent.time_start
                    self.time_end = self.time_start + data_input_storage.Capacitor_Time

                    self.magnitude_voltage = Circuit_Solver_Capacitor_Source_Voltage(Wavefront_Parent.magnitude_voltage)
                    self.magnitude_current = Circuit_Solver_Capacitor_Source_Current(Wavefront_Parent.magnitude_voltage)

                else: # A transmitted wave at source side  -|->

                    self.magnitude_voltage = Circuit_Solver_Capacitor_Voltage(Wavefront_Parent.magnitude_voltage, Wavefront_Parent.magnitude_current, 0, 0)
                    self.magnitude_current = Circuit_Solver_Capacitor_Current(Wavefront_Parent.magnitude_voltage, Wavefront_Parent.magnitude_current, 0, 0)

            else: # A reflected wave at load side   -->|

                self.position_end = 0

                self.magnitude_voltage = Wavefront_Parent.magnitude_voltage
                self.magnitude_current = - Wavefront_Parent.magnitude_current

            self.excitation_event_type = Wavefront_Parent.excitation_event_type
            self.excitation_event_number = Wavefront_Parent.excitation_event_number

        def Generate(self, Wavefront_Storage):
            if self.position_end == 0:
                Wavefront_Storage.append(Wavefront_Inductive(self,False))
                Wavefront_Storage.append(Wavefront_Capacitive(self,True))
            else:
                Wavefront_Storage.append(Wavefront_Capacitive(self,True))
        
        def Generate_Return(self):
            if self.position_end == 0:
                return Wavefront_Inductive(self,False), Wavefront_Capacitive(self,True)
            else :
                return Wavefront_Capacitive(self,True)

        def Merge(self, Wavefront_Other : Wavefront):
            self.magnitude_voltage = self.magnitude_voltage + Wavefront_Other.magnitude_voltage
            self.magnitude_current = self.magnitude_current + Wavefront_Other.magnitude_current

    class Wavefront_Inductive( Wavefront ):

        def __init__(self, Wavefront_Parent : Wavefront, is_reflection : bool):
            
            self.velocity = data_input_storage.Inductor_Velocity
            self.length = data_input_storage.Inductor_Length

            self.position_start = Wavefront_Parent.position_end

            self.time_start = Wavefront_Parent.time_end
            self.time_end = self.time_start + data_input_storage.Inductor_Time

            if self.position_start == 0:

                self.position_end = data_input_storage.Inductor_Length

                if is_reflection: # A reflected wave at source side   |<--

                    self.magnitude_voltage = Circuit_Solver_Inductor_Voltage( Wavefront_Parent.magnitude_voltage, Wavefront_Parent.magnitude_current, 0, 0)
                    self.magnitude_current = Circuit_Solver_Inductor_Current( Wavefront_Parent.magnitude_voltage, Wavefront_Parent.magnitude_current, 0, 0)

                elif isinstance(Wavefront_Parent, Wavefront_Source) : # A generate source wave (Vs)-|->

                    self.time_start = Wavefront_Parent.time_start
                    self.time_end = self.time_start + data_input_storage.Inductor_Time

                    self.magnitude_voltage = Circuit_Solver_Inductor_Source_Voltage(Wavefront_Parent.magnitude_voltage)
                    self.magnitude_current = Circuit_Solver_Inductor_Source_Current(Wavefront_Parent.magnitude_voltage)
                    
                else: # A transmitted wave at source side  -|->

                    self.magnitude_voltage = Circuit_Solver_Inductor_Voltage(0, 0, Wavefront_Parent.magnitude_voltage, Wavefront_Parent.magnitude_current)
                    self.magnitude_current = Circuit_Solver_Inductor_Current(0, 0, Wavefront_Parent.magnitude_voltage, Wavefront_Parent.magnitude_current)

            else: # A reflected wave at load side   -->|
                
                self.position_end = 0

                self.magnitude_voltage = - Wavefront_Parent.magnitude_voltage
                self.magnitude_current = Wavefront_Parent.magnitude_current

            self.excitation_event_type = Wavefront_Parent.excitation_event_type
            self.excitation_event_number = Wavefront_Parent.excitation_event_number

        def Generate(self, Wavefront_Storage):
            if self.position_end == 0:
                Wavefront_Storage.append(Wavefront_Inductive(self,True))
                Wavefront_Storage.append(Wavefront_Capacitive(self,False))
            else :
                Wavefront_Storage.append(Wavefront_Inductive(self,True))

        def Generate_Return(self):
            if self.position_end == 0:
                return Wavefront_Inductive(self,True), Wavefront_Capacitive(self,False)
            else :
                return Wavefront_Inductive(self,True)

        def Merge(self, Wavefront_Other : Wavefront):
            self.magnitude_voltage = self.magnitude_voltage + Wavefront_Other.magnitude_voltage
            self.magnitude_current = self.magnitude_current + Wavefront_Other.magnitude_current

    #Storage Arrays
    Storage_Voltage_Active : Wavefront_Source = deque()
    Storage_Voltage_Completed : Wavefront_Source = deque()
    Storage_Capacitor_Completed : Wavefront_Capacitive = deque()
    Storage_Inductor_Completed : Wavefront_Inductive = deque()

    Storage_Away : Wavefront = deque()
    Storage_Return : Wavefront = deque()
    
    Wavefronts_Away = np.full((2*(data_input_storage.Number_of_Layers+1),2*(data_input_storage.Number_of_Layers+1)),Wavefront_Source(0,0,0,0))
    Wavefronts_Return = np.full((2*(data_input_storage.Number_of_Layers+1),2*(data_input_storage.Number_of_Layers+1)),Wavefront_Source(0,0,0,0))
    
    Cartesian_Time = np.full((2*(data_input_storage.Number_of_Layers+1),2*(data_input_storage.Number_of_Layers+1)),Decimal('0'))
    
    Voltage_Interconnect_Inductor = np.full((2*(data_input_storage.Number_of_Layers+1),2*(data_input_storage.Number_of_Layers+1)),Decimal('0'))
    Current_Interconnect_Inductor = np.full((2*(data_input_storage.Number_of_Layers+1),2*(data_input_storage.Number_of_Layers+1)),Decimal('0'))

    Voltage_Interconnect_Capacitor = np.full((2*(data_input_storage.Number_of_Layers+1),2*(data_input_storage.Number_of_Layers+1)),Decimal('0'))
    Current_Interconnect_Capacitor = np.full((2*(data_input_storage.Number_of_Layers+1),2*(data_input_storage.Number_of_Layers+1)),Decimal('0'))
    
    Wavefronts_Sending_Inductor = np.full((2*(data_input_storage.Number_of_Layers+1),2*(data_input_storage.Number_of_Layers+1)), Wavefront_Source(0,0,0,0))
    Wavefronts_Sending_Capacitor = np.full((2*(data_input_storage.Number_of_Layers+1),2*(data_input_storage.Number_of_Layers+1)), Wavefront_Source(0,0,0,0))
    
    Wavefronts_Returning_Inductor = np.full((2*(data_input_storage.Number_of_Layers+1),2*(data_input_storage.Number_of_Layers+1)), Wavefront_Source(0,0,0,0))
    Wavefronts_Returning_Capacitor = np.full((2*(data_input_storage.Number_of_Layers+1),2*(data_input_storage.Number_of_Layers+1)), Wavefront_Source(0,0,0,0))
    
    ## LAYER 0
    # Generate Intial Away Waves
    Storage_Voltage_Active.append(Wavefront_Source(data_input_storage.Voltage_Souce_Magnitude,0,0,0))
    temp_wavefront = Storage_Voltage_Active.popleft()
    
    temp_wavefront.Generate(Storage_Away)
    Storage_Voltage_Completed.append(temp_wavefront)
    
    # Generate Intial Return Waves, Store Away Waves
    # Get First Sending Intial Inductive wavefront
    temp_wavefront_inductive = Storage_Away.popleft()
    temp_wavefront_inductive.Generate(Storage_Return)
    Storage_Inductor_Completed.append(temp_wavefront_inductive)
    Wavefronts_Away[1,0] = temp_wavefront_inductive
    Cartesian_Time[1-1,0] = temp_wavefront_inductive.time_start
    
    # Get Next Sending Initial Capacitive wavefront
    temp_wavefront_capacitive = Storage_Away.popleft()
    temp_wavefront_capacitive.Generate(Storage_Return)
    Storage_Capacitor_Completed.append(temp_wavefront_capacitive)
    Wavefronts_Away[0,1] = temp_wavefront_capacitive

    # Merge_Algorithm
    for layer_number in range(1,data_input_storage.Number_of_Layers):

        # Manage return waves
        
        ## Set Index    
        Cartesian_Index_x = 2*layer_number-1
        Cartesian_Index_y = 0
        
        # Get first Returning inductive wavefront 
        temp_wavefront = Storage_Return.popleft()

        # Generate Away Waves, Store Return Waves
        ## First wavefront does not merge:
        temp_wavefront.Generate(Storage_Away)
        
        Storage_Inductor_Completed.append(temp_wavefront)
        Wavefronts_Return[Cartesian_Index_x,Cartesian_Index_y] = temp_wavefront
        Cartesian_Index_x = Cartesian_Index_x - 1
        Cartesian_Index_y = Cartesian_Index_y + 1
        
        while len(Storage_Return) > 0:
            
            # Get a Returning wavefront (will be capacitve)
            temp_wavefront = Storage_Return.popleft()
            
            if len(Storage_Return) == 0 : # It is the last wave
                temp_wavefront.Generate(Storage_Away)
                Storage_Capacitor_Completed.append(temp_wavefront)
                Wavefronts_Return[Cartesian_Index_x,Cartesian_Index_y] = temp_wavefront
                Cartesian_Index_x = Cartesian_Index_x - 1
                Cartesian_Index_y = Cartesian_Index_y + 1

            else: # It is not the last wave
                
                # Get next Returning wavefront (will be inductive)
                temp_next_wavefront = Storage_Return.popleft()

                temp_wavefront_inductive, temp_wavefront_capacitve = temp_wavefront.Generate_Return()
                temp_next_wavefront_inductive, temp_next_wavefront_capacitve = temp_next_wavefront.Generate_Return()

                temp_wavefront_inductive.Merge(temp_next_wavefront_inductive)
                temp_wavefront_capacitve.Merge(temp_next_wavefront_capacitve)

                Storage_Away.append(temp_wavefront_inductive)
                Storage_Away.append(temp_wavefront_capacitve)

                Storage_Capacitor_Completed.append(temp_wavefront)
                Wavefronts_Return[Cartesian_Index_x,Cartesian_Index_y] = temp_wavefront
                Cartesian_Index_x = Cartesian_Index_x - 1
                Cartesian_Index_y = Cartesian_Index_y + 1
                
                Storage_Inductor_Completed.append(temp_next_wavefront)
                Wavefronts_Return[Cartesian_Index_x,Cartesian_Index_y] = temp_next_wavefront
                Cartesian_Index_x = Cartesian_Index_x - 1
                Cartesian_Index_y = Cartesian_Index_y + 1
        
        # Generate Return Waves, Store Away Waves
        
        ## Set Index for Away waves, will be 1 ahead! 
        Cartesian_Index_x = 2*(layer_number+1)-1
        Cartesian_Index_y = 0
        
        while len(Storage_Away)> 0:
            # Get an Away wavefront (will be inductive)
            temp_wavefront_inductive = Storage_Away.popleft()
            temp_wavefront_inductive.Generate(Storage_Return)
            Storage_Inductor_Completed.append(temp_wavefront_inductive)
            Wavefronts_Away[Cartesian_Index_x, Cartesian_Index_y] = temp_wavefront_inductive
            Cartesian_Time[Cartesian_Index_x-1,Cartesian_Index_y] = temp_wavefront_inductive.time_start
            Cartesian_Index_x = Cartesian_Index_x - 1
            Cartesian_Index_y = Cartesian_Index_y + 1
            
            # Get the next Away wavefront (will be capacitive)
            temp_wavefront_capacitve = Storage_Away.popleft()
            temp_wavefront_capacitve.Generate(Storage_Return)
            Storage_Capacitor_Completed.append(temp_wavefront_capacitve)
            Wavefronts_Away[Cartesian_Index_x, Cartesian_Index_y] = temp_wavefront_capacitve
            Cartesian_Index_x = Cartesian_Index_x - 1
            Cartesian_Index_y = Cartesian_Index_y + 1

    # Accumulation_Arrays
    for layer_number in range(0,data_input_storage.Number_of_Layers):
        ## Reset Centre Index    
        Centre_Index_x = 2*layer_number
        Centre_Index_y = 0
        
        for node_number in range(0,layer_number+1):
                # Inductor
                Away_Index_Inductor_x = Centre_Index_x + 1
                Away_Index_Inductor_y = Centre_Index_y
                
                Return_Index_Inductor_x = Centre_Index_x - 1
                Return_Index_Inductor_y = Centre_Index_y
                
                # Capacitor
                Away_Index_Capacitor_x = Centre_Index_x 
                Away_Index_Capacitor_y = Centre_Index_y + 1
                
                Return_Index_Capacitor_x = Centre_Index_x 
                Return_Index_Capacitor_y = Centre_Index_y - 1
                
                Wavefronts_Sending_Inductor[Centre_Index_x,Centre_Index_y] = Wavefronts_Away[Away_Index_Inductor_x,Away_Index_Inductor_y]
                Wavefronts_Sending_Capacitor[Centre_Index_x,Centre_Index_y] = Wavefronts_Away[Away_Index_Capacitor_x,Away_Index_Capacitor_y]
                
                Wavefronts_Returning_Inductor[Centre_Index_x,Centre_Index_y] = Wavefronts_Return[Away_Index_Inductor_x,Away_Index_Inductor_y]
                Wavefronts_Returning_Capacitor[Centre_Index_x,Centre_Index_y] = Wavefronts_Return[Away_Index_Capacitor_x,Away_Index_Capacitor_y]

                if(node_number == 0 and layer_number ==0): 
                        # Origin Node
                        # Inductor, Origin node = Away only
                        Voltage_Interconnect_Inductor[Centre_Index_x,Centre_Index_y] = Wavefronts_Away[Away_Index_Inductor_x,Away_Index_Inductor_y].magnitude_voltage 
                        Current_Interconnect_Inductor[Centre_Index_x,Centre_Index_y] = Wavefronts_Away[Away_Index_Inductor_x,Away_Index_Inductor_y].magnitude_current
                        
                        # Capacitor, Origin node = Away only
                        Voltage_Interconnect_Capacitor[Centre_Index_x,Centre_Index_y] = Wavefronts_Away[Away_Index_Capacitor_x,Away_Index_Capacitor_y].magnitude_voltage 
                        Current_Interconnect_Capacitor[Centre_Index_x,Centre_Index_y] = Wavefronts_Away[Away_Index_Capacitor_x,Away_Index_Capacitor_y].magnitude_current

                elif(node_number == 0 ): 
                        # First Node
                        # Inductor, First Node = Both Merging 
                        Voltage_Interconnect_Inductor[Centre_Index_x,Centre_Index_y] = (Wavefronts_Away[Away_Index_Inductor_x,Away_Index_Inductor_y].magnitude_voltage  + Wavefronts_Return[Return_Index_Inductor_x,Return_Index_Inductor_y].magnitude_voltage) 
                        Current_Interconnect_Inductor[Centre_Index_x,Centre_Index_y] = (Wavefronts_Away[Away_Index_Inductor_x,Away_Index_Inductor_y].magnitude_current + Wavefronts_Return[Return_Index_Inductor_x,Return_Index_Inductor_y].magnitude_current ) 
                        
                        # Capacitor, First Node = Away only
                        Voltage_Interconnect_Capacitor[Centre_Index_x,Centre_Index_y] = Wavefronts_Away[Away_Index_Capacitor_x,Away_Index_Capacitor_y].magnitude_voltage 
                        Current_Interconnect_Capacitor[Centre_Index_x,Centre_Index_y] = Wavefronts_Away[Away_Index_Capacitor_x,Away_Index_Capacitor_y].magnitude_current

                elif(node_number == layer_number): 
                        # Last Node
                        # Inductor, Last Node = Away only
                        Voltage_Interconnect_Inductor[Centre_Index_x,Centre_Index_y] = Wavefronts_Away[Away_Index_Inductor_x,Away_Index_Inductor_y].magnitude_voltage  
                        Current_Interconnect_Inductor[Centre_Index_x,Centre_Index_y] = Wavefronts_Away[Away_Index_Inductor_x,Away_Index_Inductor_y].magnitude_current
                        
                        # Capacitor, Last Node = Both Merging
                        Voltage_Interconnect_Capacitor[Centre_Index_x,Centre_Index_y] = (Wavefronts_Away[Away_Index_Capacitor_x,Away_Index_Capacitor_y].magnitude_voltage  + Wavefronts_Return[Return_Index_Capacitor_x,Return_Index_Capacitor_y].magnitude_voltage) 
                        Current_Interconnect_Capacitor[Centre_Index_x,Centre_Index_y] = (Wavefronts_Away[Away_Index_Capacitor_x,Away_Index_Capacitor_y].magnitude_current + Wavefronts_Return[Return_Index_Capacitor_x,Return_Index_Capacitor_y].magnitude_current )
                else:
                        # General Node
                        # Inductor, General Node = Both merging
                        Voltage_Interconnect_Inductor[Centre_Index_x,Centre_Index_y] = (Wavefronts_Away[Away_Index_Inductor_x,Away_Index_Inductor_y].magnitude_voltage  + Wavefronts_Return[Return_Index_Inductor_x,Return_Index_Inductor_y].magnitude_voltage) 
                        Current_Interconnect_Inductor[Centre_Index_x,Centre_Index_y] = (Wavefronts_Away[Away_Index_Inductor_x,Away_Index_Inductor_y].magnitude_current + Wavefronts_Return[Return_Index_Inductor_x,Return_Index_Inductor_y].magnitude_current ) 
                        
                        # Capacitor, General Node = Both merging
                        Voltage_Interconnect_Capacitor[Centre_Index_x,Centre_Index_y] = (Wavefronts_Away[Away_Index_Capacitor_x,Away_Index_Capacitor_y].magnitude_voltage  + Wavefronts_Return[Return_Index_Capacitor_x,Return_Index_Capacitor_y].magnitude_voltage)
                        Current_Interconnect_Capacitor[Centre_Index_x,Centre_Index_y] = (Wavefronts_Away[Away_Index_Capacitor_x,Away_Index_Capacitor_y].magnitude_current + Wavefronts_Return[Return_Index_Capacitor_x,Return_Index_Capacitor_y].magnitude_current )
                        
                Centre_Index_x -= 2
                Centre_Index_y += 2
    
    Cartesian_Time = delete_alternating(Cartesian_Time)
    
    Voltage_Interconnect_Inductor = delete_alternating(Voltage_Interconnect_Inductor)
    Current_Interconnect_Inductor = delete_alternating(Current_Interconnect_Inductor)

    Voltage_Interconnect_Capacitor = delete_alternating(Voltage_Interconnect_Capacitor)
    Current_Interconnect_Capacitor = delete_alternating(Current_Interconnect_Capacitor)
    
    Wavefronts_Sending_Inductor = delete_alternating(Wavefronts_Sending_Inductor)
    Wavefronts_Sending_Capacitor = delete_alternating(Wavefronts_Sending_Capacitor)
    
    Wavefronts_Returning_Inductor = delete_alternating(Wavefronts_Returning_Inductor)
    Wavefronts_Returning_Capacitor = delete_alternating(Wavefronts_Returning_Capacitor)
    
    data_output_storage = Data_Output_Storage(
        Cartesian_Time, # Merge Times
        Voltage_Interconnect_Inductor, # Values at interconnect 
        Current_Interconnect_Inductor, # Values at interconnect
        Voltage_Interconnect_Capacitor, # Values at interconnect
        Current_Interconnect_Capacitor, # Values at interconnect
        Wavefronts_Sending_Inductor, # Specific Wavefrotns at Nodes
        Wavefronts_Sending_Capacitor, # Specific Wavefrotns at Nodes
        Wavefronts_Returning_Inductor, # Specific Wavefrotns at Nodes
        Wavefronts_Returning_Capacitor # Specific Wavefrotns at Nodes
        )
    
    
    return (
        data_input_storage,
        data_output_storage
    ) 

## Plotting
def get_voltage(wavefront):
    return wavefront.magnitude_voltage

get_voltage_array = np.vectorize(get_voltage)

def get_current(wavefront):
    return wavefront.magnitude_current

get_current_array = np.vectorize(get_current)

def clear_subplot(axs):
    for ax in axs:
        ax.cla()

def plot_fanout_seismic(arr : np.ndarray ,ax ,title = "Fanout Plot", show_colour_bar = True ,contrast = False):
    
    max_boundary= 0
    if (contrast):
        Contrast = copy.copy(arr.astype(np.float))
        Contrast[0,0] = 0
        max_boundary = np.max(Contrast)  
    else:
        max_boundary = np.max(arr.astype(np.float))  
    
    ax.set_title(title)
    c = ax.imshow(arr.astype(np.float),cmap=cm.seismic,vmax =max_boundary, vmin = - max_boundary)
    
    if(show_colour_bar):
        plt.gcf().colorbar(c,ax=ax)
        
def plot_fanout_colour(arr : np.ndarray ,ax ,title = "Fanout Plot", show_colour_bar = True ,contrast = False):
    
    max_boundary = np.max(arr.astype(np.float))  
    
    ax.set_title(title)
    c = ax.imshow(arr.astype(np.float),cmap=cm.jet,vmax =max_boundary, vmin =0)
    
    if(show_colour_bar):
        return plt.gcf().colorbar(c,ax=ax)
        
def plot_fanout_crossection(arr : np.ndarray, ax, row_number : int, title : str, show_colour_bar = True ,contrast : bool = False):
    
    clear_subplot(ax)
    
    plt.gcf().suptitle("Crossection of " + title+" Fanout at index " + str(row_number) )
    
    row_a = arr[row_number,:]
    row_b = arr[:,row_number]
    
    ax[0].plot(row_a)
    ax[1].plot(row_b)
    
    plot_fanout_seismic(arr,ax[2],"Fanout",show_colour_bar,contrast)
    ax[2].plot([row_number,row_number],[0,arr.shape[0]],'m--')
    ax[2].plot([0,arr.shape[0]],[row_number,row_number],'c--')

def plot_fanout_interconnect(data_output_merged: Data_Output_Storage,ax, which_string :str):
    allowed_strings = ["voltage inductor", "current inductor", "voltage capacitor", "current capacitor"]
    if(which_string.lower() == allowed_strings[0] ):
        plot_fanout_seismic(data_output_merged.Voltage_Interconnect_Inductor,ax)
    elif(which_string.lower() == allowed_strings[1] ):
        plot_fanout_seismic(data_output_merged.Current_Interconnect_Inductor,ax)
    elif(which_string.lower() == allowed_strings[2] ):
        plot_fanout_seismic(data_output_merged.Voltage_Interconnect_Inductor,ax)
    elif(which_string.lower() == allowed_strings[3] ):
        plot_fanout_seismic(data_output_merged.Current_Interconnect_Inductor,ax)
    else:
            raise ValueError("Incorrect plotting choice")

def plot_time_interconnect(data_output_ordered : Data_Output_Storage_Ordered,ax, which_string :str, is_integrated: bool = False): 
    allowed_strings = ["voltage inductor", "current inductor", "voltage capacitor", "current capacitor"]
    
    if(is_integrated):
        if(which_string.lower() == allowed_strings[0] ):
            ax.set_title("Inductor voltage at Interconnect")
            ax.step(data_output_ordered.Time,np.cumsum(data_output_ordered.Voltage_Interconnect_Inductor),where='post')
        elif(which_string.lower() == allowed_strings[1] ):
            ax.set_title("Inductor current at Interconnect")
            ax.step(data_output_ordered.Time,np.cumsum(data_output_ordered.Current_Interconnect_Inductor),where='post')
        elif(which_string.lower() == allowed_strings[2] ):
            ax.set_title("Capacitor voltage at Interconnect")
            ax.step(data_output_ordered.Time,np.cumsum(data_output_ordered.Voltage_Interconnect_Capacitor),where='post')
        elif(which_string.lower() == allowed_strings[3] ):
            ax.set_title("Capacitor current at Interconnect")
            ax.step(data_output_ordered.Time,np.cumsum(data_output_ordered.Current_Interconnect_Capacitor),where='post')
        else:
            raise ValueError("Incorrect plotting choice")
    else:
        if(which_string.lower() == allowed_strings[0] ):
            ax.set_title("Inductor voltage change at Interconnect")
            ax.step(data_output_ordered.Time,data_output_ordered.Voltage_Interconnect_Inductor,where='post')
        elif(which_string.lower() == allowed_strings[1] ):
            ax.set_title("Inductor current change at Interconnect")
            ax.step(data_output_ordered.Time,data_output_ordered.Current_Interconnect_Inductor,where='post')
        elif(which_string.lower() == allowed_strings[2] ):
            ax.set_title("Capacitor voltage change at Interconnect")
            ax.step(data_output_ordered.Time,data_output_ordered.Voltage_Interconnect_Capacitor,where='post')
        elif(which_string.lower() == allowed_strings[3] ):
            ax.set_title("Capacitor current change at Interconnect")
            ax.step(data_output_ordered.Time,data_output_ordered.Current_Interconnect_Capacitor,where='post')
        else:
            raise ValueError("Incorrect plotting choice")
        
def plot_time_interconnect_3(data_output_merged : Data_Output_Storage, data_output_ordered : Data_Output_Storage_Ordered, ax, which_string : str):
    
    plot_time_interconnect(data_output_ordered,ax['A'],which_string)
    plot_time_interconnect(data_output_ordered,ax['B'],which_string,True)
    plot_fanout_interconnect(data_output_merged,ax['C'],which_string)

    for i,index in enumerate(data_output_ordered.Indexes):
        if(i  == 0):
            pass
        else:
            x1 = data_output_ordered.Indexes[i-1][0]
            y1 = data_output_ordered.Indexes[i-1][1]
            
            x2 = index[0]
            y2 = index[1]
            ax['C'].plot([y1,y2],[x1,x2],'black')