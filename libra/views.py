from rest_framework.decorators import api_view
from rest_framework.response import Response
import csv
from django.http import HttpResponse
import traceback

# Create your views here.
@api_view(['GET'])
def get_test(request):
    return Response("success3")


@api_view(['GET'])
def get_csv(request):
    try:
        # Create the HttpResponse object with the appropriate CSV header.
        response = HttpResponse(
            content_type='text/csv',
            headers={'Content-Disposition': 'attachment; filename="out.csv"'},
        )
        writer = csv.writer(response)

        with open('out.csv', 'r', encoding="utf8") as read_obj:
            csv_reader = csv.reader(read_obj)
            for row in csv_reader:
                writer.writerow(row)
    except:
        traceback.print_exc()

    return response
