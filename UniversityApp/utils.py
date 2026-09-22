
import re
import pdfplumber


# =========================================================
# QUALIFICATION KEYWORDS
# =========================================================

QUALIFICATION_KEYWORDS = {
    "hse": [
        "hse",
        "higher secondary",
        "higher secondary (+2)",
        "higher secondary examination",
        "plus two",
        "+2",
    ]
}


# =========================================================
# NORMALIZE TEXT
# =========================================================

def normalize_text(value):

    if not value:
        return ""

    value = str(value).lower().strip()

    value = re.sub(
        r"\s+",
        " ",
        value
    )

    return value.strip()


# =========================================================
# NORMALIZE NAME
# =========================================================

def normalize_name(value):

    if not value:
        return ""

    value = str(value).lower().strip()

    # -----------------------------------------------------
    # Remove dots
    # M.M -> MM
    # -----------------------------------------------------

    value = value.replace(".", "")

    # -----------------------------------------------------
    # Remove special characters
    # -----------------------------------------------------

    value = re.sub(
        r"[^a-z0-9\s]",
        " ",
        value
    )

    # -----------------------------------------------------
    # Remove extra spaces
    # -----------------------------------------------------

    value = re.sub(
        r"\s+",
        " ",
        value
    )

    return value.strip()


# =========================================================
# NAME MATCH
# =========================================================

def name_matches(
    registered_name,
    certificate_name
):

    if not registered_name:
        return False

    if not certificate_name:
        return False

    registered = normalize_name(
        registered_name
    )

    certificate = normalize_name(
        certificate_name
    )

    # -----------------------------------------------------
    # EXACT MATCH
    # -----------------------------------------------------

    if registered == certificate:

        return True


    # -----------------------------------------------------
    # WORD MATCH
    # -----------------------------------------------------

    registered_parts = registered.split()
    certificate_parts = certificate.split()

    if not registered_parts:
        return False

    if not certificate_parts:
        return False


    if (
        sorted(registered_parts)
        ==
        sorted(certificate_parts)
    ):

        return True


    # -----------------------------------------------------
    # JOINED MATCH
    #
    # Aswanth M M
    # Aswanth MM
    # -----------------------------------------------------

    registered_joined = "".join(
        registered_parts
    )

    certificate_joined = "".join(
        certificate_parts
    )

    if (
        registered_joined
        ==
        certificate_joined
    ):

        return True


    return False


# =========================================================
# QUALIFICATION MATCH
# =========================================================

def qualification_matches(
    registered_qualification,
    certificate_qualification
):

    if not registered_qualification:
        return False

    if not certificate_qualification:
        return False

    registered = normalize_text(
        registered_qualification
    )

    certificate = normalize_text(
        certificate_qualification
    )


    # -----------------------------------------------------
    # HSE / PLUS TWO
    # -----------------------------------------------------

    hse_keywords = (
        QUALIFICATION_KEYWORDS["hse"]
    )


    registered_is_hse = any(
        keyword in registered
        for keyword in hse_keywords
    )


    certificate_is_hse = any(
        keyword in certificate
        for keyword in hse_keywords
    )


    if (
        registered_is_hse
        and
        certificate_is_hse
    ):

        return True


    # -----------------------------------------------------
    # EXACT MATCH
    # -----------------------------------------------------

    if registered == certificate:

        return True


    return False


# =========================================================
# EXTRACT VALUE AFTER LABEL
# =========================================================

def extract_value_after_label(
    text,
    label_pattern,
    stop_patterns=None
):

    if not text:
        return None


    # -----------------------------------------------------
    # Normalize line endings
    # -----------------------------------------------------

    text = text.replace(
        "\r\n",
        "\n"
    )

    text = text.replace(
        "\r",
        "\n"
    )


    # -----------------------------------------------------
    # FIRST:
    # Same-line extraction
    #
    # Student Name : Aswanth M M
    #
    # -----------------------------------------------------

    pattern = (
        label_pattern
        +
        r"\s*[:\-]\s*([^\n]+)"
    )


    match = re.search(
        pattern,
        text,
        re.IGNORECASE
    )


    if match:

        value = (
            match
            .group(1)
            .strip()
        )

        if value:

            return value


    # -----------------------------------------------------
    # SECOND:
    # Next-line extraction
    #
    # Student Name :
    #
    # Aswanth M M
    #
    # -----------------------------------------------------

    pattern = (
        label_pattern
        +
        r"\s*[:\-]?\s*\n\s*([^\n]+)"
    )


    match = re.search(
        pattern,
        text,
        re.IGNORECASE
    )


    if match:

        value = (
            match
            .group(1)
            .strip()
        )

        if value:

            return value


    return None


