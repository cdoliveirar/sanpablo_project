import json
import sys
from django.core.serializers.json import DjangoJSONEncoder
from django.http import HttpResponse, Http404
from django.db import transaction
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.renderers import JSONRenderer
from .utils import calculate_age, validate_one_character, getAuthTicket
from .serializers import (DoctorSerializer,
                        EnterpriseSerializer,
                        DoctorLocalSerializer,
                        MedicalHistorySerializer,
                        PatientSerializer,
                        PatientVerifySerializer,
                        ArtifactMeasurementSerializer,
                        #PatientHistorySerializer
                        PatientUpdatingSerializer
                          )
from .models import (Doctor,
                    Location,
                    Enterprise,
                    EmergencyAttention,
                    LocationEmergencyAttention,
                    MedicalHistory,
                    Patient,
                    MedicalHistoryMedia,
                    Appointment,
                    ArtifactMeasurement,
                    )



# check
class DoctorLogin(APIView):
    serializer_class = DoctorSerializer

    def get(self, request, format=None):
        doctor = Doctor.objects.all()
        serializer = DoctorSerializer(doctor, many=True)
        return Response(serializer.data)

    def post(self, request, format=None):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        vd = serializer.validated_data

        print(vd)
        print(vd.get("midoc_user"))
        print(vd.get("password"))
        try:
            if Doctor.objects.filter(midoc_user__exact=vd.get("midoc_user")).exists() \
                    and Doctor.objects.filter(password__exact=vd.get("password")).exists():
                doctor = Doctor.objects.get(midoc_user=vd.get("midoc_user"))
                print(doctor.pk)
                print(doctor.doctor_name)
                print(doctor.midoc_user)
                print(doctor.password)

                user = {'username': vd.get("midoc_user")}

                ticket = getAuthTicket(user)

                print(doctor.location_id)
                location = Location.objects.get(pk=doctor.location_id)
                #location.enterprise.picture_url_enterprise

                d = {"id": doctor.pk, "cmd_peru": doctor.cmd_peru, "degree": doctor.degree, "doctor_name": doctor.doctor_name,
                     "year_of_birth": doctor.year_of_birth, "picture_url": doctor.picture_url, "location_id":doctor.location_id,
                     "email": doctor.email, "midoc_user": doctor.midoc_user, "password": doctor.password,
                     "type_of_specialist": doctor.type_of_specialist, "is_enabled":doctor.is_enabled,
                     "picture_url_enterprise": location.enterprise.picture_url_enterprise, "ticket":ticket  }
                print(d)
                return Response(d)
                #return HttpResponse(json.dumps(d, cls=DjangoJSONEncoder), content_type='application/json')
            else:
                print(">>> no hay!")
                response_msg = {'details': 'El usuario no existe', 'status': status.HTTP_409_CONFLICT}
                print(response_msg)
                return HttpResponse(json.dumps(response_msg, cls=DjangoJSONEncoder), content_type='application/json')

        except Exception as inst:
            print(inst)
            print(">>> exception block")
            response_msg = {'details': 'User exception', 'status': status.HTTP_409_CONFLICT, "exception": inst}
            print(response_msg)
            return HttpResponse(json.dumps(response_msg, cls=DjangoJSONEncoder), content_type='application/json')


# Headquarters list by enterprise.
class EnterpriseHeadquarters(APIView):

    def get(self, request, *args, **Kwargs):
        enterprise_id = Kwargs["enterprise_id"]
        print(enterprise_id)
        if enterprise_id:
            enterprise = Enterprise.objects.get(pk=enterprise_id)
            location_list = Location.objects.filter(enterprise=enterprise_id)
            location_array = [{"id": location.pk, "name": location.name, "description": location.description} for
                          location in location_list]
            location = {"location": location_array}
            return Response(location)
        else:
            response_msg = [{'warning': 'This location does not exist %s' % enterprise_id}]
            return Response(response_msg)


#check,
class ClinicsList(APIView):
    serializer_class = EnterpriseSerializer

    def get(self, reques, format=None):
        enterprise = self.serializer_class(Enterprise.objects.all(), many=True)
        clinics = {"enterprise": enterprise.data}
        return Response(clinics)


