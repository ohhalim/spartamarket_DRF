from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password

User = get_user_model()

<<<<<<< HEAD

#accounts/serializers.py

class UserProfileSerializer(serializers.ModelSerializer):
    profile_image = serializers.SerializerMethodField()  # 커스텀 필드로 처리
    
    class FollowSerializer(serializers.ModelSerializer):
        class Meta:
            model = User
            fields = ['id', 'email', 'username', 'profile_image']  # 반환할 필드    

=======
# 기본 Follow 정보를 위한 Serializer
class FollowSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'email', 'username', 'profile_image']

# 프로필 정보를 위한 Serializer
class UserProfileSerializer(serializers.ModelSerializer):
>>>>>>> accounts
    followers = FollowSerializer(many=True, read_only=True)
    followings = FollowSerializer(many=True, read_only=True)
    follower_count = serializers.IntegerField(source='followers.count', read_only=True)
    following_count = serializers.IntegerField(source='followings.count', read_only=True)
<<<<<<< HEAD
    profile_image = serializers.SerializerMethodField()  # 커스텀 필드로 처리
    
    class Meta:
        model = User
        fields = ['email', 'username', 'profile_image', 'followings', 'followers', 'follower_count', 'following_count']  # 반환할 필드
        
    def get_profile_image(self, obj):
        request = self.context.get('request')  # Serializer context에서 request 가져오기
=======
    profile_image = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ['email', 'username', 'name', 'birth_date', 'gender', 'bio',
                 'profile_image', 'followings', 'followers', 
                 'follower_count', 'following_count']

    def get_profile_image(self, obj):
        request = self.context.get('request')
>>>>>>> accounts
        if obj.profile_image:
            return request.build_absolute_uri(obj.profile_image.url)
        return None

<<<<<<< HEAD
class UserUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('username', 'profile_image')  # 수정 가능한 필드from rest_framework import serializers

class SignupSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True, validators=[validate_password])
=======
# 회원가입을 위한 Serializer
class SignupSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True, 
                                   validators=[validate_password])
>>>>>>> accounts
    password2 = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = User
<<<<<<< HEAD
        fields = ['email', 'password', 'password2', 'username', 'profile_image']

=======
        fields = ('email', 'username', 'name', 'birth_date', 'password', 
                 'password2', 'gender', 'bio', 'profile_image')
        extra_kwargs = {
            'name': {'required': True},
            'birth_date': {'required': True},
            'gender': {'required': False},
            'bio': {'required': False},
        }
>>>>>>> accounts

    def validate(self, data):
        if data['password'] != data['password2']:
            raise serializers.ValidationError({'password': '비밀번호가 일치하지 않습니다.'})
        return data
<<<<<<< HEAD
    
    def create(self, validated_data):
        validated_data.pop('password2')
        return User.objects.create_user(**validated_data) 
    


    
    class FollowSerializer(serializers.ModelSerializer):
        class Meta:
            model = User
            fields = ("id", "email", "username", "profile_image")

    
    class Meta:
        model = User
        fields = ['email', 'username', 'profile_image', 'followings', 'followers', 'follower_count', 'following_count']  # 반환할 필드
        
    def get_profile_image(self, obj):
        request = self.context.get('request')  # Serializer context에서 request 가져오기
        if obj.profile_image:
            return request.build_absolute_uri(obj.profile_image.url)
        return None
=======

    def create(self, validated_data):
        validated_data.pop('password2')
        return User.objects.create_user(**validated_data)

# 사용자 정보 업데이트를 위한 Serializer
class UserUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('username', 'name', 'birth_date', 'gender', 'bio', 'profile_image')
>>>>>>> accounts
