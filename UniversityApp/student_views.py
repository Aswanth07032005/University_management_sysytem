from django.core.mail import send_mail
from django.utils import timezone

import render


from UniversityApp.forms import StudentForm, RegisterForm, StudentProfileForm, AdmissionApplicationForm
from UniversityProject import settings




def StudentRegisterView(request):

    form = StudentForm()
    register_form = RegisterForm()

    if request.method == 'POST':

        form = StudentForm(request.POST, request.FILES)
        register_form = RegisterForm(request.POST)

        if form.is_valid() and register_form.is_valid():

            form_Val = register_form.save(commit=False)
            form_Val.is_student = True
            form_Val.save()

            student_val = form.save(commit=False)


            student_val.user = form_Val

            student_val.save()

            return redirect('login_p')

    return render(
        request,
        'student/student_register.html',
        {
            "form": form,
            "register_form": register_form
        }
    )


def student_dashboard(request):
    return render(request,'student/student_dashboard.html')






def StudentProfileView(request):

    student = Student.objects.get(
        user=request.user
    )

    return render(
        request,
        "student/student_profile.html",
        {
            "student": student
        }
    )





def StudentProfileEditView(request):

    student = Student.objects.get(
        user=request.user
    )

    form = StudentProfileForm(
        request.POST or None,
        request.FILES or None,
        instance=student
    )

    if form.is_valid():

        form.save()

        messages.success(
            request,
            "Profile updated successfully."
        )

        return redirect("student_profile")

    return render(
        request,
        "student/student_profile_edit.html",
        {
            "form": form
        }
    )







from .models import (
    Student,
    Course,
    AdmissionApplication,
)

from django.shortcuts import render


def AdmissionView(request):

    return render(
        request,
        "student/admission.html"
    )








from .forms import AdmissionApplicationForm

def admission_apply(request):

    # =====================================================
    # GET CURRENT STUDENT
    # =====================================================

    student = get_object_or_404(
        Student,
        user=request.user
    )

    # =====================================================
    # POST
    # =====================================================

    if request.method == "POST":

        form = AdmissionApplicationForm(
            request.POST,
            request.FILES
        )

        if form.is_valid():

            courses = form.cleaned_data["courses"]

            plus_two = form.cleaned_data[
                "plus_two_certificate"
            ]

            saved = 0
            duplicate = 0
            total_amount = 0

            application_ids = []

            # =================================================
            # APPLY FOR EACH COURSE
            # =================================================

            for course in courses:

                application, created = (
                    AdmissionApplication.objects.get_or_create(

                        student=student,

                        course=course,

                        defaults={
                            "college": course.college,
                            "department": course.department,
                            "plus_two_certificate": plus_two,
                            "status": "Pending",
                        }
                    )
                )

                # =================================================
                # NEW APPLICATION
                # =================================================

                if created:

                    saved += 1

                    total_amount += course.course_fee

                    application_ids.append(
                        application.id
                    )

                # =================================================
                # DUPLICATE APPLICATION
                # =================================================

                else:

                    duplicate += 1

                    application_ids.append(
                        application.id
                    )

            # =====================================================
            # NO NEW APPLICATION
            # =====================================================

            if saved == 0:

                messages.warning(
                    request,
                    "Selected courses were already applied."
                )

                return redirect(
                    "admission_apply"
                )

            # =====================================================
            # PAYMENT
            # =====================================================

            request.session["payment_amount"] = float(
                total_amount
            )

            request.session["application_ids"] = (
                application_ids
            )

            # =====================================================
            # SUCCESS MESSAGE
            # =====================================================

            messages.success(
                request,
                f"{saved} application(s) submitted successfully."
            )

            if duplicate:

                messages.warning(
                    request,
                    f"{duplicate} duplicate application(s) skipped."
                )

            # =====================================================
            # REDIRECT TO PAYMENT
            # =====================================================

            return redirect(
                "payment"
            )

    # =====================================================
    # GET REQUEST
    # =====================================================

    else:

        form = AdmissionApplicationForm()

    # =====================================================
    # RENDER
    # =====================================================

    return render(
        request,
        "student/admission_apply.html",
        {
            "form": form,
        }
    )