# =========================================================
# EXTRACT STUDENT NAME
# =========================================================

def extract_student_name(text):

    if not text:
        return None


    # -----------------------------------------------------
    # Try Student Name
    # -----------------------------------------------------

    name = extract_value_after_label(
        text,
        r"Student\s+Name"
    )


    if name:

        return name


    # -----------------------------------------------------
    # Try StudentName
    # -----------------------------------------------------

    name = extract_value_after_label(
        text,
        r"StudentName"
    )


    if name:

        return name


    # -----------------------------------------------------
    # Try Name
    # -----------------------------------------------------

    name = extract_value_after_label(
        text,
        r"Name"
    )


    if name:

        return name


    return None


# =========================================================
# EXTRACT QUALIFICATION
# =========================================================

def extract_qualification(text):

    if not text:
        return None


    qualification = extract_value_after_label(
        text,
        r"Qualification"
    )


    if qualification:

        return qualification


    return None


# =========================================================
# EXTRACT PERCENTAGE
# =========================================================

def extract_percentage(text):

    if not text:
        return None


    # -----------------------------------------------------
    # TOTAL PERCENTAGE: 85.60%
    # -----------------------------------------------------

    percentage_match = re.search(
        r"TOTAL\s+PERCENTAGE"
        r"\s*[:\-]?\s*"
        r"([\d]+(?:\.\d+)?)"
        r"\s*%",
        text,
        re.IGNORECASE
    )


    if percentage_match:

        return float(
            percentage_match.group(1)
        )


    # -----------------------------------------------------
    # TOTAL PERCENTAGE 85.60%
    # -----------------------------------------------------

    percentage_match = re.search(
        r"TOTAL\s+PERCENTAGE"
        r"\s+"
        r"([\d]+(?:\.\d+)?)"
        r"\s*%",
        text,
        re.IGNORECASE
    )


    if percentage_match:

        return float(
            percentage_match.group(1)
        )


    return None


# =========================================================
# EXTRACT DETAILS FROM CERTIFICATE
# =========================================================

def extract_certificate_details(file_obj):

    try:

        # =================================================
        # RESET FILE
        # =================================================

        file_obj.seek(0)


        # =================================================
        # OPEN PDF
        # =================================================

        with pdfplumber.open(file_obj) as pdf:

            text_parts = []


            for page_number, page in enumerate(
                pdf.pages,
                start=1
            ):

                # -----------------------------------------
                # Normal text extraction
                # -----------------------------------------

                page_text = (
                    page.extract_text(
                        x_tolerance=3,
                        y_tolerance=3
                    )
                )


                if page_text:

                    text_parts.append(
                        page_text
                    )


        # =================================================
        # JOIN TEXT
        # =================================================

        text = "\n".join(
            text_parts
        )


        # =================================================
        # DEBUG RAW TEXT
        # =================================================

        print(
            "\n========================================"
        )

        print(
            "RAW PDF TEXT"
        )

        print(
            "========================================"
        )

        print(text)

        print(
            "========================================"
        )


        # =================================================
        # EXTRACT NAME
        # =================================================

        certificate_name = (
            extract_student_name(
                text
            )
        )


        # =================================================
        # EXTRACT QUALIFICATION
        # =================================================

        certificate_qualification = (
            extract_qualification(
                text
            )
        )


        # =================================================
        # EXTRACT PERCENTAGE
        # =================================================

        certificate_percentage = (
            extract_percentage(
                text
            )
        )


        # =================================================
        # CLEAN NAME
        # =================================================

        if certificate_name:

            certificate_name = re.sub(
                r"\s+",
                " ",
                certificate_name
            ).strip()


        # =================================================
        # CLEAN QUALIFICATION
        # =================================================

        if certificate_qualification:

            certificate_qualification = re.sub(
                r"\s+",
                " ",
                certificate_qualification
            ).strip()


        # =================================================
        # DEBUG EXTRACTED VALUES
        # =================================================

        print(
            "\n========== EXTRACTED DETAILS =========="
        )

        print(
            "Certificate Name:",
            certificate_name
        )

        print(
            "Certificate Qualification:",
            certificate_qualification
        )

        print(
            "Certificate Percentage:",
            certificate_percentage
        )

        print(
            "========================================\n"
        )


        # =================================================
        # RETURN
        # =================================================

        return {

            "name":
                certificate_name,

            "qualification":
                certificate_qualification,

            "percentage":
                certificate_percentage,

        }


    except Exception as e:

        print(
            "Certificate extraction error:",
            str(e)
        )


        return {

            "name": None,

            "qualification": None,

            "percentage": None,

            "error": str(e),

        }


