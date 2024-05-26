import flet as ft
from databases import *
from multiprocessingDasha import *
from threading import Thread
import copy
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
        content=ft.Text("""
TalkSlang – это инструмент, который помогает вам сделать ваш аудиоконтент более профессиональным и доступным. Загружайте аудиофайл и программа автоматически обнаружит сленговые слова. Вы можете:

1. Заменить сленг голосом говорящего, сохраняя естественность речи.
2. Добавить новые сленговые слова в словарь программы.
3.  Удалить нежелательные слова из аудио.
4.  Изменить сленговые слова на более формальные варианты.

TalkSlang идеально подходит для:

1.  Подкастеров, которые хотят сделать свой контент более привлекательным для широкой аудитории.
2.  Преподавателей, которые хотят использовать аудиоматериалы в учебных целях.
3.  Любого, кто хочет улучшить качество своего аудиоконтента.

TalkSlang – это простой и удобный в использовании инструмент, который поможет вам сделать ваш аудиоконтент идеальным!
"""),
        actions=[
            ft.TextButton("Принято!", on_click=close_dlg_program),
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
        content=ft.Text("Автор: Иванченко Дарья Владимировна\nГруппа: М8О-410Б-20\nПочта: ivanchenko-darya@inbox.ru"),
        actions=[
            ft.TextButton("Спасибо!", on_click=close_dlg_author),
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

    dataBase = ft.DataTable(
                            columns=[
                                ft.DataColumn(Column([ft.Text("")])),
                                # ft.DataColumn(ft.Text("ID"), numeric=True),
                                ft.DataColumn(ft.Text("Запретное слово")),
                                ft.DataColumn(ft.Text("Замена")),
                                ft.DataColumn(ft.Text("Количество референсов"), numeric=True),
                            ],
                            rows=[],
            )
    
    listSlangWord = []

    ### Файловый диалог

    def on_dialog_file(e):
        if file_pickle.result and file_pickle.result.files:
            textFiledFile.value = file_pickle.result.files[0].path
            textFiledFile.update()

    file_pickle = ft.FilePicker(on_result=on_dialog_file)


    textFieldFileTranslate = TextField(label="Файл", read_only=True)

    def on_dialog_file_translate(e):
        if file_pickle_translate.result and file_pickle_translate.result.files:
            textFieldFileTranslate.value = file_pickle_translate.result.files[0].path
            textFieldFileTranslate.update()

    file_pickle_translate = ft.FilePicker(on_result=on_dialog_file_translate)

    page.overlay.append(file_pickle)
    page.overlay.append(file_pickle_translate)

    fileButtonTranslate = ft.ElevatedButton('Выберите файл', on_click=lambda e:file_pickle_translate.pick_files(allow_multiple=False))

    fileButton = ft.ElevatedButton('Выберите файл', on_click=lambda e:file_pickle.pick_files(allow_multiple=False))

    textFiledWord = TextField(label="Слово")
    textFiledReplace = TextField(label="Аналог")
    textFiledFile = TextField(label="Файл", read_only=True)


    content_to_add_data = [
        #  textFiledWord,
        ft.Text("Вам необходимо выбрать аудиофайл. \nЕго название должно быть в формате <категория_вес.wav>. \nНапример, cringe_0.8.wav. \nВес может быть от 0.01 до 1."),

         fileButton,
         textFiledFile,
         textFiledReplace
        ]
    
    dropDown = ft.Dropdown()

    content_to_upd_data = [
            ft.Text("Выберите слово и внесите его аналог на русском языке."),
            dropDown,
            # textFiledWord, 
            textFiledReplace
            ]
    
    def fillDataDropDown():
        print(listSlangWord)
        dropDown.options = []
        for word in listSlangWord:
            dropDown.options.append(ft.dropdown.Option(word))
        page.update()


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
        if e.control.value:
            selected_row.append(tuple(e.control.data))
        else:
            for c in selected_row:
                if c[0] == e.control.data[0]:
                    selected_row.remove(c)
        

    def select_data_from_bd():
        db.connect()
        listResult = db.selectForInterface()
        dataBase.rows = []
        listSlangWord.clear()
        print(listSlangWord)
        for item in listResult:
            listSlangWord.append(item[1])
            dataBase.rows.insert(len(dataBase.rows), 
                                    ft.DataRow(cells=[
                                                    ft.DataCell(Checkbox(value=False, 
                                                                        on_change=this_selected,
                                                                        data=item
                                                                        )),
                                                    # ft.DataCell(ft.Text(item[0])), 
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
        if selected_row:
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
        if (textFiledReplace.value or dropDown.value):
                
        # if (textFiledReplace.value or textFiledWord.value):
                print('start update')
                db.connect()
                db.updateDataInInerface(dropDown.value, textFiledReplace.value)
                # db.updateDataInInerface(textFiledWord.value, textFiledReplace.value)
                db.disconnect()
                select_data_from_bd()
        common_close_dlg_upd()


    dlg_upd = ft.AlertDialog(
            modal=True,
            title=ft.Text("Изменить слова"),
            content=ft.Column(content_to_upd_data),
            actions=[
                ft.TextButton("Изменить", on_click=upd_btn),
                ft.TextButton("Отмена", on_click=close_dlg_upd),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
            on_dismiss=lambda e: print("Modal dialog dismissed!"),
        )   


    def open_dlg_update(e):
        fillDataDropDown()

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


    def action():
        progresBar.visible=not(progresBar.visible)
        buttonStartTranslate.disabled = not(buttonStartTranslate.disabled)
        fileButtonTranslate.disabled = not(fileButtonTranslate.disabled)
        page.update()

    fileNameResult = ['']

    def cls_success(e):
        textFieldFileTranslate.value = ''
        dlg_success.open = False
        page.update()
        fileNameResult = ['']

    progresBar = ft.ProgressBar(width=page.window_width, color="amber", bgcolor="#eeeeee", visible=False, bar_height=8)
    text_result_field = ft.Text("")

    dlg_success = ft.AlertDialog(
            modal=True,
            title=ft.Text("Перевод завершен!"),
            content=text_result_field,
            actions=[
                ft.TextButton("Ура", on_click=cls_success),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
            on_dismiss=lambda e: print("Modal dialog dismissed!"),
        )

    def functionInThread():
        print('start translate')
        proga = ParallelFind(textFieldFileTranslate.value)
        fileNameResult.append(proga.findAndReplaceWords())
        # fileNameResult.append(proga.test())
        del proga
        print('end translate')


    def startTranslate(e):
        if (textFieldFileTranslate.value):
            action()
            th = Thread(target=functionInThread)
            th.start()
            # proga = ParallelFind(textFieldFileTranslate.value)
            # # proga.findAndReplaceWords()
            # progresBar.visible=False
            th.join()
            action()
            if fileNameResult[-1]:
                if fileNameResult[-1].endswith('.wav'):
                    text_result_field.value = "Поздравляю! Ваше аудио сохранено по адресy " + str(fileNameResult[-1])
                else:
                    text_result_field.value = str(fileNameResult[-1])
            else:
                text_result_field.value = "К сожалению, не удалось перевести аудио :(\nВозникли технические проблемы.\nВы можете связаться с автором работы для решения проблем!"
            # print(text_result_field)
            page.dialog = dlg_success
            dlg_success.open = True
            page.update()

    buttonStartTranslate = ft.ElevatedButton('Начать перевод', on_click=startTranslate)


    translatePage = [   
        ft.Column(spacing=5, controls=[
                fileButtonTranslate,
                textFieldFileTranslate,
                buttonStartTranslate,
                progresBar
            ]
        ),        
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
        ],
        expand=1,
        scrollable=True
    )
    page.add(t)
    page.update()


ft.app(target=main)