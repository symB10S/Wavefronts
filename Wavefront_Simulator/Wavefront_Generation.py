from decimal import *
from collections import deque
import numpy as np
import math
import copy
import warnings
from dataclasses import dataclass

getcontext().traps[FloatOperation] = True

#: The default values used in the simulation if not specified otherwise
default_input_values : dict = dict ([
    ('L_impedance','100'),('L_time' ,'1'),('L_length','1'),
    ('C_impedance','1'),  ('C_time' ,'1'),('C_length','1'),
    ('V_source','1'),('number_periods','1'),('Load_impedance','inf'),
    ('Simulation_stop_time','0'),('show_about',True)
])

def handle_default_kwargs(input_kwargs: dict,default_kwargs: dict):
    """handles default values for key-word arguments, changes defaults to given value.

    :param input_kwargs: kwargs given by user.
    :type input_kwargs: dict
    :param default_kwargs: default values that kwargs must be one of.
    :type default_kwargs: dict
    :raises Exception: ValueError if a kwarg is provided that is not one of the default values.
    :return: returns a modfied version of the default_kwargs that includes input changes
    :rtype: dict
    """
    #Set Kwargs
    for key, item in input_kwargs.items():
        if(default_kwargs.get(key) is None):
            raise ValueError(f"No setting found for {key}, here are the possible options: \n{default_kwargs}")
        else:
            default_kwargs[key] = item
            
    return default_kwargs

