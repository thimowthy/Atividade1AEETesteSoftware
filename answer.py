from unittest import TestCase
from unittest.mock import Mock

class PaymentGateway:
    def charge(self, amount):
        print(f"Charging {amount}")

class OrderProcessor:
    def __init__(self, payment_gateway):
        self.payment_gateway = payment_gateway

    def process_order(self, order):
        if not order['items']:
            # Não deve chamar o pagamento
            return "No items to process"
        total = sum(order['items'])
        self.payment_gateway.charge(total)
        return "Order processed"

    def process_order_with_retry(self, order, max_attempts=3):
        if not order['items']:
            return "No items to process"
        
        total = sum(order['items'])
        attempt = 0
        while attempt < max_attempts:
            attempt += 1
            try:
                self.payment_gateway.charge(total)
                return "Order processed successfully"
            except Exception as e:
                if attempt == max_attempts:
                    return f"Failed after {max_attempts} attempts"
        return "Order processing ended unexpectedly"
    
class OrderProcessorTest(TestCase):
    def test_payment_for_empty_order(self):
        payment_gateway = Mock(spec=PaymentGateway)
        processor = OrderProcessor(payment_gateway)
        
        empty_order = {'items': []}
        result = processor.process_order(empty_order)

        # Verifica que charge NÃO foi chamado
        payment_gateway.charge.assert_not_called()

        self.assertEqual(result, "No items to process")


    def test_payment_order(self):
        payment_gateway = Mock(spec=PaymentGateway)
        processor = OrderProcessor(payment_gateway)
        
        order = {'items': [10, 20, 30]}
        result = processor.process_order(order)

        payment_gateway.charge.assert_called_once_with(60)
        self.assertEqual(result, "Order processed")

class OrderProcessorRetryTest(TestCase):
    def test_payment_retry_until_success(self):
        payment_gateway = Mock(spec=PaymentGateway)

        # Simula falha nas duas primeiras tentativas
        payment_gateway.charge.side_effect = [Exception("fail"), Exception("fail"), None]

        processor = OrderProcessor(payment_gateway)
        order = {'items': [50, 50]}

        result = processor.process_order_with_retry(order)
        self.assertEqual(payment_gateway.charge.call_count, 3)

        self.assertEqual(result, "Order processed successfully")

    def test_payment_retry_fail_all_attempts(self):
        payment_gateway = Mock(spec=PaymentGateway)

        # Simula falha em todas as tentativas
        payment_gateway.charge.side_effect = Exception("fail")

        processor = OrderProcessor(payment_gateway)
        order = {'items': [50, 50]}

        result = processor.process_order_with_retry(order, max_attempts=3)

        # Verifica que charge foi chamado 3 vezes
        self.assertEqual(payment_gateway.charge.call_count, 3)

        self.assertEqual(result, "Failed after 3 attempts")

if __name__ == "__main__":
    import unittest
    unittest.main()
