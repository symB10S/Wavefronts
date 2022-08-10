from decimal import *
from collections import deque
from re import A, L
import numpy as np
import math

getcontext().traps[FloatOperation] = True

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

def delete_alternating(arr):
    
    x_len,ylen = arr.shape
    
    x_delete = np.arange(1,x_len,2)
    y_delete = np.arange(1,ylen,2)

    arr_deleted = np.delete(arr,x_delete, axis=0)
    arr_deleted = np.delete(arr_deleted,y_delete, axis=1)
    
    return arr_deleted

## CALCULATED VARIABLES ##
def Calculate_Variables(Inductor_List, Capacitor_List, Circuit_List):

    global Number_Periods 
    global Simulation_Stop_Time 
    global Is_Buck

    global Voltage_Souce_Magnitude 
    global Load_Resistance 

    global Inductor_Inductance_Per_Length 
    global Inductor_Capacitance_Per_Length 
    global Inductor_Length 

    global Capacitor_Inductance_Per_Length 
    global Capacitor_Capacitance_Per_Length 
    global Capacitor_Length 

    global Inductor_Total_Inductance 
    global Inductor_Total_Capacitance 
    global Inductor_Velocity 
    global Inductor_Time 
    global Inductor_Impedance 

    global Capacitor_Total_Inductance 
    global Capacitor_Total_Capacitance 
    global Capacitor_Velocity 
    global Capacitor_Time 
    global Capacitor_Impedance 

    global Load_Parallel_Inductor 
    global Load_Parallel_Capacitor 

    global Inductor_Solver_Term_VL  
    global Inductor_Solver_Term_VC  
    global Inductor_Solver_Term_IL  
    global Inductor_Solver_Term_IC  
    global Inductor_Solver_Term_VS  

    global Inductor_Solver_Term_VL_I  
    global Inductor_Solver_Term_VC_I  
    global Inductor_Solver_Term_IL_I  
    global Inductor_Solver_Term_IC_I  
    global Inductor_Solver_Term_VS_I  

    global Capacitor_Solver_Term_VC  
    global Capacitor_Solver_Term_VL  
    global Capacitor_Solver_Term_IC  
    global Capacitor_Solver_Term_IL  
    global Capacitor_Solver_Term_VS  

    global Capacitor_Solver_Term_VC_I  
    global Capacitor_Solver_Term_VL_I  
    global Capacitor_Solver_Term_IC_I  
    global Capacitor_Solver_Term_IL_I  
    global Capacitor_Solver_Term_VS_I  
    
    global Initial_Inductor_Voltage
    global Initial_Inductor_Current
    global Initial_Capacitor_Voltage
    global Initial_Capacitor_Current
    
    global GCD
    global LCM
    global Capacitor_LCM_Factor
    global Inductor_LCM_Factor
    global is_Higher_Merging
    global a 
    global b
    
    global Number_of_Wavefronts
    global Number_of_Layers
    

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
               
        
def Circuit_Solver_Inductor_Voltage(VL,IL,VC,IC):
    return -VL * Inductor_Solver_Term_VL - VC * Inductor_Solver_Term_VC - IL * Inductor_Solver_Term_IL + IC * Inductor_Solver_Term_IC 

def Circuit_Solver_Inductor_Current(VL,IL,VC,IC):
    return -VL * Inductor_Solver_Term_VL_I - VC * Inductor_Solver_Term_VC_I - IL * Inductor_Solver_Term_IL_I + IC * Inductor_Solver_Term_IC_I 

def Circuit_Solver_Inductor_Source_Voltage(VS):
    return VS * Inductor_Solver_Term_VS

def Circuit_Solver_Inductor_Source_Current(VS):
    return VS * Inductor_Solver_Term_VS_I

def Circuit_Solver_Capacitor_Voltage(VL,IL,VC,IC):
    return -VC * Capacitor_Solver_Term_VC - VL * Capacitor_Solver_Term_VL - IC * Capacitor_Solver_Term_IC + IL * Capacitor_Solver_Term_IL 

