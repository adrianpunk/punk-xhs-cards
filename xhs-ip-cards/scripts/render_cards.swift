import AppKit
import Foundation

let W: CGFloat = 1080
let H: CGFloat = 1440

struct Payload: Decodable {
    let seriesTitle: String?
    let handle: String?
    let cover: CoverSpec?
    let cards: [Card]
}

struct CoverSpec: Decodable {
    let title: String
    let author: String
    let hero: String
}

struct Card: Decodable {
    let kind: String
    let eyebrow: String?
    let title: String
    let subtitle: String?
    let summary: String?
    let highlight: String?
    let blocks: [Block]?
}

struct Block: Decodable {
    let kind: String
    let text: String?
    let number: String?
    let title: String?
    let body: String?
    let path: String?
    let caption: String?
    let height: Double?
}

struct ProfileAssets: Decodable {
    let card_pose: String
    let theme: String
}

struct ProfileManifest: Decodable {
    let name: String
    let status: String
    let assets: ProfileAssets
}

struct ThemePalette: Decodable {
    let accent: String
    let deepAccent: String
    let panel: String
    let paper: String
    let ink: String
    let body: String
    let muted: String
    let line: String
}

struct Theme: Decodable {
    let profileName: String
    let handle: String?
    let brandLabel: String?
    let palette: ThemePalette
}

func color(hex: String) -> NSColor {
    let clean = hex.trimmingCharacters(in: CharacterSet(charactersIn: "#"))
    guard clean.count == 6, let value = Int(clean, radix: 16) else {
        fatalError("Invalid theme color: \(hex)")
    }
    return NSColor(calibratedRed: CGFloat((value >> 16) & 0xFF) / 255,
                   green: CGFloat((value >> 8) & 0xFF) / 255,
                   blue: CGFloat(value & 0xFF) / 255,
                   alpha: 1)
}

struct Palette {
    static var paper = color(hex: "#FAF7F0")
    static var panel = color(hex: "#F2E7E2")
    static var red = color(hex: "#A64A3E")
    static var deepRed = color(hex: "#6F2C25")
    static var ink = color(hex: "#1D1815")
    static var body = color(hex: "#453E39")
    static var muted = color(hex: "#81766E")
    static var line = color(hex: "#DCC8C1")

    static func configure(_ source: ThemePalette) {
        paper = color(hex: source.paper)
        panel = color(hex: source.panel)
        red = color(hex: source.accent)
        deepRed = color(hex: source.deepAccent)
        ink = color(hex: source.ink)
        body = color(hex: source.body)
        muted = color(hex: source.muted)
        line = color(hex: source.line)
    }
}

func rect(_ x: CGFloat, _ y: CGFloat, _ w: CGFloat, _ h: CGFloat) -> NSRect {
    NSRect(x: x, y: y, width: w, height: h)
}

func font(_ size: CGFloat, _ weight: NSFont.Weight = .regular, mono: Bool = false) -> NSFont {
    if mono { return NSFont.monospacedSystemFont(ofSize: size, weight: weight) }
    let name: String
    switch weight {
    case .bold, .heavy, .black, .semibold: name = "PingFangSC-Semibold"
    case .medium: name = "PingFangSC-Medium"
    default: name = "PingFangSC-Regular"
    }
    return NSFont(name: name, size: size) ?? NSFont.systemFont(ofSize: size, weight: weight)
}

func attributes(size: CGFloat, weight: NSFont.Weight, color: NSColor, spacing: CGFloat,
                align: NSTextAlignment = .left, mono: Bool = false, kern: CGFloat = 0) -> [NSAttributedString.Key: Any] {
    let style = NSMutableParagraphStyle()
    style.alignment = align
    style.lineBreakMode = .byWordWrapping
    style.lineSpacing = spacing
    return [.font: font(size, weight, mono: mono), .foregroundColor: color, .paragraphStyle: style, .kern: kern]
}

