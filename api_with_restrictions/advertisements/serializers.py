from django.contrib.auth.models import User
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from advertisements.models import Advertisement


class UserSerializer(serializers.ModelSerializer):
    """Serializer для пользователя."""

    class Meta:
        model = User
        fields = ('id', 'username', 'first_name',
                  'last_name',)


class AdvertisementSerializer(serializers.ModelSerializer):
    """Serializer для объявления."""

    creator = UserSerializer(
        read_only=True,
    )

    class Meta:
        model = Advertisement
        fields = ('id', 'title', 'description', 'creator',
                  'status', 'created_at',)
        read_only_fields = ['creator', ]

    def create(self, validated_data):
        validated_data['creator'] = self.context['request'].user
        return super().create(validated_data)

    def update(self, instance, validated_data):
        instance.title = validated_data.get('title', instance.title)
        instance.description = validated_data.get('description', instance.description)
        instance.status = validated_data.get('status', instance.status)
        instance.save()
        return instance

    def validate(self, data):
        user = self.context['request'].user
        adv_num = Advertisement.objects.filter(creator=user, status='OPEN').count()
        print(adv_num)
        if self.context['request'].method == 'POST':
            if adv_num + 1 > 10:
                raise ValidationError('Не больше 10 открытых объявлений')
        if self.context['request'].method in 'PATCH' and data['status'] == 'OPEN':
            if adv_num + 1 > 10:
                raise ValidationError('Не больше 10 открытых объявлений')
        return data