from django.utils import timezone
from django.core.mail import send_mail




def payment(request):

    student = Student.objects.get(
        user=request.user
    )

    amount = request.session.get(
        "payment_amount",
        0
    )

    application_ids = request.session.get(
        "application_ids",
        []
    )

    applications = AdmissionApplication.objects.filter(
        id__in=application_ids
    ).select_related(
        "college",
        "department",
        "course"
    )

    if request.method == "POST":

        applications.update(
            payment_status="Paid",
            payment_date=timezone.now()
        )

        # Application IDs
        application_numbers = list(
            applications.values_list(
                "id",
                flat=True
            )
        )

        # Save for success page
        request.session["success_payment_amount"] = amount

        request.session["success_application_numbers"] = (
            application_numbers
        )

        # Email
        subject = "Admission Payment Successful"

        message = f"""
Dear {student.full_name},

Your admission payment has been completed successfully.

Payment Amount: ₹{amount}

Application ID(s):
{", ".join(map(str, application_numbers))}

Your admission application has been successfully submitted.

You can log in to the University Admission Portal
to check your application status.

Thank you.

University Admission Office
"""

        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            [student.email],
            fail_silently=False
        )

        # Clear payment session
        request.session.pop(
            "payment_amount",
            None
        )

        request.session.pop(
            "application_ids",
            None
        )

        return redirect(
            "application__success"
        )

    return render(
        request,
        "student/payment.html",
        {
            "amount": amount,
            "applications": applications,
        }
    )


def Application_success(request):

    amount = request.session.get(
        "success_payment_amount",
        0
    )

    application_numbers = request.session.get(
        "success_application_numbers",
        []
    )

    return render(
        request,
        "student/application_success.html",
        {
            "amount": amount,
            "application_numbers": application_numbers,
        }
    )





from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from UniversityApp.models import Student, AdmissionApplication


@login_required(login_url="StudentLogin")
def StudentApplicationsView(request):

    student = Student.objects.get(
        user=request.user
    )

    applications = (
        AdmissionApplication.objects.filter(
            student=student
        )
        .select_related(
            "college",
            "department",
            "course"
        )
        .order_by("-applied_date")
    )

    return render(
        request,
        "student/student_applications.html",
        {
            "student": student,
            "applications": applications,
        }
    )


















from datetime import datetime
from io import BytesIO
import os
import logging

from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.conf import settings

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import mm
from reportlab.platypus import (
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
    Image,
)

from .models import AdmissionApplication, Student

logger = logging.getLogger(__name__)


# ============================================================
# MMT UNIVERSITY BRAND
# ============================================================

NAVY = colors.HexColor("#092B55")
NAVY_DARK = colors.HexColor("#061E3D")
BLUE = colors.HexColor("#1769AA")
GOLD = colors.HexColor("#D9A441")

INK = colors.HexColor("#172B4D")
INK_SOFT = colors.HexColor("#61758F")

WHITE = colors.white
LIGHT_BLUE = colors.HexColor("#F2F6FB")
LIGHT_GOLD = colors.HexColor("#FBF5E8")
RULE = colors.HexColor("#D8E2EE")

GREEN = colors.HexColor("#18864B")
GREEN_BG = colors.HexColor("#EAF7EF")

RED = colors.HexColor("#B52B2B")
RED_BG = colors.HexColor("#FCEBEC")

ORANGE = colors.HexColor("#B97810")
ORANGE_BG = colors.HexColor("#FFF5E1")

UNIVERSITY_NAME = "MMT UNIVERSITY"
UNIVERSITY_TAGLINE = "Office of Admissions"
DOCUMENT_TITLE = "STUDENT ADMISSION REPORT"

# Set an absolute path if you have a real logo file, e.g.:
# LOGO_PATH = os.path.join(settings.BASE_DIR, "static", "images", "mmt_logo.png")
LOGO_PATH = None

STATUS_COLORS = {
    "Approved": (GREEN, GREEN_BG),
    "Rejected": (RED, RED_BG),
    "Pending": (ORANGE, ORANGE_BG),
}


# ============================================================
# HELPERS
# ============================================================