func textHeight(_ value: String, width: CGFloat, size: CGFloat, weight: NSFont.Weight = .regular,
                spacing: CGFloat = 7, mono: Bool = false) -> CGFloat {
    let a = attributes(size: size, weight: weight, color: Palette.body, spacing: spacing, mono: mono)
    let b = (value as NSString).boundingRect(with: NSSize(width: width, height: 10_000),
        options: [.usesLineFragmentOrigin, .usesFontLeading], attributes: a)
    return ceil(b.height)
}

func text(_ value: String, _ box: NSRect, size: CGFloat, weight: NSFont.Weight = .regular,
          color: NSColor = Palette.body, align: NSTextAlignment = .left,
          spacing: CGFloat = 7, mono: Bool = false, kern: CGFloat = 0) {
    (value as NSString).draw(in: box, withAttributes: attributes(size: size, weight: weight, color: color,
        spacing: spacing, align: align, mono: mono, kern: kern))
}

func fill(_ box: NSRect, _ color: NSColor, radius: CGFloat = 0) {
    color.setFill()
    let path = radius > 0 ? NSBezierPath(roundedRect: box, xRadius: radius, yRadius: radius) : NSBezierPath(rect: box)
    path.fill()
}

func fillPolygon(_ points: [NSPoint], _ color: NSColor) {
    guard let first = points.first else { return }
    let path = NSBezierPath()
    path.move(to: first)
    for point in points.dropFirst() { path.line(to: point) }
    path.close()
    color.setFill()
    path.fill()
}

func stroke(_ box: NSRect, _ color: NSColor, width: CGFloat = 2, radius: CGFloat = 0) {
    color.setStroke()
    let path = radius > 0 ? NSBezierPath(roundedRect: box, xRadius: radius, yRadius: radius) : NSBezierPath(rect: box)
    path.lineWidth = width
    path.stroke()
}

func rule(_ x1: CGFloat, _ y1: CGFloat, _ x2: CGFloat, _ y2: CGFloat,
          color: NSColor = Palette.line, width: CGFloat = 2) {
    color.setStroke()
    let path = NSBezierPath()
    path.move(to: NSPoint(x: x1, y: y1))
    path.line(to: NSPoint(x: x2, y: y2))
    path.lineWidth = width
    path.stroke()
}

func drawAspectFit(_ image: NSImage, in box: NSRect) {
    let scale = min(box.width / image.size.width, box.height / image.size.height)
    let width = image.size.width * scale
    let height = image.size.height * scale
    let x = box.minX + (box.width - width) / 2
    let y = box.maxY - height
    image.draw(in: rect(x, y, width, height), from: rect(0, 0, image.size.width, image.size.height),
        operation: .sourceOver, fraction: 1, respectFlipped: true,
        hints: [.interpolation: NSImageInterpolation.high])
}

func singleLineTitleSize(_ value: String, maxWidth: CGFloat) -> CGFloat {
    var size: CGFloat = 48
    while size > 20 {
        let attrs: [NSAttributedString.Key: Any] = [.font: font(size, .semibold)]
        if (value as NSString).size(withAttributes: attrs).width <= maxWidth { return size }
        size -= 1
    }
    return 20
}

func titleLineWidth(_ value: String, size: CGFloat) -> CGFloat {
    let attrs: [NSAttributedString.Key: Any] = [.font: font(size, .semibold)]
    return (value as NSString).size(withAttributes: attrs).width
}

func balancedTwoLineTitle(_ value: String) -> String {
    let characters = Array(value)
    guard characters.count >= 12 else { return value }
    let separators = Set("：:，,；;。！？!?、—-")
    var candidates: [(index: Int, score: Int)] = []
    for index in 1..<characters.count {
        let previous = characters[index - 1]
        let isBreak = separators.contains(previous) || previous.isWhitespace
        guard isBreak, index >= 5, characters.count - index >= 5 else { continue }
        let balance = abs(characters.count - index * 2)
        let semanticBonus = previous == "：" || previous == ":" ? -8 : 0
        candidates.append((index, balance + semanticBonus))
    }
    let split = candidates.min { $0.score < $1.score }?.index ?? characters.count / 2
    let first = String(characters[..<split]).trimmingCharacters(in: .whitespacesAndNewlines)
    let second = String(characters[split...]).trimmingCharacters(in: .whitespacesAndNewlines)
    return first.isEmpty || second.isEmpty ? value : first + "\n" + second
}