class Data_Input_Storage :
    """The storage object for the input varibles of a interface simulation. Calculates all the associated variables required for the simulaitons. 
        Can be used to investigate network calcualted parameters based off input vairbles.  

        Is initialised using key-word arguments. All values with the provided keys are of type string. 
        This each input variable is converterted to a Decimal value to be used for precision calculations.
        The possible parameters to change and their defualt values are as follows, 
        
        :keyword L_impedance: Characteristic impedance of the inductor, assigned to self.Inductor_Impedance (default:'100')
        :type L_impedance: String
        :keyword L_time: The time delay of the inductor in seconds, assigned to self.Inductor_Time (default:'1')
        :type L_time: String
        :keyword L_length: The length of the inductor in meters, assigned to self.Inductor_Length (default:'1')
        :type L_length: String
        :keyword C_impedance: Characteristic impedance of the capacitor, assigned to self.Capacitor_Impedance (default:'1')
        :type C_impedance: String
        :keyword C_time: The time delay of the capacitor in seconds, assigned to self.Capacitor_Time (default:'1')
        :type C_time: String
        :keyword C_length: The length of the capacitor in meters, assigned to self.Capacitor_Length (default:'1')
        :type C_length: String
        :keyword V_source: The magnitude of the initial voltage excitation in volts, assigned to self.Voltage_Souce_Magnitude (default:'1')
        :type V_source: String
        :keyword number_periods: The number of periods as according to Lumped-Element LC-Osscilator solution. 
            Used to calculate the simulation stop time if provided. Overidden if 'Simulation_stop_time' is provided (default:'1')
        :type number_periods: String
        :keyword Load_impedance: The magnitude of the load resistance, if left inf the load is ignored and the interface takes form of an LC-Osscilator.
            If a value is provided the load is considered and the self.Is_Buck flag is set to True (default:'inf')
        :type Load_impedance: String
        :keyword Simulation_stop_time: The time to which the interface will be simulated. If provided it will overwrite the 'number_periods' simulation stop time calculation (default:'0')
        :type Simulation_stop_time: String
        :keyword show_about: Indicates information about the calcualted variabels must be printed (default:True)
        :type show_about: Boolean
        

        
        :**Stored and Calculated Parameters**:
            - **self.Number_Periods** (*Decimal*) - given or calcualted number of periods
            - **self.Simulation_Stop_Time** (*Decimal*) - given or calculated simulation stop time (s)
            - **self.Is_Buck** (*bool*) - if the load across the capacitor is considered or not 
            - **self.GCD** (*Decimal*) - The greatest common denomenator of the capacitor and inductor time delays.
            - **self.LCM** (*Decimal*) - The lowest common multiple of the capacitor and inductor time delays.
            - **self.Capacitor_LCM_Factor** (*int*) - The co-factor of the capacitor time delay required to make the LCM
            - **self.Inductor_LCM_Factor** (*int*) - The co-factor of the inductor time delay required to make the LCM
            - **self.is_Higher_Merging** (*bool*) - Indicates if multiplicative merging will occur for the given simulaiton stop time
            - **self.Number_of_Wavefronts** (*int*) - The total number of sending and returning wavefronts calculated
            - **self.Number_of_Layers** (*int*) - The total number of fanout-layers simulated
            - **self.Voltage_Souce_Magnitude** (*Decimal*) - the magnitude of the voltage excitation (V)
            - **self.Load_Resistance** (*Decimal*) - the magnitude of the load resistor (Ω)
            
        :**Stored Inductor Parameters**:
            - **self.Inductor_Inductance_Per_Length** (*Decimal*) - the per length inductance of the inductor (H/m)
            - **self.Inductor_Capacitance_Per_Length** (*Decimal*) - the per length capacitance of the inductor (F/m)
            - **self.Inductor_Length** (*Decimal*) - the total length of the inductor (m)
            - **self.Inductor_Total_Inductance** (*Decimal*) - the total inductance of the inductor (H)
            - **self.Inductor_Total_Capacitance** (*Decimal*) - the total capacitance of the inductor (F)
            - **self.Inductor_Velocity** (*Decimal*) - the propagation velocity of the inductor (m/s)
            - **self.Inductor_Time** (*Decimal*) - the *one way* transit time of the inductor (s)
            - **self.Inductor_Impedance** (*Decimal*) - the characteristic impedance of the inductor (Ω)
            
        :**Stored Capacitor Parameters**:
            - **self.Capacitor_Inductance_Per_Length** (*Decimal*) - the per length inductance of the capacitor (H/m)
            - **self.Capacitor_Capacitance_Per_Length** (*Decimal*) - the per length capacitance of the capacitor (F/m)
            - **self.Capacitor_Length** (*Decimal*) - the total length of the capacitor (m)
            - **self.Capacitor_Total_Inductance** (*Decimal*) - the total inductance of the capacitor (H)
            - **self.Capacitor_Total_Capacitance** (*Decimal*) - the total capacitance of the capacitor (F)
            - **self.Capacitor_Velocity** (*Decimal*) - the propagation velocity of the capacitor (m/s)
            - **self.Capacitor_Time** (*Decimal*) - the *one way* transit time of the capacitor (s)
            - **self.Capacitor_Impedance** (*Decimal*) - the characteristic impedance of the capacitor (Ω)

        .. code-block:: python
            :caption: Example use of Data_Input_Storage

            data_input = Data_Input_Storage(Simulation_stop_time = '100',L_impedance = '225')
            print(data_input.Simulation_Stop_Time) # prints '100'
            print(data_input.Capacitor_Impedance) # prints '1', assigned by default.
            
            # generate the output wavefronts from the created Data_Input_Storage object:
            data_output = Generate_Wavefronts_Commutatively(data_input)

    """
    def __init__(self,**provided_input_values):
        """Calcualtes the varibles to be stored about the interface based off provided input parameters
        """
        # an input variable dictionary with altered default values were relevant.
        self.input_values = default_input_values.copy()
        self.input_values = handle_default_kwargs(provided_input_values,self.input_values)
        
        # Make input dictionary compatible with SPICE simulation inputs
        self.SPICE_input_values = provided_input_values.copy()
        if(self.SPICE_input_values.get('show_about') is None):
            pass
        else:
            del self.SPICE_input_values['show_about']
        
        # does the converter consider the load, or is it a LC osscilator.
        self.Is_Buck = True
        if self.input_values['Load_impedance'] == 'inf':
            self.Is_Buck = False
        
        # if simulation end time is specified, or is it calculated using "number_periods" input variable.
        self.Custom_stop_time = True
        if self.input_values['Simulation_stop_time'] == '0':
            self.Custom_stop_time = False
        
        # Extracting input variables provided for the inductor
        self.Inductor_Impedance = Decimal(self.input_values['L_impedance'])
        self.Inductor_Time = Decimal(self.input_values['L_time'])/2
        self.Inductor_Length = Decimal(self.input_values['L_length'])
        # Calcualte the variables around the inductor
        self.Inductor_Velocity = self.Inductor_Length/self.Inductor_Time
        self.Inductor_Inductance_Per_Length =  self.Inductor_Time*self.Inductor_Impedance
        self.Inductor_Capacitance_Per_Length =  self.Inductor_Time/self.Inductor_Impedance
        self.Inductor_Total_Inductance = self.Inductor_Inductance_Per_Length * self.Inductor_Length
        self.Inductor_Total_Capacitance = self.Inductor_Capacitance_Per_Length * self.Inductor_Length

        # Extracting input variables provided for the capacitor
        self.Capacitor_Impedance = Decimal(self.input_values['C_impedance'])
        self.Capacitor_Time = Decimal(self.input_values['C_time'])/2
        self.Capacitor_Length = Decimal(self.input_values['C_length'])
        # Calcualte the variables around the capacitor
        self.Capacitor_Velocity = self.Capacitor_Length/self.Capacitor_Time
        self.Capacitor_Inductance_Per_Length =  self.Capacitor_Time*self.Capacitor_Impedance
        self.Capacitor_Capacitance_Per_Length =  self.Capacitor_Time/self.Capacitor_Impedance
        self.Capacitor_Total_Inductance = self.Capacitor_Inductance_Per_Length * self.Capacitor_Length
        self.Capacitor_Total_Capacitance = self.Capacitor_Capacitance_Per_Length * self.Capacitor_Length

        # Extracting input variables provided about the circuit
        self.Voltage_Souce_Magnitude = Decimal(self.input_values['V_source'])
        self.Number_Periods = Decimal(self.input_values['number_periods'])
        self.Load_Impedance = Decimal(self.input_values['Load_impedance'])
        
        # Calculate simulation stop time
        self.Simulation_Stop_Time = Decimal()
        if(self.Custom_stop_time):
            self.Simulation_Stop_Time = Decimal(self.input_values['Simulation_stop_time'])
            self.Number_Periods = self.Simulation_Stop_Time/(Decimal('6.28318530718')*(Decimal.sqrt(self.Capacitor_Total_Capacitance*self.Inductor_Total_Inductance)))
        else:
            self.Simulation_Stop_Time = self.Number_Periods*Decimal('6.28318530718')*(Decimal.sqrt(self.Capacitor_Total_Capacitance*self.Inductor_Total_Inductance))
        
        # Determine the number of layers
        if (self.Capacitor_Time < self.Inductor_Time):
            self.Number_of_Layers = math.ceil(self.Simulation_Stop_Time/(self.Capacitor_Time*2))+1
        else:
            self.Number_of_Layers = math.ceil(self.Simulation_Stop_Time/(self.Inductor_Time*2))+1
        
        # Calculate the number of wavefronts that must be created
        self.Number_of_Wavefronts = 0
        for i in range(0,self.Number_of_Layers+1):
            self.Number_of_Wavefronts = self.Number_of_Wavefronts + 4*i
        
        # Calculate and store multiplicative realtionships between time delays
        Factor_Dict = lcm_gcd_euclid(self.Inductor_Time*2,self.Capacitor_Time*2)
        self.Inductor_LCM_Factor = int(Factor_Dict['KL'])
        self.Capacitor_LCM_Factor = int(Factor_Dict['KC'])
        self.GCD = Factor_Dict['GCD']
        self.LCM = Factor_Dict['LCM']
        
        # Determine if Multiplicative Merging will occur or not
        if(Factor_Dict['LCM'] > self.Simulation_Stop_Time):
            self.is_Higher_Merging = False
        else:
            self.is_Higher_Merging = True
        
        # Generate the associated response co-effcients for changes at the interface.
        if(self.Is_Buck):
            Load_Parallel_Inductor = 1/(1/self.Load_Impedance + 1/self.Inductor_Impedance)
            Load_Parallel_Capacitor = 1/(1/self.Load_Impedance + 1/self.Capacitor_Impedance)

            self.Inductor_Voltage_VL_coeff  = self.Inductor_Impedance/( self.Inductor_Impedance + Load_Parallel_Capacitor )
            self.Inductor_Voltage_VC_coeff  = Load_Parallel_Inductor/( self.Capacitor_Impedance + Load_Parallel_Inductor )
            self.Inductor_Voltage_IL_coeff  = self.Capacitor_Impedance * self.Inductor_Impedance * self.Load_Impedance /(self.Load_Impedance*self.Inductor_Impedance + self.Load_Impedance*self.Capacitor_Impedance + self.Inductor_Impedance * self.Capacitor_Impedance)
            self.Inductor_Voltage_IC_coeff  = self.Inductor_Voltage_IL_coeff
            self.Inductor_Voltage_VS_coeff  = self.Inductor_Impedance / ( self.Inductor_Impedance + Load_Parallel_Capacitor )

            self.Inductor_Current_VL_coeff  = self.Inductor_Voltage_VL_coeff / self.Inductor_Impedance
            self.Inductor_Current_VC_coeff  = self.Inductor_Voltage_VC_coeff / self.Inductor_Impedance
            self.Inductor_Current_IL_coeff  = self.Inductor_Voltage_IL_coeff / self.Inductor_Impedance
            self.Inductor_Current_IC_coeff  = self.Inductor_Voltage_IC_coeff / self.Inductor_Impedance
            self.Inductor_Current_VS_coeff  = self.Inductor_Voltage_VS_coeff / self.Inductor_Impedance

            self.Capacitor_Voltage_VC_coeff  = self.Capacitor_Impedance/( self.Capacitor_Impedance + Load_Parallel_Inductor )
            self.Capacitor_Voltage_VL_coeff  = Load_Parallel_Capacitor/( self.Inductor_Impedance + Load_Parallel_Capacitor )
            self.Capacitor_Voltage_IC_coeff  = self.Capacitor_Impedance * self.Inductor_Impedance * self.Load_Impedance /(self.Load_Impedance*self.Inductor_Impedance + self.Load_Impedance*self.Capacitor_Impedance + self.Inductor_Impedance * self.Capacitor_Impedance)
            self.Capacitor_Voltage_IL_coeff  = self.Capacitor_Voltage_IC_coeff
            self.Capacitor_Voltage_VS_coeff  = Load_Parallel_Capacitor / ( self.Inductor_Impedance + Load_Parallel_Capacitor )

            self.Capacitor_Current_VC_coeff  = self.Capacitor_Voltage_VC_coeff / self.Capacitor_Impedance
            self.Capacitor_Current_VL_coeff  = self.Capacitor_Voltage_VL_coeff / self.Capacitor_Impedance
            self.Capacitor_Current_IC_coeff  = self.Capacitor_Voltage_IC_coeff / self.Capacitor_Impedance
            self.Capacitor_Current_IL_coeff  = self.Capacitor_Voltage_IL_coeff / self.Capacitor_Impedance
            self.Capacitor_Current_VS_coeff  = self.Capacitor_Voltage_VS_coeff / self.Capacitor_Impedance
            
            self.Initial_Inductor_Current = self.Voltage_Souce_Magnitude/(self.Inductor_Impedance + Load_Parallel_Capacitor)
            self.Initial_Inductor_Voltage = self.Initial_Inductor_Current * self.Inductor_Impedance
            
            self.Initial_Capacitor_Voltage = self.Initial_Inductor_Current * Load_Parallel_Capacitor
            self.Initial_Capacitor_Current = self.Initial_Capacitor_Voltage/self.Capacitor_Impedance
            
        else:
            Load_Parallel_Inductor = self.Inductor_Impedance
            Load_Parallel_Capacitor = self.Capacitor_Impedance

            self.Inductor_Voltage_VL_coeff  = self.Inductor_Impedance/( self.Inductor_Impedance + self.Capacitor_Impedance )
            self.Inductor_Voltage_VC_coeff  = self.Inductor_Impedance/( self.Inductor_Impedance + self.Capacitor_Impedance )
            self.Inductor_Voltage_IL_coeff  = self.Capacitor_Impedance * self.Inductor_Impedance /(self.Inductor_Impedance + self.Capacitor_Impedance )
            self.Inductor_Voltage_IC_coeff  = self.Inductor_Voltage_IL_coeff
            self.Inductor_Voltage_VS_coeff  = self.Inductor_Impedance / ( self.Inductor_Impedance + self.Capacitor_Impedance )

            self.Inductor_Current_VL_coeff  = self.Inductor_Voltage_VL_coeff / self.Inductor_Impedance
            self.Inductor_Current_VC_coeff  = self.Inductor_Voltage_VC_coeff / self.Inductor_Impedance
            self.Inductor_Current_IL_coeff  = self.Inductor_Voltage_IL_coeff / self.Inductor_Impedance
            self.Inductor_Current_IC_coeff  = self.Inductor_Voltage_IC_coeff / self.Inductor_Impedance
            self.Inductor_Current_VS_coeff  = self.Inductor_Voltage_VS_coeff / self.Inductor_Impedance

            self.Capacitor_Voltage_VC_coeff  = self.Capacitor_Impedance/( self.Capacitor_Impedance + self.Inductor_Impedance )
            self.Capacitor_Voltage_VL_coeff  = self.Capacitor_Impedance/( self.Inductor_Impedance + self.Capacitor_Impedance )
            self.Capacitor_Voltage_IC_coeff  = self.Capacitor_Impedance * self.Inductor_Impedance  /(self.Inductor_Impedance + self.Capacitor_Impedance )
            self.Capacitor_Voltage_IL_coeff  = self.Capacitor_Voltage_IC_coeff
            self.Capacitor_Voltage_VS_coeff  = self.Capacitor_Impedance / ( self.Inductor_Impedance + self.Capacitor_Impedance )

            self.Capacitor_Current_VC_coeff  = self.Capacitor_Voltage_VC_coeff / self.Capacitor_Impedance
            self.Capacitor_Current_VL_coeff  = self.Capacitor_Voltage_VL_coeff / self.Capacitor_Impedance
            self.Capacitor_Current_IC_coeff  = self.Capacitor_Voltage_IC_coeff / self.Capacitor_Impedance
            self.Capacitor_Current_IL_coeff  = self.Capacitor_Voltage_IL_coeff / self.Capacitor_Impedance
            self.Capacitor_Current_VS_coeff  = self.Capacitor_Voltage_VS_coeff / self.Capacitor_Impedance

            self.Initial_Inductor_Current = self.Voltage_Souce_Magnitude/(self.Inductor_Impedance + self.Capacitor_Impedance)
            self.Initial_Inductor_Voltage = self.Initial_Inductor_Current * self.Inductor_Impedance
            
            self.Initial_Capacitor_Current = self.Initial_Inductor_Current
            self.Initial_Capacitor_Voltage = self.Initial_Capacitor_Current* self.Capacitor_Impedance
        
        # Show information about network
        if(self.input_values['show_about']):
            self.about()
    
    def Circuit_Solver_Inductor_Voltage(self,VL: Decimal,IL: Decimal,VC: Decimal,IC: Decimal):
        """Generates the voltage response of the inductor to wavefront distrubances. Solves by means of the wavefront equivalent circuit.

        :param VL: the magnitude of the voltage disturbance from the inductor
        :type VL: Decimal
        :param IL: the magnitude of the current disturbance from the inductor
        :type IL: Decimal
        :param VC: the magnitude of the voltage disturbance from the capacitor
        :type VC: Decimal
        :param IC: the magnitude of the current disturbance from the capacitor
        :type IC: Decimal
        :return: the the magnitude of the voltage response of the inductor to the disturbance
        :rtype: Decimal
        """
        return -VL * self.Inductor_Voltage_VL_coeff - VC * self.Inductor_Voltage_VC_coeff - IL * self.Inductor_Voltage_IL_coeff + IC * self.Inductor_Voltage_IC_coeff 

    def Circuit_Solver_Inductor_Current(self,VL: Decimal,IL: Decimal,VC: Decimal,IC: Decimal):
        """Generates the current response of the inductor to wavefront distrubances. Solves by means of the wavefront equivalent circuit.

        :param VL: the magnitude of the voltage disturbance from the inductor
        :type VL: Decimal
        :param IL: the magnitude of the current disturbance from the inductor
        :type IL: Decimal
        :param VC: the magnitude of the voltage disturbance from the capacitor
        :type VC: Decimal
        :param IC: the magnitude of the current disturbance from the capacitor
        :type IC: Decimal
        :return: the the magnitude of the current response of the inductor to the disturbance
        :rtype: Decimal
        """
        return -VL * self.Inductor_Current_VL_coeff - VC * self.Inductor_Current_VC_coeff - IL * self.Inductor_Current_IL_coeff + IC * self.Inductor_Current_IC_coeff 

    def Circuit_Solver_Inductor_Source_Voltage(self,VS: Decimal):
        """The magnitude of the voltage response of the inductor to a voltage source excitation.

        :param VS: magnitude of soure voltage excitation. 
        :type VS: Decimal
        :return: the the magnitude of the voltage response of the inductor to the disturbance
        :rtype: Decimal
        """
        return VS * self.Inductor_Voltage_VS_coeff

    def Circuit_Solver_Inductor_Source_Current(self,VS: Decimal):
        """The magnitude of the current response of the inductor to a voltage source excitation.

        :param VS: magnitude of soure voltage excitation. 
        :type VS: Decimal
        :return: the the magnitude of the current response of the inductor to the disturbance
        :rtype: Decimal
        """
        return VS * self.Inductor_Current_VS_coeff

    def Circuit_Solver_Capacitor_Voltage(self,VL: Decimal,IL: Decimal,VC: Decimal,IC: Decimal):
        """Generates the voltage response of the capacitor to wavefront distrubances. Solves by means of the wavefront equivalent circuit.

        :param VL: the magnitude of the voltage disturbance from the inductor
        :type VL: Decimal
        :param IL: the magnitude of the current disturbance from the inductor
        :type IL: Decimal
        :param VC: the magnitude of the voltage disturbance from the capacitor
        :type VC: Decimal
        :param IC: the magnitude of the current disturbance from the capacitor
        :type IC: Decimal
        :return: the the magnitude of the voltage response of the capacitor to the disturbance
        :rtype: Decimal
        """
        return -VC * self.Capacitor_Voltage_VC_coeff - VL * self.Capacitor_Voltage_VL_coeff - IC * self.Capacitor_Voltage_IC_coeff + IL * self.Capacitor_Voltage_IL_coeff 

    def Circuit_Solver_Capacitor_Current(self,VL: Decimal,IL: Decimal,VC: Decimal,IC: Decimal):
        """Generates the current response of the capacitor to wavefront distrubances. Solves by means of the wavefront equivalent circuit.

        :param VL: the magnitude of the voltage disturbance from the inductor
        :type VL: Decimal
        :param IL: the magnitude of the current disturbance from the inductor
        :type IL: Decimal
        :param VC: the magnitude of the voltage disturbance from the capacitor
        :type VC: Decimal
        :param IC: the magnitude of the current disturbance from the capacitor
        :type IC: Decimal
        :return: the the magnitude of the current response of the capacitor to the disturbance
        :rtype: Decimal
        """
        return -VC * self.Capacitor_Current_VC_coeff - VL * self.Capacitor_Current_VL_coeff - IC * self.Capacitor_Current_IC_coeff + IL * self.Capacitor_Current_IL_coeff 

    def Circuit_Solver_Capacitor_Source_Voltage(self,VS: Decimal):
        """The magnitude of the voltage response of the capacitor to a voltage source excitation.

        :param VS: magnitude of soure voltage excitation. 
        :type VS: Decimal
        :return: the the magnitude of the voltage response of the capacitor to the disturbance
        :rtype: Decimal
        """
        return VS * self.Capacitor_Voltage_VS_coeff

    def Circuit_Solver_Capacitor_Source_Current(self,VS: Decimal):
        """The magnitude of the current response of the capacitor to a voltage source excitation.

        :param VS: magnitude of soure voltage excitation. 
        :type VS: Decimal
        :return: the the magnitude of the current response of the capacitor to the disturbance
        :rtype: Decimal
        """
        return VS * self.Capacitor_Current_VS_coeff
    
    def about(self):
        """Prints out information input varibles and associated calculated variables.
        """
        print(f"\nInformation about this network : \n")

        print(f"\n- The Inductor -")
        print(f"{'Inductor Inductance Per Length :':<40}{self.Inductor_Inductance_Per_Length}")
        print(f"{'Inductor Capacitance Per Length :':<40}{self.Inductor_Capacitance_Per_Length}")
        print(f"{'Inductor Length :':<40}{self.Inductor_Length}")
        print(f"{'Inductor Total Inductance :':<40}{self.Inductor_Total_Inductance}")
        print(f"{'Inductor Total Capacitance :':<40}{self.Inductor_Total_Capacitance}")
        print(f"{'Inductor Velocity :':<40}{self.Inductor_Velocity}")
        print(f"{'Inductor One Way Time Delay :':<40}{self.Inductor_Time}")
        print(f"{'Inductor Impedance :':<40}{self.Inductor_Impedance}")
        
        print(f"\n- The Capacitor -")
        print(f"{'Capacitor Inductance Per Length :':<40}{self.Capacitor_Inductance_Per_Length}")
        print(f"{'Capacitor Capacitance Per Length :':<40}{self.Capacitor_Capacitance_Per_Length}")
        print(f"{'Capacitor Length :':<40}{self.Capacitor_Length}")
        print(f"{'Capacitor Total Inductance :':<40}{self.Capacitor_Total_Inductance}")
        print(f"{'Capacitor Total Capacitance :':<40}{self.Capacitor_Total_Capacitance}")
        print(f"{'Capacitor Velocity :':<40}{self.Capacitor_Velocity}")
        print(f"{'Capacitor One Way Time Delay :':<40}{self.Capacitor_Time}")
        print(f"{'Capacitor Impedance :':<40}{self.Capacitor_Impedance}")
        
        print(f"\n- The Time -")
        print(f"{'Number Periods :':<40}{self.Number_Periods}")
        print(f"{'Simulation Stop Time :':<40}{self.Simulation_Stop_Time}")
        print(f"{'Number of Wavefronts :':<40}{self.Number_of_Wavefronts}")
        print(f"{'Number of Layers :':<40}{self.Number_of_Layers}")
        print(f"{'Inductor Return Time Delay :':<40}{2*self.Inductor_Time}")
        print(f"{'Inductor LCM Factor :':<40}{self.Inductor_LCM_Factor}")
        print(f"{'Capacitor Return Time Delay :':<40}{2*self.Capacitor_Time}")
        print(f"{'Capacitor LCM Factor :':<40}{self.Capacitor_LCM_Factor}")
        print(f"{'LCM :':<40}{self.LCM}")
        print(f"{'GCD :':<40}{self.GCD}")
        print(f"{'Higher Merging? :':<40}{self.is_Higher_Merging}")
        

        print(f"\n- The Circuit -")
        print(f"{'Votage Source Magnitude :':<40}{self.Voltage_Souce_Magnitude}")
        print(f"{'Buck Converter :':<40}{self.Is_Buck}")
        print(f"{'Load Resistance :':<40}{self.Load_Impedance}")
    