# check
# select ap.* from emergency_attention ap
# INNER JOIN location_emergency_attention lea  on ap.id = lea.emergency_attention_id
# where lea.location_id = 1;
# select_related review
class EmergencyAttentionList(APIView):
    # get the location = id
    def get(self, request, *args, **kwargs):

        location_emergency_attention_list = LocationEmergencyAttention.objects.filter(location_id=self.kwargs['location_id'])
        print(location_emergency_attention_list.count())

        emergency_attention_id_list = [location_emergency_attention.emergency_attention_id
                                    for location_emergency_attention in location_emergency_attention_list]
        print(emergency_attention_id_list)

        emergency_attention_list = [ EmergencyAttention.objects.get(pk=emergency_attention_id)
                 for emergency_attention_id in emergency_attention_id_list ]
        print(emergency_attention_list)
        dict =[ {"id":emergency_attention.id,"name":emergency_attention.attention_type_id,
                 "description":emergency_attention.description,"picture_url":emergency_attention.picture_url}
                 for emergency_attention in emergency_attention_list]

        emergency_attention = {"emergency_attention": dict}

        return Response(emergency_attention)


# check
# Specialist Doctor by location
class SpecialistDoctor(APIView):

    def get(self, *args, **kwargs):
        type_of_specialist = "ESPEC"
        doctor_list = Doctor.objects.filter(location_id=self.kwargs['location_id']) \
             .filter(type_of_specialist=type_of_specialist) \
             .filter(emergency_attention_id__exact=self.kwargs['emergency_attention_id'])
        doctor = [{"id": doctor.pk, "doctor_name": doctor.doctor_name, "email": doctor.email, "midoc_user": doctor.midoc_user,
                       "picture_url": doctor.picture_url} for doctor in doctor_list]
        payload = {"specialist_doctor": doctor}
        return Response(payload)


# check
# emergency doctor by location
class EmergencyDoctor(APIView):
    serializer_class = DoctorLocalSerializer

    def get(self, request, *args, **kwargs):
        type_of_specialist = "EMERG"
        doctor_list = Doctor.objects.filter(location_id=self.kwargs['location_id']).\
            filter(type_of_specialist=type_of_specialist)
        doctor = [{"id": doctor.pk, "doctor_name": doctor.doctor_name,"picture_url": doctor.picture_url,
                   "cmd":doctor.cmd_peru} for doctor in doctor_list]
        clinics = {"emergency_doctor": doctor}
        return Response(clinics)


# check
# select mh.id as medical_history_id, p.name, p.year_of_birth, p.blood_type, p.allergic_reaction
# from medical_history mh inner join patient p on (mh.patient_id = p.id)
# where mh.emergencista_id = 5 and mh.location_id =1 and mh.doctor_id =2;
class MedicalHistoryList(APIView):
    serializer_class = MedicalHistorySerializer

    def get(self, request, *args, **kwargs):
        doctor_id = self.kwargs['doctor_id']
        location_id = self.kwargs['location_id']
        emergency_doctor_id = self.kwargs['emergency_doctor_id']
        print(doctor_id)
        print(location_id)
        print(emergency_doctor_id)

        medical_history_list = MedicalHistory.objects.filter(location_id=self.kwargs['location_id'])\
            .filter(doctor=doctor_id).filter(emergencista=emergency_doctor_id).order_by('created_date')
        print(medical_history_list)

        medical_history_dict = [{"patient_id":medical_history.patient.pk, "medical_history_id": medical_history.id,
                                 "age": calculate_age(medical_history.patient.year_of_birth), "fecha_ingreso": medical_history.created_date,
                                 "name": medical_history.patient.name} for medical_history in medical_history_list]
        dict = {"emergency_patient": medical_history_dict}
        return Response(dict)


