"""Adaptive check distinguishing a trait-basis change from individual motion."""
from pathlib import Path
import json
import burst_transfer as B
FAMILIES=B.FAMILIES+['physics_reference','repeat_increment']
def run():
    return B.run(target='burst_onset',family_list=FAMILIES,tag='_control')
if __name__=='__main__':run()
