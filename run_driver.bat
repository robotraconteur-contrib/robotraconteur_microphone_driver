@echo off

setlocal
call robotraconteur_microphone_driver\venv\Scripts\activate
@REM python -m robotraconteur_microphone_driver --list-devices
python -m robotraconteur_microphone_driver -d=4