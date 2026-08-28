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