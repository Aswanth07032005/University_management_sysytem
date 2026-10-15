from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import (
    render,
    redirect,
    get_object_or_404,
)

from UniversityApp.forms import (
    RegisterForm,
    StaffRegisterForm,
    StaffProfileForm,
    StudentForm,
    EligibilityForm,
)

from UniversityApp.models import (
    UniversityStaff,
    College,
    Course,
    Department,
    Student,
    AdmissionApplication,
)

from .utils import (
    extract_certificate_details,
    verify_certificate,
)


# =========================================================
# STAFF REGISTER
# =========================================================

def StaffRegisterView(request):

    register_form = RegisterForm()
    staff_form = StaffRegisterForm()

    if request.method == "POST":

        register_form = RegisterForm(request.POST)
        staff_form = StaffRegisterForm(request.POST)

        if register_form.is_valid() and staff_form.is_valid():

            # Create User
            user = register_form.save(commit=False)

            user.is_university_staff = True

            user.save()

            # Create Staff Profile
            staff = staff_form.save(commit=False)

            staff.user = user

            # Admin approval pending
            staff.is_approved = False

            staff.save()

            return redirect("login_p")

    return render(
        request,
        "staff/staff_register.html",
        {
            "register_form": register_form,
            "staff_form": staff_form,
        }
    )


# =========================================================
# STAFF DASHBOARD
# =========================================================

@login_required(login_url="UniversityStaffLogin")
def staff_dash_view(request):

    staff = get_object_or_404(
        UniversityStaff,
        user=request.user
    )

    return render(
        request,
        "staff/staff_dashboard.html",
        {
            "staff": staff,
        }
    )


# =========================================================
# STAFF PROFILE
# =========================================================

@login_required(login_url="UniversityStaffLogin")
def StaffProfileView(request):

    staff = get_object_or_404(
        UniversityStaff,
        user=request.user
    )

    return render(
        request,
        "staff/staff_profile.html",
        {
            "staff": staff,
        }
    )


# =========================================================
# STAFF PROFILE EDIT
# =========================================================

@login_required(login_url="UniversityStaffLogin")
def StaffProfileEditView(request):

    staff = get_object_or_404(
        UniversityStaff,
        user=request.user
    )

    form = StaffProfileForm(
        request.POST or None,
        instance=staff
    )

    if form.is_valid():

        form.save()

        messages.success(
            request,
            "Profile updated successfully."
        )

        return redirect("staff_profile")

    return render(
        request,
        "staff/staff_profile_edit.html",
        {
            "form": form,
            "staff": staff,
        }
    )


# =========================================================
# STAFF COURSE LIST
# =========================================================

@login_required(login_url="UniversityStaffLogin")
def StaffCourseListView(request):

    staff = get_object_or_404(
        UniversityStaff,
        user=request.user
    )

    departments = (
        Department.objects
        .prefetch_related("courses")
        .order_by("department_name")
    )

    return render(
        request,
        "staff/course_list.html",
        {
            "staff": staff,
            "departments": departments,
        }
    )


# =========================================================
# UPDATE ELIGIBILITY
# =========================================================

@login_required(login_url="UniversityStaffLogin")
def EligibilityUpdateView(request, id):

    department = get_object_or_404(
        Department,
        id=id
    )

    course = (
        Course.objects
        .filter(
            department=department
        )
        .first()
    )

    if course is None:

        messages.warning(
            request,
            "No courses found under this department."
        )

        return redirect("staff_course_list")

    if request.method == "POST":

        form = EligibilityForm(
            request.POST,
            instance=course
        )

        if form.is_valid():

            Course.objects.filter(
                department=department
            ).update(
                eligibility_percentage=
                    form.cleaned_data[
                        "eligibility_percentage"
                    ],

                course_fee=
                    form.cleaned_data[
                        "course_fee"
                    ],
            )

            messages.success(
                request,
                "Eligibility and course fee updated successfully."
            )

            return redirect("staff_course_list")

    else:

        form = EligibilityForm(
            instance=course
        )

    return render(
        request,
        "staff/eligibility_update.html",
        {
            "department": department,
            "form": form,
        }
    )


# =========================================================
# STAFF COLLEGE LIST
# =========================================================

@login_required(login_url="UniversityStaffLogin")
def StaffCollegeListView(request):

    colleges = (
        College.objects
        .filter(
            is_approved=True
        )
        .order_by(
            "college_name"
        )
    )

    return render(
        request,
        "staff/college_list.html",
        {
            "colleges": colleges,
        }
    )


# =========================================================
# STUDENT LIST
# =========================================================

