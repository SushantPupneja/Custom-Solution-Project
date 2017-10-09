# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models

# Create your models here.

class Mvmnttrack(models.Model):
    logid = models.AutoField(db_column='Logid', primary_key=True)  # Field name made lowercase.
    uuid = models.CharField(db_column='UUID', max_length=50, blank=True, null=True)  # Field name made lowercase.
    rssi_int = models.IntegerField(db_column='RSSI_INT', blank=True, null=True)  # Field name made lowercase.
    event = models.CharField(db_column='Event', max_length=10, blank=True, null=True)  # Field name made lowercase.
    longlat = models.CharField(db_column='LongLat', max_length=60, blank=True, null=True)  # Field name made lowercase.
    devid = models.CharField(db_column='DevId', max_length=15, blank=True, null=True)  # Field name made lowercase.
    sortid = models.IntegerField(db_column='SortId')  # Field name made lowercase.
    status = models.IntegerField(blank=True, null=True)
    flogdate = models.DateTimeField(db_column='FLogDate', blank=True, null=True)  # Field name made lowercase.
    tlogdate = models.DateTimeField(db_column='TLogDate', blank=True, null=True)  # Field name made lowercase.
    fdate = models.DateField(db_column='FDate', blank=True, null=True)  # Field name made lowercase.
    ftime = models.TimeField(db_column='FTIME', blank=True, null=True)  # Field name made lowercase.
    tdate = models.DateField(db_column='TDate', blank=True, null=True)  # Field name made lowercase.
    ttime = models.TimeField(db_column='TTIME', blank=True, null=True)  # Field name made lowercase.
    duration = models.IntegerField(db_column='Duration', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'MvmntTrack'

