from django.contrib.auth.models import AbstractUser
from django.db import models
from xhtml2pdf import default


class Register(AbstractUser):

    is_student = models.BooleanField(default=False)
    is_college = models.BooleanField(default=False)
    is_university_staff = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.username




class Student(models.Model):
    user = models.OneToOneField(
        Register,
        on_delete=models.CASCADE
    )

    GENDER_CHOICES = [
        ("Male", "Male"),
        ("Female", "Female"),
        ("Other", "Other"),
    ]

    QUALIFICATION_CHOICES = [
        ("HSE", "Higher Secondary (+2)"),
        ("CBSE", "CBSE (+2)"),
        ("ICSE", "ICSE (+2)"),
        ("VHSE", "VHSE"),
        ("Diploma", "Diploma"),
        ("Equivalent", "Equivalent Examination"),
    ]

    full_name = models.CharField(max_length=100)

    gender = models.CharField(
        max_length=10,
        choices=GENDER_CHOICES
    )

    date_of_birth = models.DateField()

    aadhaar_number = models.CharField(
        max_length=12,
        unique=True
    )

    phone = models.CharField(max_length=15)

    email = models.EmailField(unique=True)

    nationality = models.CharField(
        max_length=50,
        default="Indian"
    )

    state = models.CharField(max_length=100)

    district = models.CharField(max_length=100)

    address = models.TextField()

    pincode = models.CharField(max_length=6)

    previous_qualification = models.CharField(
        max_length=50,
        choices=QUALIFICATION_CHOICES
    )

    plus_two_percentage = models.DecimalField(
        max_digits=5,
        decimal_places=2
    )

    father_name = models.CharField(max_length=100)

    mother_name = models.CharField(max_length=100)

    guardian_phone = models.CharField(max_length=15)

    profile_photo = models.ImageField(
        upload_to="students/profile/",
        blank=True,
        null=True
    )

    # =====================================================
    # UNIVERSITY ALLOTMENT
    # =====================================================

    allotted_college = models.ForeignKey(
        "College",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="allotted_students"
    )

    allotted_course = models.ForeignKey(
        "Course",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="allotted_students"
    )

    allotted_date = models.DateTimeField(
        null=True,
        blank=True
    )

    # =====================================================
    # ADMISSION STATUS
    # =====================================================

    admission_status = models.CharField(
        max_length=30,
        default="Not Registered"
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):
        return self.full_name






class UniversityStaff(models.Model):

    user = models.OneToOneField(
        Register,
        on_delete=models.CASCADE
    )

    full_name = models.CharField(
        max_length=100
    )

    phone = models.CharField(
        max_length=15
    )

    email = models.EmailField(
        unique=True
    )

    qualification = models.CharField(
        max_length=100
    )

    # Admin approval
    is_approved = models.BooleanField(
        default=False
    )

    # ==========================================
    # ELIGIBILITY PERCENTAGE RANGE
    # ==========================================

    start_percentage = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        blank=True,
        null=True
    )


    end_percentage = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        blank=True,
        null=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):
        return self.full_name


# college

class College(models.Model):

    user = models.OneToOneField(
        Register,
        on_delete=models.CASCADE
    )


    college_name = models.CharField(
        max_length=150
    )


    principal_name = models.CharField(
        max_length=100
    )


    phone = models.CharField(
        max_length=15
    )


    email = models.EmailField(
        unique=True
    )


    address = models.TextField()


    district = models.CharField(
        max_length=100
    )


    state = models.CharField(
        max_length=100
    )




    # Admin approval
    is_approved = models.BooleanField(
        default=False
    )


    created_at = models.DateTimeField(
        auto_now_add=True
    )


    def __str__(self):
        return self.college_name



class Department(models.Model):

    department_name = models.CharField(max_length=100)

    department_code = models.CharField(max_length=20)

    description = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.department_name


