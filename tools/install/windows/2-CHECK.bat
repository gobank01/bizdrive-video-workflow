@echo off
REM ============================================================================
REM  BIZDRIVE Video — install checker (file 2 of 2)
REM
REM  Double-click this AFTER running 1-INSTALL.bat. It prints a green/red list
REM  of every tool + API key, so you can confirm everything is really
REM  installed. It installs nothing — safe to run any time.
REM ============================================================================
title BIZDRIVE Video - Check install

powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0check.ps1"

if %errorLevel% neq 0 (
  echo.
  echo  The checker could not run ^(code %errorLevel%^).
  pause
)