@login_required(login_url="UniversityStaffLogin")
def StudentListView(request):

    students = (
        Student.objects
        .select_related(
            "user",
            "allotted_college",
            "allotted_course",
        )
        .order_by(
            "full_name"
        )
    )

    return render(
        request,
        "staff/student_list.html",
        {
            "students": students,
        }
    )


# =========================================================
# STUDENT EDIT
# =========================================================

@login_required(login_url="UniversityStaffLogin")
def StudentEditView(request, id):

    student = get_object_or_404(
        Student,
        id=id
    )

    if request.method == "POST":

        form = StudentForm(
            request.POST,
            request.FILES,
            instance=student
        )

        if form.is_valid():

            form.save()

            messages.success(
                request,
                "Student updated successfully."
            )

            return redirect(
                "staff_student_list"
            )

    else:

        form = StudentForm(
            instance=student
        )

    return render(
        request,
        "staff/student_edit.html",
        {
            "form": form,
            "student": student,
        }
    )


# =========================================================
# STUDENT DELETE
# =========================================================

@login_required(login_url="UniversityStaffLogin")
def StudentDeleteView(request, id):

    student = get_object_or_404(
        Student,
        id=id
    )

    user = student.user

    user.delete()

    messages.success(
        request,
        "Student deleted successfully."
    )

    return redirect(
        "staff_student_list"
    )


# =========================================================
# STAFF APPLICATIONS
# =========================================================

