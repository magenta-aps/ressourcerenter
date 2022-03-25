## Specifikation af koder i G69

Til koderne har vi 15 cifre til rådighed, og skal med dem dække alle kombinationer af:

### fiskeart
Vi har p.t. 11 fiskearter i systemet, men det kan blive relevant at tilføje flere med tiden.
Ved at afsætte 2 cifte til dette har vi plads til 100 fiskearter, hvilket burde være mere end
rigeligt.

### aktivitet
Aktiviteter såsom hvor fisk er fanget (havgående, kystnært, barentshavet). Vi har under ti af disse,
så det kan repræsenteres med ét ciffer.

### skatteår
To cifre burde være tilstrækkeligt, da vi tidligst kommer ind i en Y2K-situation i år 2100 
hvis vi vælger dette. Da vi dog har rigeligt med cifre at bruge af, og vi ikke bør gentage 
fejltagelsen der ledte op til Y2K uanset hvor sikre vi føler os, kan vi lige så godt anvende 
fire cifre.

### stedkode
Stedkoderne er fire cifre i datafordeleren, så det genbruger vi. 

Vi sammensætter disse talkoder i rækkefølge til én lang talsekvens, der udgør koden:

fiskeart (2 cifre) + aktivitet (1 ciffer) + skatteår (4 cifre) + stedkode (4 cifre)

* I alt 11 cifre, så vi foranstiller 4 nuller,
eller
* I alt 11 cifre, så vi anbringer et nul foran hver blok
