from django import forms
from django.contrib.auth.forms import UserCreationForm

from .models import Student, Register, UniversityStaff, College, Department, Course, AdmissionApplication


class StudentForm(forms.ModelForm):
    class Meta:
        model = Student
        exclude = ["admission_status","user","allotted_college","allotted_course","allotted_date"]


        widgets = {
            "date_of_birth": forms.DateInput(attrs={"type": "date"}),

            "full_name": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Enter Full Name"
            }),

            "gender": forms.Select(attrs={
                "class": "form-select"
            }),

            "aadhaar_number": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Enter Aadhaar Number"
            }),

            "phone": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Enter Phone Number"
            }),

            "email": forms.EmailInput(attrs={
                "class": "form-control",
                "placeholder": "Enter Email"
            }),

            "nationality": forms.TextInput(attrs={
                "class": "form-control"
            }),

            "state": forms.TextInput(attrs={
                "class": "form-control"
            }),

            "district": forms.TextInput(attrs={
                "class": "form-control"
            }),

            "address": forms.Textarea(attrs={
                "class": "form-control",
                "rows": 3
            }),

            "pincode": forms.TextInput(attrs={
                "class": "form-control"
            }),

            "previous_qualification": forms.Select(attrs={
                "class": "form-select"
            }),

            "plus_two_percentage": forms.NumberInput(attrs={
                "class": "form-control"
            }),

            "father_name": forms.TextInput(attrs={
                "class": "form-control"
            }),

            "mother_name": forms.TextInput(attrs={
                "class": "form-control"
            }),

            "guardian_phone": forms.TextInput(attrs={
                "class": "form-control"
            }),

            "profile_photo": forms.ClearableFileInput(attrs={
                "class": "form-control"
            }),
        }


class RegisterForm(UserCreationForm):
    username = forms.CharField(label='UserName')
    password1 = forms.CharField(label='Password', widget=forms.PasswordInput)
    password2 = forms.CharField(label='Confirm Password', widget=forms.PasswordInput)

    class Meta:
        model = Register
        fields = ('username','password1','password2')






# staff




class StaffRegisterForm(forms.ModelForm):

    class Meta:
        model = UniversityStaff
        exclude = ["user", "is_approved","start_percentage","end_percentage"]

        widgets = {

            "full_name": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Enter Full Name"
            }),

            "phone": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Enter Phone Number"
            }),

            "email": forms.EmailInput(attrs={
                "class": "form-control",
                "placeholder": "Enter Email"
            }),

            "department": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Enter Department"
            }),

            "designation": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Enter Designation"
            }),

            "qualification": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Enter Qualification"
            }),
        }


# College
class CollegeRegisterForm(forms.ModelForm):

    class Meta:
        model = College

        exclude = [
            "user",
            "is_approved"
        ]





class StudentProfileForm(forms.ModelForm):

    class Meta:

        model = Student

        fields = [
            "full_name",
            "phone",
            "email",
            "gender",
            "date_of_birth",
            "nationality",
            "state",
            "district",
            "address",
            "pincode",
            "father_name",
            "mother_name",
            "guardian_phone",
            "profile_photo",
        ]







from django import forms
from UniversityApp.models import College

class CollegeProfileForm(forms.ModelForm):

    class Meta:

        model = College

        fields = [
            "college_name",
            "principal_name",
            "phone",
            "email",
            "address",
            "district",
            "state",
        ]





class StaffProfileForm(forms.ModelForm):

    class Meta:

        model = UniversityStaff

        fields = [
            "full_name",
            "phone",
            "email",
            "qualification",
        ]

        widgets = {

            "full_name": forms.TextInput(
                attrs={"class":"form-control"}
            ),

            "phone": forms.TextInput(
                attrs={"class":"form-control"}
            ),

            "email": forms.EmailInput(
                attrs={"class":"form-control"}
            ),

            "qualification": forms.TextInput(
                attrs={"class":"form-control"}
            ),

        }