func blockHeight(_ block: Block) -> CGFloat {
    switch block.kind {
    case "paragraph":
        return textHeight(block.text ?? "", width: 952, size: 24.5, spacing: 9) + 18
    case "highlight", "note":
        return max(82, textHeight(block.text ?? "", width: 882, size: 23.5, weight: .semibold, spacing: 6) + 38) + 18
    case "section":
        return 68
    case "item":
        let body = textHeight(block.body ?? "", width: 830, size: 22.5, spacing: 6)
        return max(98, 48 + body + 22)
    case "bullet":
        return max(48, textHeight(block.text ?? "", width: 900, size: 23.5, spacing: 6) + 16)
    case "code":
        return max(76, textHeight(block.text ?? "", width: 900, size: 18.5, weight: .medium, spacing: 7, mono: true) + 34) + 16
    case "image":
        let mediaHeight = min(520, max(220, CGFloat(block.height ?? 360)))
        let captionHeight = (block.caption?.isEmpty == false)
            ? textHeight(block.caption!, width: 900, size: 18.5, spacing: 4) + 22
            : 0
        return mediaHeight + captionHeight + 18
    case "spacer":
        return CGFloat(block.height ?? 16)
    default:
        return 0
    }
}

func drawBlock(_ block: Block, at y: CGFloat, assetBaseURL: URL) throws {
    let h = blockHeight(block)
    switch block.kind {
    case "paragraph":
        text(block.text ?? "", rect(64, y, 952, h - 8), size: 24.5, color: Palette.body, spacing: 9)
    case "highlight":
        fill(rect(64, y, 952, h - 18), Palette.panel, radius: 18)
        fill(rect(64, y, 8, h - 18), Palette.red, radius: 4)
        text(block.text ?? "", rect(94, y + 19, 882, h - 42), size: 23.5, weight: .semibold,
             color: Palette.deepRed, spacing: 6)
    case "note":
        fill(rect(64, y, 952, h - 18), Palette.panel, radius: 18)
        stroke(rect(64, y, 952, h - 18), Palette.line, width: 1.5, radius: 18)
        text(block.text ?? "", rect(90, y + 19, 892, h - 42), size: 23.5, weight: .semibold,
             color: Palette.deepRed, spacing: 6)
    case "section":
        fill(rect(64, y + 8, 7, 38), Palette.red, radius: 3)
        text(block.text ?? "", rect(88, y, 900, 52), size: 30, weight: .bold, color: Palette.ink, spacing: 0)
    case "item":
        fill(rect(64, y + 2, 54, 54), Palette.panel, radius: 27)
        text(block.number ?? "•", rect(64, y + 13, 54, 28), size: 18, weight: .bold,
             color: Palette.deepRed, align: .center, spacing: 0, mono: true)
        text(block.title ?? "", rect(140, y, 850, 42), size: 28, weight: .bold, color: Palette.ink, spacing: 0)
        text(block.body ?? "", rect(140, y + 47, 850, h - 65), size: 22.5, color: Palette.body, spacing: 6)
        rule(140, y + h - 8, 1016, y + h - 8)
    case "bullet":
        fill(rect(76, y + 14, 10, 10), Palette.red, radius: 5)
        text(block.text ?? "", rect(101, y, 905, h), size: 23.5, color: Palette.body, spacing: 6)
    case "code":
        fill(rect(64, y, 952, h - 16), Palette.panel, radius: 16)
        text(block.text ?? "", rect(88, y + 17, 904, h - 42), size: 18.5, weight: .medium,
             color: Palette.ink, spacing: 7, mono: true)
    case "image":
        guard let value = block.path, !value.isEmpty else {
            throw NSError(domain: "xhs-ip-cards", code: 2,
                userInfo: [NSLocalizedDescriptionKey: "Image block is missing path"])
        }
        let candidate = URL(fileURLWithPath: value)
        let imageURL = value.hasPrefix("/") ? candidate : assetBaseURL.appendingPathComponent(value)
        guard let sourceImage = NSImage(contentsOf: imageURL) else {
            throw NSError(domain: "xhs-ip-cards", code: 3,
                userInfo: [NSLocalizedDescriptionKey: "Cannot load image block: \(imageURL.path)"])
        }
        let mediaHeight = min(520, max(220, CGFloat(block.height ?? 360)))
        fill(rect(64, y, 952, mediaHeight), NSColor.white.withAlphaComponent(0.78), radius: 16)
        stroke(rect(64, y, 952, mediaHeight), Palette.line, width: 1.5, radius: 16)
        drawAspectFit(sourceImage, in: rect(78, y + 14, 924, mediaHeight - 28))
        if let caption = block.caption, !caption.isEmpty {
            text(caption, rect(82, y + mediaHeight + 10, 916, h - mediaHeight - 18), size: 18.5,
                 color: Palette.muted, spacing: 4)
        }
    default:
        break
    }
}

