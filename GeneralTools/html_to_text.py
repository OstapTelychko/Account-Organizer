from html.parser import HTMLParser
from typing import Literal, cast

NEW_LINE_TAG = "br"
TAGS_TO_REMOVE = ("span",)

ALIGNMENTS = Literal['left', 'center', 'right']


class HTMLToTextParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.text_parts:list[str] = []
        self.max_line_width = 50

        #Handle table tag (transaction)
        self.in_table = False
        self.in_table_row = False
        self.in_table_cell = False

        self.table_row_cells:list[dict[str, str|int]] = []
        self.table_cell_data = ""
        self.table_cell_width = ""
        self.table_cell_align:ALIGNMENTS = 'left'


    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag == NEW_LINE_TAG:
            self.text_parts.append("\n")
        elif tag == "table":
            self.in_table = True
        elif tag == "tr":
            self.in_table_row = True
            self.table_row_cells = []
        elif tag == "td":
            self.in_table_cell = True

            attr_dict = dict(attrs)
            self.table_cell_data = ""

            width = attr_dict["width"]
            if not width:
                raise ValueError(f"Table cell width must be in percentage. Got {width} instead.")
            self.table_cell_width = width.strip('%')

            align = attr_dict.get("align", "left")
            self.table_cell_align = cast(ALIGNMENTS, align)


    def handle_data(self, data: str) -> None:
        if self.in_table_cell:
            self.table_cell_data = data
        elif not self.in_table:
            self.text_parts.append(data)


    def handle_endtag(self, tag: str) -> None:
        if tag == "td":
            self.in_table_cell = False
            self.table_row_cells.append({
                "data": self.table_cell_data,
                "width": self.table_cell_width,
                "align": self.table_cell_align
            })
        elif tag == "tr":
            self.in_table_row = False
            self.text_parts.append(f"{self.format_table_row(self.table_row_cells)}\n")
        elif tag == "table":
            self.in_table = False
        

    def format_table_row(self, cells: list[dict[str, str|int]]) -> str:
        row_text = ""
        for cell in cells:
            data = str(cell["data"])
            width = int(int(cell["width"]) * self.max_line_width / 100)
            align = cell["align"]

            if align == 'left':
                formatted_data = data.ljust(width)
            elif align == 'center':
                formatted_data = data.center(width)
            elif align == 'right':
                formatted_data = data.rjust(width)
            else:
                formatted_data = data.ljust(width)

            row_text += formatted_data

        return row_text


    def get_text(self) -> str:
        return ''.join(self.text_parts)
    

def html_to_text(html: str) -> str:
    """Convert HTML content to plain text.

    Args:
        html (str): The HTML content to convert.

    Returns:
        str: The converted plain text.
    """

    if not isinstance(html, str):
        raise TypeError(f"Input must be a string. Got {type(html)} instead.")
    
    html_parser = HTMLToTextParser()
    html_parser.feed(html)
    text = html_parser.get_text()

    return text