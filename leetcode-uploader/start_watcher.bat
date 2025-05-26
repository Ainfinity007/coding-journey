@echo off
REM Change directory to your project folder
cd /d C:\Users\Infinity\leetcode-uploader

REM Run chokidar watcher command
chokidar "C:\Users\Infinity\leetcode-uploader\submissions\*.{py,cpp,sql}" -c "python scripts\detect_submission.py"