func footer(page: Int, total: Int, handle: String, brandLabel: String, ip: NSImage?) {
    rule(64, 1238, 742, 1238)
    text(brandLabel.uppercased(), rect(64, 1270, 360, 30), size: 19, weight: .semibold,
         color: Palette.red, spacing: 0, kern: 2)
    text(handle, rect(64, 1308, 330, 30), size: 20, weight: .medium, color: Palette.muted, spacing: 0)
    text(String(format: "%02d / %02d", page, total), rect(64, 1365, 190, 28), size: 18,
         weight: .medium, color: Palette.muted, spacing: 0, mono: true)
    if let ip = ip { drawAspectFit(ip, in: rect(785, 1172, 250, 225)) }
}

func drawBookCover(_ cover: CoverSpec, handle: String, hero: NSImage, ip: NSImage?) {
    fill(rect(0, 0, W, H), Palette.paper)
    fill(rect(0, 0, 38, H), Palette.deepRed)
    fill(rect(38, 842, W - 38, H - 842), Palette.deepRed)

    let mount = rect(78, 54, 954, 566)
    fill(mount, NSColor.white.withAlphaComponent(0.98), radius: 18)
    stroke(mount, Palette.line, width: 2, radius: 18)
    drawAspectFit(hero, in: rect(90, 66, 930, 542))

    fillPolygon([
        NSPoint(x: 38, y: 654), NSPoint(x: 1080, y: 654),
        NSPoint(x: 1080, y: 842), NSPoint(x: 735, y: 842),
        NSPoint(x: 610, y: 955), NSPoint(x: 38, y: 955)
    ], Palette.paper)
    rule(38, 654, 1080, 654, color: Palette.red, width: 2)

    let displayTitle = cover.title.replacingOccurrences(of: "\n", with: " ")
    let fitted = singleLineTitleSize(displayTitle, maxWidth: 900)
    if fitted >= 46 {
        text(displayTitle, rect(84, 702, 900, 72), size: fitted, weight: .semibold,
             color: Palette.ink, spacing: 0)
    } else {
        let arrangedTitle = balancedTwoLineTitle(displayTitle)
        let lines = arrangedTitle.components(separatedBy: "\n")
        var size: CGFloat = 52
        while size > 36 && (lines.map { titleLineWidth($0, size: size) }.max() ?? 0) > 900 {
            size -= 1
        }
        text(arrangedTitle, rect(84, 662, 900, 174), size: size, weight: .semibold,
             color: Palette.ink, spacing: 5)
    }

    rule(84, 832, 646, 832, color: Palette.red, width: 3)
    fill(rect(84, 862, 8, 42), Palette.red, radius: 3)
    text("作者", rect(112, 867, 80, 30), size: 19, weight: .semibold,
         color: Palette.red, spacing: 0, kern: 1.5)
    text(cover.author, rect(198, 860, 430, 42), size: 29, weight: .semibold,
         color: Palette.ink, spacing: 0)

    if !handle.isEmpty {
        text(handle, rect(84, 1290, 430, 34), size: 22, weight: .semibold,
             color: Palette.paper, spacing: 0, kern: 2)
        rule(84, 1342, 455, 1342, color: Palette.paper.withAlphaComponent(0.40), width: 2)
    }

    if let ip = ip { drawAspectFit(ip, in: rect(700, 965, 344, 430)) }
}

