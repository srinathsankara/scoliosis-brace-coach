import Foundation
import CoreBluetooth

actor BLEService: NSObject {
    static let shared = BLEService()

    private var centralManager: CBCentralManager?
    private var discoveredPeripherals: [CBPeripheral] = []
    private var isScanning = false
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
        isScanning = false
        scanContinuation?.finish()
    }
}

extension BLEService: CBCentralManagerDelegate {
    nonisolated func centralManagerDidUpdateState(_ central: CBCentralManager) {
        Task { @MainActor in
            if central.state == .poweredOn {
                self.centralManager?.scanForPeripherals(withServices: nil, options: nil)
                self.isScanning = true
            }
        }
    }

    nonisolated func centralManager(_ central: CBCentralManager,
                                     didDiscover peripheral: CBPeripheral,
                                     advertisementData: [String: Any],
                                     rssi RSSI: NSNumber) {
        Task { @MainActor in
            let name = peripheral.name ?? advertisementData[CBAdvertisementDataLocalNameKey] as? String ?? "Unknown"
            let device = BLEDevice(id: peripheral.identifier.uuidString, name: name, rssi: RSSI.intValue)
            if !self.discoveredPeripherals.contains(where: { $0.identifier == peripheral.identifier }) {
                self.discoveredPeripherals.append(peripheral)
            }
            let devices = self.discoveredPeripherals.map {
                BLEDevice(id: $0.identifier.uuidString,
                          name: $0.name ?? "Unknown",
                          rssi: 0)
            }
            self.scanContinuation?.yield(devices)
        }
    }
}