def safe_value(value):
    """Return a display-safe string, defaulting to an em dash."""
    if value is None or value == "":
        return "—"
    return str(value)


def get_status_colors(status):
    status = str(status or "Pending").strip()
    return STATUS_COLORS.get(status, STATUS_COLORS["Pending"])


def get_profile_image(student):
    """Return a valid, existing image path for the student's photo, or None."""
    try:
        if not getattr(student, "profile_photo", None):
            return None
        image_path = student.profile_photo.path
        if not os.path.exists(image_path):
            return None
        return image_path
    except Exception as exc:
        logger.warning("Could not resolve profile photo for student %s: %s", student.id, exc)
        return None


def make_field(label, value, style):
    value = safe_value(value)
    return Paragraph(
        f"""
        <font color="#61758F" size="6.5"><b>{label.upper()}</b></font>
        <br/>
        <font color="#172B4D">{value}</font>
        """,
        style,
    )


# ============================================================
# UNIVERSITY SEAL
# ============================================================

def draw_university_seal(c, x, y, radius=10 * mm):
    c.saveState()

    c.setFillColor(NAVY_DARK)
    c.setStrokeColor(GOLD)
    c.setLineWidth(1.5)
    c.circle(x, y, radius, stroke=1, fill=1)

    c.setStrokeColor(colors.HexColor("#7EA4CA"))
    c.setLineWidth(0.6)
    c.circle(x, y, radius * 0.78, stroke=1, fill=0)

    c.setFillColor(WHITE)
    c.setFont("Helvetica-Bold", 9)
    c.drawCentredString(x, y - 3, "MMT")

    c.setFillColor(GOLD)
    c.setFont("Helvetica-Bold", 7)
    c.drawCentredString(x, y + 5, "\u2605")

    c.restoreState()


# ============================================================
# MASTHEAD / FOOTER
# ============================================================

def draw_masthead(c, doc, student):
    width, height = A4
    band_height = 39 * mm

    c.saveState()

    c.setFillColor(NAVY_DARK)
    c.rect(0, height - band_height, width, band_height, fill=1, stroke=0)

    c.setFillColor(GOLD)
    c.rect(0, height - band_height - 1.5 * mm, width, 1.5 * mm, fill=1, stroke=0)

    if LOGO_PATH and os.path.exists(LOGO_PATH):
        try:
            c.drawImage(
                LOGO_PATH,
                17 * mm,
                height - 30 * mm,
                width=20 * mm,
                height=20 * mm,
                preserveAspectRatio=True,
                mask="auto",
            )
        except Exception as exc:
            logger.warning("Failed to draw logo, falling back to seal: %s", exc)
            draw_university_seal(c, 27 * mm, height - 20 * mm)
    else:
        draw_university_seal(c, 27 * mm, height - 20 * mm)

    c.setFillColor(GOLD)
    c.setFont("Helvetica-Bold", 8.5)
    c.drawString(42 * mm, height - 14 * mm, UNIVERSITY_NAME)

    c.setFillColor(WHITE)
    c.setFont("Helvetica-Bold", 15)
    c.drawString(42 * mm, height - 21 * mm, DOCUMENT_TITLE)

    c.setFillColor(colors.HexColor("#B9CEE6"))
    c.setFont("Helvetica", 8)
    c.drawString(42 * mm, height - 27 * mm, UNIVERSITY_TAGLINE)

    c.setFont("Helvetica", 7.5)
    c.setFillColor(colors.HexColor("#C4D5E8"))

    generated = datetime.now().strftime("%d %b %Y  |  %I:%M %p")
    c.drawRightString(width - 18 * mm, height - 14 * mm, f"Generated: {generated}")
    c.drawRightString(
        width - 18 * mm, height - 19 * mm, f"Applicant: {safe_value(student.full_name)}"
    )
    c.drawRightString(
        width - 18 * mm, height - 24 * mm, f"Student ID: MMT-{student.id:05d}"
    )

    c.restoreState()