# check
class MedicalHistoryListByEmergDoctor(APIView):
    serializer_class = MedicalHistorySerializer

    def get(self, request, *args, **kwargs):
        emergency_doctor_id = self.kwargs['emergency_doctor_id']
        location_id = self.kwargs['location_id']

        print(location_id)
        print(emergency_doctor_id)

        medical_history_list = MedicalHistory.objects.filter(location_id=self.kwargs['location_id']).filter(
        emergencista=emergency_doctor_id).order_by('created_date')
        print(medical_history_list)

        medical_history_dict = [{"patient_name": mh.patient.name, "doctor_name": mh.emergencista.doctor_name,
                                "attention_name": mh.doctor.emergency_attention.attention_name, "created_date": mh.created_date,
                                "picture_url":mh.patient.picture_url, "id":mh.pk,
                                 } for mh in medical_history_list]
        dict = {"emergency_history": medical_history_dict}
        return Response(dict)


# dev
class MedicalHistorySpecialistList(APIView):
    serializer_class = MedicalHistorySerializer

    def get(self, request, *args, **kwargs):
        doctor_id = self.kwargs['doctor_id']
        location_id = self.kwargs['location_id']
        #specialist_doctor_id = self.kwargs['specialist_doctor_id']
        print(doctor_id)
        print(location_id)
        #print(specialist_doctor_id)

        medical_history_list = MedicalHistory.objects.filter(location_id=self.kwargs['location_id']).\
            filter(doctor=doctor_id).order_by('created_date')
        print(medical_history_list)



        medical_history_dict = [{"patient_id": medical_history.patient.pk, "medical_history_id": medical_history.id,
                                     "age": calculate_age(medical_history.patient.year_of_birth),
                                     "fecha_ingreso": medical_history.created_date,
                                     "specialty_name": medical_history.doctor.emergency_attention.attention_name,
                                     "emergency_name": medical_history.emergencista.doctor_name,
                                     "name": medical_history.patient.name} for medical_history in medical_history_list]
        dict = {"emergency_patient": medical_history_dict}
        return Response(dict)



# check
class MedicalHistoryDetail(APIView):

    def get(self, request, *args, **kwargs):
        medical_history_id = self.kwargs['medical_history_id']
        mh = MedicalHistory.objects.get(pk=medical_history_id)

        patient = {"name": mh.patient.name, "edad": calculate_age(mh.patient.year_of_birth), "tipo_de_sangre":mh.patient.blood_type,
                   "alergias":mh.patient.allergic_reaction, "contact_phone": mh.patient.contact_phone, "created_date":mh.patient.created_date,
                   "gender": mh.patient.gender, "diagnostic": mh.diagnostic, "symptom": mh.symptom, "blood_type": mh.patient.blood_type,
                   "size": mh.patient.size, "email": mh.patient.email, "picture_url":mh.patient.picture_url, "dni": mh.patient.dni}

        emergencista = {"nombre_emergencista": mh.emergencista.doctor_name, "emergencista_sintoma":mh.symptom,
                        "doctor_foto":mh.emergencista.picture_url, "cmd": mh.emergencista.cmd_peru}

        doctor = {"especialista_name":mh.doctor.doctor_name, "doctor_foto": mh.doctor.picture_url,
                  "cmd": mh.doctor.cmd_peru, "especialista_comment": mh.doctor_comment}

        # get the picture medical history detail
        mhm_list = MedicalHistoryMedia.objects.filter(medical_history=medical_history_id)

        mhm2 = [{"picture_patient": mhm.picture_url} for mhm in mhm_list]

        # headers for medical history detail
        headers = {"picture_detail" : "Fotos", "emergencista" : "Médico de Área", "patient" : "Paciente", "doctor" : "Especialista"}

        medical_history_detail = [{"patient": patient, "emergencista":emergencista, "doctor":doctor, "picture_detail": mhm2, "headers": headers}]
        print(medical_history_detail)

        dict = {"medical_history_detail":medical_history_detail}

        return Response(dict)


# dev child json update/create
class MedicalHistoryUpdating(APIView):

    serializer_class = PatientUpdatingSerializer

    def post(self, request, format=None):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        #vd = serializer.validated_data


        return Response("hola")






