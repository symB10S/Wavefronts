from decimal import *
from collections import deque
import numpy as np
import math
import copy
from dataclasses import dataclass, fields
import matplotlib.cm as cm
import matplotlib as mpl
import matplotlib.pyplot as plt
from matplotlib.ticker import (MultipleLocator, FormatStrFormatter,
                               AutoMinorLocator)
from matplotlib.animation import FFMpegWriter
plt.rcParams['animation.ffmpeg_path'] = 'C:\\Users\\Jonathan\\Documents\\Academic\\Masters\\Simulator\\Git\\Main_Algorithm\\ffmpeg\\bin\\ffmpeg.exe'
import ipywidgets as widgets
from IPython.display import display


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
    
    def get_sending(self,which_string):
        allowed_strings = ["voltage inductor", "current inductor", "voltage capacitor", "current capacitor"]
        if(which_string.lower() == allowed_strings[0] ):
            return  get_voltage_array(self.Wavefronts_Sending_Inductor)
        
        elif(which_string.lower() == allowed_strings[1] ):
            return  get_current_array(self.Wavefronts_Sending_Inductor)
        
        elif(which_string.lower() == allowed_strings[2] ):
            return  get_voltage_array(self.Wavefronts_Sending_Capacitor)
        
        elif(which_string.lower() == allowed_strings[3] ):
            return  get_current_array(self.Wavefronts_Sending_Capacitor)
        
        else:
            raise ValueError("Incorrect plotting choice")
        
    def get_returning(self,which_string):
        allowed_strings = ["voltage inductor", "current inductor", "voltage capacitor", "current capacitor"]
        if(which_string.lower() == allowed_strings[0] ):
            return  get_voltage_array(self.Wavefronts_Returning_Inductor)
        
        elif(which_string.lower() == allowed_strings[1] ):
            return  get_current_array(self.Wavefronts_Returning_Inductor)
        
        elif(which_string.lower() == allowed_strings[2] ):
            return  get_voltage_array(self.Wavefronts_Returning_Capacitor)
        
        elif(which_string.lower() == allowed_strings[3] ):
            return  get_current_array(self.Wavefronts_Returning_Capacitor)
        
        else:
            raise ValueError("Incorrect plotting choice")
        
    
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
    Data_Inputs = copy.deepcopy(Data_Inputs)
    Data_Outputs = copy.deepcopy(Data_Outputs)
    
    if(Data_Inputs.is_Higher_Merging):
        Voltage_Interconnect_Inductor_merged = multiplicative_merging(Data_Outputs.Voltage_Interconnect_Inductor,Data_Inputs.a,Data_Inputs.b,Data_Inputs.Number_of_Layers)
        Current_Interconnect_Inductor_merged = multiplicative_merging(Data_Outputs.Current_Interconnect_Inductor,Data_Inputs.a,Data_Inputs.b,Data_Inputs.Number_of_Layers)
        
        Voltage_Interconnect_Capacitor_merged = multiplicative_merging(Data_Outputs.Voltage_Interconnect_Capacitor,Data_Inputs.a,Data_Inputs.b,Data_Inputs.Number_of_Layers)
        Current_Interconnect_Capacitor_merged = multiplicative_merging(Data_Outputs.Current_Interconnect_Capacitor,Data_Inputs.a,Data_Inputs.b,Data_Inputs.Number_of_Layers)
        
        Wavefronts_Sending_Inductor_merged = multiplicative_merging(Data_Outputs.Wavefronts_Sending_Inductor,Data_Inputs.a,Data_Inputs.b,Data_Inputs.Number_of_Layers)
        Wavefronts_Sending_Capacitor_merged = multiplicative_merging(Data_Outputs.Wavefronts_Sending_Capacitor,Data_Inputs.a,Data_Inputs.b,Data_Inputs.Number_of_Layers)

        Wavefronts_Returning_Inductor_merged = multiplicative_merging(Data_Outputs.Wavefronts_Returning_Inductor,Data_Inputs.a,Data_Inputs.b,Data_Inputs.Number_of_Layers)
        Wavefronts_Returning_Capacitor_merged = multiplicative_merging(Data_Outputs.Wavefronts_Returning_Capacitor,Data_Inputs.a,Data_Inputs.b,Data_Inputs.Number_of_Layers)
        
        Time_cut = Data_Outputs.Time[:,0:Data_Inputs.b]
    else:
        Voltage_Interconnect_Inductor_merged = Data_Outputs.Voltage_Interconnect_Inductor
        Current_Interconnect_Inductor_merged = Data_Outputs.Current_Interconnect_Inductor
        
        Voltage_Interconnect_Capacitor_merged = Data_Outputs.Voltage_Interconnect_Capacitor
        Current_Interconnect_Capacitor_merged = Data_Outputs.Current_Interconnect_Capacitor
        
        Wavefronts_Sending_Inductor_merged = Data_Outputs.Wavefronts_Sending_Inductor
        Wavefronts_Sending_Capacitor_merged = Data_Outputs.Wavefronts_Sending_Capacitor

        Wavefronts_Returning_Inductor_merged = Data_Outputs.Wavefronts_Returning_Inductor
        Wavefronts_Returning_Capacitor_merged = Data_Outputs.Wavefronts_Returning_Capacitor
        
        Time_cut = Data_Outputs.Time
    
    
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
    
    Data_Input = copy.deepcopy(Data_Input)
    Data_Output_Merged = copy.deepcopy(Data_Output_Merged)
    
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
            
            out_wavefront_sending_inductor.append(Data_Output_Merged.Wavefronts_Sending_Inductor[best_time_index[0],best_time_index[1]])
            out_wavefront_sending_capacitor.append(Data_Output_Merged.Wavefronts_Sending_Capacitor[best_time_index[0],best_time_index[1]])
            
            out_wavefront_returning_inductor.append(Data_Output_Merged.Wavefronts_Returning_Inductor[best_time_index[0],best_time_index[1]])
            out_wavefront_returning_capacitor.append(Data_Output_Merged.Wavefronts_Returning_Capacitor[best_time_index[0],best_time_index[1]])
            
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
        Wavefronts_Sending_Inductor, # Specific Wavefronts at Nodes
        Wavefronts_Sending_Capacitor, # Specific Wavefronts at Nodes
        Wavefronts_Returning_Inductor, # Specific Wavefronts at Nodes
        Wavefronts_Returning_Capacitor # Specific Wavefronts at Nodes
        )
    
    
    return (
        data_input_storage,
        data_output_storage
    ) 

def Full_Cycle(Inductor_List, Capacitor_List, Circuit_List):
    data_input, data_output = Process_Wavefronts(Inductor_List, Capacitor_List, Circuit_List)
    data_output_merged = Higher_Order_Merging(data_input,data_output)
    data_output_ordered = Order_Data_Output_Merged(data_input,data_output_merged)
    
    
    return data_input,data_output,data_output_merged,data_output_ordered

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

def plot_fanout_seismic(arr : np.ndarray ,ax ,title = "Fanout Plot", show_colour_bar = True ,contrast = False, padwidth = 15):
    
    max_boundary= 0
    if (contrast):
        Contrast = copy.copy(arr.astype(np.float))
        max_index = np.unravel_index(np.argmax(Contrast, axis=None), Contrast.shape)
        Contrast[max_index] = 0
        
        max_boundary = abs(np.max(Contrast))  
        min_boundary = abs(np.min(Contrast))  
        
        max_boundary = max(max_boundary, min_boundary)
    else:
        max_boundary = abs(np.max(arr.astype(np.float)))
        min_boundary = abs(np.min(arr.astype(np.float)))
        
        max_boundary = max(max_boundary, min_boundary)
    
    ax.set_title(title)
    c = ax.imshow(np.pad(arr.astype(np.float),(padwidth,padwidth)),cmap=cm.seismic,vmax =max_boundary, vmin = - max_boundary)
    
    if(show_colour_bar):
        ax.get_figure().colorbar(c,ax=ax)
        
def plot_fanout_colour(arr : np.ndarray ,ax ,title = "Fanout Plot", show_colour_bar = True ,contrast = False):
    
    max_boundary = np.max(arr.astype(np.float))  
    min_boundary = np.min(arr.astype(np.float))  
    
    ax.set_title(title)
    cb = ax.imshow(arr.astype(np.float),cmap=cm.jet,vmax =max_boundary, vmin =min_boundary)
    
    if(show_colour_bar):
        ax.get_figure().colorbar(cb,ax=ax)
        
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

def plot_fanout_interconnect(data_output_merged: Data_Output_Storage,ax, which_string :str, data_str : str = ""):
    
    allowed_strings = ["voltage inductor", "current inductor", "voltage capacitor", "current capacitor"]
    if(which_string.lower() == allowed_strings[0] ):
        plot_fanout_seismic( data_output_merged.Voltage_Interconnect_Inductor,ax,allowed_strings[0]+ data_str,True,True)
    elif(which_string.lower() == allowed_strings[1] ):
        plot_fanout_seismic(data_output_merged.Current_Interconnect_Inductor,ax,allowed_strings[1]+ data_str)
    elif(which_string.lower() == allowed_strings[2] ):
        plot_fanout_seismic(data_output_merged.Voltage_Interconnect_Capacitor,ax,allowed_strings[2]+ data_str,True,True)
    elif(which_string.lower() == allowed_strings[3] ):
        plot_fanout_seismic(data_output_merged.Current_Interconnect_Capacitor,ax,allowed_strings[3]+ data_str)
    else:
            raise ValueError("Incorrect plotting choice")

def plot_fanout_interconnect_4(data_output_merged: Data_Output_Storage):
    
    fig, ax = plt.subplot_mosaic([['A','B'],['C','D']])
    
    plot_fanout_seismic(data_output_merged.Voltage_Interconnect_Inductor,ax['A'],"Inductor Voltage",True,True)
    plot_fanout_seismic(data_output_merged.Current_Interconnect_Inductor,ax['C'],"Inductor Current")
    plot_fanout_seismic(data_output_merged.Voltage_Interconnect_Inductor,ax['B'],"Capacitor Voltage",True,True)
    plot_fanout_seismic(data_output_merged.Current_Interconnect_Inductor,ax['D'],"Capacitor Current")
    
    return fig,ax

