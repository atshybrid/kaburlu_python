from django.urls import path
from .views import *

urlpatterns = [
    #news_categories
    path('api/all_category/', GetAllCategories.as_view(), name="all_category"),
    path('api/filter_category/', FilterCategories.as_view(), name="filter_category"),
    path('api/create_category/', CreateCategory.as_view(), name="create_category"),
    path('api/category_detail/<int:category_id>/', GetCategoryDetail.as_view(), name="category_detail"),
    path('api/update_category/<int:category_id>/', UpdateCategory.as_view(), name="update_category"),
    path('api/delete_category/<int:category_id>/', DeleteCategory.as_view(), name="delete_category"),

    #news_speciality
    path('api/create_tag/', CreateTag.as_view(), name='create_tag'),
    path('api/update_tag/<int:tag_id>/', UpdateTag.as_view(), name='update_tag'),
    path('api/all_tags/', GetAllTags.as_view(), name='all_tags'),
    path('api/tag_detail/<int:tag_id>/', TagDetail.as_view(), name='tag_detail'),
    path('api/delete_tag/<int:tag_id>/', DeleteTag.as_view(), name='delete_tag'),

    #news_publish
    path('api/articles/post/', CreateNews.as_view(), name='create_news'),
    path('api/superadmin/articles/post/', SuperAdminCreateNews.as_view(), name='create_superadmin_news'),
    path('api/superadmin/articles/update/<int:news_id>/', SuperAdminNewsUpdate.as_view(), name='create_superadmin_news'),
    path('api/articles/update/<int:news_id>/', UpdateNews.as_view(), name='update_news'),
    path('api/articles/delete/<int:news_id>/', DeleteNews.as_view(), name='delete_news'),
    path('api/search_by_articles/', SearchByNews.as_view(), name='search_by_news'),
    path('api/articles/', GetAllNews.as_view(), name='all_news'),
    path('api/articles/detail/<int:news_id>/', GetNewsArticleDetail.as_view(), name='news_detail'),
    path('api/articles/views/<int:news_id>/', GetArticleViewsCount.as_view(), name='article_views'),

    #accounts
    path('api/account/create_reader/', CreateReader.as_view(), name='create_reader'),
    path('api/account/update_reader/<int:reader_id>/', UpdateReader.as_view(), name='update_reader'),
    path('api/account/all_reader_list/', AllReaderList.as_view(), name='all_reader_list'),
    path('api/account/reader_detail/<int:reader_id>/', ReaderDetail.as_view(), name='reader_detail'),

    #News Paper
    path('api/newspaper/create/', CreatNewsPaper.as_view(), name='create_news_paper'),
    path('api/newspaper/update/<int:news_id>/', UpdatNewsPaper.as_view(), name='update_news_paper'),
    path('api/newspaper/delete/<int:news_id>/', DeletNewsPaper.as_view(), name='delete_news_paper'),
    path('api/newspaper/search/', SearchByNewsPaper.as_view(), name='search_by_news_paper'),
    path('api/newspapers/', GetAllNewsPaper.as_view(), name='all_news_paper'),
    path('api/newspaper/login/', NewsPaperLoginAPIView.as_view(), name='newspaper_login'),
    path('api/verify/newspaper/otp/', VerifyNewsPaperOTPAPIView.as_view(), name='verify_newspaper_otp'),

    #NewsPaper Settings
    path('api/newspaper/domain-settings/<int:newspaper_id>/', CreatNewsPaperSetting.as_view(), name='create_newspaper_settings'),
    path('api/newspaper/settings/<int:newspaper_id>/', UpdateNewsPaperSetting.as_view(), name='update_newspaper_settings'),
    path('api/newspaper/settings/delete/<int:newspaper_id>/', DeletNewsPaperSetting.as_view(), name='delete_newspaper_settings'),
    path('api/newspaper/all/settings/', GetAllNewsPaperSetting.as_view(), name='all_newspaper_settings'),
    path('api/newspaper/settings/detail/<int:newspaper_id>/', GetNewsPaperSettingDetailView.as_view(), name='newspaper_settings_details'),

    #staff
    path('api/staff/accounts/create/', CreateStaff.as_view(), name='create_staff'),
    path('api/staff/accounts/update/<int:staff_id>/', UpdateStaff.as_view(), name='update_staff'),
    path('api/staff/accounts/delete/<int:staff_id>/', DeleteStaff.as_view(), name='delete_staff'),
    path('api/staff/accounts/detail/<int:staff_id>/', StaffDetail.as_view(), name='staff_detail'),
    path('api/staff/accounts/', AllStaffList.as_view(), name='all_staff'),
    path('api/staff/accounts/login/', StaffLoginAPIView.as_view(), name='staff_login'),
    path('api/verify/staff/accounts/otp/', VerifyStaffOTPAPIView.as_view(), name='verify_staff_otp'),

    #Staff Plan and Subscription
    path('api/kyc/update/<int:staff_id>/', StaffKycView.as_view(), name='staff_kyc'),
    path('api/aadhar/verify/<int:staff_id>/', KycOTPVerificationView.as_view(), name='kyc_opt_verification'),

    #Employee ID Setting
    path('api/employee/id-card/setup/', CreateEmpIDSetting.as_view(), name='create_empid_setting'),
    path('api/employee/id-card/setup/update/<int:empid_id>/', UpdateEmpID.as_view(), name='update_empid'),
    path('api/employee/id-card/setup/delete/<int:empid_id>/', DeleteEmpID.as_view(), name='delete_empid'),
    path('api/employee/id-card/setup/detail/<int:empid_id>/', EmpIdDetail.as_view(), name='emp_detail'),
    path('api/employee/id-card/all/setup/', AllEmpIDList.as_view(), name='all_empid'),

    #Employee Upload Document
    path('api/upload_document/', UploadEmployeeDocuments.as_view(), name='upload_document'),
    path('api/update_document/<int:doc_id>/', UpdateDocument.as_view(), name='update_document'),
    path('api/delete_document/<int:doc_id>/', DeleteDocument.as_view(), name='delete_document'),
    path('api/document_detail/<int:doc_id>/', DocumentDetail.as_view(), name='document_detail'),
    path('api/all_documents/', AllDocumentList.as_view(), name='all_documents'),

    #News Approval
    path('api/articles/publish/<int:article_id>/', ApproveNews.as_view(), name='approve_news'),

    #e-news paper
    path('api/e_news/', EPaperData.as_view(), name='e_news'),
    path('api/create_e_news/', CreateENewsPaper.as_view(), name='create_e_news'),
    path('api/all_e_news/', GetAllENewsPaper.as_view(), name='all_e_news'),
    path('api/edit_e_news/<int:enews_id>/', UpdateENewsPaper.as_view(), name='edit_e_news'),
    path('api/e_news_detail/<int:enews_id>/', GetENewsPaperDetail.as_view(), name='e_news_detail'),
    path('api/e_news_by_date/', GetENewsPaperByDate.as_view(), name='e_news_by_date'),
    path('api/delete_e_news/<int:enews_id>/', DeleteENewsPaper.as_view(), name='edit_e_news'),

    #Cropped ENewsPaper
    path('api/create_cropped_enewspaper/', AddCroppedENewsPaper.as_view(), name='create_cropped_enewspaper'),
    path('api/all_cropped_enewspaper/', GetAllCroppedENewsPaper.as_view(), name='all_cropped_enewspaper'),
    path('api/cropped_enewspaper_details/<int:enews_id>/', GetCropedENewsPaperDetailView.as_view(), name='cropped_enewspaper_details'),

    # Article feedback
    path('api/add_article_comment/', AddArticleFeedback.as_view(), name='add_article_comment'),
    path('api/all_comments/', GetAllArticleFeedback.as_view(), name='all_comments'),
    path('api/edit_comment/<int:feedback_id>/', UpdateArticleFeedback.as_view(), name='edit_comment'),
    path('api/comment_detail/<int:feedback_id>/', GetArticleFeedbackDetail.as_view(), name='comment_detail'),
    path('api/delete_comment/<int:feedback_id>/', DeleteArticleFeedback.as_view(), name='delete_comment'),

    #HTML to PDF Converter
    path('api/html/pdf/', html_to_pdf, name='html_to_pdf'),
    path('api/id/card/', sample, name='id_card'),

    # ENewsPaper feedback
    path('api/add_enewspaper_comment/', AddENewsPaperFeedback.as_view(), name='add_enewspaper_comment'),
    path('api/all_enewspaper_comments/', GetAllENewsPaperFeedback.as_view(), name='all_enewspaper_comments'),
    path('api/edit_enewspaper_comment/<int:feedback_id>/', UpdateENewsPaperFeedback.as_view(), name='edit_enewspaper_comment'),
    path('api/enewspaper_comment_detail/<int:feedback_id>/', GetENewsPaperFeedbackDetail.as_view(), name='enewspaper_comment_detail'),
    path('api/delete_enewspaper_comment/<int:feedback_id>/', DeleteENewsPaperFeedback.as_view(), name='delete_enewspaper_comment'),

    #Address 
    path('api/upload_address_file/', UploadAddress.as_view(), name='upload_address_file'),
    path('api/all_address_data/', GetAllAddressList.as_view(), name='all_address_data'),

    #news_edition
    path('api/all_edition/', GetAllEdition.as_view(), name="all_edition"),
    path('api/create_edition/', CreateEdition.as_view(), name="create_edition"),
    path('api/edition_detail/<int:edition_id>/', GetEditionDetail.as_view(), name="edition_detail"),
    path('api/update_edition/<int:edition_id>/', UpdateEdition.as_view(), name="update_edition"),
    path('api/delete_edition/<int:edition_id>/', DeleteEdition.as_view(), name="delete_edition"),

    #White Label Get APis
    path('api/webnewssettings/', GetWebNewsSettings.as_view(), name='webnewssettings'),
    path('api/allfeeds/', GetAllFeeds.as_view(), name='allfeeds'),
    path('api/feed/<int:article_id>/', GetArticle.as_view(), name='feed'),
    path('api/epapersettings/', GetEPaperSettings.as_view(), name='epapersettings'),
    path('api/getallepaperfeed/', GetAllEpaperFeed.as_view(), name='getallepaperfeed'),
    path('api/getepaperfeed/<int:epaper_id>/', GetEpaper.as_view(), name='getepaperfeed'),

    path('api/newspaper/categories/allocate/', AllocateCategory.as_view(), name='allocate_category'),
    path('api/api/newspaper/categories/allocated/', GetAllAllocatedCategory.as_view(), name='all_allocated_categories'),
    path('api/api/newspaper/categories/update/<int:allocation_id>/', UpdateCategoryAllocation.as_view(), name="update_category_allocation"),
    path('api/newspaper/categories/detail/<int:allocation_id>/', GetCategoryAllocationDetail.as_view(), name="category_allocation_detail"),
    path('api/newspaper/categories/delete/<int:allocation_id>/', DeleteCategoryAllocation.as_view(), name="delete_category_allocation"),
    path('api/newspaper/editions/allocate/', AllocateEdition.as_view(), name='allocate_edition'),
    path('api/newspaper/editions/allocated/', GetAllAllocatedEdition.as_view(), name='all_allocated_editions'),
    path('api/newspaper/editions/update/<int:allocation_id>/', UpdateEditionAllocation.as_view(), name="update_edition_allocation"),
    path('api/newspaper/editions/detail/<int:allocation_id>/', GetEditionAllocationDetail.as_view(), name="edition_allocation_detail"),
    path('api/newspaper/editions/delete/<int:allocation_id>/', DeleteEditionAllocation.as_view(), name="delete_edition_allocation"),

     #Template API Url
    path('api/all_templates/', GetAllTemplate.as_view(), name="all_templates"),
    path('api/add_template/', AddTemplates.as_view(), name="add_template"),
    path('api/template_detail/<int:tempate_id>/', GetTemplateDetail.as_view(), name="template_detail"),
    path('api/update_template/<int:tempate_id>/', UpdateTemplate.as_view(), name="update_template"),
    path('api/delete_template/<int:tempate_id>/', DeleteTemplate.as_view(), name="delete_template"),

    path('api/get/employeeid/<int:emp_id>/', GetEmployeeIDCard.as_view(), name="get_employee_id"),
    path('api/domain/list/', GetAllDomainList.as_view(), name="domain_list"),
    path('api/languages/', GetAllLanguageList.as_view(), name="language_list"),

    path('api/create/subscription/', CreateSubscription.as_view(), name="create_subscription"),
    path('api/subscription/authentication/', AuthenticateSubscription.as_view(), name="subscription_auth"),
    path('api/subscription/status/', CreateSubscription.as_view(), name="subscription_status"),
    path('api/subscription/init/', AuthenticateSubscription.as_view(), name="subscription_init"),
]