"""
deprecated
"""
class PatientViewDeprecated(APIView):
    serializer_class = PatientSerializer

    def get(self, format=None):
        serializer = self.serializer_class(Patient.objects.all(), many=True)
        return Response(serializer.data)

    @transaction.atomic()
    def post(self, request, format=None):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        vd = serializer.validated_data
        print(vd.get("dni"))
        try:
            if not Patient.objects.filter(dni__exact=vd.get("dni")).exists():
                print("object to save: {}".format(vd))
                # save and get the recent id
                patient = serializer.save()
                print(patient.dni)
                # patient.pk get the recent id

                p = {"id": patient.pk, "name": patient.name, "email": patient.email,
                    "password": patient.password, "dni": patient.dni, "picture_url": patient.picture_url,
                    "enterprise_enabled": patient.is_enterprise_enabled, "blood_type": patient.blood_type,
                    "allergic_reaction": patient.allergic_reaction, "token_sinch":patient.token_sinch,
                    "nokia_weight": patient.nokia_weight, "nokia_body_temperature": patient.nokia_body_temperature,
                    "nokia_blood_pressure": patient.nokia_blood_pressure, "size": patient.size,
                    "is_enterprise_enabled": patient.is_enterprise_enabled
                    }


                print(p)
                #return HttpResponse(json.dumps(p, cls=DjangoJSONEncoder), content_type='application/json')
                return Response(p)


            else:
                print(">>> Usuario ya se encuentra registrado")
                response_msg = {'details': 'Este Usuario ya esta registrado', 'status': status.HTTP_409_CONFLICT}
                return HttpResponse(json.dumps(response_msg, cls=DjangoJSONEncoder), content_type='application/json')
        except:
            print(">>> create failure")
            responseMsg = [{'create': 'failure'}]
            return HttpResponse(json.dumps(responseMsg, cls=DjangoJSONEncoder), content_type='application/json')


# check
class PatientView(APIView):
    serializer_class = PatientSerializer

    def get(self, format=None):
        serializer = self.serializer_class(Patient.objects.all(), many=True)
        return Response(serializer.data)

    @transaction.atomic()
    def post(self, request, format=None):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        vd = serializer.validated_data
        print(vd.get("dni"))
        try:
            if Patient.objects.filter(dni__iexact=vd.get("dni")).exists():
                # recovery the patient
                patient = Patient.objects.get(dni__iexact=vd.get("dni"))

                p = {"id": patient.pk, "name": patient.name, "email": patient.email,
                     "password": patient.password, "dni": patient.dni, "picture_url": patient.picture_url,
                     "enterprise_enabled": patient.is_enterprise_enabled, "blood_type": patient.blood_type,
                     "allergic_reaction": patient.allergic_reaction, "token_sinch": patient.token_sinch,
                     "size": patient.size
                }

                return Response(p)
            else:
                response_msg = {'details': 'Este Paciente no se encuentra registrado', 'status': status.HTTP_404_NOT_FOUND}
                return HttpResponse(json.dumps(response_msg, cls=DjangoJSONEncoder), content_type='application/json')

        except Exception as inst:
            print(">>> create failure")
            print(inst)
            response_msg = [{'create': 'failure'}]
            return HttpResponse(json.dumps(response_msg, cls=DjangoJSONEncoder), content_type='application/json')


# check
class PatientRegisterView(APIView):
    serializer_class = PatientSerializer

    def get(self, format=None):
        serializer = self.serializer_class(Patient.objects.all(), many=True)
        return Response(serializer.data)

    #@transaction.atomic()
    def post(self, request, format=None):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        vd = serializer.validated_data
        print(vd.get("dni"))
        try:
            if not Patient.objects.filter(dni__exact=vd.get("dni")).exists():
                print("object to save: {}".format(vd))
                # save and get the recent id
                patient = serializer.save()
                print(patient.dni)
                # patient.pk get the recent id

                p = {"id": patient.pk, "name": patient.name, "email": patient.email,
                     "password": patient.password, "dni": patient.dni, "picture_url": patient.picture_url,
                     "enterprise_enabled": patient.is_enterprise_enabled, "blood_type": patient.blood_type,
                     "allergic_reaction": patient.allergic_reaction, "token_sinch": patient.token_sinch,
                     "size": patient.size, "is_enterprise_enabled": patient.is_enterprise_enabled
                     }
                print(p)
                # return HttpResponse(json.dumps(p, cls=DjangoJSONEncoder), content_type='application/json')
                return Response(p)

            else:
                print(">>> Usuario ya se encuentra registrado")
                response_msg = {'details': 'Este Usuario ya esta registrado', 'status': status.HTTP_409_CONFLICT}
                return HttpResponse(json.dumps(response_msg, cls=DjangoJSONEncoder), content_type='application/json')

        except Exception as inst:
            print(">>> create failure")
            print(inst)
            response_msg = [{'create': 'failure'}]
            return HttpResponse(json.dumps(response_msg, cls=DjangoJSONEncoder), content_type='application/json')


