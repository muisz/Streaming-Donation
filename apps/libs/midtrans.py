import midtransclient
import hashlib
from django.conf import settings


class RequestPayment:
    order_id = None
    gross_amount = 0
    bank_code = None

    def __init__(self, order_id, gross_amount, bank_code):
        self.order_id = order_id
        self.gross_amount = gross_amount
        self.bank_code = bank_code


class MidtransPayment:
    transaction_id = None
    order_id = None
    transaction_status = None
    fraud_status = None
    va_number = None
    transaction_time = None

    def __init__(self, transaction_id, order_id, transaction_status, fraud_status, va_number, transaction_time):
        self.transaction_id = transaction_id
        self.order_id = order_id
        self.transaction_status = transaction_status
        self.fraud_status = fraud_status
        self.va_number = va_number
        self.transaction_time = transaction_time
    
    @property
    def is_success(self):
        return self.transaction_status == "settlement"
    
    @property
    def is_pending(self):
        return self.transaction_status == "pending"
    
    @property
    def is_failed(self):
        return self.transaction_status in ("expire", "cancel", "deny")


class Midtrans:
    IS_PRODUCTION = settings.MIDTRANS_PRODUCTION
    CLIENT_KEY = settings.MIDTRANS_CLIENT_KEY
    SERVER_KEY = settings.MIDTRANS_SERVER_KEY

    def __init__(self):
        self.core_api = midtransclient.CoreApi(
            is_production=self.IS_PRODUCTION,
            client_key=self.CLIENT_KEY,
            server_key=self.SERVER_KEY,
        )
        self.snap = midtransclient.Snap(
            is_production=self.IS_PRODUCTION,
            client_key=self.CLIENT_KEY,
            server_key=self.SERVER_KEY,
        )

    def validate_transaction_signature(cls, transaction_data: dict):
        order_id = transaction_data.get("order_id")
        status_code = transaction_data.get("status_code")
        gross_amount = transaction_data.get("gross_amount")
        server_key = settings.MIDTRANS_SERVER_KEY
        key = order_id + status_code + str(gross_amount) + server_key
        signature = hashlib.sha512(key.encode())
        return signature.hexdigest() == transaction_data.get("signature_key")

    
    def get_available_banks(self):
        return [
            {
                "name": "BNI",
                "code": "bni",
            },
            {
                "name": "BCA",
                "code": "bca",
            },
            {
                "name": "BRI",
                "code": "bri",
            },
            {
                "name": "Mandiri Bill",
                "code": "mandiri",
            },
            {
                "name": "Permata",
                "code": "permata",
            },
            {
                "name": "CIMB",
                "code": "cimb"
            }
        ]
    
    def get_transaction_detail(self, id):
        response = self.core_api.transactions.status(id)
        return MidtransPayment(
            transaction_id=response.get("transaction_id"),
            order_id=response.get("order_id"),
            transaction_status=response.get("transaction_status"),
            fraud_status=response.get("fraud_status"),
            va_number="",
            transaction_time=response.get("transaction_time"),
        )

    def create_payment(self, payment: RequestPayment):
        handler = {
            "bca": self.create_bca_payment,
            "bni": self.create_bni_payment,
            "bri": self.create_bri_payment,
            "mandiri": self.create_mandiri_bill_payment,
            "permata": self.create_permata_payment,
            "cimb": self.create_cimb_payment,
        }
        handler_class = handler.get(payment.bank_code)
        if handler_class is None:
            raise Exception("Unknown payment")
        return handler_class(payment)

    def create_bni_payment(self, payment: RequestPayment):
        payload = {
            "payment_type": "bank_transfer",
            "transaction_details": {
                "order_id": payment.order_id,
                "gross_amount": payment.gross_amount,
            },
            "bank_transfer": {
                "bank": "bni",
            }
        }
        response = self.core_api.charge(payload)
        if response.get("status_code") != "201":
            raise Exception("Failed to create transaction")
        
        va_number = None
        va_numbers = response.get("va_numbers", [])
        for va in va_numbers:
            va_number = va.get("va_number")
        
        return MidtransPayment(
            transaction_id=response.get("transaction_id"),
            order_id=response.get("order_id"),
            transaction_status=response.get("transaction_status"),
            fraud_status=response.get("fraud_status"),
            va_number=va_number,
            transaction_time=response.get("transaction_time"),
        )
    
    def create_bca_payment(self, payment: RequestPayment):
        payload = {
            "payment_type": "bank_transfer",
            "transaction_details": {
                "order_id": payment.order_id,
                "gross_amount": payment.gross_amount,
            },
            "bank_transfer": {
                "bank": "bca",
            }
        }
        response = self.core_api.charge(payload)
        if response.get("status_code") != "201":
            raise Exception("Failed to create transaction")
        
        va_number = None
        va_numbers = response.get("va_numbers", [])
        for va in va_numbers:
            va_number = va.get("va_number")
        
        return MidtransPayment(
            transaction_id=response.get("transaction_id"),
            order_id=response.get("order_id"),
            transaction_status=response.get("transaction_status"),
            fraud_status=response.get("fraud_status"),
            va_number=va_number,
            transaction_time=response.get("transaction_time"),
        )
    
    def create_bri_payment(self, payment: RequestPayment):
        payload = {
            "payment_type": "bank_transfer",
            "transaction_details": {
                "order_id": payment.order_id,
                "gross_amount": payment.gross_amount,
            },
            "bank_transfer": {
                "bank": "bri",
            }
        }
        response = self.core_api.charge(payload)
        if response.get("status_code") != "201":
            raise Exception("Failed to create transaction")
        
        va_number = None
        va_numbers = response.get("va_numbers", [])
        for va in va_numbers:
            va_number = va.get("va_number")
        
        return MidtransPayment(
            transaction_id=response.get("transaction_id"),
            order_id=response.get("order_id"),
            transaction_status=response.get("transaction_status"),
            fraud_status=response.get("fraud_status"),
            va_number=va_number,
            transaction_time=response.get("transaction_time"),
        )
    
    def create_mandiri_bill_payment(self, payment: RequestPayment):
        payload = {
            "payment_type": "echannel",
            "transaction_details": {
                "order_id": payment.order_id,
                "gross_amount": payment.gross_amount,
            },
            "echannel": {
                "bill_info1": "Payment:",
                "bill_info2": "Online Payment",
            }
        }
        response = self.core_api.charge(payload)
        if response.get("status_code") != "201":
            raise Exception("Failed to create transaction")
        
        biller_code = response.get("biller_code")
        bill_key = response.get("bill_key")
        va_number = f"{biller_code}#{bill_key}"
        
        return MidtransPayment(
            transaction_id=response.get("transaction_id"),
            order_id=response.get("order_id"),
            transaction_status=response.get("transaction_status"),
            fraud_status=response.get("fraud_status"),
            va_number=va_number,
            transaction_time=response.get("transaction_time"),
        )
    
    def create_permata_payment(self, payment: RequestPayment):
        payload = {
            "payment_type": "permata",
            "transaction_details": {
                "order_id": payment.order_id,
                "gross_amount": payment.gross_amount,
            },
        }
        response = self.core_api.charge(payload)
        if response.get("status_code") != "201":
            raise Exception("Failed to create transaction")
        
        va_number = response.get("permata_va_number")
        
        return MidtransPayment(
            transaction_id=response.get("transaction_id"),
            order_id=response.get("order_id"),
            transaction_status=response.get("transaction_status"),
            fraud_status=response.get("fraud_status"),
            va_number=va_number,
            transaction_time=response.get("transaction_time"),
        )
    
    def create_cimb_payment(self, payment: RequestPayment):
        payload = {
            "payment_type": "bank_transfer",
            "transaction_details": {
                "order_id": payment.order_id,
                "gross_amount": payment.gross_amount,
            },
            "bank_transfer": {
                "bank": "cimb",
            }
        }
        response = self.core_api.charge(payload)
        if response.get("status_code") != "201":
            raise Exception("Failed to create transaction")
        
        va_number = None
        va_numbers = response.get("va_numbers", [])
        for va in va_numbers:
            va_number = va.get("va_number")
        
        return MidtransPayment(
            transaction_id=response.get("transaction_id"),
            order_id=response.get("order_id"),
            transaction_status=response.get("transaction_status"),
            fraud_status=response.get("fraud_status"),
            va_number=va_number,
            transaction_time=response.get("transaction_time"),
        )
