# Converts the configuration_properties_docs.csv file to
# a markdown file containing a single table.

from pathlib import Path


def _convert():
    docs = Path('./configuration_properties_docs.csv')
    if not docs.is_file():
        raise Exception(f'Could not find input csv file in expected location of [{docs}].')

    with open(docs, 'r', encoding='utf-8') as file:
        lines = [line.strip() for line in file.readlines()]

    markdown = Path(__file__).absolute().parent.parent.joinpath('ConfigurationProperties.md')
    if markdown.is_file():
        markdown.unlink()

    with open(markdown, 'w', encoding='utf-8') as file:
        file.write(_to_markdown_line(lines[0]))
        file.write(_create_heading_separator(lines[0]))
        for i in range(1, len(lines)):
            file.write(_to_markdown_line(lines[i]))


def _to_markdown_line(line: str) -> str:
    parts = line.split(',')
    return '|' + '|'.join(parts) + '|\n'


def _create_heading_separator(header_line: str) -> str:
    parts = header_line.split(',')
    underlines = ['---' for _ in range(len(parts))]
    return '|' + '|'.join(underlines) + '|\n'


if __name__ == '__main__':
    _convert()