class Course(models.Model):


    college = models.ForeignKey(
        College,
        on_delete=models.CASCADE,
        related_name="courses"
    )

    department = models.ForeignKey(
        Department,
        on_delete=models.CASCADE,
        related_name="courses"
    )

    course_name = models.CharField(max_length=200)

    course_code = models.CharField(
        max_length=50,
        unique=True
    )

    duration = models.CharField(max_length=100)

    # NEW FIELD
    course_fee = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0.00
    )

    total_seats = models.PositiveIntegerField()

    eligibility_percentage = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        blank=True,
        null=True
    )

    description = models.TextField(
        blank=True,
        null=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):
        return self.course_name



class AdmissionApplication(models.Model):

    STATUS_CHOICES = [
        ("Pending", "Pending"),
        ("College Verified", "College Verified"),
        ("University Verified", "University Verified"),
        ("Approved", "Approved"),
        ("Rejected", "Rejected"),
    ]

    PAYMENT_CHOICES = [
        ("Pending", "Pending"),
        ("Paid", "Paid"),
    ]


    # =====================================================
    # STUDENT & COURSE DETAILS
    # =====================================================

    student = models.ForeignKey(
        Student,
        on_delete=models.CASCADE,
        related_name="applications"
    )

    college = models.ForeignKey(
        College,
        on_delete=models.CASCADE,
        related_name="applications"
    )

    department = models.ForeignKey(
        Department,
        on_delete=models.CASCADE
    )

    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE
    )


    # =====================================================
    # DOCUMENTS
    # =====================================================

    plus_two_certificate = models.FileField(
        upload_to="applications/plus_two/",
        blank=True,
        null=True
    )

    aadhaar_document = models.FileField(
        upload_to="applications/aadhaar/",
        blank=True,
        null=True
    )


    # =====================================================
    # CERTIFICATE VERIFICATION
    # =====================================================

    # Total percentage extracted from uploaded
    # Plus Two certificate

    certificate_percentage = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        blank=True,
        null=True
    )

    # Compare certificate percentage with
    # Student.plus_two_percentage

    certificate_percentage_verified = models.BooleanField(
        default=False
    )


    # =====================================================
    # AADHAAR VERIFICATION
    # =====================================================

    # Aadhaar number extracted from uploaded
    # Aadhaar document

    aadhaar_number_extracted = models.CharField(
        max_length=12,
        blank=True,
        null=True
    )

    # Compare extracted Aadhaar with
    # Student.aadhaar_number

    aadhaar_verified = models.BooleanField(
        default=False
    )


    # =====================================================
    # OVERALL DOCUMENT VERIFICATION
    # =====================================================

    # True only when both certificate percentage
    # and Aadhaar are verified

    document_verified = models.BooleanField(
        default=False
    )

    university_application_verification = models.IntegerField(
        default=0
    )


    # =====================================================
    # APPLICATION DETAILS
    # =====================================================

    applied_date = models.DateTimeField(
        auto_now_add=True
    )


    # =====================================================
    # APPLICATION STATUS
    # =====================================================

    status = models.CharField(
        max_length=30,
        choices=STATUS_CHOICES,
        default="Pending"
    )


    # =====================================================
    # PAYMENT
    # =====================================================

    payment_status = models.CharField(
        max_length=20,
        choices=PAYMENT_CHOICES,
        default="Pending"
    )

    payment_date = models.DateTimeField(
        blank=True,
        null=True
    )


    # =====================================================
    # REMARKS
    # =====================================================

    college_remark = models.TextField(
        blank=True,
        null=True
    )

    staff_remark = models.TextField(
        blank=True,
        null=True
    )


    # =====================================================
    # META
    # =====================================================

    class Meta:

        unique_together = (
            "student",
            "course"
        )

        ordering = [
            "-applied_date"
        ]


    # =====================================================
    # STRING REPRESENTATION
    # =====================================================

    def __str__(self):

        return (
            f"{self.student.full_name} - "
            f"{self.course.course_name}"
        )







