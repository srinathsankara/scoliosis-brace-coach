import SwiftUI

extension Color {
    // MARK: - Brand
    static let accentTeal = Color(red: 0.00, green: 0.52, blue: 0.53)
    static let accentTealLight = Color(red: 0.82, green: 0.94, blue: 0.94)
    static let accentTealDark = Color(red: 0.00, green: 0.38, blue: 0.39)
    static let accentBlue = Color(red: 0.25, green: 0.52, blue: 0.82)
    static let accentBlueLight = Color(red: 0.85, green: 0.92, blue: 0.97)

    // MARK: - Background
    static let backgroundPrimary = Color(uiColor: UIColor { $0.userInterfaceStyle == .dark
        ? UIColor(red: 0.07, green: 0.08, blue: 0.10, alpha: 1)
        : UIColor(red: 0.97, green: 0.98, blue: 0.99, alpha: 1) })
    static let backgroundSecondary = Color(uiColor: UIColor { $0.userInterfaceStyle == .dark
        ? UIColor(red: 0.10, green: 0.11, blue: 0.14, alpha: 1)
        : UIColor(red: 0.94, green: 0.96, blue: 0.97, alpha: 1) })

    // MARK: - Card
    static let cardBackground = Color(uiColor: UIColor { $0.userInterfaceStyle == .dark
        ? UIColor(red: 0.14, green: 0.15, blue: 0.18, alpha: 1)
        : UIColor(red: 1, green: 1, blue: 1, alpha: 1) })
    static let cardShadow = Color.black.opacity(0.06)
    static let cardShadowDark = Color.black.opacity(0.12)

    // MARK: - Text
    static let textPrimary = Color(uiColor: UIColor { $0.userInterfaceStyle == .dark
        ? UIColor(red: 0.92, green: 0.93, blue: 0.95, alpha: 1)
        : UIColor(red: 0.10, green: 0.14, blue: 0.18, alpha: 1) })
    static let textSecondary = Color(uiColor: UIColor { $0.userInterfaceStyle == .dark
        ? UIColor(red: 0.62, green: 0.65, blue: 0.69, alpha: 1)
        : UIColor(red: 0.55, green: 0.59, blue: 0.63, alpha: 1) })
    static let textTertiary = Color(uiColor: UIColor { $0.userInterfaceStyle == .dark
        ? UIColor(red: 0.45, green: 0.48, blue: 0.51, alpha: 1)
        : UIColor(red: 0.75, green: 0.78, blue: 0.81, alpha: 1) })

    static let dividerColor = Color(uiColor: UIColor { $0.userInterfaceStyle == .dark
        ? UIColor(red: 0.22, green: 0.23, blue: 0.26, alpha: 1)
        : UIColor(red: 0.91, green: 0.93, blue: 0.94, alpha: 1) })

    // MARK: - Status
    static let statusGood = Color(red: 0.12, green: 0.65, blue: 0.35)
    static let statusGoodLight = Color(red: 0.12, green: 0.65, blue: 0.35).opacity(0.12)
    static let statusFair = Color(red: 0.88, green: 0.57, blue: 0.07)
    static let statusFairLight = Color(red: 0.88, green: 0.57, blue: 0.07).opacity(0.12)
    static let statusPoor = Color(red: 0.78, green: 0.20, blue: 0.15)
    static let statusPoorLight = Color(red: 0.78, green: 0.20, blue: 0.15).opacity(0.12)

    // MARK: - Gradients
    static let gradientTeal = LinearGradient(
        colors: [.accentTeal, Color(red: 0.00, green: 0.42, blue: 0.44)],
        startPoint: .topLeading, endPoint: .bottomTrailing
    )
    static let gradientHero = LinearGradient(
        colors: [.accentTeal, .accentTealDark],
        startPoint: .top, endPoint: .bottom
    )
    static let gradientPremium = LinearGradient(
        colors: [Color(red: 0.00, green: 0.55, blue: 0.55),
                 Color(red: 0.15, green: 0.45, blue: 0.75)],
        startPoint: .leading, endPoint: .trailing
    )

    // MARK: - Helpers
    static func statusColor(_ s: String) -> Color {
        switch s {
        case "good": return .statusGood
        case "needs_improvement", "fair": return .statusFair
        case "poor", "needs_attention": return .statusPoor
        default: return .textSecondary
        }
    }

    static func statusLight(_ s: String) -> Color {
        switch s {
        case "good": return .statusGoodLight
        case "needs_improvement", "fair": return .statusFairLight
        case "poor", "needs_attention": return .statusPoorLight
        default: return .dividerColor
        }
    }
}

struct AppFont {
    static func title(_ size: CGFloat = 28) -> Font { .system(size: size, weight: .bold, design: .rounded) }
    static func headline(_ size: CGFloat = 17) -> Font { .system(size: size, weight: .semibold, design: .rounded) }
    static func body(_ size: CGFloat = 15) -> Font { .system(size: size, weight: .regular, design: .rounded) }
    static func caption(_ size: CGFloat = 13) -> Font { .system(size: size, weight: .medium, design: .rounded) }
    static func caption2(_ size: CGFloat = 11) -> Font { .system(size: size, weight: .medium, design: .rounded) }
    static func metric(_ size: CGFloat = 36) -> Font { .system(size: size, weight: .bold, design: .rounded) }
    static func mono(_ size: CGFloat = 12) -> Font { .system(size: size, weight: .regular, design: .monospaced) }
}
