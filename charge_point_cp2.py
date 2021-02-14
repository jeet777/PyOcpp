import asyncio
import logging

try:
    import websockets
except ModuleNotFoundError:
    print("This example relies on the 'websockets' package.")
    print("Please install it by running: ")
    print()
    print(" $ pip install websockets")
    import sys
    sys.exit(1)


from ocpp.v201 import call
from ocpp.v201 import ChargePoint as cp
from ocpp.v201 import enums

logging.basicConfig(level=logging.INFO)


class ChargePoint(cp):

    async def send_heartbeat(self, interval):
        request = call.HeartbeatPayload()
        while True:
            await self.call(request)
            await asyncio.sleep(interval)

    async def send_Authorise_Req(self):
        request = call.AuthorizePayload(            
            id_token=call.IdToken(id_token='TestID',type=enums.IdTokenType.e_maid)
        )
        await self.call(request)

    async def send_CancelReservation_Req(self):
        request = call.CancelReservationPayload(
            reservation_id='12345'
        )
        await self.call(request)

    async def send_boot_notification(self):
        request = call.BootNotificationPayload(
            charging_station={
                'model': 'Wallbox XYZ',
                'vendor_name': 'anewone'
            },
            reason="PowerUp"
        )
        return await self.call(request)

    async def auth_seq(self):
        response = await self.send_boot_notification()
        print("Boot Notification Responce : ", response.status)
        if response.status == 'Accepted':
            await asyncio.gather(self.send_heartbeat(response.interval),self.send_Authorise_Req())

async def main():
    async with websockets.connect(
            'ws://localhost:9000/CP_2',
            subprotocols=['ocpp2.0.1']
    ) as ws:

        charge_point = ChargePoint('CP_2', ws)
        await asyncio.gather(charge_point.start(),charge_point.auth_seq())

if __name__ == '__main__':
    try:
        # asyncio.run() is used when running this example with Python 3.7 and
        # higher.
        asyncio.run(main())
    except AttributeError:
        # For Python 3.6 a bit more code is required to run the main() task on
        # an event loop.
        loop = asyncio.get_event_loop()
        loop.run_until_complete(main())
        loop.close()
