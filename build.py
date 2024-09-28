import click

from buildutils import BuildConfiguration
from buildutils.plugins import (
    CoveragePlugin,
    FlakePlugin,
    GenericCommandPlugin,
    GenericCleanPlugin,
    EnsureVenvActivePlugin,
    alias,
    group
)


@click.command()
@click.option('--profile', '-pr')
@click.option('--plugins', '-p')
@click.option('--list-plugins', '-l', is_flag=True)
def main(profile: str, plugins: str, list_plugins: bool):
    (
        BuildConfiguration()
        .config('build.ini')
        .plugins(
            EnsureVenvActivePlugin(),
            GenericCleanPlugin('CLEAN', 'Remove previous build files.'),
            GenericCommandPlugin('INSTALL', 'Install required dependencies from requirements.txt file.'),
            GenericCommandPlugin('AUDIT', 'Audit the dependencies in the requirements.txt file for vulnerabilities.'),
            FlakePlugin(),
            CoveragePlugin(),
            alias(
                'integration-test',
                GenericCommandPlugin(
                    'INTEGRATION',
                    'Run integration tests with no code coverage analysis.'
                )
            ),
            group(
                'generate-docs',
                GenericCommandPlugin('PREPARE_DOCS', 'Prepare Sphinx for generating documentation from inline comments.'),
                GenericCommandPlugin('GENERATE_DOCS', 'Generate documentation from inline comments using Sphinx')
            )
        )
        .build(profile, plugins, list_plugins)
    )


if __name__ == '__main__':
    main()
