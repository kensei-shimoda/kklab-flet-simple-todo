import flet as ft


class Task(ft.Column):
    def __init__(self, task_name, task_delete):
        super().__init__()
        self.completed = False
        self.flagged = False
        self.task_name = task_name
        self.task_delete = task_delete

    def build(self):
        self.display_task = ft.Checkbox(
            value=False, label=self.task_name, on_change=self.status_changed
        )
        self.edit_name = ft.TextField(expand=1)
        self.flag_button = ft.IconButton(
            icon=ft.Icons.FLAG_OUTLINED,
            tooltip="フラグ",
            on_click=self.flag_clicked,
        )

        self.display_view = ft.Row(
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
            controls=[
                self.display_task,
                ft.Row(
                    spacing=0,
                    controls=[
                        self.flag_button,
                        ft.IconButton(
                            icon=ft.Icons.CREATE_OUTLINED,
                            tooltip="編集",
                            on_click=self.edit_clicked,
                        ),
                        ft.IconButton(
                            ft.Icons.DELETE_OUTLINE,
                            tooltip="削除",
                            on_click=self.delete_clicked,
                        ),
                    ],
                ),
            ],
        )

        self.edit_view = ft.Row(
            visible=False,
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
            controls=[
                self.edit_name,
                ft.IconButton(
                    icon=ft.Icons.DONE_OUTLINE_OUTLINED,
                    icon_color=ft.Colors.GREEN,
                    tooltip="保存",
                    on_click=self.save_clicked,
                ),
            ],
        )
        self.controls = [self.display_view, self.edit_view]

    def flag_clicked(self, e):
        self.flagged = not self.flagged
        self.flag_button.icon = ft.Icons.FLAG if self.flagged else ft.Icons.FLAG_OUTLINED
        self.flag_button.icon_color = ft.Colors.RED if self.flagged else None
        self.flag_button.update()

    def edit_clicked(self, e):
        self.edit_name.value = self.display_task.label
        self.display_view.visible = False
        self.edit_view.visible = True

    def save_clicked(self, e):
        self.display_task.label = self.edit_name.value
        self.display_view.visible = True
        self.edit_view.visible = False

    def status_changed(self, e):
        self.completed = self.display_task.value

    def delete_clicked(self, e):
        self.task_delete(self)


class TodoApp(ft.Column):
    def build(self):
        self.new_task = ft.TextField(
            key="new_task",
            hint_text="タスクを入力してください",
            on_submit=self.add_clicked,
            expand=True,
        )
        self.tasks = ft.Column()

        self.tab_all = ft.Tab(label="タスク一覧 (0)")
        self.tab_active = ft.Tab(label="タスク (0)")
        self.tab_done = ft.Tab(label="完了 (0)")

        self.filter = ft.TabBar(
            scrollable=False,
            tabs=[self.tab_all, self.tab_active, self.tab_done],
        )

        self.filter_tabs = ft.Tabs(
            length=3,
            selected_index=0,
            on_change=lambda e: self.update(),
            content=self.filter,
        )

        self.flag_only = False
        self.flag_icon = ft.Icon(ft.Icons.FLAG_OUTLINED)
        self.flag_toggle = ft.TextButton(
            content=ft.Row([self.flag_icon, ft.Text("フラグのみ表示")]),
            on_click=self.toggle_flag_filter,
        )

        self.width = 600
        self.controls = [
            ft.Row(
                [ft.Text(value="タスクまる見え", theme_style=ft.TextThemeStyle.HEADLINE_MEDIUM)],
                alignment=ft.MainAxisAlignment.CENTER,
            ),
            ft.Row(
                controls=[
                    self.new_task,
                    ft.FloatingActionButton(
                        key="add_task",
                        icon=ft.Icons.ADD,
                        on_click=self.add_clicked,
                    ),
                ],
            ),
            ft.Column(
                spacing=25,
                controls=[
                    self.filter_tabs,
                    self.flag_toggle,
                    self.tasks,
                    ft.Row(
                        alignment=ft.MainAxisAlignment.END,
                        controls=[
                            ft.OutlinedButton(
                                content="完了済みを削除", on_click=self.clear_clicked
                            ),
                        ],
                    ),
                ],
            ),
        ]

    async def add_clicked(self, e):
        if self.new_task.value:
            task = Task(self.new_task.value, self.task_delete)
            self.tasks.controls.append(task)
            self.new_task.value = ""
            self.update()

    def task_delete(self, task):
        self.tasks.controls.remove(task)

    def clear_clicked(self, e):
        for task in self.tasks.controls[:]:
            if task.completed:
                self.task_delete(task)

    def toggle_flag_filter(self, e):
        self.flag_only = not self.flag_only
        self.flag_icon.name = ft.Icons.FLAG if self.flag_only else ft.Icons.FLAG_OUTLINED
        self.flag_toggle.content.controls[1].value = "全タスク表示" if self.flag_only else "フラグのみ表示"
        self.update()

    def before_update(self):
        status = self.filter.tabs[self.filter_tabs.selected_index].label.split(" (")[0]
        total = len(self.tasks.controls)
        active = sum(1 for t in self.tasks.controls if not t.completed)
        done = sum(1 for t in self.tasks.controls if t.completed)
        self.tab_all.label = f"タスク一覧 ({total})"
        self.tab_active.label = f"タスク ({active})"
        self.tab_done.label = f"完了 ({done})"
        for task in self.tasks.controls:
            tab_match = (
                status == "タスク一覧"
                or (status == "タスク" and not task.completed)
                or (status == "完了" and task.completed)
            )
            task.visible = tab_match and (not self.flag_only or task.flagged)
            task.opacity = 0.4 if (status == "タスク一覧" and task.completed) else 1.0


def main(page: ft.Page):
    page.title = "タスクまる見え"
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    page.scroll = ft.ScrollMode.ADAPTIVE
    page.add(ft.SafeArea(content=TodoApp()))


if __name__ == "__main__":
    ft.run(main)
