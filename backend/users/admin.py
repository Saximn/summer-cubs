from django.contrib import admin
from .models import *

class PatientEntryAdmin(admin.ModelAdmin):
    model = PatientEntry
    list_display = ('get_patient_name', 'entry_time', 'completed')
    
    @admin.display(description='Patient Name', ordering='patient__name')
    def get_patient_name(self, obj):
        return obj.patient.name
  
class PatientAdmin(admin.ModelAdmin):
    model = Patient
    list_display = ('id', 'name')
    readonly_fields=('id',)

class MedicalStaffAdmin(admin.ModelAdmin):
    model = MedicalStaff
    list_display = ('name', 'role', 'id')
    readonly_fields=('id',)
  
class RoomAdmin(admin.ModelAdmin):
    model = Room
    list_display = ('room_number', 'floor', 'capacity')

# Register your models here.

admin.site.register(CustomUser)
admin.site.register(Patient, PatientAdmin)
admin.site.register(MedicalStaff, MedicalStaffAdmin)
admin.site.register(Room, RoomAdmin)
admin.site.register(PatientEntry, PatientEntryAdmin)