def Circuit_Solver_Capacitor_Current(VL,IL,VC,IC):
    return -VC * Capacitor_Solver_Term_VC_I - VL * Capacitor_Solver_Term_VL_I - IC * Capacitor_Solver_Term_IC_I + IL * Capacitor_Solver_Term_IL_I 

def Circuit_Solver_Capacitor_Source_Voltage(VS):
    return VS * Capacitor_Solver_Term_VS

def Circuit_Solver_Capacitor_Source_Current(VS):
    return VS * Capacitor_Solver_Term_VS_I


def About_Network():
    print(f"\nInformation about this network : \n")


    print(f"\n- The Inductor -")
    print(f"{'Inductor Inductance Per Length :':<40}{Inductor_Inductance_Per_Length}")
    print(f"{'Inductor Capacitance Per Length :':<40}{Inductor_Capacitance_Per_Length}")
    print(f"{'Inductor Length :':<40}{Inductor_Length}")
    print(f"{'Inductor Total Inductance :':<40}{Inductor_Total_Inductance}")
    print(f"{'Inductor Total Capacitance :':<40}{Inductor_Total_Capacitance}")
    print(f"{'Inductor Velocity :':<40}{Inductor_Velocity}")
    print(f"{'Inductor Time Delay :':<40}{Inductor_Time}")
    print(f"{'Inductor Impedance :':<40}{Inductor_Impedance}")
    

    print(f"\n- The Capacitor -")
    print(f"{'Capacitor Inductance Per Length :':<40}{Capacitor_Inductance_Per_Length}")
    print(f"{'Capacitor Capacitance Per Length :':<40}{Capacitor_Capacitance_Per_Length}")
    print(f"{'Capacitor Length :':<40}{Capacitor_Length}")
    print(f"{'Capacitor Total Inductance :':<40}{Capacitor_Total_Inductance}")
    print(f"{'Capacitor Total Capacitance :':<40}{Capacitor_Total_Capacitance}")
    print(f"{'Capacitor Velocity :':<40}{Capacitor_Velocity}")
    print(f"{'Capacitor Time Delay :':<40}{Capacitor_Time}")
    print(f"{'Capacitor Impedance :':<40}{Capacitor_Impedance}")
    
    print(f"\n- The Time -")
    print(f"{'Number Periods :':<40}{Number_Periods}")
    print(f"{'Simulation Stop Time :':<40}{Simulation_Stop_Time}")
    print(f"{'Number of Wavefronts :':<40}{Number_of_Wavefronts}")
    print(f"{'Number of Layers :':<40}{Number_of_Layers}")
    print(f"{'A :':<40}{Inductor_Time}")
    print(f"{'B :':<40}{Capacitor_Time}")
    print(f"{'a :':<40}{Inductor_LCM_Factor}")
    print(f"{'b :':<40}{Capacitor_LCM_Factor}")
    print(f"{'LCM :':<40}{LCM}")
    print(f"{'GCD :':<40}{GCD}")
    print(f"{'Higher Merging? :':<40}{is_Higher_Merging}")
    

    print(f"\n- The Circuit -")
    print(f"{'Votage Source Magnitude :':<40}{Voltage_Souce_Magnitude}")
    print(f"{'Buck Converter :':<40}{Is_Buck}")
    print(f"{'Load Resistance :':<40}{Load_Resistance}")


