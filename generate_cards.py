#!/usr/bin/env python3
"""Generate MedEdTate patient discharge business cards with QR codes."""

import qrcode
from reportlab.lib.units import inch
from reportlab.lib.colors import HexColor
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import os
import io

# Register Knoxville font
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
pdfmetrics.registerFont(TTFont('Knoxville', os.path.join(SCRIPT_DIR, 'fonts', 'Knoxville-Regular.ttf')))

# Card dimensions
CARD_W = 3.5 * inch
CARD_H = 2.0 * inch

# Colors
GREEN_DARK = HexColor('#1a2e24')
GREEN_PRIMARY = HexColor('#4a8b6e')
GREEN_LIGHT = HexColor('#e0f0e8')
TEXT_LIGHT = HexColor('#5a7268')
WHITE = HexColor('#ffffff')
CRISIS_RED = HexColor('#c0544f')

# Facilities
FACILITIES = {
    'armc': {
        'name': 'Ashley Regional Medical Center',
        'short': 'ARMC',
        'location': 'Vernal, UT',
    },
    'castleview': {
        'name': 'Castleview Hospital',
        'short': 'Castleview',
        'location': 'Price, UT',
    },
    'nnrh': {
        'name': 'Northeastern Nevada Regional Hospital',
        'short': 'NNRH',
        'location': 'Elko, NV',
    },
}


def generate_qr(url, size=1.1*inch):
    """Generate a QR code image."""
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_M,
        box_size=10,
        border=1,
    )
    qr.add_data(url)
    qr.make(fit=True)
    img = qr.make_image(fill_color='#1a2e24', back_color='white')

    buf = io.BytesIO()
    img.save(buf, format='PNG')
    buf.seek(0)
    return buf


def draw_card_front(c, x, y, facility_id, facility):
    """Draw the front of a business card."""
    url = f'https://mededtate.com?er={facility_id}'

    # Card background
    c.setFillColor(WHITE)
    c.roundRect(x, y, CARD_W, CARD_H, 6, fill=1, stroke=0)

    # Subtle top accent bar
    c.setFillColor(GREEN_PRIMARY)
    c.rect(x, y + CARD_H - 4, CARD_W, 4, fill=1, stroke=0)

    # Logo text: MED_ed_TATE in Knoxville font
    # Knoxville lowercase renders as underlined caps
    logo_x = x + 0.25 * inch
    logo_y = y + CARD_H - 0.45 * inch
    c.setFillColor(GREEN_DARK)
    c.setFont('Knoxville', 16)
    # "MED" uppercase + "ed" lowercase (underlined in Knoxville) + "TATE" uppercase
    c.drawString(logo_x, logo_y, 'MED')
    med_w = c.stringWidth('MED', 'Knoxville', 16)
    c.drawString(logo_x + med_w, logo_y, 'ed')
    ed_w = c.stringWidth('ed', 'Knoxville', 16)
    c.drawString(logo_x + med_w + ed_w, logo_y, 'TATE')

    # Tagline
    c.setFillColor(TEXT_LIGHT)
    c.setFont('Helvetica', 6.5)
    c.drawString(logo_x, logo_y - 12, 'Mindfulness-Based Stress Reduction')

    # Main message
    c.setFillColor(GREEN_DARK)
    c.setFont('Helvetica-Bold', 9)
    c.drawString(logo_x, y + CARD_H - 0.85 * inch, 'A moment of calm starts here.')

    # Description
    c.setFillColor(TEXT_LIGHT)
    c.setFont('Helvetica', 6.5)
    c.drawString(logo_x, y + CARD_H - 1.05 * inch, 'Scan for breathing exercises, guided')
    c.drawString(logo_x, y + CARD_H - 1.18 * inch, 'meditations, and local resources.')

    # Facility name
    c.setFillColor(GREEN_PRIMARY)
    c.setFont('Helvetica', 5.5)
    c.drawString(logo_x, y + 0.15 * inch, facility['name'])

    # QR Code (right side)
    qr_size = 1.1 * inch
    qr_x = x + CARD_W - qr_size - 0.2 * inch
    qr_y = y + (CARD_H - qr_size) / 2 - 0.05 * inch

    qr_buf = generate_qr(url, qr_size)
    from reportlab.lib.utils import ImageReader
    qr_img = ImageReader(qr_buf)
    c.drawImage(qr_img, qr_x, qr_y, qr_size, qr_size)

    # Small URL under QR
    c.setFillColor(TEXT_LIGHT)
    c.setFont('Helvetica', 5)
    url_text = 'mededtate.com'
    url_w = c.stringWidth(url_text, 'Helvetica', 5)
    c.drawString(qr_x + (qr_size - url_w) / 2, qr_y - 8, url_text)