@dataclass
class Data_Output_Storage:
    """Stores data of various types of fanout diagrams after simulation. 
        Stores information for commutatively merged fanouts, as well as, multipicatively merged fanouts.
        
        Fanout diagrams take form of 2D numpy arrays of format Array[L,C] where L is the inductive event number and C the capacitve event number.
        There are a total of 9 arrays stored, one for the arrival time of each grid node, 
        four for the current and voltage at the interconncet for the capacitor and inductor, 
        and another four for the sending and returning wavefronts of the capacitor and inductor. 
        
        :param Time: 2D numpy array of the return times of grid nodes
        :type Time: np.ndarray[Decimal]
        :param Voltage_Interconnect_Inductor: 2D numpy array of the interconnect voltage change of the inductor at a grid node
        :type Voltage_Interconnect_Inductor: np.ndarray[Decimal]
        :param Current_Interconnect_Inductor: 2D numpy array of the interconnect current change of the inductor at a grid node
        :type Current_Interconnect_Inductor: np.ndarray[Decimal]
        :param Voltage_Interconnect_Capacitor: 2D numpy array of the interconnect voltage change of the capacitor at a grid node
        :type Voltage_Interconnect_Capacitor: np.ndarray[Decimal]
        :param Current_Interconnect_Capacitor: 2D numpy array of the interconnect current change of the capacitor at a grid node
        :type Current_Interconnect_Capacitor: np.ndarray[Decimal]
        :param Wavefronts_Sending_Inductor: 2D numpy array of the wavefronts sent into the inductor at grid nodes
        :type Wavefronts_Sending_Inductor: np.ndarray[Wavefront_Inductive]
        :param Wavefronts_Sending_Capacitor: 2D numpy array of the wavefronts sent into the capacitor at grid nodes
        :type Wavefronts_Sending_Capacitor: np.ndarray[Wavefront_Capacitive]
        :param Wavefronts_Returning_Inductor: 2D numpy array of the wavefronts returning from the inductor at grid nodes
        :type Wavefronts_Returning_Inductor: np.ndarray[Wavefront_Inductive]
        :param Wavefronts_Returning_Capacitor: 2D numpy array of the wavefronts returning from the capacitor at grid nodes
        :type Wavefronts_Returning_Capacitor: np.ndarray[Wavefront_Capacitive]
        :param has_merged: indicates if the data stored has been multiplicatively merged or not.
        :type has_merged: bool
        
        .. code-block:: python
            :caption: Example use of Data_Output_Storage
            
            # Generate input data object from input paramters
            data_input = Data_Input_Storage(Simulation_stop_time = '100',L_impedance = '225')
            
            # Generate the commutative merging output data from the created Data_Input_Storage object:
            data_output_commutative : Data_Output_Storage = Generate_Wavefronts_Commutatively(data_input)
            # Get sending wavefronts of the capacitor after only commutative merging:
            data_output_commutative.Wavefronts_Sending_Capacitor
            
            # Generate the merged data after multiplicative merging:
            data_output_merged  : Data_Output_Storage = Higher_Order_Merging(data_input,data_output_commutative)
            # Get sending wavefronts of the capacitor after multiplicative merging:
            data_output_merged.Wavefronts_Sending_Capacitor
        
    """
    
    Time : np.ndarray
    
    Voltage_Interconnect_Inductor : np.ndarray 
    Current_Interconnect_Inductor : np.ndarray

    Voltage_Interconnect_Capacitor : np.ndarray
    Current_Interconnect_Capacitor : np.ndarray

    Wavefronts_Sending_Inductor : np.ndarray
    Wavefronts_Sending_Capacitor : np.ndarray

    Wavefronts_Returning_Inductor : np.ndarray
    Wavefronts_Returning_Capacitor : np.ndarray
    
    has_merged : bool 
    
    def get_sending_wavefronts_magnitudes(self,which_string):
        """A method for extracting voltage or current from *sending* wavefronts.

        :param which_string: possible options: ["voltage inductor", "current inductor", "voltage capacitor", "current capacitor"]
        :type which_string: str
        :raises ValueError: errors if incorrect string is given. 
        :return: Sending wavefront's Current or Voltage magnitudes 
        :rtype: np.ndarray[Decimal]
        """
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
            raise ValueError("Incorrect plotting choice,\'"+which_string+"\' is not an option. Options are : "+ str(allowed_strings))
        
    def get_returning_wavefronts_magnitudes(self,which_string):
        """A method for extracting voltage or current from *returning* wavefronts.

        :param which_string: possible options: ["voltage inductor", "current inductor", "voltage capacitor", "current capacitor"]
        :type which_string: str
        :raises ValueError: errors if incorrect string is given. 
        :return: Returning wavefront's Current or Voltage magnitudes 
        :rtype: np.ndarray[Decimal]
        """
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
            raise ValueError("Incorrect plotting choice,\'"+which_string+"\' is not an option. Options are : "+ str(allowed_strings))

