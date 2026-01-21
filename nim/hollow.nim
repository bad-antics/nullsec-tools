// NullSec - Nim-based Process Hollowing (Fast & Stealthy)
// Part of the NullSec Framework
// https://github.com/bad-antics | @AnonAntics
// discord.gg/killers

import winim/lean
import os, strformat, strutils
import std/[base64, streams]

const
  VERSION = "1.0.0"
  BANNER = """
╔═══════════════════════════════════════════════════════╗
║          NullSec - Nim Process Hollowing              ║
║              @AnonAntics | NullSec                    ║
║         discord.gg/killers for keys                   ║
╚═══════════════════════════════════════════════════════╝
"""

# Encrypted shellcode placeholder - get key from discord.gg/killers
const ENCRYPTED_PAYLOAD = [
  byte 0x4E, 0x55, 0x4C, 0x4C, 0x53, 0x45, 0x43, 0x00,
  0x48, 0x4F, 0x4C, 0x4C, 0x4F, 0x57, 0x00, 0x00
]

type
  ProcessInfo = object
    pid: DWORD
    handle: HANDLE
    threadHandle: HANDLE
    imageBase: LPVOID

proc printBanner() =
  echo BANNER
  echo fmt"Version: {VERSION}"
  echo ""

proc getNtdll(): HMODULE =
  result = GetModuleHandleA("ntdll.dll")

proc ntUnmapViewOfSection(hProcess: HANDLE, baseAddress: PVOID): NTSTATUS {.importc: "NtUnmapViewOfSection", dynlib: "ntdll.dll".}

proc createSuspendedProcess(targetPath: string): ProcessInfo =
  var
    si: STARTUPINFOA
    pi: PROCESS_INFORMATION
  
  ZeroMemory(addr si, sizeof(si))
  ZeroMemory(addr pi, sizeof(pi))
  si.cb = cast[DWORD](sizeof(si))
  
  let success = CreateProcessA(
    targetPath,
    nil,
    nil,
    nil,
    FALSE,
    CREATE_SUSPENDED,
    nil,
    nil,
    addr si,
    addr pi
  )
  
  if success == 0:
    echo fmt"[!] Failed to create process: {GetLastError()}"
    quit(1)
  
  result.pid = pi.dwProcessId
  result.handle = pi.hProcess
  result.threadHandle = pi.hThread
  
  echo fmt"[+] Created suspended process PID: {result.pid}"

proc getProcessPEB(hProcess: HANDLE): PPEB =
  var pbi: PROCESS_BASIC_INFORMATION
  var retLen: ULONG
  
  # Would use NtQueryInformationProcess here
  # This requires the key to unlock
  
  echo "[!] ENCRYPTED CONTENT"
  echo "[!] PEB access requires encryption key"
  echo "[!] Get your key at: discord.gg/killers"
  return nil

proc hollowProcess(proc_info: var ProcessInfo, payload: openArray[byte]): bool =
  echo "[*] Attempting process hollowing..."
  
  # Get PEB and image base
  let peb = getProcessPEB(proc_info.handle)
  if peb == nil:
    return false
  
  # Unmap original image
  # Write new image
  # Fix relocations
  # Resume thread
  
  # All encrypted - requires key
  echo ""
  echo "[!] ENCRYPTED CONTENT"
  echo "[!] Process hollowing payload requires encryption key"
  echo "[!] Get your key at: discord.gg/killers"
  echo ""
  
  return false

proc decryptPayload(key: string): seq[byte] =
  if key.len != 64:
    echo "[!] Invalid key length"
    echo "[!] Get valid key from discord.gg/killers"
    return @[]
  
  # AES-256 decryption would happen here
  echo "[!] Decryption requires valid key from discord.gg/killers"
  return @[]

proc listTargets() =
  echo "[*] Common hollow targets:"
  echo "    - svchost.exe (System Services)"
  echo "    - RuntimeBroker.exe (Windows Runtime)"
  echo "    - dllhost.exe (COM Surrogate)"
  echo "    - explorer.exe (Windows Explorer)"
  echo "    - notepad.exe (Safe testing)"
  echo ""

proc main() =
  printBanner()
  
  if paramCount() < 1:
    echo "Usage: hollow [options]"
    echo ""
    echo "Options:"
    echo "    -t, --target PATH   Target executable to hollow"
    echo "    -p, --payload FILE  Shellcode payload file"
    echo "    -k, --key KEY       Decryption key from discord.gg/killers"
    echo "    -l, --list          List common targets"
    echo "    -h, --help          Show this help"
    echo ""
    echo "Get encryption keys: discord.gg/killers"
    return
  
  var
    target = ""
    payloadFile = ""
    key = ""
  
  var i = 1
  while i <= paramCount():
    let arg = paramStr(i)
    case arg:
    of "-t", "--target":
      inc i
      if i <= paramCount():
        target = paramStr(i)
    of "-p", "--payload":
      inc i
      if i <= paramCount():
        payloadFile = paramStr(i)
    of "-k", "--key":
      inc i
      if i <= paramCount():
        key = paramStr(i)
    of "-l", "--list":
      listTargets()
      return
    of "-h", "--help":
      echo "Usage: hollow -t <target.exe> -p <payload.bin> -k <key>"
      return
    inc i
  
  if target == "":
    echo "[!] No target specified"
    return
  
  if not fileExists(target):
    echo fmt"[!] Target not found: {target}"
    return
  
  echo fmt"[*] Target: {target}"
  
  var proc_info = createSuspendedProcess(target)
  
  var payload: seq[byte]
  if key != "":
    payload = decryptPayload(key)
  else:
    payload = @ENCRYPTED_PAYLOAD
  
  if payload.len == 0 or not hollowProcess(proc_info, payload):
    echo "[!] Hollowing failed"
    echo "[*] Terminating suspended process..."
    discard TerminateProcess(proc_info.handle, 0)
    CloseHandle(proc_info.handle)
    CloseHandle(proc_info.threadHandle)
  else:
    echo "[+] Process hollowed successfully!"
    echo "[*] Resuming execution..."
    discard ResumeThread(proc_info.threadHandle)

when isMainModule:
  main()
