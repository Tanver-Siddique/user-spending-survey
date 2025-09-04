# main.py
import flet as ft
import asyncio
from Title_animation import GradientAnimatedTextContainer
from data import start_text


class Survey(ft.Container):
    def __init__(self, page: ft.Page):
        super().__init__(bgcolor=ft.Colors.BLACK, expand=True, padding=5)
        self.page = page
        self.language = "en"
        self.current_page = "intro"
        self.question_manager = None
        self.is_completed = False

        self.title_text = GradientAnimatedTextContainer(
            value="Desires After Duties",
            font_family="title_font",
            no_wrap=False
        )

        self.language_slider = ft.SegmentedButton(
            selected={"0"},
            allow_multiple_selection=False,
            style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=5)),
            segments=[
                ft.Segment(value="0", label=ft.Text("Eng")),
                ft.Segment(value="1", label=ft.Text("বাংলা")),
            ],
            on_change=self.change_language,
            col={"xs": 6, "sm": 3, "md": 2, "lg": 2},
        )

        self.main_content_controls = ft.Column(
            spacing=8, 
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            scroll=ft.ScrollMode.AUTO,  # Added scroll for mobile devices
        )

        self.main_content_container_column = ft.Column(
            expand=True,
            alignment=ft.MainAxisAlignment.CENTER,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            controls=[
                ft.ResponsiveRow(
                    alignment=ft.MainAxisAlignment.CENTER,
                    vertical_alignment=ft.CrossAxisAlignment.CENTER,
                    controls=[
                        ft.Column(
                            col={"xs": 12, "sm": 12, "md": 4, "lg": 4},
                            alignment=ft.MainAxisAlignment.CENTER,
                            controls=[
                                ft.Container(
                                    bgcolor=ft.Colors.WHITE,
                                    padding=ft.padding.all(10),
                                    content=self.main_content_controls,
                                    # Set width for larger screens, but not for mobile
                                    width=600 if not self._is_mobile_device() else None,
                                )
                            ],
                        )
                    ],
                )
            ],
        )

        self.content = ft.Column(
            expand=True,
            controls=[
                ft.Divider(color=ft.Colors.TRANSPARENT, height=1),
                ft.ResponsiveRow(
                    alignment=ft.MainAxisAlignment.CENTER,
                    vertical_alignment=ft.CrossAxisAlignment.CENTER,
                    controls=[
                        ft.Column(
                            col={"xs": 12},
                            alignment=ft.MainAxisAlignment.CENTER,
                            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                            controls=[self.title_text],
                        )
                    ],
                ),
                ft.Divider(color=ft.Colors.TRANSPARENT, height=5),
                ft.ResponsiveRow(
                    controls=[self.language_slider],
                    alignment=ft.MainAxisAlignment.CENTER,
                    expand=False,
                ),
                ft.Divider(height=2, color=ft.Colors.TRANSPARENT),
                self.main_content_container_column,
            ],
        )

        self._refresh_content()

    def _create_intro_controls(self):
        t = start_text[self.language]
        return [
            ft.Text(
                value=t["welcome"],
                size=25,
                font_family="Arial",
                weight=ft.FontWeight.BOLD,
                color=ft.Colors.BLUE_GREY_900,
                text_align=ft.TextAlign.CENTER,  # Center align for mobile
            ),
            ft.Text(
                value=t["request"], 
                size=20, 
                color=ft.Colors.BLUE_GREY_500,
                text_align=ft.TextAlign.CENTER,  # Center align for mobile
            ),
            ft.Text(
                value=t["description"],
                size=12,
                color=ft.Colors.BLACK,
                text_align=ft.TextAlign.JUSTIFY,
            ),
            ft.Row(
                alignment=ft.MainAxisAlignment.SPACE_EVENLY,
                controls=[
                    ft.Row(
                        spacing=4,
                        controls=[
                            ft.Icon(name=ft.Icons.TIMER_ROUNDED, color=ft.Colors.BLACK),
                            ft.Text(
                                value=t["time"],
                                weight=ft.FontWeight.BOLD,
                                size=12,
                                color=ft.Colors.BLACK,
                            ),
                        ],
                    ),
                    ft.Row(
                        spacing=4,
                        controls=[
                            ft.Icon(
                                name=ft.Icons.ENHANCED_ENCRYPTION_ROUNDED,
                                color=ft.Colors.BLACK,
                            ),
                            ft.Text(
                                value=t["anonymous"],
                                weight=ft.FontWeight.BOLD,
                                size=12,
                                color=ft.Colors.BLACK,
                            ),
                        ],
                    ),
                ],
            ),
            ft.Divider(),
            ft.ElevatedButton(
                text=t["button"],
                bgcolor=ft.Colors.BLUE_GREY_200,
                color=ft.Colors.BLACK,
                style=ft.ButtonStyle(
                    shape=ft.RoundedRectangleBorder(radius=5),
                    # Add padding for better touch targets on mobile
                    padding=ft.padding.all(12) if self._is_mobile_device() else ft.padding.all(8)
                ),
                on_click=self.clicked_start_survey,
            ),
        ]

    def _is_mobile_device(self):
        """Check if the user is on a mobile device based on user agent."""
        user_agent = (self.page.client_user_agent or "").lower()
        mobile_keywords = ['android', 'iphone', 'ipad', 'ipod', 'blackberry', 
                          'windows phone', 'mobile', 'webos', 'opera mini']
        return any(keyword in user_agent for keyword in mobile_keywords)

    def _create_questionnaire_controls(self):
        from survey import general_info_questions

        if self.question_manager is None:
            self.question_manager = general_info_questions(
                self.page, self.language, on_complete=self.on_survey_complete
            )
            return [self.question_manager.main_container]
        else:
            self.question_manager.update_language(self.language)
            return [self.question_manager.main_container]

    def _refresh_content(self):
        self.main_content_controls.controls.clear()
        if self.current_page == "intro":
            self.main_content_controls.controls.extend(self._create_intro_controls())
        elif self.current_page == "questionnaire":
            self.main_content_controls.controls.extend(self._create_questionnaire_controls())
        self.page.update()

    def on_survey_complete(self):
        self.is_completed = True

    def change_language(self, e):
        selected_value = list(e.control.selected)[0]
        self.language = "en" if selected_value == "0" else "bn"

        if self.question_manager:
            self.question_manager.update_language(self.language)
        else:
            self._refresh_content()

    def on_view_change(self, e):
        # Responsive title size using page.width
        w = getattr(self.page, "width", 800) or 800
        size = 50
        if w < 600:
            size = 25
        elif w < 900:
            size = 40
        if hasattr(self.title_text, "text_control"):
            self.title_text.text_control.size = size

        # Also allow the question manager to react to page height/width changes
        if self.question_manager:
            try:
                # call a new on_view_change on the QuestionManager (see survey.py changes)
                self.question_manager.on_view_change()
            except Exception:
                # keep UI resilient — don't crash on unexpected resize logic
                pass

        self.page.update()

    def clicked_start_survey(self, e):
        self.current_page = "questionnaire"
        self._refresh_content()