@dataclass
class Data_Output_Storage_Ordered(Data_Output_Storage):
    """A dataclass that stored ordered inteface output data in form of single dimenstional arrays. 
    All the core arrays that are present in the Data_Output_Storage class are present here but in their one-dimensional chronological form.
    
    :param Indexes: An additonal array, indicating the grid co-ordiantes on the merged fanout structure in the order events occured. 
        Is a single dimesional list of (L,C) coordiante lists. The inner lists take form of [L,C].
    :type Indexes: List[Lists]
    """
    Indexes : np.ndarray

@dataclass
class Interface_Data:
    """A Dataclass that holds all simulation data for a praticular interface. Contains four data storage components: 
    
    :param data_input: input data and calcualted parameters of the interface
    :type data_input: Data_Input_Storage
    :param data_output_commutative: Data_Output_Storage object for commutative fanouts
    :type data_output_commutative: Data_Output_Storage
    :param data_output_multiplicative: Data_Output_Storage object for multiplicatively merged fanouts
    :type data_output_multiplicative: Data_Output_Storage
    :param data_output_ordered: Chronologically ordered merged data in a linear format 
    :type data_output_ordered: Data_Output_Storage_Ordered
    """
    data_input : Data_Input_Storage
    data_output_commutative : Data_Output_Storage
    data_output_multiplicative : Data_Output_Storage
    data_output_ordered : Data_Output_Storage_Ordered

def get_array_absolute_maximum(array : np.ndarray):
    """Get the maximum absolute value of a data_output array.
    Used for normalising the colour bars of fanout plots.

    :param array: array to get the absoulute maximum
    :type array: np.ndarray[Decimal]
    :return: the absolute maximum of the array
    :rtype: Decimal
    """
    max_boundary = abs(np.max(array.astype(float)))
    min_boundary = abs(np.min(array.astype(float)))
    
    return max(max_boundary, min_boundary)

def get_voltage_from_wavefront(wavefront):
    """get the voltage of a wavefront. Used as a dummy fucntion to be vectorized, see "get_voltage_array".

    :param wavefront: a wavefront
    :type wavefront: Wavefront
    :return: voltage magnitude of wavefront
    :rtype: Decimal
    """
    return wavefront.magnitude_voltage

#: The vectorized function that extracts the voltages from an np.ndarray[Wavefronts] array.
get_voltage_array = np.vectorize(get_voltage_from_wavefront)

def get_current_from_wavefront(wavefront):
    """get the voltage of a wavefront. Used as a dummy fucntion to be vectorized, see "get_current_array".

    :param wavefront: a wavefront
    :type wavefront: Wavefront
    :return: current magnitude of wavefront
    :rtype: Decimal
    """
    return wavefront.magnitude_current

#: The vectorized function that extracts the currents from an np.ndarray[Wavefronts] array.
get_current_array = np.vectorize(get_current_from_wavefront)

def get_image_array(array):
    """Turns an output-ordered 1-dimesional array into a format that can be displayed by matplotlib "imshow".

    :param array: a single dimension np.ndarray or List 
    :type array: np.ndarray or List
    :return: an output array that can be shown using "imshow"
    :rtype: np.ndarray 
    """
    image_array = np.full((len(array),1),Decimal('0'))
    
    for i,val in enumerate(array):
        image_array[i][0] = val
        
    return image_array

def transform_merged_array_to_C_axis(data_input : Data_Input_Storage,merged_array):
    """Transform merged data output array to a C-axis merging representation

    :param data_input: input data for merged array
    :type data_input: Data_Input_Storage
    :param merged_array: merged array aligne to the C-axis
    :type merged_array: np.ndarray[Decimal]
    """
    
    def extract_merging_region(data_input : Data_Input_Storage,merged_array, KL_index):
        # extract a mergign region along the inductive axis
        KL = data_input.Inductor_LCM_Factor
        KC = data_input.Capacitor_LCM_Factor
    
        return merged_array[KL_index*KL:KL_index*KL+KL,0:KC]

    # get first meging region
    new_array = extract_merging_region(data_input,merged_array,0)
    # determine number of merging regions
    number_of_KLs = int((data_input.Number_of_Layers+1)/data_input.Inductor_LCM_Factor)
    for i in range(1,number_of_KLs):
        # rearrange and add merging regions allong the C-axis
        new_merging_region = extract_merging_region(data_input,merged_array,i)
        new_array = np.concatenate((new_array,new_merging_region),axis =1)
        
    return new_array

def lcm_gcd_euclid(TL:Decimal,TC:Decimal):
    """Gets the LCM, GCD and two co-factors KL and KC for time delays TL and TC.
    
    This function makes use of the Euclidean algorithm, which is typically only defined for the integers. 
    In this implementation the functionallity is extended to the rational numbers. 
    
    :param TL: any rational number, Typically the inductive time delay
    :type TL: Decimal
    :param TC: any rational number, Typically the capacitve time delay
    :type TC: Decimal
    :return: A dictionary that contains the LCM, GCD and two co-factors.
    :rtype: Dict
    """
    num_big = max(TL,TC)
    num_small = min(TL,TC)
    
    num_big_original = num_big
    num_small_original = num_small
    
    num_big_numerator,num_big_denomenator = num_big.as_integer_ratio()
    num_small_numerator, num_small_denomenator = num_small.as_integer_ratio()
    
    common_den = Decimal(str(num_big_denomenator ))* Decimal(str(num_small_denomenator))
    
    num_big = num_big_numerator * num_small_denomenator
    num_small = num_small_numerator * num_big_denomenator
    
    equations = []
    
    # initialize 
    multiplier, remainder = divmod(num_big,num_small)
    equations.append(dict([('num_big',num_big),('mul_small',multiplier),('num_small',num_small),('remainder',remainder)]))
    
    while remainder != 0:
        num_big = num_small
        num_small = remainder
        
        multiplier, remainder = divmod(num_big,num_small)
        equations.append(dict([('num_big',num_big),('mul_small',multiplier),('num_small',num_small),('remainder',remainder)]))
        
    GCD_big = num_small
    GCD = GCD_big/common_den
    LCM = num_big_original * num_small_original/(GCD)
    
    K_big = num_small_original/GCD
    K_small = num_big_original/GCD
    
    KL = 0
    KC = 0
    
    if(TL > TC):
        KL = K_big
        KC = K_small
    else:
        KL = K_small
        KC = K_big
    
    Factor_dict = dict([('TL',TL),('TC',TC),
                        ('KL',KL),('KC',KC),
                        ('GCD',GCD),('LCM',LCM)])

    return Factor_dict

