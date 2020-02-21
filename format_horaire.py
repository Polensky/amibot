import texttable as tt


def print_horaire(jour, heure, lieu):

    if heure[:2] == '08':
        periode = 1
    elif heure[:2] == '12':
        periode = 2
    elif heure[:2] == '15':
        periode = 3
    elif heure[:2] == '19':
        periode = 4

    if jour == 'lundi':
        le_jour = 1
    elif jour == 'mardi':
        le_jour = 2
    elif jour == 'mercredi':
        le_jour = 3
    elif jour == 'jeudi':
        le_jour = 4
    elif jour == 'vendredi':
        le_jour = 5

    horaire_template = [['           ','Lundi','Mardi','Mercredi', 'Jeudi', 'Vendredi'],
                        ['08h30-11h30','     ','     ','        ', '     ', '        '],
                        ['12h00-15h00','     ','     ','        ', '     ', '        '],
                        ['15h30-18h30','     ','     ','        ', '     ', '        '],
                        ['19h00-22h00','     ','     ','        ', '     ', '        '],]

    horaire_template[periode][le_jour] = lieu
    table = tt.Texttable()
    table.set_chars(['⋯','|','⊕','⋯'])
    table.add_rows(horaire_template)
    return table.draw()
