import SwiftUI

struct DisclaimerModifier: ViewModifier {
    func body(content: Content) -> some View {
        content
            .overlay(alignment: .bottom) {
                Text("MEDICAL DISCLAIMER: For educational purposes only. Not a medical device. Consult a healthcare provider.")
                    .font(.system(size: 6))
                    .foregroundColor(.red)
                    .padding(.horizontal, 4)
                    .padding(.vertical, 2)
                    .background(Color(.systemBackground).opacity(0.9))
            }
    }
}

extension View {
    func addDisclaimer() -> some View {
        modifier(DisclaimerModifier())
    }
}