def Steady_State_Analysis(TL:Decimal,TC:Decimal):
    """Prints out the steady-state analysis of an interface described by two time delays.
    Returns when each of the two criteria for steady-state to be reach will occur. 

    :param TL: inductive time delay
    :type TL: Decimal
    :param TC: capacitive time delay
    :type TC: Decimal
    :return: (time_before_regular_GCF, time_before_regular_Steady_State)
    :rtype: Tuple
    """
    print(f'Bezout analysis for TL = {TL}s and TC = {TC}s \n')
    # Determine the larger of the two numbers
    num_big = max(TL,TC)
    num_small = min(TL,TC)
    
    # Keep original copy
    num_big_original = num_big
    num_small_original = num_small
    
    # Make rational numbers integers, denomenator will factored back in later
    num_big_numerator,num_big_denomenator = num_big.as_integer_ratio()
    num_small_numerator, num_small_denomenator = num_small.as_integer_ratio()
    
    common_den = Decimal(str(num_big_denomenator ))* Decimal(str(num_small_denomenator))
    
    # make rational numbers integers 
    num_big = num_big_numerator * num_small_denomenator
    num_small = num_small_numerator * num_big_denomenator
    
    # container for operations to follow
    equations = []
    
    # initialize 
    multiplier, remainder = divmod(num_big,num_small)
    equations.append(dict([('num_big',num_big),('mul_small',multiplier),('num_small',num_small),('remainder',remainder)]))
    
    # Extended Euclidean Algorithm
    while remainder != 0:
        num_big = num_small
        num_small = remainder
        
        multiplier, remainder = divmod(num_big,num_small)
        equations.append(dict([('num_big',num_big),('mul_small',multiplier),('num_small',num_small),('remainder',remainder)]))
    
    # Factor back denomenator
    GCD_big = num_small
    GCD = GCD_big/common_den
    LCM = num_big_original * num_small_original/(GCD)
    
    K_big = num_small_original/GCD
    K_small = num_big_original/GCD
    
    # Find Bezout's coefficients by working back from the Euclidean Algorithm
    
    def make_equation_reverse_format (equation):
        '''Solve for remainder in orginal euclidean equation'''
        
        reverse_equation = dict([('mul_big',1),
                        ('num_big' , equation['num_big']),
                        ('mul_small' , equation['mul_small']*-1),
                        ('num_small' , equation['num_small'])
                        ])
        
        return reverse_equation
        
    def apply_next_equation (start_eq, next_eq):
        '''Create next equation when performing the Bezout algorithm on the original set of Euclidean Equations'''
        next_eq = make_equation_reverse_format(next_eq)
        next_eq['mul_small'] = start_eq['mul_big'] + start_eq['mul_small']*next_eq['mul_small']
        next_eq['mul_big'] = start_eq['mul_small']
        
        return next_eq
    
    # get the index of the second last equation
    reverse_index = len(equations) -2 
    
    start_equation = make_equation_reverse_format(equations[reverse_index])
    reverse_index -= 1
    
    # special case if Bezout's algorithm
    if num_small_original == GCD: # big num is multiple of small num
        print('** Special Case **')
        print('Small number is multiple of big number')
        start_equation['mul_big'] = Decimal('0')
        start_equation['mul_small'] = Decimal('1')
    
    else: 
        while reverse_index > -1:
            start_equation = apply_next_equation(start_equation,equations[reverse_index])
            reverse_index -= 1
    
    print(f'Euclidean algorithm completed :')
    print(f'LCM = {LCM}s, GCD = {GCD}s')
    print(f'{K_big} x {num_big_original}s = {K_small} x {num_small_original}s = {LCM}s \n')
    print(f'Bezout analysis completed: ')
    print(f'{start_equation["mul_big"]} x {num_big_original} + {start_equation["mul_small"]} x {num_small_original} = {GCD} or {start_equation["mul_big"]*num_big_original}s + {start_equation["mul_small"]*num_small_original}s = {GCD}s')
    
    new_big_mul = 0
    new_small_mul = 0
    if start_equation["mul_big"] > 0:
        new_big_mul  = start_equation["mul_big"] - K_big
        new_small_mul = start_equation["mul_small"] + K_small
    else:
        new_big_mul  = start_equation["mul_big"] + K_big
        new_small_mul = start_equation["mul_small"] - K_small
    print(f'{new_big_mul} x {num_big_original} + {new_small_mul} x {num_small_original} = {GCD} or {new_big_mul*num_big_original}s + {new_small_mul*num_small_original}s = {GCD}s\n')
    
    
    # Find first time a GCF step occurs
    significant_time_1a = abs(start_equation["mul_big"]*num_big_original)
    significant_time_1b = abs(start_equation["mul_small"]*num_small_original)
    
    significant_time_2a = abs(new_big_mul*num_big_original)
    significant_time_2b = abs(new_small_mul*num_small_original)
    
    
    print(f'Case 1 of a GCF time-step happens from {min(significant_time_1a,significant_time_1b)}s to {max(significant_time_1a,significant_time_1b)}s')
    print(f'Case 2 of a GCF time-step happens from {min(significant_time_2a,significant_time_2b)}s to {max(significant_time_2a,significant_time_2b)}s')
        
    # Find last event before regular GCF time-steps
    negative_multiple_1 = 0
    number_1 = 0
    
    negative_multiple_2 = 0
    number_2 = 0 
    
    if start_equation["mul_big"] < 0 :
        negative_multiple_1 = abs(start_equation["mul_big"])-1
        number_1 = num_big_original
        
        negative_multiple_2 = abs(new_small_mul)-1
        number_2 = num_small_original
    else:
        negative_multiple_1 = abs(start_equation["mul_small"])-1
        number_1 = num_small_original
        
        negative_multiple_2 = abs(new_big_mul)-1
        number_2 = num_big_original
    
    time_before_regular_GCF = negative_multiple_1*number_1 + negative_multiple_2*number_2
    
    # Find last event before consistent multiplicative merging/ when steady state commences.
    time_before_regular_Steady_State = LCM-num_small_original
    
    print(f'\nThe last event before regular GCF time-steps is at {time_before_regular_GCF}s')
    print(f"The last event before Steady State operation is at {LCM-num_small_original}s")
    
    return time_before_regular_GCF, time_before_regular_Steady_State

