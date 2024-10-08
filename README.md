# AWS Resource Search - Ulauncher plugin

- This plugin to [Ulauncher](https://ulauncher.io/) allows for faster access of resources in the AWS console without the need to search on each individual service.

![Demo of the plugin](images/demo.gif)

## Getting started

- Install [Ulauncher](https://ulauncher.io/#Download) in your device.
- After starting it, right-click in the "Ulauncher" icon in your system tray and then go to "Preferences".
- In the modal that will open, go to the "EXTENSIONS" tab.
- Click in "Add extension".
- Paste this repository URL: `https://github.com/samuelvictors/ulauncher-aws-search-resources` and then click on "Add".
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

### Additional arguments

- This setting allow to customize even further the browser invocation passing special arguments.
- It's possible to define a set of arguments to be supplied to all invocations or specify different arguments depending on the AWS profile which originally found the resource during update process. This is specially handy if you intend to use different browser profiles/containers depending on the account and region of the resource.
- Below some examples of using this setting:

#### Scenario 1: use a single argument to all resources

- Example: open all resources in a new private window in Firefox**

```text
-private-window 
```

#### Scenario 2: put the URL in a specific position in the arguments

- Example: open resources with a specific container in Firefox.
- If you use [Multi-Account Containers](https://addons.mozilla.org/en-US/firefox/addon/multi-account-containers) in Firefox, you can select one of them where you keep your AWS login active to open all AWS resources, like this:

```text
'ext+container:name\=AWS+Adm&url\=%url'
```

- By default, our plugin always executes the command to open the browser in the following order: browser executable + arguments + URL, but you can also put the URL in any position of the argument option using a template parameter `%url`, just like the example above.

#### Scenario 3: define different arguments based on AWS profile

- Example:
  - All resources found by "dev" AWS profile will open in profile "Developer" of the Chrome browser.
  - All resources found by "adm" AWS profile will open in profile "SysAdmin" of the Chrome browser.

```text
dev=--profile-directory\="Developer",adm=--profile-directory\="SysAdmin"
```

- **Attention**: notice that besides the "=" after the profile name, all other "=" are escaped. The same applies to ",", used as a separator character between the specific arguments to each AWS profile.

### Extra tip

- To check all available profiles in your Chrome browser, look at these directories:
  - On Linux: ~/.config/google-chrome
  - On macOS: ~/Library/Application Support/Google/Chrome
  - On Windows: %USERPROFILE%\AppData\Local\Google\Chrome\User Data

### How to debug

- If you got some error while updating the list of resources or doing another action, you might try to run the plugin outputting logs to your terminal:
  - First quit Ulauncher
  - Run this command in a terminal window to start Ulauncher again but with no plugins: `ulauncher --no-extensions --dev -v`
  - To start the plugin again, open another terminal tab/window and run:
    ```shell
    VERBOSE=1 ULAUNCHER_WS_API=ws://127.0.0.1:5054/com.github.samuelvictors.ulauncher-aws-search-resources PYTHONPATH=/usr/lib/python3/dist-packages /usr/bin/python3 \
    ~/.local/share/ulauncher/extensions/com.github.samuelvictors.ulauncher-aws-search-resources/main.py
    ```
  - With this command, all output generated during plugin execution will show up in that terminal. Just repeat the action that caused the error and it should show up something in there.