# =========================================================
# VERIFY CERTIFICATE
# =========================================================

def verify_certificate(
    student,
    certificate_details
):

    # =====================================================
    # REGISTERED DETAILS
    # =====================================================

    registered_name = (
        student.full_name
    )


    registered_qualification = (
        student.previous_qualification
    )


    registered_percentage = float(
        student.plus_two_percentage
    )


    # =====================================================
    # CERTIFICATE DETAILS
    # =====================================================

    certificate_name = (
        certificate_details.get(
            "name"
        )
    )


    certificate_qualification = (
        certificate_details.get(
            "qualification"
        )
    )


    certificate_percentage = (
        certificate_details.get(
            "percentage"
        )
    )


    # =====================================================
    # NAME MATCH
    # =====================================================

    name_matched = name_matches(
        registered_name,
        certificate_name
    )


    # =====================================================
    # QUALIFICATION MATCH
    # =====================================================

    qualification_matched = (
        qualification_matches(
            registered_qualification,
            certificate_qualification
        )
    )


    # =====================================================
    # PERCENTAGE MATCH
    # =====================================================

    percentage_matched = False


    if certificate_percentage is not None:

        percentage_matched = (
            abs(
                registered_percentage
                -
                certificate_percentage
            ) < 0.01
        )


    # =====================================================
    # FINAL RESULT
    # =====================================================

    document_verified = (
        name_matched
        and
        qualification_matched
        and
        percentage_matched
    )


    # =====================================================
    # DEBUG VERIFICATION
    # =====================================================

    print(
        "\n========== VERIFICATION =========="
    )


    print(
        "Registered Name:",
        registered_name
    )


    print(
        "Certificate Name:",
        certificate_name
    )


    print(
        "Name Matched:",
        name_matched
    )


    print(
        "Registered Qualification:",
        registered_qualification
    )


    print(
        "Certificate Qualification:",
        certificate_qualification
    )


    print(
        "Qualification Matched:",
        qualification_matched
    )


    print(
        "Registered Percentage:",
        registered_percentage
    )


    print(
        "Certificate Percentage:",
        certificate_percentage
    )


    print(
        "Percentage Matched:",
        percentage_matched
    )


    print(
        "FINAL VERIFIED:",
        document_verified
    )


    print(
        "==================================\n"
    )


    # =====================================================
    # RETURN
    # =====================================================

    return {

        # -------------------------------------------------
        # NAME
        # -------------------------------------------------

        "registered_name":
            registered_name,

        "certificate_name":
            certificate_name,

        "name_matched":
            name_matched,


        # -------------------------------------------------
        # QUALIFICATION
        # -------------------------------------------------

        "registered_qualification":
            registered_qualification,

        "certificate_qualification":
            certificate_qualification,

        "qualification_matched":
            qualification_matched,


        # -------------------------------------------------
        # PERCENTAGE
        # -------------------------------------------------

        "registered_percentage":
            registered_percentage,

        "certificate_percentage":
            certificate_percentage,

        "percentage_matched":
            percentage_matched,


        # -------------------------------------------------
        # FINAL
        # -------------------------------------------------

        "document_verified":
            document_verified,

    }