def Generate_Wavefronts_Commutatively(Data_Input : Data_Input_Storage):
    """Generates a Data_Output_Storage object from the calculated input variables stored in a Data_Input_Storage object. 
    
    :param Data_Input: Input data object containing simulation input variables
    :type Data_Input: Data_Input_Storage
    :return: output data (a collection commutative fanouts in form of np.ndarrays)
    :rtype: Data_Output_Storage
    
    Resposible for generating wavefronts and simultaneously commutatively merging the wavefronts. 
    The simaltaneous commutative merging of wavefronts is mandatory for longer simulation times.
    """

    class Wavefront:
        """Base wavefront class.
        """
        velocity = Decimal()
        length = Decimal()
        
        position_start = Decimal()
        position_end = Decimal()

        time_start = Decimal()
        time_end = Decimal()

        magnitude_voltage = Decimal()
        magnitude_current = Decimal()
        def __add__(self, Wavefront_add ):
            """superimposes two wavefronts and adds their magnitudes.

            :param Wavefront_add: wavefront to be added with self
            :type Wavefront_add: Wavefront
            :return: self wavefront with magnitudes added
            :rtype: Wavefront (same as self)
            """
            
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
        
        def Position_at_time(self,time):
            """Generates the position of wavefront at time-equirey. Returns False if no intercept.

            :param time: time enquirey
            :type time: Decimal or str
            :return: position attime enquiret
            :rtype: Decimal
            """
            t = Decimal(time)

            if self.time_start <= t <= self.time_end:
                if self.position_start == 0 :
                    return (t-self.time_start)*self.velocity
                else:
                    return self.length - (t-self.time_start)*self.velocity
            else:
                return False

    class Wavefront_Source( Wavefront ):
        """Class representing switiching wavefronts of the voltage source. 
        In this release wavefonts switching is not supported, 
        this class used to initiated wavefronts at t=0 only. 
        """

        def __init__(self,magnitude,time_start):
            """intialised the wavefront.

            :param magnitude: Source magnitude
            :type magnitude: str or Decimal
            :param time_start: start of pulse
            :type time_start: str or Decimal
            """
            
            self.length = Decimal(0)

            self.position_start = Decimal(0)
            self.position_end = Decimal(0)

            self.time_start = Decimal(time_start)

            self.magnitude_voltage = Decimal(magnitude)
            self.magnitude_current = Decimal(0)

        def generate_and_store(self, Wavefront_Storage_Away : deque):
            """triggers the creation of the inital wavefronts in the inductor and capacitor. 
            Stores them in the Wavefront_Storage. Order is important, inductive first followed by capacitive. 

            :param Wavefront_Storage: Storage array for away waves
            :type Wavefront_Storage: deque
            """
            Wavefront_Storage_Away.append(Wavefront_Inductive(self,False))
            Wavefront_Storage_Away.append(Wavefront_Capacitive(self,False))
            
    class Wavefront_Capacitive( Wavefront ):
        """A wavefront travelling in the capacitor. 
        """

        def __init__(self, Wavefront_Parent : Wavefront, is_reflection : bool):
            
            self.velocity = Data_Input.Capacitor_Velocity
            self.length = Data_Input.Capacitor_Length

            self.position_start = Wavefront_Parent.position_end

            self.time_start = Wavefront_Parent.time_end
            self.time_end = self.time_start + Data_Input.Capacitor_Time

            if self.position_start == 0:

                self.position_end = Data_Input.Capacitor_Length

                if is_reflection: # A reflected wave at source side   |<--

                    self.magnitude_voltage = Data_Input.Circuit_Solver_Capacitor_Voltage(0, 0, Wavefront_Parent.magnitude_voltage, Wavefront_Parent.magnitude_current)
                    self.magnitude_current = Data_Input.Circuit_Solver_Capacitor_Current(0, 0, Wavefront_Parent.magnitude_voltage, Wavefront_Parent.magnitude_current)

                elif isinstance(Wavefront_Parent, Wavefront_Source) : # A generate source wave (Vs)-|->

                    self.time_start = Wavefront_Parent.time_start
                    self.time_end = self.time_start + Data_Input.Capacitor_Time

                    self.magnitude_voltage = Data_Input.Circuit_Solver_Capacitor_Source_Voltage(Wavefront_Parent.magnitude_voltage)
                    self.magnitude_current = Data_Input.Circuit_Solver_Capacitor_Source_Current(Wavefront_Parent.magnitude_voltage)

                else: # A transmitted wave at source side  -|->

                    self.magnitude_voltage = Data_Input.Circuit_Solver_Capacitor_Voltage(Wavefront_Parent.magnitude_voltage, Wavefront_Parent.magnitude_current, 0, 0)
                    self.magnitude_current = Data_Input.Circuit_Solver_Capacitor_Current(Wavefront_Parent.magnitude_voltage, Wavefront_Parent.magnitude_current, 0, 0)

            else: # A reflected wave at load side   -->|

                self.position_end = 0

                self.magnitude_voltage = Wavefront_Parent.magnitude_voltage
                self.magnitude_current = - Wavefront_Parent.magnitude_current

        def generate_and_store(self, Wavefront_Storage):
            if self.position_end == 0:
                Wavefront_Storage.append(Wavefront_Inductive(self,False))
                Wavefront_Storage.append(Wavefront_Capacitive(self,True))
            else:
                Wavefront_Storage.append(Wavefront_Capacitive(self,True))
        
        def generate_and_return(self):
            if self.position_end == 0:
                return Wavefront_Inductive(self,False), Wavefront_Capacitive(self,True)
            else :
                return Wavefront_Capacitive(self,True)

        def Merge(self, Wavefront_Other : Wavefront):
            self.magnitude_voltage = self.magnitude_voltage + Wavefront_Other.magnitude_voltage
            self.magnitude_current = self.magnitude_current + Wavefront_Other.magnitude_current

    class Wavefront_Inductive( Wavefront ):

        def __init__(self, Wavefront_Parent : Wavefront, is_reflection : bool):
            
            self.velocity = Data_Input.Inductor_Velocity
            self.length = Data_Input.Inductor_Length

            self.position_start = Wavefront_Parent.position_end

            self.time_start = Wavefront_Parent.time_end
            self.time_end = self.time_start + Data_Input.Inductor_Time

            if self.position_start == 0:

                self.position_end = Data_Input.Inductor_Length

                if is_reflection: # A reflected wave at source side   |<--

                    self.magnitude_voltage = Data_Input.Circuit_Solver_Inductor_Voltage( Wavefront_Parent.magnitude_voltage, Wavefront_Parent.magnitude_current, 0, 0)
                    self.magnitude_current = Data_Input.Circuit_Solver_Inductor_Current( Wavefront_Parent.magnitude_voltage, Wavefront_Parent.magnitude_current, 0, 0)

                elif isinstance(Wavefront_Parent, Wavefront_Source) : # A generate source wave (Vs)-|->

                    self.time_start = Wavefront_Parent.time_start
                    self.time_end = self.time_start + Data_Input.Inductor_Time

                    self.magnitude_voltage = Data_Input.Circuit_Solver_Inductor_Source_Voltage(Wavefront_Parent.magnitude_voltage)
                    self.magnitude_current = Data_Input.Circuit_Solver_Inductor_Source_Current(Wavefront_Parent.magnitude_voltage)
                    
                else: # A transmitted wave at source side  -|->

                    self.magnitude_voltage = Data_Input.Circuit_Solver_Inductor_Voltage(0, 0, Wavefront_Parent.magnitude_voltage, Wavefront_Parent.magnitude_current)
                    self.magnitude_current = Data_Input.Circuit_Solver_Inductor_Current(0, 0, Wavefront_Parent.magnitude_voltage, Wavefront_Parent.magnitude_current)

            else: # A reflected wave at load side   -->|
                
                self.position_end = 0

                self.magnitude_voltage = - Wavefront_Parent.magnitude_voltage
                self.magnitude_current = Wavefront_Parent.magnitude_current

        def generate_and_store(self, Wavefront_Storage):
            if self.position_end == 0:
                Wavefront_Storage.append(Wavefront_Inductive(self,True))
                Wavefront_Storage.append(Wavefront_Capacitive(self,False))
            else :
                Wavefront_Storage.append(Wavefront_Inductive(self,True))

        def generate_and_return(self):
            if self.position_end == 0:
                return Wavefront_Inductive(self,True), Wavefront_Capacitive(self,False)
            else :
                return Wavefront_Inductive(self,True)

        def Merge(self, Wavefront_Other : Wavefront):
            self.magnitude_voltage = self.magnitude_voltage + Wavefront_Other.magnitude_voltage
            self.magnitude_current = self.magnitude_current + Wavefront_Other.magnitude_current

    # The algorithm to follow makes use of SPARSE storage arrays,
    # this is done as to store both capacitve and inductive wavefronts in a single array
    # (there will be two spares arrays, one for AWAY wavefronts and one for RETURNING wavefronts).

    # SPARSE FANOUT STORAGE ARRAY FORMAT FOR 5 LAYERS:
    # (horizontal = inductive axis, vertical = capacitive axis)
    # x = major gird node, → = wavefront inductive, ↓ = wavefront capacitve, 0 = 'blank entry'
    #   0 1 2 3 4 5 6 7 8 9
    #   ____________________
    #0 |x → x → x → x → x →
    #1 |↓ 0 ↓ 0 ↓ 0 ↓ 0 ↓ 
    #2 |x → x → x → x →
    #3 |↓ 0 ↓ 0 ↓ 0 ↓ 
    #4 |x → x → x → 
    #5 |↓ 0 ↓ 0 ↓
    #6 |x → x →
    #7 |↓ 0 ↓
    #8 |x →
    #9 |↓
    
    # The two Sparse storage arrays:
    # ------------------------------
    Wavefronts_Away = np.full((2*(Data_Input.Number_of_Layers+1),2*(Data_Input.Number_of_Layers+1)),Wavefront_Source(0,0))
    Wavefronts_Return = np.full((2*(Data_Input.Number_of_Layers+1),2*(Data_Input.Number_of_Layers+1)),Wavefront_Source(0,0))
    
    
    # These Sparse arrays are then post-porcessed in a 'gemoetric" way to extract magnitude data in a dense format.
    # Dense format arrays will store data as a function of major nodes, and will have no 'blank entries'.
    # An example of a Dense array would be "Wavefronts sent from the Inductor" (Wavefronts_Sending_Inductor):
    
    # DENSE FANOUT STORAGE ARRAY FORMAT FOR 5 LAYERS:
    # (horizontal = inductive axis, vertical = capacitive axis)
    # x = major gird node, → = wavefront inductive, ↓ = wavefront capacitve, 0 = 'blank entry'
    #   0 1 2 3 4 
    #   __________
    #0 |→ → → → →
    #1 |→ → → →  
    #2 |→ → → 
    #3 |→ → 
    #4 |→ 

    # Dense format arrays tracked:
    # ----------------------------
    Time = np.full(((Data_Input.Number_of_Layers+1),(Data_Input.Number_of_Layers+1)),Decimal('0'))
    
    Voltage_Interconnect_Inductor = np.full(((Data_Input.Number_of_Layers+1),(Data_Input.Number_of_Layers+1)),Decimal('0'))
    Current_Interconnect_Inductor = np.full(((Data_Input.Number_of_Layers+1),(Data_Input.Number_of_Layers+1)),Decimal('0'))

    Voltage_Interconnect_Capacitor = np.full(((Data_Input.Number_of_Layers+1),(Data_Input.Number_of_Layers+1)),Decimal('0'))
    Current_Interconnect_Capacitor = np.full(((Data_Input.Number_of_Layers+1),(Data_Input.Number_of_Layers+1)),Decimal('0'))
    
    Wavefronts_Sending_Inductor = np.full(((Data_Input.Number_of_Layers+1),(Data_Input.Number_of_Layers+1)), Wavefront_Source(0,0))
    Wavefronts_Sending_Capacitor = np.full(((Data_Input.Number_of_Layers+1),(Data_Input.Number_of_Layers+1)), Wavefront_Source(0,0))
    
    Wavefronts_Returning_Inductor = np.full(((Data_Input.Number_of_Layers+1),(Data_Input.Number_of_Layers+1)), Wavefront_Source(0,0))
    Wavefronts_Returning_Capacitor = np.full(((Data_Input.Number_of_Layers+1),(Data_Input.Number_of_Layers+1)), Wavefront_Source(0,0))
    
    # POPULATE THE SPARSE STORAGE ARRAYS
    # ===================================
    #Deques of wavefronts thare are used to temporarily store wavefronts as they are being processed.
    Wavefronts_Away_deque : Wavefront = deque()
    Wavefronts_Returning_deque : Wavefront = deque()

    # Generate Intial Away Waves from voltage excitation
    temp_wavefront = Wavefront_Source(Data_Input.Voltage_Souce_Magnitude,0,0)
    temp_wavefront.generate_and_store(Wavefronts_Away_deque)

    # Generate Intial Return Waves,
    # Get Intial Sending wavefront, this will be an inductive wavefront
    temp_wavefront_inductive = Wavefronts_Away_deque.popleft()
    temp_wavefront_inductive.generate_and_store(Wavefronts_Returning_deque)
    Wavefronts_Away[1,0] = temp_wavefront_inductive
    
    # Get Next Initial Sending wavefront, this will be a capacitive wavefront
    temp_wavefront_capacitive = Wavefronts_Away_deque.popleft()
    temp_wavefront_capacitive.generate_and_store(Wavefronts_Returning_deque)
    Wavefronts_Away[0,1] = temp_wavefront_capacitive

    # GENERATE WAVEFRONTS AND MERGE COMMUTATIVELY
    for layer_number in range(1,Data_Input.Number_of_Layers):

        # RETURNING WAVEFRONTS
        # --------------------
        
        # set Index    
        Wavefront_Index_x = 2*layer_number-1
        Wavefront_Index_y = 0
        
        # process first Returning Wavefront:

        # (will be inductive wavefront) 
        # (first wavefront does not merge)
        temp_wavefront = Wavefronts_Returning_deque.popleft()

        # generate away wavefronts,  
        temp_wavefront.generate_and_store(Wavefronts_Away_deque)
        # store returning wavefront, 
        Wavefronts_Return[Wavefront_Index_x,Wavefront_Index_y] = temp_wavefront
        # shift index
        Wavefront_Index_x = Wavefront_Index_x - 1
        Wavefront_Index_y = Wavefront_Index_y + 1
        
        # process remaining Returning Wavefronts:

        while len(Wavefronts_Returning_deque) > 0:
            # Get a Returning wavefront 
            # (will be capacitve)
            temp_wavefront = Wavefronts_Returning_deque.popleft()
            
            if len(Wavefronts_Returning_deque) == 0 : # It is the last wave?
                # (Last wavefront does not merge)
                # generate away wavefronts and store in Away wavefronts deque
                temp_wavefront.generate_and_store(Wavefronts_Away_deque)
                # store returning wavefronts
                Wavefronts_Return[Wavefront_Index_x,Wavefront_Index_y] = temp_wavefront
                # shift index
                Wavefront_Index_x = Wavefront_Index_x - 1
                Wavefront_Index_y = Wavefront_Index_y + 1

            else: # It is not the last wave :
                
                # merge children of 'adjacent' returning wavefronts:

                # get next returning wavefront 
                # (will be inductive)
                temp_next_wavefront = Wavefronts_Returning_deque.popleft()

                # get children of the two current wavefronts
                temp_wavefront_inductive, temp_wavefront_capacitve = temp_wavefront.generate_and_return()
                temp_next_wavefront_inductive, temp_next_wavefront_capacitve = temp_next_wavefront.generate_and_return()

                # commutatively merge the children appropriately 
                temp_wavefront_inductive.Merge(temp_next_wavefront_inductive)
                temp_wavefront_capacitve.Merge(temp_next_wavefront_capacitve)

                # add newly merged children in Away wavefronts deque
                Wavefronts_Away_deque.append(temp_wavefront_inductive)
                Wavefronts_Away_deque.append(temp_wavefront_capacitve)
                
                # Store current returning wavefronts in their completion storage array
                # capacitive returning wavefront
                Wavefronts_Return[Wavefront_Index_x,Wavefront_Index_y] = temp_wavefront
                # Shift index
                Wavefront_Index_x = Wavefront_Index_x - 1
                Wavefront_Index_y = Wavefront_Index_y + 1
                
                # inductive returning wavefront
                Wavefronts_Return[Wavefront_Index_x,Wavefront_Index_y] = temp_next_wavefront
                # shift index
                Wavefront_Index_x = Wavefront_Index_x - 1
                Wavefront_Index_y = Wavefront_Index_y + 1
        
        # AWAY WAVEFRONTS
        # ================
        # Set Index for Away wavefronts in Sparse array
        # (will be one ahead of returning) 
        Wavefront_Index_x = 2*(layer_number+1)-1
        Wavefront_Index_y = 0
        
        while len(Wavefronts_Away_deque)> 0:
            # get an away wavefront in the away wavefront deque
            # (will be inductive)
            temp_wavefront_inductive = Wavefronts_Away_deque.popleft()
            # Generate and store its returning children
            temp_wavefront_inductive.generate_and_store(Wavefronts_Returning_deque)
            # store processed away wavefront
            Wavefronts_Away[Wavefront_Index_x, Wavefront_Index_y] = temp_wavefront_inductive
            # shift index
            Wavefront_Index_x = Wavefront_Index_x - 1
            Wavefront_Index_y = Wavefront_Index_y + 1
            
            # Get the next Away wavefront 
            # (will be capacitive)
            temp_wavefront_capacitve = Wavefronts_Away_deque.popleft()
            # Generate and store its returning children
            temp_wavefront_capacitve.generate_and_store(Wavefronts_Returning_deque)
            # store processed away wavefront
            Wavefronts_Away[Wavefront_Index_x, Wavefront_Index_y] = temp_wavefront_capacitve
            # shift index
            Wavefront_Index_x = Wavefront_Index_x - 1
            Wavefront_Index_y = Wavefront_Index_y + 1

    # POST PORCESSING OF SPARSE ARRAY
    # ===============================
    
    for layer_number in range(0,Data_Input.Number_of_Layers):
        # Get major grid node coords for first node in layer
        Sparse_Major_Node_Index_x = 2*layer_number
        Sparse_Major_Node_Index_y = 0
        
        Dense_Major_Node_Index_x = layer_number
        Dense_Major_Node_Index_y = 0
        
        for node_number in range(0,layer_number+1):
            # Get indexes of surrounding wavefronts
            # -------------------------------------
            # AWAY FROM major grid node inductive wavefront index:
            Away_Index_Inductor_x = Sparse_Major_Node_Index_x + 1
            Away_Index_Inductor_y = Sparse_Major_Node_Index_y
            wavefront_sending_inductor = Wavefronts_Away[Away_Index_Inductor_x,Away_Index_Inductor_y]
            # RETURNING TO major grid node inductive wavefront index:
            Return_Index_Inductor_x = Sparse_Major_Node_Index_x - 1
            Return_Index_Inductor_y = Sparse_Major_Node_Index_y
            wavefront_returning_inductor = Wavefronts_Return[Return_Index_Inductor_x,Return_Index_Inductor_y]
            
            # AWAY FROM major grid node capacitive wavefront index:
            Away_Index_Capacitor_x = Sparse_Major_Node_Index_x 
            Away_Index_Capacitor_y = Sparse_Major_Node_Index_y + 1
            wavefront_sending_capacitor = Wavefronts_Away[Away_Index_Capacitor_x,Away_Index_Capacitor_y]
            # RETURNING TO major grid node capacitive wavefront index:
            Return_Index_Capacitor_x = Sparse_Major_Node_Index_x 
            Return_Index_Capacitor_y = Sparse_Major_Node_Index_y - 1
            wavefront_returning_capacitor = Wavefronts_Return[Return_Index_Capacitor_x,Return_Index_Capacitor_y]
            
            # store AWAY wavefronts in major node position ("away from")
            Time[Dense_Major_Node_Index_x,Dense_Major_Node_Index_y] = wavefront_sending_inductor.time_start
            Wavefronts_Sending_Inductor[Dense_Major_Node_Index_x,Dense_Major_Node_Index_y] = wavefront_sending_inductor
            Wavefronts_Sending_Capacitor[Dense_Major_Node_Index_x,Dense_Major_Node_Index_y] = wavefront_sending_capacitor
            # store RETURNING wavefronts in major node position (also "away from")
            # (returning wavefronts are stored in assoicated to the their AWAY wavefront parents major grid node)
            # (this is not the same as the RETURNING TO format used to calculate interconncet changes)
            Wavefronts_Returning_Inductor[Dense_Major_Node_Index_x,Dense_Major_Node_Index_y] = Wavefronts_Return[Away_Index_Inductor_x,Away_Index_Inductor_y]
            Wavefronts_Returning_Capacitor[Dense_Major_Node_Index_x,Dense_Major_Node_Index_y] = Wavefronts_Return[Away_Index_Capacitor_x,Away_Index_Capacitor_y]

            if(node_number == 0 and layer_number ==0): 
                    # origin node
                    # inductor interconncet magnitude for origin node has only a sent wavefront to consider
                    Voltage_Interconnect_Inductor[Dense_Major_Node_Index_x,Dense_Major_Node_Index_y] = wavefront_sending_inductor.magnitude_voltage 
                    Current_Interconnect_Inductor[Dense_Major_Node_Index_x,Dense_Major_Node_Index_y] = wavefront_sending_inductor.magnitude_current
                    
                    # capacitor interconncet magnitude for origin node has only a sent wavefront to consider
                    Voltage_Interconnect_Capacitor[Dense_Major_Node_Index_x,Dense_Major_Node_Index_y] = wavefront_sending_capacitor.magnitude_voltage 
                    Current_Interconnect_Capacitor[Dense_Major_Node_Index_x,Dense_Major_Node_Index_y] = wavefront_sending_capacitor.magnitude_current

            elif(node_number == 0 ): 
                    # first node is an INDUCTIVE UNIQUE NODE
                    # inductor interconnect magnitudes of inductive unique nodes are affected by both returning and arriving inductive wavefronts
                    Voltage_Interconnect_Inductor[Dense_Major_Node_Index_x,Dense_Major_Node_Index_y] = (wavefront_sending_inductor.magnitude_voltage  + wavefront_returning_inductor.magnitude_voltage) 
                    Current_Interconnect_Inductor[Dense_Major_Node_Index_x,Dense_Major_Node_Index_y] = (wavefront_sending_inductor.magnitude_current + wavefront_returning_inductor.magnitude_current ) 
                    
                    # capacitor interconnect magnitudes of inductive unique nodes are only affected by wavefronts sent into the capaitor
                    Voltage_Interconnect_Capacitor[Dense_Major_Node_Index_x,Dense_Major_Node_Index_y] = wavefront_sending_capacitor.magnitude_voltage 
                    Current_Interconnect_Capacitor[Dense_Major_Node_Index_x,Dense_Major_Node_Index_y] = wavefront_sending_capacitor.magnitude_current

            elif(node_number == layer_number): 
                    # last node is a CAPACITVE UNIQUE NODE
                    # inductor interconnect magnitudes of capacitive unique nodes are only affected by wavefronts sent into the inductor
                    Voltage_Interconnect_Inductor[Dense_Major_Node_Index_x,Dense_Major_Node_Index_y] = wavefront_sending_inductor.magnitude_voltage  
                    Current_Interconnect_Inductor[Dense_Major_Node_Index_x,Dense_Major_Node_Index_y] = wavefront_sending_inductor.magnitude_current
                    
                    # capacitor interconnect magnitudes of capcitive unique nodes are affected by both returning and arriving capacitor wavefronts
                    Voltage_Interconnect_Capacitor[Dense_Major_Node_Index_x,Dense_Major_Node_Index_y] = (wavefront_sending_capacitor.magnitude_voltage  + wavefront_returning_capacitor.magnitude_voltage) 
                    Current_Interconnect_Capacitor[Dense_Major_Node_Index_x,Dense_Major_Node_Index_y] = (wavefront_sending_capacitor.magnitude_current + wavefront_returning_capacitor.magnitude_current )
            else:
                    # general node
                    # interconnect values of the inductor for general nodes are a sum of both sending and returning wavefronts
                    Voltage_Interconnect_Inductor[Dense_Major_Node_Index_x,Dense_Major_Node_Index_y] = (wavefront_sending_inductor.magnitude_voltage  + wavefront_returning_inductor.magnitude_voltage) 
                    Current_Interconnect_Inductor[Dense_Major_Node_Index_x,Dense_Major_Node_Index_y] = (wavefront_sending_inductor.magnitude_current + wavefront_returning_inductor.magnitude_current ) 
                    
                    # interconnect values of the capacitor for general nodes are a sum of both sending and returning wavefronts
                    Voltage_Interconnect_Capacitor[Dense_Major_Node_Index_x,Dense_Major_Node_Index_y] = (wavefront_sending_capacitor.magnitude_voltage  + wavefront_returning_capacitor.magnitude_voltage)
                    Current_Interconnect_Capacitor[Dense_Major_Node_Index_x,Dense_Major_Node_Index_y] = (wavefront_sending_capacitor.magnitude_current + wavefront_returning_capacitor.magnitude_current )
            
            # update index and go to next layer     
            Sparse_Major_Node_Index_x -= 2
            Sparse_Major_Node_Index_y += 2
            
            Dense_Major_Node_Index_x -= 1
            Dense_Major_Node_Index_y += 1
    
    return Data_Output_Storage(
        Time, # Merge Times
        Voltage_Interconnect_Inductor, # Values at interconnect 
        Current_Interconnect_Inductor, # Values at interconnect
        Voltage_Interconnect_Capacitor, # Values at interconnect
        Current_Interconnect_Capacitor, # Values at interconnect
        Wavefronts_Sending_Inductor, # Specific Wavefronts at Nodes
        Wavefronts_Sending_Capacitor, # Specific Wavefronts at Nodes
        Wavefronts_Returning_Inductor, # Specific Wavefronts at Nodes
        Wavefronts_Returning_Capacitor, # Specific Wavefronts at Nodes
        False, # indicated that multiplicative merging has not occured
        )

