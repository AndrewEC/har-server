import click

from buildutils import BuildConfiguration
from buildutils.plugins import (
    CoveragePlugin,
    FlakePlugin,
    GenericCommandPlugin,
    GenericCleanPlugin,
    EnsureVenvActivePlugin,
    alias
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
            FlakePlugin(),
            CoveragePlugin(),
            alias(
                'integration-test',
                GenericCommandPlugin(
                    'INTEGRATION',
                    'Run integration tests with no code coverage analysis.'
                )
            ),
            GenericCommandPlugin('AUDIT', 'Audit the dependencies in the requirements.txt file for vulnerabilities.')
        )
        .build(profile, plugins, list_plugins)
    )


if __name__ == '__main__':
    main()