def draw_footer(c, doc):
    width, _ = A4
    c.saveState()

    c.setStrokeColor(RULE)
    c.setLineWidth(0.6)
    c.line(18 * mm, 16 * mm, width - 18 * mm, 16 * mm)

    c.setFont("Helvetica", 7)
    c.setFillColor(INK_SOFT)
    c.drawString(18 * mm, 11 * mm, "MMT University \u2022 Office of Admissions")
    c.drawRightString(width - 18 * mm, 11 * mm, f"Page {doc.page}")

    c.restoreState()


def later_page_header(canvas, document, student):
    width, height = A4
    canvas.saveState()

    canvas.setFillColor(NAVY_DARK)
    canvas.rect(0, height - 13 * mm, width, 13 * mm, fill=1, stroke=0)

    canvas.setFillColor(WHITE)
    canvas.setFont("Helvetica-Bold", 9)
    canvas.drawString(18 * mm, height - 8.5 * mm, f"{UNIVERSITY_NAME} \u2014 {DOCUMENT_TITLE}")

    canvas.restoreState()
    draw_footer(canvas, document)


# ============================================================
# STYLES
# ============================================================

def build_styles():
    return {
        "section": ParagraphStyle(
            "section", fontName="Helvetica-Bold", fontSize=11,
            textColor=NAVY, spaceBefore=12, spaceAfter=7,
        ),
        "field": ParagraphStyle(
            "field", fontName="Helvetica", fontSize=8.8, textColor=INK, leading=12,
        ),
        "small": ParagraphStyle(
            "small", fontName="Helvetica", fontSize=7.8, textColor=INK_SOFT, leading=10,
        ),
        "table": ParagraphStyle(
            "table", fontName="Helvetica", fontSize=7.8, textColor=INK, leading=10,
        ),
        "table_header": ParagraphStyle(
            "table_header", fontName="Helvetica-Bold", fontSize=7,
            textColor=WHITE, leading=9,
        ),
        "status": ParagraphStyle(
            "status", fontName="Helvetica-Bold", fontSize=7.5, leading=9,
        ),
        "declaration": ParagraphStyle(
            "declaration", fontName="Helvetica", fontSize=7.8,
            textColor=INK_SOFT, leading=11,
        ),
        "photo_placeholder": ParagraphStyle(
            "photo_placeholder", fontName="Helvetica-Bold", fontSize=8,
            textColor=INK_SOFT, alignment=1,
        ),
    }


# ============================================================
# SECTION BUILDERS
# ============================================================

def build_profile_section(student, styles):
    """Applicant info header + photo/details row."""
    story = [Paragraph("APPLICANT INFORMATION", styles["section"])]

    profile_path = get_profile_image(student)
    if profile_path:
        try:
            profile_image = Image(profile_path, width=30 * mm, height=36 * mm)
            profile_image.hAlign = "CENTER"
        except Exception as exc:
            logger.warning("Failed to embed profile image for student %s: %s", student.id, exc)
            profile_image = _photo_placeholder(styles)
    else:
        profile_image = _photo_placeholder(styles)

    student_fields = [
        ("Full Name", student.full_name),
        ("Student ID", f"MMT-{student.id:05d}"),
        ("Email", student.email),
        ("Phone", student.phone),
        ("Date of Birth", student.date_of_birth),
        ("Gender", student.gender),
        ("Nationality", student.nationality),
        ("Previous Qualification", student.previous_qualification),
        (
            "Plus Two Percentage",
            f"{student.plus_two_percentage}%" if student.plus_two_percentage is not None else None,
        ),
    ]

    field_rows = []
    for i in range(0, len(student_fields), 2):
        left = make_field(*student_fields[i], styles["field"])
        right = (
            make_field(*student_fields[i + 1], styles["field"])
            if i + 1 < len(student_fields)
            else ""
        )
        field_rows.append([left, right])

    details_table = Table(field_rows, colWidths=[43 * mm, 43 * mm])
    details_table.setStyle(TableStyle([
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
        ("LINEBELOW", (0, 0), (-1, -1), 0.35, RULE),
    ]))

    profile_table = Table(
        [[details_table, profile_image]],
        colWidths=[88 * mm, 34 * mm],
    )
    profile_table.setStyle(TableStyle([
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 0),
        ("RIGHTPADDING", (0, 0), (-1, -1), 0),
        ("TOPPADDING", (0, 0), (-1, -1), 2),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 2),
    ]))

    story.append(profile_table)
    story.append(Spacer(1, 3 * mm))
    return story