def multiplicative_merge_single_cycle(input_array:np.ndarray,Inductor_LCM_Factor:int,Capacitor_LCM_Factor:int):
    """Completes a single merging cycle of a mangitude fanout along its first (inductive) axis.

    :param input_array: An output array from Datat_Output_Storage class., i.e. data_output.Voltage_Interconnect_Inductor
    :type input_array: np.ndarray
    :param Inductor_LCM_Factor: The co-factor of the time-delay for the inductor, KL. KL x TL = LCM(TL,TC)
    :type Inductor_LCM_Factor: int
    :param Capacitor_LCM_Factor: The co-factor of the time-delay for the capacitor axis, KC. KC x TC = LCM(TL,TC)
    :type Capacitor_LCM_Factor: int
    :return: returns the input_array after one more subsequent merging cycle.
    :rtype: np.ndarray
    """
    
    def make_upper_and_lower(input_array,Capacitor_LCM_Factor):
        upper_array : np.ndarray = input_array[:,0:Capacitor_LCM_Factor]
        lower_array : np.ndarray = input_array[:,Capacitor_LCM_Factor:]
        
        padding_array_for_upper : np.ndarray = np.full(lower_array.shape,0,dtype=lower_array.dtype)
        padding_array_for_lower : np.ndarray = np.full(upper_array.shape,0,dtype=upper_array.dtype)
        
        upper_array= np.append(upper_array,padding_array_for_upper,axis=1)
        lower_array= np.append(lower_array,padding_array_for_lower,axis=1)
        
        return upper_array,lower_array
    
    def shif_and_pad_array_x(input_array,number_lines):
    
        rolled_array : np.ndarray = np.roll(input_array, number_lines, axis=0)
        
        left_array : np.ndarray = rolled_array[0:number_lines,:]
        left_array : np.ndarray = np.full(left_array.shape,0,dtype=left_array.dtype)
        
        
        rolled_array : np.ndarray= np.delete(rolled_array,np.arange(0,number_lines,1),axis=0)
        rolled_array : np.ndarray = np.append(left_array,rolled_array,axis=0)
        
        return rolled_array 
    
    upper_array,lower_array = make_upper_and_lower(input_array,Capacitor_LCM_Factor)
    array_merge_ready = shif_and_pad_array_x(lower_array,Inductor_LCM_Factor)
    
    array_merged = upper_array + array_merge_ready
    
    return array_merged

