# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render

from django.http import JsonResponse

from datetime import datetime , timedelta

from django.views.decorators.csrf import csrf_exempt

import MySQLdb



#host = "192.168.1.200"
host = "aitat2.ckfsniqh1gly.us-west-2.rds.amazonaws.com"

tampered_time = 150 		# in seconds
device_accuracy_time = 3 	# in seconds

ideal_time = 5 			# in minutes


def query_database(sql):
       #global db
       	db = MySQLdb.connect(host,"IndigoProd","IndigoProd","IndigoProd")
	cursor = db.cursor()
	#print "Sql : " + sql
	try:
   		cursor.execute(sql)
   		rows = cursor.fetchall()
   		no_of_rows = cursor.rowcount
   # return (y0,y1,y2)
   		db.close()
   		return (rows, no_of_rows)
	except Exception as e:
   		print "Error in executing sql", e
   		return None
   		db.close()

def update_database(sql):

       	db1 = MySQLdb.connect(host,"IndigoProd","IndigoProd","IndigoProd")
       #global db1
	cursor = db1.cursor()
	#print "Sql : " + sql
	try:
   		cursor.execute(sql)
   		#rows = cursor.fetchall()
   		db1.commit()
           	db1.close()
   		return
	except Exception as e:
   		print "Error in executing sql", e
   		db1.rollback()
           	db1.close()

# Create your views here.

