try:
    from bleak import BleakScanner
    import asyncio

    async def scan_devices():
        devices = await BleakScanner.discover(timeout=5.0)
        return [{"name": d.name, "address": d.address} for d in devices]

    def get_available_sensors():
        return asyncio.run(scan_devices())

except ImportError:
    def get_available_sensors():
        return []
