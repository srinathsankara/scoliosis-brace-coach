import Foundation
import CoreBluetooth

actor BLEService: NSObject {
    static let shared = BLEService()

    private var centralManager: CBCentralManager?
    private var discoveredPeripherals: [CBPeripheral] = []
    private var scanContinuation: AsyncStream<[BLEDevice]>.Continuation?

    struct BLEDevice: Identifiable {
        let id: String
        let name: String
        let rssi: Int
    }

    func startScan() -> AsyncStream<[BLEDevice]> {
        AsyncStream { continuation in
            self.scanContinuation = continuation
            self.centralManager = CBCentralManager(delegate: self, queue: nil)
        }
    }

    func stopScan() {
        centralManager?.stopScan()
        scanContinuation?.finish()
    }
}

extension BLEService: CBCentralManagerDelegate {
    // FIX #6: remove @MainActor dispatch — actor already guarantees serial access
    nonisolated func centralManagerDidUpdateState(_ central: CBCentralManager) {
        Task {
            await self.handleStateChange(central)
        }
    }

    private func handleStateChange(_ central: CBCentralManager) {
        if central.state == .poweredOn {
            centralManager?.scanForPeripherals(withServices: nil, options: nil)
        }
    }

    nonisolated func centralManager(_ central: CBCentralManager,
                                     didDiscover peripheral: CBPeripheral,
                                     advertisementData: [String: Any],
                                     rssi RSSI: NSNumber) {
        Task {
            await self.handleDiscovered(peripheral, advertisementData: advertisementData, rssi: RSSI)
        }
    }

    private func handleDiscovered(_ peripheral: CBPeripheral, advertisementData: [String: Any], rssi RSSI: NSNumber) {
        let name = peripheral.name ?? (advertisementData[CBAdvertisementDataLocalNameKey] as? String) ?? "Unknown"
        if !discoveredPeripherals.contains(where: { $0.identifier == peripheral.identifier }) {
            discoveredPeripherals.append(peripheral)
        }
        let devices = discoveredPeripherals.map { p in
            let rssiValue = p.identifier == peripheral.identifier ? RSSI.intValue : 0
            return BLEDevice(id: p.identifier.uuidString,
                            name: p.name ?? "Unknown",
                            rssi: rssiValue)
        }
        scanContinuation?.yield(devices)
    }
}
