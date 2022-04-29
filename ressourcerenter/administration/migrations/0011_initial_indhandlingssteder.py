from django.db import migrations


def apply_migration(apps, schema_editor):

    Indhandlingssted = apps.get_model('indberetning', 'Indhandlingssted')
    for stedkode, navn in (
            (10310, 'Nanortalik'),
            (10312, 'Aappilattoq ved Nanortalik'),
            (10320, 'Qaqortoq'),
            (10330, 'Narsaq'),
            (10331, 'Igaliku Kujalleq'),
            (10450, 'Paamiut'),
            (10451, 'Arsuk'),
            (10460, 'Nuuk'),
            (10461, 'Qeqertarsuatsiaat'),
            (10486, 'Kuummiut / Kuummiit'),
            (10570, 'Maniitsoq'),
            (10571, 'Atammik'),
            (10573, 'Kangaamiut'),
            (10580, 'Sisimiut'),
            (10583, 'Sarfannguaq / Sarfannguit'),
            (10601, 'Aasiaat'),
            (10603, 'Akunnaaq'),
            (10610, 'Qasigiannguit'),
            (10611, 'Ikamiut'),
            (10640, 'Qeqertarsuaq'),
            (10690, 'Kangaatsiaq'),
            (10692, 'Attu'),
            (10700, 'Avannaata Kommunia'),
            (10720, 'Ilulissat'),
            (10721, 'Oqaatsut'),
            (10722, 'Qeqertaq'),
            (10723, 'Saqqaq'),
            (10750, 'Uummannaq'),
            (10752, 'Qaarsut'),
            (10753, 'Ikerasak'),
            (10754, 'Saattut'),
            (10755, 'Ukkusissat'),
            (10760, 'Upernavik'),
            (10763, 'Aappilattoq ved Upernavik'),
            (10765, 'Tasiusaq-Nutaarmiut'),
            (10766, 'Nuussuaq'),
            (10767, 'Kullorsuaq'),
            (10769, 'Innaarsuit'),
            (10770, 'Qaanaaq'),
            (10779, 'Nutaarmiut'),
    ):
        Indhandlingssted.objects.update_or_create(
            stedkode=stedkode,
            defaults={'navn': navn}
        )


class Migration(migrations.Migration):

    dependencies = [
        ('administration', '0010_initial_data'),
    ]

    operations = [
        migrations.RunPython(apply_migration)
    ]
