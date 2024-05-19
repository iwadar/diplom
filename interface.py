import flet as ft
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
    Tab
)


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


    t = ft.Tabs(
        selected_index=1,
        animation_duration=300,
        tabs=[
            ft.Tab(
                icon=ft.icons.STORAGE, 
                text="База данных",
                content=ft.Container(
                    content=Column([
                        ft.Row(
                            controls=[
                            ft.FloatingActionButton("Добавить слово", icon="add"),
                            ft.FloatingActionButton("Изменить слово", icon="update"),
                            ft.FloatingActionButton("Удалить слово", icon="remove"),
                            ],
                        ),
                        ft.DataTable(
                            columns=[
                                ft.DataColumn(ft.Text("Запретное слово")),
                                ft.DataColumn(ft.Text("Замена")),
                                ft.DataColumn(ft.Text("Количество референсов"), numeric=True),
                            ],
                            rows=[
                                ft.DataRow(
                                    cells=[
                                        ft.DataCell(ft.Text("John")),
                                        ft.DataCell(ft.Text("Smith")),
                                        ft.DataCell(ft.Text("43")),
                                    ],
                                ),
                        ],
                    ),
                    ],
                ),
                    margin=20,
                    padding=20,
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
                    content=ft.ProgressBar(width=400, color="amber", bgcolor="#eeeeee"), 
                    alignment=ft.alignment.center
                ),
            ),
            ft.Tab(
                icon=ft.icons.ANALYTICS, 
                text="Статистика",
                content=ft.Text("This is Tab 3"),
            ),
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