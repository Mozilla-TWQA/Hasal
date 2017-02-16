# color for text
function Write-Color([String[]]$Text, [ConsoleColor[]]$Color = "White", [int]$StartTab = 0, [int] $LinesBefore = 0,[int] $LinesAfter = 0) {
    $DefaultColor = $Color[0]
    if ($LinesBefore -ne 0) {  for ($i = 0; $i -lt $LinesBefore; $i++) { Write-Host "`n" -NoNewline } } # Add empty line before
    if ($StartTab -ne 0) {  for ($i = 0; $i -lt $StartTab; $i++) { Write-Host "`t" -NoNewLine } }  # Add TABS before text
    if ($Color.Count -ge $Text.Count) {
        for ($i = 0; $i -lt $Text.Length; $i++) { Write-Host $Text[$i] -ForegroundColor $Color[$i] -NoNewLine } 
    } else {
        for ($i = 0; $i -lt $Color.Length ; $i++) { Write-Host $Text[$i] -ForegroundColor $Color[$i] -NoNewLine }
        for ($i = $Color.Length; $i -lt $Text.Length; $i++) { Write-Host $Text[$i] -ForegroundColor $DefaultColor -NoNewLine }
    }
    Write-Host
    if ($LinesAfter -ne 0) {  for ($i = 0; $i -lt $LinesAfter; $i++) { Write-Host "`n" } }  # Add empty line after
}

# validation of jenkin slave
$jenkins = (NET START | FINDSTR "jenkinsslave-C__Jenkins")
If ($lastexitcode -notmatch 0) {
    Try {
        $state = (CMD /C 'SC QUERY jenkinsslave-C__Jenkins | FINDSTR STATE').split(" ")[-2]
        Write-Color "[ERROR] Jenkins Slave Services Not Running" -Color Red
        Write-Color "[ERROR] Current Jenkins Slave Services Status: $state" -Color Red
        Write-Color "<Instruction>" -Color White
        "    If the state is STOPPED, you need to restart it."
        "    In PowerShell:   Restart-Service jenkinsslave-C__Jenkins"
        "    In Command Line: sc start jenkinsslave-C__Jenkins"
        ""
        "    If it doesn't work, just remove current service and reinstall it."
        "    In PowerShell: "
        "        `$service = Get-WmiObject -Class Win32_Service -Filter ""Name='jenkinsslave-C__Jenkins'"""
        "        `$service.delete()"
        "    In Command Line: sc delete jenkinsslave-C__Jenkins"
        Write-Color "<End of Instruction>" -Color White
    } Catch {
        Write-Color "[ERROR] Jenkins Slave Services Not Installed" -Color Red
        Write-Color "<Instruction>" -Color White
        "    Please try to install the jenkins slave services from jenkins server."
        Write-Color "<End of Instruction>" -Color White
    }
} Else {
    $jenkins = $jenkins.replace(" ", "")
    Write-Color "[INFO] Jenkins Slave Services Found: $jenkins" -Color Green
}

# check for space
$disk = Get-WmiObject Win32_LogicalDisk -Filter "DeviceID='C:'" | Select-Object Size,FreeSpace

$percentage = $disk.FreeSpace / $disk.Size
$disk_free = [math]::round($disk.FreeSpace/1024/1024/1024, 2)

If ($percentage -lt 0.1) {
    Write-Color "[ERROR] You have less than 10% of free spaces in your drive." -Color Red
    "Current Free Space: {0:P0}" -f $percentage
    "Current Free Space: {0:N0} GB" -f $disk_free
    Write-Color "<Instruction>" -Color White
    "    Please clean up the result files manually or run the cleaning scripts."
    Write-Color "<End of Instruction>" -Color White
} ElseIf ($disk_free -lt 100) {
    Write-Color "[ERROR] You have less than 100GB of free spaces in your drive." -Color Red
    "Current Free Space: {0:P0}" -f $percentage
    "Current Free Space: {0:N0} GB" -f $disk_free
    Write-Color "<Instruction>" -Color White
    "    Please clean up the result files manually or run the cleaning scripts."
    Write-Color "<End of Instruction>" -Color White
} Else {
    Write-Color "[INFO] There are still enough free spaces in your drive" -Color Green
    "Current Free Space: {0:P0}" -f $percentage
    "Current Free Space: {0:N0} GB" -f $disk_free
}

# check for memory
$freemem = Get-WmiObject -Class Win32_OperatingSystem
$memory_free = [math]::round(($freemem.FreePhysicalMemory / 1024 / 1024), 2)
$memory_percent = [math]::Round(($freemem.FreePhysicalMemory/$freemem.TotalVisibleMemorySize)*100,2)
If ($memory_percent -lt 10) {
    Write-Color "[ERROR] You have less than 10% of free memory in your computer." -Color Red
    "Current Free Memory: {0:N0} %" -f $memory_percent
    "Current Free Memory: {0:N0} GB" -f $memory_free
    Write-Color "<Instruction>" -Color White
    "    Please restart the computer."
    Write-Color "<End of Instruction>" -Color White
} ElseIf ($memory_free -lt 1) {
    Write-Color "[ERROR] You have less than 1GB of free memory in your computer." -Color Red
    "Current Free Memory: {0:N0} %" -f $memory_percent
    "Current Free Memory: {0:N0} GB" -f $memory_free
    Write-Color "<Instruction>" -Color White
    "    Please restart the computer."
    Write-Color "<End of Instruction>" -Color White
} Else {
    Write-Color "[INFO] There are still enough memory in your computer" -Color Green
    "Current Free Memory: {0:N0} %" -f $memory_percent
    "Current Free Memory: {0:N0} GB" -f $memory_free
}