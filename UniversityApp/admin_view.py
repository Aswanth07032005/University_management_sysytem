
from UniversityApp.forms import DepartmentForm
from UniversityApp.models import UniversityStaff, College, Department, Student


def admin_dashboard_view(request):
    return render(request,'admin/admin_dashboard.html')


def StaffListView(request):

    staffs = UniversityStaff.objects.all()

    return render(
        request,
        "admin/staff_list.html",
        {
            "staffs": staffs
        }
    )



def ApproveStaffView(request, id):

    staff = get_object_or_404(
        UniversityStaff,
        id=id
    )

    staff.is_approved = True
    staff.save()

    return redirect("staff_list")



def RejectStaffView(request, id):

    staff = get_object_or_404(
        UniversityStaff,
        id=id
    )

    staff.is_approved = False
    staff.save()

    return redirect("staff_list")






def CollegeListView(request):

    colleges = College.objects.all()

    return render(
        request,
        "admin/college_list.html",
        {
            "colleges": colleges
        }
    )





def ApproveCollegeView(request, id):

    college = get_object_or_404(
        College,
        id=id
    )

    college.is_approved = True
    college.save()

    return redirect("college_list")



def RejectCollegeView(request, id):

    college = get_object_or_404(
        College,
        id=id
    )

    college.is_approved = False
    college.save()

    return redirect("college_list")





def DepartmentAddView(request):




    form = DepartmentForm(
        request.POST or None
    )

    if form.is_valid():

        department = form.save(
            commit=False
        )




        department.save()

        messages.success(
            request,
            "Department added successfully."
        )

        return redirect("department_list")

    return render(
        request,
        "admin/department_add.html",
        {
            "form": form
        }
    )



from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages

# ==========================
# Department List
# ==========================

def DepartmentListView(request):

    departments = Department.objects.all().order_by(
        "department_name"
    )

    return render(
        request,
        "admin/department_list.html",
        {
            "departments": departments
        }
    )


# ==========================
# Department Edit
# ==========================

def DepartmentEditView(request, id):

    department = get_object_or_404(
        Department,
        id=id
    )

    if request.method == "POST":

        form = DepartmentForm(
            request.POST,
            instance=department
        )

        if form.is_valid():

            form.save()

            messages.success(
                request,
                "Department updated successfully."
            )

            return redirect("department_list")

    else:

        form = DepartmentForm(
            instance=department
        )

    return render(
        request,
        "admin/department_edit.html",
        {
            "form": form,
            "department": department
        }
    )


# ==========================
# Department Delete
# ==========================

def DepartmentDeleteView(request, id):

    department = get_object_or_404(
        Department,
        id=id
    )

    department.delete()

    messages.success(
        request,
        "Department deleted successfully."
    )

    return redirect("department_list")


# ==========================
# Student List
# ==========================

def StudentListView(request):

    students = Student.objects.select_related(
        "user"
    ).order_by(
        "-created_at"
    )

    return render(
        request,
        "admin/student_list.html",
        {
            "students": students
        }
    )