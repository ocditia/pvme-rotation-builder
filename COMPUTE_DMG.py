#
# Author - kyroh
# 
# This source code is licensed under the Attribution-NonCommercial-ShareAlike 4.0 International license found in the LICENSE file in the root directory of this source tree.
# 
# May 2023
#

import random
import os
import json

class Inputs:
    def __init__(self):
        with open(os.path.join('utils', 'ABILITIES.json'), 'r') as a:
            self.abilities = json.load(a)

        with open(os.path.join('utils', 'GEAR.json'), 'r') as g:
            self.gear = json.load(g)
        
        self.reaper_crew = True
        self.gear_input = {
            'helm': 'None',
            'body': 'None',
            'legs': 'None',
            'boots': 'None',
            'gloves': 'None',
            'cape': 'None',
            'ring': 'None',
            'neck': 'None',
            'pocket': 'None'
        }
        self.ability_input = 'asphyxiate'
        self.mh_input = 'Wand of the praesul'
        self.oh_input = 'Imperium core'
        self.th_input = 'Staff of Sliske'
        self.type = '2h'
        self.abil_params = self.get_abil_params()
        self.name = self.abil_params[0]
        self.fixed_dmg = self.abil_params[1]
        self.var_dmg = self.abil_params[2]
        self.style = self.abil_params[3]
        self.type_n = self.abil_params[4]
        self.class_n = self.abil_params[5]
        self.bonus = self.compute_bonus()
        self.magic_bonus = self.bonus[0]
        self.range_bonus = self.bonus[1]
        self.melee_bonus = self.bonus[2]
        self.spell_input = 99
        self.base_magic_level = 99
        self.base_range_level = 99
        self.base_strength_level = 99
        self.aura_input = 'None'
        self.potion_input = 'None'
        self.prayer_input = 'None'
        self.precise_rank = 6
        self.equilibrium_rank = 0
        self.lunging_rank = 0
        self.dmg_output = 'MIN'
    
    def get_abil_params(self):
        for a in self.abilities:
            if a['name'] == self.ability_input:
                abil = a
                break
        style = abil['style']
        class_n = abil['class_n']
        type_n = abil['type_n']
        fixed_dmg = abil['fixed']
        var_dmg = abil['var']
        name = abil['name']
        return [name, fixed_dmg, var_dmg, style, type_n, class_n]
    
    def compute_bonus(self):
        bonus = [0, 0, 0]
        gear_slots = {
            'helm': 'helm',
            'body': 'body',
            'legs': 'legs',
            'boots': 'boots',
            'gloves': 'gloves',
            'neck': 'neck',
            'cape': 'cape'
        }

        for item in self.gear:
            slot = item['slot']
            if item['name'] == self.gear_input.get(gear_slots.get(slot)):
                bonus[0] += item['magic_bonus']
                bonus[1] += item['range_bonus']
                bonus[2] += item['melee_bonus']
           
        if self.reaper_crew == True:
            bonus[0] += 12
            bonus[1] += 12
            bonus[2] += 12
        return bonus    
            
                
