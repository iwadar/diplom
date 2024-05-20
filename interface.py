import flet as ft
from databases import *
from multiprocessingDasha import *
from flet import (
    AppBar,
    Icon,
    IconButton,
    Page,
    PopupMenuButton,
    PopupMenuItem,
    Text,
    colors,
    icons,
    theme,
    Container,
    Column,
    margin,
    Tab,
    TextField,
    FilePicker,
    Checkbox,
    Row
)

db = Database()

def main(page: Page):

    def close_dlg_program(e):
        dlg_program.open = False
        page.update()

    def close_dlg_author(e):
        dlg_author.open = False
        page.update()

    dlg_program = ft.AlertDialog(
        modal=True,
        title=ft.Text("Информация о программе"),
        content=ft.Text("ПРОГРАММА ЕПТА"),
        actions=[
            ft.TextButton("Yes", on_click=close_dlg_program),
        ],
        actions_alignment=ft.MainAxisAlignment.END,
        on_dismiss=lambda e: print("Modal dialog dismissed!"),
    )

    def open_dlg_program(e):
        page.dialog = dlg_program
        dlg_program.open = True
        page.update()

    dlg_author = ft.AlertDialog(
        modal=True,
        title=ft.Text("Информация об авторе"),
        content=ft.Text("Я БЛЯТЬ"),
        actions=[
            ft.TextButton("Yes", on_click=close_dlg_author),
        ],
        actions_alignment=ft.MainAxisAlignment.END,
        on_dismiss=lambda e: print("Modal dialog dismissed!"),
    )

    def open_dlg_author(e):
        page.dialog = dlg_author
        dlg_author.open = True
        page.update()

    page.appbar = AppBar(
        leading=Icon(icons.AUDIOTRACK, color=ft.colors.GREY_50, size=30),
        leading_width=40,
        title=Text("TalkSlang Audio Translator", theme_style=ft.TextThemeStyle.HEADLINE_SMALL),
        center_title=True,
        bgcolor=colors.TEAL_ACCENT_700,
        actions=[
            PopupMenuButton(
                items=[
                    PopupMenuItem(text="Информация о программе", on_click=open_dlg_program),
                    PopupMenuItem(),  # divider
                    PopupMenuItem(text="Информация о авторе", on_click=open_dlg_author),
                ]
            ),
        ],
    )


    #### База данных

    def selectedall(e):
        pass

    dataBase = ft.DataTable(
                            columns=[
                                ft.DataColumn(Column([
                                    ft.Text(""),
                                    # Checkbox(value=False, on_change=selectedall)
                                
                                ])),
                                ft.DataColumn(ft.Text("ID"), numeric=True),
                                ft.DataColumn(ft.Text("Запретное слово")),
                                ft.DataColumn(ft.Text("Замена")),
                                ft.DataColumn(ft.Text("Количество референсов"), numeric=True),
                            ],
                            rows=[
                                # ft.DataRow(
                                #     cells=[
                                #         ft.DataCell(ft.Text("John")),
                                #         ft.DataCell(ft.Text("Smith")),
                                #         ft.DataCell(ft.Text("43")),
                                #     ],
                                # ),
                                #     ft.DataRow(
                                #     cells=[
                                #     ft.DataCell(ft.Text("Jack")),
                                #     ft.DataCell(ft.Text("Brown")),
                                #     ft.DataCell(ft.Text("19")),
                                #     ],
                                #     ),
                        ],
            )

    ### Файловый диалог

    def on_dialog_file(e):
        if file_pickle.result and file_pickle.result.files:
            print('tyt')
            textFiledFile.value = file_pickle.result.files[0].path
            textFiledFile.update()

    file_pickle = ft.FilePicker(on_result=on_dialog_file)
    page.overlay.append(file_pickle)

    fileButton = ft.ElevatedButton('Выберите файл', on_click=lambda e:file_pickle.pick_files(allow_multiple=False))

    textFiledWord = TextField(label="Слово")
    textFiledReplace = TextField(label="Аналог")
    textFiledFile = TextField(label="Файл", read_only=True)


    content_to_add_data = [
        #  textFiledWord, 
         fileButton,
         textFiledFile,
         textFiledReplace
        ]
    
    content_to_upd_data = [
            textFiledWord, 
            textFiledReplace
            ]
    


    def common_close_dlg_add():
        # textFiledWord.value = ''
        textFiledReplace.value = ''
        textFiledFile.value = ''

        dlg_add.open = False
        page.update()

    def close_dlg_add(e):
        common_close_dlg_add()

    selected_row = []
    
    def this_selected(e):
        id = e.control.data[0]
        word = e.control.data[1]
        replace = e.control.data[2]
        if e.control.value:
            selected_row.append((id, word, replace))
        else:
            for c in selected_row:
                if c[0] == id:
                    selected_row.remove(c)
        

    def select_data_from_bd():
        print('select ')
        db.connect()
        listResult = db.selectForInterface()
        dataBase.rows = []
        for item in listResult:
            dataBase.rows.insert(len(dataBase.rows), 
                                    ft.DataRow(cells=[
                                                    ft.DataCell(Checkbox(value=False, 
                                                                        on_change=this_selected,
                                                                        data=[item[0], item[1], item[2]])),
                                                    ft.DataCell(ft.Text(item[0])), 
                                                    ft.DataCell(ft.Text(item[1])), 
                                                    ft.DataCell(ft.Text(item[2])),
                                                    ft.DataCell(ft.Text(item[3]))
                                                    ],
                                                    selected=True
                                                    )) 
        db.disconnect()

    select_data_from_bd()

    def add_btn(e):
            if (textFiledReplace.value or textFiledFile.value):
                print('start add')
                db.insertFromInterface(fileName=textFiledFile.value, replacement=textFiledReplace.value)
                select_data_from_bd()
            # dataBase.rows.insert(len(dataBase.rows), 
            #                             ft.DataRow(cells=[ft.DataCell(ft.Text("1")), 
            #                                         ft.DataCell(ft.Text(f"First_name")), 
            #                                         ft.DataCell(ft.Text(f"Last_name"))
            #                                         ],)) 
            common_close_dlg_add()


    dlg_add = ft.AlertDialog(
            modal=True,
            title=ft.Text("Добавить экземпляр слова"),
            content=ft.Column(content_to_add_data),
            actions=[
                ft.TextButton("Добавить", on_click=add_btn),
                ft.TextButton("Отмена", on_click=close_dlg_add),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
            on_dismiss=lambda e: print("Modal dialog dismissed!"),
        )

    def open_dlg_add(e):
        page.dialog = dlg_add
        dlg_add.open = True
        page.update()


    def delete_item(e):

        db.connect()
        db.deleteDataFromInterface(selected_row)
        db.disconnect()

        dataBase.rows.clear()
        select_data_from_bd()
        selected_row.clear()
        page.update()


    def common_close_dlg_upd():
        textFiledWord.value = ''
        textFiledReplace.value = ''
        dlg_upd.open = False
        page.update()


    def close_dlg_upd(e):
        common_close_dlg_upd()
        dlg_upd.open = False
        page.update()


    def upd_btn(e):
        if (textFiledReplace.value or textFiledWord.value):
                print('start update')
                db.connect()
                db.updateDataInInerface(textFiledWord.value, textFiledReplace.value)
                db.disconnect()
                select_data_from_bd()
        common_close_dlg_upd()


    dlg_upd = ft.AlertDialog(
            modal=True,
            title=ft.Text("Изменить слова"),
            content=ft.Column(content_to_upd_data),
            actions=[
                ft.TextButton("Добавить", on_click=upd_btn),
                ft.TextButton("Отмена", on_click=close_dlg_upd),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
            on_dismiss=lambda e: print("Modal dialog dismissed!"),
        )   


    def open_dlg_update(e):
        page.dialog = dlg_upd
        dlg_upd.open = True
        page.update()


    dataBaseButton = [
        ft.Container(
            content=ft.FloatingActionButton("Добавить слово", icon="add", on_click=open_dlg_add),
            alignment=ft.alignment.center,
            border_radius=ft.border_radius.all(5),
            expand=True,
            margin=10,
            padding=10,
        ),
        ft.Container(
            content=ft.FloatingActionButton("Изменить слово", icon="update", on_click=open_dlg_update),
            alignment=ft.alignment.center,
            border_radius=ft.border_radius.all(5),
            expand=True,
            margin=10,
            padding=10
        ),
        ft.Container(
            content=ft.FloatingActionButton("Удалить слово", icon="remove", on_click=delete_item),
            alignment=ft.alignment.center,
            border_radius=ft.border_radius.all(5),
            expand=True,
            margin=10,
            padding=10
        )
    ]

    
    dataBasePage = [   
        ft.Row(spacing=5, controls=dataBaseButton),
        ft.Container(
                    content=ft.Column([dataBase], scroll= ft.ScrollMode.ALWAYS),
                    alignment=ft.alignment.top_center,
                    border_radius=ft.border_radius.all(10),
                    expand=True,
                    # bgcolor=ft.colors.AMBER_100,
                    margin=10,
        ),
        
        ]


    def cls_success(e):
        textFiledFile.value = ''
        buttonStartTranslate.disabled = False
        fileButton.disabled = False
        dlg_success.open = False
        page.update()

    progresBar = ft.ProgressBar(width=500, color="amber", bgcolor="#eeeeee", visible=False)

    dlg_success = ft.AlertDialog(
            modal=True,
            title=ft.Text("Перевод завершен!"),
            content=ft.Text("Поздравляю! Ваше аудио сохранено по адресу..."),
            actions=[
                ft.TextButton("Ура", on_click=cls_success),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
            on_dismiss=lambda e: print("Modal dialog dismissed!"),
        )

    def startTranslate(e):
        if (textFiledFile.value):
            progresBar.visible=True
            buttonStartTranslate.disabled = True
            fileButton.disabled = True
            proga = ParallelFind(textFiledFile.value)
            proga.findAndReplaceWords()
            progresBar.visible=False
            page.dialog = dlg_success
            dlg_success.open = True
            page.update()

    buttonStartTranslate = ft.ElevatedButton('Начать перевод', on_click=startTranslate)


    translatePage = [   
        ft.Column(spacing=5, controls=[
                fileButton,
                textFiledFile,
                buttonStartTranslate,
                progresBar
            ]
        ),
        # ft.Container(
        #             content=ft.Column([dataBase], scroll= ft.ScrollMode.ALWAYS),
        #             alignment=ft.alignment.top_center,
        #             border_radius=ft.border_radius.all(10),
        #             expand=True,
        #             # bgcolor=ft.colors.AMBER_100,
        #             margin=10,
        # ),
        
        ]




    t = ft.Tabs(
        selected_index=1,
        animation_duration=300,
        tabs=[
            ft.Tab(
                icon=ft.icons.STORAGE, 
                text="База данных",
                content=ft.Container(
                    content=Column(spacing=0, controls=dataBasePage),
                    margin=20,
                    padding=30,
                    alignment=ft.alignment.center,
                    bgcolor=ft.colors.GREEN_ACCENT_100,
                    border_radius=20,
                    expand=True 
                )
            ),
            ft.Tab(
                icon=ft.icons.TRANSLATE,
                #icon=ft.icons.GRAPHIC_EQ,
                text="TalkSlang",
                content=ft.Container(
                    content=Column(spacing=0, controls=translatePage), 
                    margin=20,
                    padding=30,
                    alignment=ft.alignment.center,
                    bgcolor=ft.colors.GREEN_ACCENT_100,
                    border_radius=20,
                    expand=True 
                )
            ),
            # ft.Tab(
            #     icon=ft.icons.ANALYTICS, 
            #     text="Статистика",
            #     content=ft.Text("This is Tab 3"),
            # ),
        ],
        expand=1,
        scrollable=True
    )
    
    # page.add(
    #     Container(
    #         content=Column([
    #             tab_1,
    #             tab_2,
    #             tab_3,
    #             ],
    #             alignment=ft.MainAxisAlignment.CENTER,
    #             horizontal_alignment=ft.CrossAxisAlignment.CENTER,),
    #         margin=20,
    #         padding=20,
    #         alignment=ft.alignment.center,
    #         bgcolor=ft.colors.GREEN_ACCENT_100,
    #         border_radius=20,
    #         expand=True
    #         ),
    #     )
    
    page.add(t)
    # page.theme = theme.Theme(color_scheme_seed="green")
    page.update()


ft.app(target=main)