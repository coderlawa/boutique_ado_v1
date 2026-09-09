from types import SimpleNamespace
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.test import TestCase

from checkout.webhook_handler import StripeWH_Handler
from products.models import Product
from profiles.models import UserProfile


class StripeObject(dict):
    def __getattr__(self, item):
        try:
            return self[item]
        except KeyError as exc:
            raise AttributeError(item) from exc

    def __setattr__(self, key, value):
        self[key] = value

    def to_dict(self):
        return dict(self)


class StripeWebhookHandlerTests(TestCase):
    def test_handles_missing_profile_for_logged_in_user(self):
        user = get_user_model().objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        UserProfile.objects.filter(user=user).delete()
        product = Product.objects.create(
            sku='test-sku',
            name='Test Product',
            description='A test product',
            price='19.99',
        )

        class FakeCharge:
            billing_details = SimpleNamespace(email='test@example.com')
            amount = 1999

        address = StripeObject(
            country='US',
            postal_code='12345',
            city='Test City',
            line1='1 Main St',
            line2='',
            state='CA',
        )
        shipping = StripeObject(
            name='Test User',
            phone='1234567890',
            address=address,
        )
        intent = StripeObject(
            id='pi_test_123',
            metadata=StripeObject(
                bag=f'{{"{product.id}": 1}}',
                save_info='True',
                username=user.username,
            ),
            latest_charge='ch_test_123',
            shipping=shipping,
        )

        event = StripeObject(
            type='payment_intent.succeeded',
            data=StripeObject(object=intent),
        )

        with patch('checkout.webhook_handler.stripe.Charge.retrieve', return_value=FakeCharge()):
            response = StripeWH_Handler(None).handle_payment_intent_succeeded(event)

        self.assertEqual(response.status_code, 200)
        self.assertFalse(UserProfile.objects.filter(user=user).exists())
