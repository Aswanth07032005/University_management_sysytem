from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import (
    render,
    redirect,
    get_object_or_404
)
from django.utils import timezone
from django.core.mail import send_mail
from django.conf import settings

from UniversityApp.forms import (
    RegisterForm,
    CollegeRegisterForm,
    CollegeProfileForm,
    CourseForm,
    DepartmentForm,
)

from UniversityApp.models import (
    College,
    Course,
    Department,
    AdmissionApplication,
    Student,
)



def CollegeRegisterView(request):

    register_form = RegisterForm()
    college_form = CollegeRegisterForm()

    if request.method == "POST":

        register_form = RegisterForm(request.POST)
        college_form = CollegeRegisterForm(request.POST)

        if register_form.is_valid() and college_form.is_valid():

            # =================================================
            # CREATE USER
            # =================================================

            user = register_form.save(commit=False)

            user.is_college = True

            user.save()

            # =================================================
            # CREATE COLLEGE PROFILE
            # =================================================

            college = college_form.save(commit=False)

            college.user = user

            # Admin approval pending
            college.is_approved = False

            college.save()

            return redirect("login_p")

    return render(
        request,
        "college/college_register.html",
        {
            "register_form": register_form,
            "college_form": college_form,
        }
    )


# =========================================================
# COLLEGE DASHBOARD
# =========================================================

login_required(login_url="login_p")
def College_dahsboard_view(request):
    if not request.user.is_college:
        return redirect("login_p")
    college = get_object_or_404(
        College,
        user=request.user
    )

    return render(
        request,
        "college/college_dashboard.html",
        {
            "college": college,
        }
    )


# =========================================================
# COLLEGE PROFILE
# =========================================================

@login_required(login_url="login_p")
def CollegeProfileView(request):
    if not request.user.is_college:
        return redirect("login_p")
    college = get_object_or_404(
        College,
        user=request.user
    )

    return render(
        request,
        "college/college_profile.html",
        {
            "college": college,
        }
    )


# =========================================================
# COLLEGE PROFILE EDIT
# =========================================================

@login_required(login_url="CollegeLogin")
def CollegeProfileEditView(request):

    college = get_object_or_404(
        College,
        user=request.user
    )

    form = CollegeProfileForm(
        request.POST or None,
        instance=college
    )

    if form.is_valid():

        form.save()

        messages.success(
            request,
            "College profile updated successfully."
        )

        return redirect("college_profile")

    return render(
        request,
        "college/college_profile_edit.html",
        {
            "form": form,
            "college": college,
        }
    )


# =========================================================
# COURSE ADD
# =========================================================

@login_required(login_url="CollegeLogin")
def CourseAddView(request):

    college = get_object_or_404(
        College,
        user=request.user
    )

    if request.method == "POST":

        form = CourseForm(request.POST)

        if form.is_valid():

            course = form.save(commit=False)

            course.college = college

            course.save()

            messages.success(
                request,
                "Course added successfully."
            )

            return redirect("course_list")

    else:

        form = CourseForm()

    return render(
        request,
        "college/course_add.html",
        {
            "form": form,
            "college": college,
        }
    )


# =========================================================
# COURSE EDIT
# =========================================================

@login_required(login_url="CollegeLogin")
def CourseEditView(request, id):

    college = get_object_or_404(
        College,
        user=request.user
    )

    course = get_object_or_404(
        Course,
        id=id,
        college=college
    )

    if request.method == "POST":

        form = CourseForm(
            request.POST,
            instance=course
        )

        if form.is_valid():

            course = form.save(commit=False)

            # Security:
            # Course remains under logged-in college
            course.college = college

            course.save()

            messages.success(
                request,
                "Course updated successfully."
            )

            return redirect("course_list")

    else:

        form = CourseForm(
            instance=course
        )

    return render(
        request,
        "college/course_edit.html",
        {
            "form": form,
            "course": course,
            "college": college,
        }
    )


# =========================================================
# COURSE DELETE
# =========================================================

@login_required(login_url="CollegeLogin")
def CourseDeleteView(request, id):

    college = get_object_or_404(
        College,
        user=request.user
    )

    course = get_object_or_404(
        Course,
        id=id,
        college=college
    )

    course.delete()

    messages.success(
        request,
        "Course deleted successfully."
    )

    return redirect("course_list")


# =========================================================
# COURSE LIST
# =========================================================

@login_required(login_url="CollegeLogin")
def CourseListView(request):

    college = get_object_or_404(
        College,
        user=request.user
    )

    courses = (
        Course.objects
        .filter(
            college=college
        )
        .select_related(
            "department"
        )
        .order_by(
            "department__department_name",
            "course_name"
        )
    )

    return render(
        request,
        "college/course_list.html",
        {
            "college": college,
            "courses": courses,
        }
    )




