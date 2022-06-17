"""
Yujia Liu    yujialiu@uchicago.edu
06/16/22

Default parameters are optimized for handling
SDS-PAGE loading buffer with 10% glycerol
"""

from opentrons import protocol_api

def custom_touch_tip():
    "Touching tip with custom parameters"
    
    protocol.delay(5)
    pipette.touch_tip(v_offset = -2, speed = 30, radius = 0.8)
    

def aspirate_viscous(
    pipette:protocol_api.InstrumentContext, 
    protocol:protocol_api.ProtocolContext,
    vol, 
    well, 
    rate=0.5, 
    delay=5, 
    with_speed=2,
    if_touch_tip=True):
    """
    Aspirate viscous liquid (will pick up a tip beforehand)
    
    Parameters
    - pipette and protocol: required contexts to communicate with the hardware
    - vol: pipetting volume
    - well: position of the well
    - rate: rate of aspiration in fraction of the default rate (5ul/s)
    - delay: delay after aspiration in seconds
    - with_speed: withdrawal rate in units of mm/s (default head speed is 400mm/s)
    - if_touch_tip: whether to touch tip (around the edge of the tube)
    """
    # see https://docs.opentrons.com/v2/new_pipette.html#defaults for more defaults

    pipette.pick_up_tip()
    pipette.move_to(well.top())
    pipette.aspirate(vol, well.bottom(), rate=rate)
    protocol.delay(delay)    # delay after aspiration/dispense to allow relaxation of the liquid
    pipette.move_to(well.top(), speed=with_speed)
    
    if if_touch_tip:
        custom_touch_tip()
        


def dispense_viscous(
    pipette :protocol_api.InstrumentContext, 
    protocol :protocol_api.ProtocolContext,
    vol, 
    well, 
    rate=0.1, 
    delay=5, 
    blowout_rate=0.5, 
    with_speed=2, 
    height=0.5, 
    if_mix = False,
    if_blowout=True):
    """
    Dispense viscous liquid (will drop the tip afterwards)
    
    Parameters
    - pipette and protocol: required contexts to communicate with the hardware
    - vol: pipetting volume
    - well: position of the well
    - rate: dispense rate as fraction of default rate (10ul/s)
    - delay: delay after dispense in seconds
    - blowout_rate: blowout rate in ul/s (not fraction!) default is 1000ul/s (i.e. much faster)
    - with_speed: withdrawal rate (after blowout if any) in units of mm/s (default head speed is 400mm/s)
    - height: height of the nozzle from bottom during dispense in mm. default is 1mm
    - if_mix: whether to mix (before blowout)
    - if_blowout: whether to do a blowout
    - if_touch_tip: whether to touch tip (around the edge of the tube)
    """
    
    pipette.move_to(well.top())
    pipette.dispense(vol, well.bottom(disp_height), rate=rate)    # avoid touching the bottom and block the liquid
    if if_mix:
        pipette.mix(3, vol)    # mix 3 times
    protocol.delay(delay)
    
    if if_blowout:
        def_blowout_rate = pipette.flow_rate.blow_out    # save the current blowout rate
        pipette.flow_rate.blow_out=blowout_rate    # change it
        pipette.blow_out()
        pipette.flow_rate.blow_out=def_blowout_rate    # recover the default
    
    pipette.move_to(well.top(), speed=with_speed)
    pipette.drop_tip()
    
    
def transfer_viscous(
    pipette:protocol_api.InstrumentContext,
    protocol: protocol_api.ProtocolContext,
    vol,
    from_well,
    to_well,
    if_touch_tip=True,
    if_mix=False):
    "The complex command for transfering viscous liquid"
    
    # most parameters are not exposed. If one wants more flexibility, use the building-block commands
    
    aspirate_viscous(pipette, protocol, vol, from_well, if_touch_tip=if_touch_tip)
    dispense_viscous(pipette, protocol, vol, to_well, if_mix=if_mix)
    
    