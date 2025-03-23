import os
import numpy as np
import re

GCD = 15 # decisecodns

class Boss:
    def __init__(self, Stats):
        self.Armor = 3500
        self.Level = 63
        self.SpellResistance = 0
        self.GlancingBlowChance = 0

        if Stats["Armor"] is not None: self.Armor = Stats["Armor"]
        if Stats["Level"] is not None: self.Level = Stats["Level"]
        if Stats["Resistance"] is not None: self.SpellResistance = Stats["Resistance"]

        self.DefenseSkill = 300 + (self.Level - 60) * 5
        self.PhysReduc =  self.Armor / ( self.Armor + 400 + 85 * self.Level)
        self.Dodge = 5 + (self.DefenseSkill - 300) * 0.2
        self.Miss  = 5 + (self.DefenseSkill - 300) * 0.2

        match(self.Level):
            case(60):
                self.SpellMiss = 4
            case(61):
                self.SpellMiss = 5
            case(62):
                self.SpellMiss = 6
            case(63):
                self.SpellMiss = 17
                self.GlancingBlowChance = 40

class Character:
    
    def __init__(self, Target, Stats, Weapon, Talents, SetBonuses):
        # Set default values
        self.BaseWepMin, self.BaseWepMax = 1, 2
        self.WepAttackSpeed = 0
        self.AttackPower    = 0
        self.SpellPower     = 0
        self.WeaponSkill    = 0
        self.HitChance      = 0
        self.SpellHitChance = 0
        self.MeleeCrit      = 0
        self.SpellCrit      = 0
        self.Haste          = 0
        self.WepImbue = "Windfury"
        
        self.CharacterBuffs = self.Buffs(self)
        self.CharacterAttacks = self.Attacks(self)
        
        self.initialize_stats(Stats)
        self.initialize_weapon(Weapon)
        self.initialize_talents(Talents)

        # Update combat stats against target 
        self.MissChance = Target.Miss - (self.HitChance + self.WeaponSkill * 0.2 + 3)
        self.DodgeChance = Target.Dodge 
        self.SpellMissChance = Target.SpellMiss - self.SpellHitChance
        self.SpellResistChance = Target.SpellResistance
        self.GlancingBlowDMG = 0.70 + self.WeaponSkill*0.2
        self.GlancingBlowChance = Target.GlancingBlowChance
        self.ReducedPhysDmg = (1 - Target.PhysReduc)

        self.UpdateStats()

    class Buffs:
        def __init__(self, CharacterInput):
            self.CharacterInstance = CharacterInput

            self.Flurry = False
            self.StormStrikeBuff = False
            self.ElementalStrength = False
            self.RapidSpeed = False
            self.ElementalDevastation = False
            self.UnholyStrength = False
            self.Bloodlust = False
            self.CritBloodlust = False

            self.FlurryStacks = 3
            self.StormStrikeStacks = 2

            self.ElementalStrengthDuration = 100
            self.RapidSpeedDuration = 80
            self.ElementalDevastationDuration = 100
            self.UnholyStrengthDuration = 150
            self.BloodlustDuration = 300
            self.CritBloodlustDuration = 50

            self.BuffUptimes = {"Flurry" : 0, "Stormstrike" : 0, "Elemental Strength" : 0, "Rapid Speed" : 0, "Elemental Devastation" : 0, "Unholy Strength" : 0, "Bloodlust (15%)" : 0, "Bloodlust (5%)" : 0}

        def checkBuffs(self):
            if self.Flurry: self.checkFlurry()
            if self.StormStrikeBuff: self.checkStormStrikeBuff()  
            if self.ElementalStrength: self.checkElementalStrength()
            if self.RapidSpeed: self.checkRapidSpeed()  
            if self.ElementalDevastation: self.checkElementalDevastation()
            if self.UnholyStrength: self.checkUnholyStrength()
            if self.Bloodlust: self.checkBloodlust()
            if self.CritBloodlust: self.checkCritBloodlust()
        
        def checkFlurry(self):
            if self.FlurryStacks == 0:
                self.Flurry = False
                self.CharacterInstance.Haste -= 20
            else: self.BuffUptimes["Flurry"] += 1

        def checkStormStrikeBuff(self):
            if self.StormStrikeStacks == 0:
                self.StormStrikeBuff = False
            else: self.BuffUptimes["Stormstrike"] += 1

        def checkElementalStrength(self):
            if self.ElementalStrengthDuration == 0:
                self.ElementalStrength = False
                self.CharacterInstance.AttackPower -= 130
            else:
                self.ElementalStrengthDuration -= 1
                self.BuffUptimes["Elemental Strength"] += 1
        
        def checkRapidSpeed(self):
            if self.RapidSpeedDuration == 0:
                self.RapidSpeed = False
                self.CharacterInstance.Haste -= 8
            else:
                self.RapidSpeedDuration -= 1
                self.BuffUptimes["Rapid Speed"] += 1
        
        def checkElementalDevastation(self):
            if self.ElementalDevastationDuration == 0:
                self.ElementalDevistation = False
                self.CharacterInstance.SpellHitChance -= 9
            else:
                self.ElementalDevastationDuration -= 1
                self.BuffUptimes["Elemental Devastation"] += 1
               
        def checkUnholyStrength(self):
            if self.UnholyStrengthDuration == 0:
                self.UnholyStrength = False
                self.CharacterInstance.AttackPower -= 100*2
            else:
                self.UnholyStrengthDuration -= 1
                self.BuffUptimes["Unholy Strength"] += 1
            
        def checkBloodlust(self):
            if self.BloodlustDuration == 0:
                self.CharacterInstance.Haste -= 15
                self.Bloodlust = False
            else:
                self.BloodlustDuration -= 1
                self.BuffUptimes["Bloodlust (15%)"] += 1
        
        def checkCritBloodlust(self):
            if self.CritBloodlustDuration == 0:
                self.CharacterInstance.Haste -= 5
                self.CritBloodlust = False
            else:
                self.CritBloodlustDuration -= 1
                self.BuffUptimes["Bloodlust (5%)"] += 1
        def procFlurry(self):
            if self.Flurry: 
                self.FlurryStacks = 3
            else:   
                self.Flurry = True
                self.FlurryStacks = 3
                self.CharacterInstance.Haste += 20

        def procStormStrikeBuff(self):
            if self.StormStrikeBuff: 
                self.StormStrikeStacks = 2
            else:   
                self.StormStrikeBuff = True
                self.StormStrikeStacks = 2
        
        def procElementalStrength(self):
            if self.CharacterInstance.DiceRoll() <= 35:
                if self.ElementalStrength:
                    self.ElementalStrengthDuration = 100
                else:
                    self.ElementalStrength = True
                    self.ElementalStrengthDuration = 100
                    self.CharacterInstance.AttackPower += 130
        
        def procRapidSpeed(self):
            if self.CharacterInstance.DiceRoll() <= 15:
                if self.RapidSpeed:
                    self.RapidSpeedDuration = 80
                else:
                    self.RapidSpeed = True
                    self.RapidSpeedDuration = 80
                    self.CharacterInstance.Haste += 8
        
        def procElementalDevastation(self):
            if self.ElementalDevastation:
                self.ElementalDevastationDuration = 100
            else:
                self.ElementalDevastation = True
                self.ElementalDevastationDuration = 100
                self.CharacterInstance.SpellHitChance += 9
            
        def procUnholyStrength(self):
            if self.CharacterInstance.DiceRoll() <= (self.CharacterInstance.WepAttackSpeed/10)*1.82:
                if self.UnholyStrength:
                    self.UnholyStrengthDuration = 150
                else:
                    self.UnholyStrength = True
                    self.UnholyStrengthDuration = 150
                    self.CharacterInstance.AttackPower += (100)*2
        
        def procBloodlust(self):
            if self.Bloodlust:
                if self.CritBloodlust:
                    self.CritBloodlustDuration = 50
                else:
                    self.CritBloodlustDuration = 50
                    self.CritBloodlust = True
                    self.CharacterInstance.Haste += 5
                
    class Talents:
        def __init__(self, CharacterInput):
            self.CharacterInstance = CharacterInput
            # ELEMENTAL 
            self.Conussion = False
            self.Reverberation = False
            # ENHANCEMENT
            self.WeaponMastery = False
            self.AncestralKnowledge = False
            self.ElementalWeapons = False
            # RESTORATION ?

    class ItemsAndEnchants:
        def __init__(self, CharacterInput):
            self.CharacterInstance = CharacterInput

    class Attacks:
        def __init__(self, CharacterInput):
            self.CharacterInstance = CharacterInput
            self.SwingTimer = 0
            self.AttemptedHits = {"White Attacks" : 0, "Yellow Attacks" : 0}
            self.AutoAttackStats = {"Glancing Blow": 0, "Miss" : 0, "Dodge" : 0, "Critical Strike" : 0}
            self.DamageCount = {"Auto Attack" : 0, "Earth Shock" : 0, "Stormstrike" : 0, "Lightning Strike" : 0, "Lightning Shield" : 0}
            self.Cooldowns = {"Earth Shock" : 0, "Stormstrike" : 0, "Lightning Strike" : 0, "Bloodlust" : 0}

        def WeaponSwing(self):
            WepDmg = np.random.randint(self.CharacterInstance.WepDamage[0],self.CharacterInstance.WepDamage[1])
            return WepDmg
        
        def CriticalStrike(self, Damage, Type="Melee"):
            match Type:
                case "Melee":
                    if self.CharacterInstance.DiceRoll() <= self.CharacterInstance.MeleeCrit:
                        Damage *= 2.0
                        self.CharacterInstance.CharacterBuffs.procFlurry()
                        self.CharacterInstance.CharacterBuffs.procBloodlust()
                        self.CharacterInstance.CharacterBuffs.procElementalDevastation()
                case "Spell":
                    if self.CharacterInstance.DiceRoll() <= self.CharacterInstance.SpellCrit:
                        Damage *= 1.5
            return Damage

        def EvaluateWhiteAttack(self,Damage):
            self.AttemptedHits["White Attacks"] += 1
            if self.CharacterInstance.DiceRoll() <= self.CharacterInstance.DodgeChance:
                Damage = 0
                self.AutoAttackStats["Dodge"] += 1
            elif self.CharacterInstance.DiceRoll() <= (self.CharacterInstance.MissChance):
                Damage = 0 
                self.AutoAttackStats["Miss"] += 1
            else: 
                self.CharacterInstance.CharacterBuffs.procUnholyStrength()
                if self.CharacterInstance.DiceRoll() >= self.CharacterInstance.GlancingBlowChance:
                    Damage *= self.CharacterInstance.GlancingBlowDMG
                    self.AutoAttackStats["Glancing Blow"] += 1
                else: 
                    tmp = Damage
                    Damage = self.CriticalStrike(Damage) 
                    if tmp != Damage: self.AutoAttackStats["Critical Strike"] += 1
            return Damage * self.CharacterInstance.ReducedPhysDmg
            
        def EvaluateYellowAttack(self,Damage):
            self.AttemptedHits["Yellow Attacks"] += 1
            if self.CharacterInstance.DiceRoll() <= self.CharacterInstance.DodgeChance:
                Damage = 0
            elif self.CharacterInstance.DiceRoll() <= (self.CharacterInstance.MissChance ):
                Damage = 0
            else: 
                self.CharacterInstance.CharacterBuffs.procUnholyStrength()
                Damage = self.CriticalStrike(Damage) 
                self.procWepImbue()
            return Damage * self.CharacterInstance.ReducedPhysDmg
            
        def EvaluateSpellAttack(self,Damage):
            if self.CharacterInstance.DiceRoll() <= (self.CharacterInstance.SpellMissChance):
                Damage = 0
            elif self.CharacterInstance.DiceRoll() <= self.CharacterInstance.SpellResistChance:
                Damage = 0
            else: 
                Damage = self.CriticalStrike(Damage,"Spell")
            return Damage
        
        def AutoAttack(self):
            if self.CharacterInstance.CharacterBuffs.Flurry: self.CharacterInstance.CharacterBuffs.FlurryStacks -= 1
            Damage = self.EvaluateWhiteAttack(self.WeaponSwing())
            if Damage != 0: self.procWepImbue()
            self.DamageCount["Auto Attack"] += Damage
            self.SwingTimer = 0
            return Damage
        
        def procWepImbue(self):
            match(self.CharacterInstance.WepImbue.upper()):
                case "WINDFURY":
                    self.Windfury()
                case "FROSTBRAND":
                    self.Frostbrand()
                case "FLAMETONGUE":
                    self.Flametongue()
        
        def Windfury(self):
            WF_PROC = 20 # %
            Damage = 0
            if self.CharacterInstance.DiceRoll() <= WF_PROC:
                self.CharacterInstance.AttackPower += 323
                self.CharacterInstance.UpdateStats()
                Damage += self.EvaluateWhiteAttack(self.WeaponSwing())
                Damage += self.EvaluateWhiteAttack(self.WeaponSwing())
                self.CharacterInstance.AttackPower -= 323
                self.CharacterInstance.UpdateStats()
            self.DamageCount["Windfury"] += Damage
            
        
        def Frostbrand(self):
            Damage = 0
            if self.CharacterInstance.DiceRoll() <= 9/(60/(self.CharacterInstance.WepAttackSpeed/10))*100:
                Damage = 187 + 0.1 * self.CharacterInstance.SpellPower
                Damage = self.EvaluateSpellAttack(Damage)
            self.DamageCount["Frostbrand"] += Damage
            return Damage
        
        def Flametongue(self):
            Damage = (self.CharacterInstance.WepAttackSpeed/10) * 27 + 0.1 * self.CharacterInstance.SpellPower
            Damage = self.EvaluateSpellAttack(Damage)
            self.DamageCount["Flametongue"] += Damage
            return Damage
            
        def EarthShock(self):
            DmgAmp = 1.0
            if self.CharacterInstance.CharacterBuffs.StormStrikeBuff:
                DmgAmp = 1.20
                self.CharacterInstance.CharacterBuffs.StormStrikeStacks -= 1
            Damage = (np.random.randint(506,536) + (0.10 * self.CharacterInstance.AttackPower)) * DmgAmp
            self.Cooldowns["Earth Shock"] = 50 
            self.CharacterInstance.CharacterBuffs.procElementalStrength()
            Damage = self.EvaluateSpellAttack(Damage)
            self.DamageCount["Earth Shock"] += Damage
            return Damage
        
        def StormStrike(self):
            AttackCoef = 1.11
            self.CharacterInstance.CharacterBuffs.procStormStrikeBuff()
            Damage = self.EvaluateYellowAttack(AttackCoef*self.WeaponSwing())
            self.Cooldowns["Stormstrike"] = 75
            self.DamageCount["Stormstrike"] += Damage
            return Damage
        
        def LightningStrike(self):
            AttackCoef = 0.88
            self.CharacterInstance.CharacterBuffs.procRapidSpeed()
            self.PopLightningShield()
            Damage = self.EvaluateYellowAttack(AttackCoef*self.WeaponSwing())
            self.Cooldowns["Lightning Strike"] = 85
            self.DamageCount["Lightning Strike"] += Damage 
            return Damage
        
        def PopLightningShield(self):
            DmgAmp = 1.0
            if self.CharacterInstance.CharacterBuffs.StormStrikeBuff:
                DmgAmp = 1.20
                self.CharacterInstance.CharacterBuffs.StormStrikeStacks -= 1
            Damage = (198 + self.CharacterInstance.AttackPower/4) * DmgAmp
            Damage = self.EvaluateSpellAttack(Damage)
            self.DamageCount["Lightning Shield"] += Damage
            return Damage
        
        def Bloodlust(self):
            self.Cooldowns["Bloodlust"] = 600*5
            self.CharacterInstance.CharacterBuffs.Bloodlust = True
            self.CharacterInstance.CharacterBuffs.BloodlustDuration = 300
            self.CharacterInstance.Haste += 15
            
        def ReduceCooldowns(self):
            if self.Cooldowns["Earth Shock"] > 0: self.Cooldowns["Earth Shock"] -= 1
            if self.Cooldowns["Stormstrike"] > 0: self.Cooldowns["Stormstrike"] -= 1
            if self.Cooldowns["Lightning Strike"] > 0: self.Cooldowns["Lightning Strike"] -= 1
            if self.Cooldowns["Bloodlust"] > 0: self.Cooldowns["Bloodlust"] -= 1

    def DiceRoll(self):
        return np.random.random()*100
    
    def initialize_stats(self, Stats):
        if Stats["AttackPower"] is not None: self.AttackPower = Stats["AttackPower"]
        if Stats["Haste"] is not None: self.Haste = Stats["Haste"]
        if Stats["MeleeHit"] is not None: self.HitChance = Stats["MeleeHit"]
        if Stats["MeleeCrit"] is not None: self.MeleeCrit = Stats["MeleeCrit"]
        if Stats["SpellHit"] is not None: self.SpellHit = Stats["SpellHit"]
        if Stats["SpellCrit"] is not None: self.SpellCrit = Stats["SpellCrit"]

    def initialize_weapon(self, Weapon):
        if Weapon["WeaponDmg"] is not None: self.BaseWepMin, self.BaseWepMax = Weapon["WeaponDmg"][0], Weapon["WeaponDmg"][1]
        if Weapon["WepSpeed"] is not None: self.WepAttackSpeed = Weapon["WepSpeed"] * 10
        if Weapon["WeaponSkill"] is not None: self.WeaponSkill = Weapon["WeaponSkill"]
        if Weapon["Imbue"] is not None: 
            self.WepImbue = Weapon["Imbue"]
            self.CharacterAttacks.DamageCount[self.WepImbue.lower().capitalize()] = 0
            if self.WepImbue.upper() == "ROCKBITER": self.AttackPower += 554
        
    def initialize_talents(self, Talents):
        return
        
    def UpdateStats(self):
        self.WepDamage = (np.array([self.BaseWepMin,self.BaseWepMax]) + (self.AttackPower/14) * (self.WepAttackSpeed/10) )*1.1 # 10% increase from talents
        self.AttackSpeed = self.WepAttackSpeed * (1 - self.Haste/100) 
    
