# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render

from django.http import JsonResponse

from datetime import datetime , timedelta

from django.views.decorators.csrf import csrf_exempt

from .models import Mvmnttrack

from django.utils import timezone

from django.core import serializers

import json

import ast


# Create your views here.

@csrf_exempt
def CustomTracker(request):

	if request.method == "POST":

		try:

		#	from_slot = request.POST.get("fromTime")
		#	to_slot  = request.POST.get("toTime")
			date_str  = request.POST.get("date")


		#	from_time = datetime.strptime(from_slot, '%Y-%m-%d %H:%M:%S').time()
		#	to_time = datetime.strptime(to_slot, '%Y-%m-%d %H:%M:%S').time()
			date = datetime.strptime(date_str, "%Y-%m-%d %H:%M:%S").date()

			print date

			custom_response = []


			try:

				mvmnts = Mvmnttrack.objects.filter(tdate=date).values('uuid').distinct()
				# rows = json.loads(serializers.serialize("json", mvmnts))
				# print rows
				print mvmnts
				print len(mvmnts)

				uuid_list = []    #location tracking list	

				ideal_list = []	  #ideal alert list

				tampered_list = [] # tampered alert list

				wrong_mvmnt_list = [] #wrong mvmnt alert list

				if mvmnts is not None:
				

					for row in mvmnts:
						print "step 3"
						print row, type(row)

						
						# row1 = serializers.serialize("json", row)
						
						#print row.uuid
						d = ast.literal_eval(str(row))
						var= json.loads(json.dumps(d))
						uuid = str(var['uuid'])
					
						# print(var1['uuid'], type(d))
						# print()
						# print row1["uuid"]
						#uuid = row["uuid"]


						# #check Ideal Alert Function

						# is_ideal, mvmnt = IdealAlert(uuid,date)

						# print is_ideal , mvmnt

						# if is_ideal:

						# 	ideal_dic = {}
						# 	checkflag = 1

						# 	for val in ideal_list:
						# 		if uuid in val.values():
						# 			checkflag = 0

						# 	if checkflag == 1:
						# 		ideal_dic["uuid"] = mvmnt.uuid
						# 		ideal_dic["devid"] = mvmnt.devid
						# 		ideal_dic["long/lat"] = mvmnt.longlat
						# 		ideal_dic["time"] = mvmnt.time
						# 		ideal_list.append(ideal_dic)

						#------ END OF Function --------------



						# #Check Tampered Alert Function

						# is_tampered , beac_obj = TamperedAlert(uuid,date)

						# if is_tampered:

						# 	tampered_dic = {}
						# 	checkflag = 1

						# 	for val in tampered_list:
						# 		if uuid in val.values():
						# 			checkflag = 0

						# 	if checkflag == 1:

						# 		tampered_dic["uuid"] = beac_obj.uuid
						# 		tampered_dic["devid"] = beac_obj.devid
						# 		tampered_dic["long/lat"] = beac_obj.longlat
						# 		tampered_dic["LastReprted"] = beac_obj.ttime
						# 		tampered_dic["AlertType"] = "TamperedAlert"
						# 		tampered_list.append(tampered_dic)


						#------ END OF Function --------------



						#check for wrong Mvmnt Alert function

						# is_wrong_mvmnt , mvmnt = MvmntAlert(uuid,date)

						# if is_wrong_mvmnt:

						# 	wrong_mvmnt_dic = {}
						# 	checkflag = 1

						# 	for val in wrong_mvmnt_list:
						# 		if uuid in val.values():
						# 			checkflag = 0

						# 	if checkflag == 1:
						# 		wrong_mvmnt_dic["uuid"] = mvmnt.uuid
						# 		wrong_mvmnt_dic["devid"] = mvmnt.devid
						# 		wrong_mvmnt_dic["long/lat"] = mvmnt.longlat
						# 		mvmnt_tracker_list.append(wrong_mvmnt_dic)


						#location tracking Function

						uuid_dic = {}

						checkflag = 1

						for val in uuid_list:
							if uuid in val.values():
								checkflag = 0

						if checkflag == 1:
								print uuid
								passenger_mvmnt = Mvmnttrack.objects.filter(tdate=date, uuid=uuid).order_by('-ttime')[0:1]
								print passenger_mvmnt
								uuid_dic["uuid"] = passenger_mvmnt.uuid
								uuid_dic["devid"] = passenger_mvmnt[0].devid
								uuid_dic["long/lat"] = passenger_mvmnt[0].longlat
								uuid_dic["time"] = passenger_mvmnt[0].ttime
								uuid_dic["AlertType"] = "Success"
								uuid_dic["Info"] = "Location Tracking"
								 

								uuid_list.append(uuid_dic)

						else:
							print "uuid exists"

						#-------- END OF Function --------------
					
				else:
					print "No data"

				custom_response_dic = {}
				custom_response_dic["Location_Tracker"] = uuid_list
				custom_response_dic["Ideal_Alert"] = ideal_list
				custom_response_dic["Tampered_Alert"] = tampered_list
				custom_response_dic["Wrong_Mvmnt_Tracker"] = wrong_mvmnt_list

				custom_response.append(custom_response_dic)
				
				status = "Success"

				
				if len(uuid_list) == 0:
					uuid_list = "No Beac Found"

					

			except Exception as e:
				raise e
				print "Database query Failed"
				status = "success"
				uuid_list = "Empty List"

		except Exception as e:
			raise e
			print e
			print "Incorrect parameters given"
			status = "Failed"
			custom_response = "Incorrect parameters given"



		return JsonResponse({"Status":status, "data":custom_response})

	else:
		return JsonResponse({"status":"failed", "msg":"missing parameters"})



