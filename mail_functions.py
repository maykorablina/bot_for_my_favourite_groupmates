from __future__ import print_function

import os.path
import time
import datetime
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import base64
from database import Database
import lxml
from bs4 import BeautifulSoup

# If modifying these scopes, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']


def check_email():
    """Shows basic usage of the Gmail API.
    Lists the user's Gmail labels.
    """
    global messages
    creds = None
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.json', 'w') as token:
            token.write(creds.to_json())

    try:
        service = build('gmail', 'v1', credentials=creds)
        # Call the Gmail API
        # service = build('gmail', 'v1', credentials=creds)
        result = service.users().messages().list(userId='me').execute()
        messages = result.get('messages')
        # print(messages)
    except HttpError as error:
        # TODO(developer) - Handle errors from gmail API.
        print(f'An error occurred: {error}')

    def unpack_multipart(payload):
        if 'multipart' in payload['mimeType']:
            a = []
            mult = payload.get('parts')
            for m in mult:
                if 'multipart' in m['mimeType']:
                    a.extend(unpack_multipart(m))
        a.extend(mult)
        return a
    result = []
    for msg in messages[0:1]:
        temp = {'id': msg['id'], 'date': '', 'topic': '', 'sender': '', 'text': '', 'attachments': []}
        txt = service.users().messages().get(userId='me', id=msg['id']).execute()
        payload = txt['payload']
        headers = payload['headers']
        for d in headers[::-1]:
            try:
                if d['name'] == 'Received':
                    translations_month = {'Jan': '01', 'Feb': '02', 'Mar': '03', 'Apr': '04',
                                          'May': '05', 'Jun': '06', 'Jul': '07', 'Aug': '08',
                                          'Sep': '09', 'Oct': '10', 'Nov': '11', 'Dec': '12'}
                    a = d['value'].split(';')
                    a = list(map(str.strip, a))[-1]
                    a = a.split()[1:-1]
                    a[1] = translations_month[a[1]]
                    date = "-".join(a[:3]) + " " + a[3]
                    date = datetime.datetime.strptime(date, "%m-%d-%Y %H:%M:%S")
                    formatted_date = date.strftime("%d-%m-%Y %H:%M:%S")
                    temp['date'] = formatted_date
                    # print(a)
                    break
            except:
                pass  #
            # a = a.split()[1:-1]
            # translations_month = {'Jan': '01', 'Feb': '02', 'Mar': '03', 'Apr': '04',
            #                 'May': '05', 'Jun': '06', 'Jul': '07', 'Aug': '08',
            #                 'Sep': '09', 'Oct': '10', 'Nov': '11', 'Dec': '12'}
            # a[1] = translations_month[a[1]]
            # date = "-".join(a[:3]) + " " + a[3]
            #
            # date = datetime.datetime.strptime(date, "%m-%d-%Y %H:%M:%S")
            # formatted_date = date.strftime("%d-%m-%Y %H:%M:%S")
            # temp['date'] = formatted_date
            # break
        for d in headers:
            if d['name'] == 'Subject':
                temp['topic'] = d['value']
            if d['name'] == 'From':
                temp['sender'] = d['value']
        # print(temp)
        # print(payload)
        if 'multipart' in payload['mimeType']:
            parts = unpack_multipart(payload)
            for p in parts:
                if 'multipart' not in p['mimeType']:
                    if p['filename'] == '':
                        text = p['body']['data']
                        # print(text)
                    else:
                        if 'attachment' in p['headers'][0]['value']:
                            filename = p['filename']

                            attid = p.get('body')["attachmentId"]
                            att = service.users().messages().attachments().get(userId='me', messageId=msg['id'],
                                                                               id=attid).execute()
                            data = att['data']
                            file_data = base64.urlsafe_b64decode(data.encode('UTF-8'))
                            # print(type(file_data))
                            temp['attachments'].append(str(file_data))
                            with open(f'temp/{filename}', 'wb') as f:
                                f.write(file_data)
        else:
            text = payload.get('body')['data']
        text = text.replace("-", "+").replace("_", "/")
        text = base64.b64decode(text).decode('utf-8')
        soup = BeautifulSoup(text, "lxml")
        body = soup.find_all('div')
        real_text = ''
        for i in body:
            i = i.text
            i = i.replace('\xa0', ' ').strip()
            real_text += i + '\n'
        temp['text'] = real_text
        # print(parts)
        # print(temp)
        result.append(temp)
    # print(result[1])
    return result
        # return temp

        #     headers = payload['headers']
        #     for d in headers:
        #         if d['name'] == 'Subject':
        #             temp['topic'] = d['value']
        #         if d['name'] == 'From':
        #             temp['sender'] = d['value']
        #     parts = payload.get('parts')
        #     text = parts[0]['body']['data']
        #     text = text.replace("-", "+").replace("_", "/")
        #     text = base64.b64decode(text).decode('utf-8')
        #     temp['body'] = text
        #     print(temp)
        # except: pass

        #
        # # print(messages.index(msg))
        #
        # # print(txt)
        # try:
        #     payload = txt['payload']
        #     headers = payload['headers']
        #     # print(headers)
        #     temp = {'id':'', 'topic':'', 'sender':'', 'body':''}
        #     for d in headers:
        #         temp['id'] = msg['id']
        #         # print(d)
        #         if d['name'] == 'Subject':
        #             temp['topic'] = d['value']
        #             # print(f'topic: {topic}')
        #         if d['name'] == 'From':
        #             temp['sender'] = d['value']
        #             # print(f'sender: {sender}')
        #             # print('------')
        #         # if d['name'] == 'Cc':
        #         #     cc = d['value']
        #         # print('------------')
        #             # print(f'Copy: {cc}')
        #     parts = payload.get('parts')
        #     text = parts[0]['body']['data']
        #     text = text.replace("-", "+").replace("_", "/")
        #     text = base64.b64decode(text).decode('utf-8')
        #     # for p in parts:
        #     #     print(p)
        #     # print(text)
        #     temp['body'] = text
        #     print(temp)
        #     print('-------')
        # print(parts)
        # data = parts['body']['data']
        # temp['body'] = data
        # print(temp)
        # print(data)
        # print('----------')
        # data = data.replace("-", "+").replace("_", "/")
        # decoded_data = base64.b64decode(data)
        # soup = BeautifulSoup(decoded_data, "lxml")
        # body = soup.body()
        # print('subj', subject)
        # print('from', sender)
        #     # print('mes', body)
        #     # print('\n')
        # except:
        #     pass
        #


# if __name__ == '__main__':
    # result = check_email()
    # # result = check_email()
    # db = Database('maya_mail.db')
    # for i in result:
    #     print(i)
    # # # # #
    # for r in result:
    #     values = [r['id'], r['date'], r['topic'], r['sender'], r['text']]
    #     db.execute('''
    #         INSERT INTO mails (id, date, topic, sender, text) VALUES (?, ?, ?, ?, ?);
    #     ''', values)
    #
    #     for a in r['attachments']:
    #         db.execute('''
    #                         INSERT INTO attachments (mail_id, attachment) VALUES (?, ?);
    #                     ''', [r['id'], a])
    # print(len(db.fetchall('''SELECT * FROM mails;''')))
    # print(len(db.fetchall('''SELECT * FROM attachments;''')))
    # print(db.fetchall('''SELECT * FROM MAILS'''))
# time.sleep(1)
