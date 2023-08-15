from django.shortcuts import render
from django.http import JsonResponse
from django.shortcuts import render
from django.http import HttpResponse
from django.views.decorators.http import require_http_methods
import dialogflow
import os
import uuid
import json
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
import google.auth
from google.auth.transport.requests import Request
from google.oauth2.service_account import Credentials
import requests
import json
from django.conf import settings

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow

# from __future__ import unicode_literals

#from dialogflow_v2 import dialogflow_v2 as Dialogflow
# Create your views here.

def get_token():
    SCOPES = ['https://www.googleapis.com/auth/cloud-platform']

    creds = None
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first time.
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                settings.BASE_DIR / 'credentials.json',
                SCOPES
            )
            creds = flow.run_local_server(port=8801)
        # Save the credentials for the next run
        with open('token.json', 'w') as token:
            token.write(creds.to_json())
            
    return creds

@csrf_exempt
def index_view(request):

    if request.method == "POST":
        creds = get_token()
        headers = {
            'Content-Type': 'application/json; charset=utf-8',
            'Authorization': 'Bearer {}'.format(creds.token)
            # 'Authorization': 'Bearer ya29.a0AbVbY6OlGqtWTgiNmvDguJEVucr1ldbBcuik10UbmykYKYee3Q7N2iW-lB2616sI21cjPhuQTZnV65Eq9spL0dtLW786mDLKJ3VCHsowI6f345WFRNCIRFkwyIxS7lH_tG3cnLj5_Y6hdkz5TGRVHbBHwWfdFdW_MroTvqZyWhKPmUjAs7dFe-tsPmJx_9mk6nXS3DoC7TO_S4OBmB4wfEdnceUhaG5tGygTNK6TbMnmTR_j8mV4jU4ImJu-bd4FMh6yQDDO76EoB0_wnskf72cFuDG9ONy7VvURU_BLGtgD7H5z_SjeptLLUN0JveFC98_tPI89J5BrxRJT7PjWwqj9_RI_GO1fwvYOjQzVSdlSSPC3cQoUgNVvq9MpT04Q0Q9amE375d36UuB6FzHmmjlW-PB19IM9RxAaCgYKAYcSARESFQFWKvPlE77VpD_oq3iFJjT1oSojHw0426',
        }

        
        # Note: json_data will not be serialized by requests
        # exactly as it was in the original request.
        post_data = json.loads(request.body.decode("utf-8"))
        user_message = post_data.get('question')
        data = '{"queryInput":{"text":{"text":"%s","languageCode":"en"}},"queryParams":{"source":"DIALOGFLOW_CONSOLE","timeZone":"Europe/Paris","sentimentAnalysisRequestConfig":{"analyzeQueryTextSentiment":true}}}'%user_message
        print(data)
        response = requests.post(
        'https://dialogflow.googleapis.com/v2beta1/projects/ines-bot-axht/locations/global/agent/sessions/e1e76564-d537-f955-818f-5a39420d3636:detectIntent',
        headers=headers,
        data=data,
        )
        
        response_data = response.json()

        fulfillment_text = response_data['queryResult']['fulfillmentText']
        print(type(fulfillment_text))
        return HttpResponse(json.dumps({"answer":str(fulfillment_text)}), status=200)
        return HttpResponse(response.text, status=200)
    
    return render(request, 'base.html')




@csrf_exempt
@require_http_methods(['POST'])
def chat_view(request):
    user_message = json.loads(request.body.decode('utf-8'))['text']
    if user_message:
        GOOGLE_PROJECT_ID = "ines-bot-axht"
        session_id = "1234567891"
        context_short_name = "does_not_matter"

        context_name = "projects/" + GOOGLE_PROJECT_ID + "/agent/sessions/" + session_id + "/contexts/" + \
                       context_short_name.lower()

        parameters = dialogflow.types.struct_pb2.Struct()

        context_1 = dialogflow.types.context_pb2.Context(
            name=context_name,
            lifespan_count=2,
            parameters=parameters
        )
        query_params_1 = {"contexts": [context_1]}

        language_code = 'en'

        response = detect_intent_with_parameters(
            project_id=GOOGLE_PROJECT_ID,
            session_id=session_id,
            query_params=query_params_1,
            language_code=language_code,
            user_input=user_message
        )
        return HttpResponse(response.query_result.fulfillment_text, status=200)
    else:
        return JsonResponse({'error': 'No message parameter provided.'}, status=400)
    
    


def detect_intent_with_parameters(project_id, session_id, query_params, language_code, user_input):
    """Returns the result of detect intent with texts as inputs.

    Using the same `session_id` between requests allows continuation
    of the conversaion."""
    session_client = dialogflow.SessionsClient()

    session = session_client.session_path(project_id, session_id)

    #text = "this is as test"
    text = user_input

    text_input = dialogflow.types.TextInput(
        text=text, language_code=language_code)

    query_input = dialogflow.types.QueryInput(text=text_input)

    response = session_client.detect_intent(
        session=session, query_input=query_input,
        query_params=query_params
    )

    print('=' * 20)
    print('Query text: {}'.format(response.query_result.query_text))
    print('Detected intent: {} (confidence: {})\n'.format(
        response.query_result.intent.display_name,
        response.query_result.intent_detection_confidence))
    print('Fulfillment text: {}\n'.format(
        response.query_result.fulfillment_text))

    return response
    

def about(request):
    return render(request, 'about.html')








