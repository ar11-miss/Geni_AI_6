// Extracts text from a PDF using Apple's built-in PDFKit (macOS).
// Usage: pdf2text <file.pdf>   -> prints pages separated by a form feed (\f)
import Foundation
import PDFKit

guard CommandLine.arguments.count > 1,
      let doc = PDFDocument(url: URL(fileURLWithPath: CommandLine.arguments[1])) else {
    FileHandle.standardError.write("cannot open PDF\n".data(using: .utf8)!)
    exit(1)
}
var pages: [String] = []
for i in 0..<doc.pageCount {
    pages.append(doc.page(at: i)?.string ?? "")
}
print(pages.joined(separator: "\u{0C}"))