def multiplicative_merging(input_array:np.ndarray,Inductor_LCM_Factor:int ,Capacitor_LCM_Factor:int ,number_of_layers:int):
    number_merge_cycles:int = math.ceil(number_of_layers/Capacitor_LCM_Factor) + 1
    
    for _ in range (0,number_merge_cycles):
        input_array:np.ndarray = multiplicative_merge_single_cycle(input_array,Inductor_LCM_Factor,Capacitor_LCM_Factor)

    return input_array[:,0:Capacitor_LCM_Factor]

def Higher_Order_Merging(Data_Inputs : Data_Input_Storage,Data_Outputs : Data_Output_Storage):
    Data_Outputs = copy.deepcopy(Data_Outputs)
    
    if(Data_Inputs.is_Higher_Merging):
        Voltage_Interconnect_Inductor_merged = multiplicative_merging(Data_Outputs.Voltage_Interconnect_Inductor,Data_Inputs.Inductor_LCM_Factor,Data_Inputs.Capacitor_LCM_Factor,Data_Inputs.Number_of_Layers)
        Current_Interconnect_Inductor_merged = multiplicative_merging(Data_Outputs.Current_Interconnect_Inductor,Data_Inputs.Inductor_LCM_Factor,Data_Inputs.Capacitor_LCM_Factor,Data_Inputs.Number_of_Layers)
        
        Voltage_Interconnect_Capacitor_merged = multiplicative_merging(Data_Outputs.Voltage_Interconnect_Capacitor,Data_Inputs.Inductor_LCM_Factor,Data_Inputs.Capacitor_LCM_Factor,Data_Inputs.Number_of_Layers)
        Current_Interconnect_Capacitor_merged = multiplicative_merging(Data_Outputs.Current_Interconnect_Capacitor,Data_Inputs.Inductor_LCM_Factor,Data_Inputs.Capacitor_LCM_Factor,Data_Inputs.Number_of_Layers)
        
        Wavefronts_Sending_Inductor_merged = multiplicative_merging(Data_Outputs.Wavefronts_Sending_Inductor,Data_Inputs.Inductor_LCM_Factor,Data_Inputs.Capacitor_LCM_Factor,Data_Inputs.Number_of_Layers)
        Wavefronts_Sending_Capacitor_merged = multiplicative_merging(Data_Outputs.Wavefronts_Sending_Capacitor,Data_Inputs.Inductor_LCM_Factor,Data_Inputs.Capacitor_LCM_Factor,Data_Inputs.Number_of_Layers)

        Wavefronts_Returning_Inductor_merged = multiplicative_merging(Data_Outputs.Wavefronts_Returning_Inductor,Data_Inputs.Inductor_LCM_Factor,Data_Inputs.Capacitor_LCM_Factor,Data_Inputs.Number_of_Layers)
        Wavefronts_Returning_Capacitor_merged = multiplicative_merging(Data_Outputs.Wavefronts_Returning_Capacitor,Data_Inputs.Inductor_LCM_Factor,Data_Inputs.Capacitor_LCM_Factor,Data_Inputs.Number_of_Layers)
        
        Time_cut = Data_Outputs.Time[:,0:Data_Inputs.Capacitor_LCM_Factor]
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
        Wavefronts_Returning_Capacitor_merged ,
        True # indicates Higher order merging has occured
    )

def Order_Data_Output_Merged(Data_Input : Data_Input_Storage , Data_Output_Merged : Data_Output_Storage):
    
    if (Data_Output_Merged.has_merged == False):
        raise warnings.warn("Provided Data_Output_Storage object to be ordered has not been merged yet. This can produce incorrect results if merging is not accounted for.")
    
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
    
    # Orderded self Structure
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

    while latest_time < Data_Input.Simulation_Stop_Time:
        
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
        True ,
        out_indexes
    )        

def Full_Cycle(**input_values):
    
    data_input = Data_Input_Storage(**input_values)
    data_output_commutative = Generate_Wavefronts_Commutatively(data_input)
    data_output_merged = Higher_Order_Merging(data_input,data_output_commutative)
    data_output_ordered = Order_Data_Output_Merged(data_input,data_output_merged)
    
    return Interface_Data(data_input,data_output_commutative,data_output_merged,data_output_ordered)

