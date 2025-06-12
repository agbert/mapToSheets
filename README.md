# Export Places To Google Sheets

## Google Requirements

Enable the following API's in a project on Google Cloud Console (https://console.cloud.google.com/)
- Places API (you may have to visit this page to make this happen: https://console.cloud.google.com/apis/library/places-backend.googleapis.com
)
- Places API (New)
- Google Sheets API (requires a Service Account)
- Geocoding API

Create an API Key through API's & Services > Credentials > Create credentials > API Key
- Name the key. 
- Ensure API Restrictions are set for:
  - Places API, 
  - Places API (new), and 
  - Google Sheets API.

Create a Service Account through API's & Services > Credentials > Create credentials > Service Account
- Name the service account
- Provide a description
- Hit create and continue
- The service account JSON will download automatically.
- Place this file into the Keys folder in this project. 

## System Requirements

### XCode

Go get and install XCode on your machine. Its available on the App Store on the mac.

### Homebrew

Install Homebrew

- Start up terminal. 
- run the following command:

```zsh
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
```

#### Python3

Install the correct version of python

- run the following command in Terminal:

```zsh
brew install python
```

#### virtualenv

Install virtual env so that when python runs it doesn't get in the way of the macos version of python.

- do this in terminal
  - Run this to get the project from GitHub

  ```zsh
  git clone ...
  ```

## Install Python Project Requirements

