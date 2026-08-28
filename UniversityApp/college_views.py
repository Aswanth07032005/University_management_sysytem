from django.contrib import messages
from django.shortcuts import render, redirect, get_object_or_404

from UniversityApp.forms import RegisterForm, CollegeRegisterForm, CollegeProfileForm, CourseForm, DepartmentForm
from UniversityApp.models import College, Course, Department, AdmissionApplication


def CollegeRegisterView(request):

    register_form = RegisterForm()
    college_form = CollegeRegisterForm()


    if request.method == "POST":

        register_form = RegisterForm(request.POST)
        college_form = CollegeRegisterForm(request.POST)


        if register_form.is_valid() and college_form.is_valid():

            # Create User
            user = register_form.save(commit=False)

            user.is_college = True

            user.save()


            # Create College Profile
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
            "college_form": college_form
        }
    )


def College_dahsboard_view(request):
    return render(request,'college/college_dashboard.html')




def CollegeProfileView(request):

    college = College.objects.get(
        user=request.user
    )

    return render(
        request,
        "college/college_profile.html",
        {
            "college": college
        }
    )






def CollegeProfileEditView(request):

    college = College.objects.get(
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
            "form": form
        }
    )












def CourseAddView(request):

    college = College.objects.get(user=request.user)

    if request.method == "POST":

        form = CourseForm(request.POST)

        if form.is_valid():

            course = form.save(commit=False)

            course.college = college

            course.save()

            return redirect("course_list")

    else:

        form = CourseForm()

    return render(
        request,
        "college/course_add.html",
        {
            "form": form
        }
    )
from django.shortcuts import get_object_or_404, redirect, render

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

            course.college = college

            course.save()

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
            "course": course
        }
    )






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

    return redirect("course_list")






def CourseListView(request):

    college = get_object_or_404(
        College,
        user=request.user
    )

    courses = Course.objects.filter(
        college=college
    ).select_related(
        "department"
    ).order_by(
        "department__department_name",
        "course_name"
    )

    return render(
        request,
        "college/course_list.html",
        {
            "college": college,
            "courses": courses,
        }
    )









def college_allotted_applications(request):

    college = get_object_or_404(
        College,
        user=request.user
    )

    applications = AdmissionApplication.objects.filter(
        student__allotted_college=college
    ).select_related(
        "student",
        "course",
        "department",
        "college",
    )

    return render(
        request,
        "college/allotted_applications.html",
        {
            "college": college,
            "applications": applications,
        }
    )