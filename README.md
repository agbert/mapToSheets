# Export Places To Google Sheets

## Google Requirements

Enable the following API's in a project on Google Cloud Console (https://console.cloud.google.com/)
- Places API (you may have to visit this page to make this happen: https://console.cloud.google.com/apis/library/places-backend.googleapis.com
)
- Places API (New)
- Google Sheets API (requires a Service Account)
- Geocoding API
- Google Drive API

Create an API Key through API's & Services > Credentials > Create credentials > API Key
- Name the key. 
- Ensure API Restrictions are set for:
  - Places API
  - Places API (new)
  - Google Sheets API
  - Google Drive API

Create a Service Account through API's & Services > Credentials > Create credentials > Service Account
- Name the service account
- Provide a description
- Hit create and continue
- The service account JSON will download automatically.


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

- Get the project

    ```zsh
    git clone git@github.com:agbert/mapToSheets.git
    ```

- Change directory to the new 'mapToSheets' directory
    - usually just 'cd mapToSheets' in Terminal

- Run the following command to create the virtual env config

    ```zsh
    python3 -m venv venv
    ```

- Run the following comand to activate the virtual env.

    ```zsh
    source venv/activate
    ```

- Run the following to install all required packages.

    ```zsh
    pip install -r requirements.txt
    ```

- Place the service account json file into the keys folder under mapToSheets directory.

- Edit the .env file

    ```zsh
    open -a TextEdit .env
    ```

  - Populate the GOOGLE_API_KEY value in quotes with your API Key from Google.
  - Populate the GOOGLE_APPLICATION_CREDENTIALS value in quotes with the filename of your service account json filename.

  Save the file and return to terminal

### Run the script

You can share the spreadsheet with yourself and specific emails using the following:

```zsh
python export_places_to_sheet.py "commercial real estate agency in Sacramento CA" --share agbert@gmail.com:writer --share jasonharnum@gmail.com:reader --notify
```
