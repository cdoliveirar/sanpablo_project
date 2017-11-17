from django.conf.urls import url
from .views import (PatientRegisterView,

                    DoctorLogin,
                    EnterpriseHeadquarters,
                    ClinicsList,
                    EmergencyAttentionList,
                    EmergencyDoctor,
                    SpecialistDoctor,
                    MedicalHistoryList,
                    MedicalHistoryDetail,
                    PatientView,
                    PatientUpdateToken,
                    PatientByTokenList,
                    DoctorUpdateLocationView,
                    MedicalHistoryUpdate,
                    PatientVerifyView,
                    PatientAppointments,
                    PatientHistoryView,
                    ArtifactMeasurementView,
                    MeasurementWeight,
                    MeasurementBodyTemperature,
                    BloodPressure,
                    PatientUpdate,
                    CallDoctorView,
                    MedicalHistorySpecialistList,
                    CallActivate,
                    ArtifactMeasurementTool,
                    PatientRegisterView,
                    #MedicalHistoryRegister,
                    MedicalHistoryListByEmergDoctor,
                    MedicalHistoryUpdating,
                    DoctorListView,
                    DoctorUpdateAttention,
                    CompetitionView,
                    )

urlpatterns = [
    # sanpablo
    url(r'^patientregister/$', PatientRegisterView.as_view(), name='patient_register'),
    url(r'^doctor_list/$', DoctorListView.as_view(), name='patient_register'),
    url(r'^doctor_update_attention/(?P<pk>[0-9]+)/$', DoctorUpdateAttention.as_view(), name='patient'),
    url(r'^competition/$',CompetitionView.as_view()),


    url(r'^doctorlogin/$', DoctorLogin.as_view(), name='doctorlogin'),


    url(r'^headquarters/(?P<enterprise_id>\d+)/$', EnterpriseHeadquarters.as_view(), name='headquarters'),

    url(r'^enterprise/$', ClinicsList.as_view(), name='enterprise'),
    url(r'^emergency_attention/(?P<location_id>\d+)/$', EmergencyAttentionList.as_view(), name='emergency_attention'),

    # list of emergency people by local
    url(r'^specialist_doctor/headquarters/(?P<location_id>\d+)/emergency_attention/(?P<emergency_attention_id>\d+)/$', SpecialistDoctor.as_view(), name='specialist_doctor'),
    url(r'^emergency_doctor/(?P<location_id>\d+)/$', EmergencyDoctor.as_view(), name='emergency_doctor'),

    # medical history by emergencista within doctor_id
    url(r'^emergency_history/doctor/(?P<doctor_id>\d+)/location/(?P<location_id>\d+)/emergency_doctor/(?P<emergency_doctor_id>\d+)/$',
        MedicalHistoryList.as_view(), name='emergency_history'),


    # medical history ONLY by emergencista
    url(r'^emergency_history/emergency_doctor/(?P<emergency_doctor_id>\d+)/location/(?P<location_id>\d+)/$',
        MedicalHistoryListByEmergDoctor.as_view(), name='emergency_doctor_history'),

    # medical history by specialist
    url(r'^emergency_history/doctor/(?P<doctor_id>\d+)/location/(?P<location_id>\d+)/$',
        MedicalHistorySpecialistList.as_view(), name='emergency_history'),


    url(r'^medical_history_detail/(?P<medical_history_id>\d+)/$', MedicalHistoryDetail.as_view(), name='medical_history_detail'),

    # updating medical history detail
    url(r'^medical_history_updating/$', MedicalHistoryUpdating.as_view(), name='medical_history_detail'),


    # patient
    url(r'^patient_verify/$', PatientView.as_view(), name='patient_verify'),
    url(r'^patient_register/$', PatientRegisterView.as_view(), name='patient_register'),

    url(r'^patient_update_token/(?P<pk>[0-9]+)/$', PatientUpdateToken.as_view(), name='patient'),
    url(r'^patient_token/(?P<token_sinch>[\w\-]+)/$', PatientByTokenList.as_view(), name='patient'),


    #  update doctor headquarters
    url(r'^update_doctor_headquarters/(?P<location_id>\d+)/doctor/(?P<doctor_id>\d+)/$',
        DoctorUpdateLocationView.as_view(), name='patient'),
    url(r'^medical_history_update/(?P<pk>\d+)/$', MedicalHistoryUpdate.as_view(), name='medical_history_update'),

    # ocupacional
    url(r'^patientverify/$', PatientVerifyView.as_view(), name='patient_verify'),
    url(r'^patient_appointments/(?P<patient_id>\d+)/$', PatientAppointments.as_view(), name='patient_appointments'),

    # patient history
    url(r'^patienthistory/(?P<patient_id>\d+)/$', PatientHistoryView.as_view(), name='patient_history'),

    #artifacts measures
    url('^artifact_measurement/(?P<token_sinch>[\w\-]+)/$', ArtifactMeasurementView.as_view(), name='artifact_measurement'),
    url('^artifact_measurement_tool/$', ArtifactMeasurementTool.as_view(), name='artifact_measurement'),

    url('^artifact_weight/$', MeasurementWeight.as_view(), name='artifact_measurement'),
    url('^artifact_body_temperature/$', MeasurementBodyTemperature.as_view(), name='artifact_measurement'),
    url('^artifact_blood_pressure/$', BloodPressure.as_view(), name='artifact_measurement'),


    url(r'^patient_update/(?P<pk>\d+)/$', PatientUpdate.as_view(), name='patient_update'),

    url(r'^call_doctor/(?P<midoc_user>[\w\-]+)/$', CallDoctorView.as_view(), name='call_doctor'),

    # only one character , 1 or 0
    url(r'^call_activate/doctor_id/(?P<doctor_id>\d+)/status/(?P<activate>[\w.]+)/$', CallActivate.as_view(), name='call_activate'),

    #medical history register
    #url(r'^medical_history_register/$', MedicalHistoryRegister.as_view(), name='medical_history_register'),




]