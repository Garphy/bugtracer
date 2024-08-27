@echo off
set yy=%date:~0,4%
set month=%date:~5,2%
set day=%date:~8,2%
set /a "dd=%day:0=%-1"
if %d% lss 10 set "dd=0%d%"
REM name = 20240801
set name=%yy%%month%%dd%
if EXIST _bak/%name%.rar goto err
"C:\Program Files\WinRAR\rar.exe" a -m5 _old/%name% *.php *.htm *.html *.js *.css  ./tpl/*.*
goto end

:err
echo file %name%.rar exists!
pause

:end