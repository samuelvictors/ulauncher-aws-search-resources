## Preferences

### Change the browser:

Ensure that the desired browser is installed.
```BASH 
which google-chrome
which chromium
# and so on...
```
Change the Browser field in the preferences to the selected browser.
- xdg-open - **System Default**
- firefox - Firefox
- google-chrome - Google Chrome
- google-chrome-stable - Google Chrome
- chromium - Chromium
- opera - Opera
- msedge - Microsoft Edge


***EXTRA***

It's possible in Chrome to start the browser in a specific profile, just enter the value below and change the profile name
`google-chrome --profile-directory="Profile 1"`
To check the available profiles look in the Chrome folder.
- On Linux: ~/.config/google-chrome
- On macOS: ~/Library/Application Support/Google/Chrome
- On Windows: %USERPROFILE%\AppData\Local\Google\Chrome\User Data

### Change the AWS profile:

To use the default profile, leave it ***default***