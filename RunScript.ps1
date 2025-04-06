param(
    [ValidateSet(
        "Activate",
        "All",
        "Audit",
        "Flake",
        "Install",
        "IntegrationTests",
        "Tests"
    )]
    [string]$ScriptAction
)

Import-Module ./PyBuildScripts

Invoke-ActivateScript

switch ($ScriptAction) {
    "All" {
        Invoke-InstallScript
        Invoke-FlakeScript
        Invoke-TestScript 80 {
            coverage run `
                --omit=./server/tests/* `
                --source=server.core `
                --branch `
                --module server.tests.__run_all
        }
        Invoke-OtherScript "Running integration tests" @(0) {
            python -m unittest server.tests.integration.integration_test
        }
        Invoke-AuditScript
    }
    "Audit" { Invoke-AuditScript }
    "Flake" { Invoke-FlakeScript }
    "Install" { Invoke-InstallScript }
    "IntegrationTests" {
        Invoke-OtherScript "Running integration tests" @(0) {
            python -m unittest server.tests.integration.integration_test
        }
    }
    "Tests" {
        Invoke-TestScript 80 {
            coverage run `
                --omit=./server/tests/* `
                --source=server.core `
                --branch `
                --module server.tests.__run_all
        }
    }
}
