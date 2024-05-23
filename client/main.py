from Client import Client, ControlMode



async def main():
    client = Client( control_mod = ControlMode.Manual, dummy_ws=True)
    await client.start()
    await asyncio.sleep(5)
    client.stop()

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
