from decimal import *
from collections import deque

getcontext().traps[FloatOperation] = True

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
    

    # INDUCTOR
    Inductor_Inductance_Per_Length =  Decimal(Inductor_List[0])
    Inductor_Capacitance_Per_Length =  Decimal(Inductor_List[1])#C
    Inductor_Length = Decimal(Inductor_List[2])

    # CAPACITOR
    Capacitor_Inductance_Per_Length =  Decimal(Capacitor_List[0])
    Capacitor_Capacitance_Per_Length =  Decimal(Capacitor_List[1])#C
    Capacitor_Length = Decimal(Capacitor_List[2])

    # CIRCUIT
    Voltage_Souce_Magnitude = Decimal(Circuit_List[0])
    Number_Periods = Decimal(Circuit_List[1])
    Is_Buck = Circuit_List[2]
    Load_Resistance = Decimal(Circuit_List[3])

    ## Calculations
    # Inductor
    Inductor_Total_Inductance = Inductor_Inductance_Per_Length * Inductor_Length
    Inductor_Total_Capacitance = Inductor_Capacitance_Per_Length * Inductor_Length
    Inductor_Velocity = 1/Decimal.sqrt(Inductor_Inductance_Per_Length * Inductor_Capacitance_Per_Length)
    Inductor_Time = Inductor_Length / Inductor_Velocity
    Inductor_Impedance = Decimal.sqrt(Inductor_Inductance_Per_Length/Inductor_Capacitance_Per_Length)

    # Capacitor
    Capacitor_Total_Inductance = Capacitor_Inductance_Per_Length * Capacitor_Length
    Capacitor_Total_Capacitance = Capacitor_Capacitance_Per_Length * Capacitor_Length
    Capacitor_Velocity = 1/Decimal.sqrt(Capacitor_Inductance_Per_Length * Capacitor_Capacitance_Per_Length)
    Capacitor_Time = Capacitor_Length / Capacitor_Velocity
    Capacitor_Impedance = Decimal.sqrt(Capacitor_Inductance_Per_Length/Capacitor_Capacitance_Per_Length)

    Simulation_Stop_Time = Number_Periods*Decimal('6.28318530718')*(Decimal.sqrt(Capacitor_Total_Capacitance*Inductor_Total_Inductance))

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

    print(f"\n- The Circuit -")
    print(f"{'Votage Source Magnitude :':<40}{Voltage_Souce_Magnitude}")
    print(f"{'Number Periods :':<40}{Number_Periods}")
    print(f"{'Simulation Stop Time :':<40}{Simulation_Stop_Time}")
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

        order = Decimal()

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
            print(f"{'Order :':<35}{self.order}")
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

            self.order = 0

            self.reflections_capacitive = 0
            self.reflections_inductive = 0
            self.refelections_current_chain = 0

            self.transmisions_inductor_to_capacitor = 0
            self.transmisions_capacitor_to_inductor = 0

        def Generate(self, Wavefront_Storage_Inductor : list, Wavefront_Storage_Capacitor : list):
            Wavefront_Storage_Inductor.append(Wavefront_Inductive(self,False))
            Wavefront_Storage_Capacitor.append(Wavefront_Capacitive(self,False))
            
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

                    self.order = Wavefront_Parent.order 

                elif isinstance(Wavefront_Parent, Wavefront_Source) : # A generate source wave (Vs)-|->

                    self.time_start = Wavefront_Parent.time_start
                    self.time_end = self.time_start + Capacitor_Time

                    self.magnitude_voltage = Circuit_Solver_Capacitor_Source_Voltage(Wavefront_Parent.magnitude_voltage)
                    self.magnitude_current = Circuit_Solver_Capacitor_Source_Current(Wavefront_Parent.magnitude_voltage)

                    self.reflections_inductive = Wavefront_Parent.reflections_inductive
                    self.reflections_capacitive = Wavefront_Parent.reflections_capacitive 

                    self.transmisions_inductor_to_capacitor = Wavefront_Parent.transmisions_inductor_to_capacitor
                    self.transmisions_capacitor_to_inductor = Wavefront_Parent.transmisions_capacitor_to_inductor

                    self.order = Wavefront_Parent.order 

                else: # A transmitted wave at source side  -|->

                    self.magnitude_voltage = Circuit_Solver_Capacitor_Voltage(Wavefront_Parent.magnitude_voltage, Wavefront_Parent.magnitude_current, 0, 0)
                    self.magnitude_current = Circuit_Solver_Capacitor_Current(Wavefront_Parent.magnitude_voltage, Wavefront_Parent.magnitude_current, 0, 0)

                    self.reflections_inductive = Wavefront_Parent.reflections_inductive
                    self.reflections_capacitive = Wavefront_Parent.reflections_capacitive 

                    self.transmisions_inductor_to_capacitor = Wavefront_Parent.transmisions_inductor_to_capacitor + 1
                    self.transmisions_capacitor_to_inductor = Wavefront_Parent.transmisions_capacitor_to_inductor

                    self.order = Wavefront_Parent.order + 1

            else: # A reflected wave at load side   -->|

                self.position_end = 0

                self.magnitude_voltage = Wavefront_Parent.magnitude_voltage
                self.magnitude_current = - Wavefront_Parent.magnitude_current

                self.reflections_inductive = Wavefront_Parent.reflections_inductive
                self.reflections_capacitive = Wavefront_Parent.reflections_capacitive + 1

                self.transmisions_inductor_to_capacitor = Wavefront_Parent.transmisions_inductor_to_capacitor
                self.transmisions_capacitor_to_inductor = Wavefront_Parent.transmisions_capacitor_to_inductor

                self.order = Wavefront_Parent.order 

            self.excitation_event_type = Wavefront_Parent.excitation_event_type
            self.excitation_event_number = Wavefront_Parent.excitation_event_number

            self.refelections_current_chain = reflections_current_chain

        def Generate(self, Wavefront_Storage_Inductor : list, Wavefront_Storage_Capacitor : list):
            if self.position_end == 0:
                Wavefront_Storage_Inductor.append(Wavefront_Inductive(self,False))
                Wavefront_Storage_Capacitor.append(Wavefront_Capacitive(self,True))
            else:
                Wavefront_Storage_Capacitor.append(Wavefront_Capacitive(self,True,self.refelections_current_chain+1))
        
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

                    self.order = Wavefront_Parent.order 

                elif isinstance(Wavefront_Parent, Wavefront_Source) : # A generate source wave (Vs)-|->

                    self.time_start = Wavefront_Parent.time_start
                    self.time_end = self.time_start + Inductor_Time

                    self.magnitude_voltage = Circuit_Solver_Inductor_Source_Voltage(Wavefront_Parent.magnitude_voltage)
                    self.magnitude_current = Circuit_Solver_Inductor_Source_Current(Wavefront_Parent.magnitude_voltage)

                    self.reflections_inductive = Wavefront_Parent.reflections_inductive
                    self.reflections_capacitive = Wavefront_Parent.reflections_capacitive 

                    self.transmisions_inductor_to_capacitor = Wavefront_Parent.transmisions_inductor_to_capacitor
                    self.transmisions_capacitor_to_inductor = Wavefront_Parent.transmisions_capacitor_to_inductor

                    self.order = Wavefront_Parent.order 

                else: # A transmitted wave at source side  -|->

                    self.magnitude_voltage = Circuit_Solver_Inductor_Voltage(0, 0, Wavefront_Parent.magnitude_voltage, Wavefront_Parent.magnitude_current)
                    self.magnitude_current = Circuit_Solver_Inductor_Current(0, 0, Wavefront_Parent.magnitude_voltage, Wavefront_Parent.magnitude_current)

                    self.reflections_inductive = Wavefront_Parent.reflections_inductive
                    self.reflections_capacitive = Wavefront_Parent.reflections_capacitive 

                    self.transmisions_inductor_to_capacitor = Wavefront_Parent.transmisions_inductor_to_capacitor 
                    self.transmisions_capacitor_to_inductor = Wavefront_Parent.transmisions_capacitor_to_inductor +1

                    self.order = Wavefront_Parent.order + 1

            else: # A reflected wave at load side   -->|
                
                self.position_end = 0

                self.magnitude_voltage = - Wavefront_Parent.magnitude_voltage
                self.magnitude_current = Wavefront_Parent.magnitude_current

                self.reflections_inductive = Wavefront_Parent.reflections_inductive +1
                self.reflections_capacitive = Wavefront_Parent.reflections_capacitive 

                self.transmisions_inductor_to_capacitor = Wavefront_Parent.transmisions_inductor_to_capacitor
                self.transmisions_capacitor_to_inductor = Wavefront_Parent.transmisions_capacitor_to_inductor

                self.order = Wavefront_Parent.order 

            self.excitation_event_type = Wavefront_Parent.excitation_event_type
            self.excitation_event_number = Wavefront_Parent.excitation_event_number

            self.refelections_current_chain = reflections_current_chain

        def Generate(self, Wavefront_Storage_Inductor : list, Wavefront_Storage_Capacitor : list):
            if self.position_end == 0:
                Wavefront_Storage_Inductor.append(Wavefront_Inductive(self,True))
                Wavefront_Storage_Capacitor.append(Wavefront_Capacitive(self,False))
            else :
                Wavefront_Storage_Inductor.append(Wavefront_Inductive(self,True,self.refelections_current_chain+1))

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

    # Initiation
    Storage_Voltage_Active.append(Wavefront_Source(Voltage_Souce_Magnitude,0,0,0))

    temp_wavefront = Storage_Voltage_Active.popleft()
    temp_wavefront.Generate(Storage_Away,Storage_Away)
    Storage_Voltage_Completed.append(temp_wavefront)

    # Merge_Algorithm
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

    return Storage_Inductor_Completed, Storage_Capacitor_Completed
