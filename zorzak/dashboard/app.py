import pathlib
import typing as t

import arrow
import loguru
import panel as pn
import pydantic
from loguru import logger

from zorzak.common.files import AnalysisFile, AnalysisFileCategory
from zorzak.common.observer import BaseSubscriber, SimplePublisher
from zorzak.common.renderer import get_renderers

pn.extension()


class AppState(pydantic.BaseModel):
    model_config = pydantic.ConfigDict(arbitrary_types_allowed=True)

    analysis_files: list[AnalysisFile] = []
    logger: t.Any = pydantic.Field(default_factory=lambda: loguru.logger)

    analysis_files_publisher: SimplePublisher = pydantic.Field(
        default_factory=SimplePublisher
    )

    def add_analysis_file(
        self, name: str, category: AnalysisFileCategory, content: bytes
    ):
        analysis_file = AnalysisFile(
            name=name,
            category=category,
            content=content,
        )
        self.analysis_files_publisher.publish(analysis_file)
        self.logger.info(f"Analysis file added: '{analysis_file.name}'")

    def get_analysis_files(
        self, category: AnalysisFileCategory | None = None
    ) -> list[AnalysisFile]:
        files = self.analysis_files_publisher.get_all_data()
        if category is None:
            return files
        return [
            analysis_file
            for analysis_file in files
            if analysis_file.category == category
        ]


class AnalysisFileSubscriber(BaseSubscriber):
    def __init__(self, app_view: "AppView"):
        self._app_view = app_view

    def update(self, message: AnalysisFile) -> None:
        del message
        self._app_view.render_analysis_files()


class AppView:
    _analysis_files: list[AnalysisFile]
    _analysis_file_subscriber: t.Any

    def __init__(self, logger: t.Any, analysis_files: list[AnalysisFile] | None = None):
        self.logger = logger

        self.main_container = pn.Row()
        self.left_column = pn.Column()
        self.right_column = pn.Column()

        self.main_container.extend([self.left_column, self.right_column])

        self.file_input = pn.widgets.FileInput(name="Upload Analysis File")

        self.category_input = pn.widgets.Select(
            name="Category", options=list(AnalysisFileCategory)
        )
        self.add_file_button = pn.widgets.Button(name="Add File", button_type="primary")

        self.add_file_button.on_click(self.add_file_handler)

        self.left_column.extend(
            [self.file_input, self.category_input, self.add_file_button]
        )
        self.app_state = AppState(logger=logger, analysis_files=[])

        self._analysis_file_subscriber = AnalysisFileSubscriber(app_view=self)
        self.app_state.analysis_files_publisher.attach(self._analysis_file_subscriber)

        analysis_files = analysis_files or []
        for file_ in analysis_files:
            self.app_state.add_analysis_file(
                name=file_.name, category=file_.category, content=file_.content
            )

    def render_analysis_files(self):
        less_than_one_day_diff = all(
            [
                (arrow.now() - f.date_uploaded).days < 1
                for f in self.app_state.get_analysis_files()
            ]
        )

        should_use_short_date = less_than_one_day_diff
        tabs = []
        for file_ in self.app_state.get_analysis_files():
            # tab_name =
            if should_use_short_date:
                tab_name = f"{file_.get_date_uploaded_short()} {file_.name}"
            else:
                tab_name = f"{file_.get_date_uploaded_long()} {file_.name}"

            renderers = get_renderers(file_.category)

            tab_content = []

            for renderer in renderers:
                tab_content.append((renderer.__name__, renderer(pstats_file=file_)))

            if len(tab_content) > 1:
                tab_content = pn.Tabs(*tab_content, tabs_location="above")
            else:
                tab_content = tab_content[0][1]
            tabs.append((tab_name, pn.Column(tab_content)))

        self.right_column.clear()
        self.right_column.append(pn.Tabs(*tabs, tabs_location="left"))

    def add_file_handler(self, event):
        self.logger.debug(event)
        self.file_input.filename = t.cast(str, self.file_input.filename)
        self.file_input.name = t.cast(str, self.file_input.name)
        if self.file_input.filename and self.category_input.value:
            content = pathlib.Path(self.file_input.filename).read_bytes()
            self.app_state.add_analysis_file(
                name=self.file_input.filename,
                category=self.category_input.value,
                content=content,
            )

    def servable(self):
        self.main_container.servable()
        return self.main_container


def _get_dummy_analysis_files():
    filename = "_profile_data.profile.pstats"
    content = pathlib.Path(filename).read_bytes()
    analysis_files = [
        AnalysisFile(
            name=filename,
            category=AnalysisFileCategory.pstats,
            content=content,
        )
    ]
    return analysis_files


def get_servable_app():
    app_view = AppView(logger=logger, analysis_files=_get_dummy_analysis_files())
    app_view.servable()

    return app_view
