from decimal import *

ctx = getcontext()
ctx.traps[FloatOperation] = True

Is_Buck = False

## INPUT VARIABLES ##
# Circuit


isPeriod = True
Number_Periods = Decimal('0.5')
Simulation_Stop_Time = Decimal('0.0001821')

Voltage_Souce_Magnitude = Decimal('1')
Voltage_Source_Frequency = Decimal('50000')
Voltage_Source_Duty_cycle = Decimal('0.6')
Load_Resistance = Decimal('12')

# Inductor 
T = Decimal('19')/Decimal('2')
Z = Decimal('100000')
L = T*Z
C = T/Z

Inductor_Inductance_Per_Length =  Decimal('200e-6')#L
Inductor_Capacitance_Per_Length =  Decimal('0.2e-9')#C
Inductor_Length = Decimal('1')

# Capacitor
T = Decimal('7')/Decimal('2')
Z = Decimal('7')
L = T*Z
C = T/Z

Capacitor_Inductance_Per_Length =  Decimal('42e-9')#L
Capacitor_Capacitance_Per_Length =  Decimal('4.2e-6')#C
Capacitor_Length = Decimal('1')

## CALCULATED VARIABLES ##
# Circuit
Voltage_Souce_Period_Total = 1/Voltage_Source_Frequency
Voltage_Source_Period_On = Voltage_Souce_Period_Total * Voltage_Source_Duty_cycle
Voltage_Source_Period_Off = Voltage_Souce_Period_Total - Voltage_Source_Period_On

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

if(isPeriod):
    Simulation_Stop_Time = Number_Periods*Decimal('6.28318530718')*(Decimal.sqrt(Capacitor_Total_Capacitance*Inductor_Total_Inductance))


# Circuit Solvers
# Globally Define Variables
Load_Parallel_Inductor = Decimal('0')
Load_Parallel_Capacitor = Decimal('0')

Inductor_Solver_Term_VL  = Decimal('0')
Inductor_Solver_Term_VC  = Decimal('0')
Inductor_Solver_Term_IL  = Decimal('0')
Inductor_Solver_Term_IC  =Decimal('0')
Inductor_Solver_Term_VS  = Decimal('0')

Inductor_Solver_Term_VL_I  = Decimal('0')
Inductor_Solver_Term_VC_I  = Decimal('0')
Inductor_Solver_Term_IL_I  = Decimal('0')
Inductor_Solver_Term_IC_I  = Decimal('0')
Inductor_Solver_Term_VS_I  = Decimal('0')

Capacitor_Solver_Term_VC  = Decimal('0')
Capacitor_Solver_Term_VL  = Decimal('0')
Capacitor_Solver_Term_IC  = Decimal('0')
Capacitor_Solver_Term_IL  = Decimal('0')
Capacitor_Solver_Term_VS  = Decimal('0')

Capacitor_Solver_Term_VC_I  = Decimal('0')
Capacitor_Solver_Term_VL_I  = Decimal('0')
Capacitor_Solver_Term_IC_I  = Decimal('0')
Capacitor_Solver_Term_IL_I  = Decimal('0')
Capacitor_Solver_Term_VS_I  = Decimal('0')

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

    print(f"- The Voltage Source -")
    print(f"{'Votage Source Magnitude :':<40}{Voltage_Souce_Magnitude}")
    print(f"{'Voltage Source Frequency :':<40}{Voltage_Source_Frequency}")
    print(f"{'Voltage Source Duty cycle :':<40}{Voltage_Source_Duty_cycle}")
    print(f"{'Voltage Souce Total Period :':<40}{Voltage_Souce_Period_Total}")
    print(f"{'Voltage Souce ON Period :':<40}{Voltage_Source_Period_On}")
    print(f"{'Voltage Souce OFF Period :':<40}{Voltage_Source_Period_Off}")

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
    print(f"{'Inductor Velocity :':<40}{Inductor_Velocity}")
    print(f"{'Capacitor Time Delay :':<40}{Capacitor_Time}")
    print(f"{'Capacitor Impedance :':<40}{Capacitor_Impedance}")

    print(f"\n- The Load -")
    print(f"{'Load Resistance :':<40}{Load_Resistance}")
    print(f"{'Buck Converter :':<40}{Is_Buck}")