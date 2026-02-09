//
//  PDFReportGenerator.swift
//  Choke Test Safety Check
//
//  Generates PDF reports of choke test results
//

import Foundation
import PDFKit
import AppKit

enum PDFReportGenerator {
    static func generate(results: [ChokeTestResult], standard: ChokeStandard, to url: URL) {
        let pdfDocument = createPDF(results: results, standard: standard)
        pdfDocument.write(to: url)
    }

    private static func createPDF(results: [ChokeTestResult], standard: ChokeStandard) -> PDFDocument {
        let pageWidth: CGFloat = 612 // US Letter
        let pageHeight: CGFloat = 792
        let margin: CGFloat = 50

        let pdfData = NSMutableData()
        let consumer = CGDataConsumer(data: pdfData)!

        var mediaBox = CGRect(x: 0, y: 0, width: pageWidth, height: pageHeight)
        let pdfContext = CGContext(consumer: consumer, mediaBox: &mediaBox, nil)!

        pdfContext.beginPage(mediaBox: &mediaBox)

        // Draw content
        var yPosition = pageHeight - margin

        // Title
        yPosition = drawText(
            "Choke Test Safety Check Report",
            at: CGPoint(x: margin, y: yPosition),
            fontSize: 24,
            bold: true,
            context: pdfContext
        )
        yPosition -= 20

        // Date
        let dateFormatter = DateFormatter()
        dateFormatter.dateStyle = .long
        dateFormatter.timeStyle = .short
        yPosition = drawText(
            "Generated: \(dateFormatter.string(from: Date()))",
            at: CGPoint(x: margin, y: yPosition),
            fontSize: 12,
            bold: false,
            context: pdfContext
        )
        yPosition -= 10

        // Standard info
        yPosition = drawText(
            "Standard: \(standard.name) - Ø\(String(format: "%.2f", standard.diameterMM))mm × \(String(format: "%.2f", standard.heightMM))mm",
            at: CGPoint(x: margin, y: yPosition),
            fontSize: 12,
            bold: false,
            context: pdfContext
        )
        yPosition -= 30

        // Summary
        let hazardCount = results.filter { $0.fits }.count
        let safeCount = results.count - hazardCount

        yPosition = drawText(
            "Summary",
            at: CGPoint(x: margin, y: yPosition),
            fontSize: 18,
            bold: true,
            context: pdfContext
        )
        yPosition -= 25

        yPosition = drawText(
            "Total Objects: \(results.count)",
            at: CGPoint(x: margin + 20, y: yPosition),
            fontSize: 12,
            bold: false,
            context: pdfContext
        )
        yPosition -= 20

        pdfContext.setFillColor(red: 1, green: 0, blue: 0, alpha: 1)
        yPosition = drawText(
            "Choking Hazards: \(hazardCount)",
            at: CGPoint(x: margin + 20, y: yPosition),
            fontSize: 12,
            bold: true,
            context: pdfContext
        )
        yPosition -= 20

        pdfContext.setFillColor(red: 0, green: 0.6, blue: 0, alpha: 1)
        yPosition = drawText(
            "Safe Objects: \(safeCount)",
            at: CGPoint(x: margin + 20, y: yPosition),
            fontSize: 12,
            bold: true,
            context: pdfContext
        )
        yPosition -= 40

        // Results table
        pdfContext.setFillColor(red: 0, green: 0, blue: 0, alpha: 1)
        yPosition = drawText(
            "Detailed Results",
            at: CGPoint(x: margin, y: yPosition),
            fontSize: 18,
            bold: true,
            context: pdfContext
        )
        yPosition -= 25

        for result in results {
            if yPosition < margin + 100 {
                // Start new page
                pdfContext.endPage()
                pdfContext.beginPage(mediaBox: &mediaBox)
                yPosition = pageHeight - margin
            }

            // Status indicator
            let indicatorRect = CGRect(x: margin, y: yPosition - 8, width: 10, height: 10)
            pdfContext.setFillColor(result.status.color.cgColor)
            pdfContext.fillEllipse(in: indicatorRect)

            // Object name
            pdfContext.setFillColor(red: 0, green: 0, blue: 0, alpha: 1)
            yPosition = drawText(
                result.name,
                at: CGPoint(x: margin + 20, y: yPosition),
                fontSize: 12,
                bold: true,
                context: pdfContext
            )
            yPosition -= 15

            // Details
            if let diameter = result.diameterMM, let height = result.heightMM {
                let details = "  Ø\(String(format: "%.1f", diameter))mm × \(String(format: "%.1f", height))mm - \(result.statusText)"
                yPosition = drawText(
                    details,
                    at: CGPoint(x: margin + 20, y: yPosition),
                    fontSize: 10,
                    bold: false,
                    context: pdfContext
                )
            }
            yPosition -= 25
        }

        // Footer
        let footerText = "This report is for informational purposes only. Always follow official safety guidelines."
        drawText(
            footerText,
            at: CGPoint(x: margin, y: 30),
            fontSize: 9,
            bold: false,
            context: pdfContext
        )

        pdfContext.endPage()
        pdfContext.closePDF()

        let document = PDFDocument(data: pdfData as Data)!
        return document
    }

    @discardableResult
    private static func drawText(_ text: String, at point: CGPoint, fontSize: CGFloat, bold: Bool, context: CGContext) -> CGFloat {
        let font = bold ? NSFont.boldSystemFont(ofSize: fontSize) : NSFont.systemFont(ofSize: fontSize)
        let attributes: [NSAttributedString.Key: Any] = [
            .font: font,
            .foregroundColor: NSColor(cgColor: context.fillColor ?? .black)!
        ]

        let attributedString = NSAttributedString(string: text, attributes: attributes)
        let line = CTLineCreateWithAttributedString(attributedString)

        context.textMatrix = .identity
        context.translateBy(x: point.x, y: point.y)
        context.scaleBy(x: 1, y: -1)

        CTLineDraw(line, context)

        context.scaleBy(x: 1, y: -1)
        context.translateBy(x: -point.x, y: -point.y)

        return point.y - fontSize - 5
    }
}