# =========================================================
# COLLEGE APPLICATIONS
#
# Shows applications that:
#
# 1. Are fully verified by University Staff
# 2. university_application_verification = 1
# 3. status = University Verified
# 4. Student admission is NOT already registered
#
# Approved applications are shown separately in
# CollegeApprovedApplicationsView.
# =========================================================

# =========================================================
# COLLEGE APPLICATIONS
#
# Shows applications that:
#
# 1. university_application_verification = 1
# 2. Student admission is NOT already registered
#
# Aadhaar verification is NOT checked here.
# =========================================================

@login_required(login_url="CollegeLogin")
def CollegeApplicationsView(request):

    # =====================================================
    # GET LOGGED-IN COLLEGE
    # =====================================================

    college = get_object_or_404(
        College,
        user=request.user
    )

    # =====================================================
    # GET UNIVERSITY VERIFIED APPLICATIONS
    #
    # ONLY:
    #
    # university_application_verification = 1
    #
    # AND
    #
    # student.admission_status != Admission Registered
    # =====================================================

    applications = (
        AdmissionApplication.objects
        .filter(
            college=college,
            university_application_verification=1,
        )
        .exclude(
            student__admission_status="Admission Registered"
        )
        .select_related(
            "student",
            "college",
            "department",
            "course",
        )
        .order_by(
            "-applied_date"
        )
    )

    # =====================================================
    # COLLEGE COURSES
    # =====================================================

    courses = (
        Course.objects
        .filter(
            college=college
        )
        .select_related(
            "department"
        )
        .order_by(
            "course_name"
        )
    )

    # =====================================================
    # RENDER
    # =====================================================

    return render(
        request,
        "college/applications.html",
        {
            "college": college,
            "applications": applications,
            "courses": courses,
        }
    )






@login_required(login_url="CollegeLogin")
def CollegeApproveApplicationView(
    request,
    application_id
):

    # =====================================================
    # GET LOGGED-IN COLLEGE
    # =====================================================

    college = get_object_or_404(
        College,
        user=request.user
    )

    # =====================================================
    # ONLY POST
    # =====================================================

    if request.method != "POST":

        return redirect(
            "college_applications"
        )

    # =====================================================
    # GET APPLICATION
    # ONLY THIS COLLEGE
    # =====================================================

    application = get_object_or_404(
        AdmissionApplication.objects.select_related(
            "student",
            "college",
            "department",
            "course",
        ),
        id=application_id,
        college=college
    )

    # =====================================================
    # CHECK UNIVERSITY VERIFICATION
    #
    # Name + Qualification + Percentage
    # must be fully verified.
    # =====================================================

    if (
        application.status != "University Verified"
        or
        application.university_application_verification != 1
    ):

        messages.error(
            request,
            "This application has not been fully verified "
            "by University Staff."
        )

        return redirect(
            "college_applications"
        )

    # =====================================================
    # CHECK ADMISSION ALREADY REGISTERED
    # =====================================================

    if (
        application.student.admission_status
        == "Admission Registered"
    ):

        messages.error(
            request,
            "This student's admission is already registered."
        )

        return redirect(
            "college_applications"
        )

    # =====================================================
    # APPROVE
    # =====================================================

    application.status = "Approved"

    application.save(
        update_fields=[
            "status"
        ]
    )

    # =====================================================
    # APPROVED DATE
    # =====================================================

    approved_date = timezone.localtime()

    # =====================================================
    # STUDENT EMAIL
    # =====================================================

    student_email = application.student.email

    if student_email:

        subject = (
            "Admission Approved - Congratulations "
            "from MM Technical University"
        )

        message = f"""
Dear {application.student.full_name},

Congratulations!

We are pleased to inform you that your admission application
has been APPROVED successfully.

Admission Details
----------------------------

Application Number : APP-{application.id:05d}

College             : {application.college.college_name}

Department          : {application.department.department_name}

Course              : {application.course.course_name}

Admission Status    : APPROVED

Approved Date       : {approved_date.strftime("%d %B %Y, %I:%M %p")}


Congratulations once again on securing your admission.

We wish you all the very best for your academic journey.


Regards,

{application.college.college_name}

MM Technical University
Admission Management System
"""

        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            [student_email],
            fail_silently=True,
        )

    # =====================================================
    # SUCCESS
    # =====================================================

    messages.success(
        request,
        f"{application.student.full_name}'s admission "
        f"has been approved successfully."
    )

    return redirect(
        "college_applications"
    )


# =========================================================
# APPROVED APPLICATIONS
#
# Shows only:
#
# 1. status = Approved
# 2. university_application_verification = 1
#
#
#
#
#
#
#
#
#
#
#
# =========================================================

