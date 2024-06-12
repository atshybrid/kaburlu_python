from rest_framework import serializers
from .models import *
from django.core.validators import FileExtensionValidator 


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id','category_name','content_language','parent']

class CategoryResponseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = '__all__'

    def to_representation(self, instance):
        response = super().to_representation(instance)
        response['content_language'] = instance.content_language.content_language if instance.content_language else None
        return response

class PostArticleSerializer(serializers.ModelSerializer):
    class Meta:
        model = PostArticle
        fields = field_names = ['id','staff', 'user', 'news_language', 'title1', 'title1_color_code', 'title2', 'title2_color_code', 'title3', 'title3_color_code', 'short_news', 'long_news', 'category', 'news_type', 'breaking_news', 'tags', 'meta_keyword', 'meta_description', 'template_id', 'SezReporter_Id', 'updated_staff_id']


class PostArticleResponseSerializer(serializers.ModelSerializer):
    class Meta:
        model = PostArticle
        fields = '__all__'

    def to_representation(self, instance):
        response = super().to_representation(instance)
        response['news_language'] = instance.news_language.content_language if instance.news_language else None
        response['news_type'] = instance.news_type.type_name if instance.news_type else None
        response['tags'] = [tag.hashtag for tag in instance.tags.all()]
        return response


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ['id', 'hashtag']

class NewsPaperSerializer(serializers.ModelSerializer):
    class Meta:
        model = NewsPaper
        fields = '__all__'

    def to_representation(self, instance):
        response = super().to_representation(instance)
        response['paper_language'] = instance.paper_language.content_language if instance.paper_language else None
        return response


class NewsPaperLoginSerializer(serializers.Serializer):
    email = serializers.CharField()

class StaffSerializer(serializers.ModelSerializer):
    class Meta:
        model = Staff
        fields = ['id','newspaper', 'name', 'email', 'contact_no', 'dob', 'father_name', 'staff_type', 'reporter_type', 'parent_reporter_id', 'pin_code', 'state','work_dist', 'work_const', 'division', 'work_mandal', 'news_auto_publish', 'child_articles_update_publish_status','address', 'last_working_details', 'work_area', 'acknowledgement_id','subscription_enabled','subscription_amount']

class StaffResponseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Staff
        fields = '__all__'

class StaffKycSerializer(serializers.Serializer):
    aadhar_number = serializers.CharField(max_length=128, write_only=True)

class KycOtpSerializer(serializers.Serializer):
    client_id = serializers.CharField(max_length=128, write_only=True)
    aadhar_otp = serializers.IntegerField()

class EmployeIDSerializer(serializers.ModelSerializer):
    class Meta:
        model = EmployeeIdSetting
        fields = ['id',"newspaper","Idcard_templateid","primary_color_code","emplyeeid_prefix","secondary_color_code","terms_conditions",'card_validity']

class EmployeIDResponseSerializer(serializers.ModelSerializer):
    class Meta:
        model = EmployeeIdSetting
        fields = '__all__'

class StaffLoginSerializer(serializers.Serializer):
    email = serializers.CharField()

class ApproveNewsSerializer(serializers.Serializer):
    publish_status = serializers.BooleanField()

class SubscriptionPlanSerializer(serializers.ModelSerializer):

    class Meta:
        model = SubscriptionPlan
        fields = '__all__'


class CreateENewsPaperSerializer(serializers.ModelSerializer):
    class Meta:
        model = ENewsPaper
        fields = ['id','newspaper','edition','date']

class ENewsPaperResponseSerializer(serializers.ModelSerializer):
    class Meta:
        model = ENewsPaper
        fields = '__all__'


class ArticleFeedbackSerializer(serializers.ModelSerializer):

    class Meta:
        model = ArticleFeedback
        fields = '__all__'


class UploadDocumentsSerializer(serializers.ModelSerializer):

    class Meta:
        model = UploadDocument
        fields = ['id','employee','document_type','document_name']

class UploadDocumentsResponseSerializer(serializers.ModelSerializer):

    class Meta:
        model = UploadDocument
        fields = '__all__'

class AddressSerializer(serializers.Serializer):
    address_file = serializers.FileField(validators=[FileExtensionValidator( ['csv'] ) ])


class NewsPaperSettingSerializer(serializers.ModelSerializer):
    class Meta:
        model = NewsPaperSetting
        fields = ['id','sitetitle','short_description','long_description','slogan','city','state','postal_code','footer_text','notification','newspaper_sitetheme','notice_message','about_us','newspaper_domain','epaper_enable','epaper_domain','epaperdiscription','epaper_sitetheme','social_media_links']

class NewsPaperSettingResponseSerializer(serializers.ModelSerializer):
    class Meta:
        model = NewsPaperSetting
        fields = "__all__"

class DomainListSerializer(serializers.ModelSerializer):
    class Meta:
        model = NewsPaperSetting
        fields = ['newspaper_domain']

class CroppedENewsPaperSettingSerializer(serializers.ModelSerializer):
    class Meta:
        model = CroppedENewsPaper
        fields = ["enewspaper"]

class CroppedENewsPaperResponseSettingSerializer(serializers.ModelSerializer):
    class Meta:
        model = CroppedENewsPaper
        fields = "__all__"

class ArticleViewsCountSerializer(serializers.ModelSerializer):
    class Meta:
        model = ArticleViewCount
        fields = "__all__"

class ENewsPaperFeedbackSerializer(serializers.ModelSerializer):
    class Meta:
        model = ENewsPaperFeedback
        fields = "__all__"

class CreateEditionSerializer(serializers.ModelSerializer):
    class Meta:
        model = EditionCategory
        fields = "__all__"

class CategoryAllocationSerializer(serializers.ModelSerializer):
    class Meta:
        model = CategoryAllocation
        fields = "__all__"

class EditionAllocationSerializer(serializers.ModelSerializer):
    class Meta:
        model = EditionAllocation
        fields = "__all__"

class LanguageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Language
        fields = '__all__'

class SubscriptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Subscription
        fields = '__all__'

class SubscriptionAuthSerializer(serializers.Serializer):
    flow_type = serializers.CharField()
    vpa = serializers.CharField()

