class DepartmentForm(forms.ModelForm):

    class Meta:

        model = Department

        fields = [
            "department_name",
            "department_code",
            "description",
        ]

        widgets = {

            "department_name": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Enter Department Name"
                }
            ),

            "department_code": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Enter Department Code"
                }
            ),

            "description": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 4,
                    "placeholder": "Department Description"
                }
            ),

        }




class CourseForm(forms.ModelForm):
    class Meta:
        model = Course
        fields = [
            "department",
            "course_name",
            "course_code",
            "duration",
            "total_seats",
            "description",
        ]

        widgets = {
            "department": forms.Select(attrs={"class": "form-select"}),
            "course_name": forms.TextInput(attrs={"class": "form-control"}),
            "course_code": forms.TextInput(attrs={"class": "form-control"}),
            "duration": forms.TextInput(attrs={"class": "form-control"}),
            "total_seats": forms.NumberInput(attrs={"class": "form-control"}),
            "description": forms.Textarea(attrs={
                "class": "form-control",
                "rows": 3
            }),
        }






class EligibilityForm(forms.ModelForm):

    class Meta:
        model = Course

        fields = [
            "eligibility_percentage",
            "course_fee",
        ]

        widgets = {

            "eligibility_percentage": forms.NumberInput(
                attrs={
                    "class": "form-control",
                    "step": "0.01",
                    "min": "0",
                    "max": "100",
                    "placeholder": "Eligibility Percentage"
                }
            ),

            "course_fee": forms.NumberInput(
                attrs={
                    "class": "form-control",
                    "step": "0.01",
                    "min": "0",
                    "placeholder": "Course Fee (₹)"
                }
            ),

        }







from django import forms

from .models import (
    AdmissionApplication,
    College,
    Course,
)


class AdmissionApplicationForm(forms.Form):

    # =====================================================
    # COURSE SELECTION
    # =====================================================

    courses = forms.ModelMultipleChoiceField(
        queryset=Course.objects.none(),
        widget=forms.CheckboxSelectMultiple,
        required=True,
        label="Select Courses"
    )


    # =====================================================
    # PLUS TWO CERTIFICATE
    # PDF ONLY
    # =====================================================

    plus_two_certificate = forms.FileField(
        required=True,
        label="Plus Two Certificate",
        widget=forms.ClearableFileInput(
            attrs={
                "accept": ".pdf,application/pdf"
            }
        )
    )


    # =====================================================
    # AADHAAR DOCUMENT
    # PDF ONLY
    # =====================================================

    aadhaar_document = forms.FileField(
        required=True,
        label="Aadhaar Card",
        widget=forms.ClearableFileInput(
            attrs={
                "accept": ".pdf,application/pdf"
            }
        )
    )


    # =====================================================
    # INIT
    # =====================================================

    def __init__(self, *args, **kwargs):

        super().__init__(*args, **kwargs)

        self.fields["courses"].queryset = (
            Course.objects
            .select_related(
                "college",
                "department"
            )
            .filter(
                college__is_approved=True
            )
            .order_by(
                "college__college_name",
                "course_name"
            )
        )


    # =====================================================
    # COURSE VALIDATION
    # =====================================================

    def clean_courses(self):

        courses = self.cleaned_data.get(
            "courses"
        )

        if not courses:

            raise forms.ValidationError(
                "Please select at least one course."
            )


        if len(courses) > 15:

            raise forms.ValidationError(
                "Maximum 15 courses can be selected."
            )


        return courses


    # =====================================================
    # PLUS TWO CERTIFICATE VALIDATION
    # =====================================================

    def clean_plus_two_certificate(self):

        file = self.cleaned_data.get(
            "plus_two_certificate"
        )

        if not file:

            raise forms.ValidationError(
                "Please upload your Plus Two certificate."
            )


        # -------------------------------------------------
        # File extension
        # -------------------------------------------------

        if not file.name.lower().endswith(".pdf"):

            raise forms.ValidationError(
                "Only PDF files are allowed for Plus Two certificate."
            )


        # -------------------------------------------------
        # PDF signature
        # -------------------------------------------------

        file.seek(0)

        header = file.read(5)

        file.seek(0)

        if header != b"%PDF-":

            raise forms.ValidationError(
                "Invalid PDF file. Please upload a valid PDF."
            )


        # -------------------------------------------------
        # Maximum file size = 5 MB
        # -------------------------------------------------

        max_size = 5 * 1024 * 1024

        if file.size > max_size:

            raise forms.ValidationError(
                "Plus Two certificate must be less than 5 MB."
            )


        return file


    # =====================================================
    # AADHAAR VALIDATION
    # =====================================================

    def clean_aadhaar_document(self):

        file = self.cleaned_data.get(
            "aadhaar_document"
        )

        if not file:

            raise forms.ValidationError(
                "Please upload your Aadhaar document."
            )


        # -------------------------------------------------
        # File extension
        # -------------------------------------------------

        if not file.name.lower().endswith(".pdf"):

            raise forms.ValidationError(
                "Only PDF files are allowed for Aadhaar document."
            )


        # -------------------------------------------------
        # PDF signature
        # -------------------------------------------------

        file.seek(0)

        header = file.read(5)

        file.seek(0)

        if header != b"%PDF-":

            raise forms.ValidationError(
                "Invalid Aadhaar PDF file. Please upload a valid PDF."
            )


        # -------------------------------------------------
        # Maximum file size = 5 MB
        # -------------------------------------------------

        max_size = 5 * 1024 * 1024

        if file.size > max_size:

            raise forms.ValidationError(
                "Aadhaar document must be less than 5 MB."
            )


        return file


