def _photo_placeholder(styles):
    placeholder = Table(
        [[Paragraph("<b>PHOTO</b>", styles["photo_placeholder"])]],
        colWidths=[30 * mm],
        rowHeights=[36 * mm],
    )
    placeholder.setStyle(TableStyle([
        ("BOX", (0, 0), (-1, -1), 0.7, RULE),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("BACKGROUND", (0, 0), (-1, -1), LIGHT_BLUE),
    ]))
    return placeholder


def build_two_col_info_table(rows, styles, background=None):
    """Generic 2-column labeled-field table used for address / parent info."""
    data = [
        [make_field(l1, v1, styles["field"]), make_field(l2, v2, styles["field"])]
        for (l1, v1), (l2, v2) in rows
    ]
    table = Table(data, colWidths=[85 * mm, 85 * mm])
    style_cmds = [
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("BOX", (0, 0), (-1, -1), 0.5, RULE),
        ("INNERGRID", (0, 0), (-1, -1), 0.3, RULE),
        ("TOPPADDING", (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 7),
    ]
    if background:
        style_cmds.append(("BACKGROUND", (0, 0), (-1, -1), background))
    table.setStyle(TableStyle(style_cmds))
    return table


def build_address_section(student, styles):
    story = [Paragraph("ADDRESS", styles["section"])]
    rows = [
        (("Address", student.address), ("District", student.district)),
        (("State", student.state), ("Pincode", student.pincode)),
    ]
    story.append(build_two_col_info_table(rows, styles, background=LIGHT_BLUE))
    return story


def build_parent_section(student, styles):
    story = [Paragraph("PARENT / GUARDIAN INFORMATION", styles["section"])]
    rows = [
        (("Father Name", student.father_name), ("Mother Name", student.mother_name)),
        (("Guardian Phone", student.guardian_phone), ("Aadhaar Number", student.aadhaar_number)),
    ]
    story.append(build_two_col_info_table(rows, styles))
    return story


def build_application_history_section(applications, styles):
    story = [Paragraph("APPLICATION HISTORY", styles["section"])]

    header = [
        Paragraph(text, styles["table_header"])
        for text in ("APPLICATION", "COLLEGE", "DEPARTMENT", "COURSE", "APPLIED", "STATUS")
    ]
    table_data = [header]
    status_commands = []

    if applications:
        for index, app in enumerate(applications, start=1):
            status = str(getattr(app, "status", None) or "Pending")
            fg, bg = get_status_colors(status)

            status_style = ParagraphStyle(
                f"status_{index}", parent=styles["status"], textColor=fg, alignment=1,
            )
            status_cell = Paragraph(status.upper(), status_style)
            status_commands.append(("BACKGROUND", (5, index), (5, index), bg))

            applied_date = (
                app.applied_date.strftime("%d %b %Y") if app.applied_date else "—"
            )

            table_data.append([
                Paragraph(f"MMT-{app.id:05d}", styles["table"]),
                Paragraph(safe_value(app.college), styles["table"]),
                Paragraph(safe_value(app.department), styles["table"]),
                Paragraph(safe_value(app.course), styles["table"]),
                Paragraph(applied_date, styles["table"]),
                status_cell,
            ])
    else:
        table_data.append([
            Paragraph("No applications found.", styles["table"]), "", "", "", "", "",
        ])

    application_table = Table(
        table_data,
        colWidths=[23 * mm, 34 * mm, 31 * mm, 34 * mm, 23 * mm, 25 * mm],
        repeatRows=1,
    )

    application_style = [
        ("BACKGROUND", (0, 0), (-1, 0), NAVY_DARK),
        ("TEXTCOLOR", (0, 0), (-1, 0), WHITE),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("TOPPADDING", (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
        ("LEFTPADDING", (0, 0), (-1, -1), 5),
        ("RIGHTPADDING", (0, 0), (-1, -1), 5),
        ("LINEBELOW", (0, 1), (-1, -1), 0.35, RULE),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [WHITE, LIGHT_BLUE]),
    ]
    application_style.extend(status_commands)
    application_table.setStyle(TableStyle(application_style))

    story.append(application_table)
    return story


def build_summary_section(applications, styles):
    story = [Spacer(1, 4 * mm)]

    total = applications.count()
    approved = applications.filter(status="Approved").count()
    pending = applications.filter(status="Pending").count()
    rejected = applications.filter(status="Rejected").count()

    def stat_cell(value, label):
        return Paragraph(
            f"<b>{value}</b><br/><font size='6.5'>{label}</font>", styles["table"]
        )

    summary_table = Table(
        [[
            stat_cell(total, "TOTAL APPLICATIONS"),
            stat_cell(approved, "APPROVED"),
            stat_cell(pending, "PENDING"),
            stat_cell(rejected, "REJECTED"),
        ]],
        colWidths=[42.5 * mm] * 4,
    )
    summary_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), LIGHT_BLUE),
        ("BOX", (0, 0), (-1, -1), 0.5, RULE),
        ("INNERGRID", (0, 0), (-1, -1), 0.4, RULE),
        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("TOPPADDING", (0, 0), (-1, -1), 7),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 7),
    ]))

    story.append(summary_table)
    return story


