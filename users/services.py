import stripe
from django.conf import settings
from django.views import View
from django.shortcuts import render, redirect
from django.contrib import messages


stripe.api_key = settings.STRIPE_TEST_SECRET_KEY


def create_stripe_price(payment_sum):
  """Создает цену в страйпе"""
  return stripe.Price.create(
    currency="rub",
    unit_amount=payment_sum * 100,
    product_data={"name": "Course payment"},
  )


def create_stripe_session(price):
  """Создает сессию на оплату в страйпе"""
  session = stripe.checkout.Session.create(
    success_url="http://127.0.0.1:8000/",
    line_items=[{"price": price.get("id"), "quantity": 1}],
    mode="payment",
  )
  return session.get("id"), session.get("url")


class CreateCheckoutSessionView:
    pass