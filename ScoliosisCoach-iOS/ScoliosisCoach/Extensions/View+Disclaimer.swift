import SwiftUI

struct DisclaimerModifier: ViewModifier {
    func body(content: Content) -> some View {
        content
            .safeAreaInset(edge: .bottom, spacing: 0) {
                HStack(spacing: 6) {
                    Image(systemName: "info.circle.fill")
                        .font(.system(size: 8))
                    Text("For educational monitoring only — not a medical device")
                        .font(.system(size: 9, weight: .medium))
                }
                .foregroundColor(.white.opacity(0.9))
                .frame(maxWidth: .infinity)
                .padding(.vertical, 6)
                .padding(.horizontal, 12)
                .background(.linearGradient(colors: [.accentTeal, .accentTealDark],
                                            startPoint: .leading, endPoint: .trailing))
            }
    }
}

extension View {
    func addDisclaimer() -> some View {
        modifier(DisclaimerModifier())
    }
}