def IdealAlert(uuid,date):

	passenger_mvmnt = Mvmnttrack.objects.filter(tdate=date, uuid=uuid).order_by('-ttime')[0:1]
	old_lat_long = passenger_mvmnt[0].longlat

	print datetime.now() , old_lat_long

	ideal_time = 5

	New_TTime = datetime.now() - timedelta(minutes=5)

	

	mvmnt = Mvmnttrack.objects.filter(tdate=date, uuid=uuid , ttime__lte=New_TTime).order_by('-ttime')[0:1]

	print len(mvmnt)

	if len(mvmnt) !=0 :

		new_lat_long = mvmnt[0].longlat

		if (old_lat_long == new_lat_long) and (old_lat_long != ''):

			print New_TTime , new_lat_long

			return True , mvmnt[0]

		else:
			print New_TTime , new_lat_long
			return False , mvmnt[0]


	else:
		mvmnt = []
		print "No Data Found"
		return False , mvmnt


		

	
def TamperedAlert(uuid,date):

	try:
		last_beac = Mvmnttrack.objects.filter(tdate=date, uuid=uuid).order_by('-ttime')[0:1]
		last_time = last_beac[0].tlogdate

		beac_since = int(round(( timezone.now() - last_time ).total_seconds() / 60))

		if beac_since > 2:
			print "generate alert"
			return True , last_beac[0]
		else:
			print "Beacon is working"
			return False, last_beac[0]

	except Exception as e:
		print "Problem in Tampered Alert query No Beacon found for this date"
		raise e




def MvmntAlert(uuid,date):

	try:

		wrong_mvmnt = "D1-D2-D3"

		mvmnts = Mvmnttrack.objects.filter(tdate=date, uuid=uuid).order_by('ttime')

		mvmnt_obj = Mvmnttrack.objects.filter(tdate=date, uuid=uuid).order_by('-ttime')[0:1]

		mvmnt_tracker_list = []

		for mvmnt in mvmnts:

			devid = mvmnt.devid

			if len(mvmnt_tracker_list) == 0:
				mvmnt_tracker_list.append(devid)

			elif mvmnt_tracker_list[len(mvmnt_tracker_list) - 1] != devid:
				mvmnt_tracker_list.append(devid)

			else:
				print "Same location of Beac"

		for i in range(len(mvmnt_tracker_list) - 2):

			if len(mvmnt_tracker_list) > 2:

				mvmnt_beac = mvmnt_tracker_list[i] + "-"  + mvmnt_tracker_list[i+1] + "-" + mvmnt_tracker_list[i+2]
				print "Mvmnt for beacon: " + mvmnt
			
				if mvmnt_beac == wrong_mvmnt:

					print "ALERT WRONG MVMNT"
					return True, mvmnt_obj

		mvmnt_obj = []

		return False, mvmnt_obj

	except Exception as e:
		print "Problem in Mvmnt Alert"
		raise e









#wrong_mvmnt
#ideal_time
#tampered_time
