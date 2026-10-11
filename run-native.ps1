param([int]$Minimum=18,[int]$Terms=33,[double]$Seconds=300,[string]$Prefix='', [switch]$NoPrimePrune, [int]$Memo=200000)
$ErrorActionPreference='Stop'
$sourcePath=Join-Path $PSScriptRoot 'search-native.cs'
Add-Type -TypeDefinition (Get-Content -LiteralPath $sourcePath -Raw)
[int[]]$prefixValues=@()
if($Prefix){$prefixValues=@($Prefix.Split(',') | ForEach-Object {[int]$_})}
[NativeEgyptian]::Run($Minimum,$Terms,$Seconds,$prefixValues,(-not $NoPrimePrune),$Memo)
