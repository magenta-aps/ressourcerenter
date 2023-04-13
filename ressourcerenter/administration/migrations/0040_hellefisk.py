from django.db import migrations


def get_skematype(apps, id):
    return apps.get_model('administration', 'SkemaType').objects.get(id=id)


def create_fiskeart(apps, navn_dk, navn_gl, pelagisk, skematype_ids, kode):
    FiskeArt = apps.get_model('administration', 'FiskeArt')
    fiskeart = FiskeArt.objects.create(
        navn_dk=navn_dk,
        navn_gl=navn_gl,
        pelagisk=pelagisk,
        kode=kode
    )
    fiskeart.skematype.set([get_skematype(apps, id) for id in skematype_ids])
    fiskeart.save()
    return fiskeart


def create_produkttype(apps, fiskeart, navn_dk, navn_gl, fartoej_groenlandsk=None, gruppe=None, aktivitetskode_alle=None, **kwargs):
    ProduktType = apps.get_model('administration', 'ProduktType')
    if aktivitetskode_alle is not None:
        kwargs.update({'aktivitetskode_havgående': aktivitetskode_alle, 'aktivitetskode_indhandling': aktivitetskode_alle, 'aktivitetskode_kystnært': aktivitetskode_alle})
    produkttype = ProduktType.objects.create(
        fiskeart=fiskeart,
        navn_dk=navn_dk,
        fartoej_groenlandsk=fartoej_groenlandsk,
        navn_gl=navn_gl,
        gruppe=gruppe,
        **kwargs
    )
    return produkttype


def create_produkttype_subtype(apps, parent, navn_dk, navn_gl):
    create_produkttype(
        apps,
        parent.fiskeart,
        ' - '.join([parent.navn_dk, navn_dk]),
        ' - '.join([parent.navn_gl, navn_gl]),
        gruppe=parent,
    )


def apply_migration(apps, schema_editor):
    FiskeArt = apps.get_model("administration", "FiskeArt")
    Afgiftsperiode = apps.get_model("administration", "Afgiftsperiode")
    SatsTabelElement = apps.get_model("administration", "SatsTabelElement")
    IndberetningLinje = apps.get_model("indberetning", "IndberetningLinje")
    havgående = create_fiskeart(
        apps,
        "Hellefisk - Indhandling fra havgående",
        "Hellefisk - Indhandling fra havgående",
        False,
        [2],
        6
    )
    kystnært = create_fiskeart(
        apps,
        "Hellefisk - Indhandling fra kystnært",
        "Hellefisk - Indhandling fra kystnært",
        False,
        [2],
        6
    )
    havgående_produkt = create_produkttype(
        apps,
        havgående,
        havgående.navn_dk, havgående.navn_gl,
        aktivitetskode_indhandling=10013,
    )
    kystnært_produkt = create_produkttype(
        apps,
        kystnært,
        kystnært.navn_dk, kystnært.navn_gl,
        aktivitetskode_indhandling=10013,
    )
    for produkt in (havgående_produkt, kystnært_produkt):
        create_produkttype_subtype(apps, produkt, 'Hel fisk', 'Iluitsuutillugit')
        create_produkttype_subtype(apps, produkt, 'Filet', 'Nerpiit saaneeraajakkat')
        create_produkttype_subtype(apps, produkt, 'Biprodukter', 'Saniatigut tunisassiat')
        fiskeart = produkt.fiskeart
        for periode in Afgiftsperiode.objects.all():
            for skematype in fiskeart.skematype.all():
                SatsTabelElement.objects.get_or_create(
                    skematype=skematype,
                    fiskeart=fiskeart,
                    periode=periode,
                    fartoej_groenlandsk=produkt.fartoej_groenlandsk,
                    rate_procent=5
                )

    # Fjern skematype 2 fra alm. hellefisk, og sæt dens aktivitetskode for indhandling til None
    hellefisk = FiskeArt.objects.get(navn_dk="Hellefisk")
    hellefisk.produkttype_set.update(aktivitetskode_indhandling=None)
    skematype = get_skematype(apps, 2)
    IndberetningLinje.objects.filter(
        produkttype__fiskeart=hellefisk,
        indberetning__skematype=skematype
    ).update(
        produkttype=havgående_produkt
    )
    hellefisk.skematype.remove(skematype)
    SatsTabelElement.objects.filter(
        skematype=skematype,
        fiskeart=hellefisk
    ).delete()


def revert_migration(apps, schema_editor):
    FiskeArt = apps.get_model("administration", "FiskeArt")
    ProduktType = apps.get_model('administration', 'ProduktType')
    SatsTabelElement = apps.get_model("administration", "SatsTabelElement")
    Afgiftsperiode = apps.get_model("administration", "Afgiftsperiode")
    fiskeart = FiskeArt.objects.filter(navn_dk__startswith="Hellefisk - Indhandling fra ")
    SatsTabelElement.objects.filter(fiskeart=fiskeart).delete()
    ProduktType.objects.filter(fiskeart=fiskeart).delete()
    fiskeart.delete()
    hellefisk = FiskeArt.objects.get(navn_dk="Hellefisk")
    hellefisk.produkttype_set.update(aktivitetskode_indhandling=10013)
    skematype = get_skematype(apps, 2)
    hellefisk.skematype.add(skematype)
    for periode in Afgiftsperiode.objects.all():
        SatsTabelElement.objects.get_or_create(
            skematype=skematype,
            fiskeart=hellefisk,
            periode=periode,
            fartoej_groenlandsk=None,
            rate_procent=5
        )


class Migration(migrations.Migration):

    dependencies = [
        ('administration', '0039_update_g69_fiskeartskode_overide'),
    ]

    operations = [
        migrations.RunPython(apply_migration, reverse_code=revert_migration)
    ]