def build_declaration_section(styles):
    story = [Paragraph("DECLARATION", styles["section"])]

    declaration_text = (
        "This document is electronically generated by the MMT University "
        "Admission Management System. The information displayed in this "
        "report is based on the applicant details and admission applications "
        "available in the university system at the time of generation. "
        "This report is intended for admission-related reference and "
        "verification purposes."
    )

    declaration_table = Table(
        [[Paragraph(declaration_text, styles["declaration"])]],
        colWidths=[170 * mm],
    )
    declaration_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), LIGHT_GOLD),
        ("BOX", (0, 0), (-1, -1), 0.5, colors.HexColor("#E8D39B")),
        ("LEFTPADDING", (0, 0), (-1, -1), 8),
        ("RIGHTPADDING", (0, 0), (-1, -1), 8),
        ("TOPPADDING", (0, 0), (-1, -1), 7),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 7),
    ]))

    story.append(declaration_table)
    return story


# ============================================================
# VIEW
# ============================================================

@login_required(login_url="StudentLogin")
def ApplicationReportView(request):

    student = get_object_or_404(
        Student.objects.select_related("user"),
        user=request.user,
    )

    applications = (
        AdmissionApplication.objects
        .filter(student=student)
        .select_related("college", "department", "course")
        .order_by("-applied_date")
    )

    styles = build_styles()

    story = []
    story += build_profile_section(student, styles)
    story += build_address_section(student, styles)
    story += build_parent_section(student, styles)
    story += build_application_history_section(applications, styles)
    story += build_summary_section(applications, styles)
    story += build_declaration_section(styles)

    buffer = BytesIO()

    try:
        doc = SimpleDocTemplate(
            buffer,
            pagesize=A4,
            topMargin=46 * mm,
            bottomMargin=23 * mm,
            leftMargin=18 * mm,
            rightMargin=18 * mm,
            title="MMT University Student Admission Report",
            author="MMT University Admission Management System",
            subject="Student Admission Report",
        )

        def first_page(canvas, document):
            draw_masthead(canvas, document, student)
            draw_footer(canvas, document)

        def later_pages(canvas, document):
            later_page_header(canvas, document, student)

        doc.build(story, onFirstPage=first_page, onLaterPages=later_pages)

    except Exception:
        logger.exception(
            "Failed to generate admission report PDF for student %s", student.id
        )
        buffer.close()
        return HttpResponse(
            "Sorry, we couldn't generate your admission report right now. "
            "Please try again later.",
            status=500,
            content_type="text/plain",
        )

    safe_name = (student.full_name or "student").strip().replace(" ", "_").lower()

    response = HttpResponse(buffer.getvalue(), content_type="application/pdf")
    response["Content-Disposition"] = (
        f'attachment; filename="MMT_University_Admission_Report_{safe_name}.pdf"'
    )

    buffer.close()
    return response