def plot_fanout_wavefronts(data_output: Data_Output_Storage,ax, which_string :str, is_sending : bool = True):
    if(is_sending):
        plot_fanout_seismic(data_output.get_sending(which_string),ax)
    else:
        plot_fanout_seismic(data_output.get_returning(which_string),ax)

def plot_fanout_wavefronts_all(data_output: Data_Output_Storage, is_sending : bool = True, data_str :str = ""):
    fig, ax = plt.subplot_mosaic([['A','B','C','D'],['E','F','G','H']])
    
    fig.suptitle("Wavefront Fanouts " + data_str)
    
    plot_fanout_seismic(data_output.get_sending("voltage inductor"),ax['A'],"sending voltage inductor")
    plot_fanout_seismic(data_output.get_sending("current inductor"),ax['B'],"sending current inductor")
    plot_fanout_seismic(data_output.get_sending("voltage capacitor"),ax['C'],"sending voltage capacitor")
    plot_fanout_seismic(data_output.get_sending("current capacitor"),ax['D'],"sending current capacitor")

    plot_fanout_seismic(data_output.get_returning("voltage inductor"),ax['E'],"returning voltage inductor")
    plot_fanout_seismic(data_output.get_returning("current inductor"),ax['F'],"returning current inductor")
    plot_fanout_seismic(data_output.get_returning("voltage capacitor"),ax['G'],"returning voltage capacitor")
    plot_fanout_seismic(data_output.get_returning("current capacitor"),ax['H'],"returning current capacitor")
        
    return fig, ax
    

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
        
def plot_time_interconnect_3(data_output_merged : Data_Output_Storage, data_output_ordered : Data_Output_Storage_Ordered, which_string : str):
    
    padwidth = 15
    
    fig, ax = plt.subplot_mosaic([['A','C'],['B','C']])
    
    plot_time_interconnect(data_output_ordered,ax['A'],which_string)
    plot_time_interconnect(data_output_ordered,ax['B'],which_string,True)
    plot_fanout_interconnect(data_output_merged,ax['C'],which_string)

    for i,index in enumerate(data_output_ordered.Indexes):
        if(i  == 0):
            pass
        else:
            x1 = data_output_ordered.Indexes[i-1][0]+ padwidth
            y1 = data_output_ordered.Indexes[i-1][1]+ padwidth
            
            x2 = index[0]+ padwidth
            y2 = index[1]+ padwidth
            ax['C'].plot([y1,y2],[x1,x2],'black',marker='o')
            
    return fig, ax 

def plot_time_interconnect_3_both(data_output_merged : Data_Output_Storage
                                  , data_output_ordered : Data_Output_Storage_Ordered
                                  , data_output_merged_2 : Data_Output_Storage
                                  , data_output_ordered_2 : Data_Output_Storage_Ordered
                                  , which_string : str):
    
    padwidth = 15
    
    fig, ax = plt.subplot_mosaic([['A','C','D'],['B','C','D']])
    
    plot_time_interconnect(data_output_ordered,ax['A'],which_string)
    plot_time_interconnect(data_output_ordered_2,ax['A'],which_string)
    
    plot_time_interconnect(data_output_ordered,ax['B'],which_string,True)
    plot_time_interconnect(data_output_ordered_2,ax['B'],which_string,True)
    
    plot_fanout_interconnect(data_output_merged,ax['C'],which_string," Data 1")
    plot_fanout_interconnect(data_output_merged_2,ax['D'],which_string," Data 2")

    for i,index in enumerate(data_output_ordered.Indexes):
        if(i  == 0):
            pass
        else:
            x1 = data_output_ordered.Indexes[i-1][0]+ padwidth
            y1 = data_output_ordered.Indexes[i-1][1]+ padwidth
            
            x2 = index[0]+ padwidth
            y2 = index[1]+ padwidth
            ax['C'].plot([y1,y2],[x1,x2],'black',marker='.')
            
    for i,index in enumerate(data_output_ordered_2.Indexes):
        if(i  == 0):
            pass
        else:
            x1 = data_output_ordered_2.Indexes[i-1][0]+ padwidth
            y1 = data_output_ordered_2.Indexes[i-1][1]+ padwidth
            
            x2 = index[0]+ padwidth
            y2 = index[1]+ padwidth
            ax['D'].plot([y1,y2],[x1,x2],'black',marker='.')
            
    return fig, ax 

def plot_time_interconnect_4(data_output_ordered: Data_Output_Storage_Ordered):
    
    fig, ax = plt.subplot_mosaic([['A','B'],['C','D']])
    
    ax['A'].set_title("Inductor voltage at Interconnect")
    ax['A'].step(data_output_ordered.Time,np.cumsum(data_output_ordered.Voltage_Interconnect_Inductor),where='post')
    
    ax['C'].set_title("Inductor current at Interconnect")
    ax['C'].step(data_output_ordered.Time,np.cumsum(data_output_ordered.Current_Interconnect_Inductor),where='post')
    
    ax['B'].set_title("Capacitor voltage at Interconnect")
    ax['B'].step(data_output_ordered.Time,np.cumsum(data_output_ordered.Voltage_Interconnect_Capacitor),where='post')
    
    ax['D'].set_title("Capacitor current at Interconnect")
    ax['D'].step(data_output_ordered.Time,np.cumsum(data_output_ordered.Current_Interconnect_Capacitor),where='post')
    
    return fig, ax

def plot_time_interconnect_4_wavefronts(data_output_ordered: Data_Output_Storage_Ordered):
    
    fig, ax = plt.subplot_mosaic([['A','B'],['C','D']])
    
    ax['A'].set_title("Inductor voltage change at Interconnect")
    ax['A'].step(data_output_ordered.Time,data_output_ordered.Voltage_Interconnect_Inductor,where='post')
    
    ax['C'].set_title("Inductor current change at Interconnect")
    ax['C'].step(data_output_ordered.Time,data_output_ordered.Current_Interconnect_Inductor,where='post')
    
    ax['B'].set_title("Capacitor voltage change at Interconnect")
    ax['B'].step(data_output_ordered.Time,data_output_ordered.Voltage_Interconnect_Capacitor,where='post')
    
    ax['D'].set_title("Capacitor current change at Interconnect")
    ax['D'].step(data_output_ordered.Time,data_output_ordered.Current_Interconnect_Capacitor,where='post')
    
    return fig, ax

def plot_time_interconnect_4_both(data_output_ordered: Data_Output_Storage_Ordered,data_output_ordered_2: Data_Output_Storage_Ordered):
    
    fig, ax = plt.subplot_mosaic([['A','B'],['C','D']])
    
    ax['A'].set_title("Inductor voltage at Interconnect")
    ax['A'].step(data_output_ordered.Time,np.cumsum(data_output_ordered.Voltage_Interconnect_Inductor),where='post')
    ax['A'].step(data_output_ordered_2.Time,np.cumsum(data_output_ordered_2.Voltage_Interconnect_Inductor),where='post')
    
    ax['C'].set_title("Inductor current at Interconnect")
    ax['C'].step(data_output_ordered.Time,np.cumsum(data_output_ordered.Current_Interconnect_Inductor),where='post')
    ax['C'].step(data_output_ordered_2.Time,np.cumsum(data_output_ordered_2.Current_Interconnect_Inductor),where='post')
    
    ax['B'].set_title("Capacitor voltage at Interconnect")
    ax['B'].step(data_output_ordered.Time,np.cumsum(data_output_ordered.Voltage_Interconnect_Capacitor),where='post')
    ax['B'].step(data_output_ordered_2.Time,np.cumsum(data_output_ordered_2.Voltage_Interconnect_Capacitor),where='post')
    
    ax['D'].set_title("Capacitor current at Interconnect")
    ax['D'].step(data_output_ordered.Time,np.cumsum(data_output_ordered.Current_Interconnect_Capacitor),where='post')
    ax['D'].step(data_output_ordered_2.Time,np.cumsum(data_output_ordered_2.Current_Interconnect_Capacitor),where='post')
    
    return fig, ax

def plot_time_interconnect_4_wavefronts_both(data_output_ordered: Data_Output_Storage_Ordered, data_output_ordered_2: Data_Output_Storage_Ordered):
    
    fig, ax = plt.subplot_mosaic([['A','B'],['C','D']])
    
    ax['A'].set_title("Inductor voltage change at Interconnect")
    ax['A'].step(data_output_ordered.Time,data_output_ordered.Voltage_Interconnect_Inductor,where='post')
    ax['A'].step(data_output_ordered_2.Time,data_output_ordered_2.Voltage_Interconnect_Inductor,where='post')
    
    ax['C'].set_title("Inductor current change at Interconnect")
    ax['C'].step(data_output_ordered.Time,data_output_ordered.Current_Interconnect_Inductor,where='post')
    ax['C'].step(data_output_ordered_2.Time,data_output_ordered_2.Current_Interconnect_Inductor,where='post')
    
    ax['B'].set_title("Capacitor voltage change at Interconnect")
    ax['B'].step(data_output_ordered.Time,data_output_ordered.Voltage_Interconnect_Capacitor,where='post')
    ax['B'].step(data_output_ordered_2.Time,data_output_ordered_2.Voltage_Interconnect_Capacitor,where='post')
    
    ax['D'].set_title("Capacitor current change at Interconnect")
    ax['D'].step(data_output_ordered.Time,data_output_ordered.Current_Interconnect_Capacitor,where='post')
    ax['D'].step(data_output_ordered_2.Time,data_output_ordered_2.Current_Interconnect_Capacitor,where='post')
    
    return fig, ax