@csrf_exempt
def CustomTracker(request):

	if request.method == "POST":

		try:
			date_str  = request.POST.get("date")

			date = datetime.strptime(date_str, "%Y-%m-%d %H:%M:%S").date()

			print date

			custom_response = []


			try:

				sql = "SELECT distinct uuid from BeaconAlerts where LDate='%s';"%(str(date))

            			rows,no_of_rows = query_database(sql)

           			#print no_of_rows

				# mvmnts = Mvmnttrack.objects.filter(tdate=date).values('uuid').distinct()

				uuid_list = []    #location tracking list	

				ideal_list = []	  #ideal alert list

				tampered_list = [] # tampered alert list

				wrong_mvmnt_list = [] #wrong mvmnt alert list

				if len(rows) > 0:
				

					for row in rows:

						#print "------------step 3---------------"

						print row, type(row)

						uuid = row[0]

						registered = is_Registered(uuid)

						if registered:

							print "-------------------- UUID -----------------" + uuid

							status = checkStatus(uuid,date)


							if status == "active":

								print uuid + " is active"

								#sql = "SELECT UUID, DevId, LongLat , LogDate , Ldate from BeaconAlerts where LDate='%s' and UUID='%s' ORDER BY LTIME DESC LIMIT 1;"%(str(date),uuid)
		                        
		                        			sql = "SELECT UUID,DevId,MAX(LogDate), LDate , MAX(LogId) FROM BeaconAlerts WHERE LDate = '%s' and UUID = '%s' GROUP BY DevId ORDER BY LogDate DESC, MAX(LogDate) LIMIT 2;"%(str(date),uuid)
		                        			
		                        			print sql
		        					
		        					mvmnt_analyse, no_of_rows = query_database(sql)

		        					print mvmnt_analyse

		        					if no_of_rows > 1:

		        						print mvmnt_analyse[no_of_rows-2][2], mvmnt_analyse[no_of_rows-1][2]
		        					        
		        					        time_diff = (mvmnt_analyse[no_of_rows-2][2] - mvmnt_analyse[no_of_rows-1][2]).total_seconds()

		        					        print "time diff -------------------" + str(time_diff)

		        					        if time_diff <= device_accuracy_time:


		        					        	sql1 = "SELECT UUID,DevId,LogDate,LDate,LongLat,RSSI FROM BeaconAlerts WHERE LogId IN ('%s' , '%s');"%(mvmnt_analyse[0][4],mvmnt_analyse[1][4])
		        					        	#print sql1
		        							mvmnt1, no_of_rows = query_database(sql1)
		        							#print mvmnt1
		        							rssi1 = mvmnt1[1][5]
		        							rssi2 = mvmnt1[0][5]

		        							print rssi1, rssi2

		        							# sql2 = "SELECT RSSI FROM BeaconAlerts WHERE LogId='%s';"%(mvmnt_analyse[0][4])
		        							# mvmnt2, no_of_rows = query_database(sql)
		        							# rssi2 = mvmnt2[0][0]

		        							if rssi2 < rssi1:
		        								passenger_mvmnt = mvmnt1[0]
		        							else:
		        								passenger_mvmnt = mvmnt1[1]

		        					        	
		        					        else:
		        					        	#print "------------- time diff is large---------------------"
		        					        	sql = "SELECT UUID,DevId,LogDate, LDate, LongLat FROM BeaconAlerts WHERE LDate = '%s' and UUID = '%s' ORDER BY LogDate DESC LIMIT 1;"%(str(date),uuid)

		        							mvmnt_analyse, no_of_rows = query_database(sql)

		        							passenger_mvmnt = mvmnt_analyse[0]

		        					else:
		        						#print "-------------- No Multiple devices found ----------"
		        						sql = "SELECT UUID,DevId,LogDate, LDate, LongLat FROM BeaconAlerts WHERE LDate = '%s' and UUID = '%s' ORDER BY LogDate DESC LIMIT 1;"%(str(date),uuid)

		        						mvmnt_analyse, no_of_rows = query_database(sql)

		        						passenger_mvmnt = mvmnt_analyse[0]

		        					print "------------------- Final mvmnt ------------------"

		        					print passenger_mvmnt

								#check Ideal Alert Function

								is_ideal, mvmnt = IdealAlert(passenger_mvmnt)

								# print is_ideal , mvmnt


								if is_ideal:

									ideal_dic = {}

									ideal_dic["uuid"] = mvmnt[0][-4:]
									ideal_dic["devid"] = mvmnt[1]
									ideal_dic["time"] = mvmnt[2]
									print "ideal" + mvmnt[4]
									ideal_dic["long/lat"] = mvmnt[4]
									# ideal_dic["XY_Info"] = XYInfo(mvmnt[0][1])
									ideal_dic["AlertType"] = "IdealAlert"
									ideal_list.append(ideal_dic)

								# ------ END OF Function --------------



								#Check Tampered Alert Function

								is_tampered , mvmnt = TamperedAlert(passenger_mvmnt)

								if is_tampered:

									tampered_dic = {}

									
									tampered_dic["uuid"] = mvmnt[0][-4:]
									tampered_dic["devid"] = mvmnt[1]
									tampered_dic["time"] = mvmnt[2]
									tampered_dic["long/lat"]= mvmnt[4]
									# tampered_dic["XY_Info"] = XYInfo(mvmnt[0][1])
									tampered_dic["AlertType"] = "TamperedAlert"
									tampered_list.append(tampered_dic)


								# #------ END OF Function --------------



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

		    						print passenger_mvmnt

								# passenger_mvmnt = Mvmnttrack.objects.filter(tdate=date, uuid=uuid).order_by('-ttime')[0:1]
								uuid_dic["uuid"] = passenger_mvmnt[0][-4:]
								uuid_dic["devid"] = passenger_mvmnt[1]
								uuid_dic["time"] = passenger_mvmnt[2]
								uuid_dic["long/lat"] = passenger_mvmnt[4]
								# uuid_dic["XY_Info"] = XYInfo(passenger_mvmnt[0][1])
								uuid_dic["AlertType"] = "Success"
								uuid_dic["Info"] = "Location Tracking"
								 

								uuid_list.append(uuid_dic)
						

							        

							        #-------- END OF Function --------------
							
							else:
								print uuid + " is inactive"
						else:

							print uuid + " is not registered "
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



