from rest_framework import serializers
from .models import (Patient,
                     Doctor,
                     Enterprise,
                     MedicalHistory,
                     ArtifactMeasurement,
                     )



class DoctorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Doctor
        fields = '__all__'


class EnterpriseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Enterprise
        fields = '__all__'


class DoctorLocalSerializer(serializers.ModelSerializer):
    class Meta:
        model = Doctor
        fields = ('id', 'doctor_name', 'picture_url')


class MedicalHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = MedicalHistory
        fields = '__all__'
        #depth = 1


class PatientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Patient
        fields = '__all__'


# without model
class PatientVerifySerializer(serializers.Serializer):
    dni = serializers.CharField(max_length=8)
    enterprise_id = serializers.IntegerField()


# artifact
class ArtifactMeasurementSerializer(serializers.ModelSerializer):
    class Meta:
        model = ArtifactMeasurement
        fields = '__all__'



# --
class MedicalHistoryUpdatingSerializer(serializers.ModelSerializer):

    class Meta:
        model = MedicalHistory
        fields = ('medical_history_text', 'symptom', 'doctor_comment', 'diagnostic', 'weight', 'body_temperature',
                  'blood_pressure', 'heart_rate')


class PatientUpdatingSerializer(serializers.ModelSerializer):
    patients_medical_histories = MedicalHistoryUpdatingSerializer(many=True)

    class Meta:
        model = Patient
        fields = ('name', 'email', 'dni', 'blood_type', 'allergic_reaction','size','contact_phone','gender',
                  'patients_medical_histories')

    def create(self, validated_data):
        patients_medical_histories = validated_data.pop('patients_medical_histories')
        patient = Patient.objects.create(**validated_data)
        for medical_history in patients_medical_histories:
            MedicalHistory.objects.create(patient=patient, **medical_history)
        return patient



# start - create json nested serializer

# class MedicalHistoryUpdatingSerializer(serializers.ModelSerializer):
#
#     class Meta:
#         model = MedicalHistory
#         fields = ('medical_history_text', 'symptom', 'doctor_comment', 'diagnostic', 'weight', 'body_temperature',
#                   'blood_pressure', 'heart_rate')
#
#
# class PatientUpdatingSerializer(serializers.ModelSerializer):
#     patients_medical_histories = MedicalHistoryUpdatingSerializer(many=True)
#
#     class Meta:
#         model = Patient
#         fields = ('name', 'email', 'dni', 'blood_type', 'allergic_reaction','size','contact_phone','gender',
#                   'patients_medical_histories')
#
#     def create(self, validated_data):
#         patients_medical_histories = validated_data.pop('patients_medical_histories')
#         patient = Patient.objects.create(**validated_data)
#         for medical_history in patients_medical_histories:
#             MedicalHistory.objects.create(patient=patient, **medical_history)
#         return patient

# end - create json nested serializer
#
#
# {
#     "name": "Carlos Oliveira",
#     "email": "cdoliveirar@gmail.com",
#     "dni": "cdoliveirar@gmail.com",
#     "blood_type": "A-",
#     "allergic_reaction": "No Alergias",
#     "size": "1.78",
#     "contact_phone": "931118101",
#     "gender": "M",
#
#     "patients_medical_histories": [{
#         "medical_history_text": "",
#        	"symptom": "fiebre intensa",
#         "doctor_comment": "aplicar medicina",
#         "diagnostic": "recuperacion",
#         "weight": "89",
#         "body_temperature": "37.2",
#         "blood_pressure": "40/100",
#         "heart_rate": "56"
#         }
#     ]
# }

# --