func drawCover(_ card: Card, page: Int, total: Int, handle: String, brandLabel: String, ip: NSImage?) {
    fill(rect(0, 0, W, H), Palette.paper)
    fill(rect(0, 0, 18, H), Palette.red)
    text(card.eyebrow ?? brandLabel.uppercased(), rect(64, 68, 620, 34), size: 21, weight: .semibold,
         color: Palette.red, spacing: 0, kern: 1.8)
    stroke(rect(925, 52, 91, 45), Palette.red, width: 2, radius: 22)
    text(String(format: "%02d", page), rect(925, 60, 91, 28), size: 19, weight: .bold,
         color: Palette.red, align: .center, spacing: 0, mono: true)

    let titleSize: CGFloat = card.title.count > 28 ? 61 : 69
    text(card.title, rect(60, 160, 900, 300), size: titleSize, weight: .heavy, color: Palette.ink, spacing: 6)
    rule(64, 500, 760, 500, color: Palette.red, width: 4)
    if let subtitle = card.subtitle {
        text(subtitle, rect(64, 540, 790, 68), size: 39, weight: .semibold, color: Palette.deepRed, spacing: 0)
    }
    if let summary = card.summary {
        text(summary, rect(64, 650, 720, 190), size: 25, color: Palette.body, spacing: 10)
    }
    if let highlight = card.highlight {
        fill(rect(64, 890, 740, 104), Palette.panel, radius: 18)
        fill(rect(64, 890, 8, 104), Palette.red, radius: 4)
        text(highlight, rect(94, 916, 674, 62), size: 23.5, weight: .semibold,
             color: Palette.deepRed, spacing: 6)
    }
    rule(64, 1240, 650, 1240)
    let signature = handle.isEmpty ? brandLabel.uppercased() : brandLabel.uppercased() + " · " + handle
    text(signature, rect(64, 1280, 590, 34), size: 20, weight: .medium,
         color: Palette.red, spacing: 0)
    text(String(format: "%02d / %02d", page, total), rect(64, 1360, 190, 28), size: 18,
         weight: .medium, color: Palette.muted, spacing: 0, mono: true)
    if let ip = ip { drawAspectFit(ip, in: rect(620, 790, 410, 570)) }
}

func drawContent(_ card: Card, page: Int, total: Int, handle: String, brandLabel: String,
                 ip: NSImage?, assetBaseURL: URL) throws {
    fill(rect(0, 0, W, H), Palette.paper)
    fill(rect(0, 0, 18, H), Palette.red)
    fill(rect(64, 53, 410, 42), Palette.panel, radius: 21)
    text(card.eyebrow ?? brandLabel.uppercased(), rect(82, 61, 380, 26), size: 18, weight: .semibold,
         color: Palette.deepRed, spacing: 0, kern: 0.5)
    stroke(rect(925, 48, 91, 45), Palette.red, width: 2, radius: 22)
    text(String(format: "%02d", page), rect(925, 56, 91, 28), size: 19, weight: .bold,
         color: Palette.red, align: .center, spacing: 0, mono: true)

    let titleSize: CGFloat = card.title.count > 30 ? 49 : 56
    text(card.title, rect(64, 132, 940, 166), size: titleSize, weight: .heavy, color: Palette.ink, spacing: 5)
    rule(64, 312, 1016, 312, color: Palette.red, width: 4)

    let blocks = card.blocks ?? []
    var y: CGFloat = 350
    for block in blocks {
        let h = blockHeight(block)
        if y + h > 1190 {
            throw NSError(domain: "xhs-ip-cards", code: 1,
                userInfo: [NSLocalizedDescriptionKey: "Card \(page) content overflows by \(Int(y + h - 1190)) px; reduce or redistribute blocks"])
        }
        try drawBlock(block, at: y, assetBaseURL: assetBaseURL)
        y += h
    }
    footer(page: page, total: total, handle: handle, brandLabel: brandLabel, ip: ip)
}

