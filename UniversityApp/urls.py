from django.urls import path

from UniversityApp import views, student_views, uni_staff_views, college_views, admin_view

urlpatterns = [
    path('',views.HomeView,name='Home'),
    path('login_page',views.login_view,name='login_p'),
    path('logout_button',views.logout_view,name='logout_b'),

    path( "chatbot/", views.chatbot, name="chatbot" ),
    path( "chatbot/api/", views.chatbot_api, name="chatbot_api" ),


    #admin
    path('admin_dashboard', admin_view.admin_dashboard_view, name='admin_d'),
    path("staff_list",admin_view.StaffListView,name="staff_list"),
    path("approve_staff/<int:id>/",admin_view.ApproveStaffView,name="approve_staff"),
    path("reject_staff/<int:id>/",admin_view.RejectStaffView,name="reject_staff"),
    path("college_list/", admin_view.CollegeListView, name="college_list"),
    path("approve_college/<int:id>/", admin_view.ApproveCollegeView, name="approve_college"),
    path("reject_college/<int:id>/", admin_view.RejectCollegeView, name="reject_college"),
    path("department_add/", admin_view.DepartmentAddView, name="department_add"),
    path("department_list/", admin_view.DepartmentListView, name="department_list"),
    path("department_edit/<int:id>/", admin_view.DepartmentEditView, name="department_edit"),
    path("department_delete/<int:id>/", admin_view.DepartmentDeleteView, name="department_delete"),
    path("admin_student_list/",admin_view.StudentListView,name="admin_student_list",),
    path("university-details/",admin_view.university_details_view,name="university_details"),
   path("applications/view/",admin_view.admin_application_view,name="admin_application_view"),
path(
    'admin-courses/',
    admin_view.admin_courses,
    name='admin_courses'
),






    #student
    path('student_register',student_views.StudentRegisterView,name='s_register'),
    path('student_dashboard',student_views.student_dashboard,name='s_dashboard'),
    path("student_profile",student_views.StudentProfileView,name="student_profile"),
    path("student_profile_edit/",student_views.StudentProfileEditView,name="student_profile_edit"),
    path("admissions/",student_views.AdmissionView,name="admissions"),
    path("admission/apply/",student_views.admission_apply, name="admission_apply"),
    path("payment/",student_views.payment,name="payment"),
    path("sucess_application/",student_views.Application_success,name="application__success"),
    path("student-applications/",student_views.StudentApplicationsView,name="student_applications"),
    path("application-report/",student_views.ApplicationReportView,name="application_report"),
    path("application/edit/<int:pk>/",student_views.ApplicationEditView,name="application_edit",),
    path("application/delete/<int:pk>/",student_views.ApplicationDeleteView,name="application_delete",),
    path("ajax/load-courses/",student_views.LoadCollegeCourses,name="load_college_courses"),
    path("courses-by-college/",student_views.CoursesByCollegeView,name="courses_by_college"),
    path("admission-status/",student_views.AdmissionStatusView,name="admission_status"),
    path("student/admission-slip/<int:application_id>/", student_views.AdmissionSlipDownloadView, name="admission_slip" ),



    # university_staff
    path('staff_register', uni_staff_views.StaffRegisterView, name='staff_r'),
    path('staff_dashboard', uni_staff_views.staff_dash_view, name='staff_dashboard'),
    path("staff_profile/", uni_staff_views.StaffProfileView,name="staff_profile"),
    path("staff_profile_edit/",uni_staff_views.StaffProfileEditView,name="staff_profile_edit"),
    path("staff/course_list/",uni_staff_views.StaffCourseListView,name="staff_course_list"),
    path("eligibility_update/<int:id>/",uni_staff_views.EligibilityUpdateView,name="eligibility_update"),
    path("staff/college_list/",uni_staff_views.StaffCollegeListView,name="staff_college_list"),
    path("staff/student_list/",uni_staff_views.StudentListView,name="staff_student_list"),
    path("staff/student_edit/<int:id>/",uni_staff_views.StudentEditView,name="staff_student_edit",),
    path("staff/student_delete/<int:id>/",uni_staff_views.StudentDeleteView,name="staff_student_delete",),
    path("staff/applications/",uni_staff_views.StaffApplicationsView,name="staff_applications"),
    path("staff/verify-all/",uni_staff_views.VerifyAllApplicationsView,name="verify_all_applications"),





    # college
    path('college_register',college_views.CollegeRegisterView, name='college_r'),
    path('college_dashboard',college_views.College_dahsboard_view, name='college_dashboard'),
    path("college_profile/",college_views.CollegeProfileView,name="college_profile"),
    path( "college_profile_edit/", college_views.CollegeProfileEditView,name="college_profile_edit"),
    path("course_add",college_views.CourseAddView,name="course_add"),
    path("course_list/",college_views.CourseListView,name="course_list"),
    path("course_edit/<int:id>/",college_views.CourseEditView,name="course_edit"),
    path("course_delete/<int:id>/",college_views.CourseDeleteView,name="course_delete"),
    path("college/applications/",college_views.CollegeApplicationsView,name="college_applications"),
    path("college/applications/approve/<int:application_id>/",college_views.CollegeApproveApplicationView,name="college_approve_application"),
    path("college/approved-applications/",college_views.CollegeApprovedApplicationsView,name="college_approved_applications"),
    path("admission-register/<int:application_id>/",college_views.CollegeAdmissionRegisterView,name="admission_register"),
    path("registered-students/",college_views.CollegeRegisteredStudentsView,name="college_registered_students"),



]