# ckeck
class PatientUpdateToken(APIView):

    """
    Retrieve, update a Patient instance.
    """
    def get_object(self, pk):
        try:
            return Patient.objects.get(pk=pk)
        except Patient.DoesNotExist:
            raise Http404

    def get(self, request, pk, format=None):
        patient = self.get_object(pk)
        serializer = PatientSerializer(patient)
        return Response(serializer.data)

    def put(self, request, pk, format=None):
        patient = self.get_object(pk)
        serializer = PatientSerializer(patient, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# check - TOKEN
class PatientByTokenList(APIView):

    #renderer_classes = (JSONRenderer,)

    def get(request, *args, **kwargs):
        token_sinch = kwargs['token_sinch']
        print(token_sinch)

        is_token_sinch = Patient.objects.filter(token_sinch__exact=token_sinch).exists()
        print(is_token_sinch)
        if is_token_sinch:
            patient_list = Patient.objects.filter(token_sinch__exact=token_sinch)
            print(patient_list)

            patient_dict =[ {"id": patient.pk, "name": patient.name, "age": calculate_age(patient.year_of_birth), "email": patient.email,
                     "password": patient.password, "dni": patient.dni, "picture_url": patient.picture_url,
                     "blood_type": patient.blood_type, "allergic_reaction": patient.allergic_reaction,
                     "token_sinch":patient.token_sinch, "size": patient.size, "gender": patient.gender,
                     "contact_phone": patient.contact_phone, "is_enterprise_enabled": patient.is_enterprise_enabled,
                     "enterprise_name": patient.location.enterprise.business_name
                     } for patient in patient_list
            ]

            return Response(patient_dict)
        else:
            response_msg = [{'warning': 'This token not exist:%s' % token_sinch}]
            return Response(response_msg)


# developer status
class DoctorUpdateLocationView(APIView):

    def put(self, request, *args, **kwargs):
        data = request.data
        #print(data)
        location_id2 = kwargs['location_id']
        print(location_id2)
        doctor_id = kwargs['doctor_id']
        print(doctor_id)
        try:
            doctor = Doctor.objects.filter(pk=doctor_id).update(location_id=location_id2)
            print(doctor)
            d = Doctor.objects.get(pk=doctor_id)
            new_location = d.location_id

            if doctor == 1:
                response_msg = {'id': new_location, 'details': "La sede del doctor fue actualizada",
                                 "status": status.HTTP_200_OK}
                return Response(response_msg)

            else:
                response_msg = {'details': "La sede del doctor NO fue actualizada", "status": status.HTTP_403_FORBIDDEN}
                return Response(response_msg)

        except Exception as inst:
            print(inst)
            response_msg = {'details': "El doctor no existe!", "status": status.HTTP_404_NOT_FOUND}
            return Response(response_msg)


# developer status
class MedicalHistoryUpdate(APIView):

    """
    Retrieve, update a Medical History instance.
    """
    def get_object(self, pk):
        try:
            return MedicalHistory.objects.get(pk=pk)
        except MedicalHistory.DoesNotExist:
            raise Http404

    def get(self, request, pk, format=None):
        medical_history = self.get_object(pk)
        serializer = MedicalHistorySerializer(medical_history)
        return Response(serializer.data)

    def put(self, request, pk, format=None):
        medical_history = self.get_object(pk)
        serializer = MedicalHistorySerializer(medical_history, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# check
class PatientVerifyView(APIView):
    serializer_class = PatientVerifySerializer

    def post(self, request, format=None):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        vd = serializer.validated_data
        print(vd.get("dni"))
        print(vd.get("enterprise_id"))

        try:
            patient = Patient.objects.get(dni__exact=vd.get("dni"))
        except Patient.DoesNotExist:
            patient = None

        if patient is None:
            response_msg = {'details': "El Paciente no se encuentra registrado", "status": status.HTTP_403_FORBIDDEN}
            return Response(response_msg)

        try:
            enterprise = Enterprise.objects.get(pk=vd.get("enterprise_id"))
        except Enterprise.DoesNotExist:
            enterprise = None

        if enterprise is None:
            response_msg = {'details': "La empresa que requieres aun no ha sido registrada", "status": status.HTTP_403_FORBIDDEN}
            return Response(response_msg)

        else:
            #location = Location.objects.get(pk=patient.location.pk)
            #print(location.enterprise_id)
            print(enterprise.business_name)

            dict = {"patient_id": patient.pk, "dni": patient.dni, "name": patient.name, "midoc_user": patient.midoc_user,
                    "business_name": enterprise.business_name, "picture_url": patient.picture_url,
                    "picture_url_enterprise": enterprise.picture_url_enterprise}

            return Response(dict)

# check
class PatientAppointments(APIView):

    def get(request, *args, **kwargs):
        patient_id = kwargs['patient_id']

        appointments = Appointment.objects.filter(patient_id=patient_id)

        appointment_dict = [ {"appointment_id": appointment.pk, "doctor_name": appointment.doctor.doctor_name,
                              "appointment_time": appointment.appointment_time, "specialty:":appointment.doctor.
                emergency_attention.attention_name, "appointment_status":
            appointment.appointment_status} for appointment in appointments]

        dict = {"appoitment_patient": appointment_dict}


        return Response(dict)


# dev status
class PatientHistoryView(APIView):

    def get(request, *args, **kwargs):
        patient_id = kwargs['patient_id']

        medicalhistorys = MedicalHistory.objects.filter(patient_id=patient_id)

        medical = [{"age": calculate_age(medicalhistory.patient.year_of_birth),
                     "patient_id": medicalhistory.patient.pk, "fecha_ingreso": medicalhistory.patient.created_date ,
                     "name": medicalhistory.doctor.doctor_name, "medical_history_id": medicalhistory.pk,
                     "specialty_name": medicalhistory.doctor.emergency_attention.attention_name}
                    for medicalhistory in medicalhistorys]

        dict = {"patient_history": medical}

        return Response(dict)


# dev artifact
class ArtifactMeasurementView(APIView):
    serializer_class = ArtifactMeasurementSerializer

    def get(request, *args, **kwargs):
        token_sinch = kwargs['token_sinch']

        print(token_sinch)

        try:
            artifact_measurement = ArtifactMeasurement.objects.get(token__exact=token_sinch)
        except ArtifactMeasurement.DoesNotExist:
            artifact_measurement = None

        if artifact_measurement is None:
            response_msg = {'details': "El token: "+token_sinch+" ,no existe!",
                            "status": status.HTTP_404_NOT_FOUND}
            return Response(response_msg)

        else:
            measurement = {"token": artifact_measurement.token, "weight": artifact_measurement.weight,
                           "body_temperature": artifact_measurement.body_temperature,
                           "blood_pressure": artifact_measurement.blood_pressure,
                           "picture_url": artifact_measurement.picture_url
                           }
            print(measurement)
            return Response(measurement)

# dev
class ArtifactMeasurementTool(APIView):
    serializer_class = ArtifactMeasurementSerializer

    def post(self, request, format=None):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        vd = serializer.validated_data
        print(vd)
        print(vd.get("token"))
        print(vd.get("weight"))
        print(vd.get("body_temperature"))
        print(vd.get("blood_pressure"))
        weight = vd.get("weight")
        body_temperature = vd.get("body_temperature")
        blood_pressure = vd.get("blood_pressure")

        try:
            artifact_measurement = ArtifactMeasurement.objects.get(token__exact=vd.get("token"))
        except ArtifactMeasurement.DoesNotExist:
            artifact_measurement = None

        if artifact_measurement is None:
            for key in vd:
                if key == 'weight':
                    artifact = ArtifactMeasurement(token=vd.get("token"), weight=vd.get("weight"))
                    artifact.save()
                    response_msg = {'details': "El token: "+vd.get("token")+" y el peso de: "+vd.get("weight")+"" ,
                                    "status": status.HTTP_200_OK}
                    return Response(response_msg)

                elif key == 'body_temperature':
                    artifact = ArtifactMeasurement(token=vd.get("token"), body_temperature=vd.get("body_temperature"))
                    artifact.save()
                    response_msg = {'details': "El token: " + vd.get("token") + " y el peso de: " + vd.get("body_temperature") + "",
                                    "status": status.HTTP_200_OK}
                    return Response(response_msg)

                elif key == 'blood_pressure':
                    artifact = ArtifactMeasurement(token=vd.get("token"), blood_pressure=vd.get("blood_pressure"))
                    artifact.save()
                    response_msg = {'details': "El token: " + vd.get("token") + " y el peso de: " + vd.get("body_temperature") + "",
                                    "status": status.HTTP_200_OK}
                    return Response(response_msg)

        else:
            for key in vd:
                if key == 'weight':
                    artifact_measurement.weight = vd.get("weight")
                    artifact_measurement.save()
                    response_msg = {'details': "El peso de " + weight + " fue ingresado",
                                    "status": status.HTTP_200_OK}
                    return Response(response_msg)

                elif key == 'body_temperature':
                    artifact_measurement.body_temperature = vd.get("body_temperature")
                    artifact_measurement.save()
                    response_msg = {'details': "El peso de " + vd.get("body_temperature") + " fue ingresado",
                                "status": status.HTTP_200_OK}
                    return Response(response_msg)

                elif key == 'blood_pressure':
                    artifact_measurement.blood_pressure = vd.get("blood_pressure")
                    artifact_measurement.save()
                    response_msg = {'details': "El peso de " + vd.get("blood_pressure") + " fue ingresado",
                                    "status": status.HTTP_200_OK}
                    return Response(response_msg)

            return Response("this measure can not be finalize")


# check
class MeasurementWeight(APIView):
    serializer_class = ArtifactMeasurementSerializer

    def post(self, request, format=None):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        vd = serializer.validated_data
        print(vd)
        print(vd.get("token"))
        print(vd.get("weight"))

        try:
            artifact_measurement = ArtifactMeasurement.objects.get(token__exact=vd.get("token"))
        except ArtifactMeasurement.DoesNotExist:
            artifact_measurement = None

        if artifact_measurement is None:
            artifact = ArtifactMeasurement(token=vd.get("token"), weight=vd.get("weight"))
            artifact.save()
            response_msg = {'details': "El token: "+vd.get("token")+" y el peso de: "+vd.get("weight")+"" ,
                            "status": status.HTTP_200_OK}
            return Response(response_msg)

        else:
            artifact_measurement.weight = vd.get("weight")
            artifact_measurement.save()
            response_msg = {'details': "El peso de "+vd.get("weight")+" fue ingresado",
                            "status": status.HTTP_200_OK}
            return Response(response_msg)



class MeasurementBodyTemperature(APIView):
    serializer_class = ArtifactMeasurementSerializer

    def post(self, request, format=None):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        vd = serializer.validated_data
        print(vd)
        print(vd.get("token"))
        print(vd.get("body_temperature"))

        try:
            artifact_measurement = ArtifactMeasurement.objects.get(token__exact=vd.get("token"))
        except ArtifactMeasurement.DoesNotExist:
            artifact_measurement = None

        if artifact_measurement is None:
            artifact = ArtifactMeasurement(token=vd.get("token"), body_temperature=vd.get("body_temperature"))
            artifact.save()
            response_msg = {'details': "El token: "+vd.get("token")+" y la temperatura de: "+vd.get("body_temperature")+"",
                            "status": status.HTTP_200_OK}
            return Response(response_msg)

        else:
            artifact_measurement.body_temperature = vd.get("body_temperature")
            artifact_measurement.save()
            response_msg = {'details': "La temperatura  "+vd.get("body_temperature")+" fue ingresado",
                            "status": status.HTTP_200_OK}
            return Response(response_msg)




# check
class BloodPressure(APIView):
    serializer_class = ArtifactMeasurementSerializer

    def post(self, request, format=None):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        vd = serializer.validated_data
        print(vd)
        print(vd.get("token"))
        print(vd.get("blood_pressure"))

        try:
            artifact_measurement = ArtifactMeasurement.objects.get(token__exact=vd.get("token"))
        except ArtifactMeasurement.DoesNotExist:
            artifact_measurement = None

        if artifact_measurement is None:
            artifact = ArtifactMeasurement(token=vd.get("token"), blood_pressure=vd.get("blood_pressure"))
            artifact.save()
            response_msg = {'details': "El token: "+vd.get("token")+" y la temperatura de: "+vd.get("blood_pressure")+"",
                            "status": status.HTTP_200_OK}
            return Response(response_msg)

        else:
            artifact_measurement.blood_pressure = vd.get("blood_pressure")
            artifact_measurement.save()
            response_msg = {'details': "La frecuencia cardiaca  "+vd.get("blood_pressure")+" fue ingresado",
                            "status": status.HTTP_200_OK}
            return Response(response_msg)


# check
class PatientUpdate(APIView):

    """
    Retrieve, update a Patient.
    """
    def get_object(self, pk):
        try:
            return Patient.objects.get(pk=pk)
        except Patient.DoesNotExist:
            raise Http404

    def get(self, request, pk, format=None):
        patient = self.get_object(pk)
        serializer = PatientSerializer(patient)
        return Response(serializer.data)

    def put(self, request, pk, format=None):
        patient = self.get_object(pk)
        serializer = PatientSerializer(patient, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# check
class CallDoctorView(APIView):

    def get(self, request, *args, **kwargs):
        midoc_user = self.kwargs['midoc_user']
        print(midoc_user)

        try:
            doctor = Doctor.objects.get(midoc_user__exact=midoc_user)
        except Doctor.DoesNotExist:
            doctor = None

        if doctor is None:
            response_msg = {
                'details': "The doctor " + midoc_user + " is not registered ",
                "status": status.HTTP_404_NOT_FOUND}
            return Response(response_msg)

        else:
            dict = {"doctor_name": doctor.doctor_name, "specialty":doctor.emergency_attention.attention_name,
                    "picture_url": doctor.picture_url}

        return Response(dict)

# dev
class CallActivate(APIView):
    # test patch, post
    def get(self, request, *args, **kwargs):
        doctor_id = kwargs["doctor_id"]
        activate = kwargs["activate"]
        activate_bool=validate_one_character(activate)

        if activate_bool is True:
            try:
                doctor = Doctor.objects.get(pk=doctor_id)
            except Doctor.DoesNotExist:
                doctor = None

            if doctor is None:
                response_msg = {
                    'details': "Doctor Id: " + doctor_id + " is not register",
                    #"status": status.HTTP_404_NOT_FOUND}
                    "status": activate}
                return Response(response_msg)
            else:
                doctor.call_activate = activate
                doctor.save()
                response_msg = {
                    'medical_history_registerdetails': "The Doctor Status was updated",
                    #"status": status.HTTP_200_OK}
                    "status": activate}
                return Response(response_msg)
        else:
            response_msg = {
                'details': "value too long for type status character or must be '0' or '1'",
                # "status": status.HTTP_200_OK}
                "status": status.HTTP_403_FORBIDDEN}
            return Response(response_msg)


# dev
# class MedicalHistoryRegister(APIView):
#     serializer_class = PatientHistorySerializer
#
#     def get(self, request, format=None):
#         serializer = self.serializer_class(Patient.objects.all(), many=True)
#         return Response(serializer.data)


