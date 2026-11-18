/**
 * Multi-page PDF generation utility using pdf-lib.
 * Handles automatic pagination, headers, footers, and text wrapping.
 */
import { PDFDocument, rgb, StandardFonts } from "pdf-lib";

export async function generateResumeReportPdf(analysisResult, finalJobRole, selectedPersona) {
  if (!analysisResult) return;

  const pdfDoc = await PDFDocument.create();
  const helvetica = await pdfDoc.embedFont(StandardFonts.Helvetica);
  const helveticaBold = await pdfDoc.embedFont(StandardFonts.HelveticaBold);

  const pageWidth = 595.28; // A4 dimensions
  const pageHeight = 841.89;
  const margin = 50;
  const contentWidth = pageWidth - margin * 2;

  let currentPage = pdfDoc.addPage([pageWidth, pageHeight]);
  let y = pageHeight - margin;

  const drawFooter = (page, font, pageNum) => {
    page.drawText(`AI Resume Reviewer | Confidential Report | Page ${pageNum}`, {
      x: margin,
      y: margin - 15,
      size: 8,
      font,
      color: rgb(0.5, 0.5, 0.5)
    });
  };

  const drawMiniHeader = (page, font) => {
    page.drawText(`Target Role: ${finalJobRole} | Advisor: ${selectedPersona} | Score: ${analysisResult.overall_score}/100`, {
      x: margin,
      y: pageHeight - 35,
      size: 9,
      font,
      color: rgb(0.3, 0.4, 0.5)
    });
  };

  const checkPageBreak = (neededHeight) => {
    if (y - neededHeight < margin + 30) {
      drawFooter(currentPage, helvetica, pdfDoc.getPageCount());
      currentPage = pdfDoc.addPage([pageWidth, pageHeight]);
      y = pageHeight - margin;
      drawMiniHeader(currentPage, helveticaBold);
      y -= 30;
    }
  };

  const writeWrapped = (text, size, font, color = rgb(0.1, 0.1, 0.1), lineSpacing = 1.3) => {
    const words = text.split(" ");
    let line = "";
    for (const word of words) {
      const testLine = line ? `${line} ${word}` : word;
      const textWidth = font.widthOfTextAtSize(testLine, size);
      if (textWidth > contentWidth) {
        checkPageBreak(size * lineSpacing);
        currentPage.drawText(line, { x: margin, y, size, font, color });
        y -= size * lineSpacing;
        line = word;
      } else {
        line = testLine;
      }
    }
    if (line) {
      checkPageBreak(size * lineSpacing);
      currentPage.drawText(line, { x: margin, y, size, font, color });
      y -= size * lineSpacing;
    }
  };

  // Title Banner
  currentPage.drawRectangle({
    x: margin,
    y: y - 55,
    width: contentWidth,
    height: 60,
    color: rgb(0.05, 0.35, 0.65)
  });

  currentPage.drawText("AI Resume Review & Career Strategy Report", {
    x: margin + 15,
    y: y - 25,
    size: 16,
    font: helveticaBold,
    color: rgb(1, 1, 1)
  });

  currentPage.drawText(`Target: ${finalJobRole}  |  Seniority: ${analysisResult.seniority_level || 'Mid'}  |  Score: ${analysisResult.overall_score}/100`, {
    x: margin + 15,
    y: y - 45,
    size: 9.5,
    font: helvetica,
    color: rgb(0.9, 0.95, 1)
  });

  y -= 75;

  // Executive Summary
  checkPageBreak(40);
  currentPage.drawText("EXECUTIVE ASSESSMENT", {
    x: margin,
    y,
    size: 12,
    font: helveticaBold,
    color: rgb(0.05, 0.35, 0.65)
  });
  y -= 16;
  writeWrapped(analysisResult.summary, 10, helvetica);
  y -= 14;

  // Dimension Scores
  checkPageBreak(50);
  currentPage.drawText("ATS DIMENSION SCORES", {
    x: margin,
    y,
    size: 12,
    font: helveticaBold,
    color: rgb(0.05, 0.35, 0.65)
  });
  y -= 16;
  const cats = analysisResult.category_scores || {};
  const scoreLine = `Role Relevance: ${cats.role_relevance || 0}/100  |  Impact & Metrics: ${cats.impact_quantification || 0}/100  |  ATS Readability: ${cats.ats_readability || 0}/100  |  Skills Match: ${cats.skills_alignment || 0}/100`;
  writeWrapped(scoreLine, 9, helveticaBold, rgb(0.2, 0.2, 0.2));
  y -= 14;

  // Key Strengths
  if (analysisResult.strengths?.length) {
    checkPageBreak(40);
    currentPage.drawText("KEY STRENGTHS", {
      x: margin,
      y,
      size: 12,
      font: helveticaBold,
      color: rgb(0.1, 0.5, 0.2)
    });
    y -= 16;
    for (const s of analysisResult.strengths) {
      writeWrapped(`•  ${s}`, 9.5, helvetica);
      y -= 4;
    }
    y -= 10;
  }

  // Critical Weaknesses
  if (analysisResult.weaknesses?.length) {
    checkPageBreak(40);
    currentPage.drawText("CRITICAL IMPROVEMENT AREAS", {
      x: margin,
      y,
      size: 12,
      font: helveticaBold,
      color: rgb(0.7, 0.2, 0.1)
    });
    y -= 16;
    for (const w of analysisResult.weaknesses) {
      writeWrapped(`•  [${w.severity.toUpperCase()}] ${w.issue}: ${w.description}`, 9.5, helvetica);
      y -= 4;
    }
    y -= 10;
  }

  // Bullet Rewrites
  if (analysisResult.bullet_improvements?.length) {
    checkPageBreak(50);
    currentPage.drawText("GOOGLE XYZ FORMULA BULLET REWRITES", {
      x: margin,
      y,
      size: 12,
      font: helveticaBold,
      color: rgb(0.05, 0.35, 0.65)
    });
    y -= 16;
    for (const b of analysisResult.bullet_improvements) {
      writeWrapped(`Original: "${b.original}"`, 9, helvetica, rgb(0.4, 0.4, 0.4));
      writeWrapped(`Optimized: "${b.improved}"`, 9.5, helveticaBold, rgb(0.05, 0.3, 0.6));
      writeWrapped(`Why it works: ${b.reason}`, 8.5, helvetica, rgb(0.3, 0.3, 0.3));
      y -= 8;
    }
    y -= 6;
  }

  // Action Plan
  if (analysisResult.action_plan?.length) {
    checkPageBreak(40);
    currentPage.drawText("STRATEGIC ACTION PLAN", {
      x: margin,
      y,
      size: 12,
      font: helveticaBold,
      color: rgb(0.05, 0.35, 0.65)
    });
    y -= 16;
    analysisResult.action_plan.forEach((step, idx) => {
      writeWrapped(`${idx + 1}.  ${step}`, 9.5, helvetica);
      y -= 4;
    });
    y -= 10;
  }

  // Interview Prep
  if (analysisResult.interview_questions?.length) {
    checkPageBreak(40);
    currentPage.drawText("RECOMMENDED INTERVIEW PREPARATION", {
      x: margin,
      y,
      size: 12,
      font: helveticaBold,
      color: rgb(0.05, 0.35, 0.65)
    });
    y -= 16;
    for (const q of analysisResult.interview_questions) {
      writeWrapped(`Q: ${q.question}`, 9.5, helveticaBold, rgb(0.15, 0.15, 0.15));
      writeWrapped(`Context: ${q.context}`, 8.5, helvetica, rgb(0.4, 0.4, 0.4));
      y -= 6;
    }
  }

  drawFooter(currentPage, helvetica, pdfDoc.getPageCount());

  const pdfBytes = await pdfDoc.save();
  const blob = new Blob([pdfBytes], { type: "application/pdf" });
  const filename = `AI_Resume_Review_${finalJobRole.replace(/\s+/g, "_")}.pdf`;
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  a.download = filename;
  document.body.appendChild(a);
  a.click();
  setTimeout(() => {
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  }, 2000);
}