def simulate(inputs):
    Target = Boss(inputs["TargetStats"])
    Dolph = Character(Target, inputs["Stats"],inputs["Weapon"],inputs["Talents"],inputs["SetBonuses"])
    SS_Count, ES_Count, LS_Count = 0, 0, 0
    GlobalCooldown = 0
    SimTime = inputs["Sim"]["Time"]
    SimTime_Deciseconds = SimTime*10
    
    for t in range(SimTime_Deciseconds):
        
        Dolph.CharacterBuffs.checkBuffs()
        Dolph.UpdateStats()
        
        if Dolph.CharacterAttacks.SwingTimer >= Dolph.AttackSpeed:
            Dolph.CharacterAttacks.AutoAttack()
            
        if (Dolph.CharacterAttacks.Cooldowns["Bloodlust"] == 0 and GlobalCooldown == 0):
            Dolph.CharacterAttacks.Bloodlust()
            GlobalCooldown = GCD
            
        if (Dolph.CharacterAttacks.Cooldowns["Stormstrike"] == 0 and GlobalCooldown == 0):
            Dolph.CharacterAttacks.StormStrike()
            SS_Count += 1
            GlobalCooldown = GCD
            
        if (Dolph.CharacterAttacks.Cooldowns["Earth Shock"] == 0 and GlobalCooldown == 0):
            Dolph.CharacterAttacks.EarthShock()
            ES_Count += 1
            GlobalCooldown = GCD
            
        if (Dolph.CharacterAttacks.Cooldowns["Lightning Strike"] == 0 and GlobalCooldown == 0):
            Dolph.CharacterAttacks.LightningStrike()
            LS_Count += 1
            GlobalCooldown = GCD
            
        Dolph.CharacterAttacks.SwingTimer += 1
        
        Dolph.CharacterAttacks.ReduceCooldowns()
        
        if GlobalCooldown > 0: GlobalCooldown -= 1

    TotalDPS = 0
    for key in Dolph.CharacterAttacks.DamageCount.keys():
        Dolph.CharacterAttacks.DamageCount[key] /= SimTime_Deciseconds/10
        TotalDPS += Dolph.CharacterAttacks.DamageCount[key]
    
    return Dolph