from django import forms
from .models import (
    AdmissionApplication,
    College,
    Course
)


class AdmissionApplicationEditForm(forms.ModelForm):

    class Meta:

        model = AdmissionApplication

        fields = [
            "college",
            "course",
            "plus_two_certificate",
            "aadhaar_document",
        ]

        widgets = {

            "college": forms.Select(
                attrs={
                    "class": "form-select",
                    "id": "id_college"
                }
            ),

            "course": forms.Select(
                attrs={
                    "class": "form-select",
                    "id": "id_course"
                }
            ),

            "plus_two_certificate": forms.ClearableFileInput(
                attrs={
                    "class": "form-control"
                }
            ),

            "aadhaar_document": forms.ClearableFileInput(
                attrs={
                    "class": "form-control"
                }
            ),
        }

    def __init__(self, *args, **kwargs):

        super().__init__(*args, **kwargs)

        # College queryset
        self.fields["college"].queryset = College.objects.filter(
            is_approved=True
        )

        # Initially empty course queryset
        self.fields["course"].queryset = Course.objects.none()

        # ------------------------------------------------
        # POST request
        # ------------------------------------------------

        if "college" in self.data:

            try:

                college_id = int(
                    self.data.get("college")
                )

                self.fields["course"].queryset = Course.objects.filter(
                    college_id=college_id
                ).select_related(
                    "department"
                )

            except (ValueError, TypeError):

                self.fields["course"].queryset = Course.objects.none()

        # ------------------------------------------------
        # EDIT PAGE GET
        # ------------------------------------------------

        elif self.instance.pk:

            self.fields["course"].queryset = Course.objects.filter(
                college=self.instance.college
            ).select_related(
                "department"
            )

    # ----------------------------------------------------
    # VALIDATION
    # ----------------------------------------------------

    def clean(self):

        cleaned_data = super().clean()

        college = cleaned_data.get("college")
        course = cleaned_data.get("course")

        if college and course:

            # Course must belong to selected college
            if course.college_id != college.id:

                raise forms.ValidationError(
                    "The selected course does not belong to the selected college."
                )

            # Same student + same course duplicate check
            if self.instance.pk:

                duplicate = AdmissionApplication.objects.filter(
                    student=self.instance.student,
                    course=course
                ).exclude(
                    pk=self.instance.pk
                ).exists()

                if duplicate:

                    raise forms.ValidationError(
                        "You have already applied for this course."
                    )

        return cleaned_data
