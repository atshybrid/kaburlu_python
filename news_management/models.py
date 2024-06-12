from django.db import models
from accounts.models import *
from django.core.validators import FileExtensionValidator 
from django.utils import timezone
from django.utils.timezone import now
from datetime import timedelta

class State(models.Model):
    STATE_CHOICES = [
        ('Karnatak', 'Karnatak'),
        ('Andhra', 'Andhra'),
    ]
    name = models.CharField(max_length=100, choices=STATE_CHOICES, default='Karnatak')

    def __str__(self):
        return self.name

class Language(models.Model):
    content_language = models.CharField(max_length=100)

    def __str__(self):
        return self.content_language

class NewsPaper(models.Model):
    company = models.ForeignKey(Company,on_delete=models.CASCADE,null=True,blank=True)
    paper_name = models.CharField(max_length=255)
    paper_language = models.ForeignKey(Language,on_delete=models.CASCADE,null=True,blank=True)
    rni_registered = models.BooleanField(blank=True, null=True)
    rni_number = models.CharField(max_length=20, blank=True, null=True)
    publisher_name = models.CharField(max_length=255)
    publisher_contact = models.CharField(max_length=15)
    chief_editor_name = models.CharField(max_length=255)
    contact_number = models.CharField(max_length=15)
    email = models.CharField(max_length=100,unique=True)
    paper_circulation_states = models.ManyToManyField(State,blank=True)
    address = models.JSONField()

class NewsPaperSetting(models.Model):
    newspaper = models.OneToOneField(NewsPaper, on_delete=models.CASCADE, related_name='settings')
    sitetitle = models.CharField(max_length=250,null=True, blank=True)
    favicon_logo = models.URLField(max_length=250, null=True, blank=True)
    sitelogo = models.URLField(max_length=250, null=True, blank=True)
    dashboard_logo = models.URLField(max_length=250, null=True, blank=True)
    short_description = models.CharField(max_length=250,null=True, blank=True)
    long_description = models.TextField(max_length=250,null=True, blank=True)
    slogan = models.CharField(max_length=250,null=True, blank=True)
    city = models.CharField(max_length=100,null=True, blank=True)
    state = models.CharField(max_length=100,null=True, blank=True)
    postal_code = models.CharField(max_length=10,null=True, blank=True)  # Adjusted to CharField
    footer_text = models.CharField(max_length=250,null=True, blank=True)
    newspaper_sitetheme = models.JSONField(blank=True, null=True)
    notification = models.BooleanField(default=False)
    notice_message = models.TextField(null=True, blank=True)
    about_us = models.TextField(null=True, blank=True)
    social_media_links = models.JSONField(null=True, blank=True)
    newspaper_domain = models.CharField(max_length=200,blank=True, null=True)
    epaper_enable = models.BooleanField(default=False)
    epaper_domain = models.CharField(max_length=200,blank=True, null=True)
    epaperdiscription = models.TextField(blank=True, null=True)
    epaper_sitetheme = models.JSONField(blank=True, null=True)


staff_type = [
        ('editor', 'Editor'),
        ('reporter', 'Reporter'),
    ]

reporter_type = [
        ('bureau_incharge', 'Bureau Incharge'),
        ('staff_reporter', 'Staff Reporter'),
        ('rc_incharge', 'RC Incharge'),
        ('reporter', 'Reporter'),
    ]