def plot_time_wavefronts_all(data_output : Data_Output_Storage, what_to_plot : str):
    fig_sub, ax_sub = plt.subplots(2,3)

    fig_sub.suptitle("Wavefronts of the "+ what_to_plot)
     
    ax_sub[0,0].set_title("sending voltage")
    ax_sub[0,0].step(np.ma.masked_where(data_output.Time == 0 ,data_output.Time), np.ma.masked_where(data_output.Time == 0 ,data_output.get_sending("voltage "+ what_to_plot)),where='post')
    ax_sub[0,1].set_title("returning voltage")
    ax_sub[0,1].step(np.ma.masked_where(data_output.Time == 0 ,data_output.Time), np.ma.masked_where(data_output.Time == 0 ,data_output.get_returning("voltage "+ what_to_plot)),where='post')
    ax_sub[0,2].set_title("sending + returning voltage")
    ax_sub[0,2].step(np.ma.masked_where(data_output.Time == 0 ,data_output.Time), np.ma.masked_where(data_output.Time == 0 ,data_output.get_returning("voltage "+ what_to_plot)+data_output.get_sending("voltage "+ what_to_plot)),where='post')

    ax_sub[1,0].set_title("sending current")
    ax_sub[1,0].step(np.ma.masked_where(data_output.Time == 0 ,data_output.Time), np.ma.masked_where(data_output.Time == 0 ,data_output.get_sending("current " + what_to_plot)),where='post')
    ax_sub[1,1].set_title("returning current")
    ax_sub[1,1].step(np.ma.masked_where(data_output.Time == 0 ,data_output.Time), np.ma.masked_where(data_output.Time == 0 ,data_output.get_returning("current " + what_to_plot)),where='post')
    ax_sub[1,2].set_title("sending + returning current")
    ax_sub[1,2].step(np.ma.masked_where(data_output.Time == 0 ,data_output.Time), np.ma.masked_where(data_output.Time == 0 ,data_output.get_returning("current " + what_to_plot)+data_output.get_sending("current " + what_to_plot)),where='post')
    
    return fig_sub, ax_sub

def plot_time_wavefronts_all_both(data_output : Data_Output_Storage, data_output_2: Data_Output_Storage, what_to_plot : str):
    fig_sub, ax_sub = plt.subplots(2,3)

    fig_sub.suptitle("Wavefronts of the "+ what_to_plot)
     
    ax_sub[0,0].set_title("sending voltage")
    ax_sub[0,0].step(np.ma.masked_where(data_output.Time == 0 ,data_output.Time), np.ma.masked_where(data_output.Time == 0 ,data_output.get_sending("voltage "+ what_to_plot)),where='post')
    ax_sub[0,0].step(np.ma.masked_where(data_output_2.Time == 0 ,data_output_2.Time), np.ma.masked_where(data_output_2.Time == 0 ,data_output_2.get_sending("voltage "+ what_to_plot)),where='post')
    ax_sub[0,1].set_title("returning voltage")
    ax_sub[0,1].step(np.ma.masked_where(data_output.Time == 0 ,data_output.Time), np.ma.masked_where(data_output.Time == 0 ,data_output.get_returning("voltage "+ what_to_plot)),where='post')
    ax_sub[0,1].step(np.ma.masked_where(data_output_2.Time == 0 ,data_output_2.Time), np.ma.masked_where(data_output_2.Time == 0 ,data_output_2.get_returning("voltage "+ what_to_plot)),where='post')
    ax_sub[0,2].set_title("sending + returning voltage")
    ax_sub[0,2].step(np.ma.masked_where(data_output.Time == 0 ,data_output.Time), np.ma.masked_where(data_output.Time == 0 ,data_output.get_returning("voltage "+ what_to_plot)+data_output.get_sending("voltage "+ what_to_plot)),where='post')
    ax_sub[0,2].step(np.ma.masked_where(data_output_2.Time == 0 ,data_output_2.Time), np.ma.masked_where(data_output_2.Time == 0 ,data_output_2.get_returning("voltage "+ what_to_plot)+data_output_2.get_sending("voltage "+ what_to_plot)),where='post')

    ax_sub[1,0].set_title("sending current")
    ax_sub[1,0].step(np.ma.masked_where(data_output.Time == 0 ,data_output.Time), np.ma.masked_where(data_output.Time == 0 ,data_output.get_sending("current " + what_to_plot)),where='post')
    ax_sub[1,0].step(np.ma.masked_where(data_output_2.Time == 0 ,data_output_2.Time), np.ma.masked_where(data_output_2.Time == 0 ,data_output_2.get_sending("current " + what_to_plot)),where='post')
    ax_sub[1,1].set_title("returning current")
    ax_sub[1,1].step(np.ma.masked_where(data_output.Time == 0 ,data_output.Time), np.ma.masked_where(data_output.Time == 0 ,data_output.get_returning("current " + what_to_plot)),where='post')
    ax_sub[1,1].step(np.ma.masked_where(data_output_2.Time == 0 ,data_output_2.Time), np.ma.masked_where(data_output_2.Time == 0 ,data_output_2.get_returning("current " + what_to_plot)),where='post')
    ax_sub[1,2].set_title("sending + returning current")
    ax_sub[1,2].step(np.ma.masked_where(data_output.Time == 0 ,data_output.Time), np.ma.masked_where(data_output.Time == 0 ,data_output.get_returning("current " + what_to_plot)+data_output.get_sending("current " + what_to_plot)),where='post')
    ax_sub[1,2].step(np.ma.masked_where(data_output_2.Time == 0 ,data_output_2.Time), np.ma.masked_where(data_output_2.Time == 0 ,data_output_2.get_returning("current " + what_to_plot)+data_output_2.get_sending("current " + what_to_plot)),where='post')
    
    return fig_sub, ax_sub
   
def get_spatial_zip(Time_Enquriey, Data_Output_Merged : Data_Output_Storage,Data_Output_Ordered : Data_Output_Storage_Ordered, is_Inductor : bool):
    
    termination_length = 1
    
    dc_voltage = Decimal('0')
    dc_current = Decimal('0')

    send_position = []
    send_value_voltage = []
    send_value_current = []

    return_position = []
    return_value_voltage = []
    return_value_current = []

    sending_wavefront = []
    returning_wavefront = []
    
    for index in Data_Output_Ordered.Indexes:
        x = index[0]
        y = index[1]
        
        if(is_Inductor):
            sending_wavefront = Data_Output_Merged.Wavefronts_Sending_Inductor[x,y]
            returning_wavefront = Data_Output_Merged.Wavefronts_Returning_Inductor[x,y]
        else:
            sending_wavefront = Data_Output_Merged.Wavefronts_Sending_Capacitor[x,y]
            returning_wavefront = Data_Output_Merged.Wavefronts_Returning_Capacitor[x,y]
            
        if(sending_wavefront.time_start > Time_Enquriey): # Finished
            break
            
        elif(returning_wavefront.time_end <= Time_Enquriey): # Both DC
            dc_voltage += sending_wavefront.magnitude_voltage
            dc_current += sending_wavefront.magnitude_current
                
            dc_voltage += returning_wavefront.magnitude_voltage
            dc_current += returning_wavefront.magnitude_current
                
        elif(returning_wavefront.time_end >= Time_Enquriey and returning_wavefront.time_start < Time_Enquriey): # Returning Intercept, Sending DC
            return_position.append(returning_wavefront.Position_at_time(Time_Enquriey))
            return_value_voltage.append(returning_wavefront.magnitude_voltage)
            return_value_current.append(returning_wavefront.magnitude_current)
                
            dc_voltage += sending_wavefront.magnitude_voltage
            dc_current += sending_wavefront.magnitude_current
                
        elif(sending_wavefront.time_end >= Time_Enquriey and sending_wavefront.time_start <= Time_Enquriey): # Sending Intercept
            send_position.append(sending_wavefront.Position_at_time(Time_Enquriey))
            send_value_voltage.append(sending_wavefront.magnitude_voltage)
            send_value_current.append(sending_wavefront.magnitude_current)
                
        else:
            raise Exception("Somethings wrong, wavefront has to be intecepted/ stored or done")
            
    termination_value_voltage = dc_voltage
    interconnect_value_voltage =  dc_voltage
        
    termination_value_current = dc_current
    interconnect_value_current =  dc_current

    position_all = []
    value_left_voltage = []
    value_right_voltage = []
        
    value_left_current = []
    value_right_current = []

    # input sending values in output form, make all DC value
    for i, pos in enumerate(send_position):
        position_all.append(pos)
            
        value_left_voltage.append(dc_voltage)
        value_right_voltage.append(dc_voltage)
        interconnect_value_voltage += send_value_voltage[i]
            
        value_left_current.append(dc_current)
        value_right_current.append(dc_current)
        interconnect_value_current += send_value_current[i]
            

    # input returning values in output form, make all DC value
    for i, pos in enumerate(return_position):
        position_all.append(pos)
            
        value_left_voltage.append(dc_voltage)
        value_right_voltage.append(dc_voltage)
        termination_value_voltage += return_value_voltage[i]
            
        value_left_current.append(dc_current)
        value_right_current.append(dc_current)
            
        termination_value_current += return_value_current[i]
            
        if (pos ==0):
            pass
            raise Exception("Returning wavefront at interconnect, problematic")

    # add values left and right
    for i,position in enumerate(position_all):
        for j, send_pos in enumerate(send_position):
            if(send_pos> position):
                value_left_voltage[i] += send_value_voltage[j]
                value_right_voltage[i] += send_value_voltage[j]
                    
                value_left_current[i] += send_value_current[j]
                value_right_current[i] += send_value_current[j]
                    
            if (send_pos == position ):
                value_left_voltage[i] += send_value_voltage[j]
                    
                value_left_current[i] += send_value_current[j]
                
        for j, return_pos in enumerate(return_position):
            if(return_pos< position):
                value_left_voltage[i] += return_value_voltage[j]
                value_right_voltage[i] += return_value_voltage[j]
                    
                value_left_current[i] += return_value_current[j]
                value_right_current[i] += return_value_current[j]
                    
            if (return_pos == position ):
                value_right_voltage[i] += return_value_voltage[j]
                    
                value_right_current[i] += return_value_current[j]
                    
    # append interconnect
    position_all.append(0)
        
    value_left_voltage.append(interconnect_value_voltage)
    value_right_voltage.append(interconnect_value_voltage)
        
    value_left_current.append(interconnect_value_current)
    value_right_current.append(interconnect_value_current)

    # append termination
    position_all.append(termination_length)
            
    value_left_voltage.append(termination_value_voltage)
    value_right_voltage.append(termination_value_voltage)
        
    value_left_current.append(termination_value_current)
    value_right_current.append(termination_value_current)

    # sort values
    zip_positions_voltage_current = sorted(zip(position_all,value_left_voltage,value_right_voltage,value_left_current,value_right_current))
    position_all, value_left_voltage, value_right_voltage, value_left_current, value_right_current = zip(*zip_positions_voltage_current)
        
    # convert to lists
    position_all = list(position_all)
        
    value_left_voltage = list(value_left_voltage)
    value_right_voltage = list(value_right_voltage)
        
    value_left_current = list(value_left_current)
    value_right_current = list(value_right_current)
        
    # Merge neighbours
    found_duplicate = True
    while found_duplicate:
        found_duplicate = False
        for index,position in enumerate(position_all):
            if(index < len(position_all)-1):
                if(position == position_all[index+1]):
                    value_left_voltage[index] += value_left_voltage[index +1]
                    value_right_voltage[index] += value_right_voltage[index +1]
                        
                    value_left_current[index] += value_left_current[index +1]
                    value_right_current[index] += value_right_current[index +1]
                        
                    del position_all[index +1]
                    del value_left_voltage[index +1]
                    del value_right_voltage[index +1]
                    del value_left_current[index +1]
                    del value_right_current[index +1]

                    found_duplicate = True
                        
    
    return position_all,value_left_voltage,value_right_voltage,value_left_current,value_right_current

