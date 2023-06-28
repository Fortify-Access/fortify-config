from django.shortcuts import render

# Create your views here.
def inbound_list(request):
    return render(request, 'inbounds/inbound_list.html')