# --------- MAIN ENTRY POINT ----------
def main(page: ft.Page):
    page.title = "Survey"
    page.spacing = 0
    page.padding = 0
    page.fonts = {
        "title_font": "ZenDots-Regular.ttf"
    }
    page.theme = ft.Theme(
        scrollbar_theme=ft.ScrollbarTheme(
            thumb_color={
                ft.ControlState.HOVERED: ft.Colors.BLACK,
                ft.ControlState.DEFAULT: ft.Colors.BLACK87,
            },
            track_color=ft.Colors.GREY_800,
            thickness=10,
            radius=5,
            interactive=True,
        )
    )

    # This function will reset and build the survey UI
    def initialize_survey(e=None):
        page.controls.clear()  # Clear any existing controls
        
        survey_container = Survey(page)
        page.on_resized = survey_container.on_view_change
        page.add(survey_container)

        # Animate gradient
        if hasattr(survey_container.title_text, "animate_gradient_task"):
            page.run_task(survey_container.title_text.animate_gradient_task)
        
        # Trigger initial responsive layout
        survey_container.on_view_change(None)
        
        page.update()

    # Assign the reset function to the on_connect event
    page.on_connect = initialize_survey

    # Call the function once to build the UI for the very first connection
    initialize_survey()


if __name__ == "__main__":
    ft.app(
        target=main,
        assets_dir="assets",
        # view=ft.AppView.WEB_BROWSER  # Ensure it opens in web browser mode
    )