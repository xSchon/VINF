import PySimpleGUI as sg

from searcher import Searcher

sg.theme('DarkBlue13')   

def find_fields_to_search(values, search_names, filter_amount) -> list:
    csv_columns = ['Team', 'PlayerName', 'HistoryText', 'PlayerCard', 'TournamentResults', 'ChampionsStats', 'BirthCountry', 'Age', 'Role', 'Sports', 'CountryInfo', 'InfoBox']
    search_fields = []
    search_values = []
    for i in range(filter_amount):
        idx = i+1
        field = values[f'combo{idx}']
        value = values[f'{idx}']
        
        if field == '' or value == '':
            continue
        # Age is stored as a float, convert and check input
        if field == 'Age':
            try:
                value = str(float(value))
            except:
                pass

        search_fields.append(field)
        search_values.append(value)

    for rep in range(len(search_fields)):
        mapped = search_names.index(search_fields[rep])
        search_fields[rep] = csv_columns[mapped]


    return(search_fields, search_values)

def create_gui():
    search_names = ['Team', 'Player Name', 'History Text', 'Player Card', 'Tournaments', 'Champions', 'Country', 'Age', 'Role', 'Country Sports', 'Country Info', 'Country Box']
    search_arrays = 1

    layout = [
        [sg.Text('Search', justification='center')],
        [sg.Text('Filters dependency: '), sg.Button("OR", key="type_button", button_color=("white", "blue"))],
        [sg.Column([[sg.Text('Field: '), sg.Combo(search_names, key='combo1', readonly=True), sg.Text('Filter: '), sg.InputText(key='1', size=(15,20))]], key='-Column-')],
        [sg.Button('Search'), sg.Button('Add filter'), sg.Button('Clear output'), sg.Button('Close'), 
        sg.Text('   Results amount:'), sg.Combo(['5', '10', '25', '50', 'All'], readonly=True, key='amount', default_value='5')],
        

        # Select what will be shown in the output
        [sg.Text('Select what information you want to see in the output: ')],
        [sg.Checkbox('Team name', key='Team', default=True),
        sg.Checkbox('Player name', key='PlayerName', default=True), 
        sg.Checkbox('Played since', key='Since'),
        sg.Checkbox('Played till', key='Till'), 
        sg.Checkbox('Team History', key='TeamHistory'), 
        sg.Checkbox('Player History Text', key='HistoryText'),
        sg.Checkbox('Player Card', key='PlayerCard')],
        [sg.Checkbox('Tournaments', key='TournamentResults'), 
        sg.Checkbox('Champions', key='ChampionsStats'),
        sg.Checkbox('Country', key='BirthCountry', default=True), 
        sg.Checkbox('Age', key='Age'), 
        sg.Checkbox('Role', key='Role'),
        sg.Checkbox('Country Sports', key='Sports'),
        sg.Checkbox('Country Info', key='InfoBox'),
        sg.Checkbox('Country Box', key='CountryIntro')],

        [sg.Text('Player Information')],
        [sg.Output(size=(180, 40), key='outp')]  # Output element to display search results
        
    ]

    # Start the window
    window = sg.Window('League of Legends pro players information', layout)
    searcher = Searcher()


    while True:
        event, values = window.read()
        if event == sg.WIN_CLOSED or event == 'Close': # if user closes window or clicks cancel
            break

        if event == 'Clear output':
            # Clear window for output
            window.FindElement('outp').Update('')
            continue
        
        if event == 'Add filter':
            # Add new row of filter possibilities, up to 8 filters in one app
            if search_arrays == 8:
                print("Maximum amount of filters reached")
                continue
            search_arrays += 1
            window.extend_layout(window['-Column-'], [[sg.Text('Field: '), sg.Combo(search_names, readonly=True, key=f'combo{str(search_arrays)}'), 
                                                        sg.Text('Filter: '), sg.InputText(key=str(search_arrays), size=(15,20))]])
            continue
        
        if event == "type_button":
            # Toggle the button state between filter type OR/AND
            current_state = window["type_button"].GetText()
            new_state = "AND" if current_state == "OR" else "OR"
            window["type_button"].update(text=new_state)
            continue

        # Select which values to show in search
        checkbox_keys = ['Team','PlayerName','Since','Till','TeamHistory','HistoryText','PlayerCard','TournamentResults',
        'ChampionsStats','BirthCountry','Age' ,'Role','Sports','InfoBox','CountryIntro']
        results_show = []
        for key in checkbox_keys:
            if(values[key]):
                results_show.append(key)

        # Get search filters and results based on those filters
        search_fields, search_values = find_fields_to_search(values, search_names, search_arrays)
        if(len(search_fields) > 0):
            strings_to_print = searcher.search_index(fields_to_search=search_fields, queries=search_values, results_amount=values['amount'], 
                                                        search_type=window["type_button"].GetText(), printable_cols=results_show)

             
        for record in strings_to_print:
            print(record)
        print()
        

    window.close()


create_gui()

