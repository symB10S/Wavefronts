from decimal import *
from collections import deque
import numpy as np
import math
import copy
import warnings
from Wavefront_Storage import *
from Wavefront_Misc import *

getcontext().traps[FloatOperation] = True

def Generate_Wavefronts_Commutatively(Data_Input : Data_Input_Storage):
    """Generates a Data_Output_Storage object from the calculated input variables stored in a Data_Input_Storage object. 
    
    :param Data_Input: Input data object containing simulation input variables
    :type Data_Input: Data_Input_Storage
    :return: output data (a collection commutative fanouts in form of np.ndarrays)
    :rtype: Data_Output_Storage
    
    Resposible for generating wavefronts and simultaneously commutatively merging the wavefronts. 
    The simaltaneous commutative merging of wavefronts is mandatory for longer simulation times.
    """
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
    Wavefronts_Away = np.full((2*(Data_Input.Number_of_Layers+1),2*(Data_Input.Number_of_Layers+1)),Wavefront_Source(Data_Input,0,0))
    Wavefronts_Return = np.full((2*(Data_Input.Number_of_Layers+1),2*(Data_Input.Number_of_Layers+1)),Wavefront_Source(Data_Input,0,0))
    
    
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
    
    Wavefronts_Sending_Inductor = np.full(((Data_Input.Number_of_Layers+1),(Data_Input.Number_of_Layers+1)), Wavefront())
    Wavefronts_Sending_Capacitor = np.full(((Data_Input.Number_of_Layers+1),(Data_Input.Number_of_Layers+1)), Wavefront())
    
    Wavefronts_Returning_Inductor = np.full(((Data_Input.Number_of_Layers+1),(Data_Input.Number_of_Layers+1)), Wavefront())
    Wavefronts_Returning_Capacitor = np.full(((Data_Input.Number_of_Layers+1),(Data_Input.Number_of_Layers+1)), Wavefront())
    
    # POPULATE THE SPARSE STORAGE ARRAYS
    # ===================================
    #Deques of wavefronts thare are used to temporarily store wavefronts as they are being processed.
    Wavefronts_Away_deque : Wavefront = deque()
    Wavefronts_Returning_deque : Wavefront = deque()

    # Generate Intial Away Waves from voltage excitation
    temp_wavefront = Wavefront_Source(Data_Input,0,Data_Input.Voltage_Souce_Magnitude)
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
    """Completes a single merging cycle of a mangitude fanout along the inductive axis.
    A single cycle consitis of splitting -> shift -> merging.

    :param input_array: An output array from Datat_Output_Storage class., i.e. data_output.Voltage_Interconnect_Inductor
    :type input_array: np.ndarray
    :param Inductor_LCM_Factor: The co-factor of the time-delay for the inductor, KL. KL x TL = LCM(TL,TC)
    :type Inductor_LCM_Factor: int
    :param Capacitor_LCM_Factor: The co-factor of the time-delay for the capacitor axis, KC. KC x TC = LCM(TL,TC)
    :type Capacitor_LCM_Factor: int
    :return: returns the input_array after one more subsequent merging cycle.
    :rtype: np.ndarray
    """
    # split arrays along C = Capacitor_LCM_Factor,
    stationary_array,translated_array = split_and_translate_to_L_axis(input_array,Capacitor_LCM_Factor)
    # shift translated array by L = Inductor_LCM_Factor
    array_merge_ready = translate_along_L_axis(translated_array,Inductor_LCM_Factor)
    # merging regions will now be aligned, can now merge. 
    array_merged = stationary_array + array_merge_ready
    
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
    
    return Data_Interface_Storage(data_input,data_output_commutative,data_output_merged,data_output_ordered)

