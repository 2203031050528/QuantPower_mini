import struct
from datetime import datetime


EXCHANGE_SEGMENTS = {
    0: "IDX_I",
    1: "NSE_EQ",
    2: "NSE_FNO",
    3: "NSE_CURRENCY",
    4: "BSE_EQ",
    5: "MCX_COMM",
    7: "BSE_CURRENCY",
    8: "BSE_FNO",
}


class DhanPacketParser:

    TICKER_PACKET = 2
    DISCONNECT_PACKET = 50

    @classmethod
    def parse(cls, data: bytes):

        if len(data) < 8:
            return None

        response_code = data[0]

        exchange_code = data[3]

        security_id = struct.unpack_from(
            "<I",
            data,
            4,
        )[0]

        exchange_segment = EXCHANGE_SEGMENTS.get(
            exchange_code,
            "UNKNOWN",
        )

        if response_code == cls.TICKER_PACKET:

            if len(data) < 17:
                return None

            ltp = struct.unpack_from(
                "<f",
                data,
                8,
            )[0]

            ltt = struct.unpack_from(
                "<I",
                data,
                12,
            )[0]

            return {
                "type": "ticker",
                "exchange_segment": exchange_segment,
                "security_id": str(security_id),
                "ltp": round(ltp, 2),
                "timestamp": datetime.fromtimestamp(
                    ltt
                ).isoformat(),
            }

        if response_code == cls.DISCONNECT_PACKET:

            reason = None

            if len(data) >= 10:
                reason = struct.unpack_from(
                    "<h",
                    data,
                    8,
                )[0]

            return {
                "type": "disconnect",
                "reason": reason,
            }

        return {
            "type": "unknown",
            "response_code": response_code,
            "exchange_segment": exchange_segment,
            "security_id": str(security_id),
        }