guard CommandLine.arguments.count >= 4 else {
    fputs("Usage: render_cards <cards.json> <output-dir> <profile.json> [--allow-draft]\n", stderr)
    exit(2)
}

let inputURL = URL(fileURLWithPath: CommandLine.arguments[1])
let outputURL = URL(fileURLWithPath: CommandLine.arguments[2])
let profileURL = URL(fileURLWithPath: CommandLine.arguments[3])
let allowDraft = CommandLine.arguments.contains("--allow-draft")
let profile = try JSONDecoder().decode(ProfileManifest.self, from: Data(contentsOf: profileURL))
if profile.status != "confirmed" && !allowDraft {
    fputs("ERROR: profile is not confirmed; render a sample with --allow-draft or confirm it first\n", stderr)
    exit(3)
}
let profileDirectory = profileURL.deletingLastPathComponent()
func assetURL(_ value: String) -> URL {
    let candidate = URL(fileURLWithPath: value)
    return value.hasPrefix("/") ? candidate : profileDirectory.appendingPathComponent(value)
}
let theme = try JSONDecoder().decode(Theme.self, from: Data(contentsOf: assetURL(profile.assets.theme)))
Palette.configure(theme.palette)
guard let ip = NSImage(contentsOf: assetURL(profile.assets.card_pose)) else {
    fatalError("Cannot load profile card pose")
}
let data = try Data(contentsOf: inputURL)
let payload = try JSONDecoder().decode(Payload.self, from: data)
let handle = payload.handle ?? theme.handle ?? ""
let brandLabel = (theme.brandLabel?.isEmpty == false ? theme.brandLabel! : theme.profileName)
try FileManager.default.createDirectory(at: outputURL, withIntermediateDirectories: true)

if let cover = payload.cover {
    let heroCandidate = URL(fileURLWithPath: cover.hero)
    let heroURL = cover.hero.hasPrefix("/") ? heroCandidate : inputURL.deletingLastPathComponent().appendingPathComponent(cover.hero)
    guard let hero = NSImage(contentsOf: heroURL) else {
        fatalError("Cannot load cover Hero: \(heroURL.path)")
    }
    let coverImage = NSImage(size: NSSize(width: W, height: H), flipped: true) { _ in
        NSGraphicsContext.current?.imageInterpolation = .high
        drawBookCover(cover, handle: handle, hero: hero, ip: ip)
        return true
    }
    guard let tiff = coverImage.tiffRepresentation,
          let rep = NSBitmapImageRep(data: tiff),
          let png = rep.representation(using: .png, properties: [.compressionFactor: 0.94]) else {
        fatalError("Failed to render cover")
    }
    let path = outputURL.appendingPathComponent("cover.png")
    try png.write(to: path)
    print(path.path)
}

for (index, card) in payload.cards.enumerated() {
    let page = index + 1
    let image = NSImage(size: NSSize(width: W, height: H), flipped: true) { _ in
        NSGraphicsContext.current?.imageInterpolation = .high
        do {
            if card.kind == "cover" {
                drawCover(card, page: page, total: payload.cards.count, handle: handle, brandLabel: brandLabel, ip: ip)
            } else {
                try drawContent(card, page: page, total: payload.cards.count, handle: handle,
                                brandLabel: brandLabel, ip: ip,
                                assetBaseURL: inputURL.deletingLastPathComponent())
            }
            return true
        } catch {
            fputs("ERROR: \(error.localizedDescription)\n", stderr)
            return false
        }
    }
    guard let tiff = image.tiffRepresentation,
          let rep = NSBitmapImageRep(data: tiff),
          let png = rep.representation(using: .png, properties: [.compressionFactor: 0.94]) else {
        fatalError("Failed to render card \(page)")
    }
    let path = outputURL.appendingPathComponent(String(format: "card-%02d.png", page))
    try png.write(to: path)
    print(path.path)
}