class StandardAbility:
    def __init__(self):
        with open(os.path.join('utils', 'WEAPONS.json'), 'r') as w:
            self.weapons = json.load(w)
        
        with open(os.path.join('utils', 'BOOSTS.json'), 'r') as b:
            self.boosts = json.load(b)

        # Variables from GUI inputs
        self.inputs = Inputs()
        self.sunshine = False
        self.death_swiftness = False
        self.berserk = False
        self.zgs_spec = False
        self.sim = 10000
        
        # Variables from methods
        self.boosted_levels = self.calculate_levels()
        self.boosted_magic_level = self.boosted_levels[0]
        self.boosted_range_level = self.boosted_levels[1]
        self.boosted_strength_level = self.boosted_levels[2]
        
        self.inputs.ability_dmg = self.base_ability_dmg()
        
        self.prayer_boost = self.prayer_dmg()
        self.magic_prayer = self.prayer_boost[0]
        self.range_prayer = self.prayer_boost[1]
        self.melee_prayer = self.prayer_boost[2]

    # Computes the dmg boosts from prayer
    def prayer_dmg(self):
        boost = None
        for b in self.boosts:
            if b['name'] == self.inputs.prayer_input:
                boost = b
                break
        if boost is None:
            pass
        
        prayer_dmg = [b["magic_dmg_percent"], b["range_dmg_percent"], b["strength_dmg_percent"]]
        
        return prayer_dmg
    
    # Computes your boosted level from aura for ability dmg computation
    def aura_level_boost(self):
        boost = next((b for b in self.boosts if b['name'] == self.inputs.aura_input), None)
        if boost is None:
            return [0, 0, 0]

        magic_boost_percent = self.inputs.base_magic_level * boost.get('magic_level_percent', 0)
        range_boost_percent = self.inputs.base_range_level * boost.get('range_level_percent', 0)
        strength_boost_percent = self.inputs.base_strength_level * boost.get('strength_level_percent', 0)

        return [magic_boost_percent, range_boost_percent, strength_boost_percent]

    # Computes your boosted level from potions for ability dmg computation
    def potion_level_boost(self):
        boost = next((b for b in self.boosts if b['name'] == self.inputs.potion_input), None)
        if boost is None:
            return [0, 0, 0]

        boost_values = {
            'magic_level_percent': self.inputs.base_magic_level * boost.get('magic_level_percent', 0),
            'range_level_percent': self.inputs.base_range_level * boost.get('range_level_percent', 0),
            'strength_level_percent': self.inputs.base_strength_level * boost.get('strength_level_percent', 0),
            'magic_level_boost': boost.get('magic_level_boost', 0),
            'range_level_boost': boost.get('range_level_boost', 0),
            'strength_level_boost': boost.get('strength_level_boost', 0)
        }

        net_magic_boost = boost_values['magic_level_percent'] + boost_values['strength_level_boost']
        net_range_boost = boost_values['range_level_percent'] + boost_values['range_level_boost']
        net_strength_boost = boost_values['strength_level_percent'] + boost_values['magic_level_boost']

        return [net_magic_boost, net_range_boost, net_strength_boost]

    # Takes all boosts and appends it to your magic level for net boosted level
    def calculate_levels(self):
        aura_boosts = self.aura_level_boost()
        potion_boosts = self.potion_level_boost()
        base_levels = [self.inputs.base_magic_level, self.inputs.base_range_level, self.inputs.base_strength_level]
        total_levels = []
        for x, y, z in zip(aura_boosts, potion_boosts, base_levels):
            total_levels.append(int(x + y + z))
        return total_levels
    
    # Computes base ability dmg for dual wield weapons
    def dw_ability_dmg(self):
        mh = None
        oh = None
        mh_ability_dmg = 0
        oh_ability_dmg = 0
        base_ability_dmg = 0
        
        for w in self.weapons:
            if w['name'] == self.inputs.mh_input:
                mh = w
                break
        if mh is None:
            pass
        if mh['style'] == 'MAGIC':
            mh_ability_dmg = int(2.5 * self.boosted_magic_level) + int(9.6 * min(mh['dmg_tier'],self.inputs.spell_input) + self.inputs.magic_bonus)
        elif mh['style'] == 'RANGE':
            mh_ability_dmg = int(2.5 * self.boosted_range_level) + int(9.6 * min(mh['dmg_tier'],self.inputs.spell_input) + self.inputs.range_bonus)
        elif mh['style'] == 'MELEE':
            mh_ability_dmg = int(2.5 * self.boosted_strength_level) + int(9.6 * mh['dmg_tier'] + self.inputs.melee_bonus)
        else:
            pass
        
        for w in self.weapons:
            if w['name'] == self.oh_input:
                oh = w
                break
        if oh is None:
            pass
        elif oh['style'] == 'MAGIC':
            oh_ability_dmg = int(0.5 * (int(2.5 * self.boosted_magic_level) + int(9.6 * min(oh['dmg_tier'],self.inputs.spell_input) + self.inputs.magic_bonus)))
        elif oh['style'] == 'RANGE':
            oh_ability_dmg = int(0.5 * (int(2.5 * self.boosted_range_level) + int(9.6 * min(oh['dmg_tier'],self.inputs.spell_input) + self.inputs.range_bonus)))
        elif oh['style'] == 'MELEE':
            oh_ability_dmg = int(0.5 * (int(2.5 * self.boosted_strength_level) + int(9.6 * oh['dmg_tier'] + self.inputs.melee_bonus)))
        else:
            pass
        
        base_ability_dmg = mh_ability_dmg + oh_ability_dmg
        return base_ability_dmg
   
    # Computes base ability dmg for 2h weapon
    def th_ability_dmg(self):
        th = None
        base_ability_dmg = 0 
        
        for w in self.weapons:
            if w['name'] == self.inputs.th_input:
                th = w
                break
        if th is None:
            pass
        if th['style'] == 'MAGIC':
            base_ability_dmg = int(2.5 * self.boosted_magic_level) + int(1.25 * self.boosted_magic_level) + int(14.4 * min(th['dmg_tier'],self.inputs.spell_input) + 1.5 * self.inputs.magic_bonus)
        elif th['style'] == 'RANGE':
            base_ability_dmg = int(2.5 * self.boosted_range_level) + int(1.25 * self.boosted_range_level) + int(14.4 * min(th['dmg_tier'],self.inputs.spell_input) + 1.5 * self.inputs.range_bonus)
        elif th['style'] == 'MELEE':
            base_ability_dmg = int(2.5 * self.boosted_strength_level) + int(1.25 * self.boosted_strength_level) + int(14.4 * th['dmg_tier'] + 1.5 * self.inputs.melee_bonus)
        else:
            pass
        return base_ability_dmg
    
    # Computes base ability dmg for Mainhand + no-offhand
    def ms_ability_dmg(self):
        mh = None
        mh_ability_dmg = 0
        
        for w in self.weapons:
            if w['name'] == self.inputs.mh_input:
                mh = w
                break
        if mh['style'] == 'MAGIC':
            mh_ability_dmg = int(2.5 * self.boosted_magic_level) + int(9.6 * min(mh['dmg_tier'],self.inputs.spell_input) + self.inputs.magic_bonus)
        elif mh['style'] == 'RANGE':
            mh_ability_dmg = int(2.5 * self.boosted_range_level) + int(9.6 * min(mh['dmg_tier'],self.inputs.spell_input) + self.inputs.range_bonus)
        elif mh['style'] == 'MELEE':
            mh_ability_dmg = int(2.5 * self.boosted_strength_level) + int(9.6 * mh['dmg_tier'] + self.inputs.melee_bonus)
        else:
            pass
        return mh_ability_dmg
    
    # Helper function to identify which weapons you're casting with and return the proper base ability dmg
    def base_ability_dmg(self):
        base_ability_dmg = 0
        
        if self.inputs.type == '2h':
            base_ability_dmg = self.th_ability_dmg()
        elif self.inputs.type == 'dw':
            base_ability_dmg = self.dw_ability_dmg()
        elif self.inputs.type == 'ms':
            base_ability_dmg = self.ms_ability_dmg()
        else:
            pass
        return base_ability_dmg
    
    # Computes dmg floor with prayer modifier
    def fixed(self):
        prayer_map = {
            'MAGIC': self.magic_prayer,
            'RANGE': self.range_prayer,
            'MELEE': self.melee_prayer
        }
        
        if self.inputs.style in prayer_map:
            fixed = int(int(self.inputs.ability_dmg * self.inputs.fixed_dmg) * (1 + prayer_map[self.inputs.style]))
        else:
            fixed = 0
        return fixed
    
    # Computes var dmg with prayer modifier
    def var(self):
        prayer_map = {
            'MAGIC': self.magic_prayer,
            'RANGE': self.range_prayer,
            'MELEE': self.melee_prayer
        }
        
        if self.inputs.style in prayer_map:
            var = int(int(self.inputs.ability_dmg * self.inputs.var_dmg) * (1 + prayer_map[self.inputs.style]))
        else:
            var = 0
        return var
    
    # Computes the dmg range of an abil after precise
    def precise(self):
        dmg_values = self.dpl()
        fixed = dmg_values[0]
        var = dmg_values[1]
        precise = int(0.015 * (fixed + var) * self.inputs.precise_rank)
        fixed += precise
        var -= precise
        return [(fixed), (var)]
        
    # Computes the dmg range of an abil after equilibrium
    def equilibrium(self):
        precise = self.precise()
        fixed = precise[0]
        var = precise[1]
        
        if self.inputs.aura_input == 'Equilibrium':
            fixed += 0.25 * var
            var -= 0.5 * var
        else:
            fixed += 0.03 * var * self.inputs.equilibrium_rank
            var -= 0.04 * var * self.inputs.equilibrium_rank
        return [int(fixed), int(var)]
    
    # Computes dmg per level and outputs new fixed and var dmg
    def dpl(self):
        fixed = self.fixed()
        var = self.var()
    
        if self.inputs.style in ('MAGIC', 'RANGE', 'MELEE'):
            if self.inputs.style == 'MAGIC':
                base_level = self.inputs.base_magic_level
                boosted_level = self.boosted_magic_level
            elif self.inputs.style == 'RANGE':
                base_level = self.inputs.base_range_level
                boosted_level = self.boosted_range_level
            elif self.inputs.style == 'MELEE':
                base_level = self.inputs.base_melee_level
                boosted_level = self.boosted_melee_level
            else:
                pass
        
            level_difference = boosted_level - base_level
            fixed += int(level_difference * 4)
            var += int(level_difference * 4)
        
        return [fixed, var]
    
    # Computes the dmg boost from aura passives
    def aura_passive(self):
        dmg = self.dmg_boost()
        fixed = dmg[0]
        var = dmg[1]
        
        boost = None
        for b in self.boosts:
            if b['name'] == self.inputs.aura_input:
                boost = b
                break
        if self.inputs.style == 'MAGIC' and self.sunshine == False:
            fixed += int(fixed * boost['magic_dmg_percent'])
            var += int(var * boost['magic_dmg_percent'])
        elif self.inputs.style == 'RANGE' and self.death_swiftness == False:
            fixed += int(fixed * boost['range_dmg_percent'])
            var += int(var * boost['range_dmg_percent'])
        elif self.inputs.style == 'MELEE' and (self.berserk == False or self.zgs_spec == False):
            fixed += int(fixed * boost['strength_dmg_percent'])
            var += int(var * boost['strength_dmg_percent'])
        else:
            pass
        return [fixed, var]

    # Computes the dmg boost from ultimates and specs
    def dmg_boost(self):
        dmg_values = self.equilibrium()
        fixed = dmg_values[0]
        var = dmg_values[1]
    
        if (self.sunshine == True and self.inputs.style == 'MAGIC') or (self.death_swiftness == True and self.inputs.style == 'RANGE'):
            boost_multiplier = 0.5
        elif self.berserk == True and self.inputs.style == 'MELEE':
            boost_multiplier = 2.0
        elif self.zgs_spec == True and self.inputs.style == 'MELEE':
            boost_multiplier = 1.25
        else:
            boost_multiplier = 0
        
        fixed += int(fixed * boost_multiplier)
        var += int(var * boost_multiplier)
        
        return [fixed, var]