def plot_spatial_at_time_4(Time_Enquriey, Data_Output_Merged : Data_Output_Storage,Data_Output_Ordered : Data_Output_Storage_Ordered ,fig ,ax ):
    
    ax['A'].cla()
    ax['B'].cla()
    ax['C'].cla()
    ax['D'].cla()

    termination_length = 1
    
    # Create Plot
    fig.suptitle("Spatial Waveforms at " + str(Time_Enquriey.quantize(Decimal('.0001'), rounding=ROUND_HALF_DOWN)) + "s")

    # Get inductor zip
    pos_all, value_lv, value_rv, value_lc, value_rc = get_spatial_zip(Time_Enquriey, Data_Output_Merged,Data_Output_Ordered,True)
    zip_out = zip(pos_all, value_lv, value_rv, value_lc, value_rc)
    
    x = 0
    x_old = 0
    
    
    y1_voltage = 0
    y2_voltage = 0
    y_voltage_old = value_lv[0]
    
    y1_current = 0
    y2_current = 0
    y_current_old = value_lc[0]
    
    ax["A"].set_title(str(value_rv[-1].quantize(Decimal('0.0001')))+"   ←   Voltage Inductor   →   "+str(y_voltage_old.quantize(Decimal('.0001'))))
    ax["C"].set_title(str(value_rc[-1].quantize(Decimal('0.0001')))+"   ←   Current Inductor   →   "+str(y_current_old.quantize(Decimal('.0001'))))
    
    ax["A"].plot([0,0],[0,y_voltage_old],'k--')
    ax["C"].plot([0,0],[0,y_current_old],'k--')

    for (position, left_voltage, right_voltage, left_current, right_current) in zip_out:
        x = position
        
        y1_voltage = left_voltage
        y2_voltage = right_voltage
        
        y1_current = left_current
        y2_current = right_current
        
        ax["A"].plot([x_old,x], [y_voltage_old,y1_voltage],'k-')
        ax["A"].plot([x,x] ,   [y1_voltage,y2_voltage])
        
        ax["C"].plot([x_old,x], [y_current_old,y1_current],'k-')
        ax["C"].plot([x,x],    [y1_current,y2_current])
        
        x_old = x
        
        y_voltage_old = y2_voltage
        y_current_old = y2_current
        
    
    ax["A"].plot([termination_length,termination_length],[0,y_voltage_old],'k--')
    ax["C"].plot([termination_length,termination_length],[0,y_current_old],'k--')
    
    ax["A"].invert_xaxis()
    ax["C"].invert_xaxis()
    
    
    # Get Capacitor Zip
    pos_all, value_lv, value_rv, value_lc, value_rc = get_spatial_zip(Time_Enquriey,Data_Output_Merged, Data_Output_Ordered, False)
    zip_out = zip(pos_all, value_lv, value_rv, value_lc, value_rc)

    x = 0
    x_old = 0
    
    
    y1_voltage = 0
    y2_voltage = 0
    y_voltage_old = value_lv[0]
    
    y1_current = 0
    y2_current = 0
    y_current_old = value_lc[0]
    
    ax["B"].set_title(str(y_voltage_old.quantize(Decimal('.0001')))+"   ←   Voltage Capacitor   →   "+str(value_rv[-1].quantize(Decimal('.0001'))))
    ax["D"].set_title(str(y_current_old.quantize(Decimal('.0001')))+"   ←   Current Capacitor   →   "+str(value_rc[-1].quantize(Decimal('.0001'))))
    
    ax["B"].plot([0,0],[0,y_voltage_old],'k--')
    ax["D"].plot([0,0],[0,y_current_old],'k--')

    for (position, left_voltage, right_voltage, left_current, right_current) in zip_out:
        x = position
        
        y1_voltage = left_voltage
        y2_voltage = right_voltage
        
        y1_current = left_current
        y2_current = right_current
        
        ax["B"].plot([x_old,x], [y_voltage_old,y1_voltage],'k-')
        ax["B"].plot([x,x] ,   [y1_voltage,y2_voltage])
        
        ax["D"].plot([x_old,x], [y_current_old,y1_current],'k-')
        ax["D"].plot([x,x],    [y1_current,y2_current])
        
        x_old = x
        
        y_voltage_old = y2_voltage
        y_current_old = y2_current
        
    
    ax["B"].plot([termination_length,termination_length],[0,y_voltage_old],'k--')
    ax["D"].plot([termination_length,termination_length],[0,y_current_old],'k--')

def plot_diff(Y,X,ax,title_str :str = "Derivative"):
    dy = np.ediff1d(Y[1:])
    dx = np.ediff1d(X[1:])
    
    dydx = dy/dx
    
    ax.set_title(title_str)
    ax.step(X[1:-1],dydx,where="post") 
    
def plot_refelction_diagram(Data_Input: Data_Input_Storage, Data_Output_Ordered : Data_Output_Storage_Ordered, stop_time, ax, mutiple_ticks : bool = True):
    
    C_Time = str(2*Data_Input.Capacitor_Time)
    C_impedance = str(Data_Input.Capacitor_Impedance)
    
    L_Time = str(2*Data_Input.Inductor_Time)
    L_impedance = str(Data_Input.Inductor_Impedance)

    ax.axhline(linewidth=1, color='k')
    ax.axvline(linewidth=1, color='k')
    
    ax.plot([-1,-1],[0,stop_time],'k')
    ax.plot([1,1],[0,stop_time],'k')
    #ax.plot([-1,1],[stop_time,stop_time],'k')
    
    #ax.get_xaxis().set_visible(False)
    ax2 = ax.secondary_yaxis('right')
    ax.set_xticks = ([])
    ax2.set_xticks = ([])
    ax.set_xticklabels = ('')
    ax2.set_xticklabels = ('')
    
    ax.set_ylabel('Capacitor Time Delay = '+ C_Time, fontsize = 'large')
    ax2.set_ylabel('Inductor Time Delay = '+ L_Time, fontsize = 'large')
    #ax.yaxis.set_ticks(np.arange(0, stop_time, 1))
    #ax2.yaxis.set_ticks(np.arange(0, stop_time, 1))
    
    ax.set_title('Capacitor Impedance = '+ C_impedance +'Ω, Inductor Impedance = ' + L_impedance+ 'Ω', fontsize = 'large')
    ax.set_xlabel('Relative distance down Transmission Line')
    
    if(mutiple_ticks):
        ax.yaxis.set_major_locator(MultipleLocator(float(C_Time)))
        ax2.yaxis.set_major_locator(MultipleLocator(float(L_Time)))
        #ax.yaxis.set_major_formatter(FormatStrFormatter('%d'))

        # For the minor ticks, use no labels; default NullFormatter.
        ax.yaxis.set_minor_locator(MultipleLocator(float(C_Time)/2))
        ax2.yaxis.set_minor_locator(MultipleLocator(float(L_Time)/2))
    
    ax.set_ylim(0,stop_time)


    for wave in Data_Output_Ordered.Wavefronts_Sending_Capacitor:

        x1 = -wave.position_start
        x2 = -wave.position_end

        y1 = wave.time_start
        y2 = wave.time_end

        if(wave.time_start <=stop_time):
            ax.plot([x1,x2],[y1,y2],'b-')
            
    for wave in Data_Output_Ordered.Wavefronts_Returning_Capacitor:

        x1 = -wave.position_start
        x2 = -wave.position_end

        y1 = wave.time_start
        y2 = wave.time_end

        if(wave.time_start <=stop_time):
            ax.plot([x1,x2],[y1,y2],'b-')


    for wave in Data_Output_Ordered.Wavefronts_Sending_Inductor:

        x1 = wave.position_start
        x2 = wave.position_end

        y1 = wave.time_start
        y2 = wave.time_end

        if(wave.time_start <=stop_time):
            ax.plot([x1,x2],[y1,y2],'k-')
            
    for wave in Data_Output_Ordered.Wavefronts_Returning_Inductor:

        x1 = wave.position_start
        x2 = wave.position_end

        y1 = wave.time_start
        y2 = wave.time_end

        if(wave.time_start <=stop_time):
            ax.plot([x1,x2],[y1,y2],'k-')

