from django.contrib import messages
from django.contrib.auth import login, authenticate, logout
from django.shortcuts import render, redirect

from UniversityApp.models import College, UniversityStaff, Course


def HomeView(request):

    data = Course.objects.all()

    return render(request,'Index.html',{'data':data})

# admin
# admin567567567

def login_view(request):

    if request.method == "POST":

        username = request.POST.get("username")
        password = request.POST.get("password")

        user = authenticate(
            request,
            username=username,
            password=password
        )

        if user is not None:

            # -------------------- Admin --------------------

            if user.is_superuser or user.is_staff:

                login(request, user)
                return redirect("admin_d")

            # -------------------- University Staff --------------------

            elif user.is_university_staff:

                staff = UniversityStaff.objects.get(user=user)

                if not staff.is_approved:

                    messages.error(
                        request,
                        "Staff account waiting for admin approval."
                    )

                    return redirect("login_p")

                login(request, user)
                # return redirect("staff_dashboard")
                return redirect("/")

            # -------------------- College --------------------

            elif user.is_college:

                college = College.objects.get(user=user)

                if not college.is_approved:

                    messages.error(
                        request,
                        "College account waiting for admin approval."
                    )

                    return redirect("login_p")

                login(request, user)
                messages.success(request, "Login Successful. Welcome !")
                # return redirect("college_dashboard")
                return redirect("/")


            # -------------------- Student --------------------

            elif user.is_student:

                login(request, user)
                messages.success(request, "Login Successful. Welcome Student!")
                return redirect("/")

            # -------------------- Other Users --------------------

            else:

                login(request, user)
                return redirect("home")

        else:

            messages.error(
                request,
                "Invalid username or password."
            )

    return render(
        request,
        "login.html"
    )


def logout_view(request):

    logout(request)
    messages.warning(
        request,
        "You have been logged out successfully."
    )

    return redirect("/")
























from django.shortcuts import render
from django.http import JsonResponse

from .models import (
    College,
    Course,
    Department,
)

from .groq_service import ask_groq


# =========================================================
# PUBLIC CHATBOT PAGE
# =========================================================

def chatbot(request):

    return render(
        request,
        "chatbot.html"
    )


# =========================================================
# PUBLIC CHATBOT API
# =========================================================

def chatbot_api(request):

    if request.method != "POST":

        return JsonResponse({
            "success": False,
            "answer": "Invalid request."
        })


    message = request.POST.get(
        "message",
        ""
    ).strip()


    if not message:

        return JsonResponse({
            "success": False,
            "answer": "Please enter a message."
        })


    try:

        # =================================================
        # APPROVED COLLEGES
        # =================================================

        colleges = College.objects.filter(
            is_approved=True
        )


        college_context = ""


        for college in colleges:

            college_context += f"""
College Name: {college.college_name}
District: {college.district}
State: {college.state}
Address: {college.address}
"""


        if not college_context:

            college_context = "No approved colleges available."


        # =================================================
        # COURSES
        # =================================================

        courses = Course.objects.select_related(
            "college",
            "department"
        )


        course_context = ""


        for course in courses:

            course_context += f"""
Course Name: {course.course_name}
Course Code: {course.course_code}
College: {course.college.college_name}
Department: {course.department.department_name}
Duration: {course.duration}
Course Fee: ₹{course.course_fee}
Total Seats: {course.total_seats}
Eligibility: {course.eligibility_percentage}%
Description: {course.description}
"""


        if not course_context:

            course_context = "No course information available."


        # =================================================
        # DEPARTMENTS
        # =================================================

        departments = Department.objects.all()


        department_context = ""


        for department in departments:

            department_context += f"""
Department Name: {department.department_name}
Department Code: {department.department_code}
Description: {department.description}
"""


        if not department_context:

            department_context = "No department information available."


        # =================================================
        # DATABASE CONTEXT
        # =================================================

        context = f"""

========================================
UNIVERSITY MANAGEMENT SYSTEM
========================================


APPROVED COLLEGES:

{college_context}


AVAILABLE COURSES:

{course_context}


DEPARTMENTS:

{department_context}


========================================
END DATABASE INFORMATION
========================================
"""


        # =================================================
        # ASK GROQ
        # =================================================

        answer = ask_groq(
            message,
            context
        )


        return JsonResponse({

            "success": True,

            "answer": answer

        })


    except Exception as e:

        print(
            "CHATBOT ERROR:",
            repr(e)
        )


        return JsonResponse({

            "success": False,

            "answer":
            f"Chatbot Error: {str(e)}"

        })

