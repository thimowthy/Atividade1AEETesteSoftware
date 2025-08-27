class PaymentGateway:
    def charge(self, amount):
        print(f"Charging {amount}")


class OrderProcessor:
    def __init__(self, payment_gateway):
        self.payment_gateway = payment_gateway

    def process_order(self, order):
        # PROBLEMA 1: cobra mesmo quando não há itens
        total = sum(order['items']) if 'items' in order else 0
        self.payment_gateway.charge(total)  
        return "Order processed"

    def process_order_with_retry(self, order, max_attempts=3):
        # PROBLEMA 2: não trata pedido vazio → vai tentar cobrar 0
        total = sum(order['items']) if 'items' in order else 0
        attempt = 0
        while attempt < max_attempts:
            attempt += 1
            try:
                status = self.payment_gateway.charge(total)
                # PROBLEMA 3: considera sucesso sem verificar se realmente foi processado
                return "Order processed successfully"
            except Exception as e:
                # PROBLEMA 4: se nunca tiver sucesso, pode cair em loop infinito
                print(f"Attempt {attempt} failed: {e}")
        return "Order processing ended unexpectedly"


if __name__ == "__main__":
    gateway = PaymentGateway()
    processor = OrderProcessor(gateway)

    # Pedido vazio → mesmo assim vai cobrar 0
    empty_order = {"items": []}
    print(processor.process_order(empty_order))

    # Pedido com retry, mas sem validar sucesso real
    faulty_order = {"items": [100]}
    # Aqui, se o gateway falhar sempre, vamos imprimir tentativas infinitas
    print(processor.process_order_with_retry(faulty_order, max_attempts=1000000))