def IdealAlert(passenger_mvmnt):

	#sql = "SELECT UUID, DevId, LongLat , LogDate from BeaconAlerts where LDate='%s' and UUID='%s' ORDER BY LTIME DESC LIMIT 1;"%(str(date),uuid)

        print passenger_mvmnt

	# passenger_mvmnt = Mvmnttrack.objects.filter(tdate=date, uuid=uuid).order_by('-ttime')[0:1]
	latest_logdate = passenger_mvmnt[2]
	date = passenger_mvmnt[3]
	uuid = passenger_mvmnt[0]
	print datetime.now() , latest_logdate


	old_logdate = latest_logdate - timedelta(minutes=ideal_time)

	
	sql1 = "SELECT DevId, MAX(LogDate) from BeaconAlerts WHERE LDate='%s' and UUID='%s' and LogDate BETWEEN '%s' AND '%s' GROUP BY DevId"%(str(date),uuid, old_logdate,latest_logdate)
	print sql1

	mvmnt, no_of_rows = query_database(sql1)
	print "ideal"
	print  mvmnt

	#mvmnt = Mvmnttrack.objects.filter(tdate=date, uuid=uuid , ttime__lte=New_TTime).order_by('-ttime')[0:1]

	if no_of_rows == 1 :

		last_rec_date = mvmnt[0][1]

		sql1 = "SELECT LogCreated FROM BeaconAllocations WHERE UUID = '%s' AND Status = 1 ORDER BY LogCreated DESC"%(uuid)
		print sql1
		record , no_of_rows = query_database(sql1)

		active_date = record[0][0] + timedelta(minutes=330)

		print active_date 

		time_diff = (last_rec_date - active_date).total_seconds()

		print "active since " + str(time_diff) + " secs"

		if time_diff > 300:

			return True , passenger_mvmnt

		else:
			return False, passenger_mvmnt

	else:
		
		return False , passenger_mvmnt



	
def TamperedAlert(passenger_mvmnt):

	try:	
		latest_logdate = passenger_mvmnt[2]

		# last_beac = Mvmnttrack.objects.filter(tdate=date, uuid=uuid).order_by('-ttime')[0:1]

		beac_since = ( datetime.now().replace(microsecond=0) - latest_logdate ).total_seconds()

		print beac_since

		if beac_since > tampered_time:
			print "generate alert"
			return True , passenger_mvmnt
		else:
			print "Beacon is working"
			return False, passenger_mvmnt

	except Exception as e:
		print "Problem in Tampered Alert query No Beacon found for this date"
		raise e




def MvmntAlert(uuid,date):

	try:

		wrong_mvmnt = "ILad101_-ILad104_"

		sql1 = "SELECT UUID, DevId, LongLat , LogDate from BeaconAlerts where LDate='%s' and UUID='%s' ORDER BY LTIME ASC;"%(str(date),uuid)

		print sql1

		mvmnts, no_of_rows = query_database(sql1) 

		# mvmnts = Mvmnttrack.objects.filter(tdate=date, uuid=uuid).order_by('ttime')

		# mvmnt_obj = Mvmnttrack.objects.filter(tdate=date, uuid=uuid).order_by('-ttime')[0:1]

		mvmnt_tracker_list = []

		for mvmnt in mvmnts:

			devid = mvmnt[1]

			if len(mvmnt_tracker_list) == 0:
				mvmnt_tracker_list.append(devid)

			elif mvmnt_tracker_list[len(mvmnt_tracker_list) - 1] != devid:
				mvmnt_tracker_list.append(devid)

			else:
				print "Same location of Beac"

		for i in range(len(mvmnt_tracker_list) - 1):

			if len(mvmnt_tracker_list) > 1:

				mvmnt_beac = mvmnt_tracker_list[i] + "-"  + mvmnt_tracker_list[i+1]

				print "Mvmnt for beacon: " + mvmnt
			
				if mvmnt_beac == wrong_mvmnt:

					print "ALERT WRONG MVMNT"
					return True, mvmnt_obj

		mvmnt_obj = []

		return False, mvmnt_obj

	except Exception as e:
		print "Problem in Mvmnt Alert"
		raise e


def checkStatus(uuid,date):

	date1 = str(date) + " 00:00:00"
	date2 = str(date) + " 23:59:59"

	sql = "SELECT Status , LogCreated FROM BeaconAllocations WHERE LogCreated BETWEEN '%s' AND '%s' AND UUID='%s' ORDER BY LogCreated DESC;"%(date1, date2, uuid)
	print "checkStatus -- " + sql
	#sql = "SELECT Status,LogUpdated FROM BeaconAllocations WHERE UUID = '%s' AND LogDate BETWEEN '%s' AND '%s' ORDER BY SLogDate DESC;"%(uuid,date1,date2)
	record , no_of_rows = query_database(sql)

	if no_of_rows >= 1:

		status = record[0][0]

		if status == 1:
			return "active"
		elif status == 0:
			return "inactive"

	else:
		print uuid + " activity not running yet"
		return "inactive"