class Staff(models.Model):
    newspaper = models.ForeignKey(NewsPaper,on_delete=models.CASCADE,null=True,blank=True)
    name = models.CharField(max_length=100)
    email = models.CharField(max_length=100,unique=True,null=True,blank=True)
    contact_no = models.CharField(max_length=15,unique=True)
    dob = models.CharField(max_length=20,null=True,blank=True)
    father_name = models.CharField(max_length=100,null=True,blank=True)
    staff_type = models.CharField(max_length=10, choices=staff_type)
    reporter_type = models.CharField(max_length=20, choices=reporter_type)
    parent_reporter_id = models.ForeignKey('self', on_delete=models.SET_NULL, blank=True, null=True, related_name='children')
    pin_code = models.IntegerField()
    state = models.CharField(max_length=50,null=True,blank=True)
    work_dist = models.CharField(max_length=50,null=True,blank=True)
    work_const = models.CharField(max_length=50,null=True,blank=True)
    division = models.CharField(max_length=50,null=True,blank=True)
    work_mandal = models.CharField(max_length=50,null=True,blank=True)
    news_auto_publish = models.BooleanField(default=False)
    child_articles_update_publish_status = models.BooleanField(default=False)
    address = models.JSONField()
    employee_photo = models.URLField(max_length=250, blank=True, null=True)
    last_working_details = models.JSONField(blank=True, null=True)
    work_area = models.CharField(max_length=200)
    acknowledgement_id = models.BooleanField(default=False)
    acknowledgement_image = models.URLField(max_length=250,null=True,blank=True)
    staff_kyc = models.BooleanField(default=False)
    subscription_enabled = models.BooleanField(default=False)
    subscription_amount = models.IntegerField(null=True,blank=True)
    Id_card_charage_amount = models.IntegerField(null=True,blank=True)
    # subscription_id = models.CharField(max_length = 100,null=True,blank=True)
    # subscription_status = models.CharField(max_length=100,default='Inactive')
    # merchant_user_id = models.CharField(max_length = 100,null=True,blank=True)
    # merchant_subscription_id = models.CharField(max_length = 100,null=True,blank=True)

    def __str__(self):
        return self.name


class Subscription(models.Model):
    staff = models.ForeignKey(Staff,on_delete=models.CASCADE)
    subscription_id = models.CharField(max_length = 100,null=True,blank=True) 
    merchant_user_id = models.CharField(max_length = 100,null=True,blank=True)
    merchant_subscription_id = models.CharField(max_length = 100,null=True,blank=True)
    recurring_count = models.IntegerField(null=True,blank=True)
    
    
    def __str__(self):
        return self.staff



class UploadDocument(models.Model):
    employee = models.ForeignKey(Staff, on_delete=models.CASCADE, related_name='upload_documents',null=True,blank=True)
    document_type = models.CharField(max_length=50)
    document_name = models.CharField(max_length=100)
    document_data = models.URLField(max_length=100)
        
    @property
    def upload_documents_list(self):
        return self.upload_documents.values_list('document_type', 'document_name', 'document_data')

    class Meta:
        verbose_name = 'Staff'
        verbose_name_plural = 'Staffs'

class EmployeeIdSetting(models.Model):
    newspaper = models.ForeignKey(NewsPaper,on_delete=models.CASCADE)
    company_logo = models.URLField(max_length=255)
    Idcard_templateid = models.ForeignKey(Templates,on_delete=models.CASCADE)
    primary_color_code = models.CharField(max_length=100)
    emplyeeid_prefix = models.CharField(max_length=100)
    secondary_color_code = models.CharField(max_length=100)
    authorised_sign = models.URLField(max_length=255)
    terms_conditions = models.JSONField()
    card_validity = models.IntegerField()

    
class Category(models.Model):
    category_name = models.CharField(max_length=255, blank=True, null=True)
    content_language = models.ForeignKey(Language,on_delete=models.CASCADE,blank=True, null=True)
    image = models.URLField(max_length=255, blank=True, null=True)
    parent = models.ForeignKey('self', on_delete=models.SET_NULL, blank=True, null=True, related_name='children')

class CategoryAllocation(models.Model):
    newspaper = models.ForeignKey(NewsPaper,on_delete=models.CASCADE)
    category = models.ManyToManyField(Category)

class NewsType(models.Model):
    type_name = models.CharField(max_length=255, blank=True, null=True)

class Tag(models.Model):
    hashtag = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        return self.hashtag


media_type = [
        ('image', 'Image'),
        ('video', 'Video'),
        ('url', 'url'),
    ]
