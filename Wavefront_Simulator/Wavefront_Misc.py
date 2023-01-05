import numpy as np
from decimal import Decimal
    
def split_and_translate_to_L_axis(input_array : np.ndarray ,C_value : int):
    """The first step in the recursive merging process.
    Seperates the input array into two arrays along the line C = C_value, this line is parallel to the L-axis.
    Both arrays are padded with 'zeros' such that the shape of the input array is maintained. 
    The split array touching the origin and the L-axis will be padded such that it is 'stationary',
    The other array will be shifted to the origin along the L-axis with the padding is 'ontop'.

    :param input_array: array to be split.
    :type input_array: np.ndarray
    :param C_value: The value on the C-axis in which the array is split in two. Typically this is C = KC such as to divide along multiplicative merging region boundary.
    :type C_value: int
    :return: Stationary and Translated arrays in that order.
    :rtype: tuple( np.ndarray , np.ndarray )
    """
    
    # split arrays
    stationary_array : np.ndarray = input_array[:,0:C_value]
    translated_array : np.ndarray = input_array[:,C_value:]

    # generate padding such that when appended input shape is maintianed
    padding_array_for_stationary : np.ndarray = np.full(translated_array.shape,0,dtype=translated_array.dtype)
    padding_array_for_translated : np.ndarray = np.full(stationary_array.shape,0,dtype=stationary_array.dtype)
    
    # append paddding such that there is a 'translation' for the translated array
    stationary_array= np.append(stationary_array,padding_array_for_stationary,axis=1)
    translated_array= np.append(translated_array,padding_array_for_translated,axis=1)
    
    return stationary_array,translated_array

def translate_along_L_axis(input_array : np.ndarray , L_value : int ):
    """The second step in the recursive merigng process.
    Shifts an array L_value units along the L-axis, and pads it with zeros so that the input shape is maintained.

    :param input_array: array to be translated.
    :type input_array: np.ndarray
    :param L_value: the extent to which the array is shifted.
    :type L_value: int
    :return: the shifted array.
    :rtype: np.ndarray
    """
    
    # isolate relevant remaining portion
    split_array = input_array[0:-L_value,:]
    # generate padding
    padding_array = np.full((L_value, input_array.shape[1]), 0, dtype = input_array.dtype)
    # combine with padding first as to shift the array
    shifted_array = np.append(padding_array, split_array, axis=0)
    
    return shifted_array

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
