param([string]$Out, [string]$ProcName = "PrinceOfPersia_Launcher", [int]$Tries = 12)
Add-Type -AssemblyName System.Drawing
Add-Type @"
using System; using System.Runtime.InteropServices;
public class C {
 [DllImport("user32.dll")] public static extern IntPtr GetDC(IntPtr h);
 [DllImport("user32.dll")] public static extern int ReleaseDC(IntPtr h, IntPtr dc);
 [DllImport("user32.dll")] public static extern bool GetWindowRect(IntPtr h, out R r);
 [DllImport("user32.dll")] public static extern bool SetForegroundWindow(IntPtr h);
 [DllImport("user32.dll")] public static extern IntPtr GetForegroundWindow();
 [DllImport("gdi32.dll")]  public static extern bool BitBlt(IntPtr d,int x,int y,int w,int hgt,IntPtr s,int sx,int sy,int rop);
 [StructLayout(LayoutKind.Sequential)] public struct R { public int L,T,Rr,B; }
}
"@
$p = Get-Process $ProcName -ErrorAction Stop
$h = $p.MainWindowHandle
# BitBlt reads the SCREEN, so anything overlapping the game lands in the shot - including our own
# console. Verify the game is genuinely frontmost BEFORE grabbing, and fail loudly if it never is.
$ok = $false
for ($i = 0; $i -lt $Tries; $i++) {
  [C]::SetForegroundWindow($h) | Out-Null
  Start-Sleep -Milliseconds 350
  if ([C]::GetForegroundWindow() -eq $h) { $ok = $true; break }
}
if (-not $ok) { Write-Output "REFUSED: game window never became foreground - capture would show other windows"; exit 2 }
Start-Sleep -Milliseconds 250
$r = New-Object C+R
[C]::GetWindowRect($h, [ref]$r) | Out-Null
$w = $r.Rr - $r.L; $ht = $r.B - $r.T
$screen = [C]::GetDC([IntPtr]::Zero)
$bmp = New-Object System.Drawing.Bitmap $w, $ht
$g = [System.Drawing.Graphics]::FromImage($bmp)
$dc = $g.GetHdc()
[C]::BitBlt($dc, 0, 0, $w, $ht, $screen, $r.L, $r.T, 0x00CC0020) | Out-Null
$g.ReleaseHdc($dc); $g.Dispose()
[C]::ReleaseDC([IntPtr]::Zero, $screen) | Out-Null
$bmp.Save($Out, [System.Drawing.Imaging.ImageFormat]::Png)
$bmp.Dispose()
# re-check afterwards: if focus moved mid-grab the shot is suspect
$still = ([C]::GetForegroundWindow() -eq $h)
Write-Output ("saved {0} {1}x{2} foreground-verified-after={3}" -f $Out, $w, $ht, $still)
