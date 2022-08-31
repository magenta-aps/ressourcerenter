# Leverancetest

Denne leverancetestmanual beskriver alle de ting, der skal testes, for
at systemet til håndtering af Aalisakkat eller Ressourcerenter kan siges
at være funktionelt og brugbart for kunden.

Nogle af tingene, såsom NemID-login, kan pr. definition kun testes på et
produktionssetup som det, vi leverer til Skattestyrelsen i Grønland
(Akileraartarnermut Aqutsisoqarfik, forkortet AKA).

Testmanualen er opdelt i sektioner svarende til selve systemets
opdeling:

- Indberetning
- Administration
- Statistik

Disse tre områder skal bruges af tre forskellige kategorier af brugere,
nemlig

- virksomhedsbrugere, dvs. indberettere på indhandlingssteder, fabrikker mv.
- statistik-brugere bl.a. hos Grønlands StatistikA
- administratorer hos AKA

Administratorerne hos AKA vil have adgang til alle tre interfaces, men
statistik- og indberetnings-interfacet vil være helt det samme for
administratorer som for de øvrige brugere.

Meningen er som sagt, at leverancetesten vil dække _al_ den
funktionalitet, som er leveret til AKA. Enkelte detaljer omkring
formattering af output mv. kan være udeladt.

## Indberetning

Test cases:

* En virksomhed kan logge ind med NemID og få adgang til
  indberetningsdselen.
* Når en virksomhed logger ind i selvbetjeningen for første gang, vil
  den blive oprettet i systemet, og navn, kontaktoplysninger og adresse
  kan indtastes.
* Når en virksomhed logger ind i selvbetjeningen, får den adgang til en
  liste af sine egne tidligere indberetninger samt til at oprette nye
  indberetninger.
* 

## Administration

## Statistik