def plot_refelction_diagram_specific(Data_Input: Data_Input_Storage, Data_Output_Ordered : Data_Output_Storage_Ordered, is_current, stop_time, ax, mutiple_ticks : bool = True):
    
    C_Time = str(2*Data_Input.Capacitor_Time)
    C_impedance = str(Data_Input.Capacitor_Impedance)
    
    L_Time = str(2*Data_Input.Inductor_Time)
    L_impedance = str(Data_Input.Inductor_Impedance)
    
    ax.axhline(linewidth=1, color='k')
    ax.axvline(linewidth=1, color='k')
    
    ax.plot([-1,-1],[0,stop_time],'k')
    ax.plot([1,1],[0,stop_time],'k')
    #ax.plot([-1,1],[stop_time,stop_time],'k')
    
    #ax.get_xaxis().set_visible(False)
    ax2 = ax.secondary_yaxis('right')
    ax.set_xticks = ([])
    ax2.set_xticks = ([])
    ax.set_xticklabels = ('')
    ax2.set_xticklabels = ('')
    
    ax.set_ylabel('Capacitor Time Delay = '+ C_Time, fontsize = 'large')
    ax2.set_ylabel('Inductor Time Delay = '+ L_Time, fontsize = 'large')
    #ax.yaxis.set_ticks(np.arange(0, stop_time, 1))
    #ax2.yaxis.set_ticks(np.arange(0, stop_time, 1))
    
    if(is_current):
        ax.set_title('Current Reflection Diagarm \n Capacitor Impedance = '+ C_impedance +'Ω, Inductor Impedance = ' + L_impedance+ 'Ω', fontsize = 'large')
    else:
        ax.set_title('Votlage Reflection Diagarm \n Capacitor Impedance = '+ C_impedance +'Ω, Inductor Impedance = ' + L_impedance+ 'Ω', fontsize = 'large')
        
    # ax.set_xlabel('Relative distance down Transmission Line')
    
    if(mutiple_ticks):
        ax.yaxis.set_major_locator(MultipleLocator(float(C_Time)))
        ax2.yaxis.set_major_locator(MultipleLocator(float(L_Time)))
        #ax.yaxis.set_major_formatter(FormatStrFormatter('%d'))

        # For the minor ticks, use no labels; default NullFormatter.
        ax.yaxis.set_minor_locator(MultipleLocator(float(C_Time)/2))
        ax2.yaxis.set_minor_locator(MultipleLocator(float(L_Time)/2))
    
    ax.set_ylim(0,stop_time)
    
    # Setup Colour Map
    max_cap_s = 0
    min_cap_s = 0
    max_ind_s = 0
    min_ind_s = 0
    
    max_cap_r = 0
    min_cap_r = 0
    max_ind_r = 0
    min_ind_r = 0
    
    boundary = 0 
    
    if(is_current):
        max_cap_s = abs(np.max(Data_Output_Ordered.get_sending("current capacitor")))
        min_cap_s = abs(np.min(Data_Output_Ordered.get_sending("current capacitor")))
        max_ind_s = abs(np.max(Data_Output_Ordered.get_sending("current inductor")))
        min_ind_s = abs(np.min(Data_Output_Ordered.get_sending("current inductor")))

        max_cap_r = abs(np.max(Data_Output_Ordered.get_returning("current capacitor")))
        min_cap_r = abs(np.min(Data_Output_Ordered.get_returning("current capacitor")))
        max_ind_r = abs(np.max(Data_Output_Ordered.get_returning("current inductor")))
        min_ind_r = abs(np.min(Data_Output_Ordered.get_returning("current inductor")))
    else:
        max_cap_s = abs(np.max(Data_Output_Ordered.get_sending("voltage capacitor")))
        min_cap_s = abs(np.min(Data_Output_Ordered.get_sending("voltage capacitor")))
        max_ind_s = abs(np.max(Data_Output_Ordered.get_sending("voltage inductor")))
        min_ind_s = abs(np.min(Data_Output_Ordered.get_sending("voltage inductor")))

        max_cap_r = abs(np.max(Data_Output_Ordered.get_returning("voltage capacitor")))
        min_cap_r = abs(np.min(Data_Output_Ordered.get_returning("voltage capacitor")))
        max_ind_r = abs(np.max(Data_Output_Ordered.get_returning("voltage inductor")))
        min_ind_r = abs(np.min(Data_Output_Ordered.get_returning("voltage inductor")))
        
    boundary = max(max_cap_s,min_cap_s,max_ind_s,min_ind_s,max_cap_r,min_cap_r,max_ind_r,min_ind_r)
    
    colour_map = cm.seismic
    norm = mpl.colors.Normalize(vmin=-boundary, vmax=boundary)
    
    for wave in Data_Output_Ordered.Wavefronts_Sending_Capacitor:

        x1 = -wave.position_start
        x2 = -wave.position_end

        y1 = wave.time_start
        y2 = wave.time_end
        
        mag = 0
        
        if(is_current):
            mag = float(wave.magnitude_current)
        else:
            mag = float(wave.magnitude_voltage)

        if(wave.time_start <=stop_time):
            ax.plot([x1,x2],[y1,y2],c=colour_map(norm(mag)))
            # ax.plot([(x2-x1)/2],[y1 + (y2-y1)/2], marker ='o',c=colour_map(norm(mag)),markersize=15)
            
    for wave in Data_Output_Ordered.Wavefronts_Returning_Capacitor:

        x1 = -wave.position_start
        x2 = -wave.position_end

        y1 = wave.time_start
        y2 = wave.time_end
        
        mag = 0
        
        if(is_current):
            mag = float(wave.magnitude_current)
        else:
            mag = float(wave.magnitude_voltage)

        if(wave.time_start <=stop_time):
            ax.plot([x1,x2],[y1,y2],c=colour_map(norm(mag)))
            # ax.plot([-(x2-x1)/2],[y1 + (y2-y1)/2], marker ='o',c=colour_map(norm(mag)),markersize=15)

    # Inductor Wavefronts
    for wave in Data_Output_Ordered.Wavefronts_Sending_Inductor:

        x1 = wave.position_start
        x2 = wave.position_end

        y1 = wave.time_start
        y2 = wave.time_end

        mag = 0
        
        if(is_current):
            mag = float(wave.magnitude_current)
        else:
            mag = float(wave.magnitude_voltage)

        if(wave.time_start <=stop_time):
            ax.plot([x1,x2],[y1,y2],c=colour_map(norm(mag)))
            # ax.plot([(x2-x1)/2],[y1 + (y2-y1)/2], marker ='o',c=colour_map(norm(mag)),markersize=15)
            
    for wave in Data_Output_Ordered.Wavefronts_Returning_Inductor:

        x1 = wave.position_start
        x2 = wave.position_end

        y1 = wave.time_start
        y2 = wave.time_end

        mag = 0
        
        if(is_current):
            mag = float(wave.magnitude_current)
        else:
            mag = float(wave.magnitude_voltage)

        if(wave.time_start <=stop_time):
            ax.plot([x1,x2],[y1,y2],c=colour_map(norm(mag)))
            # ax.plot([-(x2-x1)/2],[y1 + (y2-y1)/2], marker ='o',c=colour_map(norm(mag)),markersize=15)      
            
def plot_refelction_diagram_sending(Data_Input: Data_Input_Storage, Data_Output_Ordered : Data_Output_Storage_Ordered, is_current, stop_time, ax, mutiple_ticks : bool = True):
    
        
    non_active_wavefront_colour = 'xkcd:dark grey'
    
    C_Time = str(2*Data_Input.Capacitor_Time)
    C_impedance = str(Data_Input.Capacitor_Impedance)
    
    L_Time = str(2*Data_Input.Inductor_Time)
    L_impedance = str(Data_Input.Inductor_Impedance)
    
    ax.axhline(linewidth=1, color='k')
    ax.axvline(linewidth=1, color='k')
    
    ax.plot([-1,-1],[0,stop_time],'k')
    ax.plot([1,1],[0,stop_time],'k')
    #ax.plot([-1,1],[stop_time,stop_time],'k')
    
    #ax.get_xaxis().set_visible(False)
    ax2 = ax.secondary_yaxis('right')
    ax.set_xticks = ([])
    ax2.set_xticks = ([])
    ax.set_xticklabels = ('')
    ax2.set_xticklabels = ('')
    
    ax.set_ylabel('Capacitor Time Delay = '+ C_Time, fontsize = 'large')
    ax2.set_ylabel('Inductor Time Delay = '+ L_Time, fontsize = 'large')
    #ax.yaxis.set_ticks(np.arange(0, stop_time, 1))
    #ax2.yaxis.set_ticks(np.arange(0, stop_time, 1))
    
    if(is_current):
        ax.set_title('Sending Current Reflection Diagarm \n Capacitor Impedance = '+ C_impedance +'Ω, Inductor Impedance = ' + L_impedance+ 'Ω', fontsize = 'large')
    else:
        ax.set_title('Sending Votlage Reflection Diagarm \n Capacitor Impedance = '+ C_impedance +'Ω, Inductor Impedance = ' + L_impedance+ 'Ω', fontsize = 'large')
        
    # ax.set_xlabel('Relative distance down Transmission Line')
    
    if(mutiple_ticks):
        ax.yaxis.set_major_locator(MultipleLocator(float(C_Time)))
        ax2.yaxis.set_major_locator(MultipleLocator(float(L_Time)))
        #ax.yaxis.set_major_formatter(FormatStrFormatter('%d'))

        # For the minor ticks, use no labels; default NullFormatter.
        ax.yaxis.set_minor_locator(MultipleLocator(float(C_Time)/2))
        ax2.yaxis.set_minor_locator(MultipleLocator(float(L_Time)/2))
    
    ax.set_ylim(0,stop_time)
    
    # Setup Colour Map
    max_cap_s = 0
    min_cap_s = 0
    max_ind_s = 0
    min_ind_s = 0
    
    max_cap_r = 0
    min_cap_r = 0
    max_ind_r = 0
    min_ind_r = 0
    
    boundary = 0 
    
    if(is_current):
        max_cap_s = abs(np.max(Data_Output_Ordered.get_sending("current capacitor")))
        min_cap_s = abs(np.min(Data_Output_Ordered.get_sending("current capacitor")))
        max_ind_s = abs(np.max(Data_Output_Ordered.get_sending("current inductor")))
        min_ind_s = abs(np.min(Data_Output_Ordered.get_sending("current inductor")))

        max_cap_r = abs(np.max(Data_Output_Ordered.get_returning("current capacitor")))
        min_cap_r = abs(np.min(Data_Output_Ordered.get_returning("current capacitor")))
        max_ind_r = abs(np.max(Data_Output_Ordered.get_returning("current inductor")))
        min_ind_r = abs(np.min(Data_Output_Ordered.get_returning("current inductor")))
    else:
        max_cap_s = abs(np.max(Data_Output_Ordered.get_sending("voltage capacitor")))
        min_cap_s = abs(np.min(Data_Output_Ordered.get_sending("voltage capacitor")))
        max_ind_s = abs(np.max(Data_Output_Ordered.get_sending("voltage inductor")))
        min_ind_s = abs(np.min(Data_Output_Ordered.get_sending("voltage inductor")))

        max_cap_r = abs(np.max(Data_Output_Ordered.get_returning("voltage capacitor")))
        min_cap_r = abs(np.min(Data_Output_Ordered.get_returning("voltage capacitor")))
        max_ind_r = abs(np.max(Data_Output_Ordered.get_returning("voltage inductor")))
        min_ind_r = abs(np.min(Data_Output_Ordered.get_returning("voltage inductor")))
        
    boundary = max(max_cap_s,min_cap_s,max_ind_s,min_ind_s,max_cap_r,min_cap_r,max_ind_r,min_ind_r)
    
    colour_map = cm.seismic
    norm = mpl.colors.Normalize(vmin=-boundary, vmax=boundary)
    
    for wave in Data_Output_Ordered.Wavefronts_Sending_Capacitor:

        x1 = -wave.position_start
        x2 = -wave.position_end

        y1 = wave.time_start
        y2 = wave.time_end
        
        mag = 0
        
        if(is_current):
            mag = float(wave.magnitude_current)
        else:
            mag = float(wave.magnitude_voltage)

        if(wave.time_start <=stop_time):
            ax.plot([x1,x2],[y1,y2],c=colour_map(norm(mag)),zorder=2)
            # ax.plot([(x2-x1)/2],[y1 + (y2-y1)/2], marker ='o',c=colour_map(norm(mag)),markersize=15)
            
    for wave in Data_Output_Ordered.Wavefronts_Returning_Capacitor:

        x1 = -wave.position_start
        x2 = -wave.position_end

        y1 = wave.time_start
        y2 = wave.time_end
        
        mag = 0
        
        if(is_current):
            mag = float(wave.magnitude_current)
        else:
            mag = float(wave.magnitude_voltage)

        if(wave.time_start <=stop_time):
            ax.plot([x1,x2],[y1,y2],c=non_active_wavefront_colour,linestyle='dashed',zorder=1)
            # ax.plot([-(x2-x1)/2],[y1 + (y2-y1)/2], marker ='o',c=colour_map(norm(mag)),markersize=15)

    # Inductor Wavefronts
    for wave in Data_Output_Ordered.Wavefronts_Sending_Inductor:

        x1 = wave.position_start
        x2 = wave.position_end

        y1 = wave.time_start
        y2 = wave.time_end

        mag = 0
        
        if(is_current):
            mag = float(wave.magnitude_current)
        else:
            mag = float(wave.magnitude_voltage)

        if(wave.time_start <=stop_time):
            ax.plot([x1,x2],[y1,y2],c=colour_map(norm(mag)),zorder=2)
            # ax.plot([(x2-x1)/2],[y1 + (y2-y1)/2], marker ='o',c=colour_map(norm(mag)),markersize=15)
            
    for wave in Data_Output_Ordered.Wavefronts_Returning_Inductor:

        x1 = wave.position_start
        x2 = wave.position_end

        y1 = wave.time_start
        y2 = wave.time_end

        mag = 0
        
        if(is_current):
            mag = float(wave.magnitude_current)
        else:
            mag = float(wave.magnitude_voltage)

        if(wave.time_start <=stop_time):
            ax.plot([x1,x2],[y1,y2],c=non_active_wavefront_colour,linestyle='dashed',zorder=1)
            # ax.plot([-(x2-x1)/2],[y1 + (y2-y1)/2], marker ='o',c=colour_map(norm(mag)),markersize=15)      