@login_required(login_url="CollegeLogin")
def CollegeApprovedApplicationsView(request):

    # =====================================================
    # GET LOGGED-IN COLLEGE
    # =====================================================

    college = get_object_or_404(
        College,
        user=request.user
    )

    # =====================================================
    # GET APPROVED APPLICATIONS
    # =====================================================

    applications = (
        AdmissionApplication.objects
        .filter(
            college=college,
            status="Approved",
            university_application_verification=1,
        )
        .select_related(
            "student",
            "college",
            "department",
            "course",
        )
        .order_by(
            "-applied_date"
        )
    )

    # =====================================================
    # COLLEGE COURSES
    # =====================================================

    courses = (
        Course.objects
        .filter(
            college=college
        )
        .select_related(
            "department"
        )
        .order_by(
            "course_name"
        )
    )

    # =====================================================
    # RENDER
    # =====================================================

    return render(
        request,
        "college/approved_applications.html",
        {
            "college": college,
            "applications": applications,
            "courses": courses,
        }
    )


# =========================================================
# COLLEGE ADMISSION REGISTER
#
# Approved application -> Admission Registered
#
# Can register ONLY when:
#
# 1. status = Approved
# 2. university_application_verification = 1
# 3. Application belongs to logged-in college
# =========================================================











@login_required(login_url="CollegeLogin")
def CollegeAdmissionRegisterView(
    request,
    application_id
):

    # =====================================================
    # GET LOGGED-IN COLLEGE
    # =====================================================

    college = get_object_or_404(
        College,
        user=request.user
    )

    # =====================================================
    # ONLY POST
    # =====================================================

    if request.method != "POST":

        return redirect(
            "college_approved_applications"
        )

    # =====================================================
    # GET APPROVED APPLICATION
    #
    # ONLY THIS COLLEGE
    # =====================================================

    application = get_object_or_404(
        AdmissionApplication.objects.select_related(
            "student",
            "college",
            "department",
            "course",
        ),
        id=application_id,
        college=college,
        status="Approved",
        university_application_verification=1,
    )

    # =====================================================
    # GET STUDENT
    # =====================================================

    student = application.student

    # =====================================================
    # CHECK ALREADY REGISTERED
    # =====================================================

    if (
        student.admission_status
        == "Admission Registered"
    ):

        messages.warning(
            request,
            f"{student.full_name}'s admission is already "
            f"registered."
        )

        return redirect(
            "college_approved_applications"
        )

    # =====================================================
    # REGISTER ADMISSION
    # =====================================================

    student.admission_status = (
        "Admission Registered"
    )

    student.allotted_college = (
        application.college
    )

    student.allotted_course = (
        application.course
    )

    # =====================================================
    # SAVE REGISTRATION DATE/TIME
    # =====================================================

    student.allotted_date = timezone.now()

    # =====================================================
    # SAVE STUDENT
    # =====================================================

    student.save(
        update_fields=[
            "admission_status",
            "allotted_college",
            "allotted_course",
            "allotted_date",
        ]
    )

    # =====================================================
    # SUCCESS
    # =====================================================

    messages.success(
        request,
        f"{student.full_name}'s admission has been "
        f"registered successfully."
    )

    return redirect(
        "college_approved_applications"
    )


# =========================================================
# COLLEGE REGISTERED STUDENTS
#
# ONLY students whose:
#
# admission_status = Admission Registered
#
# AND
#
# allotted_college = logged-in college
# =========================================================
















@login_required(login_url="CollegeLogin")
def CollegeRegisteredStudentsView(request):

    # =====================================================
    # GET LOGGED-IN COLLEGE
    # =====================================================

    college = get_object_or_404(
        College,
        user=request.user
    )

    # =====================================================
    # SEARCH
    # =====================================================

    search = request.GET.get(
        "search",
        ""
    ).strip()

    # =====================================================
    # REGISTERED STUDENTS
    # =====================================================

    students = (
        Student.objects
        .filter(
            allotted_college=college,
            admission_status="Admission Registered"
        )
        .select_related(
            "user",
            "allotted_college",
            "allotted_course",
            "allotted_course__department",
        )
        .order_by(
            "-allotted_date",
            "-created_at"
        )
    )

    # =====================================================
    # SEARCH
    # =====================================================

    if search:

        students = students.filter(
            full_name__icontains=search
        ) | students.filter(
            id__icontains=search
        )

    # =====================================================
    # CONTEXT
    # =====================================================

    context = {
        "college": college,
        "students": students,
        "search": search,
    }

    # =====================================================
    # RENDER
    # =====================================================

    return render(
        request,
        "college/registered_students.html",
        context
    )