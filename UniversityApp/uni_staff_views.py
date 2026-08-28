from django.contrib import messages
from django.shortcuts import render, redirect, get_object_or_404

from UniversityApp.forms import (
    RegisterForm,
    StaffRegisterForm,
    StaffProfileForm,
    StudentForm,
    EligibilityForm,
)

from UniversityApp.models import (
    UniversityStaff,
    Course,
    Department,
    Student,
    AdmissionApplication,
)





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
            "staff_form": staff_form
        }
    )


def staff_dash_view(request):
    return render(request,'staff/staff_dashboard.html')






def StaffProfileView(request):

    staff = UniversityStaff.objects.get(
        user=request.user
    )

    return render(
        request,
        "staff/staff_profile.html",
        {
            "staff": staff
        }
    )








def StaffProfileEditView(request):

    staff = UniversityStaff.objects.get(
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
            "form": form
        }
    )





def StaffCourseListView(request):

    staff = UniversityStaff.objects.get(
        user=request.user
    )

    departments = Department.objects.prefetch_related(
        "courses"
    ).order_by(
        "department_name"
    )

    return render(
        request,
        "staff/course_list.html",
        {
            "staff": staff,
            "departments": departments,
        }
    )

from django.shortcuts import get_object_or_404, redirect, render

from django.shortcuts import get_object_or_404, redirect, render


def EligibilityUpdateView(request, id):
    department = get_object_or_404(Department, id=id)

    # A department can have several courses — we only need one
    # to pre-fill the form; the values get applied to all of them.
    course = Course.objects.filter(department=department).first()
    if course is None:
        # No courses under this department yet — nothing to edit
        return redirect("staff_course_list")

    if request.method == "POST":
        form = EligibilityForm(request.POST, instance=course)
        if form.is_valid():
            Course.objects.filter(department=department).update(
                eligibility_percentage=form.cleaned_data["eligibility_percentage"],
                course_fee=form.cleaned_data["course_fee"],
            )
            return redirect("staff_course_list")
    else:
        form = EligibilityForm(instance=course)

    return render(
        request,
        "staff/eligibility_update.html",
        {
            "department": department,
            "form": form,
        },
    )





from django.shortcuts import render
from .models import College

def StaffCollegeListView(request):

    colleges = College.objects.filter(
        is_approved=True
    ).order_by("college_name")

    return render(
        request,
        "staff/college_list.html",
        {
            "colleges": colleges
        }
    )




def StudentListView(request):

    students = Student.objects.select_related(
        "user"
    ).order_by(
        "full_name"
    )

    return render(
        request,
        "staff/student_list.html",
        {
            "students": students
        }
    )








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

            return redirect("staff_student_list")

    else:

        form = StudentForm(
            instance=student
        )

    return render(
        request,
        "staff/student_edit.html",
        {
            "form": form,
            "student": student
        }
    )




def StudentDeleteView(request, id):

    student = get_object_or_404(
        Student,
        id=id
    )

    user = student.user

    user.delete()   # OneToOneField(CASCADE) ആണെങ്കിൽ Student record-ും delete ആവും

    messages.success(
        request,
        "Student deleted successfully."
    )

    return redirect("staff_student_list")













from django.contrib.auth.decorators import login_required
from django.shortcuts import render

from .models import AdmissionApplication, UniversityStaff


@login_required(login_url="UniversityStaffLogin")
def StaffApplicationsView(request):

    # =====================================================
    # GET LOGGED-IN UNIVERSITY STAFF
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

    # =====================================================
    # CONTEXT
    # =====================================================

    context = {
        "staff": staff,
        "applications": applications,
    }

    # =====================================================
    # RENDER
    # =====================================================

    return render(
        request,
        "staff/staff_applications.html",
        context
    )