def plot_refelction_diagram_returning(Data_Input: Data_Input_Storage, Data_Output_Ordered : Data_Output_Storage_Ordered, is_current, stop_time, ax, mutiple_ticks : bool = True):
    
        
    non_active_wavefront_colour = 'xkcd:dark grey'
    
    C_Time = str(2*Data_Input.Capacitor_Time)
    C_impedance = str(Data_Input.Capacitor_Impedance)
    
    L_Time = str(2*Data_Input.Inductor_Time)
    L_impedance = str(Data_Input.Inductor_Impedance)
    
    ax.axhline(linewidth=1, color='k')
    ax.axvline(linewidth=1, color='k')
    
    ax.plot([-1,-1],[0,stop_time],'k')
    ax.plot([1,1],[0,stop_time],'k')
    #ax.plot([-1,1],[stop_time,stop_time],'k')
    
    #ax.get_xaxis().set_visible(False)
    ax2 = ax.secondary_yaxis('right')
    ax.set_xticks = ([])
    ax2.set_xticks = ([])
    ax.set_xticklabels = ('')
    ax2.set_xticklabels = ('')
    
    ax.set_ylabel('Capacitor Time Delay = '+ C_Time, fontsize = 'large')
    ax2.set_ylabel('Inductor Time Delay = '+ L_Time, fontsize = 'large')
    #ax.yaxis.set_ticks(np.arange(0, stop_time, 1))
    #ax2.yaxis.set_ticks(np.arange(0, stop_time, 1))
    
    if(is_current):
        ax.set_title('Returning Current Reflection Diagarm \n Capacitor Impedance = '+ C_impedance +'Ω, Inductor Impedance = ' + L_impedance+ 'Ω', fontsize = 'large')
    else:
        ax.set_title('Returning Votlage Reflection Diagarm \n Capacitor Impedance = '+ C_impedance +'Ω, Inductor Impedance = ' + L_impedance+ 'Ω', fontsize = 'large')
        
    # ax.set_xlabel('Relative distance down Transmission Line')
    
    if(mutiple_ticks):
        ax.yaxis.set_major_locator(MultipleLocator(float(C_Time)))
        ax2.yaxis.set_major_locator(MultipleLocator(float(L_Time)))
        #ax.yaxis.set_major_formatter(FormatStrFormatter('%d'))

        # For the minor ticks, use no labels; default NullFormatter.
        ax.yaxis.set_minor_locator(MultipleLocator(float(C_Time)/2))
        ax2.yaxis.set_minor_locator(MultipleLocator(float(L_Time)/2))
    
    ax.set_ylim(0,stop_time)
    
    # Setup Colour Map
    max_cap_s = 0
    min_cap_s = 0
    max_ind_s = 0
    min_ind_s = 0
    
    max_cap_r = 0
    min_cap_r = 0
    max_ind_r = 0
    min_ind_r = 0
    
    boundary = 0 
    
    if(is_current):
        max_cap_s = abs(np.max(Data_Output_Ordered.get_sending("current capacitor")))
        min_cap_s = abs(np.min(Data_Output_Ordered.get_sending("current capacitor")))
        max_ind_s = abs(np.max(Data_Output_Ordered.get_sending("current inductor")))
        min_ind_s = abs(np.min(Data_Output_Ordered.get_sending("current inductor")))

        max_cap_r = abs(np.max(Data_Output_Ordered.get_returning("current capacitor")))
        min_cap_r = abs(np.min(Data_Output_Ordered.get_returning("current capacitor")))
        max_ind_r = abs(np.max(Data_Output_Ordered.get_returning("current inductor")))
        min_ind_r = abs(np.min(Data_Output_Ordered.get_returning("current inductor")))
    else:
        max_cap_s = abs(np.max(Data_Output_Ordered.get_sending("voltage capacitor")))
        min_cap_s = abs(np.min(Data_Output_Ordered.get_sending("voltage capacitor")))
        max_ind_s = abs(np.max(Data_Output_Ordered.get_sending("voltage inductor")))
        min_ind_s = abs(np.min(Data_Output_Ordered.get_sending("voltage inductor")))

        max_cap_r = abs(np.max(Data_Output_Ordered.get_returning("voltage capacitor")))
        min_cap_r = abs(np.min(Data_Output_Ordered.get_returning("voltage capacitor")))
        max_ind_r = abs(np.max(Data_Output_Ordered.get_returning("voltage inductor")))
        min_ind_r = abs(np.min(Data_Output_Ordered.get_returning("voltage inductor")))
        
    boundary = max(max_cap_s,min_cap_s,max_ind_s,min_ind_s,max_cap_r,min_cap_r,max_ind_r,min_ind_r)
    
    colour_map = cm.seismic
    norm = mpl.colors.Normalize(vmin=-boundary, vmax=boundary)
    
    for wave in Data_Output_Ordered.Wavefronts_Returning_Capacitor:

        x1 = -wave.position_start
        x2 = -wave.position_end

        y1 = wave.time_start
        y2 = wave.time_end
        
        mag = 0
        
        if(is_current):
            mag = float(wave.magnitude_current)
        else:
            mag = float(wave.magnitude_voltage)

        if(wave.time_start <=stop_time):
            ax.plot([x1,x2],[y1,y2],c=colour_map(norm(mag)),zorder=2)
            # ax.plot([(x2-x1)/2],[y1 + (y2-y1)/2], marker ='o',c=colour_map(norm(mag)),markersize=15)
            
    for wave in Data_Output_Ordered.Wavefronts_Sending_Capacitor:

        x1 = -wave.position_start
        x2 = -wave.position_end

        y1 = wave.time_start
        y2 = wave.time_end
        
        mag = 0
        
        if(is_current):
            mag = float(wave.magnitude_current)
        else:
            mag = float(wave.magnitude_voltage)

        if(wave.time_start <=stop_time):
            ax.plot([x1,x2],[y1,y2],c=non_active_wavefront_colour,linestyle='dashed',zorder=1)
            # ax.plot([-(x2-x1)/2],[y1 + (y2-y1)/2], marker ='o',c=colour_map(norm(mag)),markersize=15)

    # Inductor Wavefronts
    for wave in Data_Output_Ordered.Wavefronts_Returning_Inductor:

        x1 = wave.position_start
        x2 = wave.position_end

        y1 = wave.time_start
        y2 = wave.time_end

        mag = 0
        
        if(is_current):
            mag = float(wave.magnitude_current)
        else:
            mag = float(wave.magnitude_voltage)

        if(wave.time_start <=stop_time):
            ax.plot([x1,x2],[y1,y2],c=colour_map(norm(mag)),zorder=2)
            # ax.plot([(x2-x1)/2],[y1 + (y2-y1)/2], marker ='o',c=colour_map(norm(mag)),markersize=15)
            
    for wave in Data_Output_Ordered.Wavefronts_Sending_Inductor:

        x1 = wave.position_start
        x2 = wave.position_end

        y1 = wave.time_start
        y2 = wave.time_end

        mag = 0
        
        if(is_current):
            mag = float(wave.magnitude_current)
        else:
            mag = float(wave.magnitude_voltage)

        if(wave.time_start <=stop_time):
            ax.plot([x1,x2],[y1,y2],c=non_active_wavefront_colour,linestyle='dashed',zorder=1)
            # ax.plot([-(x2-x1)/2],[y1 + (y2-y1)/2], marker ='o',c=colour_map(norm(mag)),markersize=15)    