class PostArticle(models.Model):
    staff = models.ForeignKey(Staff, on_delete=models.CASCADE, null=True, blank=True)
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, null=True, blank=True)
    news_language = models.ForeignKey(Language,on_delete=models.CASCADE,blank=True, null=True)
    title1 = models.CharField(max_length=60, blank=True, null=True)
    title1_color_code = models.CharField(max_length=100, blank=True, null=True)
    title2 = models.CharField(max_length=60, blank=True, null=True)
    title2_color_code = models.CharField(max_length=100, blank=True, null=True)
    title3 = models.CharField(max_length=60, blank=True, null=True)
    title3_color_code = models.CharField(max_length=100, blank=True, null=True)
    short_news = models.CharField(max_length=100,blank=True, null=True)
    long_news = models.TextField(blank=True, null=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    news_type = models.ForeignKey(NewsType, on_delete=models.CASCADE,null=True,blank=True)
    breaking_news = models.BooleanField(blank=True, null=True)
    file_upload = models.URLField(blank=True, null=True)
    media_type = models.CharField(max_length=100,choices=media_type)
    tags = models.ManyToManyField(Tag,blank=True)
    meta_keyword = models.JSONField(blank=True, null=True)
    meta_description = models.CharField(max_length=250,blank=True, null=True)
    publish_status = models.BooleanField(default=False)
    template_id = models.ForeignKey(Templates, on_delete=models.CASCADE, null=True, blank=True)
    SezReporter_Id = models.IntegerField(blank=True, null=True)
    updated_staff_id = models.IntegerField(blank=True, null=True)
    article_location = models.JSONField(blank=True, null=True)
    create_time = models.DateTimeField(default=timezone.now)
    kabulru_used_article = models.BooleanField(default=False)
    

class ArticleViewCount(models.Model):
    article = models.ForeignKey(PostArticle, on_delete=models.CASCADE)
    view_count = models.IntegerField(default=0)


class ArticleFeedback(models.Model):
    article = models.ForeignKey(PostArticle,on_delete=models.CASCADE)
    comment = models.TextField()
    like = models.BooleanField(blank=True, null=True)
    dislike = models.BooleanField(blank=True, null=True)
    angry = models.BooleanField(blank=True, null=True)
    happy = models.BooleanField(blank=True, null=True)


class SubscriptionPlan(models.Model):
    company = models.ForeignKey(Company,on_delete=models.CASCADE)
    newspaper = models.ForeignKey(NewsPaper,on_delete=models.CASCADE)
    plan_id = models.CharField(max_length=100)
    entity = models.CharField(max_length=100)
    interval = models.IntegerField()
    period = models.CharField(max_length=100)
    item = models.JSONField()
    notes = models.JSONField()
    created_at = models.BigIntegerField()

class EditionCategory(models.Model):
    name = models.CharField(max_length=200)
    parent = models.ForeignKey('self', on_delete=models.SET_NULL, blank=True, null=True, related_name='children')

class EditionAllocation(models.Model):
    newspaper = models.ForeignKey(NewsPaper,on_delete=models.CASCADE)
    edition = models.ManyToManyField(EditionCategory)

class ENewsPaper(models.Model):
    newspaper = models.ForeignKey(NewsPaper,on_delete=models.CASCADE,blank=True, null=True)
    edition = models.ForeignKey(EditionCategory,on_delete=models.CASCADE)
    pdf_file = models.URLField(max_length=255)
    image = models.URLField(max_length=255)
    date = models.DateTimeField()

class ENewsPaperFeedback(models.Model):
    enewspaper = models.ForeignKey(ENewsPaper,on_delete=models.CASCADE)
    comment = models.TextField()
    like = models.BooleanField(blank=True, null=True)
    dislike = models.BooleanField(blank=True, null=True)
    angry = models.BooleanField(blank=True, null=True)
    happy = models.BooleanField(blank=True, null=True)

class CroppedENewsPaper(models.Model):
    enewspaper = models.ForeignKey(ENewsPaper,on_delete=models.CASCADE)
    cropped_image = models.URLField(max_length=255)

