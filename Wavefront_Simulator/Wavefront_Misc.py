import numpy as np
    
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