def plot_refelction_diagram_one_tx_s_and_r(Data_Input: Data_Input_Storage, Data_Output_Ordered : Data_Output_Storage_Ordered, is_capacitor,is_current, stop_time, ax, mutiple_ticks : bool = True):
    
        
    non_active_wavefront_colour = 'xkcd:dark grey'
    
    C_Time = str(2*Data_Input.Capacitor_Time)
    C_impedance = str(Data_Input.Capacitor_Impedance)
    
    L_Time = str(2*Data_Input.Inductor_Time)
    L_impedance = str(Data_Input.Inductor_Impedance)
    
    ax.axhline(linewidth=1, color='k')
    ax.axvline(linewidth=1, color='k')
    
    ax.plot([-1,-1],[0,stop_time],'k')
    ax.plot([1,1],[0,stop_time],'k')
    #ax.plot([-1,1],[stop_time,stop_time],'k')
    
    #ax.get_xaxis().set_visible(False)
    ax2 = ax.secondary_yaxis('right')
    ax.set_xticks = ([])
    ax2.set_xticks = ([])
    ax.set_xticklabels = ('')
    ax2.set_xticklabels = ('')
    
    ax.set_ylabel('Capacitor Time Delay = '+ C_Time, fontsize = 'large')
    ax2.set_ylabel('Inductor Time Delay = '+ L_Time, fontsize = 'large')
    #ax.yaxis.set_ticks(np.arange(0, stop_time, 1))
    #ax2.yaxis.set_ticks(np.arange(0, stop_time, 1))
    
    title_str =""
    
    if(is_capacitor):
        title_str += "Capacitor "
    else:
        title_str += "Inductor "
        
    if(is_current):
        title_str += "Current "
    else:
        title_str += "Voltage "
    
    
    ax.set_title(title_str+'Reflection Diagarm \n Capacitor Impedance = '+ C_impedance +'Ω, Inductor Impedance = ' + L_impedance+ 'Ω', fontsize = 'large')
        
    # ax.set_xlabel('Relative distance down Transmission Line')
    
    if(mutiple_ticks):
        ax.yaxis.set_major_locator(MultipleLocator(float(C_Time)))
        ax2.yaxis.set_major_locator(MultipleLocator(float(L_Time)))
        #ax.yaxis.set_major_formatter(FormatStrFormatter('%d'))

        # For the minor ticks, use no labels; default NullFormatter.
        ax.yaxis.set_minor_locator(MultipleLocator(float(C_Time)/2))
        ax2.yaxis.set_minor_locator(MultipleLocator(float(L_Time)/2))
    
    ax.set_ylim(0,stop_time)
    
    # Setup Colour Map
    max_cap_s = 0
    min_cap_s = 0
    max_ind_s = 0
    min_ind_s = 0
    
    max_cap_r = 0
    min_cap_r = 0
    max_ind_r = 0
    min_ind_r = 0
    
    boundary = 0 
    
    if(is_current):
        max_cap_s = abs(np.max(Data_Output_Ordered.get_sending("current capacitor")))
        min_cap_s = abs(np.min(Data_Output_Ordered.get_sending("current capacitor")))
        max_ind_s = abs(np.max(Data_Output_Ordered.get_sending("current inductor")))
        min_ind_s = abs(np.min(Data_Output_Ordered.get_sending("current inductor")))

        max_cap_r = abs(np.max(Data_Output_Ordered.get_returning("current capacitor")))
        min_cap_r = abs(np.min(Data_Output_Ordered.get_returning("current capacitor")))
        max_ind_r = abs(np.max(Data_Output_Ordered.get_returning("current inductor")))
        min_ind_r = abs(np.min(Data_Output_Ordered.get_returning("current inductor")))
    else:
        max_cap_s = abs(np.max(Data_Output_Ordered.get_sending("voltage capacitor")))
        min_cap_s = abs(np.min(Data_Output_Ordered.get_sending("voltage capacitor")))
        max_ind_s = abs(np.max(Data_Output_Ordered.get_sending("voltage inductor")))
        min_ind_s = abs(np.min(Data_Output_Ordered.get_sending("voltage inductor")))

        max_cap_r = abs(np.max(Data_Output_Ordered.get_returning("voltage capacitor")))
        min_cap_r = abs(np.min(Data_Output_Ordered.get_returning("voltage capacitor")))
        max_ind_r = abs(np.max(Data_Output_Ordered.get_returning("voltage inductor")))
        min_ind_r = abs(np.min(Data_Output_Ordered.get_returning("voltage inductor")))
        
    boundary = max(max_cap_s,min_cap_s,max_ind_s,min_ind_s,max_cap_r,min_cap_r,max_ind_r,min_ind_r)
    
    colour_map = cm.seismic
    norm = mpl.colors.Normalize(vmin=-boundary, vmax=boundary)
    
    for wave in Data_Output_Ordered.Wavefronts_Returning_Capacitor:

        x1 = -wave.position_start
        x2 = -wave.position_end

        y1 = wave.time_start
        y2 = wave.time_end
        
        mag = 0
        
        if(is_current):
            mag = float(wave.magnitude_current)
        else:
            mag = float(wave.magnitude_voltage)

        if(wave.time_start <=stop_time):
            if(is_capacitor):
                ax.plot([x1,x2],[y1,y2],c=colour_map(norm(mag)),zorder=2)
            else:
                ax.plot([x1,x2],[y1,y2],c=non_active_wavefront_colour,linestyle='dashed',zorder=1)
            
    for wave in Data_Output_Ordered.Wavefronts_Sending_Capacitor:

        x1 = -wave.position_start
        x2 = -wave.position_end

        y1 = wave.time_start
        y2 = wave.time_end
        
        mag = 0
        
        if(is_current):
            mag = float(wave.magnitude_current)
        else:
            mag = float(wave.magnitude_voltage)

        if(wave.time_start <=stop_time):
            if(is_capacitor):
                ax.plot([x1,x2],[y1,y2],c=colour_map(norm(mag)),zorder=2)
            else:
                ax.plot([x1,x2],[y1,y2],c=non_active_wavefront_colour,linestyle='dashed',zorder=1)

    # Inductor Wavefronts
    for wave in Data_Output_Ordered.Wavefronts_Returning_Inductor:

        x1 = wave.position_start
        x2 = wave.position_end

        y1 = wave.time_start
        y2 = wave.time_end

        mag = 0
        
        if(is_current):
            mag = float(wave.magnitude_current)
        else:
            mag = float(wave.magnitude_voltage)

        if(wave.time_start <=stop_time):
            if(not is_capacitor):
                ax.plot([x1,x2],[y1,y2],c=colour_map(norm(mag)),zorder=2)
            else:
                ax.plot([x1,x2],[y1,y2],c=non_active_wavefront_colour,linestyle='dashed',zorder=1)
            # ax.plot([(x2-x1)/2],[y1 + (y2-y1)/2], marker ='o',c=colour_map(norm(mag)),markersize=15)
            
    for wave in Data_Output_Ordered.Wavefronts_Sending_Inductor:

        x1 = wave.position_start
        x2 = wave.position_end

        y1 = wave.time_start
        y2 = wave.time_end

        mag = 0
        
        if(is_current):
            mag = float(wave.magnitude_current)
        else:
            mag = float(wave.magnitude_voltage)

        if(wave.time_start <=stop_time):
            if(not is_capacitor):
                ax.plot([x1,x2],[y1,y2],c=colour_map(norm(mag)),zorder=2)  
            else:
                ax.plot([x1,x2],[y1,y2],c=non_active_wavefront_colour,linestyle='dashed',zorder=1)
            
