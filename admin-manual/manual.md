# Administration af Aalisakkat

Brugergrænsefladen til administrationssystemet har en række overordnede punkter i baren øverst, hvormed der kan navigeres til de relevante områder.
Hvert område har en vejledende tekst, der introducerer hvad siden gør.

## Centrale koncepter

Generelt gælder det i systemet, at der eksisterer en række fiskearter (f.eks. Sild, Torsk), og ud fra disse fiskearter er der en række produkttyper.

Der eksisterer også et antal afgiftsperioder, hver med en satstabel. Satstabellerne beskriver hvilke afgifter der skal være gældende for hver fiskeart.

Indberettere angiver i deres indberetningsformularer hvilken produkttype en fangst drejer sig om, og fangstafgiften beregnes ud fra opslag i den relevante satstabel.

Hver indberetning benytter en skematype, der bestemmer hvilke formularfelter og fiskearter der er relevante.

Skematyperne er:
- Havgående fartøjer og kystnære rejefartøjer - producerende fartøjer. Denne skematype bruges til eksportfiskeri, og der skal angives fartøjsnavn men ikke indhandlingssted.
- Indhandlinger - Indberetninger fra fabrikkerne / Havgående fiskeri og kystnært fiskeri efter rejer. Denne skematype bruges til indhandlinger, og der skal angives både fartøjsnavn og indhandlingssted.
- Kystnært fiskeri efter andre arter end rejer - indberetninger fra fabrikkerne. Denne skematype bruges til indhandling, og der skal kun angives indhandlingssted. Den er p.t. deaktiveret.

Indberetninger består af et antal indberetningslinjer, der repræsenterer en fangst af en enkelt produkttype, og har data som mængde og salgspris tilknyttet, samt den beregnede afgiftssats.


## Oplistning af indberetninger

Under punktet "Indberetninger" vises en liste af eksisterende indberetninger i systemet.
Listen kan afgrænses med formularen, hvor Afgiftsperiode, Beregningsmodel, Indberetningstidspunkt, CVR og Produkttype kan angives.
Hver indberetning i listen kan foldes ud ved at klikke på den, så de enkelte indberetningslinjer fremkommer.
Der kan også åbnes en detaljeside for hver indberetning, hvor yderligere detaljer vises, ved klik på knappen "Vis detaljer".


## Oprettelse af fakturaer

Under punktet "Fakturaer" er indberetningslinjer grupperet efter virksomheder. Hver virksomhed har et antal tabeller, én for hver indrapporteret fiskeart.
Tabellerne er yderligere opdelt i fangsttyper (havgående og indhandling).
Der oprettes en faktura pr. indberetningslinje, som automatisk sendes til Prisme.

Hvis der ønskes vist data for andre afgiftsperioder, kan det vælges i dropdown.


## Administration af virksomheder

Data om virksomheder vil normalt blive oprettet når der logges ind fra en ny virksomhed i indberetningsgrænsefladen, men administratoren kan også oprette dem eksplicit.
Hver virksomhed kan redigeres, så dens navn, kontaktoplysninger eller stedkode opdateres.

Administratoren kan også indtaste data på vegne af virksomheden, ved at vælge knappen "Repræsentér".
Der vil så skiftes til indberetningssiden, som den givne virksomhed ser den, og indberetninger kan oprettes og opdateres.
Ved klik på knappen "Afslut repræsentation" lukkes repræsentationssessionen ned, og man vender tilbage til listen af virksomheder.


## Statistik

Statistiksiden udtrækker summerede data for afstemte indberetninger, hvor der kan vælges hvilke parametre udtrækkene skal inddeles i og begrænses udfra.

For hver parameterboks kan der vælges et antal muligheder, som uddata vælges udfra.
Vælges der ikke nogen af mulighederne, foretages der ikke opsplitning på parameteren.

For eksempel kan der i boksen til Fiskeart vælges "Torsk". Da vil der kun medtages indberetningslinjer på torksefangster.
Hvis der vælges både "Torsk" og "Sej", medtages fangster af Torsk og Sej, opdelt i rækker for hver af disse fiskearter.
Vælges alle fiskearter kommer alle med, men fortsat opdelt i en række pr. fiskeart.

Vælges derimod ingen fiskearter, kommer fangster for alle fiskearter med, men ikke opdelt i rækker.

Felterne "År" og "Kvartal" er obligatoriske; hvis man ønsker at summere på tværs af disse, kan man vælge flere af dem.

Feltet "Enhed" er dog særligt; modsat ovenstående filtrering og opdeling bestemmer dette felt hvilke kolonner, der optræder i resultatet, og der skal altid vælges mindst én enhed.

Slutteligt kan resultatet downloades som Excel-regneark.
