$ErrorActionPreference = "Stop"
$Repo = ".cache/eel_vm"
$Commit = "284b3da00af91efc3aff6bfc1acefb4e801a8ad6"

if (-not (Test-Path $Repo)) {
    git clone https://github.com/james34602/EEL_VM.git $Repo
}
git -C $Repo fetch origin
git -C $Repo checkout $Commit

$Solution = Join-Path $Repo "CLI/eel_CLI.sln"
msbuild $Solution /m /p:Configuration=Release /p:Platform=x64

$Exe = Get-ChildItem $Repo -Recurse -Filter "eel_CLI.exe" |
    Where-Object { $_.FullName -match "Release" } |
    Select-Object -First 1
if (-not $Exe) {
    throw "eel_CLI.exe was not produced by the upstream build"
}
Write-Output $Exe.FullName