def Gaussian(x,N,mu,sigma):
    return N * 1.0 / (np.sqrt(2*np.pi) * sigma) * np.exp( -0.5 * (x-mu)**2 / sigma**2)


def read_input(file):
    sections = {}
    current_section = None
    with open(file, 'r') as file:
        for line in file:
            line = line.strip()
            if re.match(r'^@\w+', line):
                current_section = line[1:].strip()
                sections[current_section] = {}
            elif line == '@':
                current_section = None  # End of a section
            elif current_section:
                match = re.match(r'^(.*?):\s*(.*)$', line)
                if match:
                    key, value = match.groups()
                    key = key.strip()
                    value = value.strip()
                    if "-" in value:
                        value = [int(x) for x in value.split("-")]
                    # Convert value to int or float if possible
                    elif re.match(r'^\d+$', value):
                        value = int(value)
                    elif re.match(r'^\d+\.\d+$', value):
                        value = float(value)
                    
                    sections[current_section][key] = value if value else None
    
    return sections

def write2file(file, NSIM, SIMTIME, DamageCount, BuffUptimes, AADiags):
    out = open(file,"w")
    out.write("|==================== TurtleSim ====================|\n\n")
    out.write(f"Number of simulations: {NSIM}\n")
    out.write(f"Simulation time [s]: {SIMTIME}\n\n")
    # Write damage 
    out.write("------------------- DPS overview -------------------\n")
    for key in DamageCount.keys():
        string = f"{DamageCount[key][0]:.2f}" 
        string2 = "+- " + f"{DamageCount[key][1]:.2f}"
        out.write(f"{key:<20}   {string:>10} {string2:>1}  ({(DamageCount[key][0]/DamageCount["Total DPS"][0]):.2%})\n")
        if key=="Total DPS": out.write("\n")
    out.write("----------------------------------------------------\n\n")
    out.write("------------------- Buff uptimes -------------------\n")
    for key in BuffUptimes.keys():
        string = f"{BuffUptimes[key][0]:.2f}" 
        string2 = "+- " + f"{BuffUptimes[key][1]:.2f}"
        out.write(f"{key:<25}   {string:>10}% {string2:>1}%\n")
    out.write("----------------------------------------------------\n\n")
    out.write("------------------- Auto attacks -------------------\n")
    for key in AADiags.keys():
        string = f"{AADiags[key][0]:.2f}" 
        string2 = "+- " + f"{AADiags[key][1]:.2f}"
        out.write(f"{key:<25}   {string:>10}% {string2:>1}%\n")
    out.write("----------------------------------------------------\n\n")

    out.close()

