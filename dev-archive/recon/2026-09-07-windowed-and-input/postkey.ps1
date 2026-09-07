param([string]$Keys, [int]$GapMs = 500, [string]$ProcName = "PrinceOfPersia_Launcher")
Add-Type @"
using System; using System.Runtime.InteropServices;
public class P {
 [DllImport("user32.dll")] public static extern bool PostMessage(IntPtr h, uint m, IntPtr w, IntPtr l);
 [DllImport("user32.dll")] public static extern bool SetForegroundWindow(IntPtr h);
}
"@
# This game ignores SendInput entirely (verified 2026-09-07 against a no-input control);
# posted window messages are the route that works.
$vk = @{ 'esc'=0x1B; 'enter'=0x0D; 'space'=0x20; 'up'=0x26; 'down'=0x28; 'left'=0x25; 'right'=0x27;
         'w'=0x57; 'a'=0x41; 's'=0x53; 'd'=0x44; 'tab'=0x09; 'f1'=0x70; 'f2'=0x71; 'tilde'=0xC0; 'back'=0x08 }
$h = (Get-Process $ProcName -ErrorAction Stop).MainWindowHandle
[P]::SetForegroundWindow($h) | Out-Null
Start-Sleep -Milliseconds 200
foreach ($k in $Keys.Split(',')) {
  $k = $k.Trim().ToLower()
  if (-not $vk.ContainsKey($k)) { Write-Output "unknown '$k'"; continue }
  $code = [int]$vk[$k]
  [P]::PostMessage($h, 0x0100, [IntPtr]$code, [IntPtr]0) | Out-Null
  Start-Sleep -Milliseconds 100
  [P]::PostMessage($h, 0x0102, [IntPtr]$code, [IntPtr]0) | Out-Null
  Start-Sleep -Milliseconds 100
  [P]::PostMessage($h, 0x0101, [IntPtr]$code, [IntPtr]0) | Out-Null
  Start-Sleep -Milliseconds $GapMs
  Write-Output ("posted {0} (vk 0x{1:X2})" -f $k, $code)
}