def Process_Wavefronts(Inductor_List, Capacitor_List, Circuit_List):

    Calculate_Variables(Inductor_List, Capacitor_List, Circuit_List)
    About_Network()
    
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

        reflections_inductive = Decimal()
        reflections_capacitive = Decimal()
        refelections_current_chain = Decimal()

        transmisions_inductor_to_capacitor = Decimal()
        transmisions_capacitor_to_inductor = Decimal()

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
            print(f"{'Inductive Reflections :':<35}{self.reflections_inductive}")
            print(f"{'Capacitive Reflections :':<35}{self.reflections_capacitive}")
            print(f"{'Current Chain Reflections :':<35}{self.refelections_current_chain}")
            print(f"{'Transmission Ind -> Cap :':<35}{self.transmisions_inductor_to_capacitor}")
            print(f"{'Transmission Cap -> Ind :':<35}{self.transmisions_capacitor_to_inductor}")
        
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

            self.reflections_capacitive = 0
            self.reflections_inductive = 0
            self.refelections_current_chain = 0

            self.transmisions_inductor_to_capacitor = 0
            self.transmisions_capacitor_to_inductor = 0

        def Generate(self, Wavefront_Storage : list):
            Wavefront_Storage.append(Wavefront_Inductive(self,False))
            Wavefront_Storage.append(Wavefront_Capacitive(self,False))
            
    class Wavefront_Capacitive( Wavefront ):

        def __init__(self, Wavefront_Parent : Wavefront, is_reflection : bool, reflections_current_chain = 0):
            
            self.velocity = Capacitor_Velocity
            self.length = Capacitor_Length

            self.position_start = Wavefront_Parent.position_end

            self.time_start = Wavefront_Parent.time_end
            self.time_end = self.time_start + Capacitor_Time

            if self.position_start == 0:

                self.position_end = Capacitor_Length

                if is_reflection: # A reflected wave at source side   |<--

                    self.magnitude_voltage = Circuit_Solver_Capacitor_Voltage(0, 0, Wavefront_Parent.magnitude_voltage, Wavefront_Parent.magnitude_current)
                    self.magnitude_current = Circuit_Solver_Capacitor_Current(0, 0, Wavefront_Parent.magnitude_voltage, Wavefront_Parent.magnitude_current)

                    self.reflections_inductive = Wavefront_Parent.reflections_inductive
                    self.reflections_capacitive = Wavefront_Parent.reflections_capacitive + 1

                    self.transmisions_inductor_to_capacitor = Wavefront_Parent.transmisions_inductor_to_capacitor
                    self.transmisions_capacitor_to_inductor = Wavefront_Parent.transmisions_capacitor_to_inductor

                elif isinstance(Wavefront_Parent, Wavefront_Source) : # A generate source wave (Vs)-|->

                    self.time_start = Wavefront_Parent.time_start
                    self.time_end = self.time_start + Capacitor_Time

                    self.magnitude_voltage = Circuit_Solver_Capacitor_Source_Voltage(Wavefront_Parent.magnitude_voltage)
                    self.magnitude_current = Circuit_Solver_Capacitor_Source_Current(Wavefront_Parent.magnitude_voltage)

                    self.reflections_inductive = Wavefront_Parent.reflections_inductive
                    self.reflections_capacitive = Wavefront_Parent.reflections_capacitive 

                    self.transmisions_inductor_to_capacitor = Wavefront_Parent.transmisions_inductor_to_capacitor
                    self.transmisions_capacitor_to_inductor = Wavefront_Parent.transmisions_capacitor_to_inductor

                else: # A transmitted wave at source side  -|->

                    self.magnitude_voltage = Circuit_Solver_Capacitor_Voltage(Wavefront_Parent.magnitude_voltage, Wavefront_Parent.magnitude_current, 0, 0)
                    self.magnitude_current = Circuit_Solver_Capacitor_Current(Wavefront_Parent.magnitude_voltage, Wavefront_Parent.magnitude_current, 0, 0)

                    self.reflections_inductive = Wavefront_Parent.reflections_inductive
                    self.reflections_capacitive = Wavefront_Parent.reflections_capacitive 

                    self.transmisions_inductor_to_capacitor = Wavefront_Parent.transmisions_inductor_to_capacitor + 1
                    self.transmisions_capacitor_to_inductor = Wavefront_Parent.transmisions_capacitor_to_inductor

            else: # A reflected wave at load side   -->|

                self.position_end = 0

                self.magnitude_voltage = Wavefront_Parent.magnitude_voltage
                self.magnitude_current = - Wavefront_Parent.magnitude_current

                self.reflections_inductive = Wavefront_Parent.reflections_inductive
                self.reflections_capacitive = Wavefront_Parent.reflections_capacitive + 1

                self.transmisions_inductor_to_capacitor = Wavefront_Parent.transmisions_inductor_to_capacitor
                self.transmisions_capacitor_to_inductor = Wavefront_Parent.transmisions_capacitor_to_inductor

            self.excitation_event_type = Wavefront_Parent.excitation_event_type
            self.excitation_event_number = Wavefront_Parent.excitation_event_number

            self.refelections_current_chain = reflections_current_chain

        def Generate(self, Wavefront_Storage):
            if self.position_end == 0:
                Wavefront_Storage.append(Wavefront_Inductive(self,False))
                Wavefront_Storage.append(Wavefront_Capacitive(self,True))
            else:
                Wavefront_Storage.append(Wavefront_Capacitive(self,True,self.refelections_current_chain+1))
        
        def Generate_Return(self):
            if self.position_end == 0:
                return Wavefront_Inductive(self,False), Wavefront_Capacitive(self,True)
            else :
                return Wavefront_Capacitive(self,True,self.refelections_current_chain+1)

        def Merge(self, Wavefront_Other : Wavefront):
            self.magnitude_voltage = self.magnitude_voltage + Wavefront_Other.magnitude_voltage
            self.magnitude_current = self.magnitude_current + Wavefront_Other.magnitude_current

    class Wavefront_Inductive( Wavefront ):

        def __init__(self, Wavefront_Parent : Wavefront, is_reflection : bool, reflections_current_chain = 0):
            
            self.velocity = Inductor_Velocity
            self.length = Inductor_Length

            self.position_start = Wavefront_Parent.position_end

            self.time_start = Wavefront_Parent.time_end
            self.time_end = self.time_start + Inductor_Time

            if self.position_start == 0:

                self.position_end = Inductor_Length

                if is_reflection: # A reflected wave at source side   |<--

                    self.magnitude_voltage = Circuit_Solver_Inductor_Voltage( Wavefront_Parent.magnitude_voltage, Wavefront_Parent.magnitude_current, 0, 0)
                    self.magnitude_current = Circuit_Solver_Inductor_Current( Wavefront_Parent.magnitude_voltage, Wavefront_Parent.magnitude_current, 0, 0)

                    self.reflections_inductive = Wavefront_Parent.reflections_inductive + 1
                    self.reflections_capacitive = Wavefront_Parent.reflections_capacitive 

                    self.transmisions_inductor_to_capacitor = Wavefront_Parent.transmisions_inductor_to_capacitor
                    self.transmisions_capacitor_to_inductor = Wavefront_Parent.transmisions_capacitor_to_inductor

                elif isinstance(Wavefront_Parent, Wavefront_Source) : # A generate source wave (Vs)-|->

                    self.time_start = Wavefront_Parent.time_start
                    self.time_end = self.time_start + Inductor_Time

                    self.magnitude_voltage = Circuit_Solver_Inductor_Source_Voltage(Wavefront_Parent.magnitude_voltage)
                    self.magnitude_current = Circuit_Solver_Inductor_Source_Current(Wavefront_Parent.magnitude_voltage)

                    self.reflections_inductive = Wavefront_Parent.reflections_inductive
                    self.reflections_capacitive = Wavefront_Parent.reflections_capacitive 

                    self.transmisions_inductor_to_capacitor = Wavefront_Parent.transmisions_inductor_to_capacitor
                    self.transmisions_capacitor_to_inductor = Wavefront_Parent.transmisions_capacitor_to_inductor
                    
                else: # A transmitted wave at source side  -|->

                    self.magnitude_voltage = Circuit_Solver_Inductor_Voltage(0, 0, Wavefront_Parent.magnitude_voltage, Wavefront_Parent.magnitude_current)
                    self.magnitude_current = Circuit_Solver_Inductor_Current(0, 0, Wavefront_Parent.magnitude_voltage, Wavefront_Parent.magnitude_current)

                    self.reflections_inductive = Wavefront_Parent.reflections_inductive
                    self.reflections_capacitive = Wavefront_Parent.reflections_capacitive 

                    self.transmisions_inductor_to_capacitor = Wavefront_Parent.transmisions_inductor_to_capacitor 
                    self.transmisions_capacitor_to_inductor = Wavefront_Parent.transmisions_capacitor_to_inductor +1

            else: # A reflected wave at load side   -->|
                
                self.position_end = 0

                self.magnitude_voltage = - Wavefront_Parent.magnitude_voltage
                self.magnitude_current = Wavefront_Parent.magnitude_current

                self.reflections_inductive = Wavefront_Parent.reflections_inductive +1
                self.reflections_capacitive = Wavefront_Parent.reflections_capacitive 

                self.transmisions_inductor_to_capacitor = Wavefront_Parent.transmisions_inductor_to_capacitor
                self.transmisions_capacitor_to_inductor = Wavefront_Parent.transmisions_capacitor_to_inductor

            self.excitation_event_type = Wavefront_Parent.excitation_event_type
            self.excitation_event_number = Wavefront_Parent.excitation_event_number

            self.refelections_current_chain = reflections_current_chain

        def Generate(self, Wavefront_Storage):
            if self.position_end == 0:
                Wavefront_Storage.append(Wavefront_Inductive(self,True))
                Wavefront_Storage.append(Wavefront_Capacitive(self,False))
            else :
                Wavefront_Storage.append(Wavefront_Inductive(self,True,self.refelections_current_chain+1))

        def Generate_Return(self):
            if self.position_end == 0:
                return Wavefront_Inductive(self,True), Wavefront_Capacitive(self,False)
            else :
                return Wavefront_Inductive(self,True,self.refelections_current_chain+1)

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
    
    Cartesian_Voltage_Away = np.full((2*(Number_of_Layers+1),2*(Number_of_Layers+1)),Decimal('0'))
    Cartesian_Voltage_Return = np.full((2*(Number_of_Layers+1),2*(Number_of_Layers+1)),Decimal('0'))
    
    Cartesian_Current_Away = np.full((2*(Number_of_Layers+1),2*(Number_of_Layers+1)),Decimal('0'))
    Cartesian_Current_Return = np.full((2*(Number_of_Layers+1),2*(Number_of_Layers+1)),Decimal('0'))
    
    Cartesian_Time = np.full((2*(Number_of_Layers+1),2*(Number_of_Layers+1)),Decimal('0'))
    
    Voltage_Accumulation_Inductor = np.full((2*(Number_of_Layers+1),2*(Number_of_Layers+1)),Decimal('0'))
    Current_Accumulation_Inductor = np.full((2*(Number_of_Layers+1),2*(Number_of_Layers+1)),Decimal('0'))

    Voltage_Accumulation_Capacitor = np.full((2*(Number_of_Layers+1),2*(Number_of_Layers+1)),Decimal('0'))
    Current_Accumulation_Capacitor = np.full((2*(Number_of_Layers+1),2*(Number_of_Layers+1)),Decimal('0'))
    
    ## LAYER 0
    # Generate Intial Away Waves
    Storage_Voltage_Active.append(Wavefront_Source(Voltage_Souce_Magnitude,0,0,0))
    temp_wavefront = Storage_Voltage_Active.popleft()
    
    temp_wavefront.Generate(Storage_Away)
    Storage_Voltage_Completed.append(temp_wavefront)
    
    # Generate Intial Return Waves, Store Away Waves
    # Get First Sending Intial Inductive wavefront
    temp_wavefront_inductive = Storage_Away.popleft()
    temp_wavefront_inductive.Generate(Storage_Return)
    Storage_Inductor_Completed.append(temp_wavefront_inductive)
    Cartesian_Voltage_Away[1,0] = temp_wavefront_inductive.magnitude_voltage
    Cartesian_Current_Away[1,0] = temp_wavefront_inductive.magnitude_current 
    Cartesian_Time[1-1,0] = temp_wavefront_inductive.time_start
    
    # Get Next Sending Initial Capacitive wavefront
    temp_wavefront_capacitive = Storage_Away.popleft()
    temp_wavefront_capacitive.Generate(Storage_Return)
    Storage_Capacitor_Completed.append(temp_wavefront_capacitive)
    Cartesian_Voltage_Away[0,1] = temp_wavefront_capacitive.magnitude_voltage
    Cartesian_Current_Away[0,1] = temp_wavefront_capacitive.magnitude_current 

    # Merge_Algorithm
    for layer_number in range(1,Number_of_Layers):

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
        Cartesian_Voltage_Return[Cartesian_Index_x,Cartesian_Index_y] = temp_wavefront.magnitude_voltage
        Cartesian_Current_Return[Cartesian_Index_x,Cartesian_Index_y] = temp_wavefront.magnitude_current 
        Cartesian_Index_x = Cartesian_Index_x - 1
        Cartesian_Index_y = Cartesian_Index_y + 1
        
        while len(Storage_Return) > 0:
            
            # Get a Returning wavefront (will be capacitve)
            temp_wavefront = Storage_Return.popleft()
            
            if len(Storage_Return) == 0 : # It is the last wave
                temp_wavefront.Generate(Storage_Away)
                Storage_Capacitor_Completed.append(temp_wavefront)
                Cartesian_Voltage_Return[Cartesian_Index_x,Cartesian_Index_y] = temp_wavefront.magnitude_voltage
                Cartesian_Current_Return[Cartesian_Index_x,Cartesian_Index_y] = temp_wavefront.magnitude_current 
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
                Cartesian_Voltage_Return[Cartesian_Index_x,Cartesian_Index_y] = temp_wavefront.magnitude_voltage
                Cartesian_Current_Return[Cartesian_Index_x,Cartesian_Index_y] = temp_wavefront.magnitude_current
                Cartesian_Index_x = Cartesian_Index_x - 1
                Cartesian_Index_y = Cartesian_Index_y + 1
                
                Storage_Inductor_Completed.append(temp_next_wavefront)
                Cartesian_Voltage_Return[Cartesian_Index_x,Cartesian_Index_y] = temp_next_wavefront.magnitude_voltage
                Cartesian_Current_Return[Cartesian_Index_x,Cartesian_Index_y] = temp_next_wavefront.magnitude_current 
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
            Cartesian_Voltage_Away[Cartesian_Index_x, Cartesian_Index_y] = temp_wavefront_inductive.magnitude_voltage
            Cartesian_Current_Away[Cartesian_Index_x, Cartesian_Index_y] = temp_wavefront_inductive.magnitude_current 
            Cartesian_Time[Cartesian_Index_x-1,Cartesian_Index_y] = temp_wavefront_inductive.time_start
            Cartesian_Index_x = Cartesian_Index_x - 1
            Cartesian_Index_y = Cartesian_Index_y + 1
            
            # Get the next Away wavefront (will be capacitive)
            temp_wavefront_capacitve = Storage_Away.popleft()
            temp_wavefront_capacitve.Generate(Storage_Return)
            Storage_Capacitor_Completed.append(temp_wavefront_capacitve)
            Cartesian_Voltage_Away[Cartesian_Index_x, Cartesian_Index_y] = temp_wavefront_capacitve.magnitude_voltage
            Cartesian_Current_Away[Cartesian_Index_x, Cartesian_Index_y] = temp_wavefront_capacitve.magnitude_current 
            Cartesian_Index_x = Cartesian_Index_x - 1
            Cartesian_Index_y = Cartesian_Index_y + 1

    # Accumulation_Arrays
    for layer_number in range(0,Number_of_Layers):
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

                if(node_number == 0 and layer_number ==0): 
                        # Origin Node
                        # Inductor, Origin node = Away only
                        Voltage_Accumulation_Inductor[Centre_Index_x,Centre_Index_y] = Cartesian_Voltage_Away[Away_Index_Inductor_x,Away_Index_Inductor_y] 
                        Current_Accumulation_Inductor[Centre_Index_x,Centre_Index_y] = Cartesian_Current_Away[Away_Index_Inductor_x,Away_Index_Inductor_y] 
                        
                        # Capacitor, Origin node = Away only
                        Voltage_Accumulation_Capacitor[Centre_Index_x,Centre_Index_y] = Cartesian_Voltage_Away[Away_Index_Capacitor_x,Away_Index_Capacitor_y] 
                        Current_Accumulation_Capacitor[Centre_Index_x,Centre_Index_y] = Cartesian_Current_Away[Away_Index_Capacitor_x,Away_Index_Capacitor_y] 

                elif(node_number == 0 ): 
                        # First Node
                        # Inductor, First Node = Both Merging 
                        Voltage_Accumulation_Inductor[Centre_Index_x,Centre_Index_y] = (Cartesian_Voltage_Away[Away_Index_Inductor_x,Away_Index_Inductor_y] + Cartesian_Voltage_Return[Return_Index_Inductor_x,Return_Index_Inductor_y]) 
                        Current_Accumulation_Inductor[Centre_Index_x,Centre_Index_y] = (Cartesian_Current_Away[Away_Index_Inductor_x,Away_Index_Inductor_y] + Cartesian_Current_Return[Return_Index_Inductor_x,Return_Index_Inductor_y]) 
                        
                        # Capacitor, First Node = Away only
                        Voltage_Accumulation_Capacitor[Centre_Index_x,Centre_Index_y] = Cartesian_Voltage_Away[Away_Index_Capacitor_x,Away_Index_Capacitor_y] 
                        Current_Accumulation_Capacitor[Centre_Index_x,Centre_Index_y] = Cartesian_Current_Away[Away_Index_Capacitor_x,Away_Index_Capacitor_y]

                elif(node_number == layer_number): 
                        # Last Node
                        # Inductor, Last Node = Away only
                        Voltage_Accumulation_Inductor[Centre_Index_x,Centre_Index_y] = Cartesian_Voltage_Away[Away_Index_Inductor_x,Away_Index_Inductor_y] 
                        Current_Accumulation_Inductor[Centre_Index_x,Centre_Index_y] = Cartesian_Current_Away[Away_Index_Inductor_x,Away_Index_Inductor_y]
                        
                        # Capacitor, Last Node = Both Merging
                        Voltage_Accumulation_Capacitor[Centre_Index_x,Centre_Index_y] = (Cartesian_Voltage_Away[Away_Index_Capacitor_x,Away_Index_Capacitor_y] + Cartesian_Voltage_Return[Return_Index_Capacitor_x,Return_Index_Capacitor_y]) 
                        Current_Accumulation_Capacitor[Centre_Index_x,Centre_Index_y] = (Cartesian_Current_Away[Away_Index_Capacitor_x,Away_Index_Capacitor_y] + Cartesian_Current_Return[Return_Index_Capacitor_x,Return_Index_Capacitor_y])
                else:
                        # General Node
                        # Inductor, General Node = Both merging
                        Voltage_Accumulation_Inductor[Centre_Index_x,Centre_Index_y] = (Cartesian_Voltage_Away[Away_Index_Inductor_x,Away_Index_Inductor_y] + Cartesian_Voltage_Return[Return_Index_Inductor_x,Return_Index_Inductor_y]) 
                        Current_Accumulation_Inductor[Centre_Index_x,Centre_Index_y] = (Cartesian_Current_Away[Away_Index_Inductor_x,Away_Index_Inductor_y] + Cartesian_Current_Return[Return_Index_Inductor_x,Return_Index_Inductor_y]) 
                        
                        # Capacitor, General Node = Both merging
                        Voltage_Accumulation_Capacitor[Centre_Index_x,Centre_Index_y] = (Cartesian_Voltage_Away[Away_Index_Capacitor_x,Away_Index_Capacitor_y] + Cartesian_Voltage_Return[Return_Index_Capacitor_x,Return_Index_Capacitor_y])
                        Current_Accumulation_Capacitor[Centre_Index_x,Centre_Index_y] = (Cartesian_Current_Away[Away_Index_Capacitor_x,Away_Index_Capacitor_y] + Cartesian_Current_Return[Return_Index_Capacitor_x,Return_Index_Capacitor_y])
                        
                Centre_Index_x -= 2
                Centre_Index_y += 2
                
    Voltage_Accumulation_Inductor = delete_alternating(Voltage_Accumulation_Inductor)
    Current_Accumulation_Inductor = delete_alternating(Current_Accumulation_Inductor)

    Voltage_Accumulation_Capacitor = delete_alternating(Voltage_Accumulation_Capacitor)
    Current_Accumulation_Capacitor = delete_alternating(Current_Accumulation_Capacitor)
    
    return (
        Storage_Inductor_Completed, 
        Storage_Capacitor_Completed,
        Voltage_Accumulation_Inductor,
        Current_Accumulation_Inductor,
        Voltage_Accumulation_Capacitor,
        Current_Accumulation_Capacitor,
        delete_alternating(Cartesian_Time)
    )
