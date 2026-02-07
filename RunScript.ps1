param(
    [ValidateSet(
        "Activate",
        "All",
        "Audit",
        "Lint",
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
        Invoke-RuffScript
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
    "Lint" { Invoke-RuffScript }
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