# def create_plots():
#     counts, bin_edges = np.histogram(sim_DPS,bins=nbins)
#     bin_centers = (bin_edges[:-1] + bin_edges[1:]) / 2
#     bin_centers = bin_centers[counts > 0]
#     counts = counts[counts > 0]
#     c = cost.LeastSquares(bin_centers,counts,np.sqrt(counts),Gaussian)
#     fit = Minuit(c,N=100,mu=np.mean(sim_DPS),sigma=np.std(sim_DPS,ddof=1))
#     fit.migrad()
#     xaxis = np.linspace(min(sim_DPS),max(sim_DPS),1000)
#     fig, ax = plt.subplots()
#     ax.plot(xaxis,Gaussian(xaxis,*fit.values),color="magenta")
#     ax.hist(sim_DPS,bins=nbins,color="darkturquoise",edgecolor="black")
#     ax.set_xlabel("DPS"   ,fontsize=15)
#     ax.set_ylabel("Counts",fontsize=15)
#     mean, std = fit.values["mu"], fit.values["sigma"]
#     plotinfo = [r"$\mu$ = " f"{mean:.0f}",
#                 r"$\sigma$ = " + f"{std:.0f}" ,
#                 r"$\chi^2 / N_{dof}$ = " + f"{fit.fval:.2f} / {fit.ndof}",
#                 f"p-value: {stats.chi2.sf(fit.fval,fit.ndof):.2f}"]
                
