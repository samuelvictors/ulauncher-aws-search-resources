# AWS Resource Search - Ulauncher plugin

- This plugin to [Ulauncher](https://ulauncher.io/) allows for faster access of resources in the AWS console without the need to search on each individual service.

![Demo of the plugin](images/demo.gif)

## Getting started

- Install [Ulauncher](https://ulauncher.io/#Download) in your device.
- After starting it, right-click in the "Ulauncher" icon in your system tray and then go to "Preferences".
- In the modal that will open, go to the "EXTENSIONS" tab.
- Click in "Add extension".
- Paste this repository URL: `https://github.com/samuelvictors/ulauncher-aws-search-resources` and the click on "Add".
- The plugin searches for resources based in a local database stored in `~/.local/share/ulauncher/extensions/com.github.samuelvictors.ulauncher-aws-search-resources/resources.json`.
- In order to fill it, first you need to run an update process. Just type `update` and then press "Enter" twice.
- A small window will pop up and start the update process, that might take some minutes to complete (depending on the amount of resources that your current AWS profile has access to).
- After that, you can start searching:
  - First, to invoke the launcher prompt press "Ctrl+Space" (the default shortcut).
  - After that you must declare the resource type you're looking for: `lambda`(Lambda function), `table` (DynamoDB table), `bucket` (S3 bucket) or `log` (CloudWatch log group).
  - Then you insert the stage in which the resource is located: `dev`, `beta` or `prod`.
  - The next terms you type in the launcher will filter all the available resources by name based on the type and stage you defined previously.
  - Select the result and type "Enter" to open the resource URL in your default browser.
- To customize the plugin behavior and options, keep reading.

## Preferences

- To change the plugin preferences, right-click in the "Ulauncher" icon in your system tray and then go to "Preferences".
- In the modal that will open, go to the "EXTENSIONS" tab and then "AWS Resource Search"

### Keywords

- For every feature of the plugin you can define which keyword typed in the launcher will activate it:
  - S3 buckets search (default `bucket`)
  - Lambda functions search (default `lambda`)
  - DynamoDB tables search (default `table`)
  - CloudWatch log groups search (default `log`)
  - The process to update the resources local database (default `update`)

### Profile

- Input the profile name that should be used to search for AWS resources.
- You can check the ones currently available in your environment with the command: `cat ~/.aws/config`.
- You can leave this empty if you just want to use your default profile.

### Stages

- Input all the stages you want to search during the update process.
- They should be separated by comma, like this: `dev-xx,stg-yy`.
- If the field is kept empty, the default is searching for `dev,beta,prod`.

### Change the browser

- This setting allows to select which browser is used to open the URL of the selected resource in the launcher.
- Ensure that the desired browser is installed:

```BASH
which google-chrome
which chromium
# and so on...
```

- Change the Browser field in the preferences to the selected browser.
  - xdg-open - **System Default**
  - firefox - Firefox
  - google-chrome - Google Chrome
  - google-chrome-stable - Google Chrome
  - chromium - Chromium
  - opera - Opera
  - msedge - Microsoft Edge

***EXTRA***

- It's possible in Chrome to start the browser in a specific profile, just enter the value below and change the profile name:

```BASH
google-chrome --profile-directory="Profile 1"
```

- To check the available profiles look in the Chrome folder.
  - On Linux: ~/.config/google-chrome
  - On macOS: ~/Library/Application Support/Google/Chrome
  - On Windows: %USERPROFILE%\AppData\Local\Google\Chrome\User Data