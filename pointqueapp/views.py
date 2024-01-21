from django.shortcuts import render
from django.shortcuts import redirect
from django.contrib.auth import login, logout
from django.contrib.auth.forms import AuthenticationForm
from .forms import InitialPointPieceForm, CompletePointPieceForm, DCSelectForm
from django.utils import timezone
from .models import PointPiece, DC, Associate, RepairType, PartType, Route
from django.shortcuts import get_object_or_404
import requests
from django.contrib import messages
from django.contrib.auth.models import User
from requests.exceptions import ConnectionError, RequestException
from django.conf import settings
import pandas as pd
import xlsxwriter
from django.http import HttpResponse
from django_pandas.io import read_frame
import pytz
from django.utils.timezone import make_naive, get_default_timezone
from datetime import datetime, timedelta



def index(request):
    if request.method == "POST":
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            login(request, form.get_user())
            return redirect('pointqueapp:set_dc')
    else:
        form = AuthenticationForm()
        form.fields['username'].widget.attrs.update({'placeholder': 'Username'})
        form.fields['password'].widget.attrs.update({'placeholder': 'Password'})
    return render(request, 'pointqueapp/index.html', {'form': form})

def set_dc(request):
    if request.method == 'POST':
        form = DCSelectForm(request.POST)
        if form.is_valid():
            request.session['selected_dc'] = form.cleaned_data['dc'].id
            return redirect('pointqueapp:tech_que')
    else:
        form = DCSelectForm()
    return render(request, 'pointqueapp/dc_select.html', {'form': form})



def tech_que(request):
    selected_dc_id = request.session.get('selected_dc')
    if not selected_dc_id:
        return redirect('pointqueapp:set_dc')
    dc = get_object_or_404(DC, id=selected_dc_id)
    
    print(f"DC: {dc}")
    queue = PointPiece.objects.filter(end_time__isnull=True, dc=dc ).order_by('start_time')
    
    
    if request.method == "POST":
            initial_form = InitialPointPieceForm(request.POST or None)
            complete_form = CompletePointPieceForm(request.POST or None, selected_dc=dc)

            if 'initial_form' in request.POST:
                if initial_form.is_valid():
                    point_piece = initial_form.save(commit=False, selected_dc=dc)
                    lp = initial_form.cleaned_data['lp']
                    if PointPiece.objects.filter(lp=lp, end_time__isnull=True).exists():
                        messages.error(request, "This LP is already in the queue.")
                    else:
                        try:
                            headers = {'API-Key': settings.API_KEY}
                            response = requests.get(f"http://localhost:8000/MockJumpApp/api/get_sku/?lp={lp}", headers=headers)
                            sku_data = response.json()
                            sku = sku_data.get('sku')
                            if sku:
                                point_piece.sku = sku
                                point_piece.line_time = timezone.now()
                                point_piece.save()
                                messages.success(request, "The piece has been added to the queue.")
                            else:
                                messages.error(request, "SKU not found/invalid LP.")
                        except ConnectionError:
                            messages.error(request, "Failed to Connect to SKU Service")
                        except RequestException as e:
                            messages.error(request, f"Error: {e}")
                    return redirect('pointqueapp:tech_que')
            elif 'complete_form' in request.POST:
                if complete_form.is_valid():
                    point_piece_instance = complete_form.cleaned_data['lp']
                    associate = complete_form.cleaned_data['associate']
                    repair = complete_form.cleaned_data['repair']
                    part = complete_form.cleaned_data['part']
                    point_piece_instance.associate = associate
                    point_piece_instance.repair.set(repair)
                    point_piece_instance.part.set(part)
                    point_piece_instance.start_time = timezone.now()
                    point_piece_instance.save()

                    messages.success(request, "The piece status has been updated.")
                else:
                    print(complete_form.errors)

                return redirect('pointqueapp:tech_que')
            
            else:
                
                messages.error(request, "There was an error with your submission.")

    else:
        initial_form = InitialPointPieceForm()
        complete_form = CompletePointPieceForm(selected_dc=dc)

    return render(request, 'pointqueapp/tech_que.html', {
        'initial_form': initial_form,
        'complete_form': complete_form,
        'queue': queue,
    })


def update_status(request, piece_id):
    point_piece = get_object_or_404(PointPiece, id=piece_id)

    if request.method == "POST":
        if point_piece.associate and point_piece.start_time:
            point_piece.end_time = timezone.now()
            point_piece.status = 'Repair Complete'
            point_piece.save()
            messages.success(request, "Piece marked as complete.")
        else:
            messages.error(request, "Cannot mark as complete. Please fill out all required fields.")

        return redirect('pointqueapp:tech_que') 

    return redirect('pointqueapp:tech_que')


  # Make sure you have pytz installed or use Django's timezone support


