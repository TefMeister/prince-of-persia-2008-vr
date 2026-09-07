param([string]$Keys, [int]$HoldMs = 60, [int]$GapMs = 250, [string]$ProcName = "PrinceOfPersia_Launcher")
Add-Type @"
using System; using System.Runtime.InteropServices;
public class K {
 [StructLayout(LayoutKind.Sequential)] public struct KEYBDINPUT { public ushort wVk, wScan; public uint dwFlags, time; public IntPtr dwExtraInfo; }
 [StructLayout(LayoutKind.Explicit, Size=28)] public struct INPUT { [FieldOffset(0)] public uint type; [FieldOffset(4)] public KEYBDINPUT ki; }
 [DllImport("user32.dll")] public static extern uint SendInput(uint n, INPUT[] p, int cb);
 [DllImport("user32.dll")] public static extern bool SetForegroundWindow(IntPtr h);
 public const uint KEYEVENTF_SCANCODE = 0x0008, KEYEVENTF_KEYUP = 0x0002, KEYEVENTF_EXTENDEDKEY = 0x0001;
 public static void Key(ushort scan, bool ext, bool up) {
   var i = new INPUT(); i.type = 1;
   i.ki.wVk = 0; i.ki.wScan = scan;
   i.ki.dwFlags = KEYEVENTF_SCANCODE | (up ? KEYEVENTF_KEYUP : 0) | (ext ? KEYEVENTF_EXTENDEDKEY : 0);
   SendInput(1, new INPUT[]{i}, Marshal.SizeOf(typeof(INPUT)));
 }
}
"@
# scancode set 1. 'ext' = the extended-key flag arrow keys and a few others REQUIRE.
$map = @{
  'esc'=@(0x01,$false); 'enter'=@(0x1C,$false); 'space'=@(0x39,$false);
  'up'=@(0x48,$true); 'down'=@(0x50,$true); 'left'=@(0x4B,$true); 'right'=@(0x4D,$true);
  'w'=@(0x11,$false); 'a'=@(0x1E,$false); 's'=@(0x1F,$false); 'd'=@(0x20,$false);
  'f1'=@(0x3B,$false); 'f2'=@(0x3C,$false); 'f3'=@(0x3D,$false); 'tab'=@(0x0F,$false);
  'backspace'=@(0x0E,$false); 'tilde'=@(0x29,$false)
}
$p = Get-Process $ProcName -ErrorAction Stop
[K]::SetForegroundWindow($p.MainWindowHandle) | Out-Null
Start-Sleep -Milliseconds 300
foreach ($k in $Keys.Split(',')) {
  $k = $k.Trim().ToLower()
  if (-not $map.ContainsKey($k)) { Write-Output "unknown key '$k'"; continue }
  $scan = [uint16]$map[$k][0]; $ext = [bool]$map[$k][1]
  [K]::Key($scan, $ext, $false); Start-Sleep -Milliseconds $HoldMs
  [K]::Key($scan, $ext, $true);  Start-Sleep -Milliseconds $GapMs
  Write-Output ("sent {0} (scan 0x{1:X2} ext={2})" -f $k, $scan, $ext)
}
