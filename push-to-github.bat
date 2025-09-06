@echo off
echo Enter your GitHub username:
set /p username=khanfardeen833-ship-it

echo Enter your repository name (e.g., health-care-chatbot):
set /p repo=health-care-bot

git remote add origin https://github.com/%username%/%repo%.git
git branch -M main
git push -u origin main

echo.
echo Repository pushed successfully!
echo Your code is now on GitHub at: https://github.com/%username%/%repo%
pause