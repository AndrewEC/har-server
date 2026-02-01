# Converts the configuration_properties_docs.csv file to
# a markdown file containing a single table.

from pathlib import Path


_DESTINATION_NAME = 'ConfigurationProperties.md'
_TEMP_NAME = 'temp-ConfigurationProperties.md'


def _convert():
    docs = Path('./configuration_properties_docs.csv').absolute()
    if not docs.is_file():
        raise Exception(f'Could not find input csv file in expected location of [{docs}].')

    print(f'Reading contents of csv file: [{docs}].')
    with open(docs, 'r', encoding='utf-8') as file:
        lines = [line.strip() for line in file.readlines()]

    markdown = Path(__file__).absolute().parent.parent.joinpath(_TEMP_NAME)
    if markdown.is_file():
        markdown.unlink()

    print(f'Writing markdown contents to: [{markdown}].')
    with open(markdown, 'w', encoding='utf-8') as file:
        file.write(_to_markdown_line(lines[0]))
        file.write(_create_heading_separator(lines[0]))
        for i in range(1, len(lines)):
            file.write(_to_markdown_line(lines[i]))

    final_destination = markdown.parent.joinpath(_DESTINATION_NAME)
    if final_destination.is_file():
        print(f'Removing old markdown file from: [{final_destination}].')
        final_destination.unlink()

    print(f'Renaming [{_TEMP_NAME}] to [{_DESTINATION_NAME}].')
    markdown.rename(final_destination)


def _to_markdown_line(line: str) -> str:
    parts = line.split(',')
    return '|' + '|'.join(parts) + '|\n'


def _create_heading_separator(header_line: str) -> str:
    parts = header_line.split(',')
    underlines = ['---' for _ in range(len(parts))]
    return '|' + '|'.join(underlines) + '|\n'


if __name__ == '__main__':
    _convert()
