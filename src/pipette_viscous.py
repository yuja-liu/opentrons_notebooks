"""
Yujia Liu    yujialiu@uchicago.edu
06/16/22

Default parameters are optimized for handling
4x SDS-PAGE loading buffer with 40% glycerol
or any liquid covered by mineral oil (to pervent from evaporation)
"""

from opentrons import protocol_api

def custom_touch_tip(pipette:protocol_api.InstrumentContext, protocol:protocol_api.ProtocolContext,
                    repeats=2):
    "Touching tip with custom parameters"
    
    for i in range(repeats):
        protocol.delay(1)
        pipette.touch_tip(v_offset = -2, speed = 30, radius = 0.8)
    

def aspirate_viscous(
    pipette:protocol_api.InstrumentContext, 
    protocol:protocol_api.ProtocolContext,
    vol, 
    well, 
    rate=0.5, 
    delay=5, 
    entry_speed=2,
    with_speed=2,
    asp_height=1,
    if_touch_tip=True):
    """
    Aspirate viscous liquid (will pick up a tip beforehand)
    
    Parameters
    - pipette and protocol: required contexts to communicate with the hardware
    - vol: pipetting volume
    - well: position of the well
    - rate: rate of aspiration in fraction of the default rate (5ul/s)
    - delay: delay after aspiration in seconds
    - entry_speed: speed that the tip enters the liquid in units of mm/s (default = 400mm/s)
    - with_speed: withdrawal rate in units of mm/s (default head speed is 400mm/s)
    - asp_height: height of aspiration. For a small amount of liquid covered with oil, aspirating too close to the bottom
    actually worsens oil contamination, since the oil will be stuck between the orifice and the bottom
    2 is ususlly good to avoid this
    - if_touch_tip: whether to touch tip (around the edge of the tube)
    """
    # see https://docs.opentrons.com/v2/new_pipette.html#defaults for more defaults

    pipette.pick_up_tip()
    
    # move slowly to the bottom of the well/tube
    pipette.move_to(well.top())    # first hover at top
    def_speed = pipette.default_speed    # back it up
    pipette.default_speed = entry_speed
    pipette.aspirate(vol, well.bottom(asp_height), rate=rate)
    pipette.default_speed = def_speed    # restore
    
    protocol.delay(delay)    # delay after aspiration/dispense to allow relaxation of the liquid
    pipette.move_to(well.top(), speed=with_speed)
    
    if if_touch_tip:
        custom_touch_tip(pipette, protocol)
        


def dispense_viscous(
    pipette :protocol_api.InstrumentContext, 
    protocol :protocol_api.ProtocolContext,
    vol, 
    well, 
    rate=0.1, 
    delay=5, 
    blowout_rate=0.5,
    mix_rate=1.0,
    entry_speed=2,
    with_speed=2, 
    disp_height=1.0, 
    mix_height=-1,
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
    - mix_rate: fraction of the default rate of mixing. default is 1.0
    - with_speed: withdrawal rate (after blowout if any) in units of mm/s (default head speed is 400mm/s)
    - disp_height: height of the nozzle from bottom during dispense in mm. default is 1mm
    - if_mix: whether to mix (before blowout)
    - if_blowout: whether to do a blowout
    """
    
    pipette.move_to(well.top())
    
    # move slowly to the bottom of the well/tube
    def_speed = pipette.default_speed    # back it up
    pipette.default_speed = entry_speed
    pipette.dispense(vol, well.bottom(disp_height), rate=rate)    # avoid touching the bottom and block the liquid
    pipette.default_speed = def_speed    # restore
    
    if if_mix:
        if mix_height < 0:    # unset
            mix_height = disp_height
        pipette.mix(3, vol, well.bottom(mix_height), rate=mix_rate)    # mix 3 times. Reduce speed to avoid introducing air gap
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
    asp_height=1.0,
    disp_height=1.0,
    delay=5,
    if_touch_tip=True,
    if_mix=False,
    if_blowout=True):
    "The complex command for transfering viscous liquid"
    
    # most parameters are not exposed. If one wants more flexibility, use the building-block commands
    
    aspirate_viscous(pipette, protocol, vol, from_well, asp_height=asp_height, delay=delay, if_touch_tip=if_touch_tip)
    dispense_viscous(pipette, protocol, vol, to_well, disp_height=disp_height, delay=delay, if_mix=if_mix, if_blowout=if_blowout)
    
"Manual compensation for the volumetric error of the p10 pipette"
#def calibrated(v):
#    # units: ul
#    return v + 0.34

"""
Compensating for pipetting viscous liquid (due to presumably both viscosity and
a different handling protocol, it requires a different calibration)
"""
def calibrated_viscous(v):
    # units: ul
    
    # new compensation scheme, measured from adding-in volumes
    # taking-out volumes are (within measurement uncertainties) accurate -- no need for compensating
    return min(10, v + 0.30)
    