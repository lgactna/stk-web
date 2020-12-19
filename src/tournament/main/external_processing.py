"""Logic for retreiving and processing osu! API and Google Sheets data."""

def a(sheet_id):
    """Get data from Google Sheets. Spit out."""
    #theoretically we'll need this practically never so imports occur here
    #if we find a need to regularly rebuild databases from gsheets, then we can move this out
    import pickle
    import os.path
    from googleapiclient.discovery import build
    from google_auth_oauthlib.flow import InstalledAppFlow
    from google.auth.transport.requests import Request

    # If modifying these scopes, delete the file token.pickle.
    SCOPES = ['https://www.googleapis.com/auth/spreadsheets.readonly']

    # The ID and range of a sample spreadsheet.

    creds = None
    # The file token.pickle stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)

    service = build('sheets', 'v4', credentials=creds)

    # Call the Sheets API
    sheet = service.spreadsheets()

    ranges = {
        'meta': 'meta!A2:B',
        'matches': 'matches!A2:F',
        'pools': 'pools!A2:D',
        'teams': 'teams!A2:E'
    }

    for range_id in ranges:
        range_name = ranges[range_id]
        result = sheet.values().get(spreadsheetId=sheet_id,
                                    range=range_name).execute()
        output[range_id] = result.get('values', [])

        '''
        print("for %s:"%range)
        if not values:
            print('No data found.')
        else:
            for row in values:
                print(row)
        '''
