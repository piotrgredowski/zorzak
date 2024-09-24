import datetime
import enum

import panel as pn
import pydantic

# Enable Panel extension for Jupyter Notebook (if you're using one)
pn.extension()


class AnalysisFileCategory(enum.StrEnum):
    pstats = enum.auto()


class AnalysisFile(pydantic.BaseModel):
    name: str
    category: AnalysisFileCategory
    date_uploaded: datetime.datetime


class AppState(pydantic.BaseModel):
    analysis_files: list[AnalysisFile] = []

    def add_analysis_file(self, name: str, category: AnalysisFileCategory):
        analysis_file = AnalysisFile(
            name=name, category=category, date_uploaded=datetime.datetime.now()
        )
        self.analysis_files.append(analysis_file)

    def remove_analysis_file(self, name: str):
        self.analysis_files = [
            analysis_file
            for analysis_file in self.analysis_files
            if analysis_file.name != name
        ]

    def get_analysis_files(self, category: AnalysisFileCategory):
        return [
            analysis_file
            for analysis_file in self.analysis_files
            if analysis_file.category == category
        ]


def get_servable_app():
    # Create a Panel widget

    app_state = AppState()

    # Create a Panel row
    row = pn.Row()

    # Create a Panel column
    column = pn.Column(row, row)

    # Create a file input widget
    file_input = pn.widgets.FileInput(name="Upload Analysis File")

    # Create a dropdown for file category
    category_input = pn.widgets.Select(
        name="Category", options=list(AnalysisFileCategory)
    )

    # Create a button to add the file
    add_button = pn.widgets.Button(
        name="Add File",
        button_type="primary",
    )

    # Define the callback function for the button
    def add_file(event):
        if file_input.filename and category_input.value:
            app_state.add_analysis_file(
                name=file_input.filename, category=category_input.value
            )
            file_input.filename = ""  # Clear the file input after adding
            category_input.value = None  # Clear the category input after adding

            print(file_input)

    # Attach the callback to the button
    add_button.on_click(add_file)

    # Add the widgets to the column
    column.append(file_input)
    column.append(category_input)
    column.append(add_button)

    app = pn.Column(column)

    # # Create a Panel tab
    # tabs = pn.Tabs(("Tab 1", column), ("Tab 2", column))

    # # Create a Panel app
    # app = pn.Column(tabs)

    app.servable()

    return app