def plot_refelction_diagram_one_tx_s_or_r(Data_Input: Data_Input_Storage, Data_Output_Ordered : Data_Output_Storage_Ordered, is_capacitor,is_sending,is_current, stop_time, ax, mutiple_ticks : bool = True):
    
        
    non_active_wavefront_colour = 'xkcd:dark grey'
    
    C_Time = str(2*Data_Input.Capacitor_Time)
    C_impedance = str(Data_Input.Capacitor_Impedance)
    
    L_Time = str(2*Data_Input.Inductor_Time)
    L_impedance = str(Data_Input.Inductor_Impedance)
    
    ax.axhline(linewidth=1, color='k')
    ax.axvline(linewidth=1, color='k')
    
    ax.plot([-1,-1],[0,stop_time],'k')
    ax.plot([1,1],[0,stop_time],'k')
    #ax.plot([-1,1],[stop_time,stop_time],'k')
    
    #ax.get_xaxis().set_visible(False)
    ax2 = ax.secondary_yaxis('right')
    ax.set_xticks = ([])
    ax2.set_xticks = ([])
    ax.set_xticklabels = ('')
    ax2.set_xticklabels = ('')
    
    ax.set_ylabel('Capacitor Time Delay = '+ C_Time, fontsize = 'large')
    ax2.set_ylabel('Inductor Time Delay = '+ L_Time, fontsize = 'large')
    #ax.yaxis.set_ticks(np.arange(0, stop_time, 1))
    #ax2.yaxis.set_ticks(np.arange(0, stop_time, 1))
    
    title_str =""
    
    if(is_capacitor):
        title_str += "Capacitor "
    else:
        title_str += "Inductor "
        
    if(is_sending):
        title_str += "Sending "
    else:
        title_str += "Returning "
        
    if(is_current):
        title_str += "Current "
    else:
        title_str += "Voltage "
    
    
    ax.set_title(title_str+'Reflection Diagarm \n Capacitor Impedance = '+ C_impedance +'Ω, Inductor Impedance = ' + L_impedance+ 'Ω', fontsize = 'large')
        
    # ax.set_xlabel('Relative distance down Transmission Line')
    
    if(mutiple_ticks):
        ax.yaxis.set_major_locator(MultipleLocator(float(C_Time)))
        ax2.yaxis.set_major_locator(MultipleLocator(float(L_Time)))
        #ax.yaxis.set_major_formatter(FormatStrFormatter('%d'))

        # For the minor ticks, use no labels; default NullFormatter.
        ax.yaxis.set_minor_locator(MultipleLocator(float(C_Time)/2))
        ax2.yaxis.set_minor_locator(MultipleLocator(float(L_Time)/2))
    
    ax.set_ylim(0,stop_time)
    
    # Setup Colour Map
    max_cap_s = 0
    min_cap_s = 0
    max_ind_s = 0
    min_ind_s = 0
    
    max_cap_r = 0
    min_cap_r = 0
    max_ind_r = 0
    min_ind_r = 0
    
    boundary = 0 
    
    if(is_current):
        max_cap_s = abs(np.max(Data_Output_Ordered.get_sending("current capacitor")))
        min_cap_s = abs(np.min(Data_Output_Ordered.get_sending("current capacitor")))
        max_ind_s = abs(np.max(Data_Output_Ordered.get_sending("current inductor")))
        min_ind_s = abs(np.min(Data_Output_Ordered.get_sending("current inductor")))

        max_cap_r = abs(np.max(Data_Output_Ordered.get_returning("current capacitor")))
        min_cap_r = abs(np.min(Data_Output_Ordered.get_returning("current capacitor")))
        max_ind_r = abs(np.max(Data_Output_Ordered.get_returning("current inductor")))
        min_ind_r = abs(np.min(Data_Output_Ordered.get_returning("current inductor")))
    else:
        max_cap_s = abs(np.max(Data_Output_Ordered.get_sending("voltage capacitor")))
        min_cap_s = abs(np.min(Data_Output_Ordered.get_sending("voltage capacitor")))
        max_ind_s = abs(np.max(Data_Output_Ordered.get_sending("voltage inductor")))
        min_ind_s = abs(np.min(Data_Output_Ordered.get_sending("voltage inductor")))

        max_cap_r = abs(np.max(Data_Output_Ordered.get_returning("voltage capacitor")))
        min_cap_r = abs(np.min(Data_Output_Ordered.get_returning("voltage capacitor")))
        max_ind_r = abs(np.max(Data_Output_Ordered.get_returning("voltage inductor")))
        min_ind_r = abs(np.min(Data_Output_Ordered.get_returning("voltage inductor")))
        
    boundary = max(max_cap_s,min_cap_s,max_ind_s,min_ind_s,max_cap_r,min_cap_r,max_ind_r,min_ind_r)
    
    colour_map = cm.seismic
    norm = mpl.colors.Normalize(vmin=-boundary, vmax=boundary)
    
    for wave in Data_Output_Ordered.Wavefronts_Returning_Capacitor:

        x1 = -wave.position_start
        x2 = -wave.position_end

        y1 = wave.time_start
        y2 = wave.time_end
        
        mag = 0
        
        if(is_current):
            mag = float(wave.magnitude_current)
        else:
            mag = float(wave.magnitude_voltage)

        if(wave.time_start <=stop_time):
            if(is_capacitor and not is_sending):
                ax.plot([x1,x2],[y1,y2],c=colour_map(norm(mag)),zorder=2)
            else:
                ax.plot([x1,x2],[y1,y2],c=non_active_wavefront_colour,linestyle='dashed',zorder=1)
            
    for wave in Data_Output_Ordered.Wavefronts_Sending_Capacitor:

        x1 = -wave.position_start
        x2 = -wave.position_end

        y1 = wave.time_start
        y2 = wave.time_end
        
        mag = 0
        
        if(is_current):
            mag = float(wave.magnitude_current)
        else:
            mag = float(wave.magnitude_voltage)

        if(wave.time_start <=stop_time):
            if(is_capacitor and is_sending):
                ax.plot([x1,x2],[y1,y2],c=colour_map(norm(mag)),zorder=2)
            else:
                ax.plot([x1,x2],[y1,y2],c=non_active_wavefront_colour,linestyle='dashed',zorder=1)

    # Inductor Wavefronts
    for wave in Data_Output_Ordered.Wavefronts_Returning_Inductor:

        x1 = wave.position_start
        x2 = wave.position_end

        y1 = wave.time_start
        y2 = wave.time_end

        mag = 0
        
        if(is_current):
            mag = float(wave.magnitude_current)
        else:
            mag = float(wave.magnitude_voltage)

        if(wave.time_start <=stop_time):
            if(not is_capacitor and not is_sending):
                ax.plot([x1,x2],[y1,y2],c=colour_map(norm(mag)),zorder=2)
            else:
                ax.plot([x1,x2],[y1,y2],c=non_active_wavefront_colour,linestyle='dashed',zorder=1)
            # ax.plot([(x2-x1)/2],[y1 + (y2-y1)/2], marker ='o',c=colour_map(norm(mag)),markersize=15)
            
    for wave in Data_Output_Ordered.Wavefronts_Sending_Inductor:

        x1 = wave.position_start
        x2 = wave.position_end

        y1 = wave.time_start
        y2 = wave.time_end

        mag = 0
        
        if(is_current):
            mag = float(wave.magnitude_current)
        else:
            mag = float(wave.magnitude_voltage)

        if(wave.time_start <=stop_time):
            if(not is_capacitor and is_sending):
                ax.plot([x1,x2],[y1,y2],c=colour_map(norm(mag)),zorder=2)  
            else:
                ax.plot([x1,x2],[y1,y2],c=non_active_wavefront_colour,linestyle='dashed',zorder=1)

# UI
def spatial_investigator_ui(data_input : Data_Input_Storage, data_output_merged : Data_Output_Storage, data_output_ordered: Data_Output_Storage_Ordered):
    fig_s,ax_s = plt.subplot_mosaic(
        """
        AB
        CD
        """
    )

    increment_button = widgets.Button(description = "step forward", layout=widgets.Layout(width='auto'))
    decrement_button = widgets.Button(description = "step backward", layout=widgets.Layout(width='auto'))
    increment_text = widgets.FloatText(description = 'val', value=0.1)


    time_slider = widgets.FloatSlider(value=0, min =0, max = data_input.Simulation_Stop_Time-1, layout=widgets.Layout(width='auto'))
    output = widgets.Output()

    def on_increment_click(b):
        time_slider.value += increment_text.value
        plot_spatial_at_time_4(Decimal(str(time_slider.value)),data_output_merged,data_output_ordered,fig_s,ax_s)
        
    def on_decrement_click(b):
        time_slider.value -= increment_text.value
        plot_spatial_at_time_4(Decimal(str(time_slider.value)),data_output_merged,data_output_ordered,fig_s,ax_s)
        
    def handle_slider_change(change):
        if(isinstance(change.new,dict)):
            if(len(change.new) > 0):
                change_str = str(change.new['value'])
                plot_spatial_at_time_4(Decimal(change_str),data_output_merged,data_output_ordered,fig_s,ax_s)

    increment_button.on_click(on_increment_click)
    decrement_button.on_click(on_decrement_click)
    time_slider.observe(handle_slider_change)

    increment_grid = widgets.GridspecLayout(1,3)
    increment_grid[0,0] = decrement_button
    increment_grid[0,1] = increment_button
    increment_grid[0,2] = increment_text

    display(increment_grid,time_slider)

def video_save_ui(data_input : Data_Input_Storage, data_output_merged : Data_Output_Storage, data_output_ordered: Data_Output_Storage_Ordered):
    
    fig_save,ax_save = plt.subplot_mosaic(
        """
        AB
        CD
        """
    )
    
    save_title = widgets.Label('Video Saving Widget!!')
    save_sub_title = widgets.Label('Max Simulation time = ' + str(data_input.Simulation_Stop_Time.quantize(Decimal('0.01'))))

    fps_toggle = widgets.ToggleButtons(
        options=['15', '30', '60'],
        description='fps:',
    )

    start_input = widgets.FloatText(value=0)
    end_input = widgets.FloatText(value=data_input.Simulation_Stop_Time)
    video_length_input = widgets.FloatText(value=5)
    dpi_input = widgets.FloatText(value=100)

    duration_bar = widgets.HBox([
        widgets.Label("Start time : "),
        start_input,
        widgets.Label("End time : "),
        end_input,
        widgets.Label("Video Length : "),
        video_length_input,
        widgets.Label("DPI : "),
        dpi_input
    ])

    save_ext = widgets.Output(layout={})
    save_ext.append_stdout('.mp4')


    ProgressBar = widgets.IntProgress(min=0, max=int(100)) # instantiate the bar
    ProgressBar_Label = widgets.Label("Ready when you are !  ")

    save_name = widgets.Text(placeholder='Type Filename')
    save_button = widgets.Button(description = "save video")

    save_name_grid = widgets.HBox([save_name,save_ext,save_button])
    
    def on_save_click (b):
        if(save_name.value==''):
            raise Exception("Enter Valid File name")
        else:
            number_frames =  video_length_input.value*float(fps_toggle.value)
            time_increment = (end_input.value - start_input.value)/number_frames
            
            ProgressBar.max = number_frames
            metadata = dict(title='Distributed Modelling', artist='Jonathan Meerholz')
            writer = FFMpegWriter(fps=float(fps_toggle.value), metadata=metadata)
            
            time = start_input.value
            frame_counter = 0
            ProgressBar.value = 0
            with writer.saving(fig_save, (save_name.value+".mp4"), float(dpi_input.value)):
                
                for _ in range(0,int(number_frames)):
                    
                    plot_spatial_at_time_4(Decimal(str(time)),data_output_merged,data_output_ordered,fig_save,ax_save)
                    writer.grab_frame()
                    time += time_increment
                    frame_counter +=1
                    ProgressBar.value =frame_counter
                    ProgressBar_Label.value = "frame " + str(frame_counter) + " of " + str(number_frames) 
                    
            ProgressBar_Label.value += " Completed !"

    save_button.on_click(on_save_click)

    display(save_title,save_sub_title,fps_toggle,duration_bar,save_name_grid,widgets.HBox([ProgressBar_Label,ProgressBar]))