def draw_card_back(c, x, y):
    """Draw the back of a business card with crisis info."""
    # Card background
    c.setFillColor(GREEN_DARK)
    c.roundRect(x, y, CARD_W, CARD_H, 6, fill=1, stroke=0)

    # Logo in Knoxville
    c.setFillColor(WHITE)
    c.setFont('Knoxville', 18)
    logo_x = x + CARD_W / 2
    logo_text = 'MED' + 'ed' + 'TATE'
    c.drawCentredString(logo_x, y + CARD_H - 0.5 * inch, logo_text)

    # Divider
    c.setStrokeColor(HexColor('#4a8b6e'))
    c.setLineWidth(0.5)
    c.line(x + 0.5*inch, y + CARD_H - 0.65*inch, x + CARD_W - 0.5*inch, y + CARD_H - 0.65*inch)

    # Crisis info
    c.setFillColor(HexColor('#e0f0e8'))
    c.setFont('Helvetica-Bold', 7.5)
    c.drawCentredString(logo_x, y + CARD_H - 0.85 * inch, 'If you need immediate help:')

    c.setFillColor(WHITE)
    c.setFont('Helvetica-Bold', 9)
    c.drawCentredString(logo_x, y + CARD_H - 1.1 * inch, 'Call or text 988')

    c.setFillColor(HexColor('#e0f0e8'))
    c.setFont('Helvetica', 6.5)
    c.drawCentredString(logo_x, y + CARD_H - 1.3 * inch, 'Suicide & Crisis Lifeline  |  Available 24/7')

    c.setFillColor(WHITE)
    c.setFont('Helvetica', 6.5)
    c.drawCentredString(logo_x, y + 0.5 * inch, 'Text HOME to 741741  |  Crisis Text Line')

    # 911
    c.setFillColor(HexColor('#e0f0e8'))
    c.setFont('Helvetica-Bold', 7)
    c.drawCentredString(logo_x, y + 0.32 * inch, 'Emergency? Call 911')

    c.setFillColor(HexColor('#6ba593'))
    c.setFont('Helvetica', 5)
    c.drawCentredString(logo_x, y + 0.15 * inch, 'mededtate.com')


def generate_cards_pdf(facility_id, output_dir):
    """Generate a PDF with multiple business cards for a facility."""
    facility = FACILITIES.get(facility_id)
    if not facility:
        print(f"Unknown facility: {facility_id}")
        return

    output_path = os.path.join(output_dir, f'cards-{facility_id}.pdf')

    # Letter size with 10 cards per page (2 columns x 5 rows)
    page_w, page_h = letter
    cols = 2
    rows = 5

    margin_x = (page_w - cols * CARD_W) / 2
    margin_y = (page_h - rows * CARD_H) / 2
    gap = 0

    c_pdf = canvas.Canvas(output_path, pagesize=letter)
    c_pdf.setTitle(f'MedEdTate Cards - {facility["short"]}')

    # Page 1: Fronts
    c_pdf.setFont('Helvetica', 8)
    c_pdf.setFillColor(TEXT_LIGHT)
    c_pdf.drawCentredString(page_w / 2, page_h - 0.35 * inch,
                            f'MedEdTate Cards - {facility["name"]} (Front)')

    for row in range(rows):
        for col in range(cols):
            x = margin_x + col * (CARD_W + gap)
            y = margin_y + (rows - 1 - row) * (CARD_H + gap)

            # Light cut line
            c_pdf.setStrokeColor(HexColor('#d4e5dc'))
            c_pdf.setLineWidth(0.25)
            c_pdf.rect(x, y, CARD_W, CARD_H, fill=0, stroke=1)

            draw_card_front(c_pdf, x, y, facility_id, facility)

    c_pdf.showPage()

    # Page 2: Backs
    c_pdf.setFont('Helvetica', 8)
    c_pdf.setFillColor(TEXT_LIGHT)
    c_pdf.drawCentredString(page_w / 2, page_h - 0.35 * inch,
                            f'MedEdTate Cards - {facility["name"]} (Back)')

    for row in range(rows):
        for col in range(cols):
            # Mirror columns for back side printing
            x = margin_x + (cols - 1 - col) * (CARD_W + gap)
            y = margin_y + (rows - 1 - row) * (CARD_H + gap)

            c_pdf.setStrokeColor(HexColor('#d4e5dc'))
            c_pdf.setLineWidth(0.25)
            c_pdf.rect(x, y, CARD_W, CARD_H, fill=0, stroke=1)

            draw_card_back(c_pdf, x, y)

    c_pdf.showPage()
    c_pdf.save()
    print(f'Generated: {output_path}')
    return output_path


if __name__ == '__main__':
    output_dir = os.path.dirname(os.path.abspath(__file__))

    for fid in FACILITIES:
        generate_cards_pdf(fid, output_dir)

    print('Done! Cards ready to print.')