from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import (
    render,
    redirect,
    get_object_or_404
)

from .models import (
    Student,
    AdmissionApplication
)

from .forms import AdmissionApplicationEditForm


@login_required(login_url="StudentLogin")
def ApplicationEditView(request, pk):

    student = get_object_or_404(
        Student,
        user=request.user
    )

    application = get_object_or_404(
        AdmissionApplication,
        pk=pk,
        student=student
    )

    # Only Pending applications can be edited
    if application.status != "Pending":

        messages.error(
            request,
            "Verified applications cannot be edited."
        )

        return redirect(
            "student_applications"
        )

    # ------------------------------------------------
    # FORM
    # ------------------------------------------------

    if request.method == "POST":

        form = AdmissionApplicationEditForm(
            request.POST,
            request.FILES,
            instance=application
        )

        if form.is_valid():

            updated_application = form.save(
                commit=False
            )

            # Department automatically comes from Course
            updated_application.department = (
                updated_application.course.department
            )

            updated_application.save()

            messages.success(
                request,
                "Application updated successfully."
            )

            return redirect(
                "student_applications"
            )

    else:

        form = AdmissionApplicationEditForm(
            instance=application
        )

    return render(
        request,
        "student/application_edit.html",
        {
            "form": form,
            "application": application,
        }
    )






@login_required(login_url="StudentLogin")
def ApplicationDeleteView(request, pk):

    student = get_object_or_404(
        Student,
        user=request.user
    )

    application = get_object_or_404(
        AdmissionApplication,
        pk=pk,
        student=student
    )

    # Only Pending application can be deleted
    if application.status != "Pending":

        messages.error(
            request,
            "Verified applications cannot be deleted."
        )

        return redirect(
            "student_applications"
        )

    if request.method == "POST":

        application.delete()

        messages.success(
            request,
            "Application deleted successfully."
        )

        return redirect(
            "student_applications"
        )

    return render(
        request,
        "student/application_delete.html",
        {
            "application": application,
        }
    )


# AJAX - Load courses according to college
@login_required(login_url="StudentLogin")
def LoadCollegeCourses(request):

    college_id = request.GET.get("college_id")

    if not college_id:

        return JsonResponse(
            {
                "courses": []
            }
        )

    courses = Course.objects.filter(
        college_id=college_id
    ).select_related(
        "department"
    )

    data = []

    for course in courses:

        data.append(
            {
                "id": course.id,
                "name": course.course_name,
                "code": course.course_code,
                "department": course.department.department_name,
            }
        )

    return JsonResponse(
        {
            "courses": data
        }
    )










from django.http import JsonResponse

from .models import Course


def CoursesByCollegeView(request):

    college_id = request.GET.get("college_id")

    if not college_id:

        return JsonResponse(
            [],
            safe=False
        )

    courses = Course.objects.filter(
        college_id=college_id
    ).select_related(
        "department"
    )

    data = []

    for course in courses:

        data.append({

            "id": course.id,

            "course_name": course.course_name,

            "department_name": (
                course.department.department_name
            ),

            "course_code": course.course_code,

            "duration": course.duration,

            "course_fee": str(
                course.course_fee
            ),

            "total_seats": course.total_seats,

        })

    return JsonResponse(
        data,
        safe=False
    )


















from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404

from .models import (
    Student,
    AdmissionApplication,
)

@login_required(login_url="StudentLogin")
def AdmissionStatusView(request):

    # =====================================================
    # GET LOGGED-IN STUDENT
    # =====================================================

    student = get_object_or_404(
        Student,
        user=request.user
    )

    # =====================================================
    # GET STUDENT APPLICATIONS
    # =====================================================

    applications = (
        AdmissionApplication.objects
        .filter(
            student=student
        )
        .select_related(
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

        "student": student,

        "applications": applications,

        # ---------------------------------------------
        # ALLOTMENT DETAILS
        # ---------------------------------------------

        "allotted_college":
            student.allotted_college,

        "allotted_course":
            student.allotted_course,

        "allotted_date":
            student.allotted_date,
    }

    # =====================================================
    # RENDER
    # =====================================================

    return render(
        request,
        "student/admission_status.html",
        context
    )