from decimal import Decimal
import math
from collections import deque
import numpy as np
from dataclasses import dataclass

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

class Data_Input_Storage :
    """The storage object for the input varibles of a interface simulation. Calculates all the associated variables required for the simulaitons. 
        Can be used to investigate network calcualted parameters based off input vairbles. 
        It also stores and calculates all the interaction functions of the interface.

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
    
    def Self_Reflection_Event_Solver_Inductor(self,Wavefront_Parent_voltage: Decimal,Wavefront_Parent_current: Decimal):
        """Calculates the voltage and current magnitude of a produced inductive wavefront due to an inductive self-reflection event. 
        A self-reflection event is when a wavefron form a transmission line arrives at the interface and is reflected back into itself.
        The Parent wavefront's parameters are passed to this function, the self reflected child wavefront magnitudes are calculated.
        
        :param Wavefront_Parent_voltage: voltage of the parent wavefront arriving at the interface
        :type Wavefront_Parent_voltage: Decimal
        :param Wavefront_Parent_current: current of the parent wavefront arriving at the interface
        :type Wavefront_Parent_current: Decimal
        :return: (voltage, current ) of child wavefront
        :rtype: Tuple
        """
        magnitude_voltage = self.Circuit_Solver_Inductor_Voltage( Wavefront_Parent_voltage, Wavefront_Parent_current, 0, 0)
        magnitude_current = self.Circuit_Solver_Inductor_Current( Wavefront_Parent_voltage, Wavefront_Parent_current, 0, 0)
        
        return magnitude_voltage, magnitude_current
    
    def Exitation_Event_Solver_Inductor(self,Wavefront_Parent_voltage : Decimal,Wavefront_Parent_current : Decimal):
        """The voltage and current calcualtion of the inducitve wavefront produced due to a source excitation event.

        :param Wavefront_Parent_voltage: voltage of the source excitation wavefront 
        :type Wavefront_Parent_voltage: Decimal
        :param Wavefront_Parent_current: current of the source excitation wavefront 
        :type Wavefront_Parent_current: Decimal
        :return: (voltage, current) of the produced inductive wavefront 
        :rtype: Tuple (Decimal, Decimal)
        """
        magnitude_voltage = self.Circuit_Solver_Inductor_Source_Voltage(Wavefront_Parent_voltage)
        magnitude_current = self.Circuit_Solver_Inductor_Source_Current(Wavefront_Parent_voltage)
        
        return magnitude_voltage, magnitude_current

    def Transmission_Event_Solver_Inductor(self,Wavefront_Parent_voltage : Decimal,Wavefront_Parent_current : Decimal):
        """The voltage and current calculation of the inductive wavefront produced due to a capacitve wavefront arriving at the interface.

        :param Wavefront_Parent_voltage: voltage of the incident capacitve wavefront
        :type Wavefront_Parent_voltage: Decimal
        :param Wavefront_Parent_current: current of the incident capacitve wavefront
        :type Wavefront_Parent_current: Decimal
        :return: (voltage, current) of the produced inductive wavefront 
        :rtype: Tuple (Decimal, Decimal)
        """
        magnitude_voltage = self.Circuit_Solver_Inductor_Voltage(0, 0, Wavefront_Parent_voltage, Wavefront_Parent_current)
        magnitude_current = self.Circuit_Solver_Inductor_Current(0, 0, Wavefront_Parent_voltage, Wavefront_Parent_current)
        
        return magnitude_voltage, magnitude_current

    def Termination_Event_Solver_Inductor(self,Arriving_Voltage: Decimal,Arriving_Current: Decimal):
        """The voltage and current calcutation of the re-reflected wavefront produced when an inductive wavefront reaches its termination.

        :param Arriving_Voltage: voltage of the wavefront arriving at the inductor termination
        :type Arriving_Voltage: Decimal
        :param Arriving_Current: current of the wavefront arriving at the inductor termination
        :type Arriving_Current: Decimal
        :return: (voltage, current) of the re-reflected inductive wavefront
        :rtype: Tuple (Decimal, Decimal)
        """
        return -Arriving_Voltage, Arriving_Current

    def Self_Reflection_Event_Solver_Capacitor(self,Wavefront_Parent_voltage: Decimal,Wavefront_Parent_current: Decimal):
        """Calculates the voltage and current magnitude of a produced capcaitve wavefront due to a capacitve self-reflection event. 
        A self-reflection event is when a wavefront form a transmission line arrives at the interface and is reflected back into itself.
        The Parent wavefront's parameters are passed to this function, the self reflected child wavefront magnitudes are calculated.

        :param Wavefront_Parent_voltage: voltage of the parent wavefront arriving at the interface
        :type Wavefront_Parent_voltage: Decimal
        :param Wavefront_Parent_current: current of the parent wavefront arriving at the interface
        :type Wavefront_Parent_current: Decimal
        :return: (voltage, current ) of child wavefront
        :rtype: Tuple
        """
        magnitude_voltage = self.Circuit_Solver_Capacitor_Voltage( 0,0,Wavefront_Parent_voltage, Wavefront_Parent_current)
        magnitude_current = self.Circuit_Solver_Capacitor_Current( 0,0,Wavefront_Parent_voltage, Wavefront_Parent_current)
        
        return magnitude_voltage, magnitude_current
    
    def Exitation_Event_Solver_Capacitor(self,Wavefront_Parent_voltage : Decimal,Wavefront_Parent_current : Decimal):
        """The voltage and current calcualtion of the capacitive wavefront produced due to a source excitation event.

        :param Wavefront_Parent_voltage: voltage of the source excitation wavefront 
        :type Wavefront_Parent_voltage: Decimal
        :param Wavefront_Parent_current: current of the source excitation wavefront 
        :type Wavefront_Parent_current: Decimal
        :return: (voltage, current) of the produced capacitive wavefront 
        :rtype: Tuple (Decimal, Decimal)
        """     
        magnitude_voltage = self.Circuit_Solver_Capacitor_Source_Voltage(Wavefront_Parent_voltage)
        magnitude_current = self.Circuit_Solver_Capacitor_Source_Current(Wavefront_Parent_voltage)
        
        return magnitude_voltage, magnitude_current

    def Transmission_Event_Solver_Capacitor(self,Wavefront_Parent_voltage : Decimal,Wavefront_Parent_current : Decimal):
        """The voltage and current calculation of the capacitve wavefront produced due to a inductive wavefront arriving at the interface.

        :param Wavefront_Parent_voltage: voltage of the incident inductive wavefront
        :type Wavefront_Parent_voltage: Decimal
        :param Wavefront_Parent_current: current of the incident inductive wavefront
        :type Wavefront_Parent_current: Decimal
        :return: (voltage, current) of the produced capacitve wavefront 
        :rtype: Tuple (Decimal, Decimal)
        """    
        magnitude_voltage = self.Circuit_Solver_Capacitor_Voltage(Wavefront_Parent_voltage, Wavefront_Parent_current,0,0)
        magnitude_current = self.Circuit_Solver_Capacitor_Current(Wavefront_Parent_voltage, Wavefront_Parent_current,0,0)
        
        return magnitude_voltage, magnitude_current

    def Termination_Event_Solver_Capacitor(self,Arriving_Voltage: Decimal,Arriving_Current: Decimal):
        """The voltage and current calcutation of the re-reflected wavefront produced when a capacitve wavefront reaches its termination.

        :param Arriving_Voltage: voltage of the wavefront arriving at the capcitor termination
        :type Arriving_Voltage: Decimal
        :param Arriving_Current: current of the wavefront arriving at the capcitor termination
        :type Arriving_Current: Decimal
        :return: (voltage, current) of the re-reflected capacitve wavefront
        :rtype: Tuple (Decimal, Decimal)
        """
        return Arriving_Voltage, -Arriving_Current
    
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

class Wavefront:
    """Base wavefront class. Assings basic wavefront parameters, all of Decimal type initialised to zero.
    """
    def __init__(self):

        self.position_start = Decimal('0')
        self.position_end = Decimal('0')

        self.time_start = Decimal('0')
        self.time_end = Decimal('0')

        self.magnitude_voltage = Decimal('0')
        self.magnitude_current = Decimal('0')
        
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
        """add operation but for RHS. same as __add__
        """
        return self.__add__(Wavefront_add)
        
    def about(self) :
        """Displays information anout the wavefront
        """
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

class Wavefront_Source(Wavefront):
    """Class representing switiching wavefronts of the voltage source. 
    In this release wavefonts switching is not supported, 
    this class used to initiated wavefronts at t=0 only. 
    """

    def __init__(self, Data_input: Data_Input_Storage,time_start, magnitude = 1  ):
        """intialised the wavefront.

        :param magnitude: Source magnitude
        :type magnitude: str or Decimal
        :param time_start: start of pulse
        :type time_start: str or Decimal
        """
        super().__init__()
        self.Data_input = Data_input

        self.time_start = Decimal(time_start)
        self.time_end = self.time_start
        self.magnitude_voltage = Decimal(magnitude)

    def generate_and_store(self, Wavefront_Storage_Away : deque):
        """triggers the creation of the inital wavefronts in the inductor and capacitor. 
        Stores them in the Wavefront_Storage. Order is important, inductive first followed by capacitive. 

        :param Wavefront_Storage: Storage array for away waves
        :type Wavefront_Storage: deque
        """
        Wavefront_Storage_Away.append(Wavefront_Inductive(self.Data_input,self,False))
        Wavefront_Storage_Away.append(Wavefront_Capacitive(self.Data_input,self,False))
   
class Wavefront_Kintetic( Wavefront ):
    """An parent class for Inductive and Capacitve wavefronts. Contains the logic for determining how wavefronts respond to particualr events.
    """
    def setup_Wavefront(self,Wavefront_Parent : Wavefront, is_self_reflection : bool):
        """handles how the voltage and current of a newly produced wavefront must be assigned. 

        :param Wavefront_Parent: The Parent wavefront that is producing this wavefronts
        :type Wavefront_Parent: Wavefront
        :param is_self_reflection: if the parent wavefront is in the same wavefront as the child. Limits the need for an isinstance check.
        :type is_self_reflection: bool
        """
        # key:
        # | = interface,  X = termination, --> = this wavefront ,(Vs) = Source excitation
        
        #               waves travelling to termination : | --> X
        #    | --> X  = this wavefront travelling to termination, parent from same tx - self-reflection
        # (v)| --> X  = this wavefront travelling to termination, parent is voltage source - source excitation
        #  ->| --> X  = this wavefront travelling to termination, parent from other tx - transmission
        
        #               waves returning to interface : | <-- X
        #    | <-- X  = this wavefront returning to inerface, parent from same - re-reflection
        
        # waves travelling to termination : | --> X
        if self.position_start == 0:

            # was the parent wavefront in the same transmission line?
            if is_self_reflection: # Yes, | --> X , self-reflection

                self.magnitude_voltage,self.magnitude_current  = self.Self_Reflection_Event_Solver(Wavefront_Parent.magnitude_voltage,Wavefront_Parent.magnitude_current)

            # was the parent wavefront an excitation event ? 
            elif isinstance(Wavefront_Parent, Wavefront_Source) : # (v)| --> X , source excitation

                self.magnitude_voltage,self.magnitude_current = self.Exitation_Event_Solver(Wavefront_Parent.magnitude_voltage,Wavefront_Parent.magnitude_current)

            else: # A transmitted wave at source side  ->| --> X, transmission

                self.magnitude_voltage,self.magnitude_current = self.Transmission_Event_Solver(Wavefront_Parent.magnitude_voltage,Wavefront_Parent.magnitude_current)
        
        # waves returning to interface : | <-- X , re-reflection
        else: 
            self.magnitude_voltage,self.magnitude_current = self.Termination_Event_Solver(Wavefront_Parent.magnitude_voltage,Wavefront_Parent.magnitude_current)
    
    def Merge(self, Wavefront_Other : Wavefront):
        """superimposes two wavefronts by altering the voltage and current magnitudes of this wavefront.

        :param Wavefront_Other: Partner Wavefront to be merging 
        :type Wavefront_Other: Wavefront
        """
        self.magnitude_voltage = self.magnitude_voltage + Wavefront_Other.magnitude_voltage
        self.magnitude_current = self.magnitude_current + Wavefront_Other.magnitude_current

    def Self_Reflection_Event_Solver(self,Wavefront_Parent_voltage,Wavefront_Parent_current):
        pass
    
    def Exitation_Event_Solver(self,Wavefront_Parent_voltage,Wavefront_Parent_current):
        pass
    
    def Transmission_Event_Solver(self,Wavefront_Parent_voltage,Wavefront_Parent_current):
        pass
    
    def Termination_Event_Solver(self,Wavefront_Parent_voltage,Wavefront_Parent_current):
        pass

class Wavefront_Capacitive( Wavefront_Kintetic ):
    """
    A wavefront travelling in the capacitor. Follows the "wavefronts create wavefronts" paradigm. 
    """

    def __init__(self, Data_Input : Data_Input_Storage, Wavefront_Parent : Wavefront, is_self_reflection : bool):
        """
        Generates a capacitive wavefront based off the information of the parent wavefront. 

        :param Data_Input: the input paramaters of the interface being investigated.
        :type Data_Input: Data_Input_Storage
        :param Wavefront_Parent: the parent wavefront producing this wavefront
        :type Wavefront_Parent: Wavefront
        :param is_self_reflection: if the parent wavefront is in the same wavefront as the child. Limits the need for an isinstance check.
        :type is_self_reflection: bool
        """
        self.Data_Input = Data_Input
        
        self.position_start = Wavefront_Parent.position_end
        
        if self.position_start == 0:
            self.position_end = self.Data_Input.Capacitor_Length
        else:
            self.position_end = 0
        
        self.time_start = Wavefront_Parent.time_end
        self.time_end = self.time_start + self.Data_Input.Capacitor_Time
        
        self.velocity = self.Data_Input.Capacitor_Velocity
        self.length = self.Data_Input.Capacitor_Length
        
        self.magnitude_voltage = 0
        self.magnitude_current = 0
        
        self.Self_Reflection_Event_Solver = self.Data_Input.Self_Reflection_Event_Solver_Capacitor
        self.Exitation_Event_Solver = self.Data_Input.Exitation_Event_Solver_Capacitor
        self.Transmission_Event_Solver = self.Data_Input.Transmission_Event_Solver_Capacitor
        self.Termination_Event_Solver = self.Data_Input.Termination_Event_Solver_Capacitor

        self.setup_Wavefront(Wavefront_Parent,is_self_reflection)

    def generate_and_store(self, Wavefront_Storage : deque):
        """Generates and stores wavefronts the childern wavefront in a que to be processed

        :param Wavefront_Storage: The deque of wavefronts that are actively being processed
        :type Wavefront_Storage: deque
        """
        if self.position_end == 0:
            Wavefront_Storage.append(Wavefront_Inductive(self.Data_Input,self,False))
            Wavefront_Storage.append(Wavefront_Capacitive(self.Data_Input,self,True))
        else:
            Wavefront_Storage.append(Wavefront_Capacitive(self.Data_Input,self,True))
    
    def generate_and_return(self):
        """Generates the children wavefront/s of this wavefront without directly storing them. 

        :return: children wavefront/s
        :rtype: Tuple (Wavefront_Inductive, Wavefront_Capacitive) or Wavefront_Capacitive
        """
        if self.position_end == 0:
            return Wavefront_Inductive(self.Data_Input,self,False), Wavefront_Capacitive(self.Data_Input,self,True)
        else :
            return Wavefront_Capacitive(self.Data_Input,self,self.Data_Input,True)

class Wavefront_Inductive( Wavefront_Kintetic ):
    """
    A wavefront travelling in the inductor. Follows the "wavefronts create wavefronts" paradigm. 
    """
    def __init__(self, Data_Input : Data_Input_Storage, Wavefront_Parent : Wavefront, is_self_reflection : bool):
        """
        Generates a inductive wavefront based off the information of the parent wavefront. 

        :param Data_Input: the input paramaters of the interface being investigated.
        :type Data_Input: Data_Input_Storage
        :param Wavefront_Parent: the parent wavefront producing this wavefront
        :type Wavefront_Parent: Wavefront
        :param is_self_reflection: if the parent wavefront is in the same wavefront as the child. Limits the need for an isinstance check.
        :type is_self_reflection: bool
        """
        
        self.Data_Input = Data_Input
        
        self.position_start = Wavefront_Parent.position_end
        
        if self.position_start == 0:
            self.position_end = self.Data_Input.Inductor_Length
        else:
            self.position_end = 0
        
        self.time_start = Wavefront_Parent.time_end
        self.time_end = self.time_start + self.Data_Input.Inductor_Time
        
        self.velocity = self.Data_Input.Inductor_Velocity
        self.length = self.Data_Input.Inductor_Length
        
        self.magnitude_voltage = 0
        self.magnitude_current = 0
        
        self.Self_Reflection_Event_Solver = self.Data_Input.Self_Reflection_Event_Solver_Inductor
        self.Exitation_Event_Solver = self.Data_Input.Exitation_Event_Solver_Inductor
        self.Transmission_Event_Solver = self.Data_Input.Transmission_Event_Solver_Inductor
        self.Termination_Event_Solver = self.Data_Input.Termination_Event_Solver_Inductor

        self.setup_Wavefront(Wavefront_Parent,is_self_reflection)

    def generate_and_store(self, Wavefront_Storage):
        """Generates and stores wavefronts the childern wavefront in a que to be processed

        :param Wavefront_Storage: The deque of wavefronts that are actively being processed
        :type Wavefront_Storage: deque
        """
        if self.position_end == 0:
            Wavefront_Storage.append(Wavefront_Inductive(self.Data_Input,self,True))
            Wavefront_Storage.append(Wavefront_Capacitive(self.Data_Input,self,False))
        else :
            Wavefront_Storage.append(Wavefront_Inductive(self.Data_Input,self,True))

    def generate_and_return(self):
        """Generates the children wavefront/s of this wavefront without directly storing them. 

        :return: children wavefront/s
        :rtype: Tuple (Wavefront_Inductive, Wavefront_Capacitive) or Wavefront_Inductive
        """
        if self.position_end == 0:
            return Wavefront_Inductive(self.Data_Input,self,True), Wavefront_Capacitive(self.Data_Input,self,False)
        else :
            return Wavefront_Inductive(self.Data_Input,self,True)


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
    """A dataclass that stores ordered inteface output data in form of single dimenstional arrays. 
    All the core arrays that are present in the Data_Output_Storage class are present here but in a one-dimensional chronological form.
    
    :param Indexes: An additonal array, indicating the grid co-ordiantes on the merged fanout structure in the order events occured. 
        Is a single dimesional list of (L,C) coordiante lists. The inner lists take form of [L,C].
    :type Indexes: List[Lists]
    """
    Indexes : np.ndarray

@dataclass
class Data_Interface_Storage:
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
    :return: merged array aligned to the C-axis
    :rtype: np.ndarray[Decimal]
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