class BleedAbility:
    
    def __init__(self):
        with open(os.path.join('utils', 'BLEEDS.json'), 'r') as bleed:
            self.bleeds = json.load(bleed)
            
        self.standard = StandardAbility()
        self.inputs = Inputs()

    # Conmputes fixed dmg without prayer because bleeds are great
    def fixed(self):
        fixed = int(self.inputs.ability_dmg * self.inputs.fixed_dmg)
        return fixed
    
    # Computes var dmg without prayer because bleeds make sense
    def var(self):
        var = int(self.inputs.ability_dmg * self.inputs.var_dmg)
        return var
    
    # Simulates the abil n times and returns the average
    def avg_dmg(self):
        fixed = self.fixed()
        var = self.var()
        max_dmg = fixed + var
        avg_dmg = 0
        total = 0
        
        if self.inputs.name == 'combust' or self.inputs.name == 'fragmentation shot' or self.inputs.name == 'dismember' or self.inputs.name == 'slaughter':
            for _ in range(self.standard.sim):
                random_num = random.randint(1,100)
                dmg = int((self.inputs.ability_dmg * max(((random_num * (1.88 + 0.2 * self.inputs.lunging_rank)) / 100), 1)) / 5)
                total += dmg
                avg_dmg = int(total / self.standard.sim)
        else:
            for _ in range(self.standard.sim):
                random_num = random.randint(fixed, max_dmg)
                total += random_num
            avg_dmg = int(total / self.standard.sim)
        return avg_dmg
    
    def hits(self):
        avg_dmg = self.avg_dmg()
        var = self.var()
        fixed = self.fixed()
        max_dmg = fixed + var
        hits = []
        
        for bleed in self.bleeds:
            if bleed['name'] == self.inputs.name:
                abil = bleed
                break
        hit_count = abil['hits']
        dmg_decay = abil['dmg_decay']
        
        if dmg_decay == 0:
            if self.inputs.dmg_output == 'MIN':
                hits = [fixed] * hit_count
            elif self.inputs.dmg_output == 'AVG':
                hits = [avg_dmg] * hit_count
            elif self.inputs.dmg_output == 'MAX':
                hits = [max_dmg] * hit_count
            else:
                pass
        else:
            if self.inputs.name == 'corruption shot' or self.inputs.name == 'corruption blast':
                if self.inputs.dmg_output == 'MIN':
                    last_hit = int(self.inputs.ability_dmg * 0.067)
                    for i in range(1, hit_count + 1):
                        hits.append(last_hit * i)
                elif self.inputs.dmg_output == 'AVG':
                    last_hit_min = int(self.inputs.ability_dmg * 0.067)
                    last_hit_max = int(self.inputs.ability_dmg * 0.067 * 3)
                    last_hit = int((last_hit_min + last_hit_max) / 2)
                    for i in range(1, hit_count + 1):
                        hits.append(last_hit * i)
                elif self.inputs.dmg_output == 'MAX':
                    last_hit = int(self.inputs.ability_dmg * 0.067 * 3)
                    for i in range(1, hit_count + 1):
                        hits.append(last_hit * i)
                else:
                    pass
            elif self.inputs.name == 'blood tendrils':
                if self.inputs.dmg_output == 'MIN':
                    small_hit = int(36 / 20 * fixed)
                    large_hit = small_hit * 2
                    hits = [large_hit] + [small_hit] * (hit_count - 1)
                elif self.inputs.dmg_output == 'AVG':
                    small_hit = int((int((36 / 20 * fixed) + (36 / 20 * var)) + int(36 / 20 * fixed)) / 2)
                    large_hit = small_hit * 2
                    hits = [large_hit] + [small_hit] * (hit_count - 1)
                elif self.inputs.dmg_output == 'MAX':
                    small_hit = int((36 / 20 * fixed) + (36 / 20 * var))
                    large_hit = small_hit * 2
                    hits = [large_hit] + [small_hit] * (hit_count - 1)
            else:
                pass
        return [hits]

    
    def walk(self):
        walk = False
        hits = self.hits()

        for bleed in self.bleeds:
            if bleed['name'] == self.inputs.name:
                abil = bleed
                break
        multiplier = abil['walk']  

        if walk == True:
            hits = [entry * multiplier for entry in hits]
        else:
            pass
        return hits

class ChanneledABility:
    def __init__(self):
        self.standard = StandardAbility()
        self.inputs = Inputs()

    def hits(self):
        dmg = self.standard.aura_passive()
        fixed = dmg[0]
        var = dmg[1]
        hits = []

        if self.inputs.dmg_output == 'MIN':
            hits = [fixed] * 4
        elif self.inputs.dmg_output == 'AVG':
            hits = [fixed + int(var / 2)] * 4
        elif self.inputs.dmg_output == 'MAX':
            hits = [fixed + var] * 4
        return [hits]

class OnHitEffects:
    pass


test = ChanneledABility() 


dmg = test.hits()

print(dmg)





