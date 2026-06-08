@echo off
REM ============================================================================
REM  BIZDRIVE Video — one-click Windows installer (NO WSL)
REM
REM  Double-click this file. It runs setup.ps1 (sitting next to it), which
REM  installs Git, ffmpeg, Python, Node, Claude Code, the repo, and all
REM  dependencies natively on Windows. No WSL, no reboot, no admin shell.
REM ============================================================================
title BIZDRIVE Video - Install (no WSL)

powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0setup.ps1"

REM If PowerShell itself failed to launch, keep the window open to show why.
if %errorLevel% neq 0 (
  echo.
  echo  The installer exited with an error ^(code %errorLevel%^).
  echo  Take a screenshot of the message above and send it to your teacher.
  pause
)
