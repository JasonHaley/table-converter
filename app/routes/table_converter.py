"""Routes for the table converter skill."""

import json
import itertools

from markdown_it import MarkdownIt
from bs4 import BeautifulSoup
from fastapi import APIRouter, Header
from pydantic import BaseModel

from app.skill import SkillInput, SkillInputRecord, SkillIssue, SkillOutput, SkillOutputRecord

__all__ = ("router",)

SKILL_TIMEOUT = 230  # max timeout for a custom skill


class TableConverterInput(BaseModel):
    """Input data for the table converter model."""

    text: str | None


class TableConverterInputRecord(SkillInputRecord[TableConverterInput]):
    """Individual input record for the table converter model."""


class TableConverterOutput(BaseModel):
    """Output data from the table converter model."""

    text: str | None


class TableConverterOutputRecord(SkillOutputRecord[TableConverterOutput]):
    """Individual output record from the table converter model."""


class TableConverterInput(SkillInput[TableConverterInputRecord]):
    """Input for the table converter skill."""


class TableConverterSkillOutput(SkillOutput[TableConverterOutputRecord]):
    """Output for the table converter skill."""


router = APIRouter()


@router.post("/convert")
async def convert(body: TableConverterInput) -> TableConverterSkillOutput:
    """Convert tables to JSON."""
    
    inputs_without_text = tuple(input_data for input_data in body.values if not input_data.data.text)
    inputs_with_text = tuple(input_data for input_data in body.values if input_data.data.text)

    modified_text = (
        markdown_tables_to_json_and_replace(input_data.data.text)
        for input_data in inputs_with_text
    )

    return TableConverterSkillOutput(
        values=tuple(
            itertools.chain(
                (
                    TableConverterOutputRecord(
                        record_id=input_data.record_id,
                        data=TableConverterOutput(text=modified_text),
                    )
                    for input_data, modified_text in zip(inputs_with_text, modified_text)
                ),
                (
                    TableConverterOutputRecord(
                        record_id=input_data.record_id,
                        data=TableConverterOutput(text=None),
                        warnings=(SkillIssue(message="No input text provided."),),
                    )
                    for input_data in inputs_without_text
                ),
            ),
        ),
    )

def expand_row(row):
    """Expand cells with colspan > 1"""
    expanded = []
    for cell in row:
        text = cell.get_text(strip=True)
        colspan = int(cell.get("colspan", 1))
        expanded.extend([text] * colspan)
    return expanded


def flatten_headers(header_rows):
    """Flatten multi-row headers into a single header row"""
    max_len = max(len(row) for row in header_rows)
    flat_headers = ['' for _ in range(max_len)]
    for row in header_rows:
        for idx, col in enumerate(row):
            flat_headers[idx] = (flat_headers[idx] + ' ' + col).strip()
    return flat_headers


def parse_html_table(table):
    header_rows = []

    # Try to collect rows with <th> as headers
    for tr in table.find_all("tr"):
        if tr.find("th"):
            expanded = expand_row(tr.find_all(["th", "td"]))
            header_rows.append(expanded)
        else:
            break

    if header_rows:
        flat_headers = flatten_headers(header_rows)
        data_start_index = len(header_rows)
    else:
        flat_headers = []
        data_start_index = 0

    # Parse body rows
    body_rows = []
    trs = table.find_all("tr")[data_start_index:]
    for tr in trs:
        cells = expand_row(tr.find_all(["td", "th"]))
        if not cells:
            continue
        if not flat_headers:
            flat_headers = [f"Column {i+1}" for i in range(len(cells))]
        
        row = {}
        header_counts = {}
    
        for header, cell in zip(flat_headers, cells):
            if header in header_counts:
                header_counts[header] += 1
                row[f"{header} {header_counts[header]}"] = cell
            else:
                header_counts[header] = 0
                row[header] = cell
    
        body_rows.append(row)

    return body_rows


def markdown_tables_to_json_and_replace(md_text: str) -> str:
    trimmed_md_text = md_text.replace('\r\n', '').replace('\n', '')
    md = MarkdownIt().enable('table')
    html = md.render(trimmed_md_text)
    soup = BeautifulSoup(html, "html.parser")
    tables = soup.find_all("table")

    for table in tables:
        json_table = parse_html_table(table)
        json_str = json.dumps(json_table, indent=2)

        # Replace table HTML in markdown text with its JSON representation
        trimmed_md_text = trimmed_md_text.replace(str(table), f"\n```json\n{json_str.replace('\n', '')}\n```\n")

    return trimmed_md_text

