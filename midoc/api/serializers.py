from rest_framework import serializers
from .models import (Patient,
                     Doctor,
                     Enterprise,
                     MedicalHistory,
                     ArtifactMeasurement,
                     Competition
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


class CompetitionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Competition
        fields = '__all__'
        #fields = ('id', 'patient', 'doctor', 'qualification', 'qualification_feedback', 'recommendation',
        #              'recommendation_feedback')




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



class MedicalHistorySerializer2(serializers.ModelSerializer):
    class Meta:
        model = MedicalHistory
        fields = ('id','symptom','doctor_comment','diagnostic')



class PatientSerializer2(serializers.ModelSerializer):
    medical_history = MedicalHistorySerializer2(many=True)

    class Meta:
        model = Patient
        fields = ('id','name','year_of_birth','email','midoc_user','password','dni','picture_url','blood_type',
                  'allergic_reaction', 'token_sinch', 'size', 'contact_phone', 'gender', 'created_date')

    def create(self, validated_data):
        patients_medical_histories = validated_data.pop('patients_medical_histories')
        patient = Patient.objects.create(**validated_data)
        for medical_history in patients_medical_histories:
            MedicalHistory.objects.create(patient=patient, **medical_history)
        return patient


    def update(self, instance, validated_data):
        medical_histories_data = validated_data.pop('patients_medical_histories')
        medical_histories = (instance.patients_medical_histories).all()
        medical_histories = list(medical_histories)
        validated_data.get()






    def update(self, instance, validated_data):
        albums_data = validated_data.pop('album_musician')
        albums = (instance.album_musician).all()
        albums = list(albums)
        instance.first_name = validated_data.get('first_name', instance.first_name)
        instance.last_name = validated_data.get('last_name', instance.last_name)
        instance.instrument = validated_data.get('instrument', instance.instrument)
        instance.save()

        for album_data in albums_data:
            album = albums.pop(0)
            album.name = album_data.get('name', album.name)
            album.release_date = album_data.get('release_date', album.release_date)
            album.num_stars = album_data.get('num_stars', album.num_stars)
            album.save()
        return instance