@login_required(login_url="UniversityStaffLogin")
def StaffApplicationsView(request):

    staff = get_object_or_404(
        UniversityStaff,
        user=request.user
    )

    applications = (
        AdmissionApplication.objects
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

    return render(
        request,
        "staff/staff_applications.html",
        {
            "staff": staff,
            "applications": applications,
        }
    )


























@login_required(login_url="UniversityStaffLogin")
def VerifyAllApplicationsView(request):

    # =====================================================
    # GET LOGGED-IN STAFF
    # =====================================================

    staff = get_object_or_404(
        UniversityStaff,
        user=request.user
    )

    # =====================================================
    # GET ALL APPLICATIONS
    # =====================================================

    applications = (
        AdmissionApplication.objects
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

    verification_results = []

    # =====================================================
    # VERIFY EACH APPLICATION
    # =====================================================

    for application in applications:

        student = application.student

        # =================================================
        # ADMISSION ALREADY REGISTERED
        # =================================================

        already_registered = (
            student.admission_status
            == "Admission Registered"
        )

        # =================================================
        # NO CERTIFICATE
        # =================================================

        if not application.plus_two_certificate:

            application.university_application_verification = 0

            application.document_verified = False

            application.save(
                update_fields=[
                    "university_application_verification",
                    "document_verified",
                ]
            )

            verification_results.append({

                "application": application,

                "verification": {

                    "registered_name":
                        student.full_name,

                    "certificate_name":
                        None,

                    "name_matched":
                        False,

                    "registered_qualification":
                        student.previous_qualification,

                    "certificate_qualification":
                        None,

                    "qualification_matched":
                        False,

                    "registered_percentage":
                        student.plus_two_percentage,

                    "certificate_percentage":
                        None,

                    "percentage_matched":
                        False,

                    "document_verified":
                        application.document_verified,
                },

                "error":
                    "Plus Two certificate not uploaded.",

            })

            continue

        # =================================================
        # EXTRACT CERTIFICATE DETAILS
        # =================================================

        certificate_details = extract_certificate_details(
            application.plus_two_certificate
        )

        # =================================================
        # EXTRACTION ERROR
        # =================================================

        if certificate_details.get("error"):

            application.university_application_verification = 0

            application.document_verified = False

            application.save(
                update_fields=[
                    "university_application_verification",
                    "document_verified",
                ]
            )

            verification_results.append({

                "application":
                    application,

                "verification": {

                    "registered_name":
                        student.full_name,

                    "certificate_name":
                        None,

                    "name_matched":
                        False,

                    "registered_qualification":
                        student.previous_qualification,

                    "certificate_qualification":
                        None,

                    "qualification_matched":
                        False,

                    "registered_percentage":
                        student.plus_two_percentage,

                    "certificate_percentage":
                        None,

                    "percentage_matched":
                        False,

                    "document_verified":
                        application.document_verified,
                },

                "error":
                    certificate_details.get("error"),

            })

            continue

        # =================================================
        # VERIFY CERTIFICATE
        # =================================================

        verification = verify_certificate(
            student,
            certificate_details
        )

        # =================================================
        # CHECK 3 CONDITIONS
        #
        # 1. NAME
        # 2. QUALIFICATION
        # 3. PERCENTAGE
        #
        # Aadhaar is NOT checked here.
        # =================================================

        name_matched = verification.get(
            "name_matched",
            False
        )

        qualification_matched = verification.get(
            "qualification_matched",
            False
        )

        percentage_matched = verification.get(
            "percentage_matched",
            False
        )

        # =================================================
        # ALL VERIFICATION
        # =================================================

        all_verified = (
            name_matched
            and
            qualification_matched
            and
            percentage_matched
        )

        # =================================================
        # UPDATE CERTIFICATE PERCENTAGE
        # =================================================

        certificate_percentage = (
            verification.get(
                "certificate_percentage"
            )
        )

        if certificate_percentage is not None:

            application.certificate_percentage = (
                certificate_percentage
            )

        # =================================================
        # UNIVERSITY APPLICATION VERIFICATION
        #
        # 0 = Not fully verified
        # 1 = Name + Qualification + Percentage verified
        # =================================================

        if all_verified:

            application.university_application_verification = 1

            application.document_verified = True

            # =================================================
            # UPDATE STATUS
            # =================================================

            if (
                application.status != "Approved"
                and not already_registered
            ):

                application.status = (
                    "University Verified"
                )

            application.staff_remark = (
                "Name, qualification and percentage "
                "verified successfully."
            )

        else:

            # =================================================
            # VERIFICATION FAILED
            # =================================================

            application.university_application_verification = 0

            application.document_verified = False

            # =================================================
            # DO NOT REJECT AUTOMATICALLY
            # DO NOT DOWNGRADE APPROVED
            # =================================================

            if not already_registered:

                pass

        # =================================================
        # SAVE
        # =================================================

        application.save(
            update_fields=[
                "certificate_percentage",
                "document_verified",
                "university_application_verification",
                "status",
                "staff_remark",
            ]
        )

        # =================================================
        # RESULT
        # =================================================

        verification_results.append({

            "application":
                application,

            "verification":
                verification,

            "error":
                None,

        })

    # =====================================================
    # RENDER
    # =====================================================

    return render(
        request,
        "staff/staff_applications.html",
        {
            "staff":
                staff,

            "applications":
                applications,

            "verification_results":
                verification_results,

            "verification_done":
                True,
        }
    )














from django.contrib.auth.decorators import login_required
from django.shortcuts import render

from .models import Message


@login_required
def staff_messages(request):

    messages_list = Message.objects.filter(
        receiver=request.user
    ).order_by("-created_at")

    return render(
        request,
        "staff/messages.html",
        {
            "messages_list": messages_list
        }
    )











from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect

from .models import Message


@login_required
def staff_send_message(request):

    if not request.user.is_university_staff:
        messages.error(
            request,
            "You are not authorized to send messages to the admin."
        )
        return redirect("staff_dashboard")

    if request.method == "POST":

        subject = request.POST.get("subject")
        message_text = request.POST.get("message")
        priority = request.POST.get("priority", "NORMAL")

        if not subject or not message_text:

            messages.error(
                request,
                "Please fill in all required fields."
            )

            return render(
                request,
                "staff/send_message.html"
            )

        admin_user = request.user.__class__.objects.filter(
            is_superuser=True,
            is_active=True
        ).first()

        if not admin_user:

            messages.error(
                request,
                "Admin account was not found."
            )

            return render(
                request,
                "staff/send_message.html"
            )

        Message.objects.create(
            sender=request.user,
            receiver=admin_user,
            subject=subject,
            message=message_text,
            priority=priority
        )

        messages.success(
            request,
            "Your message has been sent to the administrator successfully."
        )

        return redirect("staff_send_message")

    return render(
        request,
        "staff/send_message.html"
    )








from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render

from .models import Message


@login_required
def staff_college_messages(request):

    if not request.user.is_university_staff:
        return redirect("login_p")

    # College അയച്ച messages മാത്രം
    college_messages = Message.objects.filter(
        receiver=request.user,
        sender__is_college=True
    ).select_related(
        "sender"
    ).order_by("-created_at")


    if request.method == "POST":

        message_id = request.POST.get("message_id")
        reply_text = request.POST.get("message", "").strip()

        original_message = get_object_or_404(
            Message,
            id=message_id,
            receiver=request.user,
            sender__is_college=True
        )

        if not reply_text:

            messages.error(
                request,
                "Please enter a reply message."
            )

            return redirect("staff_college_messages")


        # Reply ONLY to the college that sent the message
        Message.objects.create(
            sender=request.user,
            receiver=original_message.sender,
            subject=f"Re: {original_message.subject}",
            message=reply_text
        )

        messages.success(
            request,
            "Reply sent successfully to the college."
        )

        return redirect("staff_college_messages")


    return render(
        request,
        "staff/college_messages.html",
        {
            "college_messages": college_messages
        }
    )