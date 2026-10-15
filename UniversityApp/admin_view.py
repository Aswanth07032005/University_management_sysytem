
from UniversityApp.forms import DepartmentForm
from UniversityApp.models import UniversityStaff, College, Department, Student


def admin_dashboard_view(request):
    return render(request,'admin/admin_dashboard.html')





from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from .models import Register, College, Department


@login_required
def university_details_view(request):

    total_students = Register.objects.filter(
        is_student=True
    ).count()

    total_staff = Register.objects.filter(
        is_university_staff=True
    ).count()

    total_colleges = College.objects.count()

    total_departments = Department.objects.count()

    context = {
        "total_students": total_students,
        "total_staff": total_staff,
        "total_colleges": total_colleges,
        "total_departments": total_departments,
    }

    return render(
        request,
        "admin/university_details.html",
        context
    )




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





from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from .models import AdmissionApplication



def admin_application_view(request):
    applications = AdmissionApplication.objects.select_related(
        "student",
        "college"
    ).order_by("-id")

    return render(
        request,
        "admin/admin_application_view.html",
        {
            "applications": applications
        }
    )





from django.shortcuts import render
from .models import Course


def admin_courses(request):
    courses = Course.objects.all().order_by('course_name')

    context = {
        'courses': courses,
    }

    return render(
        request,
        'admin/admin_courses.html',
        context
    )






from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect

from .models import Notification, Message
from UniversityApp.models import Register


@login_required
def admin_send_message(request):

    # Admin മാത്രം access ചെയ്യാൻ
    if not request.user.is_superuser:
        messages.error(request, "You are not authorized to access this page.")
        return redirect("home")

    if request.method == "POST":

        category = request.POST.get("category")
        subject = request.POST.get("subject")
        message_text = request.POST.get("message")
        priority = request.POST.get("priority", "NORMAL")

        # Validation
        if not category or not subject or not message_text:
            messages.error(
                request,
                "Please fill in all required fields."
            )
            return render(
                request,
                "admin/send_message.html"
            )

        # Selected category users
        if category == "STUDENT":
            receivers = Register.objects.filter(
                is_student=True,
                is_active=True
            )

        elif category == "COLLEGE":
            receivers = Register.objects.filter(
                is_college=True,
                is_active=True
            )

        elif category == "STAFF":
            receivers = Register.objects.filter(
                is_university_staff=True,
                is_active=True
            )

        else:
            messages.error(request, "Invalid recipient category.")
            return render(
                request,
                "admin/send_message.html"
            )

        # Create common notification
        notification = Notification.objects.create(
            sender=request.user,
            category=category,
            subject=subject,
            message=message_text,
            priority=priority
        )

        # Create individual message for each receiver
        for receiver in receivers:

            Message.objects.create(
                sender=request.user,
                receiver=receiver,
                notification=notification,
                subject=subject,
                message=message_text,
                priority=priority
            )

        messages.success(
            request,
            f"Message sent successfully to {receivers.count()} {category.lower()} users."
        )

        return redirect("admin_send_message")

    return render(
        request,
        "admin/send_message.html"
    )






def admin_staff_messages(request):
    messages = Message.objects.filter(
        sender__is_university_staff=True
    ).order_by("-created_at")

    return render(
        request,
        "admin/staff_messages.html",
        {
            "messages": messages
        }
    )





def admin_staff_messages(request):
    messages_list = Message.objects.filter(
        sender__is_university_staff=True
    ).order_by("-created_at")

    return render(
        request,
        "admin/staff_messages.html",
        {
            "messages": messages_list
        }
    )


def admin_reply_staff(request, message_id):

    original_message = get_object_or_404(
        Message,
        id=message_id,
        sender__is_university_staff=True
    )

    if request.method == "POST":

        reply_text = request.POST.get("message", "").strip()

        if reply_text:

            Message.objects.create(
                sender=request.user,
                receiver=original_message.sender,
                subject=f"Re: {original_message.subject}",
                message=reply_text
            )

            messages.success(
                request,
                "Reply sent successfully to the staff member."
            )

        else:

            messages.error(
                request,
                "Please enter a message."
            )

    return redirect("admin_staff_messages")