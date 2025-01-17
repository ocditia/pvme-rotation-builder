from components.inputs import UserInputs
from components.ability_dmg import AbilityDmg
from components.standard import StandardAbility

class ChanneledAbility:
    def __init__(self, ability, cast_tick):
        self.inputs = UserInputs(ability)
        self.ad = AbilityDmg(ability, cast_tick)
        self.standard = StandardAbility(ability, cast_tick)
        self.cast_tick = cast_tick
        
        for a in self.inputs.channels:
            if a['name'] == self.inputs.ability_input:
                abil = a
                break
            
        self.hit_tick = abil['hit_tick']
        self.hit_delay = abil['hit_delay']
        self.max_hits = abil['max_hits']
        if abil['bleed'] == 1:
            self.bleedable = True
        else:
            self.bleedable = False
    
    # figures out if an abil was canceled and returns the tick it was canceled
    def cancel(self):
        if self.inputs.type_n == 'CHANNELED':
            for i, entry in enumerate(self.inputs.rotation):
                if entry['tick'] == self.cast_tick:
                    if i + 1 < len(self.inputs.rotation):
                        return self.inputs.rotation[i + 1]['tick']
                    else:
                        None
        else:
            pass
    
    # figures out bled channels
    def bleed(self):
        if not self.bleedable:
            return False
    
        barge_entries = [entry for entry in self.inputs.rotation if entry['name'] == 'greater barge' and self.cast_tick - 10 <= entry['tick']]
    
        for barge_entry in barge_entries:
            barge_tick = barge_entry['tick']
            for i in self.inputs.rotation:
                if barge_tick < i['tick'] < self.cast_tick:
                    check = i['name']
                    for b in self.inputs.channels:
                        if check == b['name']:
                            if b['bleed'] == 1:
                                return False
                            break
                    else:
                        return True
    
        return True

    # figures out how many times a channeled abil hits factoring in cancelations and bleeding
    def hit_count(self):
        cancel_tick = self.cancel()
        bleed = self.bleed()
        if cancel_tick is not None:
            if bleed == True:
                hit_count = self.max_hits
            else:
                hit_count = min(int((cancel_tick - self.cast_tick + self.hit_tick) / self.hit_delay), self.max_hits)
        else:
            hit_count = self.max_hits
        return hit_count

    # returns a dict of the hits for the channeled ability and the tick they land on
    def hits(self):
        dmg = self.standard.aura_passive()
        fixed = dmg[0]
        var = dmg[1]
        hits = {}
        hit_count = self.hit_count()
        tick = self.cast_tick + self.hit_tick

        if self.inputs.dmg_output == 'MIN':
            for n in range(1, hit_count + 1):
                hits[f'tick {tick}'] = fixed
                tick += self.hit_delay
        elif self.inputs.dmg_output == 'AVG':
            for n in range(1, hit_count + 1):
                hits[f'tick {tick}'] = fixed + int(var / 2)
                tick += self.hit_delay
        elif self.inputs.dmg_output == 'MAX':
            for n in range(1, hit_count + 1):
                hits[f'tick {tick}'] = fixed + var
                tick += self.hit_delay

        return hits