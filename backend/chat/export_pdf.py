"""
PDF Export — NEW FILE: save as chat/export_pdf.py

Generates a styled PDF of a conversation.
GET /api/chat/conversations/:id/export-pdf/
"""

import io
from datetime import datetime
from django.http import HttpResponse
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_LEFT, TA_RIGHT
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, HRFlowable
from reportlab.lib.colors import HexColor

from .models import Conversation


class ExportPdfView(APIView):
    """Export a conversation as a styled PDF file."""
    permission_classes = [IsAuthenticated]

    def get(self, request, conversation_id):
        try:
            conversation = Conversation.objects.get(
                id=conversation_id, user=request.user
            )
        except Conversation.DoesNotExist:
            return Response(
                {"detail": "Conversation not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        messages = conversation.messages.all()
        if not messages.exists():
            return Response(
                {"detail": "No messages to export."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        lang = request.user.language
        is_rtl = lang == "ar"
        align = TA_RIGHT if is_rtl else TA_LEFT

        # Build PDF
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(
            buffer, pagesize=A4,
            topMargin=50, bottomMargin=40,
            leftMargin=50, rightMargin=50,
        )

        styles = getSampleStyleSheet()

        title_style = ParagraphStyle(
            'ConvTitle', parent=styles['Title'],
            fontSize=18, spaceAfter=6,
            textColor=HexColor('#1c1917'), alignment=align,
        )
        meta_style = ParagraphStyle(
            'Meta', parent=styles['Normal'],
            fontSize=9, textColor=HexColor('#a8a29e'),
            spaceAfter=16, alignment=align,
        )
        role_style = ParagraphStyle(
            'Role', parent=styles['Normal'],
            fontSize=8, textColor=HexColor('#6366f1'),
            spaceBefore=12, alignment=align,
        )
        user_style = ParagraphStyle(
            'UserMsg', parent=styles['Normal'],
            fontSize=10, textColor=HexColor('#1c1917'),
            spaceAfter=4, leftIndent=16,
            backColor=HexColor('#f5f5f4'),
            borderPadding=8, alignment=align,
        )
        ai_style = ParagraphStyle(
            'AIMsg', parent=styles['Normal'],
            fontSize=10, textColor=HexColor('#44403c'),
            spaceAfter=4, leftIndent=16,
            borderPadding=8, alignment=align,
        )

        elements = []

        # Title
        title = conversation.title or (
            "محادثة بدون عنوان" if is_rtl else "Untitled Conversation"
        )
        elements.append(Paragraph(title, title_style))

        # Metadata
        date_str = conversation.created_at.strftime("%Y-%m-%d %H:%M")
        model_label = conversation.model
        if is_rtl:
            meta = f"{date_str} | المحرك: {model_label}"
        else:
            meta = f"Model: {model_label} | {date_str}"
        elements.append(Paragraph(meta, meta_style))
        elements.append(HRFlowable(
            width="100%", thickness=0.5, color=HexColor('#e7e5e4'),
        ))
        elements.append(Spacer(1, 12))

        # Messages
        for msg in messages:
            if is_rtl:
                role_label = "أنت" if msg.role == "user" else "المساعد"
            else:
                role_label = "You" if msg.role == "user" else "Assistant"

            elements.append(Paragraph(f"<b>{role_label}</b>", role_style))

            # Escape XML and preserve newlines
            safe_content = (
                msg.content
                .replace('&', '&amp;')
                .replace('<', '&lt;')
                .replace('>', '&gt;')
                .replace('\n', '<br/>')
            )

            style = user_style if msg.role == "user" else ai_style
            elements.append(Paragraph(safe_content, style))

        # Footer
        elements.append(Spacer(1, 24))
        elements.append(HRFlowable(
            width="100%", thickness=0.5, color=HexColor('#e7e5e4'),
        ))
        footer_text = (
            "تم التصدير من AqlAI" if is_rtl else "Exported from AqlAI"
        )
        footer_style = ParagraphStyle(
            'Footer', parent=styles['Normal'],
            fontSize=8, textColor=HexColor('#a8a29e'),
        )
        elements.append(Paragraph(footer_text, footer_style))

        doc.build(elements)
        buffer.seek(0)

        filename = f"aqlai_chat_{conversation.id}_{datetime.now().strftime('%Y%m%d')}.pdf"
        response = HttpResponse(buffer, content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        return response