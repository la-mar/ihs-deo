

# param (
$project_dir=$args[0]
$api=$args[1]
# $step=$args[0]
# )

Set-Location -Path $project_dir
Write-host "Current Working Directory is: $project_dir"


New-Variable -Name exe -Value .\DriftwoodDigest.exe
# New-Variable -Name main_path -Value
# Write-host "Virtualenv path is: $env_path"
# Write-host "Working directory is:""$PWD"
# Write-host "Entrypoint path is: $main_path"
& $exe -a $api; Exit-PSSession
# & echo 'yep'; Exit-PSSession