def get_spatial_voltage_current_at_time(Time_Enquriey, Interface : Data_Interface_Storage , is_Inductor : bool):
    
    
    # Exctract wavefront interceptions at a specific time
    # 1. get sending + returning wavefronts
    # 2. determine DC line values
    # 3. get intercept positions, voltages and currents
    
    sending_wavefronts = []
    returning_wavefronts = []
    
    dc_voltage = Decimal('0')
    dc_current = Decimal('0')

    sending_intercept_positions = []
    sending_intercept_voltages = []
    sending_intercept_currents = []

    returning_intercept_positions = []
    returning_intercept_voltages = []
    returning_intercept_currents = []
    
    if(is_Inductor):
        termination_length = Interface.data_input.Inductor_Length
        sending_wavefronts = Interface.data_output_multiplicative.Wavefronts_Sending_Inductor
        returning_wavefronts = Interface.data_output_multiplicative.Wavefronts_Returning_Inductor
    else:
        termination_length = Interface.data_input.Capacitor_Length
        sending_wavefronts = Interface.data_output_multiplicative.Wavefronts_Sending_Capacitor
        returning_wavefronts = Interface.data_output_multiplicative.Wavefronts_Returning_Capacitor

    for index in Interface.data_output_ordered.Indexes:
        x = index[0]
        y = index[1]
        
        # Get sending + returning wavefronts
        sending_wavefront = sending_wavefronts[x,y]
        returning_wavefront = returning_wavefronts[x,y]
        
        # get position intercepts and determine line DC values
        
        # x = time enquirey
        # -s-> = sending wavefront
        # -r-> = returning wavefront
        
        # x-s->-r-> before 
        if(sending_wavefront.time_start > Time_Enquriey): # Finished
            break
        
        # -s->-r->x after
        elif(returning_wavefront.time_end <= Time_Enquriey): # Both DC
            dc_voltage += sending_wavefront.magnitude_voltage
            dc_current += sending_wavefront.magnitude_current
                
            dc_voltage += returning_wavefront.magnitude_voltage
            dc_current += returning_wavefront.magnitude_current
        
        # -s->-x-r-> returning intercept
        elif(returning_wavefront.time_end >= Time_Enquriey and returning_wavefront.time_start < Time_Enquriey): # Returning Intercept, Sending DC
            returning_intercept_positions.append(returning_wavefront.Position_at_time(Time_Enquriey))
            returning_intercept_voltages.append(returning_wavefront.magnitude_voltage)
            returning_intercept_currents.append(returning_wavefront.magnitude_current)
                
            dc_voltage += sending_wavefront.magnitude_voltage
            dc_current += sending_wavefront.magnitude_current
        
        # -x-s->-r-> sending intercept
        elif(sending_wavefront.time_end >= Time_Enquriey and sending_wavefront.time_start <= Time_Enquriey): # Sending Intercept
            sending_intercept_positions.append(sending_wavefront.Position_at_time(Time_Enquriey))
            sending_intercept_voltages.append(sending_wavefront.magnitude_voltage)
            sending_intercept_currents.append(sending_wavefront.magnitude_current)
                
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

    # input sending values in output form, make all DC value, add to inerconnect value
    for i, pos in enumerate(sending_intercept_positions):
        position_all.append(pos)
            
        value_left_voltage.append(dc_voltage)
        value_right_voltage.append(dc_voltage)
        interconnect_value_voltage += sending_intercept_voltages[i]
            
        value_left_current.append(dc_current)
        value_right_current.append(dc_current)
        interconnect_value_current += sending_intercept_currents[i]
            

    # input returning values in output form, make all DC value
    for i, pos in enumerate(returning_intercept_positions):
        position_all.append(pos)
            
        value_left_voltage.append(dc_voltage)
        value_right_voltage.append(dc_voltage)
        termination_value_voltage += returning_intercept_voltages[i]
            
        value_left_current.append(dc_current)
        value_right_current.append(dc_current)
        termination_value_current += returning_intercept_currents[i]
            
        if (pos ==0):
            raise Exception("Returning wavefront at interconnect, problematic")

    # add values left and right
    for i,position in enumerate(position_all):
        for j, send_pos in enumerate(sending_intercept_positions):
            if(send_pos> position):
                value_left_voltage[i] += sending_intercept_voltages[j]
                value_right_voltage[i] += sending_intercept_voltages[j]
                    
                value_left_current[i] += sending_intercept_currents[j]
                value_right_current[i] += sending_intercept_currents[j]
                    
            if (send_pos == position ):
                value_left_voltage[i] += sending_intercept_voltages[j]
                
                value_left_current[i] += sending_intercept_currents[j]
                
        for j, return_pos in enumerate(returning_intercept_positions):
            if(return_pos< position):
                value_left_voltage[i] += returning_intercept_voltages[j]
                value_right_voltage[i] += returning_intercept_voltages[j]
                    
                value_left_current[i] += returning_intercept_currents[j]
                value_right_current[i] += returning_intercept_currents[j]
                    
            if (return_pos == position ):
                value_right_voltage[i] += returning_intercept_voltages[j]
                    
                value_right_current[i] += returning_intercept_currents[j]
                    
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

    # sort values based on position
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
                    del position_all[index +1]
                    del value_left_voltage[index +1]
                    del value_right_voltage[index +1]
                    del value_left_current[index +1]
                    del value_right_current[index +1]

                    found_duplicate = True
                        
    return position_all,value_left_voltage,value_right_voltage,value_left_current,value_right_current