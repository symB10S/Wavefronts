from email.policy import default
from Circuit_Solver import *

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