#     ax.text(0.6,0.7,"\n".join(plotinfo),transform=ax.transAxes,fontsize=11)
#     plt.tight_layout()
#     plt.savefig("Gaussian_DPS.png")
    
#     fig, ax = plt.subplots()
#     keys = list(DamageCounts.keys())
#     values = list(DamageCounts.values())
#     sorted_value_index = np.argsort(values)
#     sorted_dict = {keys[i]: values[i] for i in sorted_value_index}
    
#     Sources = sorted_dict.keys()
#     Colors = ["grey","yellow","dodgerblue","darkblue","darkturquoise"]
#     DamageDist = sorted_dict.values()
#     ax.bar(Sources, DamageDist)
#     ax.set_xticklabels(ax.get_xticklabels(), rotation=45)
#     plt.tight_layout()
#     plt.savefig("DPS_Dist.png")

def find_inp_files():
    directory = os.path.dirname(os.path.realpath(__file__))
    # List to store all the found .inp files
    inp_files = []
    
    # Loop through the files in the directory
    for file in os.listdir(directory):
        # Check if the file ends with .inp and is a file (not a directory)
        if file.endswith('.inp') and os.path.isfile(os.path.join(directory, file)):
            inp_files.append(file)
    
    return inp_files

def main():
    arguments = find_inp_files()
    for arg in arguments:
        outputfile = arg[:-4] + ".out"
        inputs = read_input(arg)
        NumSims = inputs["Sim"]["NumberSims"]
        SimTime = inputs["Sim"]["Time"]

        savedResults = {}
        for sim in range(NumSims):
            Dolph = simulate(inputs)
            savedResults[sim] = Dolph

        keys = Dolph.CharacterAttacks.DamageCount.keys()
        meanDPS = {"Total DPS" : np.zeros(2)}
        for key in keys:
            nums = np.zeros(NumSims)
            for sim in range(NumSims):
                nums[sim] = savedResults[sim].CharacterAttacks.DamageCount[key]
            meanDPS[key] = np.array([np.mean(nums), np.std(nums, ddof=1)/np.sqrt(NumSims)])
            meanDPS["Total DPS"] += np.array([np.mean(nums), np.std(nums, ddof=1)/np.sqrt(NumSims)**2])
        meanDPS["Total DPS"][1] = np.sqrt(meanDPS["Total DPS"][1])

        keys = Dolph.CharacterBuffs.BuffUptimes.keys()
        meanBuffUptimes = {}
        for key in keys:
            nums = np.zeros(NumSims)
            for sim in range(NumSims):
                nums[sim] = savedResults[sim].CharacterBuffs.BuffUptimes[key] / (SimTime*10) * 100
            meanBuffUptimes[key] = np.array([np.mean(nums), np.std(nums, ddof=1)/np.sqrt(NumSims)])

        keys = Dolph.CharacterAttacks.AutoAttackStats.keys()
        meanAAs = {}
        for key in keys:
            nums = np.zeros(NumSims)
            for sim in range(NumSims):
                nums[sim] = savedResults[sim].CharacterAttacks.AutoAttackStats[key] / savedResults[sim].CharacterAttacks.AttemptedHits["White Attacks"] * 100
                                                    
            meanAAs[key] = np.array([np.mean(nums), np.std(nums, ddof=1)/np.sqrt(NumSims)])
    
        write2file(outputfile, NumSims, SimTime, meanDPS, meanBuffUptimes, meanAAs)
    
if __name__ == "__main__":
    main()