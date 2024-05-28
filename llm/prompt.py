folio_example = """
<NL>
All iPhones are electronic.
Some phones are iPhones.
</NL>
<FOL>
∀x (IPhone(x) → Electronic(x))
∃x (Phone(x) ∧ IPhone(x))
</FOL>
<NL>
Some fish may sting.
Stonefish is a fish.
It stings to step on a stonefish.
Stonefish stings cause death if not treated.
To treat stonefish stings, apply heat to the affected area or use an antivenom.
</NL>
<FOL>
∃x ∃y (Fish(x) → Sting(x,y))
Fish(stonefish)
∀x (StepOn(stonefish, x) → Sting(stonefish, x))
∀x (Sting(stonefish, x) ∧ ¬Treated(x) → CauseDeath(x))
∀x (Sting(stonefish, x) ∧ (ApplyHeat(x) ∨ UseAntivenom(x)) → Treated(x))
</FOL>
<NL>
System 7 is a UK-based electronic dance music band.
Steve Hillage and Miquette Giraudy formed System 7.
Steve Hillage and Miquette Giraudy are former members of the band Gong.
Electric dance music bands are bands.
System 7 has released several club singles.
Club singles are not singles.
</NL>
<FOL>
BasedOn(system7, uk) ∧ ElectronicDanceMusicBand(system7)
Formed(stevehillage, system7) ∧ Formed(miquettegiraudy, system7)
FormerMemberOf(stevehillage, gong) ∧ FormerMemberOf(miquettegiraudy, gong)
∀x (ElectronicDanceMusicBand(x) → Band(x))
∃x (ClubSingle(x) ∧ Released(system7, x))
∀x (ClubSingle(x) → ¬Single(x))
</FOL>
<NL>
Westworld is an American science fiction-thriller TV series.
In 2016, a new television series named Westworld debuted on HBO.
The TV series Westworld is adapted from the original film in 1973, which was written and directed by Michael Crichton.
The 1973 film Westworld is about robots that malfunction and begin killing the human visitors.
</NL>
<FOL>
TVSeries(westworld) ∧ American(westworld) ∧ ScienceFictionThriller(westworld)
Debut(westworld, year2016)
∃x (Adapt(westworld, x) ∧ Produce(x, year1973) ∧ Write(michael, x) ∧ Direct(michael, x))
About(westworld, robots)
</FOL>
"""

proofwriter_example = """
<NL>
The lion is nice
If someone is red and nice then they are kind
If the lion is kind then the lion is round
</NL>
<FOL>
Nice(lion)
∀x ((Red(x) ∧ Nice(x)) → Kind(x))
(Kind(lion) → Round(lion))
</FOL>
<NL>
The rabbit is big
The rabbit is cold
The rabbit is rough
The rabbit is round
The rabbit is young
If someone is round and not big then they are not rough
</NL>
<FOL>
Big(rabbit)
Cold(rabbit)
Rough(rabbit)
Round(rabbit)
Young(rabbit)
∀x (Round(x) ∧ ¬Big(x) → ¬Rough(x))
</FOL>"""