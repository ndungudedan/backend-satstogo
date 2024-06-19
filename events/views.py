import requests
from django.conf import settings
import pytz
from rest_framework.response import Response
from rest_framework.parsers import JSONParser
from rest_framework.views import APIView
from rest_framework import status
from datetime import datetime
from .models import Event, Attendance,EventSession
from api.models import SatsUser
from .serializers import EventSerializer, EventReadSerializer, ConfirmEventSerialiazer, AttendanceSerializer
import csv
from django.http import HttpResponse
from django.utils import timezone
from datetime import date
import os
from django.db.models import Q

ADMIN_API_KEY = settings.ADMIN_API_KEY
LNURL_ENDPOINT = settings.LNURL_ENDPOINT
INVOICE_READ_KEY = settings.INVOICE_READ_KEY
LNURL_PAYMENTS_ENDPOINT = settings.LNURL_PAYMENTS_ENDPOINT

class EventCrud(APIView):
    serializer_class = EventSerializer
    parser_classes = [JSONParser]

    def post(self, request):
        serializer = EventSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({
                "message": "Event created successfully!",
                "data": serializer.data
            }, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    def create(self, request):
        # Override create to handle attendee data (assuming data format)
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(data={
            "message":"Event created successfully!",
            "data": serializer.data
        })

    def get(self,request):
        org = request.GET.get('org')
        print(f"/{org}---------Org Related Events---------------")
        if not(org):
            events = Event.objects.prefetch_related('eventsession_set')
        else:
            events = Event.objects.prefetch_related('eventsession_set').filter(org_username=org)
        print('events',events)
        serializer = EventReadSerializer(events, many=True)
        return Response(data=serializer.data,status=status.HTTP_200_OK)
        # events = Event.objects.prefetch_related('eventsession_set')
        # my_events = []

        # for event in events:
        #     # Create a dictionary for each event
        #     sessions = event.eventsession_set.all()
        #     event_dict = {
        #         'name': event.name,
        #         'deadline': str(event.deadline),
        #         'event_type': event.event_type,
        #         'venue': event.venue,
        #         'reward': event.reward,
        #         'sessions': sessions # List to hold session data
        #     }
        #     my_events.append(event_dict)
        # return Response({
        #     "message":"Event created successfully!",
        #     "data": json.dumps(my_events)
        # },status=status.HTTP_200_OK)

class ActivateUser(APIView):

    serializer_class = ConfirmEventSerialiazer

    def post(self, request):
        serialize_data = self.serializer_class(data=request.data)
        if serialize_data.is_valid():
            try:
                pk = request.data.get('pk')
                magic_string = request.data.get('magic_string')
                user = SatsUser.objects.get(magic_string=magic_string)
                session = EventSession.objects.prefetch_related('parent_event').get(pk=pk)
                parent_event = session.parent_event
                try:
                    today = timezone.now().date()
                    alreadyActivated = Attendance.objects.get(user=user,event=parent_event,locked=True,clock_in_time__date=today)
                    responsedict = {'error': 'You have already activated for this event'}
                    status = 403
                    return Response(data=responsedict,status=status)
                except Attendance.DoesNotExist:
                    print(f"datetime.now(): {datetime.now().time()}")
                    formatted_datetime = datetime.now().time()
                    print(f"formatted_datetime: {formatted_datetime}")
                    deadline_to_time = session.deadline.time()
                    print(f"deadline_to_time: {deadline_to_time}")
                    if formatted_datetime < deadline_to_time:
                        user.update_sats_balance(user.sats_balance+parent_event.reward)
                        status = 200
                        responsedict = {'message': f'Congrats!! you have won ${parent_event.reward} Sats.'}
                        is_activated = True
                    else:
                        responsedict = {'error': 'Oops, you are not eligible to receive this reward'}
                        status = 403
                        is_activated = False
                    new_attendance, created = Attendance.objects.update_or_create(
                            user=user,
                            event=parent_event,
                            eventSession=session,
                            created_at=timezone.now().date(),
                            defaults={
                                'is_activated': is_activated,
                                'locked': True,
                                'clock_in_time': datetime.today()
                            },
                        )
            except (SatsUser.DoesNotExist, EventSession.DoesNotExist):
                responsedict = {'error': 'User or Event does not exist.'}
                status = 404
        else:
            responsedict = serialize_data.errors
            status = 400

        return Response(data=responsedict,status=status)

    def export(request):
        checkins = Attendance.objects.all().filter(event__isnull=False).select_related('user', 'event').order_by('-clock_in_time')

        response = HttpResponse(content_type="text/csv")
        response['Content-Disposition'] = 'attachment; filename="attendances.csv"'

        writer = csv.writer(response)
        writer.writerow(['user', 'sats_balance', "event", "reward", "is_activated", "clock_in_time"])

        for att in checkins:
            print(f"att: ${att}")
            writer.writerow([f"${att.user.first_name} ${att.user.last_name}",att.user.sats_balance, att.event.name,att.event.reward, att.is_activated, att.clock_in_time])

        return response

class RegisterUser(APIView):
    serializer_class = AttendanceSerializer

    def post(self, request):
            try:
                first_name = request.data.get('first_name')
                last_name = request.data.get('last_name')
                phone_number = request.data.get('phone_number')
                session_id = request.data.get('session')
                session = EventSession.objects.get(pk=session_id)
                magic_string = request.data.get('magic_string')
                if magic_string is None or len(magic_string)==0:
                    random_data = os.urandom(32)
                    magic_string = '00' + random_data.hex()[2:64]
                    user=SatsUser.objects.create(magic_string=magic_string)
                else:
                    user = SatsUser.objects.get(magic_string=magic_string)

                existing_match = Attendance.objects.filter(user__magic_string=user.magic_string, eventSession=session).first()
                if existing_match:
                    responsedict = {'error': "You have already registered for this event"}
                    status = 403
                else:
                    att = Attendance.objects.create(
                        first_name=first_name,
                        last_name=last_name,
                        user=user,
                        event=session.parent_event,
                        eventSession= session,
                        phone_number=phone_number,
                        )
                    return Response(
                        data={
                            "message":"User has registered for event successfully!",
                            "data": {
                                "first_name": att.first_name,
                                "last_name": att.last_name,
                                "event": att.event.pk,
                                "magic_string": magic_string,
                                "phone_number": att.phone_number,
                            }
                        },
                        status=201
                    )
            except Exception as e:
                print(e)
                responsedict = {'error': 'Error Processing Request'}
                status = 500

            return Response(data=responsedict,status=status)       

    def get(self,request):
        try:
            event_id = request.query_params.get('event_id')
            event = Event.get_method(pk=event_id)
            responsedict = event
            status = 200
        except(Event.DoesNotExist): 
            responsedict = {'error': 'Event does not exist'}
            status = 404
        except Exception:
            responsedict = {'error': 'An unexpected error occured'}
            status = 500
        return Response(data=responsedict,status=status)

class RewardView(APIView):
    def generate_lnurl(self, request):
        title = request.GET.get("title")
        min_withdrawable = request.GET.get("min_withdrawable")
        max_withdrawable = request.GET.get("max_withdrawable")
        uses = request.GET.get("uses")
        wait_time = request.GET.get("wait_time")
        is_unique = request.GET.get("is_unique")
        webhook_url = request.GET.get("webhook_url")
        admin_key = request.GET.get("X-Api-Key")
        
        payload = {
            "title": title,
            "min_withdrawable": int(min_withdrawable),
            "max_withdrawable": int(max_withdrawable),
            "is_unique": True,
            "uses": 1, 
            "wait_time": 1
        }

        lnurl_endpoint = LNURL_ENDPOINT

        headers = {"Content-type": "application/json", "X-Api-Key": ADMIN_API_KEY}

        # Making a POST request to the LNURL generation endpoint
        response = requests.post(lnurl_endpoint, json=payload, headers=headers)

        if response.status_code == status.HTTP_201_CREATED:
            lnurl = response.json()
            return Response(data={"lnurl": lnurl}, status=status.HTTP_200_OK)
        else:
            return Response(data={"error": "Failed to generate LNURL"}, status=response.status_code)

    def get(self, request):
        # Call the generate_lnurl method
        return self.generate_lnurl(request)

class WithdrawCallbackView(APIView):
    def get(self, request):
        # Extract k1 token and Lightning invoice from query parameters
        k1_token = request.GET.get('k1')
        invoice = request.GET.get('invoice')
        # create_invoice = {
        #         "unit": "sat",
        #         "internal": False,
        #         "out": False,
        #         "amount": 10,
        #         "memo": "Payment memo", 
        # }
        # headers = {"Content-type": "application/json", "X-Api-Key": INVOICE_READ_KEY}
        # response = requests.post(LNURL_PAYMENTS_ENDPOINT, json=create_invoice, headers=headers)
        # Assuming response.content contains the JSON data
        # response_data = json.loads(response.content.decode('utf-8'))
        # payment_request = response_data.get("payment_request")
        pay_invoice = {
            "out": True,
            "bolt11": invoice,
        }
        payment_headers = {"Content-type": "application/json", "X-Api-Key": ADMIN_API_KEY}
        payment_response = requests.post(LNURL_PAYMENTS_ENDPOINT, json=pay_invoice, headers=payment_headers)
        return Response(payment_response.json())