def is_Registered(uuid):

	sql = "SELECT UUID , Status FROM BeaconMaster WHERE UUID = '%s';" %(uuid)

	records, no_of_rows = query_database(sql)

	if no_of_rows == 1:

		status = records[0][1]
		print status

		if status == 1:

			return True
		else:
			return False
	else:
		return False		




# def XYInfo(devid):

# 	sql1 = "SELECT XYInfo FROM DevcMaster WHERE DevcId = '%s';" %(devid)

# 	print sql1

# 	mvmnt, no_of_rows = query_database(sql1)

# 	print no_of_rows ,  mvmnt

# 	xy_info = mvmnt[0][0]

# 	return xy_info


def get_devices(request):

	sql = "SELECT DevcId, LatLong, XYInfo from DevcMaster;"
        rows,no_of_rows = query_database(sql)
        print rows

        data = []

        for row in rows:
        	dic = {}
        	dic["devid"] = row[0]
        	dic["latlong"] = row[1]
        	dic["XYInfo"] = row[2]
        	data.append(dic)

       	return JsonResponse({"Message":"Success", "data":data})




#wrong_mvmnt
#ideal_time
#tampered_time

# @csrf_exempt
# def StatusConfiguration(request):

# 	if request.method == "POST":

# 		try:
# 			uuid = request.POST.get("uuid")


# 			sql = "SELECT UUID, Status FROM BeaconMaster WHERE UUID = '%s';" %(uuid)
# 			mvmnts, no_of_rows = query_database(sql)

# 			print mvmnts

# 			new_status = 0

# 			if no_of_rows == 1:

# 				status = mvmnts[0][1]
# 				print status

# 				if status == 0:
# 					new_status = 1
# 				elif status == 1:
# 					new_status = 0

# 				print str(new_status) + " new status"

# 				sql1 = "UPDATE BeaconMaster SET Status = '%s' WHERE UUID = '%s';"%(new_status,uuid)
# 				update_database(sql1)	

# 				return JsonResponse({"message":"success", "status":"status has been changed to " + str(new_status)})
# 			else:
# 				return JsonResponse({"message":"success", "status": uuid + " not registered"})


# 		except Exception as e:
# 			raise e

		

# 	else:
# 		return JsonResponse({"status":"failed", "message":"request type is not a POST"})






@csrf_exempt
def BeaconAllocation(request):


	try:
		if request.method == "POST":


			try:
				
				uuid = request.POST.get("uuid")
				devid = request.POST.get("devid")

			except Exception as e:
				return JsonResponse({"status":"failed", "message":" paramters not given"})
				raise e


			date1 = str(datetime.now().date()) + " 00:00:00"
			date2 = str(datetime.now().date()) + " 23:59:59"

			print date1, date2

			sql = "SELECT LogId , LogCreated FROM BeaconAllocations WHERE LogCreated BETWEEN '%s' AND '%s' AND Status = 1 AND UUID='%s' ORDER BY LogCreated DESC;"%(date1, date2, uuid)
			record, no_of_rows = query_database(sql)

			print sql , record

			set_status = 1

			if no_of_rows >= 1:

				logid = record[0][0]
				sql1 = "UPDATE BeaconAllocations SET Status = 0 WHERE LogId = '%s';" %(logid)
				update_database(sql1)
				set_status = 0

				return JsonResponse({"message":"success", "status": set_status})

			else:
				print "Hi"
				sql1= "INSERT INTO BeaconAllocations (DevId, UUID, Status) VALUES ('" + str(devid)  + "','" + str(uuid) + "',1);"
				print sql1
				update_database(sql1)
				print "Bye"

				return JsonResponse({"message":"success", "status": set_status})
	except Exception as e:

		raise e

		return JsonResponse({"status":"failed", "message":" paramters not given"})

	
	