def data(request):
    dcs = DC.objects.all()
    start_date_param = request.GET.get('start_date')
    end_date_param = request.GET.get('end_date')
    sort_by = request.GET.get('sort_by', 'line_time')
    dc_param = request.GET.get('dc')

    ninety_days_ago = datetime.now() - timedelta(days=90)
    start_date_default = ninety_days_ago.replace(hour=0, minute=0, second=0)
    end_date_default = datetime.now().replace(hour=23, minute=59, second=59)

    try:
        start_date = datetime.strptime(start_date_param, "%Y-%m-%d") if start_date_param else start_date_default
        end_date = datetime.strptime(end_date_param, "%Y-%m-%d").replace(hour=23, minute=59, second=59) if end_date_param else end_date_default
    except ValueError:
        messages.error(request, "Incorrect date format. Please use YYYY-MM-DD.")
        start_date, end_date = start_date_default, end_date_default  # Fallback to defaults

    repairs_qs = PointPiece.objects.filter(line_time__range=(start_date, end_date))

    if dc_param and dc_param.isdigit():
        repairs_qs = PointPiece.objects.filter(dc=dc_param).order_by(sort_by)

    formatted_start_date = start_date.strftime("%m-%d-%Y")
    formatted_end_date = end_date.strftime("%m-%d-%Y")

    repairs_qs = repairs_qs.order_by(sort_by).prefetch_related('repair', 'part', 'associate', 'dc')
    if 'export_to_excel' in request.GET:
        # Query all PointPiece objects and prefetch related objects for efficiency

        # Build a list of dictionaries with the data for the DataFrame
        data = []
        for piece in repairs_qs:
            # Convert datetime fields to naive in the default timezone
            line_time_naive = make_naive(piece.line_time, get_default_timezone()) if piece.line_time else None
            start_time_naive = make_naive(piece.start_time, get_default_timezone()) if piece.start_time else None
            end_time_naive = make_naive(piece.end_time, get_default_timezone()) if piece.end_time else None
            
            piece_data = {
                'ID': piece.id,
                'Associate': piece.associate.associate if piece.associate else '',
                'SKU': piece.sku,
                'LP': piece.lp,
                'Route': piece.route,
                'DC': piece.dc.dc if piece.dc else '',
                'Stock Type': piece.get_stock_type_display(),
                'Status': piece.get_status_display(),
                'Line Time': line_time_naive,
                'Start Time': start_time_naive,
                'End Time': end_time_naive,
                'Repairs': ', '.join([repair.repair_type for repair in piece.repair.all()]),
                'Parts': ', '.join([part.part_type for part in piece.part.all()]),
            }
            data.append(piece_data)

        # Convert the list of dictionaries to a DataFrame
        df = pd.DataFrame(data)

        # Define the Excel response
        response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        response['Content-Disposition'] = 'attachment; filename="repairs.xlsx"'

        # Write the DataFrame to the Excel file
        with pd.ExcelWriter(response, engine='xlsxwriter') as writer:
            df.to_excel(writer, index=False)
            workbook = writer.book
            worksheet = writer.sheets['Sheet1']
            # Format the datetime columns
            datetime_format = writer.book.add_format({'num_format': 'yyyy-mm-dd hh:mm:ss', 'align': 'center'})
            wrap_center_format = writer.book.add_format({'text_wrap': True, 'align': 'center'})
            worksheet.set_column('A:A', 10, wrap_center_format)  # Column ID width
            worksheet.set_column('B:B', 20, wrap_center_format)  # Column Associate width
            worksheet.set_column('C:C', 10, wrap_center_format)  # Column SKU width
            worksheet.set_column('D:D', 30, wrap_center_format)  # Column LP width
            worksheet.set_column('E:E', 10, wrap_center_format)  # Column Route width
            worksheet.set_column('F:F', 10, wrap_center_format)  # Column DC width
            worksheet.set_column('G:G', 15, wrap_center_format)
            worksheet.set_column('H:H', 30, wrap_center_format)  
            worksheet.set_column('I:I', 25, datetime_format)  
            worksheet.set_column('J:J', 25, datetime_format)
            worksheet.set_column('K:K', 25, datetime_format)
            worksheet.set_column('L:L', 35, wrap_center_format)  
            worksheet.set_column('M:M', 35, wrap_center_format)

        return response

    context = {
        'repairs': repairs_qs,
        'start_date': start_date.strftime("%Y-%m-%d"),
        'end_date': end_date.strftime("%Y-%m-%d"),
        'formatted_start_date': formatted_start_date,
        'formatted_end_date': formatted_end_date,
        'dcs': dcs,
        
    }
    
    return render(request, 'pointqueapp/data.html', context)



def tv_display(request):
    all_routes = Route.objects.all()
    selected_route_codes = request.GET.getlist('route')

    # Get today's date
    today = timezone.localdate()

    # Filter based on selected routes and today's date
    if selected_route_codes:
        pieces = PointPiece.objects.filter(route__in=selected_route_codes, line_time__date=today).order_by('line_time')
    else:
        pieces = PointPiece.objects.filter(line_time__date=today).order_by('line_time')

    context = {
        'pieces': pieces,
        'all_routes': all_routes,
        'selected_route_codes': selected_route_codes
    }
    return render(request, 'pointqueapp/tv_display.html', context)


def logout_request(request):
    logout(request)   
    return render(request, 'pointqueapp/logout.html')



